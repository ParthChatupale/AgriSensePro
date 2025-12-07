import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Camera, MapPin } from "lucide-react";
import { toast } from "sonner";
import { getCurrentUser, getUser, isAuthenticated, updateProfile, User, getDistricts, getStates } from "../services/api";


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
            
            // Update formData with location and reverse geocoded results
            setFormData({
              ...formData,
              location: coords,
              state: updatedUser.state || "",
              district: updatedUser.district || "",
              village: updatedUser.village || "",
            });
            setUser(updatedUser);
            // Update saved location ref
            savedLocationRef.current = coords;
            toast.success("Location detected and reverse geocoded!");
          } catch (error: any) {
            // If auto-save fails, still update location in form
            setFormData({ ...formData, location: coords });
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
                    </div>
                  </div>

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
