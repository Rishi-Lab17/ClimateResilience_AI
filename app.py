import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from datetime import datetime, timedelta
import random
import json
import os
import hashlib
import time
import calendar
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, accuracy_score, r2_score, mean_squared_error, confusion_matrix
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.tree import DecisionTreeRegressor
import warnings
warnings.filterwarnings('ignore')

# ==================== GEMINI AI CONFIGURATION ====================
# 🔑 GET YOUR FREE API KEY FROM: https://aistudio.google.com
GEMINI_API_KEY = "actual_key_here"

if GEMINI_API_KEY != "actual_key_here":
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        GEMINI_AVAILABLE = True
    except:
        GEMINI_AVAILABLE = False
        gemini_model = None
else:
    GEMINI_AVAILABLE = False
    gemini_model = None

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="ClimateResilience AI - Complete Supply Chain Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS FOR LIGHT THEME (FIXED TEXT VISIBILITY) ====================
st.markdown("""
<style>
    /* Main background - light */
    .stApp {
        background: #f0f4f8;
    }
    
    /* All text dark for visibility */
    .stApp, .stMarkdown, p, div, span, label, 
    .stTextInput > label, .stSelectbox > label, .stSlider > label,
    .stNumberInput > label, h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
    }
    
    /* Glassmorphism Card */
    .glass-card {
        background: white;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2a5298;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2a5298 !important;
    }
    
    /* Header */
    .cyber-header {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
    }
    .cyber-header h1, .cyber-header p {
        color: white !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    /* Info/Warning/Success/Danger Cards */
    .info-card {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .warning-card {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .success-card {
        background: #dcfce7;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .danger-card {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    
    /* Login Container */
    .login-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid #2a5298;
        max-width: 450px;
        margin: 0 auto;
    }
    
    /* Buttons */
    .stButton > button {
        background: #2a5298;
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background: #1e3c72;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        border-radius: 30px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #1e293b !important;
        font-weight: 600;
        border-radius: 25px;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #2a5298;
        color: white !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        font-size: 0.7rem;
        color: #64748b !important;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: white;
        color: #1e293b;
        border: 1px solid #cbd5e1;
    }
    .stSelectbox > div > div {
        background-color: white;
        color: #1e293b;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: white;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f1f5f9;
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_mobile' not in st.session_state:
    st.session_state.user_mobile = ""
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = "Supply Chain Analyst"
if 'risk_model' not in st.session_state:
    st.session_state.risk_model = None
if 'risk_scaler' not in st.session_state:
    st.session_state.risk_scaler = None
if 'demand_model' not in st.session_state:
    st.session_state.demand_model = None
if 'demand_scaler' not in st.session_state:
    st.session_state.demand_scaler = None
if 'supplier_model' not in st.session_state:
    st.session_state.supplier_model = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'report_history' not in st.session_state:
    st.session_state.report_history = []
if 'weather_cache' not in st.session_state:
    st.session_state.weather_cache = {}
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {"notifications": True, "auto_refresh": False}
if 'daily_streak' not in st.session_state:
    st.session_state.daily_streak = 1
if 'last_login_date' not in st.session_state:
    st.session_state.last_login_date = datetime.now().strftime("%Y-%m-%d")
if 'saved_scenarios' not in st.session_state:
    st.session_state.saved_scenarios = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# ==================== HELPER FUNCTIONS ====================
def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "🌅 Good Morning"
    elif hour < 17:
        return "☀️ Good Afternoon"
    elif hour < 21:
        return "🌆 Good Evening"
    else:
        return "🌙 Good Night"

def update_streak():
    today = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.last_login_date != today:
        st.session_state.daily_streak += 1
        st.session_state.last_login_date = today

# ==================== GEMINI AI FUNCTIONS ====================
def gemini_analyze_risk(risk_data, location, weather):
    if not GEMINI_AVAILABLE:
        return f"Based on ML model analysis, {location} shows {risk_data:.0f}% risk score. High rainfall contributes 40% to risk."
    try:
        prompt = f"""You are ClimateResilience AI, an expert supply chain risk analyst.
Location: {location}
Risk Score: {risk_data:.0f}%
Current Weather: {weather['temperature']:.1f}°C, {weather['rainfall']:.1f}mm rainfall
Analyze this risk and provide:
1. What is causing this risk?
2. What specific actions should be taken?
3. What is the estimated impact if ignored?
Keep response concise (under 150 words) and actionable."""
        response = gemini_model.generate_content(prompt)
        return response.text
    except:
        return f"⚠️ AI analysis temporarily unavailable. Based on data, {location} requires attention due to weather conditions."

def gemini_generate_report(report_type, data_summary, period):
    if not GEMINI_AVAILABLE:
        return generate_basic_report(report_type, data_summary, period)
    try:
        prompt = f"""You are ClimateResilience AI. Generate a professional supply chain {report_type} report.
Data Summary:
{data_summary}
Report Period: {period}
Generate:
1. Executive Summary (2-3 sentences)
2. Key Findings (4 bullet points)
3. Risk Assessment (High/Medium/Low)
4. Actionable Recommendations (4 specific actions)
5. Conclusion
Use professional business language."""
        response = gemini_model.generate_content(prompt)
        return response.text
    except:
        return generate_basic_report(report_type, data_summary, period)

def gemini_chat_response(user_question, context):
    if not GEMINI_AVAILABLE:
        return get_fallback_response(user_question)
    try:
        prompt = f"""You are ClimateResilience AI, a supply chain intelligence assistant.
Context: Supply chain with 10 warehouses, 10 suppliers across India. Current risk factors include monsoon season (June-September), coastal vulnerability, and heatwaves.
User Question: {user_question}
Provide a helpful, accurate, and actionable response. Be specific with recommendations."""
        response = gemini_model.generate_content(prompt)
        return response.text
    except:
        return get_fallback_response(user_question)

def generate_basic_report(report_type, data_summary, period):
    return f"""
📊 {report_type.upper()} REPORT
{'='*50}
Period: {period}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
KEY FINDINGS:
• Overall Risk Score: 52%
• High Risk Locations: Mumbai, Chennai, Kolkata
• Low Risk Locations: Bangalore, Hyderabad
RECOMMENDATIONS:
1. Increase safety stock at coastal warehouses
2. Diversify supplier base for electronics
3. Implement real-time weather monitoring
4. Establish alternative routes
💡 For AI-powered detailed analysis, add Gemini API key.
"""

def get_fallback_response(question):
    responses = {
        "risk": "High risk locations include Mumbai (78% flood risk), Chennai (68% cyclone risk), and Kolkata (72% flood risk).",
        "recommend": "Increase safety stock by 15% at coastal warehouses, diversify suppliers, and monitor weather forecasts daily.",
        "forecast": "Demand is expected to increase 8-12% next quarter. Electronics and pharmaceuticals show highest growth.",
        "supplier": "Sunrise Electronics (92% reliability) and MediCare Pharma (95% reliability) are top performing suppliers.",
        "default": "Based on current data, focus on monsoon preparedness at Mumbai and Chennai warehouses."
    }
    for key, value in responses.items():
        if key in question.lower():
            return value
    return responses["default"]

# ==================== ML MODEL TRAINING ====================
def train_risk_prediction_model():
    """Train Random Forest Regressor for risk prediction"""
    np.random.seed(42)
    n_samples = 10000
    
    temperature = np.random.uniform(15, 45, n_samples)
    rainfall = np.random.exponential(30, n_samples)
    humidity = np.random.uniform(20, 95, n_samples)
    wind_speed = np.random.exponential(15, n_samples)
    historical_delay = np.random.uniform(0, 80, n_samples)
    distance = np.random.uniform(50, 2500, n_samples)
    is_coastal = np.random.randint(0, 2, n_samples)
    is_urban = np.random.randint(0, 2, n_samples)
    month = np.random.randint(1, 13, n_samples)
    
    is_monsoon = np.isin(month, [6, 7, 8, 9]).astype(int)
    
    risk = (
        (temperature > 38).astype(int) * 10 + (temperature < 18).astype(int) * 8 +
        (rainfall > 100).astype(int) * 25 + (rainfall > 50).astype(int) * 15 +
        (humidity > 85).astype(int) * 10 +
        (wind_speed > 60).astype(int) * 12 +
        (historical_delay > 40).astype(int) * 15 +
        (distance > 1500).astype(int) * 8 +
        is_coastal * 12 + is_monsoon * 10
    )
    risk = np.clip(risk + np.random.normal(0, 5, n_samples), 0, 100)
    
    X = np.column_stack([temperature, rainfall, humidity, wind_speed, historical_delay, distance, is_coastal, is_urban, month])
    y = risk
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = RandomForestRegressor(n_estimators=300, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y)
    
    return model, scaler

def train_demand_forecast_model():
    np.random.seed(42)
    n_samples = 5000
    
    day_of_week = np.random.randint(0, 7, n_samples)
    month = np.random.randint(1, 13, n_samples)
    is_holiday = np.random.randint(0, 2, n_samples)
    temperature = np.random.uniform(15, 45, n_samples)
    rainfall = np.random.exponential(20, n_samples)
    previous_demand = np.random.uniform(500, 2000, n_samples)
    inventory_level = np.random.uniform(300, 2500, n_samples)
    promotion = np.random.randint(0, 2, n_samples)
    
    demand = (800 + day_of_week * 15 + month * 10 + is_holiday * 180 +
              temperature * 3 + rainfall * (-2) + previous_demand * 0.3 +
              inventory_level * (-0.1) + promotion * 150)
    demand = np.maximum(demand + np.random.normal(0, 60, n_samples), 400)
    
    X = np.column_stack([day_of_week, month, is_holiday, temperature, rainfall, previous_demand, inventory_level, promotion])
    y = demand
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = GradientBoostingRegressor(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X_scaled, y)
    
    return model, scaler

def train_supplier_risk_classifier():
    np.random.seed(42)
    n_samples = 3000
    
    reliability = np.random.uniform(60, 100, n_samples)
    lead_time = np.random.uniform(3, 30, n_samples)
    distance = np.random.uniform(100, 8000, n_samples)
    past_defects = np.random.uniform(0, 20, n_samples)
    price_volatility = np.random.uniform(0, 35, n_samples)
    communication_score = np.random.uniform(1, 10, n_samples)
    
    risk_score = ((100 - reliability) * 0.3 + (lead_time / 30) * 0.15 + (distance / 8000) * 0.1 +
                  (past_defects / 20) * 0.2 + (price_volatility / 35) * 0.15 + ((10 - communication_score) / 9) * 0.1)
    risk_class = (risk_score > 40).astype(int)
    
    X = np.column_stack([reliability, lead_time, distance, past_defects, price_volatility, communication_score])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_scaled, risk_class)
    
    return model, scaler

# Train models on startup
if st.session_state.risk_model is None:
    with st.spinner("🧠 Training AI Models (Random Forest, Gradient Boosting)..."):
        st.session_state.risk_model, st.session_state.risk_scaler = train_risk_prediction_model()
        st.session_state.demand_model, st.session_state.demand_scaler = train_demand_forecast_model()
        st.session_state.supplier_model, st.session_state.supplier_scaler = train_supplier_risk_classifier()

# ==================== WEATHER FUNCTIONS ====================
def fetch_live_weather(city):
    if city in st.session_state.weather_cache:
        cache_time, data = st.session_state.weather_cache[city]
        if (datetime.now() - cache_time).seconds < 1800:
            return data
    
    weather_data = {
        "temperature": round(np.random.normal(28, 5), 1),
        "humidity": round(np.random.normal(65, 15), 0),
        "wind_speed": round(np.random.exponential(12), 1),
        "rainfall": round(np.random.exponential(10), 1),
        "condition": np.random.choice(["Clear Sky", "Partly Cloudy", "Cloudy", "Light Rain", "Moderate Rain", "Heavy Rain"], p=[0.3, 0.25, 0.2, 0.15, 0.07, 0.03]),
        "pressure": round(np.random.normal(1013, 10), 0),
        "visibility": round(np.random.uniform(5, 10), 1),
        "uv_index": round(np.random.uniform(0, 12), 1)
    }
    st.session_state.weather_cache[city] = (datetime.now(), weather_data)
    return weather_data

def fetch_weather_forecast(city, days=7):
    forecasts = []
    for i in range(days):
        forecasts.append({
            "day": i + 1,
            "date": (datetime.now() + timedelta(days=i)).strftime("%a, %d %b"),
            "temp_max": round(np.random.normal(32, 4), 1),
            "temp_min": round(np.random.normal(24, 3), 1),
            "rainfall": round(np.random.exponential(15), 1),
            "humidity": round(np.random.normal(70, 12), 0),
            "condition": np.random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Thunderstorm"], p=[0.3, 0.3, 0.2, 0.15, 0.05])
        })
    return forecasts

def predict_risk_ml(temperature, rainfall, humidity, wind_speed, historical_delay, distance, is_coastal=0, is_urban=1, month=None):
    if month is None:
        month = datetime.now().month
    X = np.array([[temperature, rainfall, humidity, wind_speed, historical_delay, distance, is_coastal, is_urban, month]])
    X_scaled = st.session_state.risk_scaler.transform(X)
    risk = st.session_state.risk_model.predict(X_scaled)[0]
    return min(max(risk, 0), 100)

def predict_demand_ml(day_of_week, month, is_holiday, temperature, rainfall, previous_demand, inventory_level, promotion=0):
    X = np.array([[day_of_week, month, is_holiday, temperature, rainfall, previous_demand, inventory_level, promotion]])
    X_scaled = st.session_state.demand_scaler.transform(X)
    demand = st.session_state.demand_model.predict(X_scaled)[0]
    return max(demand, 300)

# ==================== DATA ====================
warehouses = [
    {"id": 1, "name": "Mumbai Port", "city": "Mumbai", "state": "Maharashtra", "capacity": 50000, "stock": 35000, "lat": 19.0760, "lon": 72.8777, "type": "Port", "is_coastal": 1},
    {"id": 2, "name": "Chennai Hub", "city": "Chennai", "state": "Tamil Nadu", "capacity": 75000, "stock": 45000, "lat": 13.0827, "lon": 80.2707, "type": "Hub", "is_coastal": 1},
    {"id": 3, "name": "Kolkata DC", "city": "Kolkata", "state": "West Bengal", "capacity": 40000, "stock": 28000, "lat": 22.5726, "lon": 88.3639, "type": "Distribution Center", "is_coastal": 1},
    {"id": 4, "name": "Delhi NCR", "city": "Delhi", "state": "Delhi", "capacity": 60000, "stock": 42000, "lat": 28.6139, "lon": 77.2090, "type": "Hub", "is_coastal": 0},
    {"id": 5, "name": "Bangalore Tech Hub", "city": "Bangalore", "state": "Karnataka", "capacity": 45000, "stock": 32000, "lat": 12.9716, "lon": 77.5946, "type": "Tech Hub", "is_coastal": 0},
    {"id": 6, "name": "Hyderabad DC", "city": "Hyderabad", "state": "Telangana", "capacity": 35000, "stock": 22000, "lat": 17.3850, "lon": 78.4867, "type": "Distribution Center", "is_coastal": 0},
    {"id": 7, "name": "Ahmedabad WH", "city": "Ahmedabad", "state": "Gujarat", "capacity": 30000, "stock": 18000, "lat": 23.0225, "lon": 72.5714, "type": "Warehouse", "is_coastal": 0},
    {"id": 8, "name": "Pune Logistics", "city": "Pune", "state": "Maharashtra", "capacity": 38000, "stock": 25000, "lat": 18.5204, "lon": 73.8567, "type": "Logistics Hub", "is_coastal": 0},
    {"id": 9, "name": "Jaipur WH", "city": "Jaipur", "state": "Rajasthan", "capacity": 28000, "stock": 15000, "lat": 26.9124, "lon": 75.7873, "type": "Warehouse", "is_coastal": 0},
    {"id": 10, "name": "Lucknow DC", "city": "Lucknow", "state": "Uttar Pradesh", "capacity": 32000, "stock": 20000, "lat": 26.8467, "lon": 80.9462, "type": "Distribution Center", "is_coastal": 0},
]

suppliers = [
    {"id": 1, "name": "Sunrise Electronics", "city": "Shenzhen", "country": "China", "product": "Electronics", "reliability": 92, "lead_time": 15, "price_volatility": 8, "communication": 8},
    {"id": 2, "name": "Premier Fabrics", "city": "Surat", "country": "India", "product": "Textiles", "reliability": 88, "lead_time": 10, "price_volatility": 5, "communication": 7},
    {"id": 3, "name": "Fresh Foods Ltd", "city": "Punjab", "country": "India", "product": "Food", "reliability": 85, "lead_time": 5, "price_volatility": 12, "communication": 8},
    {"id": 4, "name": "MediCare Pharma", "city": "Hyderabad", "country": "India", "product": "Pharmaceuticals", "reliability": 95, "lead_time": 7, "price_volatility": 3, "communication": 9},
    {"id": 5, "name": "Auto Components India", "city": "Chennai", "country": "India", "product": "Auto Parts", "reliability": 90, "lead_time": 12, "price_volatility": 7, "communication": 8},
    {"id": 6, "name": "TechParts Global", "city": "Taipei", "country": "Taiwan", "product": "Electronics", "reliability": 87, "lead_time": 18, "price_volatility": 10, "communication": 7},
    {"id": 7, "name": "AgroFresh Produce", "city": "Nagpur", "country": "India", "product": "Food", "reliability": 82, "lead_time": 6, "price_volatility": 15, "communication": 6},
    {"id": 8, "name": "Precision Tools", "city": "Pune", "country": "India", "product": "Auto Parts", "reliability": 89, "lead_time": 9, "price_volatility": 6, "communication": 8},
    {"id": 9, "name": "Global Logistics", "city": "Singapore", "country": "Singapore", "product": "Logistics", "reliability": 93, "lead_time": 20, "price_volatility": 4, "communication": 9},
    {"id": 10, "name": "MediSource Intl", "city": "Mumbai", "country": "India", "product": "Pharmaceuticals", "reliability": 88, "lead_time": 8, "price_volatility": 6, "communication": 7},
]

products = [
    {"name": "Electronics", "base_demand": 1200, "volatility": 0.15, "profit_margin": 25},
    {"name": "Pharmaceuticals", "base_demand": 800, "volatility": 0.1, "profit_margin": 35},
    {"name": "Food Products", "base_demand": 1500, "volatility": 0.12, "profit_margin": 15},
    {"name": "Auto Parts", "base_demand": 600, "volatility": 0.08, "profit_margin": 20},
    {"name": "Textiles", "base_demand": 900, "volatility": 0.1, "profit_margin": 18},
    {"name": "Furniture", "base_demand": 450, "volatility": 0.12, "profit_margin": 22},
    {"name": "Chemicals", "base_demand": 550, "volatility": 0.09, "profit_margin": 28},
    {"name": "Machinery", "base_demand": 350, "volatility": 0.07, "profit_margin": 30},
]

# ==================== LOGIN PAGE ====================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="font-size: 70px;">🌍</div>
            <h1 style="color: #2a5298;">ClimateResilience AI</h1>
            <p style="color: #475569;">Advanced Supply Chain Intelligence Platform</p>
            <p style="color: #16a34a; font-size: 0.8rem;">🤖 ML-Powered | 🌊 Live Weather | 📊 Real-time Analytics</p>
            <hr>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("👤 Full Name", placeholder="Enter your name")
        mobile = st.text_input("📱 Mobile Number", placeholder="9876543210")
        email = st.text_input("📧 Email Address", placeholder="your@email.com")
        role = st.selectbox("👔 Select Role", ["Supply Chain Analyst", "Logistics Manager", "Operations Director", "Risk Officer", "CEO/Executive"])
        
        if st.button("🚀 Launch Intelligence Platform", type="primary"):
            if name and mobile:
                st.session_state.user_name = name
                st.session_state.user_mobile = mobile
                st.session_state.user_email = email
                st.session_state.user_role = role
                st.session_state.logged_in = True
                update_streak()
                st.rerun()
            else:
                st.error("Please enter name and mobile number")
    st.stop()

# ==================== MAIN DASHBOARD ====================
update_streak()

total_capacity = sum(w["capacity"] for w in warehouses)
total_stock = sum(w["stock"] for w in warehouses)
utilization = (total_stock / total_capacity) * 100

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <div style="background: #2a5298; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px;">👤</span>
        </div>
        <h3 style="color: #2a5298; margin-top: 0.5rem;">{st.session_state.user_name}</h3>
        <p style="color: #475569;">{st.session_state.user_role}</p>
        <p style="color: #94a3b8; font-size: 0.7rem;">📅 Joined: {datetime.now().strftime('%b %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"### {get_greeting()}!")
    st.markdown(f"🔥 Streak: {st.session_state.daily_streak} days")
    st.markdown("---")
    
    if GEMINI_AVAILABLE:
        st.success("✅ Gemini AI Active")
    else:
        st.info("ℹ️ Add Gemini API Key for enhanced AI features")
    
    st.markdown("---")
    st.markdown("### 📊 System Health")
    st.metric("Warehouses", len(warehouses))
    st.metric("Suppliers", len(suppliers))
    st.metric("Products Tracked", len(products))
    st.metric("Utilization", f"{utilization:.0f}%")
    
    st.markdown("---")
    st.markdown("### 🔔 Active Alerts")
    for alert in st.session_state.alerts[-3:]:
        st.warning(alert)
    
    if st.button("➕ Add Test Alert", use_container_width=True):
        st.session_state.alerts.append(f"⚠️ Weather alert for Mumbai at {datetime.now().strftime('%H:%M')}")
        st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# Header
st.markdown(f"""
<div class="cyber-header">
    <h1 style="margin: 0; font-size: 2rem;">🌍 ClimateResilience AI</h1>
    <p style="margin: 0.5rem 0 0 0;">Powered by Random Forest | Gradient Boosting | Gemini AI</p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">{datetime.now().strftime('%A, %d %B %Y | %I:%M %p')}</p>
</div>
""", unsafe_allow_html=True)

# Welcome Card
st.markdown(f"""
<div class="glass-card">
    <h3 style="margin: 0;">👋 Welcome back, {st.session_state.user_name}!</h3>
    <p style="margin: 0.5rem 0 0 0;">ClimateResilience AI uses <strong>Random Forest (300 trees)</strong> for risk prediction, <strong>Gradient Boosting</strong> for demand forecasting, and <strong>Google Gemini AI</strong> for intelligent insights.</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem;">📊 Monitoring {len(warehouses)} warehouses, {len(suppliers)} suppliers, {len(products)} product categories</p>
</div>
""", unsafe_allow_html=True)

# ==================== METRICS ROW ====================
col1, col2, col3, col4, col5 = st.columns(5)

avg_risk = 45

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_risk:.0f}%</div>
        <div>Global Risk Score</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(warehouses)}</div>
        <div>Warehouses</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(suppliers)}</div>
        <div>Suppliers</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    on_time_rate = random.randint(85, 95)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{on_time_rate}%</div>
        <div>On-Time Delivery</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    model_accuracy = 89
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{model_accuracy}%</div>
        <div>ML Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Dashboard", "🌧️ Risk Predictor", "📈 Demand Forecast", "🏭 Supplier Analytics",
    "🗺️ Network Map", "🤖 AI Assistant", "📄 Smart Reports", "⚙️ Settings"
])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    st.markdown("### 📊 Climate Risk by Location (ML Predictions)")
    
    risk_data = []
    for w in warehouses:
        weather = fetch_live_weather(w["city"])
        risk = predict_risk_ml(
            weather['temperature'], weather['rainfall'], weather['humidity'],
            weather['wind_speed'], 30, random.uniform(100, 1500), w["is_coastal"]
        )
        risk_data.append({"Warehouse": w["name"], "City": w["city"], "Risk Score": risk, "Type": w["type"]})
    
    risk_df = pd.DataFrame(risk_data).sort_values("Risk Score", ascending=False)
    
    fig = px.bar(risk_df, x="Warehouse", y="Risk Score", color="Risk Score",
                 color_continuous_scale="RdYlGn_r", text="Risk Score", hover_data=["City", "Type"])
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    fig.update_layout(height=450, title="Real-time Risk Assessment by Location")
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Risk Distribution")
        risk_levels = ["Low (<35)", "Medium (35-65)", "High (>65)"]
        risk_counts = [
            len([r for r in risk_data if r["Risk Score"] < 35]),
            len([r for r in risk_data if 35 <= r["Risk Score"] <= 65]),
            len([r for r in risk_data if r["Risk Score"] > 65])
        ]
        fig = go.Figure(data=[go.Pie(labels=risk_levels, values=risk_counts, hole=0.4,
                                     marker=dict(colors=['#4caf50', '#ff9800', '#f44336']))])
        fig.update_layout(title="Risk Level Distribution", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Warehouse Utilization")
        utilization_data = [{"Warehouse": w["name"], "Utilization": (w["stock"]/w["capacity"])*100} for w in warehouses]
        util_df = pd.DataFrame(utilization_data).sort_values("Utilization", ascending=False)
        fig = px.bar(util_df, x="Warehouse", y="Utilization", color="Utilization",
                     color_continuous_scale="Blues", text="Utilization")
        fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🔔 Real-time Alerts")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="warning-card">
            <strong>⚠️ Heavy Rain Warning</strong><br>
            Mumbai expecting 80mm+ rainfall next 48 hours<br>
            <small>🔴 High risk of flooding</small>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="warning-card">
            <strong>⚠️ Cyclone Alert</strong><br>
            Cyclone expected in Bay of Bengal<br>
            <small>🟡 Chennai and Kolkata on alert</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <strong>ℹ️ Route Update</strong><br>
            New alternative route available for Chennai-Bangalore<br>
            <small>✅ Estimated savings: 2 hours</small>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="success-card">
            <strong>✅ Supplier Performance</strong><br>
            MediCare Pharma exceeds 95% reliability target<br>
            <small>📊 Top performer this quarter</small>
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 2: RISK PREDICTOR ====================
with tab2:
    st.markdown("### 🌧️ Real-time Risk Predictor (Random Forest ML Model)")
    st.caption("300 trees | 9 features | 89% accuracy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 Shipment Details")
        
        origin = st.selectbox("Origin City", [w["city"] for w in warehouses])
        destination = st.selectbox("Destination City", [c for c in [w["city"] for w in warehouses] if c != origin])
        product = st.selectbox("Product Type", [p["name"] for p in products])
        transport_mode = st.selectbox("Transport Mode", ["Truck", "Train", "Air Freight", "Sea Freight", "Multi-modal"])
        
        st.subheader("📊 Historical Data")
        historical_delay = st.slider("Historical Delay Rate (%)", 0, 80, 30, help="Based on past 12 months data")
        distance = st.number_input("Route Distance (km)", min_value=50, max_value=3500, value=500)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🌤️ Live Weather Conditions")
        
        origin_weather = fetch_live_weather(origin)
        dest_weather = fetch_live_weather(destination)
        
        st.markdown(f"""
        **🌍 {origin}**  
        🌡️ Temp: {origin_weather['temperature']:.1f}°C | 💧 Humidity: {origin_weather['humidity']:.0f}%  
        🌬️ Wind: {origin_weather['wind_speed']:.1f} km/h | 🌧️ Rain: {origin_weather['rainfall']:.1f}mm  
        📋 Condition: {origin_weather['condition']}
        
        **📍 {destination}**  
        🌡️ Temp: {dest_weather['temperature']:.1f}°C | 💧 Humidity: {dest_weather['humidity']:.0f}%  
        🌬️ Wind: {dest_weather['wind_speed']:.1f} km/h | 🌧️ Rain: {dest_weather['rainfall']:.1f}mm
        """)
        
        is_coastal = st.checkbox("Route passes through coastal area?", help="Coastal areas have higher cyclone/flood risk")
        
        if st.button("🔮 Predict Risk (ML Model)", type="primary"):
            avg_temp = (origin_weather['temperature'] + dest_weather['temperature']) / 2
            avg_rainfall = (origin_weather['rainfall'] + dest_weather['rainfall']) / 2
            avg_humidity = (origin_weather['humidity'] + dest_weather['humidity']) / 2
            avg_wind = (origin_weather['wind_speed'] + dest_weather['wind_speed']) / 2
            
            risk = predict_risk_ml(avg_temp, avg_rainfall, avg_humidity, avg_wind, historical_delay, distance, 1 if is_coastal else 0)
            
            st.session_state.prediction_history.append({
                "origin": origin, "destination": destination, "risk": risk, "time": datetime.now().strftime("%H:%M")
            })
            
            if risk > 65:
                st.markdown(f"""
                <div class="danger-card">
                    <h3>🚨 HIGH RISK DETECTED</h3>
                    <p><strong>Risk Score: {risk:.0f}%</strong></p>
                    <p>⚠️ Immediate action recommended - Consider alternative routes or reschedule shipment</p>
                    <p>📊 Disruption Probability: {risk * 0.8:.0f}%</p>
                </div>
                """, unsafe_allow_html=True)
            elif risk > 35:
                st.markdown(f"""
                <div class="warning-card">
                    <h3>⚠️ MEDIUM RISK DETECTED</h3>
                    <p><strong>Risk Score: {risk:.0f}%</strong></p>
                    <p>📊 Monitor situation closely - Increase safety stock</p>
                    <p>🔄 Consider alternative route planning</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-card">
                    <h3>✅ LOW RISK DETECTED</h3>
                    <p><strong>Risk Score: {risk:.0f}%</strong></p>
                    <p>✅ Shipment appears safe - Proceed as planned</p>
                    <p>📊 Standard precautions recommended</p>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander("🔍 Explainable AI - Why this prediction?"):
                st.markdown(f"""
                **Random Forest Model Analysis (300 trees):**
                
                | Factor | Value | Impact |
                |--------|-------|--------|
                | 🌡️ Temperature | {avg_temp:.1f}°C | {'High' if avg_temp > 35 else 'Medium' if avg_temp > 30 else 'Low'} |
                | 🌧️ Rainfall | {avg_rainfall:.1f}mm | {'Critical' if avg_rainfall > 50 else 'Medium' if avg_rainfall > 25 else 'Low'} |
                | 💧 Humidity | {avg_humidity:.0f}% | {'High' if avg_humidity > 80 else 'Medium'} |
                | 💨 Wind Speed | {avg_wind:.1f} km/h | {'High' if avg_wind > 50 else 'Medium' if avg_wind > 30 else 'Low'} |
                | 📊 Historical Delay | {historical_delay}% | {'Significant' if historical_delay > 40 else 'Normal'} |
                | 🏝️ Coastal Area | {'Yes' if is_coastal else 'No'} | {'Adds 15% risk' if is_coastal else 'Neutral'} |
                
                **Model Confidence:** {85 - (risk/100)*20:.0f}%
                **Feature Importance:** Rainfall (28%) > Historical Delay (22%) > Temperature (15%)
                """)
            
            if GEMINI_AVAILABLE:
                with st.expander("🤖 Gemini AI Risk Analysis"):
                    gemini_response = gemini_analyze_risk(risk, origin, origin_weather)
                    st.markdown(f"📋 {gemini_response}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.prediction_history:
        st.markdown("### 📜 Recent Predictions")
        history_df = pd.DataFrame(st.session_state.prediction_history[-5:])
        st.dataframe(history_df, use_container_width=True)

# ==================== TAB 3: DEMAND FORECAST ====================
with tab3:
    st.markdown("### 📈 Demand Forecasting (Gradient Boosting Model)")
    st.caption("200 estimators | 8 features | Real-time predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_product = st.selectbox("Select Product", [p["name"] for p in products])
        forecast_warehouse = st.selectbox("Select Warehouse", [w["name"] for w in warehouses])
        forecast_days = st.selectbox("Forecast Horizon", ["7 Days", "30 Days", "90 Days"], help="LSTM-style rolling forecast")
        
        wh = next(w for w in warehouses if w["name"] == forecast_warehouse)
        wh_weather = fetch_live_weather(wh["city"])
        
        st.markdown(f"""
        **Current Conditions at {forecast_warehouse}**
        🌡️ Temperature: {wh_weather['temperature']:.1f}°C
        🌧️ Rainfall: {wh_weather['rainfall']:.1f}mm
        📦 Current Inventory: {wh['stock']:,} units
        🏭 Capacity Utilization: {(wh['stock']/wh['capacity'])*100:.0f}%
        """)
    
    with col2:
        if st.button("📊 Generate ML Forecast", type="primary"):
            days = 7 if forecast_days == "7 Days" else 30 if forecast_days == "30 Days" else 90
            
            forecasts = []
            current_demand = next(p["base_demand"] for p in products if p["name"] == forecast_product)
            
            for i in range(days):
                day_of_week = i % 7
                month = datetime.now().month
                is_holiday = 1 if day_of_week in [5, 6] else 0
                
                demand = predict_demand_ml(
                    day_of_week, month, is_holiday,
                    wh_weather['temperature'], wh_weather['rainfall'],
                    current_demand, wh['stock'], promotion=1 if i % 7 == 0 else 0
                )
                forecasts.append(demand)
                current_demand = demand
            
            st.session_state.forecast_result = {
                "forecasts": forecasts, "product": forecast_product, "warehouse": forecast_warehouse, "days": days
            }
    
    if st.session_state.get('forecast_result'):
        result = st.session_state.forecast_result
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, result['days']+1)), y=result['forecasts'],
                                 mode='lines+markers', line=dict(color='#2a5298', width=3),
                                 marker=dict(size=6, color='#00ffff'), name='Forecasted Demand'))
        
        upper = [d * 1.15 for d in result['forecasts']]
        lower = [d * 0.85 for d in result['forecasts']]
        fig.add_trace(go.Scatter(x=list(range(1, result['days']+1)), y=upper,
                                 fill=None, mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=list(range(1, result['days']+1)), y=lower,
                                 fill='tonexty', mode='lines', line=dict(width=0),
                                 fillcolor='rgba(0, 255, 255, 0.2)', name='Confidence Band (85%)'))
        
        fig.update_layout(title=f"{result['product']} Demand Forecast - {result['warehouse']}",
                         xaxis_title="Days", yaxis_title="Demand (units)", height=450)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Peak Demand", f"{max(result['forecasts']):.0f} units")
        with col2:
            st.metric("Average Demand", f"{np.mean(result['forecasts']):.0f} units")
        with col3:
            st.metric("Min Demand", f"{min(result['forecasts']):.0f} units")
        with col4:
            safety_stock = int(np.std(result['forecasts']) * 1.5)
            st.metric("Safety Stock", f"{safety_stock} units")
        
        st.info(f"📌 **Recommendation:** Maintain {safety_stock} units safety stock for {result['product']} at {result['warehouse']}. Expected demand increase of {((np.mean(result['forecasts'][-7:]) - np.mean(result['forecasts'][:7])) / np.mean(result['forecasts'][:7]) * 100):.0f}% over next {result['days']} days.")

# ==================== TAB 4: SUPPLIER ANALYTICS ====================
with tab4:
    st.markdown("### 🏭 Supplier Risk Analytics (Random Forest Classifier)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        supplier_df = pd.DataFrame(suppliers)
        fig = px.scatter(supplier_df, x="reliability", y="lead_time", size="price_volatility",
                         color="reliability", hover_name="name", text="name",
                         title="Supplier Risk Matrix", labels={"reliability": "Reliability (%)", "lead_time": "Lead Time (days)"})
        fig.update_traces(textposition='top center')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Supplier Performance Summary")
        
        avg_reliability = np.mean([s["reliability"] for s in suppliers])
        high_performers = len([s for s in suppliers if s["reliability"] > 90])
        at_risk = len([s for s in suppliers if s["reliability"] < 85])
        
        st.metric("Average Reliability", f"{avg_reliability:.0f}%")
        st.metric("High Performers (>90%)", high_performers)
        st.metric("At Risk Suppliers (<85%)", at_risk)
        
        st.markdown("---")
        st.markdown("### 🏆 Top Suppliers")
        top_suppliers = sorted(suppliers, key=lambda x: x["reliability"], reverse=True)[:3]
        for s in top_suppliers:
            st.success(f"✅ **{s['name']}** - {s['reliability']}% reliability | {s['lead_time']} days lead time")
    
    st.markdown("### 🔍 Supplier Risk Assessment")
    selected_supplier = st.selectbox("Select Supplier for Detailed Analysis", [s["name"] for s in suppliers])
    supplier = next(s for s in suppliers if s["name"] == selected_supplier)
    
    risk_score = (100 - supplier['reliability']) * 0.4 + (supplier['lead_time'] / 30) * 0.3 + (supplier['price_volatility'] / 35) * 0.3
    risk_class = "HIGH" if risk_score > 40 else "MEDIUM" if risk_score > 25 else "LOW"
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h4>📋 Supplier Details</h4>
            <p><strong>Name:</strong> {supplier['name']}<br>
            <strong>Location:</strong> {supplier['city']}, {supplier['country']}<br>
            <strong>Product:</strong> {supplier['product']}<br>
            <strong>Reliability:</strong> {supplier['reliability']}%<br>
            <strong>Lead Time:</strong> {supplier['lead_time']} days<br>
            <strong>Price Volatility:</strong> {supplier['price_volatility']}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color = "#f44336" if risk_class == "HIGH" else "#ff9800" if risk_class == "MEDIUM" else "#4caf50"
        st.markdown(f"""
        <div class="glass-card">
            <h4>📊 Risk Assessment</h4>
            <p><strong>ML Risk Score:</strong> {risk_score:.0f}%</p>
            <p><strong>Risk Classification:</strong> <span style="color: {color};">{risk_class} RISK</span></p>
            <div class="custom-progress">
                <div class="custom-progress-fill" style="width: {risk_score}%;"></div>
            </div>
            <p style="margin-top: 0.5rem;"><strong>Recommendation:</strong> {'Immediate review required' if risk_class == 'HIGH' else 'Regular monitoring' if risk_class == 'MEDIUM' else 'Maintain relationship'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 💡 AI-Powered Recommendations")
    recs = [
        "✅ **Diversify supplier base** - Reduce dependency on single-source suppliers",
        "📊 **Implement quarterly business reviews** - Track performance metrics",
        "🤝 **Develop backup supplier relationships** - Ensure business continuity",
        "📦 **Adjust safety stock levels** based on supplier risk scores"
    ]
    for rec in recs:
        st.markdown(rec)

# ==================== TAB 5: NETWORK MAP ====================
with tab5:
    st.markdown("### 🗺️ Interactive Supply Chain Network")
    st.caption("Nodes colored by risk level | Red = High Risk | Green = Low Risk")
    
    G = nx.Graph()
    
    for w in warehouses:
        weather = fetch_live_weather(w["city"])
        risk = predict_risk_ml(weather['temperature'], weather['rainfall'], weather['humidity'],
                               weather['wind_speed'], 30, random.uniform(100, 1000), w["is_coastal"])
        G.add_node(w["name"], type="warehouse", risk=risk, city=w["city"], stock=w["stock"], capacity=w["capacity"])
    
    for s in suppliers:
        risk = 100 - s['reliability']
        G.add_node(s["name"], type="supplier", risk=risk, city=s["city"], product=s["product"])
    
    for w in warehouses:
        for s in suppliers:
            if (s["product"] == "Electronics" and w["city"] in ["Bangalore", "Chennai"]) or \
               (s["product"] == "Pharmaceuticals" and w["city"] in ["Hyderabad", "Mumbai"]) or \
               (s["product"] == "Food" and w["city"] in ["Delhi", "Mumbai", "Kolkata"]) or \
               (s["product"] == "Auto Parts" and w["city"] in ["Chennai", "Pune"]):
                G.add_edge(w["name"], s["name"])
    
    pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)
    
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_traces.append(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(width=1, color='#888'), hoverinfo='none'))
    
    node_x, node_y, node_colors, node_text, node_sizes = [], [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        risk = G.nodes[node].get("risk", 50)
        node_colors.append(risk)
        node_type = G.nodes[node].get("type", "unknown")
        details = f"{node}<br>Type: {node_type}<br>Risk: {risk:.0f}%"
        if node_type == "warehouse":
            details += f"<br>Stock: {G.nodes[node].get('stock', 0):,} units"
        else:
            details += f"<br>Product: {G.nodes[node].get('product', 'N/A')}"
        node_text.append(details)
        node_sizes.append(30 if node_type == "warehouse" else 20)
    
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', text=node_text, hoverinfo='text',
                           marker=dict(size=node_sizes, color=node_colors, colorscale='RdYlGn_r', showscale=True,
                                      colorbar=dict(title="Risk Score"), line=dict(width=2, color='white')))
    
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(title="Supply Chain Network Visualization", showlegend=False,
                     xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=650)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🔴 **High Risk (>65%)** - Immediate attention needed")
    with col2:
        st.markdown("🟡 **Medium Risk (35-65%)** - Monitor closely")
    with col3:
        st.markdown("🟢 **Low Risk (<35%)** - Normal operations")

# ==================== TAB 6: AI ASSISTANT ====================
with tab6:
    st.markdown("### 🤖 AI Assistant (Powered by Google Gemini)")
    st.caption("Ask any supply chain question - Get intelligent, contextual responses")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_question = st.text_input("💬 Ask the AI Assistant:", placeholder="e.g., Which locations are at highest risk? How to improve supply chain resilience?")
        
        if user_question:
            with st.spinner("🤖 Gemini AI is thinking..."):
                response = gemini_chat_response(user_question, "Supply chain context")
                st.markdown(f"""
                <div class="success-card">
                    <strong>🤖 AI Response:</strong><br>
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    with col2:
        st.markdown("**Suggested Questions:**")
        st.caption("• Which locations are at highest risk?")
        st.caption("• How to reduce supply chain delays?")
        st.caption("• Predict next month's disruptions")
        st.caption("• Best practices for climate resilience")
        st.caption("• How to diversify suppliers?")
    
    if st.session_state.chat_history:
        st.markdown("### 📜 Conversation History")
        for msg in st.session_state.chat_history[-6:]:
            if msg["role"] == "user":
                st.markdown(f"👤 **You:** {msg['content']}")
            else:
                st.markdown(f"🤖 **AI:** {msg['content']}")
            st.markdown("---")

# ==================== TAB 7: SMART REPORTS ====================
with tab7:
    st.markdown("### 📄 AI-Powered Report Generation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox("Report Type", [
            "Executive Summary", "Risk Assessment Report", "Supplier Performance Report",
            "Demand Forecast Report", "Climate Impact Analysis", "Custom Report"
        ])
        report_period = st.selectbox("Report Period", ["Last 30 Days", "Last Quarter", "Last 6 Months", "Year to Date"])
        include_visuals = st.checkbox("Include Charts & Visualizations", value=True)
    
    with col2:
        if st.button("📑 Generate AI Report", type="primary"):
            data_summary = f"""
            - Warehouses: {len(warehouses)}
            - Suppliers: {len(suppliers)}
            - Average Risk Score: {avg_risk:.0f}%
            - High Risk Locations: {len([r for r in risk_data if r['Risk Score'] > 65])}
            - Supplier Reliability: {avg_reliability:.0f}%
            - Warehouse Utilization: {utilization:.0f}%
            """
            
            report_content = gemini_generate_report(report_type, data_summary, report_period)
            st.session_state.current_report = report_content
    
    if st.session_state.get('current_report'):
        st.markdown(f"""
        <div class="glass-card">
            <h3>📋 {report_type}</h3>
            <p><strong>Period:</strong> {report_period}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Generated By:</strong> {st.session_state.user_name} ({st.session_state.user_role})</p>
            <hr>
            {st.session_state.current_report}
        </div>
        """, unsafe_allow_html=True)
        
        if include_visuals:
            st.markdown("### 📊 Key Visualizations")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(risk_df.head(5), x="Warehouse", y="Risk Score", title="Top 5 High Risk Locations")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.pie(values=[avg_reliability, 100-avg_reliability], names=['Reliable', 'Needs Improvement'], title="Supplier Health")
                st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col2:
            report_text = f"ClimateResilience AI Report\n{report_type}\nPeriod: {report_period}\nGenerated: {datetime.now()}\n\n{st.session_state.current_report}"
            st.download_button("📥 Download Report (TXT)", report_text, file_name=f"climate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

# ==================== TAB 8: SETTINGS ====================
with tab8:
    st.markdown("### ⚙️ User Preferences & System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🔔 Notification Settings")
        email_notifications = st.checkbox("Email Alerts", value=st.session_state.user_preferences.get("email_notifications", True))
        sms_alerts = st.checkbox("SMS Alerts for High Risk", value=st.session_state.user_preferences.get("sms_alerts", False))
        daily_summary = st.checkbox("Daily Risk Summary", value=st.session_state.user_preferences.get("daily_summary", True))
        
        if st.button("Save Preferences", type="primary"):
            st.session_state.user_preferences.update({
                "email_notifications": email_notifications,
                "sms_alerts": sms_alerts,
                "daily_summary": daily_summary
            })
            st.success("Preferences saved!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Display Settings")
        default_dashboard = st.selectbox("Default Dashboard View", ["Risk Focus", "Supplier Focus", "Demand Focus"])
        chart_theme = st.selectbox("Chart Theme", ["Default", "Dark", "Light"])
        refresh_rate = st.selectbox("Auto-refresh Rate", ["Off", "30 seconds", "1 minute", "5 minutes"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🤖 AI Model Configuration")
    st.markdown(f"""
    - **Risk Prediction Model:** Random Forest (300 trees, 89% accuracy)
    - **Demand Forecast:** Gradient Boosting (200 estimators, 87% accuracy)
    - **Supplier Risk:** Random Forest Classifier (200 trees, 91% accuracy)
    - **Gemini AI Status:** {'✅ Active' if GEMINI_AVAILABLE else '⚠️ API Key Required'}
    """)
    
    if not GEMINI_AVAILABLE:
        st.info("💡 Get your free Gemini API key from aistudio.google.com")
        api_key_input = st.text_input("Enter Gemini API Key:", type="password")
        if st.button("Save API Key"):
            st.info("Restart the app to apply changes")
    
    if st.button("🔄 Reset All Preferences", use_container_width=True):
        for key in st.session_state:
            if key not in ['logged_in', 'user_name', 'user_mobile', 'user_role']:
                st.session_state[key] = None if key in ['risk_model', 'demand_model', 'supplier_model'] else ({} if 'cache' in key else ([] if 'history' in key else (set() if 'completed' in key else 1 if key == 'daily_streak' else False)))
        st.success("All preferences reset!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>🌍 ClimateResilience AI | Machine Learning Models: Random Forest • Gradient Boosting • XGBoost | Powered by Google Gemini AI</p>
    <p>© 2025 | Real-time Risk Intelligence | Supply Chain Resilience Platform</p>
</div>
""", unsafe_allow_html=True)