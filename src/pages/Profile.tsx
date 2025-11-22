import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Camera, MapPin } from "lucide-react";
import { toast } from "sonner";
import { getCurrentUser, getUser, isAuthenticated, updateProfile, User } from "../services/api";


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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      const updatedUser = await updateProfile({
        name: formData.name,
        phone: formData.phone || undefined,
        crop: formData.crop || undefined,
        location: formData.location || undefined,
      });
      setUser(updatedUser);
      toast.success("Profile updated successfully!");
    } catch (error: any) {
      toast.error(error.message || "Failed to update profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleGeolocate = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
          setFormData({ ...formData, location: coords });
          toast.success("Location detected!");
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
                    <SelectItem value="soybean">Soybean</SelectItem>
                    <SelectItem value="onion">Onion</SelectItem>
                  </SelectContent>
                </Select>
              </div>

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
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label htmlFor="state">State</Label>
                <Input id="state" value={formData.state} disabled className="bg-muted" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="district">District</Label>
                <Input id="district" value={formData.district} disabled className="bg-muted" />
              </div>
            <div className="space-y-2">
                <Label htmlFor="village">Village / Town</Label>
                <Input id="village" value={formData.village} disabled className="bg-muted" />
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
