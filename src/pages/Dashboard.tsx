import { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CloudRain, TrendingUp, Satellite, AlertTriangle, RefreshCw, Sprout, Thermometer, Droplets, Bug, ArrowUpRight, ArrowDownRight, ArrowRight, Map as MapIcon, Loader2 } from "lucide-react";
import { getDashboardData, getCurrentUser } from "@/services/api";
import type { DashboardResponse, Alert } from "@/types/fusion";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { NdviModal } from "@/components/NdviModal";

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
  const [userState, setUserState] = useState<string | null>(null);
  const [userDistrict, setUserDistrict] = useState<string | null>(null);
  const [advisory, setAdvisory] = useState<AdvisoryLite | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [ndviImage, setNdviImage] = useState<string | null>(null);
  const [ndviStats, setNdviStats] = useState<any>(null);
  const [ndviLoading, setNdviLoading] = useState(false);
  const [ndviError, setNdviError] = useState<string | null>(null);
  // Real NDVI stats from API (for dashboard display)
  const [realNdviStats, setRealNdviStats] = useState<{ mean?: number; min?: number; max?: number; valid_pixels?: number } | null>(null);
  const [realNdviLoading, setRealNdviLoading] = useState(false);
  // Store job ID and image URL from initial NDVI fetch to reuse in modal
  const [realNdviJobId, setRealNdviJobId] = useState<string | null>(null);
  const [realNdviImageUrl, setRealNdviImageUrl] = useState<string | null>(null);
  // Real NDVI time series history (for graph)
  const [realNdviHistory, setRealNdviHistory] = useState<Array<{ date: string; mean: number }>>([]);
  const [realNdviHistoryLoading, setRealNdviHistoryLoading] = useState(false);
  // Flag to prevent multiple NDVI requests
  const ndviRequestInProgress = useRef(false);
  // Track last coordinates we fetched NDVI for to prevent duplicate requests
  const lastNdviCoords = useRef<{ lat: number; lon: number } | null>(null);
  // Track last coordinates we fetched timeseries for to prevent duplicate requests
  const lastTimeseriesCoords = useRef<{ lat: number; lon: number } | null>(null);
  // Flag to prevent multiple timeseries requests
  const timeseriesRequestInProgress = useRef(false);
  const navigate = useNavigate();

  // Interpolate missing dates in NDVI timeseries using linear interpolation
  const interpolateNdviTimeseries = (
    data: Array<{ date: string; mean: number }>,
    days: number = 7
  ): Array<{ date: string; mean: number }> => {
    if (data.length === 0) return [];
    
    // Generate all dates for the past N days
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const allDates: string[] = [];
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      allDates.push(date.toISOString().split('T')[0]);
    }
    
    // Create a map of available data points
    const dataMap = new Map<string, number>();
    data.forEach(item => {
      dataMap.set(item.date, item.mean);
    });
    
    // Interpolate missing dates
    const interpolated: Array<{ date: string; mean: number }> = [];
    
    for (let i = 0; i < allDates.length; i++) {
      const currentDate = allDates[i];
      
      // If we have data for this date, use it
      if (dataMap.has(currentDate)) {
        interpolated.push({ date: currentDate, mean: dataMap.get(currentDate)! });
        continue;
      }
      
      // Otherwise, find the nearest data points before and after
      let beforeDate: string | null = null;
      let beforeValue: number | null = null;
      let afterDate: string | null = null;
      let afterValue: number | null = null;
      
      // Look backwards for the nearest data point
      for (let j = i - 1; j >= 0; j--) {
        const checkDate = allDates[j];
        if (dataMap.has(checkDate)) {
          beforeDate = checkDate;
          beforeValue = dataMap.get(checkDate)!;
          break;
        }
      }
      
      // Look forwards for the nearest data point
      for (let j = i + 1; j < allDates.length; j++) {
        const checkDate = allDates[j];
        if (dataMap.has(checkDate)) {
          afterDate = checkDate;
          afterValue = dataMap.get(checkDate)!;
          break;
        }
      }
      
      // Interpolate based on available neighbors
      if (beforeValue !== null && afterValue !== null && beforeDate && afterDate) {
        // Linear interpolation between two points
        const beforeTime = new Date(beforeDate).getTime();
        const afterTime = new Date(afterDate).getTime();
        const currentTime = new Date(currentDate).getTime();
        const ratio = (currentTime - beforeTime) / (afterTime - beforeTime);
        const interpolatedValue = beforeValue + (afterValue - beforeValue) * ratio;
        interpolated.push({ date: currentDate, mean: interpolatedValue });
      } else if (beforeValue !== null) {
        // Only have data before - forward fill
        interpolated.push({ date: currentDate, mean: beforeValue });
      } else if (afterValue !== null) {
        // Only have data after - backward fill
        interpolated.push({ date: currentDate, mean: afterValue });
      } else {
        // No data at all - skip this date (shouldn't happen if we have at least one data point)
        continue;
      }
    }
    
    return interpolated;
  };

  // Fetch real NDVI time series data from API (runs in parallel)
  const fetchNdviTimeSeries = async (coords: { lat?: number; lon?: number }, days: number = 7) => {
    console.log("[Dashboard] fetchNdviTimeSeries called with coords:", coords);
    
    // Only fetch if we have valid coordinates
    if (!coords.lat || !coords.lon) {
      console.log("[Dashboard] ❌ No coordinates provided, skipping timeseries fetch");
      setRealNdviHistory([]);
      return;
    }

    // Check if we already fetched for these exact coordinates
    if (lastTimeseriesCoords.current && 
        lastTimeseriesCoords.current.lat === coords.lat && 
        lastTimeseriesCoords.current.lon === coords.lon) {
      console.log("[Dashboard] ⏭️ Already fetched for these coordinates, skipping");
      return;
    }

    // Prevent multiple simultaneous requests
    if (timeseriesRequestInProgress.current) {
      console.log("[Dashboard] ⏭️ Request already in progress, skipping");
      return;
    }

    timeseriesRequestInProgress.current = true;
    setRealNdviHistoryLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const url = `${API_URL}/api/ndvi/timeseries?lat=${coords.lat}&lon=${coords.lon}&days=${days}`;
      console.log("[Dashboard] 🌐 Fetching NDVI timeseries from:", url);
      
      const res = await fetch(url);

      console.log("[Dashboard] 📡 API Response status:", res.status, res.statusText);

      if (!res.ok) {
        const errorText = await res.text();
        console.error("[Dashboard] ❌ API request failed:", res.status, errorText);
        setRealNdviHistory([]);
        return;
      }

      const data = await res.json();
      console.log("[Dashboard] 📦 API Response data:", data);
      
      if (data.ndvi && Array.isArray(data.ndvi)) {
        console.log("[Dashboard] ✅ Received", data.ndvi.length, "raw NDVI data points");
        // Interpolate missing dates to get exactly 7 values
        const interpolated = interpolateNdviTimeseries(data.ndvi, days);
        console.log("[Dashboard] NDVI timeseries - Raw:", data.ndvi.length, "Interpolated:", interpolated.length);
        console.log("[Dashboard] Interpolated values:", interpolated.map(i => `${i.date}: ${i.mean.toFixed(4)}`).join(", "));
        if (interpolated.length >= 7) {
          const first = interpolated[0].mean;
          const last = interpolated[interpolated.length - 1].mean;
          const change = last - first;
          console.log("[Dashboard] Calculated change:", change.toFixed(4), `(${last.toFixed(4)} - ${first.toFixed(4)})`);
        }
        setRealNdviHistory(interpolated);
        console.log("[Dashboard] ✅ Successfully stored", interpolated.length, "interpolated values in realNdviHistory");
        // Update last fetched coordinates
        lastTimeseriesCoords.current = { lat: coords.lat, lon: coords.lon };
      } else {
        console.log("[Dashboard] ❌ No NDVI timeseries data in response. Response structure:", Object.keys(data));
        setRealNdviHistory([]);
      }
    } catch (err) {
      // Log error instead of silently failing
      console.error("[Dashboard] ❌ Error fetching NDVI timeseries:", err);
      if (err instanceof Error) {
        console.error("[Dashboard] Error message:", err.message);
        console.error("[Dashboard] Error stack:", err.stack);
      }
      setRealNdviHistory([]);
    } finally {
      setRealNdviHistoryLoading(false);
      timeseriesRequestInProgress.current = false;
    }
  };

  // Fetch real NDVI data from API (runs in parallel)
  const fetchNdviData = async (coords: { lat?: number; lon?: number }) => {
    // Only fetch if we have valid coordinates
    if (!coords.lat || !coords.lon) {
      setRealNdviStats(null);
      return;
    }

    // Check if we already fetched for these exact coordinates
    if (lastNdviCoords.current && 
        lastNdviCoords.current.lat === coords.lat && 
        lastNdviCoords.current.lon === coords.lon) {
      // Already fetched for these coordinates, skip
      return;
    }

    // Prevent multiple simultaneous requests
    if (ndviRequestInProgress.current) {
      return;
    }

    ndviRequestInProgress.current = true;
    setRealNdviLoading(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/ndvi/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: coords.lat,
          lon: coords.lon,
          radius: 250,
        }),
      });

      if (!res.ok) {
        // Don't show error for NDVI - it's optional data
        setRealNdviStats(null);
        setRealNdviJobId(null);
        setRealNdviImageUrl(null);
        return;
      }

      const data = await res.json();

      if (data.status === "ok" && data.stats && data.job) {
        setRealNdviStats(data.stats);
        setRealNdviJobId(data.job);
        // Store image URL for later use
        const imgUrl = `${API_URL}/api/ndvi/image/${data.job}/${data.job}_visual.png`;
        setRealNdviImageUrl(imgUrl);
        // Update last fetched coordinates
        lastNdviCoords.current = { lat: coords.lat, lon: coords.lon };
      } else {
        setRealNdviStats(null);
        setRealNdviJobId(null);
        setRealNdviImageUrl(null);
      }
    } catch (err) {
      // Silently fail - NDVI is optional, don't block dashboard
      setRealNdviStats(null);
      setRealNdviJobId(null);
      setRealNdviImageUrl(null);
    } finally {
      setRealNdviLoading(false);
      ndviRequestInProgress.current = false;
    }
  };

  const fetchDashboardData = async (
    crop?: string | null, 
    coords?: { lat?: number; lon?: number }, 
    location?: string | null,
    state?: string | null,
    district?: string | null
  ) => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch dashboard data and NDVI data in parallel
      const [dashboardResult, advisoryResult] = await Promise.all([
        // Main dashboard data
        (async () => {
          const params = new URLSearchParams();
          if (crop) {
            params.append("crop", crop);
          }
          
          // If manual state/district are provided, use those; otherwise use coordinates/location
          if (state && district) {
            params.append("state", state);
            params.append("district", district);
          } else if (coords?.lat !== undefined && coords?.lon !== undefined) {
            params.append("latitude", coords.lat.toString());
            params.append("longitude", coords.lon.toString());
          } else if (location) {
            params.append("location", location);
          }
          
          return await getDashboardData(
            crop || undefined,
            coords?.lat,
            coords?.lon,
            location || undefined,
            state || undefined,
            district || undefined
          );
        })(),
        // Advisory data (if crop is set)
        crop ? (async () => {
          try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/fusion/advisory/${encodeURIComponent(crop)}`);
            if (res.ok) {
              return (await res.json()) as AdvisoryLite;
            }
            return null;
          } catch {
            return null;
          }
        })() : Promise.resolve(null),
      ]);

      setDashboardData(dashboardResult);
      setAdvisory(advisoryResult);

      // Fetch NDVI data in parallel (non-blocking)
      console.log("[Dashboard] fetchDashboardData - Checking coords for NDVI fetch:", {
        coords,
        hasLat: !!coords?.lat,
        hasLon: !!coords?.lon,
        latValue: coords?.lat,
        lonValue: coords?.lon
      });
      
      if (coords?.lat && coords?.lon) {
        console.log("[Dashboard] ✅ Coordinates available, calling fetchNdviTimeSeries");
        Promise.all([
          fetchNdviData(coords).catch((err) => {
            console.error("[Dashboard] ❌ fetchNdviData failed:", err);
          }),
          fetchNdviTimeSeries(coords, 7).catch((err) => {
            console.error("[Dashboard] ❌ fetchNdviTimeSeries failed:", err);
          })
        ]);
      } else {
        console.log("[Dashboard] ❌ No coordinates available, skipping NDVI fetch. Coords:", coords);
      }
    } catch (err: any) {
      setError(err.message || t("dashboard.error.load_failed"));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const loadUserProfile = async () => {
      try {
        const user = await getCurrentUser();
        let crop: string | null = null;
        let coords: { lat?: number; lon?: number } = {};
        let location: string | null = null;
        
        if (user.crop) crop = user.crop;
        
        // Check if user has manual state/district selection
        const manualState = user.state || null;
        const manualDistrict = user.district || null;
        
        // Parse coordinates from user.location if available (works for both auto-detect and manual mode)
        if (user.location) {
          location = user.location;
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
        
        if (manualState && manualDistrict) {
          // Manual selection mode: use state and district
          setUserState(manualState);
          setUserDistrict(manualDistrict);
          // Keep location and coords if they exist (for NDVI functionality)
          setUserLocation(location);
          setUserCoords(coords);
        } else {
          // Auto-detect mode: use location coordinates
          setUserLocation(location);
          setUserCoords(coords);
          setUserState(null);
          setUserDistrict(null);
        }
        
        setUserCrop(crop);
        
        // Fetch dashboard data with loaded profile info
        await fetchDashboardData(crop, coords, location, manualState, manualDistrict);
      } catch {
        // If profile load fails, still fetch dashboard with defaults
        await fetchDashboardData(null, {}, null);
      }
    };
    loadUserProfile();
  }, []);

  useEffect(() => {
    // Refetch when userCrop, coordinates, or manual state/district change (e.g., after profile update)
    // Skip initial render to prevent duplicate calls (initial load is handled by first useEffect)
    const hasData = userCrop !== null || 
                    (userCoords.lat !== undefined && userCoords.lon !== undefined) || 
                    userState || 
                    userDistrict;
    
    if (hasData) {
      // Reset NDVI coordinates tracking when coordinates change to allow new fetch
      if (userCoords.lat !== undefined && userCoords.lon !== undefined) {
        const coordsChanged = !lastNdviCoords.current || 
                            lastNdviCoords.current.lat !== userCoords.lat || 
                            lastNdviCoords.current.lon !== userCoords.lon;
        if (coordsChanged) {
          lastNdviCoords.current = null; // Reset to allow new fetch
        }
        
        // Also reset timeseries coordinates tracking
        const timeseriesCoordsChanged = !lastTimeseriesCoords.current || 
                                       lastTimeseriesCoords.current.lat !== userCoords.lat || 
                                       lastTimeseriesCoords.current.lon !== userCoords.lon;
        if (timeseriesCoordsChanged) {
          lastTimeseriesCoords.current = null; // Reset to allow new fetch
        }
      }
      fetchDashboardData(userCrop, userCoords, userLocation, userState, userDistrict);
    }
  }, [userCrop, userCoords.lat, userCoords.lon, userState, userDistrict]);

  const handleRefresh = () => fetchDashboardData();

  const runNdvi = async () => {
    // Check if we have coordinates
    if (!userCoords.lat || !userCoords.lon) {
      setNdviError("Please set your location coordinates first");
      setModalOpen(true);
      return;
    }

    setModalOpen(true);
    setNdviError(null);

    // If we already have NDVI data from the initial fetch, reuse it
    if (realNdviJobId && realNdviImageUrl && realNdviStats) {
      setNdviStats(realNdviStats);
      setNdviImage(realNdviImageUrl);
      setNdviLoading(false);
      
      // Check if image is available (with retry)
      let retries = 0;
      const maxRetries = 10;
      const retryDelay = 1000;
      
      const checkImageAvailability = async (): Promise<void> => {
        try {
          const imgRes = await fetch(realNdviImageUrl, { method: "HEAD" });
          if (imgRes.ok) {
            // Image is available
            setNdviImage(realNdviImageUrl);
            setNdviLoading(false);
          } else if (retries < maxRetries) {
            retries++;
            setTimeout(checkImageAvailability, retryDelay);
          } else {
            // Max retries reached, but still show the modal with stats
            setNdviLoading(false);
          }
        } catch (imgErr) {
          if (retries < maxRetries) {
            retries++;
            setTimeout(checkImageAvailability, retryDelay);
          } else {
            setNdviLoading(false);
          }
        }
      };
      
      checkImageAvailability();
      return;
    }

    // If no cached data, make a new request (fallback case)
    setNdviLoading(true);
    setNdviImage(null);
    setNdviStats(null);

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/ndvi/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: userCoords.lat,
          lon: userCoords.lon,
          radius: 250,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();

      if (data.status === "no_valid_data") {
        setNdviError(data.message || "No valid NDVI pixels found at this location (clouds, snow, water, or no data).");
        setNdviLoading(false);
        return;
      }

      if (data.status === "ok" && data.job) {
        const job = data.job;
        const imgUrl = `${API_URL}/api/ndvi/image/${job}/${job}_visual.png`;
        setNdviStats(data.stats || null);
        
        // Wait for image to be available (retry with delay)
        let retries = 0;
        const maxRetries = 10;
        const retryDelay = 1000;
        
        const checkImageAvailability = async (): Promise<void> => {
          try {
            const imgRes = await fetch(imgUrl, { method: "HEAD" });
            if (imgRes.ok) {
              setNdviImage(imgUrl);
              setNdviLoading(false);
            } else if (retries < maxRetries) {
              retries++;
              setTimeout(checkImageAvailability, retryDelay);
            } else {
              setNdviError("Image is taking longer than expected. Please try again in a moment.");
              setNdviLoading(false);
            }
          } catch (imgErr) {
            if (retries < maxRetries) {
              retries++;
              setTimeout(checkImageAvailability, retryDelay);
            } else {
              setNdviError("Failed to load NDVI image. Please try again.");
              setNdviLoading(false);
            }
          }
        };
        
        checkImageAvailability();
      } else {
        throw new Error("Unexpected response format");
      }
    } catch (err: any) {
      setNdviError(err.message || "Failed to generate NDVI map. Please try again.");
      setNdviLoading(false);
    }
  };

  const handleViewAdvisory = (crop?: string) => {
    if (crop) navigate(`/advisory/${crop.toLowerCase()}`);
    else navigate("/advisory/cotton");
  };

  // Null-safe number formatters
  const fmtNumber = (v: number | null | undefined): string => {
    if (v != null && !isNaN(v) && typeof v === "number") {
      return v.toLocaleString("en-IN");
    }
    return "—";
  };

  const fmtNumberFixed = (v: number | null | undefined, decimals: number = 2): string => {
    if (v != null && !isNaN(v) && typeof v === "number") {
      return v.toFixed(decimals);
    }
    return "—";
  };

  const fmtPercent = (v: number | null | undefined, decimals: number = 1): string => {
    if (v != null && !isNaN(v) && typeof v === "number") {
      return `${Math.abs(v).toFixed(decimals)}%`;
    }
    return "—";
  };

  const formatPrice = (price: number | null | undefined, changePercent: number | null | undefined) => {
    const safePrice = price != null && !isNaN(price) && typeof price === "number" ? price : null;
    const safeChangePercent = changePercent != null && !isNaN(changePercent) && typeof changePercent === "number" ? changePercent : null;
    
    if (safePrice === null) {
      return <span className="font-medium text-muted-foreground">—</span>;
    }

    const isUp = safeChangePercent != null && safeChangePercent >= 0;
    const TrendIcon = isUp ? ArrowUpRight : safeChangePercent != null ? ArrowDownRight : ArrowRight;
    const color = isUp ? "text-success" : safeChangePercent != null ? "text-destructive" : "text-muted-foreground";

    return (
      <div className="flex items-center gap-2">
        <span className="font-medium">₹{fmtNumber(safePrice)}</span>
        {safeChangePercent != null && (
          <span className={`flex items-center gap-1 text-xs ${color}`}>
            <TrendIcon className="h-3 w-3" />
            {fmtPercent(safeChangePercent)}
          </span>
        )}
      </div>
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
  
  // Use real NDVI history if available (with interpolation), otherwise fall back to synthetic data
  // Ensure we always have exactly 7 values for the sparkline
  const ndviHistory = useMemo(() => {
    // If we have real NDVI history data, use it (already interpolated to 7 days)
    if (realNdviHistory.length > 0) {
      // Convert format from {date, mean} to {date, ndvi} for compatibility
      // Ensure we have exactly 7 values (should already be interpolated, but slice to be safe)
      return realNdviHistory.slice(0, 7).map(item => ({
        date: item.date,
        ndvi: item.mean
      }));
    }
    
    // Fallback to synthetic data
    return ndviHistoryRaw
      .filter((entry: any) => entry && typeof entry.ndvi === "number")
      .slice(-7);
  }, [realNdviHistory, ndviHistoryRaw]);

  // Calculate real NDVI change from interpolated history (matching backend logic)
  // Change = last value - first value (Day 7 - Day 1)
  // Must have exactly 7 interpolated values for accurate calculation
  const realNdviChange = useMemo(() => {
    // Ensure we have at least 7 interpolated values (full week)
    if (realNdviHistory.length >= 7) {
      const firstValue = realNdviHistory[0].mean;
      const lastValue = realNdviHistory[realNdviHistory.length - 1].mean;
      if (typeof firstValue === "number" && typeof lastValue === "number" && !isNaN(firstValue) && !isNaN(lastValue)) {
        const change = lastValue - firstValue;
        console.log("[Dashboard] Real NDVI change calculated:", {
          firstValue,
          lastValue,
          change,
          historyLength: realNdviHistory.length,
          history: realNdviHistory.map(h => ({ date: h.date, mean: h.mean }))
        });
        return change;
      }
    } else if (realNdviHistory.length >= 2) {
      // Fallback: if we have at least 2 values, calculate change
      const firstValue = realNdviHistory[0].mean;
      const lastValue = realNdviHistory[realNdviHistory.length - 1].mean;
      if (typeof firstValue === "number" && typeof lastValue === "number" && !isNaN(firstValue) && !isNaN(lastValue)) {
        const change = lastValue - firstValue;
        console.log("[Dashboard] Real NDVI change (partial data):", {
          firstValue,
          lastValue,
          change,
          historyLength: realNdviHistory.length
        });
        return change;
      }
    }
    console.log("[Dashboard] No real NDVI change - history length:", realNdviHistory.length);
    return null;
  }, [realNdviHistory]);

  // Use real change if available, otherwise fall back to synthetic change
  const displayNdviChange =
  realNdviChange !== null ? realNdviChange : ndviChange;
  
  // Debug: Log which change value is being used
  useEffect(() => {
    if (realNdviChange !== null) {
      console.log("[Dashboard] ✅ Using REAL NDVI change:", realNdviChange.toFixed(4), "from", realNdviHistory.length, "interpolated values");
      if (realNdviHistory.length >= 7) {
        console.log("[Dashboard] First (Day 1):", realNdviHistory[0]?.mean.toFixed(4), "Last (Day 7):", realNdviHistory[6]?.mean.toFixed(4));
      }
    } else if (realNdviHistory.length > 0) {
      console.log("[Dashboard] ⚠️ Real NDVI history exists but change is NULL. History length:", realNdviHistory.length);
      console.log("[Dashboard] History:", realNdviHistory.map(h => `${h.date}: ${h.mean.toFixed(4)}`).join(", "));
    } else {
      console.log("[Dashboard] ⚠️ Real NDVI history is EMPTY, falling back to synthetic:", ndviChange);
    }
  }, [realNdviChange, ndviChange, realNdviHistory]);

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

  // Safely get weather values with null checks
  const getWeatherValue = (value: number | null | undefined, fallback: number): number => {
    if (value != null && !isNaN(value) && typeof value === "number") {
      return value;
    }
    return fallback;
  };
  
  const weatherData = dashboardData?.weather || {};
  const weather = {
    temperature: getWeatherValue(weatherData.temperature, 28),
    humidity: getWeatherValue(weatherData.humidity, 65),
    rainfall: getWeatherValue(weatherData.rainfall, 5),
    wind_speed: getWeatherValue(weatherData.wind_speed, 12),
  };
  const marketList = Array.isArray(dashboardData?.market) ? dashboardData.market : [];
  const alerts = dashboardData?.alerts || [];
  const cropHealth = dashboardData?.crop_health || {};
  console.log("NDVI DEBUG", {
    realNdviChange,
    ndviChange,
    displayNdviChange,
  });


  const ndviStatus = getNdviStatus(ndviLatest);
  const ndviTrend = getTrendInfo(displayNdviChange);
  const TrendIcon = ndviTrend.icon;
  const formattedNdviChange = displayNdviChange != null && !isNaN(displayNdviChange) && typeof displayNdviChange === "number" 
    ? `${displayNdviChange > 0 ? "+" : ""}${fmtNumberFixed(displayNdviChange, 3)}` 
    : null;
  const lastUpdated = formatTimestamp(dashboardData?.weather?.timestamp);
  const sparklineColor = ndviStatus.label === "Good" ? "text-success" : ndviStatus.label === "Moderate" ? "text-warning" : ndviStatus.label === "Poor" ? "text-destructive" : "text-muted-foreground";

  // Safely get market primary price with fallback
  const getMarketPrimaryPrice = (): number | null => {
    const fromData = dashboardData?.market_primary_price;
    if (fromData != null && !isNaN(fromData) && typeof fromData === "number") {
      return fromData;
    }
    if (marketList.length > 0 && marketList[0]?.price != null && !isNaN(marketList[0].price) && typeof marketList[0].price === "number") {
      return marketList[0].price;
    }
    return null;
  };
  const marketPrimaryPrice = getMarketPrimaryPrice();

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
                <h3 className="text-2xl font-bold">{fmtNumber(weather.temperature)}°C</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                <CloudRain className="h-6 w-6 text-secondary" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.humidity")}</span><span className="font-medium">{fmtNumber(weather.humidity)}%</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.wind_speed")}</span><span className="font-medium">{fmtNumber(weather.wind_speed)} km/h</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.rainfall")}</span><span className="font-medium">{fmtNumber(weather.rainfall)}mm</span></div>
            </div>
          </Card>

          {/* Market Prices Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{t("dashboard.market.title")}</p>
                <h3 className="text-2xl font-bold">₹{fmtNumber(marketPrimaryPrice)}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              {marketList.length > 0 ? (
                marketList.map((entry) => (
                  <div key={entry.crop} className="flex justify-between">
                    <span className="text-muted-foreground capitalize">{entry.crop}</span>
                    {formatPrice(entry.price, entry.change_percent)}
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">{t("dashboard.market.no_data")}</p>
              )}
            </div>
          </Card>

          {/* NDVI Insight Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{t("dashboard.ndvi.title")}</p>
                {(() => {
                  // Use real NDVI stats if available, otherwise fall back to dashboard NDVI
                  const displayValue = realNdviStats?.mean ?? ndviLatest;
                  const displayStatus = getNdviStatus(displayValue);
                  
                  return displayValue != null ? (
                    <div className="flex items-baseline gap-3">
                      <h3 className="text-3xl font-bold">{fmtNumberFixed(displayValue, 2)}</h3>
                      <span className={`text-xs font-medium px-2 py-1 rounded-full tracking-wide ${displayStatus.badgeClass}`}>
                        {displayStatus.label}
                      </span>
                      {realNdviLoading && (
                        <span className="text-xs text-muted-foreground">(Loading...)</span>
                      )}
                    </div>
                  ) : (
                    <h3 className="text-2xl font-bold text-muted-foreground">
                      {realNdviLoading ? "Loading..." : t("dashboard.ndvi.unavailable")}
                    </h3>
                  );
                })()}
              </div>
              <div className="w-12 h-12 rounded-full bg-primary/15 flex items-center justify-center">
                <Satellite className="h-6 w-6 text-primary" />
              </div>
            </div>

            {(() => {
              // Use real NDVI stats if available, otherwise fall back to dashboard NDVI
              const displayValue = realNdviStats?.mean ?? ndviLatest;
              
              if (displayValue != null) {
                const displayStatus = getNdviStatus(displayValue);
                
                return (
                  <>
                    {/* Show trend if available (from real interpolated data or dashboard data) */}
                    {ndviHistory.length > 0 && displayNdviChange != null && (
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
                      </>
                    )}
                    
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{realNdviStats ? "Real-time NDVI" : t("dashboard.ndvi.last_updated", { time: lastUpdated })}</span>
                      {ndviLatest != null && <span>{t("dashboard.ndvi.trend_7day")}</span>}
                    </div>
                  </>
                );
              } else {
                return (
                  <div className="space-y-3">
                    <div className="w-full h-16 rounded-md bg-muted" />
                    <p className="text-sm text-muted-foreground">{t("dashboard.ndvi.unavailable")}</p>
                    <p className="text-xs text-muted-foreground">{t("dashboard.ndvi.last_updated", { time: lastUpdated })}</p>
                  </div>
                );
              }
            })()}

            {/* View Crop Health Map Button - Always visible at bottom of card */}
            <div className="mt-4 pt-4 border-t">
              <Button
                onClick={runNdvi}
                className="w-full"
                variant="outline"
                size="sm"
                disabled={ndviLoading || !userCoords.lat || !userCoords.lon}
              >
                {ndviLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <MapIcon className="h-4 w-4 mr-2" />
                    View Crop Health Map
                  </>
                )}
              </Button>
              {(!userCoords.lat || !userCoords.lon) && (
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  Set your location to view NDVI map
                </p>
              )}
            </div>
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
                  <h3 className="text-2xl font-bold">{fmtNumberFixed(advisory.metrics?.ndvi, 2)}</h3>
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
                  <h3 className="text-2xl font-bold">
                    {advisory.metrics?.soil_moisture != null && !isNaN(advisory.metrics.soil_moisture) && typeof advisory.metrics.soil_moisture === "number"
                      ? `${Math.round(advisory.metrics.soil_moisture * 100)}%`
                      : "—"}
                  </h3>
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
                  <h3 className="text-2xl font-bold">{fmtNumber(advisory.metrics?.temperature)}°C</h3>
                </div>
                <Thermometer className="h-6 w-6 text-secondary" />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.humidity")}</span><span className="font-medium">{fmtNumber(advisory.metrics?.humidity)}%</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.weather.rainfall")}</span><span className="font-medium">{fmtNumber(advisory.metrics?.rainfall)}mm</span></div>
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
                  <h3 className="text-2xl font-bold">₹{fmtNumber(advisory.metrics?.market_price)}</h3>
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
                const healthScore = (health.health_score != null && !isNaN(health.health_score) && typeof health.health_score === "number") 
                  ? health.health_score 
                  : 0;
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
                      <div className="flex justify-between"><span className="text-muted-foreground">NDVI</span><span className="font-medium">{fmtNumberFixed(health.ndvi, 2)}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("dashboard.advisory.soil_moisture")}</span><span className="font-medium">
                        {health.soil_moisture != null && !isNaN(health.soil_moisture) && typeof health.soil_moisture === "number"
                          ? `${fmtNumber(health.soil_moisture < 1 ? health.soil_moisture * 100 : health.soil_moisture)}%`
                          : "—"}
                      </span></div>
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
                        <span className="font-medium">{fmtNumber(alert.confidence)}%</span>
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

      {/* NDVI Modal */}
      <NdviModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setNdviError(null);
        }}
        imageUrl={ndviImage}
        stats={ndviStats}
        loading={ndviLoading}
        error={ndviError}
      />
    </div>
  );
};


export default Dashboard;
