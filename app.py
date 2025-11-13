import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

st.set_page_config(page_title="Eiendomsskatt–statistikk", layout="wide")
st.title("🏠 Eiendomsskatt – statistikk (Malvik 2025)")

# --- Les data ---
URL = "https://raw.githubusercontent.com/jensmorten/malvikeskattkalkulator/c775305799ed70fd54d389948339248219360e85/data/skatteliste_clean_bunn.csv"

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

df = load_data(URL)

st.success(f"Data lasta frå GitHub ({len(df)} rader)")

# --- Kolonnar som skal analyserast ---
cols_to_analyze = ["Takst", "Bunnfradrag", "Grunnlag", "Promillesats", "Skatt"]

# Sikre at dei er float
for col in cols_to_analyze:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --- Sidebar-filter ---
st.sidebar.header("Filter")
min_takst, max_takst = int(df["Takst"].min()), int(df["Takst"].max())
takst_range = st.sidebar.slider(
    "Takst-intervall",
    min_value=min_takst,
    max_value=max_takst,
    value=(min_takst, max_takst)
)

df_filt = df[(df["Takst"] >= takst_range[0]) & (df["Takst"] <= takst_range[1])]

st.sidebar.write(f"Rader etter filter: **{len(df_filt)}**")

# --- Statistikk ---
st.subheader("📊 Statistisk oversikt (describe)")
st.dataframe(df_filt[cols_to_analyze].describe().round(2))

# --- Histogram ---
st.subheader("📈 Fordelingar")

for col in cols_to_analyze:
    st.markdown(f"### `{col}`")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(df_filt[col].dropna(), bins=20, edgecolor="black")
    ax.set_xlabel(col)
    ax.set_ylabel("Antall eigedomar")
    ax.grid(axis="y", alpha=0.3)
    st.pyplot(fig)

# --- Korrelasjon ---
st.subheader("🔗 Korrelasjonsmatrise")

corr = df_filt[cols_to_analyze].corr().round(2)
st.dataframe(corr.style.background_gradient(cmap="Blues"))

# Heatmap
fig, ax = plt.subplots(figsize=(5, 4))
im = ax.imshow(corr, cmap="Blues", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45, ha="right")
ax.set_yticks(range(len(corr.columns)))
ax.set_yticklabels(corr.columns)

for (i, j), val in np.ndenumerate(corr.values):
    ax.text(j, i, f"{val:.2f}", ha="center", va="center")

plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
st.pyplot(fig)

# --- Nedlasting ---
st.subheader("⬇️ Last ned filtrert data")
csv_buf = io.StringIO()
df_filt.to_csv(csv_buf, index=False)
st.download_button(
    "Last ned CSV",
    csv_buf.getvalue().encode("utf-8"),
    "skatteliste_filtered.csv",
    "text/csv"
)

st.caption("Kjelde: Malvik kommune – eigedomsskatteliste 2025")
