import { useState, useEffect, useRef } from "react";
import districtAreasJson from "@/config/agmarknet_district_areas.json";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, Marker, useMapEvents, Rectangle } from "react-leaflet";
import L from "leaflet";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Camera, MapPin, X } from "lucide-react";
import { toast } from "sonner";
import { getCurrentUser, getUser, isAuthenticated, updateProfile, User, getDistricts, getStates } from "../services/api";
import type { Map as LeafletMap } from "leaflet";



interface District {
  district_id: number;
  district_name: string;
  markets: Array<{ id: number; mkt_name: string }>;
}

interface State {
  state_id: number;
  state_name: string;
}

const Profile = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    userType: "",
    crop: "",
    location: "",
    state: "",
    district: "",
    village: "",
  });
  const [isSaving, setIsSaving] = useState(false);
  const [useManualSelection, setUseManualSelection] = useState(false);
  const [districts, setDistricts] = useState<District[]>([]);
  const [states, setStates] = useState<State[]>([]);
  const [availableDistricts, setAvailableDistricts] = useState<District[]>([]);
  const savedLocationRef = useRef<string>(""); // Store location when switching to manual mode
  const [mapVisible, setMapVisible] = useState(false);
  const [selectedPoint, setSelectedPoint] = useState<{ lat: number; lon: number } | null>(null);
  const [districtAreas, setDistrictAreas] = useState<Record<string, [number, number, number, number]> | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    // Load user data
    const loadUserData = async () => {
      try {
        setLoading(true);
        // Try to get from backend, fallback to localStorage
        const userData = await getCurrentUser();
        setUser(userData);
        setFormData({
          name: userData.name || "",
          phone: userData.phone || "",
          email: userData.email || "",
          userType: userData.userType || "",
          crop: userData.crop || "",
          location: userData.location || "",
          state: userData.state || "",
          district: userData.district || "",
          village: userData.village || "",
        });
        // Initialize saved location ref with user's location
        if (userData.location) {
          savedLocationRef.current = userData.location;
        }
      } catch (error: any) {
        // Fallback to stored user data
        const storedUser = getUser();
        if (storedUser) {
          setUser(storedUser);
          setFormData({
            name: storedUser.name || "",
            phone: storedUser.phone || "",
            email: storedUser.email || "",
            userType: storedUser.userType || "",
            crop: storedUser.crop || "",
            location: storedUser.location || "",
            state: storedUser.state || "",
            district: storedUser.district || "",
            village: storedUser.village || "",
          });
          // Initialize saved location ref with stored user's location
          if (storedUser.location) {
            savedLocationRef.current = storedUser.location;
          }
        } else {
          toast.error("Failed to load user data");
          navigate("/login");
        }
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, [navigate]);

  // Load districts and states metadata
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const [districtsData, statesData] = await Promise.all([
          getDistricts(),
          getStates(),
        ]);
        setDistricts(districtsData);
        setStates(statesData);
        
        // If user has state selected, filter districts
        if (formData.state) {
          // For now, show all districts (districts.json only has Maharashtra districts)
          setAvailableDistricts(districtsData);
        } else {
          setAvailableDistricts(districtsData);
        }
        // Load Agmarknet district area bounds (single source of truth)
        // `districtAreasJson` is imported as an ES module at the top of the file
        // and applied in a separate effect below.
      } catch (error) {
        console.error("Failed to load metadata:", error);
      }
    };
    loadMetadata();
  }, []);

  // Update available districts when state changes
  useEffect(() => {
    if (formData.state && districts.length > 0) {
      // For now, districts.json only has Maharashtra districts, so show all
      // In future, if multiple states are added, filter by state here
      setAvailableDistricts(districts);
    } else {
      setAvailableDistricts(districts);
    }
    
    // Clear district if state changes
    if (!formData.state) {
      setFormData({ ...formData, district: "" });
    }
  }, [formData.state, districts]);

  // Clear selected map point when district changes
  useEffect(() => {
    setSelectedPoint(null);
    setMapVisible(false);
    // Hide any saved manual location preview when district changes
    savedLocationRef.current = "";
    // Clear saved manual location from form when district changes
    setFormData((prev) => ({ ...prev, location: "" }));
  }, [formData.district]);

  // Helper: parse a location string like "lat, lon" into a point
  const parseLocationString = (loc?: string | null) => {
    if (!loc) return null;
    const parts = loc.trim().split(/[\s,]+/).map(p => p.trim()).filter(Boolean);
    if (parts.length < 2) return null;
    const lat = parseFloat(parts[0]);
    const lon = parseFloat(parts[1]);
    if (isNaN(lat) || isNaN(lon)) return null;
    return { lat, lon };
  };

  // Expose previously selected map-based location if present in formData
  useEffect(() => {
    if (formData.location) {
      const parts = formData.location.split(/[\s,]+/).map((p) => p.trim()).filter(Boolean);
      if (parts.length >= 2) {
        const lat = parseFloat(parts[0]);
        const lon = parseFloat(parts[1]);
        if (!isNaN(lat) && !isNaN(lon)) {
          setSelectedPoint({ lat, lon });
        }
      }
    }
  }, [formData.location]);

  const getDistrictBbox = (districtName?: string) => {
    if (!districtName || !districtAreas) return null;
    // Exact match required
    const bbox = (districtAreas as any)[districtName];
    if (!bbox || !Array.isArray(bbox) || bbox.length !== 4) return null;
    return bbox as [number, number, number, number];
  };

  // Cached bbox for the currently selected district (avoids complex inline expressions in JSX)
  const districtBbox = getDistrictBbox(formData.district);
  const districtBoundsArray: [[number, number], [number, number]] | null =
  districtBbox
    ? [
        [districtBbox[0], districtBbox[1]],
        [districtBbox[2], districtBbox[3]],
      ]
    : null;
  

    const mapRef = useRef<LeafletMap | null>(null);



  // Determine saved manual point (only from `formData.location` when manual mode is active)
  const savedManualPoint = useManualSelection ? parseLocationString(formData.location) : null;

  // Initialize districtAreas from the static JSON import (Vite-friendly)
  useEffect(() => {
    try {
      // Imported JSON has type Record<string, number[]>. Validate and normalize to fixed-length tuples.
      const raw = districtAreasJson as Record<string, number[]>;
      const normalized: Record<string, [number, number, number, number]> = {};
      for (const [k, v] of Object.entries(raw)) {
        if (Array.isArray(v) && v.length === 4 && v.every((n) => typeof n === "number" && Number.isFinite(n))) {
          normalized[k] = [v[0], v[1], v[2], v[3]];
        }
      }
      setDistrictAreas(Object.keys(normalized).length ? normalized : null);
    } catch (err) {
      setDistrictAreas(null);
    }
  }, []);

  // Map click handler hook that restricts clicks to bbox
  function ClickHandler({ bbox }: { bbox: [number, number, number, number] }) {
    useMapEvents({
      click(e) {
        const { lat, lng } = e.latlng;
        const [south, west, north, east] = bbox;
        if (lat >= south && lat <= north && lng >= west && lng <= east) {
          setSelectedPoint({ lat, lon: lng });
        }
      },
    });
    return null;
  }

  // Small green DivIcon for marker to match theme
  const greenIcon = L.divIcon({
    className: "agri-marker",
    html: `<span style="display:inline-block;width:16px;height:16px;border-radius:50%;background:#0f766e;border:2px solid white;box-shadow:0 0 0 2px rgba(15,118,110,0.12);"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });

  // Check if user has manual selection enabled (if state/district are set)
  useEffect(() => {
    if (formData.state || formData.district) {
      setUseManualSelection(true);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const updateData: any = {
        name: formData.name,
        phone: formData.phone || undefined,
        crop: formData.crop || undefined,
      };
      
      if (useManualSelection) {
        // Manual mode: use state and district
        updateData.state = formData.state || undefined;
        updateData.district = formData.district || undefined;
        updateData.location = undefined; // Clear location in manual mode
      } else {
        // Auto-detect mode: use location
        updateData.location = formData.location || undefined;
        updateData.state = undefined;
        updateData.district = undefined;
      }
      
      const updatedUser = await updateProfile(updateData);
      setUser(updatedUser);
      toast.success("Profile updated successfully!");
    } catch (error: any) {
      toast.error(error.message || "Failed to update profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleGeolocate = async () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const coords = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
          
            // Auto-save location to profile (backend will reverse geocode automatically)
          try {
            const updatedUser = await updateProfile({
              name: formData.name,
              phone: formData.phone || undefined,
              crop: formData.crop || undefined,
              location: coords,
            });

            // Update formData with location and reverse geocoded results (use functional update to avoid stale closures)
            setFormData((prev) => ({
              ...prev,
              location: coords,
              state: updatedUser.state || "",
              district: updatedUser.district || "",
              village: updatedUser.village || "",
            }));
            setUser(updatedUser);
            // Update saved location ref
            savedLocationRef.current = coords;
            toast.success("Location detected and reverse geocoded!");
          } catch (error: any) {
            // If auto-save fails, still update location in form (use functional update)
            setFormData((prev) => ({ ...prev, location: coords }));
            toast.success("Location detected! Please save to update profile.");
            console.log("Auto-save location failed:", error);
          }
        },
        () => {
          toast.error("Unable to detect location");
        }
      );
    } else {
      toast.error("Geolocation is not supported by your browser");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen py-8 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg text-muted-foreground">Loading profile...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }




  // Get first letter of name for avatar
  const initials = user.name ? user.name.charAt(0).toUpperCase() : "U";

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-heading font-bold text-primary mb-8">Profile Settings</h1>

        <Card className="p-6 shadow-hover bg-gradient-card">
          {/* Profile Picture */}
          <div className="flex flex-col items-center mb-8">
            <div className="relative">
              <Avatar className="w-24 h-24">
                <AvatarFallback className="bg-primary text-primary-foreground text-3xl">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <button className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-secondary text-white flex items-center justify-center hover:bg-secondary/90 transition-colors">
                <Camera className="h-4 w-4" />
              </button>
            </div>
            <h2 className="mt-4 text-xl font-semibold">{user.name}</h2>
            <p className="text-muted-foreground capitalize">{user.userType || "User"}</p>
          </div>

          {/* Profile Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input 
                  id="name" 
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input 
                  id="phone" 
                  type="tel" 
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input 
                  id="email" 
                  type="email" 
                  value={formData.email}
                  disabled
                  className="bg-muted"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="crop">Primary Crop</Label>
                <Select
                  value={formData.crop}
                  onValueChange={(value) => setFormData({ ...formData, crop: value })}
                >
                  <SelectTrigger id="crop">
                    <SelectValue placeholder="Select primary crop" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cotton">Cotton</SelectItem>
                    <SelectItem value="wheat">Wheat</SelectItem>
                    <SelectItem value="rice">Rice</SelectItem>
                    <SelectItem value="sugarcane">Sugarcane</SelectItem>
                    <SelectItem value="soyabean">Soyabean</SelectItem>
                    <SelectItem value="onion">Onion</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Location Mode Toggle */}
              <div className="space-y-2 md:col-span-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="location-mode">Location Selection Mode</Label>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {useManualSelection ? "Manual Selection" : "Auto-Detect"}
                    </span>
                    <Switch
                      id="location-mode"
                      checked={useManualSelection}
                      onCheckedChange={async (checked) => {
                        setUseManualSelection(checked);
                        if (!checked) {
                          // Switching to auto-detect: clear manual selections
                          // Restore location from saved ref, formData, user profile, or keep existing
                          const locationToUse = savedLocationRef.current || formData.location || user?.location || "";
                          const newFormData = { 
                            ...formData, 
                            state: "", 
                            district: "", 
                            village: "",
                            location: locationToUse
                          };
                          setFormData(newFormData);
                          
                          // If location exists, reverse geocode it to populate state, district, village
                          if (locationToUse) {
                            try {
                              const locationStr = locationToUse.trim();
                              const parts = locationStr.split(/[,\s]+/).filter(p => p);
                              if (parts.length >= 2) {
                                const lat = parseFloat(parts[0]);
                                const lon = parseFloat(parts[1]);
                                if (!isNaN(lat) && !isNaN(lon)) {
                                  // Call backend to reverse geocode and update profile
                                  // The backend's updateProfile automatically reverse geocodes location
                                  const updatedUser = await updateProfile({
                                    name: formData.name,
                                    phone: formData.phone || undefined,
                                    crop: formData.crop || undefined,
                                    location: locationToUse,
                                  });
                                  
                                  // Update formData with reverse geocoded results
                                  setFormData({
                                    ...newFormData,
                                    state: updatedUser.state || "",
                                    district: updatedUser.district || "",
                                    village: updatedUser.village || "",
                                  });
                                  setUser(updatedUser);
                                  // Update saved location ref
                                  savedLocationRef.current = locationToUse;
                                  toast.success("Location reverse geocoded successfully!");
                                }
                              }
                            } catch (error: any) {
                              console.error("Reverse geocoding failed:", error);
                              // Don't show error toast, just log it - user can manually geolocate
                            }
                          } else {
                            // No saved location available — attempt to auto-detect now
                            try {
                              handleGeolocate();
                            } catch (e) {
                              // ignore failures here; user can click the geolocate button
                            }
                          }
                        } else {
                          // Switching to manual: save current location before clearing it
                          if (formData.location) {
                            savedLocationRef.current = formData.location;
                          } else if (user?.location) {
                            savedLocationRef.current = user.location;
                          }
                          // Clear location from form display (but keep it in savedLocationRef)
                          setFormData({ ...formData, location: "" });
                        }
                      }}
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  {useManualSelection 
                    ? "Select your state and district manually" 
                    : "Automatically detect location from GPS coordinates"}
                </p>
              </div>

              {useManualSelection ? (
                <>
                  {/* Manual Selection Mode: State and District Dropdowns */}
                  <div className="space-y-2">
                    <Label htmlFor="state-select">State</Label>
                    <Select
                      value={formData.state}
                      onValueChange={(value) => setFormData({ ...formData, state: value, district: "" })}
                    >
                      <SelectTrigger id="state-select">
                        <SelectValue placeholder="Select state" />
                      </SelectTrigger>
                      <SelectContent>
                        {states.map((state) => (
                          <SelectItem key={state.state_id} value={state.state_name}>
                            {state.state_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="district-select">District</Label>
                    <Select
                      value={formData.district}
                      onValueChange={(value) => setFormData({ ...formData, district: value })}
                      disabled={!formData.state}
                    >
                      <SelectTrigger id="district-select">
                        <SelectValue placeholder={formData.state ? "Select district" : "Select state first"} />
                      </SelectTrigger>
                      <SelectContent>
                        {availableDistricts.map((district) => (
                          <SelectItem key={district.district_id} value={district.district_name}>
                            {district.district_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Map action: show button to expand inline map picker (only when manual mode + district selected) */}
                  {useManualSelection && (
                    <>
                      <div className="space-y-2">
                        {districtBbox ? (
                          <div className="mt-3">
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => {
                                // When opening the map, pre-fill the marker from saved formData or savedLocationRef
                                const existing = parseLocationString(formData.location) || parseLocationString(savedLocationRef.current) || parseLocationString(user?.location || "");
                                if (existing) setSelectedPoint(existing);
                                setMapVisible((v) => !v);
                              }}
                            >
                              Select exact farm location on map
                            </Button>
                          </div>
                        ) : (
                          formData.district && (
                            <p className="text-xs text-destructive mt-3">Map not available for the selected district.</p>
                          )
                        )}
                      </div>

                      <div className="space-y-2">
                        {useManualSelection && savedManualPoint && !mapVisible ? (
                          <>
                            <Label>Saved Location (Manual)</Label>
                            <div className="grid grid-cols-1 gap-2">
                              <Input value={savedManualPoint.lat.toFixed(6)} disabled className="bg-muted" />
                              <Input value={savedManualPoint.lon.toFixed(6)} disabled className="bg-muted" />
                            </div>
                          </>
                        ) : null}
                      </div>
                    </>
                  )}
                </>
              ) : (
                <>
                  {/* Auto-Detect Mode: Location Input */}
                  <div className="space-y-2">
                    <Label htmlFor="location">Farm Location</Label>
                    <div className="flex gap-2">
                      <Input 
                        id="location" 
                        value={formData.location}
                        onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                        placeholder="Enter farm location or coordinates"
                        disabled={!!formData.location}
                        className={formData.location ? "bg-muted" : ""}
                      />
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={handleGeolocate}
                        title="Auto-detect location"
                      >
                        <MapPin className="h-4 w-4" />
                      </Button>
                      {formData.location && (
                        <Button
                          type="button"
                          variant="outline"
                          size="icon"
                          onClick={() => {
                            setFormData({ ...formData, location: "", state: "", district: "", village: "" });
                            savedLocationRef.current = "";
                            toast.info("Location cleared. You can now enter coordinates manually or use GPS to detect.");
                          }}
                          title="Clear location"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                    {formData.location && (
                      <p className="text-xs text-muted-foreground">
                        Location is auto-detected. Click the GPS button to re-detect or clear to enter manually.
                      </p>
                    )}
                  </div>

                  {/* Display coordinates when location exists */}
                  {formData.location && (() => {
                    const coords = parseLocationString(formData.location);
                    return coords ? (
                      <div className="space-y-2">
                        <Label>Coordinates (Auto-detected)</Label>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="space-y-1">
                            <Label htmlFor="latitude" className="text-xs text-muted-foreground">Latitude</Label>
                            <Input 
                              id="latitude" 
                              value={coords.lat.toFixed(6)} 
                              disabled 
                              className="bg-muted" 
                            />
                          </div>
                          <div className="space-y-1">
                            <Label htmlFor="longitude" className="text-xs text-muted-foreground">Longitude</Label>
                            <Input 
                              id="longitude" 
                              value={coords.lon.toFixed(6)} 
                              disabled 
                              className="bg-muted" 
                            />
                          </div>
                        </div>
                      </div>
                    ) : null;
                  })()}

                  {/* Auto-detected fields (read-only) */}
                  <div className="space-y-2">
                    <Label htmlFor="state">State (Auto-detected)</Label>
                    <Input id="state" value={formData.state} disabled className="bg-muted" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="district">District (Auto-detected)</Label>
                    <Input id="district" value={formData.district} disabled className="bg-muted" />
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label htmlFor="village">Village / Town</Label>
                <Input 
                  id="village" 
                  value={formData.village}
                  onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                  placeholder="Optional"
                />
              </div>
              {/* Inline map container (expandable) */}
              {mapVisible && districtBbox && (
                <div className="md:col-span-2">
                  <Card className="p-4 mt-4 shadow-hover bg-gradient-card">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h3 className="text-sm font-medium">Pick precise farm location</h3>
                        <p className="text-xs text-muted-foreground">Click near your farm location</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => { setMapVisible(false); }}>
                          Close
                        </Button>
                      </div>
                    </div>
                    <div style={{ height: 280 }}>
                      <MapContainer
                        bounds={districtBoundsArray!}
                        style={{ height: "100%", width: "100%" }}
                        attributionControl={false}
                        zoomControl={true}
                        maxZoom={18}
                        ref={mapRef}
                        whenReady={() => {
                          const map = mapRef.current;
                          if (!map || !districtBoundsArray) return;

                          // Lock map inside district
                          map.setMaxBounds(districtBoundsArray);
                          map.options.maxBoundsViscosity = 1.0;

                          // Prevent zooming out beyond district
                          const minZoom = map.getBoundsZoom(districtBoundsArray);
                          map.setMinZoom(minZoom);

                          map.on("zoomend", () => {
                            if (map.getZoom() < map.getMinZoom()) {
                              map.setZoom(map.getMinZoom());
                            }
                          });
                        }}
                      >
                        <TileLayer
                          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                          attribution="&copy; OpenStreetMap contributors"
                        />

                        <Rectangle
                          bounds={districtBoundsArray}
                          pathOptions={{ color: "#065f46", weight: 1, fillOpacity: 0 }}
                        />

                        <ClickHandler bbox={districtBbox} />

                        {selectedPoint && (
                          <Marker
                            position={[selectedPoint.lat, selectedPoint.lon]}
                            icon={greenIcon}
                          />
                        )}
                      </MapContainer>

                    </div>
                    {/* Selected coordinates preview (shown only after selecting a point) */}
                    {selectedPoint && (
                      <div className="mt-2 text-sm text-muted-foreground">
                        <div className="font-medium">Selected location:</div>
                        <div>Latitude: {selectedPoint.lat.toFixed(6)}</div>
                        <div>Longitude: {selectedPoint.lon.toFixed(6)}</div>
                      </div>
                    )}
                    <div className="mt-3 flex items-center justify-end gap-2">
                      <Button
                        type="button"
                        disabled={!selectedPoint}
                        onClick={() => {
                          if (!selectedPoint) return;
                          const coords = `${selectedPoint.lat.toFixed(6)}, ${selectedPoint.lon.toFixed(6)}`;
                          // Update existing profile state only (no auto-save)
                          setFormData({ ...formData, location: coords });
                          savedLocationRef.current = coords;
                          setMapVisible(false);
                          toast.success("Location selected. Click Save Changes to persist profile.");
                        }}
                      >
                        Confirm Location
                      </Button>
                    </div>
                  </Card>
                </div>
              )}
            </div>

            <div className="flex gap-4">
              <Button type="submit" className="bg-primary hover:bg-primary/90" disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
