import streamlit as st
import pandas as pd
from engine_1v1 import run_analysis

st.set_page_config(page_title="1-v-1 Draft Explorer", layout="wide")
st.title("Warzone 1 v 1 ABBA Draft Explorer")

with st.sidebar:
    st.header("Parameters")
    max_pick = st.slider("Number of territories considered", 3, 12, 8)
    pref_len = st.slider("Prefix length", 1, max_pick, 4)
    inc_txt  = st.text_input("Included (ours)", "")
    exc_txt  = st.text_input("Excluded (lost)", "")

def to_int_list(txt):
    return [int(t) for t in txt.split(",") if t.strip().isdigit()]

included = to_int_list(inc_txt)
excluded = to_int_list(exc_txt)

# ---------- run ----------
header, rows = run_analysis(max_pick, included, excluded, pref_len)
st.markdown(f"### {header}")

if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
else:
    st.warning("No sequences with these filters.")
