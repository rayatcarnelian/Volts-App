import streamlit as st
import pandas as pd
import json
import os
from modules.engineering_specifier import MaterialSpecifier

def render_production_studio():
    st.set_page_config(layout="wide") if "layout" not in st.session_state else None
    
    st.title("⚡ Volts Lighting Calculation & Cost Studio")
    st.caption("Professional Lighting Mathematics, Asset Procurement & Analytics")
    
    # 1. Inputs
    st.header("1. Room Dimensions & Requirements")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        room_w = st.number_input("Room Width (ft)", min_value=5.0, value=20.0, step=1.0)
    with col2:
        room_d = st.number_input("Room Depth (ft)", min_value=5.0, value=16.0, step=1.0)
    with col3:
        target_lux = st.number_input("Target Illuminance (Lux)", min_value=100, max_value=2000, value=500, step=50)
    with col4:
        room_type = st.selectbox("Room Type", ["Office", "Retail", "Residential", "Industrial", "Warehouse"])

    area_sqft = room_w * room_d
    area_sqm = area_sqft * 0.092903
    
    st.info(f"📐 **Room Area:** {area_sqft:.1f} sq ft ({area_sqm:.1f} sq m)  |  💡 **Absolute Lumens Required (Est):** {(target_lux * area_sqm / 0.48):,.0f} lm")

    st.divider()

    # 2. Fixture Selection
    st.header("2. Fixture Selection & Schedule")
    
    fixture_db = {
        "Downlight (Standard)": {"lumens": 800, "watts": 10, "cost": 85.00},
        "Spotlight (Accent)": {"lumens": 1200, "watts": 15, "cost": 120.00},
        "Track Light (Retail)": {"lumens": 2000, "watts": 25, "cost": 280.00},
        "Pendant (Decorative)": {"lumens": 1500, "watts": 20, "cost": 150.00},
        "Wall Sconce (Hallway)": {"lumens": 600, "watts": 8, "cost": 95.00},
        "LED Strip (Ambient)": {"lumens": 400, "watts": 5, "cost": 45.00},
        "High Bay (Industrial)": {"lumens": 15000, "watts": 100, "cost": 350.00}
    }
    
    selected_fixture = st.selectbox("Select Primary Fixture", list(fixture_db.keys()))
    fixture_specs = fixture_db[selected_fixture]
    
    st.caption(f"**Fixture Specs:** {fixture_specs['lumens']} lm | {fixture_specs['watts']}W | ${fixture_specs['cost']:.2f} each")
    
    # Target Algorithm: (Target Lux * Area in M2) / (Light Lumens * CU * LLF)
    # Using industry standard CU=0.6, LLF=0.8 => Multiplier = 0.48
    recommended_qty = int(max(1, (target_lux * area_sqm / 0.48) / fixture_specs['lumens']))
    
    st.success(f"✨ **Algorithm Recommendation:** To achieve {target_lux} lux uniformly across the {room_type}, you will need approximately **{recommended_qty}x {selected_fixture}s**.")
    
    actual_qty = st.number_input(f"Quantity of {selected_fixture}s to Procure", min_value=1, value=recommended_qty, step=1)
    
    # Calculate results
    total_lumens = actual_qty * fixture_specs['lumens']
    total_watts = actual_qty * fixture_specs['watts']
    total_cost = actual_qty * fixture_specs['cost']
    estimated_lux = (total_lumens * 0.48) / area_sqm
    
    st.divider()

    # 3. Analytics & Calculations
    st.header("3. Project Analytics & Costs")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Estimated Illuminance", f"{estimated_lux:.0f} lx", f"{estimated_lux - target_lux:.0f} lx vs Target")
    with c2:
        st.metric("Total Lumens", f"{total_lumens:,} lm")
    with c3:
        # ASHRAE 90.1 limits (Watts/sq ft)
        ashrae_limits = {
            "Office": 0.79,
            "Retail": 1.06,
            "Residential": 0.60,
            "Industrial": 0.82,
            "Warehouse": 0.45
        }
        allowed_lpd = ashrae_limits.get(room_type, 0.79)
        actual_lpd = total_watts / area_sqft if area_sqft > 0 else 0
        lpd_delta = actual_lpd - allowed_lpd
        
        st.metric(
            "Lighting Power Density", 
            f"{actual_lpd:.2f} W/ft²", 
            f"{lpd_delta:.2f} W/ft² vs Code Limit", 
            delta_color="inverse"
        )
    with c4:
        st.metric("Total Fixture Cost", f"${total_cost:,.2f}")
        
    # --- ASHRAE 90.1 Compliance Gauge ---
    st.subheader("🏛️ Live ASHRAE 90.1 Code Compliance")
    if actual_lpd <= allowed_lpd:
        st.success(f"**PASS:** Your design consumes {actual_lpd:.2f} W/ft², which is strictly below the strict {room_type} legal limit of {allowed_lpd:.2f} W/ft².")
        # Progress bar
        try:
            st.progress(min(actual_lpd / allowed_lpd, 1.0))
        except:
            pass
    else:
        st.error(f"**FAIL — CODE VIOLATION:** Your design consumes {actual_lpd:.2f} W/ft², exceeding the strict {room_type} legal limit of {allowed_lpd:.2f} W/ft². You must select higher-efficiency fixtures or reduce counts.")
        try:
            st.progress(1.0) # Max out
        except:
            pass

    st.divider()

    # 4. Financial ROI & Payback Engine
    st.header("4. Financial ROI & Payback Engine")
    st.caption("Auto-calculate the capital payback period based on old fluorescent benchmarks to speed up sales pipelines.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        old_watts = st.number_input("Old System Total Wattage (W)", min_value=100, value=1500, step=100)
    with col2:
        elec_rate = st.number_input("Electricity Blended Rate ($/kWh)", min_value=0.01, value=0.15, step=0.01)
    with col3:
        op_hours = st.number_input("Average Daily Operating Hours", min_value=1, max_value=24, value=12, step=1)
        
    annual_days = 260 # Working days
    old_kwh = (old_watts / 1000.0) * op_hours * annual_days
    new_kwh = (total_watts / 1000.0) * op_hours * annual_days
    annual_savings = max((old_kwh - new_kwh) * elec_rate, 0)
    
    payback_years = total_cost / annual_savings if annual_savings > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Annual Legal Energy Savings", f"${annual_savings:,.2f}", f"{(old_kwh - new_kwh):,.0f} kWh Saved")
    c2.metric("New System Energy Load", f"{new_kwh:,.0f} kWh/yr")
    if payback_years > 0:
        c3.metric("Capital Payback Period", f"{payback_years:.1f} Years", "- Instant Cashflow" if payback_years < 2.0 else "Standard ROI")
    else:
        c3.metric("Capital Payback Period", "No Savings", "Negative ROI", delta_color="inverse")
    
    st.divider()

        
    # BoQ
    st.subheader("📋 Bill of Quantities (BoQ)")
    
    boq_df = pd.DataFrame([{
        "Asset / Fixture": selected_fixture,
        "Quantity": actual_qty,
        "Unit Price": f"${fixture_specs['cost']:.2f}",
        "Total Price": f"${total_cost:.2f}",
        "Total Power": f"{total_watts}W",
        "Total Output": f"{total_lumens} lm"
    }])
    
    st.table(boq_df)
    
    project_name = st.text_input("Project ID for Export", "VOLTS_CALC_001")
    if st.button("📊 Export Master Specification (.xlsx)", type="primary"):
        specifier = MaterialSpecifier()
        # Mocking individual items for the existing engineering_specifier logic
        items = [{"name": selected_fixture.split(" (")[0], "price": fixture_specs['cost']}] * actual_qty
        filepath = specifier.generate_boq(project_name, items)
        if filepath and os.path.exists(filepath):
            st.toast("Spec Generated Successfully!")
            with open(filepath, "rb") as f:
                st.download_button("⬇️ Download Excel Spec", data=f, 
                                 file_name=os.path.basename(filepath),
                                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    render_production_studio()
