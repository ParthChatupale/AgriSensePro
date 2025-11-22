/**
 * API Configuration
 * Centralized configuration for backend API endpoints
 */
export const API_BASE = "http://localhost:8000";

export const API_ENDPOINTS = {
  FUSION_DASHBOARD: `${API_BASE}/fusion/dashboard`,
  FUSION_ADVISORY: (crop: string) => `${API_BASE}/fusion/advisory/${crop}`,
  FUSION_HEALTH: `${API_BASE}/fusion/health`,
} as const;

