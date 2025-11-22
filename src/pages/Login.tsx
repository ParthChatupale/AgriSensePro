import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { loginUser } from "../services/api";


const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    setIsLoading(true);
    try {
      const response = await loginUser({ email, password });
      toast.success(response.message || "Login successful!");
      navigate("/dashboard");
    } catch (error: any) {
      // Show specific error message from API
      const errorMessage = error.message || "Invalid email or password. Please try again.";
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
          <h1 className="text-3xl font-heading font-bold text-primary mb-2">Welcome Back</h1>
          <p className="text-muted-foreground">Sign in to continue to krushiRakshak</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="farmer@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="flex items-center justify-between text-sm">
            <Link to="/forgot-password" className="text-primary hover:underline">
              Forgot password?
            </Link>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90"
            disabled={isLoading}
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm">
          <p className="text-muted-foreground">
            Don't have an account?{" "}
            <Link to="/signup" className="text-primary font-semibold hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Login;
