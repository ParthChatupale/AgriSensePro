"""
Rule evaluation helper for the Fusion Engine.

Evaluates rules against feature data and returns fired rules with scores.
"""
import json
import os
from typing import Dict, List, Tuple, Any


def evaluate_rules(rules: Dict[str, Any], features: Dict[str, Any]) -> Tuple[List[str], float]:
    """
    Evaluate rules against feature data.
    
    Args:
        rules: Dictionary of rules with conditions
        features: Dictionary of feature values (temperature, humidity, etc.)
    
    Returns:
        Tuple of (fired_rules_descriptions, max_score)
    """
    fired_rules = []
    total_score = 0.0
    
    for rule_name, rule in rules.items():
        match = True
        
        # Check all conditions for this rule
        for cond in rule.get("conditions", []):
            feature_name = cond.get("feature")
            operator = cond.get("op")
            threshold = cond.get("value")
            
            # Get feature value
            feature_val = features.get(feature_name)
            
            # If feature is missing, rule doesn't match
            if feature_val is None:
                match = False
                break
            
            # Evaluate condition
            if operator == ">":
                if not (feature_val > threshold):
                    match = False
                    break
            elif operator == "<":
                if not (feature_val < threshold):
                    match = False
                    break
            elif operator == ">=":
                if not (feature_val >= threshold):
                    match = False
                    break
            elif operator == "<=":
                if not (feature_val <= threshold):
                    match = False
                    break
            elif operator == "==":
                if not (feature_val == threshold):
                    match = False
                    break
            elif operator == "!=":
                if not (feature_val != threshold):
                    match = False
                    break
            elif operator == "abs_gte":
                # Absolute value greater than or equal to threshold
                if not (abs(feature_val) >= threshold):
                    match = False
                    break
        
        # If all conditions matched, rule is fired
        if match:
            fired_rules.append(rule.get("description", rule_name))
            total_score = max(total_score, rule.get("score", 0.0))
    
    return fired_rules, total_score


def load_rules(rule_type: str = "pest") -> Dict[str, Any]:
    """
    Load rules from JSON file.
    
    Args:
        rule_type: Type of rules to load (pest, irrigation, market)
    
    Returns:
        Dictionary of rules
    """
    rules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rules")
    rule_file = os.path.join(rules_dir, f"{rule_type}_rules.json")
    
    if not os.path.exists(rule_file):
        return {}
    
    with open(rule_file, "r") as f:
        return json.load(f)


def combine_features(weather: Dict, crop_health: Dict, market: Dict = None) -> Dict[str, Any]:
    """
    Combine data from different sources into a feature dictionary.
    
    Args:
        weather: Weather data dictionary
        crop_health: Crop health data dictionary
        market: Market data dictionary (optional)
    
    Returns:
        Combined feature dictionary
    """
    features = {
        "temperature": weather.get("temperature"),
        "humidity": weather.get("humidity"),
        "rainfall": weather.get("rainfall"),
        "wind_speed": weather.get("wind_speed"),
        "ndvi": crop_health.get("ndvi"),
        "ndvi_change": crop_health.get("ndvi_change"),
        "soil_moisture": crop_health.get("soil_moisture"),
        "crop_stage": crop_health.get("crop_stage"),
    }
    
    if market:
        features["price_change_percent"] = market.get("change_percent", 0)
    
    return features

