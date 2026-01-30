
import streamlit as st
import pandas as pd
import datetime
from herbal_engine import HerbalFormulator

# --- Configuration ---
st.set_page_config(
    page_title="Herbal Formula System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling (Apple-like Aesthetics) ---
st.markdown("""
<style>
    /* Global Typography */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1d1d1f;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 2.5rem; color: #1d1d1f; margin-bottom: 0.5rem; }
    h2 { font-size: 1.5rem; color: #1d1d1f; margin-top: 2rem; margin-bottom: 1rem; }
    h3 { font-size: 1.1rem; color: #86868b; font-weight: 500; }
    
    /* Input Fields */
    .stTextInput input {
        border-radius: 8px;
        padding: 10px 12px;
        border: 1px solid #d2d2d7;
    }
    
    /* Cards / Containers */
    .stCard {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        border: 1px solid #f5f5f7;
    }
    
    /* Primary Button */
    .stButton button {
        background-color: #0071e3;
        color: white;
        border-radius: 20px;
        padding: 8px 24px;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #0077ed;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- Initialization ---
DB_PATH = "/Users/rodrigoperezcordero/Documents/TRABAJO/plants_db.json"

@st.cache_resource
def load_engine():
    return HerbalFormulator(DB_PATH)

engine = load_engine()

# --- Helpers ---
def render_header():
    st.title("Herbal Formula System")
    st.markdown("<h3 style='margin-top: -15px;'>Clinical-Grade Botanical Formulation Engine</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #86868b; font-size: 0.9rem;'>Pharmacological Precision. Aesthetics of Apple.</p>", unsafe_allow_html=True)
    st.markdown("---")

def sidebar_admin():
    with st.sidebar:
        st.header("Settings")
        st.info(f"Engine Loaded: {len(engine.db)} Plants")
        
        if st.checkbox("View Plant Rules"):
             st.dataframe(pd.DataFrame([vars(p) for p in engine.db]))

# --- Main App ---
def main():
    render_header()
    sidebar_admin()

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.subheader("Patient Profile")
        with st.container():
            name = st.text_input("Full Name", placeholder="e.g. Jane Doe")
            
            st.write(" ") # Spacer
            st.markdown("**Clinical Filters**")
            
            # Use columns for compact toggles
            c1, c2 = st.columns(2)
            with c1:
                pregnancy = st.checkbox("Pregnancy / Lactation")
                medications = st.checkbox("Polypharmacy")
            with c2:
                asteraceae = st.checkbox("Allergy (Asteraceae)")
                gastritis = st.checkbox("Gastritis / Sensitive Stomach")

        st.write(" ")
        st.markdown("**Symptom Priorities (1-10)**")
        st.caption("Drag to indicate severity. Scores ≥ 7 trigger specific clinical protocols.")

        anxiety = st.slider("Anxiety & Stress", 0, 10, 5)
        insomnia = st.slider("Insomnia", 0, 10, 2)
        digestion = st.slider("Digestive Issues", 0, 10, 4)
        fatigue = st.slider("Fatigue / Low Energy", 0, 10, 3)
        inflammation = st.slider("Pain & Inflammation", 0, 10, 2)
        immunity = st.slider("Low Immunity", 0, 10, 2)
        focus = st.slider("Brain Fog / Focus", 0, 10, 3)

    # Prepare Profile
    profile_data = {
        "priorities": [],
        "conditions": {
            "pregnancy": pregnancy,
            "medications": medications, # General polypharmacy
            "medication_polypharmacy": medications,
            "asteraceae_allergy": asteraceae,
            "gastritis": gastritis,
            "high_anxiety": (anxiety >= 7),
            "insomnia": (insomnia >= 6), # Active insomnia condition
            "daytime_anxiety": (anxiety >= 5 and insomnia < 5) # Heuristic for daytime
        },
        "anxiety_level": anxiety,
        "insomnia_level": insomnia
    }
    
    # Map map priorities
    prio_map = {
        "anxiety": anxiety, "sleep": insomnia, "digestion": digestion,
        "energy": fatigue, "inflammation": inflammation, "immunity": immunity, 
        "focus": focus, "memory": focus, "stress": anxiety, "bloating": digestion
    }
    
    # Strictly order priorities
    sorted_prio = sorted(prio_map.items(), key=lambda x: x[1], reverse=True)
    profile_data["priorities"] = [k for k, v in sorted_prio if v >= 4]

    with col2:
        st.subheader("Formula Generation")
        
        st.markdown("""
        <div style='background-color: #f5f5f7; padding: 15px; border-radius: 10px; margin-bottom: 20px; font-size: 0.9em; color: #555;'>
            <strong>System Status:</strong> Ready to process constraints.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Precision Blend", type="primary", use_container_width=True):
            if not profile_data["priorities"]:
                st.error("Please select at least one priority condition (Score ≥ 4).")
            else:
                with st.spinner("Analyzing constraints, safety caps, and synergistic roles..."):
                    result = engine.generate_formula(profile_data)
                    
                    components = result.get('components', [])
                    total_g = result.get('total_grams', 4.0)
                    
                    if not components:
                        st.warning("No suitable plants found matching strict safety criteria.")
                    else:
                        st.success(f"Formula optimized for {name}")
                        
                        # --- Results Card ---
                        st.markdown(f"### Total Dose: {total_g}g per infusion")
                        
                        # Dataframe for clean display
                        df = pd.DataFrame(components)
                        df_display = df[["role", "name", "percent", "grams", "reason"]].copy()
                        df_display.columns = ["Role", "Plant", "Percent (%)", "Dose (g)", "Notes"]
                        
                        # Format
                        df_display["Percent (%)"] = df_display["Percent (%)"].apply(lambda x: f"{x}%")
                        df_display["Dose (g)"] = df_display["Dose (g)"].apply(lambda x: f"{x}g")
                        
                        st.table(df_display)
                        
                        # --- Download ---
                        csv = df_display.to_csv(index=False)
                        filename = f"HerbalFormula_{name.replace(' ', '')}_{datetime.date.today()}.csv"
                        
                        st.download_button(
                            "Download Production CSV",
                            csv,
                            filename,
                            "text/csv",
                            key='download-csv'
                        )
                        
                        # --- Clinical Debug ---
                        with st.expander("View Clinical Logic Trace"):
                            st.write("**Active Constraints:**")
                            for k, v in profile_data["conditions"].items():
                                if v: st.markdown(f"- `{k}` : Active")
                            
                            st.write("**Priority Axis:**")
                            st.write(profile_data["priorities"])

if __name__ == "__main__":
    main()
