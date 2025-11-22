import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { signupUser } from "../services/api";

const Signup = () => {
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    password: "",
    userType: "",
  });
  const [coords, setCoords] = useState<{ lat?: number; lon?: number }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const navigate = useNavigate();

  const detectLocation = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation is not supported by your browser");
      return;
    }
    setDetecting(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoords({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
        toast.success("Location detected successfully");
        setDetecting(false);
      },
      () => {
        toast.error("Unable to detect location");
        setDetecting(false);
      }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.password || !formData.userType) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (!coords.lat || !coords.lon) {
      toast.info("Detecting GPS will help customize advisories");
    }

    setIsLoading(true);
    try {
      const response = await signupUser({
        name: formData.name,
        phone: formData.phone || undefined,
        email: formData.email,
        password: formData.password,
        userType: formData.userType,
        latitude: coords.lat,
        longitude: coords.lon,
      });
      toast.success(response.message || "Account created successfully!");
      navigate("/dashboard");
    } catch (error: any) {
      const errorMessage = error.message || "Failed to create account. Please try again.";
      toast.error(errorMessage, {
        duration: 4000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gradient-to-br from-background via-muted/30 to-background">
      <Card className="w-full max-w-md p-8 shadow-hover bg-gradient-card">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-hero text-white mb-4">
            <span className="text-3xl">🌿</span>
          </div>
          <h1 className="text-3xl font-heading font-bold text-primary mb-2">Join krushiRakshak</h1>
          <p className="text-muted-foreground">Create your account to get started</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full Name *</Label>
            <Input
              id="name"
              type="text"
              placeholder="Enter your full name"
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
              placeholder="+91 1234567890"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email *</Label>
            <Input
              id="email"
              type="email"
              placeholder="farmer@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password *</Label>
            <Input
              id="password"
              type="password"
              placeholder="Create a strong password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="userType">I am a *</Label>
            <Select
              value={formData.userType}
              onValueChange={(value) => setFormData({ ...formData, userType: value })}
              required
            >
              <SelectTrigger>
                <SelectValue placeholder="Select your role" />
              </SelectTrigger>
              <SelectContent className="bg-popover">
                <SelectItem value="farmer">Farmer</SelectItem>
                <SelectItem value="expert">Agricultural Expert</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Location (auto-detected)</Label>
            <div className="flex items-center gap-2">
              <Button type="button" variant="outline" onClick={detectLocation} disabled={detecting}>
                {detecting ? "Detecting..." : "Detect Location"}
              </Button>
              <span className="text-xs text-muted-foreground">
                {coords.lat && coords.lon
                  ? `Lat ${coords.lat.toFixed(4)}, Lon ${coords.lon.toFixed(4)}`
                  : "GPS helps tailor advisories"}
              </span>
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 mt-6"
            disabled={isLoading}
          >
            {isLoading ? "Creating account..." : "Create Account"}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm">
          <p className="text-muted-foreground">
            Already have an account?{" "}
            <Link to="/login" className="text-primary font-semibold hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Signup;
