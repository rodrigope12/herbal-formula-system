"""
Herbal Formula Generator UI - Custom MVP
Developed by: Rodrigo Perez Cordero (Physics Student & Python Developer)
Date: January 2026

Description:
Streamlit-based interface for managing patient profiles and generating 
optimized herbal blends with production-ready CSV output.
"""

import streamlit as st
import pandas as pd
import json
from herbal_engine import HerbalFormulator
import datetime

# --- Configuration ---
st.set_page_config(page_title="Herbal Formula System", layout="wide")
DB_PATH = "/Users/rodrigoperezcordero/Documents/TRABAJO/plants_db.json"

@st.cache_resource
def load_engine():
    return HerbalFormulator(DB_PATH)

engine = load_engine()

# --- Header ---
st.title("🌿 Personalized Herbal Formula Generator")
st.markdown("Generates custom tea blends based on clinical logic and safety rules.")

# --- Sidebar: Admin & Controls ---
with st.sidebar:
    st.header("Admin / Settings")
    if st.checkbox("Show Plant Database"):
        st.subheader("Current Plant Rules")
        df_plants = pd.DataFrame([vars(p) for p in engine.db])
        # Convert complex objects to string to avoid PyArrow serialization errors
        df_plants['constraints'] = df_plants['constraints'].astype(str)
        # Simplify view
        st.dataframe(df_plants[["name", "family", "role", "min_percent", "max_percent", "constraints"]])
    
    st.info("System Ready. Logic loaded from `plants_db.json`.")

# --- Main Form: Questionnaire (Simulated Categories) ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Patient Profile")
    name = st.text_input("Patient Name", "Guest User")
    
    st.subheader("Safety Filters")
    pregnancy = st.checkbox("Pregnancy / Lactation")
    medications = st.checkbox("Chronic Medication (Polypharmacy)")
    asteraceae = st.checkbox("Allergy to Asteraceae")
    
    st.subheader("Clinical Priorities (Axes)")
    st.caption("Rate conditions from 1 (None) to 10 (Severe)")
    
    anxiety = st.slider("Anxiety / Hyperactivation", 0, 10, 5)
    insomnia = st.slider("Insomnia / Difficulty Sleeping", 0, 10, 2)
    digestion = st.slider("Digestive Issues / Bloating", 0, 10, 4)
    fatigue = st.slider("Fatigue / Low Energy", 0, 10, 3)
    inflammation = st.slider("Pain / Inflammation", 0, 10, 2)
    immunity = st.slider("Low Immunity", 0, 10, 2)
    focus = st.slider("Brain Fog / Low Focus", 0, 10, 3)

# --- Logic Mapping ---
# Convert UI inputs to the "profile" dict expected by the engine
profile = {
    "priorities": [],
    "pregnancy": pregnancy,
    "medications": medications,
    "high_anxiety": (anxiety >= 7),
    "insomnia": (insomnia >= 6),
    "asteraceae_allergy": asteraceae
}

# Map sliders to engine 'priorities' strings
priorities_map = {
    "anxiety": anxiety,
    "sleep": insomnia,
    "digestion": digestion,
    "energy": fatigue,
    "inflammation": inflammation,
    "immunity": immunity,
    "focus": focus
}

# Add high scoring items to priorities list
sorted_priorities = sorted(priorities_map.items(), key=lambda x: x[1], reverse=True)
profile["priorities"] = [k for k, v in sorted_priorities if v >= 4]

with col2:
    st.header("2. Formula Generation")
    
    if st.button("Generate Formula", type="primary"):
        with st.spinner("Calculating scores and verifying safety..."):
            result = engine.generate_formula(profile)
            
            st.success("Formula Generated!")
            
            # Display Result
            components = result['components']
            total_g = result['total_grams']
            
            st.subheader(f"Custom Blend for {name}")
            st.markdown(f"**Total Dose per Infusion:** {total_g}g")
            
            # Create a nice table
            display_data = []
            for c in components:
                grams = (c['percent'] / 100) * total_g
                display_data.append({
                    "Plant": c['name'],
                    "Role": c['role'],
                    "Percentage": f"{c['percent']}%",
                    "Amount (g)": f"{grams:.2f}g"
                })
            
            st.table(display_data)
            
            # --- Phase 3: Production Output ---
            csv_data = pd.DataFrame(display_data).to_csv(index=False)
            
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            file_name = f"Formula_{name.replace(' ', '_')}_{date_str}.csv"
            
            st.download_button(
                label="📥 Download Production CSV",
                data=csv_data,
                file_name=file_name,
                mime="text/csv"
            )
            
            # Show Logic / Rationale (Bonus)
            with st.expander("See Clinical Rationale"):
                st.write(f"**Detected Priorities:** {', '.join(profile['priorities'])}")
                if profile['pregnancy']: st.warning("Applied Pregnancy Safety Filters")
                if profile['high_anxiety']: st.warning("Applied High Anxiety Filters (No Stimulants)")
                if profile['asteraceae_allergy']: st.warning("Applied Allergy Constraints")

