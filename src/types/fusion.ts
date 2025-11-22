/**
 * TypeScript interfaces for Fusion Engine API responses
 */

export interface WeatherData {
  temperature: number;
  humidity: number;
  rainfall: number;
  wind_speed: number;
  location?: string;
  timestamp?: string;
  forecast?: {
    next_3_days: Array<{
      day: number;
      temp: number;
      humidity: number;
      rainfall: number;
    }>;
  };
}

export interface MarketPrice {
  price: number;
  unit: string;
  change_percent: number;
  trend: "up" | "down";
  mandi?: string;
  last_updated?: string;
}

export interface MarketPrices {
  [crop: string]: MarketPrice;
}

export interface Alert {
  id: number;
  title: string;
  level: "high" | "medium" | "low";
  confidence: number;
  type: string;
  crop?: string;
  description?: string;
  timestamp?: string;
  action_required?: boolean;
}

export interface CropHealth {
  ndvi: number;
  ndvi_change: number;
  soil_moisture: number;
  crop_stage: string;
  health_score: number;
  last_updated?: string;
}

export interface CropHealthData {
  [crop: string]: CropHealth;
}

export interface DashboardResponse {
  weather: WeatherData;
  market: MarketPrices;
  alerts: Alert[];
  crop_health: CropHealthData;
  summary: {
    total_alerts: number;
    high_priority_count: number;
    crops_monitored: number;
  };
  timestamp?: string;
}

export interface Recommendation {
  title: string;
  desc: string;
  priority: "high" | "medium" | "low";
  timeline: string;
}

export interface RuleBreakdown {
  pest: {
    fired: string[];
    score: number;
  };
  irrigation: {
    fired: string[];
    score: number;
  };
  market: {
    fired: string[];
    score: number;
  };
}

export interface AdvisoryResponse {
  crop: string;
  analysis: string;
  priority: "High" | "Medium" | "Low";
  severity: "High" | "Medium" | "Low";
  rule_score: number;
  fired_rules: string[];
  recommendations: Recommendation[];
  rule_breakdown?: RuleBreakdown;
  data_sources?: {
    weather: string;
    satellite: string;
    market: string;
  };
  last_updated?: string;
}

