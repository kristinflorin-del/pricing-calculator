import streamlit as st
import pandas as pd

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Print Cost Calculator 2026", layout="wide")

st.title("👕 Wholesale Cost & Margin Calculator (2026)")
st.markdown("Based on Sans Price List & Wholesale Logic")
st.markdown("---")

# --- 2. PRICING LOGIC ---

def get_price_from_matrix(units, colors):
    """
    Looks up the exact price from the 'Sans Price List' matrix.
    """
    if units < 12:
        return 0.0
    if colors == 0:
        return 0.0
        
    quantities = [12, 24, 48, 72, 144, 288, 576, 1200, 5000, 10000, 20000]
    
    # 2026 Pricing Matrix
    pricing = {
        1: {12: 3.2, 24: 2.9, 48: 2.55, 72: 2.35, 144: 2.1, 288: 2.0, 576: 1.8, 1200: 1.55, 5000: 1.45, 10000: 1.4, 20000: 1.35},
        2: {12: 3.85, 24: 3.45, 48: 2.9, 72: 2.55, 144: 2.35, 288: 2.1, 576: 1.9, 1200: 1.65, 5000: 1.9, 10000: 1.8, 20000: 1.65},
        3: {12: 4.6, 24: 4.2, 48: 3.65, 72: 3.3, 144: 3.1, 288: 2.9, 576: 2.65, 1200: 2.45, 5000: 2.1, 10000: 2.0, 20000: 1.9},
        4: {12: 5.4, 24: 5.1, 48: 4.75, 72: 4.4, 144: 4.1, 288: 3.75, 576: 3.55, 1200: 3.45, 5000: 3.0, 10000: 2.9, 20000: 2.65},
        5: {12: 6.2, 24: 5.75, 48: 5.3, 72: 4.85, 144: 4.55, 288: 3.55, 576: 3.45, 1200: 3.2, 5000: 3.1, 10000: 2.75, 20000: 2.55},
        6: {12: 6.85, 24: 6.4, 48: 6.05, 72: 5.65, 144: 5.3, 288: 4.3, 576: 4.2, 1200: 3.85, 5000: 3.55, 10000: 3.3, 20000: 3.2},
        7: {12: 7.5, 24: 6.85, 48: 6.75, 72: 6.3, 144: 5.95, 288: 5.4, 576: 5.2, 1200: 4.85, 5000: 4.4, 10000: 3.85, 20000: 3.65},
        8: {12: 7.85, 24: 7.3, 48: 6.95, 72: 6.75, 144: 6.4, 288: 5.85, 576: 5.5, 1200: 5.2, 5000: 4.85, 10000: 4.1, 20000: 3.85},
        9: {12: 8.4, 24: 7.85, 48: 7.3, 72: 6.95, 144: 6.6, 288: 5.95, 576: 5.65, 1200: 5.4, 5000: 5.2, 10000: 4.3, 20000: 3.65},
        10: {12: 9.15, 24: 8.4, 48: 8.1, 72: 8.25, 144: 7.95, 288: 7.15, 576: 6.85, 1200: 6.5, 5000: 5.4, 10000: 4.55, 20000: 3.55}
    }
    
    applicable_break = 12
    for q in quantities:
        if units >= q:
            applicable_break = q
        else:
            break
    
    c = min(colors, 10)
    return pricing.get(c, {}).get(applicable_break, 0.0)

# Automatic Flash Calculation Helper
def calculate_flash(screens):
    # Formula: MAX(0, 0.1 * (Screens - 1))
    return max(0.0, 0.1 * (screens - 1))

# --- 3. INPUTS SIDEBAR ---
with st.sidebar:
    st.header("1. Job Specs")
    units = st.number_input("Units (Quantity)", min_value=12, value=250, step=1)
    
    st.header("2. Print Locations")
    screens_f = st.number_input("Screens Front", 0, 10, 3)
    screens_b = st.number_input("Screens Back", 0, 10, 2)
    screens_rs = st.number_input("Screens Right Sleeve", 0, 10, 3)
    screens_ls = st.number_input("Screens Left Sleeve", 0, 10, 0)
    
    total_screens = screens_f + screens_b + screens_rs + screens_ls
    
    # Auto-Calculate Flash Costs
    flash_f = calculate_flash(screens_f)
    flash_b = calculate_flash(screens_b)
    flash_rs = calculate_flash(screens_rs)
    flash_ls = calculate_flash(screens_ls)
    total_flash = flash_f + flash_b + flash_rs + flash_ls
    
    st.info(f"Total Screens: {total_screens} | Auto-Flash Cost: ${total_flash:.2f}")

    # --- LOCKED SCREEN LOGIC START ---
    st.header("3. Setup & Fees")
    is_reorder = st.toggle("Is this a Reorder?", value=False)
    
    # Logic: New=23, Reorder>144=0, Reorder<145=15
    if is_reorder:
        if units > 144:
            calculated_screen_price = 0.0
            lock_msg = "Reorder >144 pcs: Free"
        else:
            calculated_screen_price = 15.0
            lock_msg = "Reorder <145 pcs: $15"
    else:
        calculated_screen_price = 23.0
        lock_msg = "New Order Standard"
        
    st.text_input(
        f"Price Per Screen - {lock_msg}", 
        value=f"${calculated_screen_price:.2f}",
        disabled=True
    )
    # --- LOCKED SCREEN LOGIC END ---
    
    # --- LOCKED FLEECE LOGIC START ---
    is_fleece = st.checkbox("Is Fleece?")
    
    if is_fleece:
        fleece_charge = 0.20
    else:
        fleece_charge = 0.00
        
    # Read-only text input for fleece charge
    st.text_input(
        "Fleece Charge (Per Unit)",
        value=f"${fleece_charge:.2f}",
        disabled=True
    )
    # --- LOCKED FLEECE LOGIC END ---

    st.header("4. Product Cost")
    retail_price = st.number_input("Retail Price ($)", value=36.70)
    blank_price = st.number_input("Blank Garment Price ($)", value=4.21)

# --- 4. CALCULATIONS ---

use_auto_pricing = st.toggle("Use Automated 'Sans Price List' Lookup?", value=True)

if use_auto_pricing:
    cost_front = get_price_from_matrix(units, screens_f)
    cost_back = get_price_from_matrix(units, screens_b)
    cost_rs = get_price_from_matrix(units, screens_rs)
    cost_ls = get_price_from_matrix(units, screens_ls)
else:
    st.warning("Manual Mode Active")
    col1, col2, col3, col4 = st.columns(4)
    cost_front = col1.number_input("Print Cost Front", value=3.10)
    cost_back = col2.number_input("Print Cost Back", value=2.35)
    cost_rs = col3.number_input("Print Cost R.Sleeve", value=3.80)
    cost_ls = col4.number_input("Print Cost L.Sleeve", value=0.00)

# Variable Expenses
with st.expander("Variable Expenses (%)"):
    ve_rebates = st.number_input("Buyer Rebates %", value=0.0) / 100
    ve_royalties = st.number_input("Licensing Royalties %", value=0.0) / 100
    ve_commissions = st.number_input("Sales Commissions %", value=4.4) / 100
    ve_freelance = st.number_input("Freelance Artist %", value=0.0) / 100

# --- 5. FINAL MATH ---

# 1. Base Print Cost Sum
raw_print_cost_per_unit
