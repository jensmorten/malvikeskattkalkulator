import pandas as pd
import re 

input_path = "Kopi av Skatteliste Offentlig Ettersyn 2026 - ingen eller delvis fritak - datafil.xlsx"   # <-- din fil
output_path = "skatteliste_renset2.csv"

# --------- LES FIL ---------
xls = pd.ExcelFile(input_path)
df = pd.concat(
    [xls.parse(sheet, header=None) for sheet in xls.sheet_names],
    ignore_index=True
)

df = df.astype(str)

# --------- FILTRERING ---------
def is_page_footer(row):
    text = " ".join(row).lower()
    return bool(re.search(r"\d{2}\.\d{2}\.\d{4}.*side \d+ av \d+", text))

def is_noise(row):
    text = " ".join(row).lower()
    keywords = ["skatteliste", "offentlig ettersyn"]
    return any(k in text for k in keywords)

def is_empty(row):
    return sum(cell.strip() not in ["", "nan"] for cell in row) <= 1

mask = []
for _, row in df.iterrows():
    r = row.tolist()
    if is_page_footer(r) or is_noise(r) or is_empty(r):
        mask.append(False)
    else:
        mask.append(True)

df = df[mask].copy()

# --------- RENS TEKST ---------
df.replace("nan", "", inplace=True)
df = df.applymap(lambda x: x.strip())

# --------- BEHALD RELEVANTE KOLONNER ---------
df = df.iloc[:, :10]

df.columns = [
    "Adresse",
    "tom_kolonne",   # skal fjernast
    "Eiendom",
    "Takst",
    "Skattenivå",
    "Bunnfradrag",
    "Grunnlag",
    "Promillesats",
    "Skatt",
    "Fritak"
]

# --------- FJERN TOM KOLONNE ---------
df = df.drop(columns=["tom_kolonne"])

# --------- FJERN HEADER-RADER SOM HAR SNEKET SEG INN ---------
def is_fake_header(row):
    return (
        str(row["Adresse"]).strip().lower() == "adresse" or
        str(row["Eiendom"]).strip().lower() == "eiendom"
    )

df = df[~df.apply(is_fake_header, axis=1)]

# --------- BEHALD KUN GYLDIGE EIENDOMMER ---------
df = df[df["Eiendom"].str.match(r"\d+/\d+/\d+/\d+", na=False)]

# --------- RENS FELT ---------

# Skattenivå: "70%" -> "70"
df["Skattenivå"] = df["Skattenivå"].str.replace("%", "", regex=False)

# Promillesats: "1,8‰" -> "1.8"
df["Promillesats"] = (
    df["Promillesats"]
    .str.replace("‰", "", regex=False)
    .str.replace(",", ".", regex=False)
)

# Funksjon for å rense tal (fjerne tusenskilletegn)
def clean_number(col):
    return (
        col.str.replace(",", "", regex=False)
           .str.replace(" ", "", regex=False)
    )

for col in ["Takst", "Bunnfradrag", "Grunnlag", "Skatt"]:
    df[col] = clean_number(df[col])



# --------- KONVERTER TIL TAL ---------
numeric_cols = [
    "Takst",
    "Skattenivå",
    "Bunnfradrag",
    "Grunnlag",
    "Promillesats",
    "Skatt",
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

##faktor
df['faktor']=(df['Bunnfradrag']/320000).clip(lower=1)

# --------- (VALFRITT) SPLITT EIENDOM ---------
# gnr/bnr/fnr/snr
#df[["Gnr", "Bnr", "Fnr", "Snr"]] = df["Eiendom"].str.split("/", expand=True)

# konverter til tal
#for col in ["Gnr", "Bnr", "Fnr", "Snr"]:
#    df[col] = pd.to_numeric(df[col], errors="coerce")

# --------- LAGRE ---------
df.to_csv(output_path, index=False)

print("Ferdig! 🎯")