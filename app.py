import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

st.set_page_config(page_title="Eigendomssatt i Malvik", layout="wide")
st.title("🏠 Eigendomssatt i Malvik")

# --- Les data ---
URL = "https://raw.githubusercontent.com/jensmorten/malvikeskattkalkulator/refs/heads/main/data/skatteliste_clean_bunn.csv"

def load_data(url):
    return pd.read_csv(
        url,
        dtype=str,
        sep=",",
        engine="python",      # MER ROBUST
        on_bad_lines="skip",  # HOPP OVER TOMME/STØY-LINJER
        encoding="utf-8-sig"  # TAR HÅND OM BOM-FILER
    )

df=load_data(URL)

st.markdown(
    f"""
<div style="padding: 0.6em; border-radius: 5px; background-color: #e6ffed; border-left: 4px solid #00cc44;">
<b></b> ({len(df)} rader med data) frå Malvik kommune (2025), kjelde:
<a href="https://www.malvik.kommune.no/nyhet/offentlig-ettersyn-eiendomsskatt-2025" target="_blank">
Malvik kommune
</a>
</div>
""",
    unsafe_allow_html=True
)
# --- Tvungen tallkonvertering ---
for col in ["Takst", "Skattenivå", "Bunnfradrag", "Grunnlag", "Promillesats", "Skatt"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(" ", "")
        .str.replace(",", ".")
        .str.extract(r"([0-9\.]+)")        # hent kun tall og punktum
        .fillna("0")
        .astype(float)
    )
# --- Total skatt ---
df["Fritak"] = df["Fritak"].astype(str).str.strip().str.lower()

df_utan_fritak = df[df["Fritak"] == "ingen"]

total_skatt_utan_fritak = df_utan_fritak["Skatt"].sum()

st.subheader("💰 Total eigedomsskatt (2025)")

total_mill = round(total_skatt_utan_fritak / 1_000_000)
st.metric(
    "Total skatt etter justering",
    f"{total_mill} mill. kr"
)

# ============================
#      SIDEBAR START
# ============================

st.sidebar.header("⚙️ Justering av satsar")

# --- Rødt sine foreslåtte verdier ---
RODT_BOLIG = 2.9
RODT_NAERING = 5.0
RODT_BUNN = 1200000

# --- Standard når av ---
STD_BOLIG = 1.8
STD_NAERING = 4.0
STD_BUNN = 200000

# --- Init session states ---
if "rodt_modus" not in st.session_state:
    st.session_state.rodt_modus = False

if "bolig_sats" not in st.session_state:
    st.session_state.bolig_sats = STD_BOLIG

if "naering_sats" not in st.session_state:
    st.session_state.naering_sats = STD_NAERING

if "bunnfradrag_ny" not in st.session_state:
    st.session_state.bunnfradrag_ny = STD_BUNN


# ---- ON-CLICK FUNKSJON ----
def toggle_rodt_modus():
    st.session_state.rodt_modus = not st.session_state.rodt_modus
    if st.session_state.rodt_modus:
        st.session_state.bolig_sats = RODT_BOLIG
        st.session_state.naering_sats = RODT_NAERING
        st.session_state.bunnfradrag_ny = RODT_BUNN
    else:
        st.session_state.bolig_sats = STD_BOLIG
        st.session_state.naering_sats = STD_NAERING
        st.session_state.bunnfradrag_ny = STD_BUNN


# --- Bestem knappens stil + tekst ---
aktiv = st.session_state.rodt_modus
btn_color = "#cc0000" if not aktiv else "#888888"
btn_text = "🔴 Sett i Raudt-modus" if not aktiv else "⚪ Slå av Raudt-modus"

# --- CSS for knappen ---
st.sidebar.markdown(f"""
<style>
.rodt-btn > button {{
    background-color: {btn_color} !important;
    color: white !important;
    font-weight: bold;
    border-radius: 5px;
    height: 3em;
    width: 100%;
}}
</style>
""", unsafe_allow_html=True)


# --- KNAPP MED on_click (løser alt) ---
with st.sidebar:
    st.button(
        btn_text,
        key="rodt_button",
        on_click=toggle_rodt_modus
    )

# -----------------------------------
# Sliderne (alltid synlige)
# -----------------------------------
st.sidebar.slider(
    "Promillesats for bolig (1.9‰ i 2025)",
    min_value=0.0, max_value=4.0, step=0.1,
    key="bolig_sats"
)

st.sidebar.slider(
    "Promillesats for næring (4.0‰ i 2025)",
    min_value=0.0, max_value=7.0, step=0.1,
    key="naering_sats"
)

st.sidebar.slider(
    "Botnfrådrag (0–2 000 000)",
    min_value=0, max_value=2000000, step=100000,
    key="bunnfradrag_ny"
)

# ============================
#     OVERFØR SLIDER-VERDIAR
# ============================

bolig_sats = st.session_state.bolig_sats
naering_sats = st.session_state.naering_sats
bunnfradrag_ny = st.session_state.bunnfradrag_ny


# --- Ny promillesats basert på type eiendom ---
df["Promillesats_ny"] = df["Promillesats"]  # start med dagens sats

# bolig: 1.9 ‰ → bruk bolig_sats
df.loc[df["Promillesats"] == 1.9, "Promillesats_ny"] = bolig_sats
df.loc[df["Bunnfradrag"] == 200000, "Bunnfradrag_ny"] = bunnfradrag_ny
df.loc[df["Bunnfradrag"] != 200000, "Bunnfradrag_ny"] = df["Bunnfradrag"] 

# næring: 4.0 ‰ → bruk næring_sats
df.loc[df["Promillesats"] == 4.0, "Promillesats_ny"] = naering_sats

# 1. takst * prosent
df["Beregningsgrunnlag"] = df["Takst"] * (df["Skattenivå"] / 100)- df['Bunnfradrag']

# 2. trekk frå nytt bunnfradrag
df["Grunnlag_ny"] = df["Takst"] * (df["Skattenivå"] / 100) - df["Bunnfradrag_ny"]
df["Grunnlag_ny"] = df["Grunnlag_ny"].clip(lower=0)

# 3. ny promillesats (i promille → /1000)
df["Skatt_ny"] = df["Grunnlag_ny"] * (df["Promillesats_ny"] / 1000)

# 4. minimum 300-regel
df.loc[df["Skatt_ny"] < 300, "Skatt_ny"] = 0

# 5. Rund av til nærmaste krone
df["Skatt_ny"] = (
    df["Skatt_ny"]
    .fillna(0)     # <- viktig
    .replace([np.inf, -np.inf], 0)
    .round(0)
    .astype(int)
)

total_skatt_ny = df["Skatt_ny"].sum()

st.subheader("🔮 Ny berekna eigedomsskatt (2026)")
total_mill = round(total_skatt_ny / 1_000_000)
st.metric(
    "Total skatt",
    f"{total_mill} mill. kr"
)

st.caption("Basert på brukaren sine val for promillesats og bunnfradrag.")

inntekt_diff = total_skatt_ny - total_skatt_utan_fritak
inntekt_diff_mill = round(inntekt_diff / 1_000_000)

if inntekt_diff_mill > 0:
    tekst = f"📈 Endring i satsar gir auke i inntekter på **{inntekt_diff_mill:.1f} millionar kr**."
elif inntekt_diff < 0:
    tekst = f"📉 Endring i satsar gir kutt i inntekter på **{abs(inntekt_diff_mill):.1f} millionar kr**."
else:
    tekst = "⚖️ Inga endring i inntektene."
    
st.markdown(f"### {tekst}")

#st.subheader("🔍 Debug – topp 10 etter skatt")

debug_cols = [
    "Adresse",
    "Eiendom",
    "Takst",
    "Skattenivå",
    "Bunnfradrag",
    "Grunnlag",
    "Promillesats",
    "Bunnfradrag_ny",
    "Skatt",
    "Promillesats_ny",
    "Beregningsgrunnlag",
    "Grunnlag_ny",
    "Skatt_ny",
]

#st.dataframe(
#    df.head(30)[debug_cols]
#)


p25 = 2500000 #df["Takst"].quantile(0.25)
p50 = 4000000 #df["Takst"].quantile(0.50)
p75 = 5500000 #df["Takst"].quantile(0.75)
p99 = 10000000 ###3df["Takst"].quantile(0.985)


def beregn_skatt(takst, skattenivå, bunnfradrag, promille):
    grunnlag = takst * (skattenivå / 100) - bunnfradrag
    grunnlag = max(grunnlag, 0)
    skatt = grunnlag * (promille / 1000)
    return 0 if skatt < 300 else skatt

def to_mill(x):
    return f"{x/1_000_000:.1f} mill."


rows = []

for label, takst in [("låg takst (~0.25-percentil)", p25),
                     ("median takst (~0.5-percentil)", p50),
                     ("høg takst, (~0.75-percentil)", p75),
                     ("svørt høg takst (~0.99-percentil)", p99)]:

    # dagens satser
    skatt_dagens = beregn_skatt(
        takst=takst,
        skattenivå=70,   # *antatt lik for alle*
        bunnfradrag=200000, # *typisk 0 eller 200k*
        promille=1.9    # blir ≈ 1.9
    )

    # nye satser (basert på sliderne)
    skatt_ny = beregn_skatt(
        takst=takst,
        skattenivå=70,
        bunnfradrag=bunnfradrag_ny,
        promille=bolig_sats  # persentil = bolig
    )

    eom=(skatt_ny-skatt_dagens)/12

    rows.append({
        "Takst-nivå": label,
        "Takst": f"{takst:,.0f} kr",
        "Skatt (dagens)": f"{skatt_dagens:,.0f} kr",
        "Skatt (ny)":  f"{skatt_ny:,.0f} kr",
        "Mogleg endring per mnd":  f"{eom:,.0f} kr"
        })
    
    

st.subheader("📘 Kostnad for typiske eigendomar")

df_sim = pd.DataFrame(rows)

def farge_neg_pos(val):
    try:
        clean = float(val.replace(" kr", "").replace(",", "").replace(" ", ""))
    except:
        return ""
    if clean < 0:
        return "background-color: #e6ffe6;"   # grøn
    elif clean > 0:
        return "background-color: #ffe6e6;"   # raud
    return ""


df_sim_styled = (
    df_sim
    .style
    # farge på endring
    .applymap(farge_neg_pos, subset=["Mogleg endring per mnd"])
    # generelt utseende
    .set_properties(**{
        "font-size": "16px",     # større skrift
        "padding": "10px",       # meir luft
        "text-align": "left"
    })
    # fet og bakgrunn for header
    .set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#f0f0f0"),
                ("font-weight", "bold"),
                ("font-size", "17px"),
                ("padding", "12px")
            ]
        }
    ])
)

st.dataframe(df_sim_styled, hide_index=True, use_container_width=True)


tiltak = {
    "Gratis folkebad": 240000,
    "Arbeidsklær til barnehage/SFO": 1700000,
    "Redusert kulturskolepris": 400000,
    "Halv husleie kommunale boliger": 200000,
    "Stoppe tvangssalg ved kommunale gebyrer": 100000
}

stillinger = {
    "Lærar": 787200,
    "Barnehagelærar": 787200,
    "Lektor": 880500,
    "Spesialpedagog": 880000,
    "Fagarbeidar": 705000,
    "Assistent": 605500,
    "Kjøkkenassistent (fagbrev)": 705000,
    "Kjøkkenassistent": 605500,
    "Sjukepleiar": 850000,
    "Hjelpepleiar": 750000,
}

if inntekt_diff_mill > 0:

    inntekt_diff_kr = inntekt_diff_mill * 1000000

    st.subheader("🧮 Kva kan kommunen gjere med denne inntektsauken?")
    st.write(f"Tilgjengelege midlar: **{inntekt_diff_kr:,.0f} kr**")

    # ----------------------
    # Tiltak som kan finansierast
    # ----------------------
    st.markdown("### 🟩 Tiltak som kan finansierast")

    remaining = inntekt_diff_kr
    rows_tiltak = []

    for namn, kostnad in tiltak.items():
        if kostnad == 0:
            kan = "ja (gratis)"
        elif kostnad <= remaining:
            kan = "ja"
            remaining -= kostnad
        else:
            kan = "nei"

        rows_tiltak.append({
        "Tiltak": namn,
        "Kostnad": f"{kostnad:,.0f} kr",
        "Kan gjennomførast": kan,
        "Gjenværende budsjett": f"{remaining:,.0f} kr"
        })


    st.dataframe(pd.DataFrame(rows_tiltak), hide_index=True)

    # ----------------------
    # Kor mange stillingar
    # ----------------------
    st.markdown("### 👩‍🏫 Kor mange stillingar kan opprettast?")

    rows_stilling = []
    for kategori, løn in stillinger.items():
        antal = inntekt_diff_kr / løn
        rows_stilling.append({
            "Stilling": kategori,
            "Årskostnad": f"{løn:,.0f} kr",
            "Tal mogleg årsverk": round(antal, 1)
        })

    st.dataframe(pd.DataFrame(rows_stilling), hide_index=True)

st.sidebar.markdown("""
<hr>
<p>
ℹ️ Dette er ein enkel kalkulator som reknar ut konsekvensen av å endre eigendomsskatten i Malvik kommune, 
både for kommunebudsjettet og huseigarar. Eksperimenter med promillesats og botnfrådrag og sjå konsekvensen. 
</p>
<p>
Kalkulatoren bruker data henta frå <a href="https://www.malvik.kommune.no/nyhet/offentlig-ettersyn-eiendomsskatt-2025">
offentleg ettersyn, eiendomsskatt 2025 i Malvik</a>. All data som er brukt ligg opent tilgjengeleg på nett. 
</p>
<p>
Moglege feilkjelder: data er henta inn frå eit PDF-dokument og konvertert til tabellformat og sjølv om manuell kontroll av data er 
utført kan slik metode gi enkelte feil. Vidare tar den forenkla kalkulatoren ikkje omsyn til "delvis fritak" for eigendomsskatt. 
</p>
<p>
Ta gjerne kontakt med <a href="mailto:jens.morten.nilsen@gmail.com">jens.morten.nilsen@gmail.com</a> for spørsmål eller kommentarar.  
</p>
<p>
Utviklaren er kommunestyrerepresentant for Raudt i Malvik men vil undertreke at kalkulatoren kan brukast av alle, 
og den reknar like bra utansett som skatten går opp eller ned. 
</p>
""", unsafe_allow_html=True)