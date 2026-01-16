import streamlit as st
import pandas as pd
import math

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Print Cost Calculator 2026", layout="wide")

# --- CSS HACK: FORCE DARK/BLACK THEME ---
st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #FAFAFA; }
        [data-testid="stSidebar"] { background-color: #111111; }
        .stTextInput > div > div > input { color: #FAFAFA; }
        .stNumberInput > div > div > input { color: #FAFAFA; }
        p, h1, h2, h3, label { color: #FAFAFA !important; }
    </style>
""", unsafe_allow_html=True)

st.title("👕 Wholesale Price & Margin Calculator")
st.markdown("Based on Screen Print Price List")
st.markdown("---")

# --- 2. PRICING LOGIC ---

def get_price_from_matrix(units, colors):
    if units < 12: return 0.0
    if colors == 0: return 0.0
    quantities = [12, 24, 48, 72, 144, 288, 576, 1200, 5000, 10000, 20000]
    pricing = {
        1: {12: 3.2, 24: 2.9, 48: 2.55, 72: 2.35, 144: 2.1, 288: 2.0, 576: 1.8, 1200: 1.55, 5000: 1.45, 10000: 1.4, 20000: 1.35},
        2: {12: 3.85, 24: 3.45, 48: 2.9, 72: 2.55, 144: 2.35, 288: 2.1, 576: 1.9, 1200: 1.65, 5000: 1.9, 10000: 1.8, 20000: 1.65},
        3: {12: 4.6, 24: 4.2, 48: 3.65, 72: 3.3, 144: 3.1, 288: 2.9, 576: 2.65, 1200: 2.45, 5000: 2.1, 10000: 2.0, 20000: 1.9},
        4: {12: 5.4, 24: 5.1, 48: 4.75, 72: 4.4, 144: 4.1, 288: 3.75, 576: 3.55, 1200: 3.45, 5000: 3.0, 10000: 2.9, 20000: 2.65},
        5: {12: 6.2, 24: 5.75, 48: 5.3, 72: 4.85, 144: 4.55, 288: 3.55, 576: 3.45, 1200: 3.2, 5000: 3.1, 10000: 2.75, 20000: 2.55},
        6: {12: 6.85, 24: 6.4, 48: 6.05, 72: 5.65, 144: 5.3, 288: 4.3, 576: 4.2, 1200: 3.85, 5000: 3.55, 10000: 3.3, 20000: 3.2},
        7: {12: 7.5, 24: 6.85, 48: 6.75, 72: 6.3, 144: 5.95, 288: 5.4, 576: 5.2, 1200: 4.85, 5000: 4.4, 10000: 3.85, 20000: 3.65},
        8: {12: 7.85, 24: 7.3, 48: 6.95, 72: 6.75, 144: 6.4, 288: 5.85, 576: 5.5, 1200: 5.2, 5000: 4.85, 10000: 4.1, 20000: 3.85},
        9: {12:
