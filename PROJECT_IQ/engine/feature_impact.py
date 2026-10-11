"""
PROJECTIQ - Feature Impact Predictor

Estimates the impact of a proposed new feature using keyword-matched
rule profiles. All output is clearly labeled as an ESTIMATE.
"""

from typing import Dict, List

IMPACT_PROFILES = [
    {
        "keywords": ["chatbot", "chat bot", "assistant", "conversational"],
        "portfolio_value": 8, "technical_complexity": 6, "user_value": 7,
        "prerequisites": ["LLM API", "Backend Endpoint", "Chat Context Storage"],
    },
    {
        "keywords": ["authentication", "login", "sign up", "auth"],
        "portfolio_value": 6, "technical_complexity": 5, "user_value": 8,
        "prerequisites": ["Password Hashing", "Session/Token Management", "User Table"],
    },
    {
        "keywords": ["payment", "checkout", "stripe", "billing"],
        "portfolio_value": 8, "technical_complexity": 7, "user_value": 8,
        "prerequisites": ["Payment Gateway Integration", "Secure API Keys", "Order Records"],
    },
    {
        "keywords": ["notification", "alert", "email", "push"],
        "portfolio_value": 5, "technical_complexity": 4, "user_value": 6,
        "prerequisites": ["SMTP / Push Service", "Event Triggers", "User Preferences"],
    },
    {
        "keywords": ["dashboard", "analytics", "chart", "visualization"],
        "portfolio_value": 7, "technical_complexity": 5, "user_value": 7,
        "prerequisites": ["Charting Library", "Aggregated Data Queries"],
    },
    {
        "keywords": ["machine learning", "prediction", "model", "ai"],
        "portfolio_value": 9, "technical_complexity": 8, "user_value": 7,
        "prerequisites": ["Training Data", "Model Serving Endpoint", "Evaluation Metrics"],
    },
    {
        "keywords": ["search"],
        "portfolio_value": 5, "technical_complexity": 5, "user_value": 6,
        "prerequisites": ["Indexing Strategy", "Query Filtering"],
    },
    {
        "keywords": ["export", "report", "pdf", "csv"],
        "portfolio_value": 4, "technical_complexity": 3, "user_value": 6,
        "prerequisites": ["Export Library", "Report Template"],
    },
    {
        "keywords": ["real-time", "realtime", "websocket", "live"],
        "portfolio_value": 7, "technical_complexity": 7, "user_value": 6,
        "prerequisites": ["WebSocket Server", "Client Subscription Handling"],
    },
    {
        "keywords": ["mobile", "app", "ios", "android"],
        "portfolio_value": 7, "technical_complexity": 8, "user_value": 7,
        "prerequisites": ["Mobile Framework", "API Compatibility Layer"],
    },
]

DEFAULT_PROFILE = {
    "portfolio_value": 4, "technical_complexity": 4, "user_value": 4,
    "prerequisites": ["Requirements Definition", "Design Review"],
}


def predict_feature_impact(feature_description: str) -> Dict:
    lowered = feature_description.lower()
    matched = None
    for profile in IMPACT_PROFILES:
        if any(kw in lowered for kw in profile["keywords"]):
            matched = profile
            break
    profile = matched or DEFAULT_PROFILE

    total = profile["portfolio_value"] + profile["technical_complexity"] + profile["user_value"]
    if total >= 20:
        recommendation = "Strongly Recommended"
    elif total >= 14:
        recommendation = "Recommended"
    elif total >= 9:
        recommendation = "Optional"
    else:
        recommendation = "Low Priority"

    return {
        "feature_description": feature_description,
        "portfolio_value": f"+{profile['portfolio_value']}",
        "technical_complexity": f"+{profile['technical_complexity']}",
        "user_value": f"+{profile['user_value']}",
        "recommendation": recommendation,
        "prerequisites": profile["prerequisites"],
        "disclaimer": "All impact scores are estimates generated from a rule-based profile, not a guarantee.",
    }
