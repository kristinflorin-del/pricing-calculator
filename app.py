import streamlit as st
import pandas as pd
import math
import plotly.express as px
import streamlit.components.v1 as components

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="Print Cost Calculator 2026", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- CSS: SHARP LOGO ADAPTER (ROBUST VERSION) ---
st.markdown("""
    <style>
        /* BASE RULE: Light Mode (Default) */
        [data-testid="stSidebar"] img {
            transition: filter 0.3s ease;
            filter: invert(1) brightness(0); /* Forces White -> Black */
        }

        /* OVERRIDE: Dark Mode */
        [data-theme="dark"] [data-testid="stSidebar"] img {
            filter: none; /* Stays original White */
        }
        
        /* FALLBACK: System Preference Dark Mode */
        @media (prefers-color-scheme: dark) {
            [data-testid="stSidebar"] img {
                filter: none; /* Stays original White */
            }
        }
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
        9: {12: 8.4, 24: 7.85, 48: 7.3, 72: 6.95, 144: 6.6, 288: 5.95, 576: 5.65, 1200: 5.4, 5000: 5.2, 10000: 4.3, 20000: 3.65},
        10: {12: 9.15, 24: 8.4, 48: 8.1, 72: 8.25, 144: 7.95, 288: 7.15, 576: 6.85, 1200: 6.5, 5000: 5.4, 10000: 4.55, 20000: 3.55}
    }
    applicable_break = 12
    for q in quantities:
        if units >= q: applicable_break = q
        else: break
    c = min(colors, 10)
    return pricing.get(c, {}).get(applicable_break, 0.0)

def calculate_flash(screens):
    return max(0.0, 0.1 * (screens - 1))

def get_margin_color_style(value, is_gross=True):
    if value < 0: return "red"
    if is_gross:
        # GM Logic: < 46 Orange, < 50 Yellow, >= 50 Green
        if value < 46: return "orange" 
        elif value < 50: return "#D4AC0D" # Dark Gold
        else: return "green" 
    else:
        # CM Logic: < 16 Orange, < 25 Yellow, >= 25 Green
        if value < 16: return "orange" 
        elif value < 25: return "#D4AC0D" 
        else: return "green" 

# --- 3. INPUTS SIDEBAR ---
with st.sidebar:
    # Logo
    try:
        st.image("logo.png", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
    except:
        st.warning("⚠️ Logo not found.")

    # --- SECTION 1 CONTAINER (To be filled last) ---
    st.header("1. Order Details")
    retail_container = st.container()
    
    # Standard Inputs for Sec 1
    units = st.number_input("Quantity", min_value=12, value=144, step=1)
    
    blank_price = st.number_input(
        "Blank Garment Cost ($)", 
        value=3.33,
        help="Find prices on [ACC](https://www.orderacc.com)"
    )
    
    # --- SECTION 2 ---
    st.header("2. Print Locations")
    screens_f = st.number_input("Screens Front", 0, 10, 3)
    screens_b = st.number_input("Screens Back", 0, 10, 0)
    screens_rs = st.number_input("Screens Right Sleeve", 0, 10, 0)
    screens_ls = st.number_input("Screens Left Sleeve", 0, 10, 0)
    total_screens = screens_f + screens_b + screens_rs + screens_ls
    flash_f = calculate_flash(screens_f)
    flash_b = calculate_flash(screens_b)
    flash_rs = calculate_flash(screens_rs)
    flash_ls = calculate_flash(screens_ls)
    total_flash = flash_f + flash_b + flash_rs + flash_ls
    st.info(f"Total Screens: {total_screens} | Flash Cost: ${total_flash:.2f}")

    # --- SECTION 3 ---
    st.header("3. Setup & Fees")
    is_reorder = st.toggle("Is this a Reorder?", value=False)
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
    st.text_input(f"Price Per Screen - {lock_msg}", value=f"${calculated_screen_price:.2f}", disabled=True)
    
    is_fleece = st.toggle("Is the product fleece?", value=False)
    fleece_charge = 0.20 if is_fleece else 0.00
    st.text_input("Fleece Charge (Per Unit)", value=f"${fleece_charge:.2f}", disabled=True)

    # --- SECTION 4 ---
    st.header("4. Variable Expenses (%)")
    ve_rebates = st.number_input("Buyer Rebates %", value=2.5) / 100
    ve_royalties = st.number_input("Licensing Royalties %", value=18.0) / 100
    ve_commissions = st.number_input("Sales Commissions %", value=4.4) / 100
    ve_freelance = st.number_input("Freelance Artist %", value=0.0) / 100

# --- 4. CALCULATE COGS (For Retail Logic) ---

use_auto_pricing = st.toggle("Use Automated Screen Print Price List Lookup?", value=True)

if use_auto_pricing:
    cost_front = get_price_from_matrix(units, screens_f)
    cost_back = get_price_from_matrix(units, screens_b)
    cost_rs = get_price_from_matrix(units, screens_rs)
    cost_ls = get_price_from_matrix(units, screens_ls)
else:
    col1, col2, col3, col4 = st.columns(4)
    cost_front = col1.number_input("Print Cost Front", value=3.10)
    cost_back = col2.number_input("Print Cost Back", value=2.35)
    cost_rs = col3.number_input("Print Cost R.Sleeve", value=3.80)
    cost_ls = col4.number_input("Print Cost L.Sleeve", value=0.00)

raw_print_cost_per_unit = cost_front + cost_back + cost_rs + cost_ls + total_flash
total_screen_fees = total_screens * calculated_screen_price
gross_print_run_cost = (raw_print_cost_per_unit * units) + total_screen_fees
discounted_print_run_cost = gross_print_run_cost * (1 - 0.12)
final_print_cost_per_unit = discounted_print_run_cost / units
vas_cost = 1.60
total_cogs = final_print_cost_per_unit + blank_price + vas_cost + fleece_charge

# Calculated globally here for use in both Retail Logic and Scenario Logic
total_var_expense_pct = ve_rebates + ve_royalties + ve_commissions + ve_freelance

# --- 5. RETAIL PRICE SUGGESTION LOGIC ---

with retail_container:
    use_suggested = st.toggle("Suggest Retail Price?", value=True)
    
    if use_suggested:
        optimization_strategy = st.radio(
            "Optimization Goal:",
            ["Balanced (GM & CM)", "Contribution Margin Only"],
            horizontal=False
        )
        
        target_gm_percent = 50.0 
        target_cm_percent = 25.0 
        
        if optimization_strategy == "Contribution Margin Only":
            target_cm_percent = st.number_input(
                "Target Contribution Margin (%)", 
                value=25.0,
                step=1.0,
                format="%.1f"
            )

        # Logic 1: Find min Retail for GM > target (50%)
        # GM% = (Wholesale - COGS) / Wholesale > target_gm_percent
        gm_denom = 1.0 - (target_gm_percent / 100.0)
        min_retail_gm = (total_cogs / gm_denom) * 2
        
        # Logic 2: Find min Retail for CM > target (25% or user defined)
        # Wholesale > COGS / (1 - target - Var%)
        cm_denom = (1.0 - (target_cm_percent / 100.0)) - total_var_expense_pct
        
        if cm_denom <= 0:
            min_retail_cm = 999.00 
        else:
            min_retail_cm = (total_cogs / cm_denom) * 2
        
        # Determine Target based on selection
        if optimization_strategy == "Contribution Margin Only":
            # Only care about User's CM target (ignore GM status)
            target_retail = min_retail_cm
            help_text = f"Optimized for CM > {target_cm_percent}% only (rounded to nearest $0.05)"
        else:
            # Must satisfy BOTH standard targets (GM > 50% and CM > 25%)
            target_retail = max(min_retail_gm, min_retail_cm)
            help_text = f"Calculated to ensure GM > {target_gm_percent}% AND CM > {target_cm_percent}% (rounded to nearest $0.05)"
            
        suggested_retail = math.ceil(target_retail / 0.05) * 0.05
        
        retail_price = st.number_input(
            "Suggested Retail Price ($)", 
            value=float(round(suggested_retail, 2)), 
            disabled=True,
            help=help_text
        )
    else:
        # Standard manual input
        retail_price = st.number_input("Retail Price ($)", value=36.00)

# --- 6. FINAL MARGIN MATH ---

wholesale_price = retail_price / 2
total_wholesale_revenue = wholesale_price * units

gross_margin_dollar = wholesale_price - total_cogs
gross_margin_percent = (gross_margin_dollar / wholesale_price) * 100

var_expenses_dollar = wholesale_price * total_var_expense_pct
contribution_margin_dollar = gross_margin_dollar - var_expenses_dollar
contribution_margin_percent = (contribution_margin_dollar / wholesale_price) * 100

# --- 7. DISPLAY RESULTS ---

st.header("Results Summary")

gm_color = get_margin_color_style(gross_margin_percent, is_gross=True)
cm_color = get_margin_color_style(contribution_margin_percent, is_gross=False)

# Using 4 columns to include Total Wholesale Price
col_res1, col_res2, col_res3, col_res4 = st.columns(4)

col_res1.markdown(f"""
    <div style="text-align: left;">
        <p style="font-size: 14px; margin-bottom: 5px; opacity: 0.8;">Unit Wholesale Price<br>(50% Retail)</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0px; line-height: 1.1;">
            ${wholesale_price:,.2f}
        </p>
    </div>
""", unsafe_allow_html=True)

col_res2.markdown(f"""
    <div style="text-align: left;">
        <p style="font-size: 14px; margin-bottom: 5px; opacity: 0.8;">Total Wholesale<br>Price</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0px; line-height: 1.1;">
            ${total_wholesale_revenue:,.2f}
        </p>
    </div>
""", unsafe_allow_html=True)

col_res3.markdown(f"""
    <div style="text-align: left;">
        <p style="font-size: 14px; margin-bottom: 5px; opacity: 0.8;">Gross Margin<br>($)</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0px; line-height: 1.1;">
            ${gross_margin_dollar:,.2f} 
            <span style="color: {gm_color}; font-size: 20px; display: block;">{gross_margin_percent:.1f}%</span>
        </p>
    </div>
""", unsafe_allow_html=True)

col_res4.markdown(f"""
    <div style="text-align: left;">
        <p style="font-size: 14px; margin-bottom: 5px; opacity: 0.8;">Contrib. Margin<br>($)</p>
        <p style="font-size: 32px; font-weight: bold; margin: 0px; line-height: 1.1;">
            ${contribution_margin_dollar:,.2f} 
            <span style="color: {cm_color}; font-size: 20px; display: block;">{contribution_margin_percent:.1f}%</span>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- 8. SCENARIO ANALYSIS (MOVED UP) ---
st.subheader("Scenario Analysis: CM% Pricing Tiers")

scenario_cms = [25, 20, 15, 10, 5]
scenario_data = []

for cm_target in scenario_cms:
    # Logic: Wholesale > COGS / (1 - target_cm - Var%)
    denom = (1.0 - (cm_target / 100.0)) - total_var_expense_pct
    
    if denom <= 0:
        rec_wholesale = 0.0
        rec_total = 0.0
    else:
        # Calculate raw wholesale needed
        raw_wholesale = total_cogs / denom
        
        # Round up to next $0.05 logic (applied via retail rounding to be consistent)
        raw_retail = raw_wholesale * 2
        rounded_retail = math.ceil(raw_retail / 0.05) * 0.05
        rec_wholesale = rounded_retail / 2
        
        rec_total = rec_wholesale * units
    
    scenario_data.append({
        "CM Goal": f"{cm_target}%",
        "Rec. Unit Wholesale": rec_wholesale,
        "Rec. Total Wholesale": rec_total
    })

df_scenarios = pd.DataFrame(scenario_data)

st.dataframe(
    df_scenarios.style.format({
        "Rec. Unit Wholesale": "${:,.2f}",
        "Rec. Total Wholesale": "${:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("<br>", unsafe_allow_html=True)

# --- 9. VISUAL BREAKDOWN (MOVED DOWN) ---
st.subheader("Visual Breakdown: Where is the money going?")

# Prepare Data for Chart
chart_data = pd.DataFrame({
    "Cost Component": ["Blank Garment", "Print & Finish", "Royalties & Comm.", "Net Margin"],
    "Value": [
        blank_price, 
        (final_print_cost_per_unit + vas_cost + fleece_charge), # Grouping Print/VAS/Fleece
        var_expenses_dollar,
        contribution_margin_dollar
    ]
})

# Create Donut Chart
fig = px.pie(
    chart_data, 
    values="Value", 
    names="Cost Component", 
    hole=0.4, # Makes it a Donut
    color_discrete_sequence=px.colors.qualitative.Pastel # Nice colors
)
fig.update_traces(textinfo='percent+label') # Show labels clearly
fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0)) # Compact layout

col_chart, col_spacer = st.columns([1, 1]) # Keep chart from being too huge
with col_chart:
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 10. COST BREAKDOWN ---
st.subheader("Cost Breakdown Table")

data = {
    "Line Item": ["Price Charging", "Print Cost (with 12% disc)", "Blank Price", "VAS", "Fleece Charge", "TOTAL COGS"],
    "Per Unit": [wholesale_price, final_print_cost_per_unit, blank_price, vas_cost, fleece_charge, total_cogs],
    "Total Run": [wholesale_price * units, discounted_print_run_cost, blank_price * units, vas_cost * units, fleece_charge * units, total_cogs * units]
}
df = pd.DataFrame(data)

st.dataframe(
    df.style.format({"Per Unit": "${:.2f}", "Total Run": "${:,.2f}"}), 
    use_container_width=True,
    hide_index=True
)

with st.expander("Show detailed breakdown"):
    st.write(f"**Total Screen Fees:** ${total_screen_fees:.2f}")
    st.write(f"**Total Flash Fee:** ${total_flash:.2f}")
    st.write(f"**Pre-Discount Print Per Unit Cost:** ${raw_print_cost_per_unit:.2f}")
    st.write(f"**Quantity:** {units}")
    st.write(f"**Pre-Discount Print Total:** ${gross_print_run_cost:.2f}")
    st.write(f"**Discount Applied:** 12% (-${gross_print_run_cost - discounted_print_run_cost:.2f})")
