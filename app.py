import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

st.set_page_config(page_title="Eigedomsskatt i Malvik", layout="wide")
st.title("🏠 Eigedomsskatt i Malvik kommune")

# --- Budsjettår og datagrunnlag (oppdater her kvart år) ---
BUDSJETTAAR = 2027
DATAAAR = 2026  # skattelista frå offentleg ettersyn som er brukt som grunnlag
KD_FORSLAG_MILL = 35.3  # kommunedirektørens anslag for eigedomsskatt i budsjettforslaget
KD_URL = "https://pub.framsikt.net/2027/malvik/bm-2027-hp27#/generic/summary/budsum"
MINSTESKATT = 300  # skatt under dette blir ikkje kravd inn

# --- Les data ---
URL = "https://raw.githubusercontent.com/jensmorten/malvikeskattkalkulator/refs/heads/main/data/2026/skatteliste_renset2.csv"

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
<b></b> {len(df)} rader med data frå skattelista for {DATAAAR} (offentleg ettersyn i Malvik kommune) er lasta.
Lista er grunnlaget for utrekninga for {BUDSJETTAAR}.
</div>
""",
    unsafe_allow_html=True
)
# --- Tvungen tallkonvertering ---
for col in ["Takst", "Skattenivå", "Bunnfradrag", "Grunnlag", "Promillesats", "Skatt", 'faktor']:
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
# Alle rader, også dei med delvis fritak (§ 5 h): dei følgjer same formel,
# og utrekninga under brukar dei same radene. Lista viser utrekna skatt også
# under MINSTESKATT, men den blir ikkje kravd inn og er difor ikkje med.
total_skatt = df.loc[df["Skatt"] >= MINSTESKATT, "Skatt"].sum()

# Skattelista for DATAAAR summerer seg til litt mindre enn kommunedirektørens anslag
# for BUDSJETTAAR. Skilnaden kjem truleg frå nye eigedomar og endringar i lista,
# ikkje prisvekst: takstane ligg fast, og 1.027 (prisvekst 2027) ville gitt 36.1 mill.
# Totalane blir skalerte med denne faktoren (≈ 1.0045 for 2027), så kalkulatoren
# gir anslaget ved satsane i forslaget.
JUSTERING = KD_FORSLAG_MILL * 1_000_000 / total_skatt

kol_kd, kol_kalk = st.columns(2)

with kol_kd:
    st.subheader(f"💁‍♂️ Kommunedirektørens forslag ({BUDSJETTAAR})")
    st.metric(
        label="",
        value=f"{KD_FORSLAG_MILL} mill. kr"
    )
    st.markdown(f'<a href="{KD_URL}" target="_blank">Budsjettforslaget {BUDSJETTAAR}</a>', unsafe_allow_html=True)

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
STD_BUNN = 320000

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
    f"Promillesats for bolig (1.8‰ i forslag {BUDSJETTAAR})",
    min_value=0.0, max_value=4.0, step=0.1,
    key="bolig_sats"
)

st.sidebar.slider(
    f"Promillesats for næring (4.0‰ i forslag {BUDSJETTAAR})",
    min_value=0.0, max_value=7.0, step=0.1,
    key="naering_sats"
)

st.sidebar.slider(
    "Botnfrådrag (0–2 000 000)",
    min_value=0, max_value=2000000, step=10000,
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

# bolig: 1.8 ‰ → bruk bolig_sats
df.loc[df["Promillesats"] == 1.8, "Promillesats_ny"] = bolig_sats

# næring: 4.0 ‰ → bruk næring_sats
df.loc[df["Promillesats"] == 4.0, "Promillesats_ny"] = naering_sats

# Bunnfradrag i lista er alt summert over boeiningane (320 000 per sjølvstendig
# boeining), så talet på boeiningar er Bunnfradrag / 320 000. Nytt botnfrådrag
# gjeld per boeining, også for eigedomar med fleire boeiningar.
df["Boeiningar"] = (df["Bunnfradrag"] / STD_BUNN).round()
df["Bunnfradrag_ny"] = bunnfradrag_ny * df["Boeiningar"]

# 1. takst * skattenivå - bunnfradrag (gir Grunnlag i lista)
df["Beregningsgrunnlag"] = df["Takst"] * (df["Skattenivå"] / 100) - df["Bunnfradrag"]

# 2. trekk frå nytt bunnfradrag
df["Grunnlag_ny"] = df["Takst"] * (df["Skattenivå"] / 100) - df["Bunnfradrag_ny"]
df["Grunnlag_ny"] = df["Grunnlag_ny"].clip(lower=0)

# 3. ny promillesats (i promille → /1000)
df["Skatt_ny"] = df["Grunnlag_ny"] * (df["Promillesats_ny"] / 1000)

# 4. Rund ned til heile kroner, som i skattelista.
df["Skatt_ny"] = (
    np.floor(
        df["Skatt_ny"]
        .fillna(0)
        .replace([np.inf, -np.inf], 0)
        + 1e-6  # unngå at flyttal som 4644.9999999 blir runda ned ei krone
    )
    .astype(int)
)

# 5. Skatt under MINSTESKATT blir ikkje kravd inn (183 rader i lista for 2026).
df.loc[df["Skatt_ny"] < MINSTESKATT, "Skatt_ny"] = 0

# Med satsane i forslaget gir dette same skatt som lista for kvar rad som
# blir kravd inn (35 140 425 kr totalt). Totalen blir så skalert til budsjettanslaget.
total_skatt_ny = df["Skatt_ny"].sum() * JUSTERING

total_mill_ny = round(total_skatt_ny / 1_000_000,1)

with kol_kalk:
    st.subheader(f"🔮 Kalkulatorens berekna eigedomsskatt ({BUDSJETTAAR})")
    st.metric(
        label="",
        value=f"{total_mill_ny} mill. kr"
    )

text= "Basert på brukaren sine val for promillesats og botnfrådrag. "
if bolig_sats==1.8 and naering_sats==4.0 and bunnfradrag_ny==320000:
    text = text + f"Promillesats 1.8‰ og botnfrådrag 320 000 tilsvarar kommunedirektørens forslag for {BUDSJETTAAR} (uendra frå 2026)"
elif bolig_sats==2.9 and naering_sats==5.0 and bunnfradrag_ny==1200000:
    text = text + "Promillesats 2.9‰ og botnfrådrag 1 200 000 tilsvarar Raudts alternative budsjett for 2026"

st.caption(text)


# Ved satsane i forslaget er total_skatt_ny lik anslaget, så differansen er
# endringa mot forslaget. Avrundinga til 0.1 mill. kr gjer at endringar under
# 0.05 mill. kr blir vist som "inga endring".
inntekt_diff = total_skatt_ny / 1_000_000 - KD_FORSLAG_MILL

if round(inntekt_diff,1) > 0:
    tekst = f"📈 Den valde endringa i satsar gir auke i inntekter på **{inntekt_diff:.1f} millionar kr samanlikna med kommunedirektørens forslag for {BUDSJETTAAR}**."
elif round(inntekt_diff,1) < 0:
    tekst = f"📉 Den valde endringa i satsar gir kutt i inntekter på **{abs(inntekt_diff):.1f} millionar kr samanlikna med kommunedirektørens forslag for {BUDSJETTAAR}**."
else:
    tekst = "⚖️ Inga endring i inntektene."

st.markdown(f"### {tekst}")

st.caption(
    f"Skattelista for {DATAAAR} summerer seg til {total_skatt / 1_000_000:.1f} mill. kr (skatt under {MINSTESKATT} kr blir ikkje kravd inn). "
    f"For å treffe kommunedirektørens anslag for {BUDSJETTAAR} er totalane skalerte med {JUSTERING:.4f}, "
    f"som dekkjer nye eigedomar og endringar i lista. Tabellen under viser skatt per eigedom utan skalering."
)

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
    skatt = np.floor(grunnlag * (promille / 1000) + 1e-6)
    return skatt if skatt >= MINSTESKATT else 0

def to_mill(x):
    return f"{x/1_000_000:.1f} mill."


rows = []

for label, takst in [("Eigedom med låg takst (~nedre kvartil)", p25),
                     ("Eigedom med median takst (~0.5-persentil)", p50),
                     ("Eigedom med høg takst, (~øvre kvartil)", p75),
                     ("Eigedom med svært høg takst (~0.99-persentil)", p99)]:

    # dagens satser
    skatt_dagens = beregn_skatt(
        takst=takst,
        skattenivå=70,   # *antatt lik for alle*
        bunnfradrag=320000, # *typisk 0 eller 200k*
        promille=1.8    # blir ≈ 1.9
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
        f"Skatt (forslag {BUDSJETTAAR})": f"{skatt_dagens:,.0f} kr",
        "Skatt (kalkulator)":  f"{skatt_ny:,.0f} kr",
        "Mogleg endring per mnd":  f"{eom:,.0f} kr"
        })
    
    

st.subheader("📘 Kostnad for typiske eigedomar")

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


#df_sim_styled = (
#    df_sim
#    .style
#    # farge på endring
#    .applymap(farge_neg_pos, subset=["Mogleg endring per mnd"])
    # generelt utseende
    #.set_properties(**{
    #    "font-size": "26px",     # større skrift
    #    "padding": "10px",       # meir luft
    #    "text-align": "right"
    #})
    # fet og bakgrunn for header
    #.set_table_styles([
    #    {
    #        "selector": "th",
    #        "props": [
    #            ("background-color", "#f0f0f0"),
    #            ("font-weight", "bold"),
    #            ("font-size", "17px"),
    #            ("padding", "12px")
    #        ]
    #    }
    #])
#)

#st.dataframe(df_sim_styled, hide_index=True, use_container_width=False)
st.dataframe(df_sim, hide_index=True, use_container_width=False)


st.sidebar.markdown(f"""
<hr>
<p>
ℹ️ Dette er ein enkel kalkulator som reknar ut konsekvensen av å endre eigedomsskatten i Malvik kommune,
både for kommunebudsjettet og huseigarar. Eksperimenter med promillesats og botnfrådrag og sjå konsekvensen.
</p>
<p>
Kalkulatoren samanliknar med <a href="{KD_URL}">kommunedirektørens budsjettforslag for {BUDSJETTAAR}</a>,
som held fram med same satsar som i 2026. Skattelista for {BUDSJETTAAR} er ikkje lagt ut enno, så utrekninga
bruker skattelista for {DATAAAR} frå offentleg ettersyn i Malvik kommune.
</p>
<p>
<a href=" https://github.com/jensmorten/malvikeskattkalkulator/blob/main/README.md"> Validering av kalkulatoren </a> er utført ved samanlikning med berekningar kommunedirektøren publiserte for tidlegare år, med same utrekningsmetode.
Desse tala har inga direkte relevans for tala i år, men avvika gir ein generell peikepinn på kor nøyaktig kalkulatoren kan forventast å vere.
Totalane er skalerte med ein faktor ({JUSTERING:.4f}) slik at kalkulatoren treffer kommunedirektørens anslag for {BUDSJETTAAR} ved satsane i forslaget.
Brukaren må sjølv ta stilling til om avviket er akseptabelt for aktuell bruk.
</p>
<p>
Moglege feilkjelder som kan forklare avvik: utrekninga for {BUDSJETTAAR} byggjer på skattelista for {DATAAAR}, så nye eigedomar og endringar
i lista er berre med gjennom skaleringa. Eigedomar med delvis fritak er tekne med slik dei står i skattelista.
</p>
<p>
Ta gjerne kontakt med <a href="mailto:jens.morten.nilsen@gmail.com">jens.morten.nilsen@gmail.com</a> for spørsmål eller kommentarar.  
</p>
<p>
Utviklaren er kommunestyrerepresentant for Raudt i Malvik men vil undertreke at kalkulatoren kan brukast av alle, 
og den reknar like bra utansett som skatten går opp eller ned. 
</p>
""", unsafe_allow_html=True)