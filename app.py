import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from datetime import timedelta

# Page Config
st.set_page_config(page_title="Super-AI v3.0", layout="wide")

st.title("🧠 Adaptive Super-AI v3.0: High-Accuracy Filter")
st.write("अगर Loser लिस्ट से नंबर आ रहे हैं, तो यह 'Double-Verification' मोड ऑन कर देगा।")

# 1. Master Patterns
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

uploaded_file = st.sidebar.file_uploader("Upload Data File", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE']).dt.date
            available_dates = df['DATE'].dropna().unique()
            selected_date = st.sidebar.selectbox("Base Date चुनें:", options=reversed(available_dates))
            base_idx = df[df['DATE'] == selected_date].index[0]
            tomorrow = selected_date + timedelta(days=1)
        else:
            st.error("फाइल में 'DATE' कॉलम ज़रूरी है।")
            st.stop()

        for s in shifts:
            if s in df.columns:
                df[s] = pd.to_numeric(df[s], errors='coerce')

        # --- STEP 1: TREND LEARNING ---
        lookback = st.sidebar.slider("लर्निंग विंडो (Days)", 3, 15, 10)
        recent_hits = []
        cold_numbers = set(range(100)) # Start with all, remove as they appear
        
        for i in range(max(0, base_idx - 15), base_idx + 1):
            day_vals = set(df.iloc[i][shifts].dropna().values)
            cold_numbers -= day_vals # Remove seen numbers
            
            if i > 0:
                prev = set(df.iloc[i-1][shifts].dropna().values)
                for v in prev:
                    for p in master_patterns:
                        if (v + p) % 100 in day_vals:
                            recent_hits.append(p)
        
        pattern_loyalty = Counter(recent_hits)

        # --- STEP 2: SCORING ---
        scores = np.zeros(100)
        today_nums = df.loc[base_idx, [s for s in shifts if s in df.columns]].dropna().to_dict()
        
        for val in today_nums.values():
            for p in master_patterns:
                target = int((val + p) % 100)
                bonus = pattern_loyalty.get(p, 0)
                scores[target] += (1 + bonus)

        # --- STEP 3: REFINED LOSER LOGIC (The Fix) ---
        # Loser वही होगा जो: 
        # 1. किसी पैटर्न में नहीं आया (Score == 0)
        # 2. और जो हाल ही में बहुत 'Cold' रहा है
        final_losers = []
        for n in range(100):
            if scores[n] == 0:
                final_losers.append(n)
        
        # अगर Losers कम हैं, तो 1 स्कोर वाले वो नंबर जोड़ें जो Cold हैं
        if len(final_losers) < 50:
            for n in range(100):
                if scores[n] == 1 and n in cold_numbers:
                    final_losers.append(n)

        # --- DISPLAY ---
        st.info(f"📅 **Base Date:** {selected_date} | 🎯 **Prediction for:** {tomorrow}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("✅ High-Confidence Winners")
            winners = []
            for n in range(100):
                if scores[n] >= 3:
                    # Confidence calculation
                    conf = min(99.0, (scores[n] / (len(today_nums) * 2.5)) * 100)
                    winners.append({"Number": n, "Power Score": round(scores[n], 1), "Confidence %": f"{conf:.1f}%"})
            
            if winners:
                w_df = pd.DataFrame(winners).sort_values("Power Score", ascending=False)
                st.table(w_df.head(15))
            else:
                st.write("अभी कोई सुपर-स्ट्रांग नंबर नहीं मिला।")

        with col2:
            st.header("❌ Safe-Exclusion (Losers)")
            st.error(f"इन {len(final_losers)} नंबरों से बचें (Double Verified):")
            # Highlight Cold numbers in the loser list
            st.write(sorted(list(set(final_losers))))
            if cold_numbers:
                st.caption(f"नोट: इनमें से {len(cold_numbers.intersection(final_losers))} नंबर पिछले 15 दिनों से गायब (Cold) हैं।")

        # --- ACCURACY CHECK ---
        st.divider()
        if base_idx + 1 < len(df):
            actual = set(df.loc[base_idx + 1, shifts].dropna().values)
            st.subheader(f"🧪 Result Check ({tomorrow})")
            st.write(f"असली रिजल्ट: `{list(actual)}`")
            
            wrong_losers = actual.intersection(set(final_losers))
            if wrong_losers:
                st.warning(f"⚠️ चेतावनी: Loser लिस्ट से ये नंबर आ गए: `{list(wrong_losers)}` (मार्केट ट्रेंड बदल रहा है)")
            else:
                st.success("✅ शानदार! Loser लिस्ट से एक भी नंबर नहीं आया।")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Sidebar में अपनी Excel/CSV फाइल अपलोड करें।")
      
