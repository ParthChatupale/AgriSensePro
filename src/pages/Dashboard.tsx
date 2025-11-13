import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CloudRain, TrendingUp, Satellite, AlertTriangle, RefreshCw, Sprout, Loader2 } from "lucide-react";
import { getDashboardData } from "@/services/api";
import type { DashboardResponse, Alert } from "@/types/fusion";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDashboardData();
      setDashboardData(data);
    } catch (err: any) {
      setError(err.message || "Unable to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const handleViewAdvisory = (crop?: string) => {
    if (crop) {
      navigate(`/advisory/${crop.toLowerCase()}`);
    } else {
      navigate("/advisory/cotton"); // Default to cotton if no crop specified
    }
  };

  // Format price with trend indicator
  const formatPrice = (price: number, changePercent: number) => {
    const trend = changePercent >= 0 ? "↑" : "↓";
    const color = changePercent >= 0 ? "text-success" : "text-destructive";
    return (
      <span className={`font-medium ${color}`}>
        {trend} ₹{price.toLocaleString("en-IN")}
      </span>
    );
  };

  // Get alert color based on level
  const getAlertColor = (level: string) => {
    switch (level) {
      case "high":
        return "destructive";
      case "medium":
        return "warning";
      case "low":
        return "info";
      default:
        return "default";
    }
  };

  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <Skeleton className="h-9 w-48 mb-2" />
            <Skeleton className="h-5 w-64" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <Skeleton className="h-8 w-24 mb-4" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );

  // Loading state
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen py-8 px-4 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-destructive" />
          <h2 className="text-2xl font-bold mb-2">Unable to Load Dashboard</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={handleRefresh} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Default values if data is missing
  const weather = dashboardData?.weather || {
    temperature: 28,
    humidity: 65,
    rainfall: 5,
    wind_speed: 12,
  };

  const market = dashboardData?.market || {};
  const alerts = dashboardData?.alerts || [];
  const cropHealth = dashboardData?.crop_health || {};

  // Calculate average health score
  const healthScores = Object.values(cropHealth).map((crop: any) => crop.health_score || 0);
  const avgHealthScore = healthScores.length > 0
    ? Math.round(healthScores.reduce((a, b) => a + b, 0) / healthScores.length)
    : 78;

  // Get health status text
  const getHealthStatus = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Fair";
    return "Poor";
  };

  // Get average market price for display
  const marketPrices = Object.values(market);
  const avgMarketPrice = marketPrices.length > 0
    ? Math.round(marketPrices.reduce((sum: number, crop: any) => sum + (crop.price || 0), 0) / marketPrices.length)
    : 2450;

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-heading font-bold text-primary mb-2">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Here's your farm overview</p>
          </div>
          <Button variant="outline" className="gap-2" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh Data
          </Button>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Weather Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Weather Summary</p>
                <h3 className="text-2xl font-bold">{weather.temperature}°C</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                <CloudRain className="h-6 w-6 text-secondary" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Humidity</span>
                <span className="font-medium">{weather.humidity}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Wind Speed</span>
                <span className="font-medium">{weather.wind_speed} km/h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Rainfall</span>
                <span className="font-medium">{weather.rainfall}mm</span>
              </div>
            </div>
            {/* 3-Day Forecast */}
            {weather.forecast && weather.forecast.next_3_days && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-xs text-muted-foreground mb-2">3-Day Forecast</p>
                <div className="space-y-1.5">
                  {weather.forecast.next_3_days.map((day: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-xs">
                      <span className="text-muted-foreground">Day {day.day}</span>
                      <span className="font-medium">{day.temp}°C • {day.rainfall}mm</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>

          {/* Market Prices Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Market Prices</p>
                <h3 className="text-2xl font-bold">₹{avgMarketPrice.toLocaleString("en-IN")}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              {market.wheat && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Wheat</span>
                  {formatPrice(market.wheat.price, market.wheat.change_percent)}
                </div>
              )}
              {market.rice && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Rice</span>
                  {formatPrice(market.rice.price, market.rice.change_percent)}
                </div>
              )}
              {market.cotton && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Cotton</span>
                  {formatPrice(market.cotton.price, market.cotton.change_percent)}
                </div>
              )}
              {market.sugarcane && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sugarcane</span>
                  {formatPrice(market.sugarcane.price, market.sugarcane.change_percent)}
                </div>
              )}
              {Object.keys(market).length === 0 && (
                <p className="text-sm text-muted-foreground">No market data available</p>
              )}
            </div>
          </Card>

          {/* NDVI Health Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Crop Health (NDVI)</p>
                <h3 className="text-2xl font-bold">{getHealthStatus(avgHealthScore)}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <Satellite className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div className="relative pt-1">
              <div className="overflow-hidden h-3 text-xs flex rounded-full bg-muted">
                <div
                  style={{ width: `${avgHealthScore}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-success"
                ></div>
              </div>
              <p className="text-sm text-muted-foreground mt-2">Health Score: {avgHealthScore}%</p>
            </div>
          </Card>
        </div>

        {/* Individual Crop Health Cards */}
        {Object.keys(cropHealth).length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-heading font-bold mb-4">Crop Health Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(cropHealth).map(([cropName, health]: [string, any]) => {
                const healthScore = health.health_score || 0;
                const healthColor = healthScore >= 80 ? "text-success" : healthScore >= 60 ? "text-warning" : "text-destructive";
                const healthStatus = healthScore >= 80 ? "Good" : healthScore >= 60 ? "Warning" : "Risk";
                return (
                  <Card key={cropName} className="p-4 hover:shadow-hover transition-all">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold capitalize">{cropName}</h4>
                      <Badge variant={healthScore >= 80 ? "default" : healthScore >= 60 ? "secondary" : "destructive"}>
                        {healthStatus}
                      </Badge>
                    </div>
                    <div className="space-y-1.5 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">NDVI</span>
                        <span className="font-medium">{health.ndvi?.toFixed(2) || "N/A"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Soil Moisture</span>
                        <span className="font-medium">{health.soil_moisture || 0}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Stage</span>
                        <span className="font-medium capitalize">{health.crop_stage || "N/A"}</span>
                      </div>
                      <div className="mt-2 pt-2 border-t">
                        <div className="flex justify-between items-center">
                          <span className="text-muted-foreground text-xs">Health Score</span>
                          <span className={`font-bold ${healthColor}`}>{healthScore}%</span>
                        </div>
                        <div className="mt-1 h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full ${healthScore >= 80 ? "bg-success" : healthScore >= 60 ? "bg-warning" : "bg-destructive"}`}
                            style={{ width: `${healthScore}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* Risk Alerts Section */}
        {alerts.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-warning" />
              <h2 className="text-xl font-heading font-bold">Risk Alerts</h2>
              <span className="text-sm text-muted-foreground">
                ({dashboardData?.summary?.high_priority_count || 0} high priority)
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {alerts.map((alert: Alert) => {
                const badgeVariant = alert.level === "high" ? "destructive" : alert.level === "medium" ? "secondary" : "default";
                return (
                  <Card
                    key={alert.id}
                    className={`p-4 border-l-4 hover:shadow-hover transition-all ${
                      alert.level === "high"
                        ? "border-l-destructive"
                        : alert.level === "medium"
                        ? "border-l-warning"
                        : "border-l-info"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold">{alert.title}</h4>
                      <Badge variant={badgeVariant} className="text-xs">
                        {alert.level.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-muted-foreground">Confidence</span>
                        <span className="font-medium">{alert.confidence}%</span>
                      </div>
                      {alert.description && (
                        <p className="text-xs text-muted-foreground mt-2">{alert.description}</p>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full mt-2"
                        onClick={() => handleViewAdvisory(alert.crop)}
                      >
                        View Advisory
                      </Button>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* Motivational Banner */}
        <Card className="p-6 bg-gradient-hero text-white text-center">
          <Sprout className="h-8 w-8 mx-auto mb-3 animate-float" />
          <p className="text-lg font-medium">"Healthy soil, happy harvest 🌾"</p>
          <p className="text-sm opacity-90 mt-2">Keep nurturing your land with smart decisions</p>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
