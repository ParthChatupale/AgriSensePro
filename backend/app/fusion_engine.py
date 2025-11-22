"""
Fusion Engine - Intelligence layer that merges data sources and generates advisories.

Combines weather (IMD), market prices (Agmarknet), and satellite imagery (Bhuvan)
to provide crop advisories, pest alerts, and risk detection.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import sys
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

# Add backend directory to path for imports
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BACKEND_DIR)

from etl.make_features import combine_features, load_rules
from app.utils.loader import load_crop_metadata
from app.services.crop_stage import detect_crop_stage
from app.services.ndvi_utils import ndvi_stress_level, compute_ndvi_change
from app.services.weather import get_realtime_weather
from app.services.geocode import reverse_geocode
from app.services.ndvi_synthetic import synthetic_ndvi, synthetic_ndvi_history
from app.services.market_service import fetch_market_price

router = APIRouter(prefix="/fusion", tags=["Fusion Engine"])

# Load crop metadata once
crop_metadata = load_crop_metadata()

# Get the backend directory path (already set above)
DATA_PATH = os.path.join(BACKEND_DIR, "data")
RULES_PATH = os.path.join(BACKEND_DIR, "rules")
MOCK_PATH = os.path.join(os.path.dirname(__file__), "mock_data")

RULE_CACHE: Dict[str, Dict[str, Any]] = {}


def get_rules(rule_type: str) -> Dict[str, Any]:
    if rule_type not in RULE_CACHE:
        RULE_CACHE[rule_type] = load_rules(rule_type) or {}
    return RULE_CACHE[rule_type]


def get_threshold(crop: str, key: str):
    meta = crop_metadata.get(crop, {})
    thresholds = meta.get("thresholds", {})
    if key in thresholds:
        return thresholds[key]
    return meta.get(key)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file safely."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {file_path}: {str(e)}")


INDIA_CENTROID_LAT = 22.59
INDIA_CENTROID_LON = 78.96


def parse_lat_lon(location: str | None) -> Tuple[Optional[float], Optional[float]]:
    if not location:
        return None, None
    try:
        lat_str, lon_str = location.split(",", 1)
        return float(lat_str.strip()), float(lon_str.strip())
    except (ValueError, AttributeError):
        return None, None


async def resolve_weather_context(
    location: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    state: str | None = None,
    district: str | None = None,
    village: str | None = None,
) -> Tuple[Dict[str, Any], Dict[str, Any], float, float]:
    lat, lon = parse_lat_lon(location)

    if lat is None or lon is None:
        if latitude is not None and longitude is not None:
            lat, lon = latitude, longitude

    if lat is None or lon is None:
        lat, lon = INDIA_CENTROID_LAT, INDIA_CENTROID_LON

    fallback_weather = load_json_file(os.path.join(DATA_PATH, "weather_data.json"))

    weather = await get_realtime_weather(lat, lon)
    if not weather:
        weather = _load_weather_from_fallback(fallback_weather, lat, lon)

    try:
        geo_info = await reverse_geocode(lat, lon)
    except Exception:
        lat, lon = INDIA_CENTROID_LAT, INDIA_CENTROID_LON
        weather = await get_realtime_weather(lat, lon)
        geo_info = {
            "state": state,
            "district": district,
            "village": village,
        }

    if not geo_info:
        geo_info = {
            "state": state,
            "district": district,
            "village": village,
        }

    if fallback_weather:
        weather.setdefault("forecast", fallback_weather.get("forecast"))
    weather.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    weather.setdefault("location", f"{lat},{lon}")

    return weather, geo_info, lat, lon


def _load_weather_from_fallback(fallback_data: Dict[str, Any], lat: float, lon: float) -> Dict[str, Any]:
    if not fallback_data:
        return {
            "temperature": None,
            "humidity": None,
            "rainfall": None,
            "wind_speed": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": f"{lat},{lon}",
        }
    result = dict(fallback_data)
    result.setdefault("location", f"{lat},{lon}")
    result.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    return result


async def fetch_ndvi_context(lat: float, lon: float, crop: str = "cotton"):
    latest = synthetic_ndvi(lat, lon, crop)
    history = synthetic_ndvi_history(lat, lon, crop, days=7)

    ndvi_change = None
    if len(history) >= 2:
        ndvi_change = round(history[-1]["ndvi"] - history[-2]["ndvi"], 4)

    return latest, ndvi_change, history


def load_crop_mock(crop_name: str) -> Dict[str, Any]:
    """Load mock data JSON for a given crop if available."""
    filename = f"{crop_name.lower()}.json"
    file_path = os.path.join(MOCK_PATH, filename)
    if os.path.exists(file_path):
        return load_json_file(file_path)
    return {}


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _evaluate_numeric(feature_value, operator: str, target_value) -> bool:
    fv = _to_float(feature_value)
    tv = _to_float(target_value)
    if fv is None or tv is None:
        return False
    if operator == ">":
        return fv > tv
    if operator == "<":
        return fv < tv
    if operator == ">=":
        return fv >= tv
    if operator == "<=":
        return fv <= tv
    if operator == "abs_gte":
        return abs(fv) >= tv
    return False


def run_rules(
    rule_type: str,
    context: Dict[str, Any],
    crop: str,
    crop_meta: Dict[str, Any],
    detected_stage: str,
) -> Tuple[List[str], float]:
    rules = get_rules(rule_type)
    fired: List[str] = []
    max_score = 0.0

    for rule_name, rule in rules.items():
        conditions_met = True
        for cond in rule.get("conditions", []):
            feature = cond.get("feature")
            operator = cond.get("op", "==")

            if feature == "crop_stage":
                expected_stage = cond.get("value")
                if expected_stage and detected_stage != expected_stage:
                    conditions_met = False
                continue

            if feature == "ndvi_status":
                expected_status = cond.get("value")
                if expected_status and context.get("ndvi_status") != expected_status:
                    conditions_met = False
                continue

            feature_value = context.get(feature)
            if operator == "use_threshold":
                threshold_key = cond.get("value")
                threshold_val = get_threshold(crop, threshold_key)
                if threshold_val is None:
                    conditions_met = False
                    break
                if feature_value is None or feature_value > threshold_val:
                    conditions_met = False
                continue

            if feature_value is None:
                conditions_met = False
                break

            target_value = cond.get("value")
            if "use_threshold" in cond:
                threshold_val = get_threshold(crop, cond["use_threshold"])
                if threshold_val is None:
                    conditions_met = False
                    break
                target_value = threshold_val

            if operator in {">", "<", ">=", "<=", "abs_gte"}:
                if not _evaluate_numeric(feature_value, operator, target_value):
                    conditions_met = False
                    break
            elif operator == "==":
                if feature_value != target_value:
                    conditions_met = False
                    break
            elif operator == "!=":
                if feature_value == target_value:
                    conditions_met = False
                    break
            else:
                # Unknown operator -> fail safe
                conditions_met = False
                break

        if conditions_met:
            fired.append(rule.get("description", rule_name))
            max_score = max(max_score, rule.get("score", 0.0))

    return fired, max_score


def build_advisory_from_features(
    crop: str,
    raw_features: Dict[str, Any],
    user_context: Dict[str, Any] | None = None,
) -> Tuple[Dict[str, Any], float, List[str], Dict[str, Any]]:
    """Evaluate rules and produce advisory fields for a crop."""
    crop = crop.lower()
    crop_meta = crop_metadata.get(crop, {})

    context: Dict[str, Any] = {}
    context.update(raw_features or {})
    if user_context:
        context.update(user_context)

    if context.get("ndvi_change") is None:
        context.pop("ndvi_change", None)

    ndvi_current = context.get("ndvi")
    previous_ndvi = (
        context.get("previous_ndvi")
        or context.get("ndvi_previous")
        or context.get("ndvi_prior")
    )
    computed_change = compute_ndvi_change(ndvi_current, previous_ndvi)
    if "ndvi_change" not in context and computed_change != 0:
        context["ndvi_change"] = computed_change
    if "ndvi_change" not in context:
        context["ndvi_change"] = 0.0

    context["ndvi_status"] = ndvi_stress_level(crop_meta, ndvi_current)

    detected_stage = context.get("crop_stage") or "unknown"
    if detected_stage == "unknown":
        days_since_sowing = context.get("days_since_sowing")
        if days_since_sowing is not None:
            detected_stage = detect_crop_stage(crop_meta, days_since_sowing)
    context["crop_stage"] = detected_stage

    region_priority = crop_meta.get("region_priority", [])
    user_district = context.get("user_district") or context.get("district")
    context["region_priority_match"] = bool(
        region_priority and user_district and user_district in region_priority
    )

    pest_fired, pest_score = run_rules("pest", context, crop, crop_meta, detected_stage)
    irrigation_fired, irrigation_score = run_rules("irrigation", context, crop, crop_meta, detected_stage)
    market_fired, market_score = run_rules("market", context, crop, crop_meta, detected_stage)

    rule_breakdown = {
        "pest": {"fired": pest_fired, "score": pest_score},
        "irrigation": {"fired": irrigation_fired, "score": irrigation_score},
        "market": {"fired": market_fired, "score": market_score},
    }

    max_score = max(pest_score, irrigation_score, market_score, 0.0)
    if context.get("region_priority_match") and max_score > 0:
        max_score = min(max_score * 1.1, 1.0)

    fired_rules = pest_fired + irrigation_fired + market_fired

    if max_score >= 0.8:
        severity = "high"
        summary = "High risk detected"
    elif max_score >= 0.6:
        severity = "medium"
        summary = "Moderate risk detected"
    else:
        severity = "low"
        summary = "Low risk detected"

    alerts: List[Dict[str, str]] = []
    alerts.extend({"type": "pest", "message": msg} for msg in pest_fired)
    alerts.extend({"type": "soil", "message": msg} for msg in irrigation_fired)
    alerts.extend({"type": "market", "message": msg} for msg in market_fired)

    metrics = {
        "ndvi": ndvi_current,
        "ndvi_change": context.get("ndvi_change"),
        "soil_moisture": context.get("soil_moisture"),
        "market_price": context.get("market_price") or context.get("price"),
        "temperature": context.get("temperature"),
        "humidity": context.get("humidity"),
        "rainfall": context.get("rainfall"),
        "wind_speed": context.get("wind_speed"),
    }

    advisory_fields = {
        "summary": summary,
        "severity": severity,
        "alerts": alerts,
        "metrics": metrics,
    }

    return advisory_fields, max_score, fired_rules, rule_breakdown


@router.get("/dashboard")
async def get_dashboard_data(
    crop: Optional[str] = None,
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    village: Optional[str] = None,
):
    """
    Combine weather, market, and alert mock data for dashboard.
    """
    try:
        weather, geo_info, lat, lon = await resolve_weather_context(
            location=location,
            latitude=latitude,
            longitude=longitude,
            state=state,
            district=district,
            village=village,
        )
        crop_name_for_ndvi = crop.lower() if crop else "cotton"
        ndvi_latest, ndvi_change, ndvi_history = await fetch_ndvi_context(lat, lon, crop_name_for_ndvi)
        
        # Fetch real market prices with fallback
        market_data = {}
        if crop:
            market_price_data = await fetch_market_price(crop, geo_info.get("district"))
            market_data[crop.lower()] = market_price_data
        else:
            # Load all crops from fallback if no specific crop
            market_data = load_json_file(os.path.join(DATA_PATH, "market_prices.json"))
        
        alerts = load_json_file(os.path.join(DATA_PATH, "alerts.json"))
        crop_health = load_json_file(os.path.join(DATA_PATH, "crop_health.json"))

        total_alerts = len(alerts) if isinstance(alerts, list) else 0
        high_priority_alerts = [
            alert for alert in alerts
            if isinstance(alert, dict) and alert.get("level") == "high"
        ] if isinstance(alerts, list) else []

        response_data = {
            "weather": weather,
            "market": market_data,
            "alerts": alerts,
            "crop_health": crop_health,
            "ndvi": {
                "latest": ndvi_latest,
                "change": ndvi_change,
                "history": ndvi_history,
            },
            "summary": {
                "total_alerts": total_alerts,
                "high_priority_count": len(high_priority_alerts),
                "crops_monitored": len(crop_health) if isinstance(crop_health, dict) else 0,
            },
            "timestamp": weather.get("timestamp"),
        }

        if crop:
            response_data["user_crop"] = crop.lower()
        if geo_info.get("district"):
            response_data["user_district"] = geo_info.get("district")
        response_data["coordinates"] = {"latitude": lat, "longitude": lon}

        return JSONResponse(response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dashboard data: {str(e)}")


@router.get("/advisory/{crop_name}")
async def get_advisory(
    crop_name: str,
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    village: Optional[str] = None,
):
    """Return advisory for a given crop using realtime weather."""
    try:
        crop = crop_name.lower()
        weather, geo_info, lat, lon = await resolve_weather_context(
            location=location,
            latitude=latitude,
            longitude=longitude,
            state=state,
            district=district,
            village=village,
        )
        ndvi_latest, ndvi_change, ndvi_history = await fetch_ndvi_context(lat, lon, crop)
        user_context = {
            "user_district": geo_info.get("district"),
            "district": geo_info.get("district"),
            "state": geo_info.get("state"),
            "location": weather.get("location"),
            "ndvi": ndvi_latest,
            "ndvi_change": ndvi_change,
        }

        # Fetch real market price
        market = await fetch_market_price(crop, geo_info.get("district"))
        
        mock = load_crop_mock(crop)
        if mock:
            features = {
                "temperature": weather.get("temperature"),
                "humidity": weather.get("humidity"),
                "rainfall": weather.get("rainfall"),
                "wind_speed": weather.get("wind_speed"),
                "ndvi": ndvi_latest if ndvi_latest is not None else mock.get("ndvi"),
                "soil_moisture": mock.get("soil_moisture"),
                "crop_stage": mock.get("crop_stage", "unknown"),
                "price_change_percent": market.get("price_change_percent", 0),
                "market_price": market.get("price") or mock.get("market_price"),
                "days_since_sowing": mock.get("days_since_sowing"),
                "previous_ndvi": mock.get("previous_ndvi") or mock.get("ndvi_previous"),
                "ndvi_change": (
                    ndvi_change
                    if ndvi_change is not None
                    else compute_ndvi_change(
                        ndvi_latest,
                        mock.get("previous_ndvi") or mock.get("ndvi_previous")
                    )
                ),
                "user_district": mock.get("district") or geo_info.get("district"),
                "district": mock.get("district") or geo_info.get("district"),
            }

            fields, score, fired_rules, breakdown = build_advisory_from_features(crop, features, user_context)
            legacy_priority = "High" if score >= 0.8 else ("Medium" if score >= 0.6 else "Low")
            response = {
                "crop": crop.capitalize(),
                "analysis": fields["summary"],
                "priority": legacy_priority,
                "severity": fields["severity"].capitalize(),
                "rule_score": score,
                "fired_rules": fired_rules,
                "recommendations": [],
                "rule_breakdown": breakdown,
                "data_sources": {"weather": "Open-Meteo", "satellite": "Bhuvan", "market": "Agmarknet"},
                "last_updated": weather.get("timestamp", "recently"),
                "summary": fields["summary"],
                "alerts": fields["alerts"],
                "metrics": fields["metrics"],
            }
            if response.get("metrics") is not None and ndvi_history:
                response["metrics"]["ndvi_history"] = ndvi_history
            return JSONResponse(response)

        advisory = await generate_advisory(
            crop,
            weather,
            user_context,
            ndvi_latest=ndvi_latest,
            ndvi_change=ndvi_change,
            ndvi_history=ndvi_history,
        )
        if ndvi_history and isinstance(advisory.get("metrics"), dict):
            advisory["metrics"]["ndvi_history"] = ndvi_history
        return JSONResponse(advisory)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advisory: {str(e)}")


async def enhance_advisory_with_rules(advisory: Dict[str, Any], crop_name: str) -> Dict[str, Any]:
    """Enhance pre-generated advisory with metadata-aware rule evaluation."""
    try:
        crop = crop_name.lower()
        metrics = advisory.get("metrics") if isinstance(advisory.get("metrics"), dict) else {}
        location_hint = metrics.get("location") if isinstance(metrics, dict) else None
        weather, geo_info, lat, lon = await resolve_weather_context(
            location=location_hint,
            state=advisory.get("state"),
            district=advisory.get("district"),
            village=advisory.get("village"),
        )
        ndvi_latest, ndvi_change, ndvi_history = await fetch_ndvi_context(lat, lon, crop)
        crop_health_data = load_json_file(os.path.join(DATA_PATH, "crop_health.json"))
        
        # Fetch real market price with fallback
        market = await fetch_market_price(crop, geo_info.get("district"))

        crop_health = crop_health_data.get(crop, {})

        features = combine_features(weather, crop_health, market)
        if ndvi_latest is not None:
            features["ndvi"] = ndvi_latest
        if ndvi_change is not None:
            features["ndvi_change"] = ndvi_change
        features["market_price"] = market.get("price")
        features["price_change_percent"] = market.get("price_change_percent", 0.0)
        features["days_since_sowing"] = crop_health.get("days_since_sowing")
        features["previous_ndvi"] = (
            crop_health.get("previous_ndvi")
            or crop_health.get("ndvi_previous")
            or crop_health.get("ndvi_prior")
        )

        user_context = {
            "user_district": geo_info.get("district"),
            "district": geo_info.get("district"),
            "state": geo_info.get("state"),
            "location": weather.get("location"),
        }

        fields, score, fired, breakdown = build_advisory_from_features(crop, features, user_context)

        advisory["fired_rules"] = fired
        advisory["rule_score"] = score
        advisory["rule_breakdown"] = breakdown
        advisory.setdefault("summary", fields["summary"])
        advisory["alerts"] = fields["alerts"]
        advisory.setdefault("metrics", {}).update({k: v for k, v in fields["metrics"].items() if v is not None})
        if ndvi_history:
            advisory["metrics"]["ndvi_history"] = ndvi_history
        advisory.setdefault("data_sources", {}).update({"weather": "Open-Meteo"})
        advisory["last_updated"] = weather.get("timestamp", advisory.get("last_updated"))
        return advisory
    except Exception:
        return advisory


async def generate_advisory(
    crop_name: str,
    weather: Dict[str, Any],
    user_context: Dict[str, Any],
    ndvi_latest: Optional[float] = None,
    ndvi_change: Optional[float] = None,
    ndvi_history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Generate advisory dynamically for crops without pre-generated files."""
    try:
        crop = crop_name.lower()
        crop_health_data = load_json_file(os.path.join(DATA_PATH, "crop_health.json"))
        
        # Fetch real market price with fallback
        district = user_context.get("district") or user_context.get("user_district")
        market = await fetch_market_price(crop_name, district)

        crop_health = crop_health_data.get(crop, {})

        features = combine_features(weather, crop_health, market)
        if ndvi_latest is not None:
            features["ndvi"] = ndvi_latest
        if ndvi_change is not None:
            features["ndvi_change"] = ndvi_change
        features["market_price"] = market.get("price")
        features["price_change_percent"] = market.get("price_change_percent", 0.0)
        features["days_since_sowing"] = crop_health.get("days_since_sowing")
        features["previous_ndvi"] = (
            crop_health.get("previous_ndvi")
            or crop_health.get("ndvi_previous")
            or crop_health.get("ndvi_prior")
        )

        if ndvi_latest is not None:
            user_context.setdefault("ndvi", ndvi_latest)
        if ndvi_change is not None:
            user_context.setdefault("ndvi_change", ndvi_change)

        advisory_fields, max_score, fired_rules, breakdown = build_advisory_from_features(crop, features, user_context)

        if ndvi_history:
            advisory_fields.setdefault("metrics", {}).setdefault("ndvi_history", ndvi_history)

        if max_score >= 0.8:
            priority = "High"
            severity = "High"
        elif max_score >= 0.6:
            priority = "Medium"
            severity = "Medium"
        else:
            priority = "Low"
            severity = "Low"

        recommendations: List[Dict[str, Any]] = []
        if "pest" in breakdown and breakdown["pest"]["fired"]:
            recommendations.append({
                "title": "Inspect for pests",
                "desc": "Rule-based indicators suggest pest pressure; inspect immediately.",
                "priority": "high" if max_score >= 0.8 else "medium",
                "timeline": "immediate",
            })
        if "irrigation" in breakdown and breakdown["irrigation"]["fired"]:
            recommendations.append({
                "title": "Review irrigation schedule",
                "desc": "Soil moisture and weather conditions warrant irrigation adjustment.",
                "priority": "medium",
                "timeline": "within 24 hours",
            })
        if not recommendations:
            recommendations.append({
                "title": "Continue standard monitoring",
                "desc": "No immediate risks detected. Maintain regular field checks.",
                "priority": "low",
                "timeline": "ongoing",
            })

        return {
            "crop": crop.capitalize(),
            "analysis": advisory_fields["summary"],
            "priority": priority,
            "severity": severity,
            "rule_score": max_score,
            "fired_rules": fired_rules,
            "recommendations": recommendations,
            "rule_breakdown": breakdown,
            "summary": advisory_fields["summary"],
            "alerts": advisory_fields["alerts"],
            "metrics": advisory_fields["metrics"],
            "data_sources": {
                "weather": "Open-Meteo",
                "satellite": "Bhuvan",
                "market": "Agmarknet"
            },
            "last_updated": weather.get("timestamp", datetime.now(timezone.utc).isoformat()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating advisory: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the fusion engine."""
    return JSONResponse({
        "status": "healthy",
        "service": "Fusion Engine",
        "data_sources": ["IMD Weather", "Bhuvan Satellite", "Agmarknet Market"]
    })

