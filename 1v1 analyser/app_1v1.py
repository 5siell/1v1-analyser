import streamlit as st
import pandas as pd
from engine_1v1 import run_analysis

st.set_page_config(page_title="1-v-1 Draft Explorer", layout="wide")
st.title("Warzone 1-v-1 ABBA Draft Explorer")

# ---------- sidebar ----------
with st.sidebar:
    st.header("Parameters")
    max_pick  = st.slider("Total territories in preference list", 3, 12, 8)
    prefix_k  = st.slider("Prefix length (k)", 1, max_pick, 4)
    inc_txt   = st.text_input("Included (comma-sep)", "")
    exc_txt   = st.text_input("Excluded (comma-sep)", "")

def to_int_list(t):
    return [int(x) for x in t.split(",") if x.strip().isdigit()]

included = to_int_list(inc_txt)
excluded = to_int_list(exc_txt)

# ---------- run engine ----------
header, rows = run_analysis(max_pick, included, excluded, prefix_k)
st.markdown(f"### {header}")

if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
else:
    st.info("No sequences match these filters.")