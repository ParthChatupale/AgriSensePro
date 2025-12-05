import { useState, useEffect, useMemo, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CloudRain, TrendingUp, Satellite, AlertTriangle, RefreshCw, Sprout, Thermometer, Droplets, Bug, ArrowUpRight, ArrowDownRight, ArrowRight } from "lucide-react";
import { getDashboardData, getCurrentUser } from "@/services/api";
import type { DashboardResponse, Alert } from "@/types/fusion";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

// Lightweight advisory type to read new fields if present
type AdvisoryLite = {
  summary?: string;
  severity?: "low" | "medium" | "high" | string;
  alerts?: { type: string; message: string }[];
  metrics?: {
    ndvi?: number;
    soil_moisture?: number;
    market_price?: number;
    temperature?: number;
    humidity?: number;
    rainfall?: number;
  };
};

const Dashboard = () => {
  const { t } = useTranslation();
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userCrop, setUserCrop] = useState<string | null>(null);
  const [userLocation, setUserLocation] = useState<string | null>(null);
  const [userCoords, setUserCoords] = useState<{ lat?: number; lon?: number }>({});
  const [advisory, setAdvisory] = useState<AdvisoryLite | null>(null);
  const navigate = useNavigate();

  const fetchDashboardData = useCallback(async (crop?: string | null, coords?: { lat?: number; lon?: number }, location?: string | null) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDashboardData(
        crop || undefined,
        coords?.lat,
        coords?.lon,
        location || undefined
      );
      setDashboardData(data);

      // Fetch advisory for user's crop if set
      if (crop) {
        const res = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/fusion/advisory/${encodeURIComponent(crop)}`);
        if (res.ok) {
          const adv = (await res.json()) as AdvisoryLite;
          setAdvisory(adv);
        } else {
          setAdvisory(null);
        }
      } else {
        setAdvisory(null);
      }
    } catch (err: any) {
      setError(err.message || t("dashboard.error.load_failed"));
    } finally {
      setIsLoading(false);
    }
  }, [t]);

  useEffect(() => {
    const loadUserProfile = async () => {
      try {
        const user = await getCurrentUser();
        let crop: string | null = null;
        let coords: { lat?: number; lon?: number } = {};
        let location: string | null = null;
        
        if (user.crop) crop = user.crop;
        if (user.location) {
          location = user.location;
          // Parse location string (format: "lat, lon" or "lat,lon")
          const locationStr = user.location.trim();
          const parts = locationStr.split(/[,\s]+/).filter(p => p);
          if (parts.length >= 2) {
            const lat = parseFloat(parts[0]);
            const lon = parseFloat(parts[1]);
            if (!isNaN(lat) && !isNaN(lon)) {
              coords = { lat, lon };
            }
          }
        }
        
        setUserCrop(crop);
        setUserLocation(location);
        setUserCoords(coords);
        
        // Fetch dashboard data with loaded profile info
        await fetchDashboardData(crop, coords, location);
      } catch {
        // If profile load fails, still fetch dashboard with defaults
        await fetchDashboardData(null, {}, null);
      }
    };
    loadUserProfile();
  }, []);

  useEffect(() => {
    // Refetch when userCrop or coordinates change (e.g., after profile update)
    if (userCrop !== null || userCoords.lat !== undefined || userCoords.lon !== undefined) {
      fetchDashboardData(userCrop, userCoords, userLocation);
    }
  }, [userCrop, userCoords.lat, userCoords.lon, userLocation, fetchDashboardData]);

  const handleRefresh = () => fetchDashboardData(userCrop, userCoords, userLocation);

  const handleViewAdvisory = (crop?: string) => {
    if (crop) navigate(`/advisory/${crop.toLowerCase()}`);
    else navigate("/advisory/cotton");
  };

  const formatPrice = (price: number, changePercent: number) => {
    const trend = changePercent >= 0 ? "↑" : "↓";
    const color = changePercent >= 0 ? "text-success" : "text-destructive";
    return (
      <span className={`font-medium ${color}`}>
        {trend} ₹{price.toLocaleString("en-IN")}
      </span>
    );
  };

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

  const getNdviStatus = (value: number | null) => {
    if (value == null) {
      return { label: t("dashboard.ndvi.status.unknown"), badgeClass: "bg-muted text-muted-foreground" };
    }
    if (value > 0.6) {
      return { label: t("dashboard.ndvi.status.good"), badgeClass: "bg-success/15 text-success" };
    }
    if (value >= 0.4) {
      return { label: t("dashboard.ndvi.status.moderate"), badgeClass: "bg-warning/15 text-warning" };
    }
    return { label: t("dashboard.ndvi.status.poor"), badgeClass: "bg-destructive/15 text-destructive" };
  };

  const getTrendInfo = (change: number | null) => {
    if (change == null) {
      return { icon: ArrowRight, color: "text-muted-foreground", label: t("dashboard.ndvi.trend.no_data") };
    }
    if (change > 0.02) {
      return { icon: ArrowUpRight, color: "text-success", label: t("dashboard.ndvi.trend.rising") };
    }
    if (change < -0.02) {
      return { icon: ArrowDownRight, color: "text-destructive", label: t("dashboard.ndvi.trend.dropping") };
    }
    return { icon: ArrowRight, color: "text-warning", label: t("dashboard.ndvi.trend.steady") };
  };

  const formatTimestamp = (iso?: string) => {
    if (!iso) return "—";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return iso;
    return date.toLocaleString();
  };

  const ndviData = dashboardData?.ndvi;
  const ndviLatest = typeof ndviData?.latest === "number" ? ndviData.latest : null;
  const ndviChange = typeof ndviData?.change === "number" ? ndviData.change : null;
  const ndviHistoryRaw = Array.isArray(ndviData?.history) ? ndviData.history : [];
  const ndviHistory = useMemo(
    () =>
      ndviHistoryRaw
        .filter((entry: any) => entry && typeof entry.ndvi === "number")
        .slice(-7),
    [ndviHistoryRaw]
  );

  const sparklinePoints = useMemo(() => {
    const values = ndviHistory.map((entry: any) => entry.ndvi as number);
    if (!values.length) {
      if (ndviLatest != null) {
        values.push(ndviLatest, ndviLatest);
      } else {
        return null;
      }
    } else if (values.length === 1) {
      values.push(values[0]);
    }

    const max = Math.max(...values);
    const min = Math.min(...values);
    const height = 40;
    const width = 100;
    const range = max - min || 0.0001;

    return values
      .map((value, index) => {
        const x = (index / (values.length - 1)) * width;
        const y = height - ((value - min) / range) * height;
        return `${x},${y}`;
      })
      .join(" ");
  }, [ndviHistory, ndviLatest]);

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

  if (isLoading) return <LoadingSkeleton />;

  if (error) {
    return (
      <div className="min-h-screen py-8 px-4 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-destructive" />
          <h2 className="text-2xl font-bold mb-2">{t("dashboard.error.title")}</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={handleRefresh} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t("dashboard.error.try_again")}
          </Button>
        </div>
      </div>
    );
  }

  const weather = dashboardData?.weather || { temperature: 28, humidity: 65, rainfall: 5, wind_speed: 12 };
  const market = dashboardData?.market || {};
  const alerts = dashboardData?.alerts || [];
  const cropHealth = dashboardData?.crop_health || {};

  const ndviStatus = getNdviStatus(ndviLatest);
  const ndviTrend = getTrendInfo(ndviChange);
  const TrendIcon = ndviTrend.icon;
  const formattedNdviChange = ndviChange != null ? `${ndviChange > 0 ? "+" : ""}${ndviChange.toFixed(3)}` : null;
  const lastUpdated = formatTimestamp(dashboardData?.weather?.timestamp);
  const sparklineColor = ndviStatus.label === "Good" ? "text-success" : ndviStatus.label === "Moderate" ? "text-warning" : ndviStatus.label === "Poor" ? "text-destructive" : "text-muted-foreground";

  const marketPrices = Object.values(market);
  const avgMarketPrice = marketPrices.length > 0 ? Math.round(marketPrices.reduce((sum: number, crop: any) => sum + (crop.price || 0), 0) / marketPrices.length) : 2450;

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-heading font-bold text-primary mb-2">{t("dashboard.title")}</h1>
            <p className="text-muted-foreground">{t("dashboard.subtitle")}</p>
          </div>
          <Button variant="outline" className="gap-2" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            {t("dashboard.refresh")}
          </Button>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Weather Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{t("dashboard.weather.title")}</p>
                <h3 className="text-2xl font-bold">{weather.temperature}°C</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                <CloudRain className="h-6 w-6 text-secondary" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.humidity")}</span><span className="font-medium">{weather.humidity}%</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.wind_speed")}</span><span className="font-medium">{weather.wind_speed} km/h</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.rainfall")}</span><span className="font-medium">{weather.rainfall}mm</span></div>
            </div>
          </Card>

          {/* Market Prices Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{t("dashboard.market.title")}</p>
                <h3 className="text-2xl font-bold">₹{avgMarketPrice.toLocaleString("en-IN")}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              {market.wheat && (<div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.market.wheat")}</span>{formatPrice(market.wheat.price, market.wheat.change_percent)}</div>)}
              {market.rice && (<div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.market.rice")}</span>{formatPrice(market.rice.price, market.rice.change_percent)}</div>)}
              {market.cotton && (<div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.market.cotton")}</span>{formatPrice(market.cotton.price, market.cotton.change_percent)}</div>)}
              {market.sugarcane && (<div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.market.sugarcane")}</span>{formatPrice(market.sugarcane.price, market.sugarcane.change_percent)}</div>)}
              {Object.keys(market).length === 0 && (<p className="text-sm text-muted-foreground">{t("dashboard.market.no_data")}</p>)}
            </div>
          </Card>

          {/* NDVI Insight Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{t("dashboard.ndvi.title")}</p>
                {ndviLatest != null ? (
                  <div className="flex items-baseline gap-3">
                    <h3 className="text-3xl font-bold">{ndviLatest.toFixed(2)}</h3>
                    <span className={`text-xs font-medium px-2 py-1 rounded-full tracking-wide ${ndviStatus.badgeClass}`}>
                      {ndviStatus.label}
                    </span>
                  </div>
                ) : (
                  <h3 className="text-2xl font-bold text-muted-foreground">{t("dashboard.ndvi.unavailable")}</h3>
                )}
              </div>
              <div className="w-12 h-12 rounded-full bg-primary/15 flex items-center justify-center">
                <Satellite className="h-6 w-6 text-primary" />
              </div>
            </div>

            {ndviLatest != null ? (
              <>
                <div className="flex items-center gap-2 text-sm mb-4">
                  <TrendIcon className={`h-4 w-4 ${ndviTrend.color}`} />
                  <span className="font-medium">{ndviTrend.label}</span>
                  {formattedNdviChange && <span className="text-muted-foreground">({formattedNdviChange})</span>}
                </div>
                <div className="h-16 mb-4">
                  {sparklinePoints ? (
                    <svg viewBox="0 0 100 40" className="w-full h-full">
                      <polyline
                        fill="none"
                        vectorEffect="non-scaling-stroke"
                        strokeWidth={2.5}
                        className={sparklineColor}
                        stroke="currentColor"
                        points={sparklinePoints}
                      />
                      <line x1="0" y1="36" x2="100" y2="36" stroke="currentColor" strokeWidth={0.75} strokeOpacity={0.2} className="text-muted-foreground" />
                    </svg>
                  ) : (
                    <div className="w-full h-full rounded-md bg-muted flex items-center justify-center text-xs text-muted-foreground">
                      {t("dashboard.ndvi.no_history")}
                    </div>
                  )}
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{t("dashboard.ndvi.last_updated", { time: lastUpdated })}</span>
                  <span>{t("dashboard.ndvi.trend_7day")}</span>
                </div>
              </>
            ) : (
              <div className="space-y-3">
                <div className="w-full h-16 rounded-md bg-muted" />
                <p className="text-sm text-muted-foreground">{t("dashboard.ndvi.unavailable")}</p>
                <p className="text-xs text-muted-foreground">{t("dashboard.ndvi.last_updated", { time: lastUpdated })}</p>
              </div>
            )}
          </Card>
        </div>

        {/* New: Advisory-driven Cards (if user crop set and advisory loaded) */}
        {userCrop && advisory && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* Crop Health (NDVI) */}
            <Card className="p-6 hover:shadow-hover transition-all">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t("dashboard.advisory.ndvi_title", { crop: userCrop })}</p>
                  <h3 className="text-2xl font-bold">{advisory.metrics?.ndvi?.toFixed(2) ?? "-"}</h3>
                </div>
                <Satellite className="h-6 w-6 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground">{t("dashboard.advisory.ndvi_desc")}</p>
            </Card>

            {/* Soil Moisture */}
            <Card className="p-6 hover:shadow-hover transition-all">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t("dashboard.advisory.soil_moisture")}</p>
                  <h3 className="text-2xl font-bold">{advisory.metrics?.soil_moisture != null ? `${Math.round((advisory.metrics?.soil_moisture ?? 0)*100)}%` : "-"}</h3>
                </div>
                <Droplets className="h-6 w-6 text-info" />
              </div>
              <p className="text-sm text-muted-foreground">{t("dashboard.advisory.soil_moisture_desc")}</p>
            </Card>

            {/* Weather snapshot from advisory metrics if present */}
            <Card className="p-6 hover:shadow-hover transition-all">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t("dashboard.advisory.weather_snapshot")}</p>
                  <h3 className="text-2xl font-bold">{advisory.metrics?.temperature ?? "-"}°C</h3>
                </div>
                <Thermometer className="h-6 w-6 text-secondary" />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.humidity")}</span><span className="font-medium">{advisory.metrics?.humidity ?? "-"}%</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.rainfall")}</span><span className="font-medium">{advisory.metrics?.rainfall ?? "-"}mm</span></div>
              </div>
            </Card>

            {/* Pest Alert */}
            <Card className="p-6 hover:shadow-hover transition-all">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t("dashboard.advisory.pest_alerts")}</p>
                  <h3 className="text-2xl font-bold">{(advisory.alerts || []).filter(a => a.type === "pest").length}</h3>
                </div>
                <Bug className="h-6 w-6 text-destructive" />
              </div>
              <ul className="text-sm space-y-1">
                {(advisory.alerts || []).filter(a => a.type === "pest").slice(0,3).map((a, i) => (
                  <li key={i} className="text-muted-foreground">• {a.message}</li>
                ))}
                {((advisory.alerts || []).filter(a => a.type === "pest").length === 0) && (
                  <li className="text-muted-foreground">{t("dashboard.advisory.no_pest")}</li>
                )}
              </ul>
            </Card>

            {/* Market Trend */}
            <Card className="p-6 hover:shadow-hover transition-all">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t("dashboard.advisory.market_price")}</p>
                  <h3 className="text-2xl font-bold">{advisory.metrics?.market_price ? `₹${advisory.metrics?.market_price.toLocaleString("en-IN")}` : "-"}</h3>
                </div>
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
              <p className="text-sm text-muted-foreground">{t("dashboard.advisory.market_price_desc", { crop: userCrop })}</p>
            </Card>
          </div>
        )}

        {/* Individual Crop Health Cards */}
        {Object.keys(cropHealth).length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-heading font-bold mb-4">{t("dashboard.crop_health.title")}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(cropHealth).map(([cropName, health]: [string, any]) => {
                const healthScore = health.health_score || 0;
                const healthColor = healthScore >= 80 ? "text-success" : healthScore >= 60 ? "text-warning" : "text-destructive";
                const healthStatus = healthScore >= 80 ? t("dashboard.crop_health.status.good") : healthScore >= 60 ? t("dashboard.crop_health.status.warning") : t("dashboard.crop_health.status.risk");
                const isUserCrop = userCrop && cropName.toLowerCase() === userCrop.toLowerCase();
                return (
                  <Card 
                    key={cropName} 
                    className={`p-4 hover:shadow-hover transition-all ${isUserCrop ? "ring-2 ring-primary" : ""}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold capitalize">
                        {cropName}
                        {isUserCrop && <span className="ml-2 text-xs text-primary">{t("dashboard.crop_health.your_crop")}</span>}
                      </h4>
                      <Badge variant={healthScore >= 80 ? "default" : healthScore >= 60 ? "secondary" : "destructive"}>
                        {healthStatus}
                      </Badge>
                    </div>
                    <div className="space-y-1.5 text-sm">
                      <div className="flex justify-between"><span className="text-muted-foreground">NDVI</span><span className="font-medium">{health.ndvi?.toFixed(2) || "N/A"}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.advisory.soil_moisture")}</span><span className="font-medium">{health.soil_moisture || 0}%</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.crop_health.stage")}</span><span className="font-medium capitalize">{health.crop_stage || "N/A"}</span></div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* Risk Alerts Section (existing) */}
        {alerts.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-warning" />
              <h2 className="text-xl font-heading font-bold">{t("dashboard.alerts.title")}</h2>
              <span className="text-sm text-muted-foreground">{t("dashboard.alerts.high_priority", { count: dashboardData?.summary?.high_priority_count || 0 })}</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {alerts.map((alert: Alert) => {
                const badgeVariant = alert.level === "high" ? "destructive" : alert.level === "medium" ? "secondary" : "default";
                return (
                  <Card key={alert.id} className={`p-4 border-l-4 hover:shadow-hover transition-all ${alert.level === "high" ? "border-l-destructive" : alert.level === "medium" ? "border-l-warning" : "border-l-info"}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold">{alert.title}</h4>
                      <Badge variant={badgeVariant} className="text-xs">{alert.level.toUpperCase()}</Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-muted-foreground">{t("dashboard.alerts.confidence")}</span>
                        <span className="font-medium">{alert.confidence}%</span>
                      </div>
                      {alert.description && (<p className="text-xs text-muted-foreground mt-2">{alert.description}</p>)}
                      <Button variant="outline" size="sm" className="w-full mt-2" onClick={() => handleViewAdvisory(alert.crop)}>{t("dashboard.alerts.view_advisory")}</Button>
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
          <p className="text-lg font-medium">{t("dashboard.motivational.quote")}</p>
          <p className="text-sm opacity-90 mt-2">{t("dashboard.motivational.subtitle")}</p>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
