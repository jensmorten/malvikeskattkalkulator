#!/usr/bin/env python3
import csv

CSV_FILE = "skatteliste_clean_bunn.csv"
EXPECTED_COLS = 9
COLNAMES = ["Adresse","Eiendom","Takst","Skattenivå","Bunnfradrag","Grunnlag","Promillesats","Skatt","Fritak"]

def is_float(s):
    try:
        float(s)
        return True
    except:
        return False

bad_struct = []
bad_values = []
total = 0

with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader, start=1):
        total += 1

        # sjekk struktur
        if len(row) != EXPECTED_COLS:
            bad_struct.append((i, row))
            continue

        # sjekk tallverdier
        d = dict(zip(COLNAMES, row))
        for col in ["Takst","Skattenivå","Bunnfradrag","Grunnlag","Promillesats","Skatt"]:
            if d[col].strip() == "":
                continue
            if not is_float(d[col]):
                bad_values.append((i, col, d[col], row))

print("\n--- RESULTAT ---\n")
print(f"* Totale linjer: {total}")
print(f"* Linjer med feil kolonnar: {len(bad_struct)}")
print(f"* Linjer med ugyldige tall: {len(bad_values)}")

if bad_struct[:10]:
    print("\n--- Første 10 linjer med feil kolonnar ---")
    for i, r in bad_struct[:10]:
        print(f"Linje {i}: {r}")

if bad_values[:10]:
    print("\n--- Første 10 linjer med ugyldige tall ---")
    for i, col, val, r in bad_values[:10]:
        print(f"Linje {i}: kolonne '{col}' inneheld '{val}' → {r}")

print("\n--- Ferdig ---")
