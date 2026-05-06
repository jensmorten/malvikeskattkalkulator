#!/usr/bin/env python3
import pdfplumber, re, csv

PDF = "skatteliste.pdf"          # <-- endre ved behov
OUT = "skatteliste_clean_bunn.csv"

MATRIKKEL = re.compile(r"\d+/\d+/\d+/\d+")
PCT = re.compile(r"\d+%")
PROM_RE = re.compile(r"(\d+[,\.]?\d*)\s*‰")  # fanger 1,9‰ eller 4‰
BIG_NUM = re.compile(r"\d[\d\s]+\d|\d+")     # stort tall (med eller uten mellomrom)

# Liste over vanlege bunnfradrag (må være utan mellomrom her)
KNOWN_BUNNS = ["0", "200000", "400000", "600000", "100000", "300000"]

def norm_digits(s):
    if s is None: return ""
    return re.sub(r"\D", "", s)

def norm_prom(s):
    if not s: return ""
    s = s.replace("‰", "").replace(",", ".")
    return re.sub(r"[^\d.]", "", s)

def find_first_big_before(text, stoppos):
    """Finn første big number i text[:stoppos] (frå venstre)."""
    m = BIG_NUM.search(text[:stoppos])
    return m.group(0) if m else ""

def find_first_big_after(text, startpos):
    m = BIG_NUM.search(text[startpos:])
    return (m.group(0), startpos + m.start()) if m else ("", -1)

def find_known_bunn(rest):
    """Finn known bunn i resten; return (bunn_str, start_idx, end_idx) eller (None,-1,-1)."""
    # match også med optional spaces: bygg variant regex
    for b in KNOWN_BUNNS:
        pat = re.compile(r"\b" + r"\s*".join(list(b)) + r"\b")
        m = pat.search(rest)
        if m:
            # return without spaces
            return (re.sub(r"\s+", "", m.group(0)), m.start(), m.end())
    # også prøv å finne bunn utan word-boundary (i tilfeller utan mellomrom)
    for b in KNOWN_BUNNS:
        idx = rest.replace(" ", "").find(b)
        if idx != -1:
            # need to map idx in collapsed string back to index in original rest
            # simplest: search for first occurrence of b in rest allowing optional spaces
            pat = re.compile("(" + "".join([c + r"\s*" for c in b]) + ")")
            m = pat.search(rest)
            if m:
                return (b, m.start(), m.end())
    return (None, -1, -1)

bad_lines = []
rows = []
cols = ["Adresse","Eiendom","Takst","Skattenivå","Bunnfradrag","Grunnlag","Promillesats","Skatt","Fritak"]

with pdfplumber.open(PDF) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        for line in text.split("\n"):
            m = MATRIKKEL.search(line)
            if not m:
                continue
            eiendom = m.group(0)
            adresse = line[:m.start()].strip().rstrip(",")
            rest = line[m.end():].strip()

            # finn skattenivå (NN%) i resten
            pct = PCT.search(rest)
            if not pct:
                # logg og hopp over
                bad_lines.append(("no_pct", line))
                rows.append([adresse, eiendom, "", "", "", "", "", "", ""])
                continue
            skniv = norm_digits(pct.group(0))
            skniv_end = pct.end()

            # takst: første big number innanfor starten av rest fram til pct.start()
            takst_raw = find_first_big_before(rest, pct.start())
            takst = norm_digits(takst_raw)

            # no finn vi bunnfradrag ved hjelp av kjente verdiar
            after_pct = rest[pct.end():].lstrip()
            bunn_val, bstart, bend = find_known_bunn(after_pct)

            if bunn_val is not None:
                # dersom bunn funne, sjå om bunn og grunn er klemt saman utan mellomrom
                # substring frå bend og framover kan byrje utan mellomrom med grunn
                # ta alt etter bend inntil promille som kandidatt for grunn
                part_after_bunn = after_pct[bend:].lstrip()
                # finn promille i dette substringet
                prom_m = PROM_RE.search(part_after_bunn)
                if prom_m:
                    # grunn er alt frå start av part_after_bunn fram til promilles start
                    grund_candidate = part_after_bunn[:prom_m.start()].strip()
                    # remove spaces and non-digits
                    grunn = norm_digits(grund_candidate)
                    prom = norm_prom(prom_m.group(1))
                    # skatt er tal etter promille
                    post_prom = part_after_bunn[prom_m.end():].strip()
                    skatt_match = BIG_NUM.search(post_prom)
                    skatt = norm_digits(skatt_match.group(0)) if skatt_match else ""
                    # fritak er resten etter skatt
                    if skatt_match:
                        fritak = post_prom[skatt_match.end():].strip().strip(",")
                    else:
                        fritak = post_prom.strip().strip(",")
                    bunn = norm_digits(bunn_val)
                    rows.append([adresse, eiendom, takst, skniv, bunn, grunn, prom, skatt, fritak])
                    continue
                else:
                    # om ingen promille funne, fallback - logg
                    bad_lines.append(("no_prom_after_bunn", line))
                    rows.append([adresse, eiendom, takst, skniv, bunn_val, "", "", "", ""])
                    continue
            else:
                # ingen kjent bunnfunne — fallback: finn neste to store tal etter pct
                # collapse spaces to help
                after = after_pct
                # finn to først store tal i after
                numbers = re.findall(r"\d[\d\s]+\d|\d+", after)
                if len(numbers) >= 3:
                    # forvent: bunn, grunn, prom/skatt...
                    bunn = norm_digits(numbers[0])
                    grunn = norm_digits(numbers[1])
                    # prom kan vere like etter grunn i original substring (sjekk PROM_RE)
                    prom_search = PROM_RE.search(after)
                    prom = norm_prom(prom_search.group(1)) if prom_search else ""
                    # skatt: ta første number som ligger etter prom (eller numbers[2])
                    skatt = norm_digits(numbers[2])
                    # fritak: rest after the third number and/or prom
                    # crude attempt:
                    rest_after_third = after.split(numbers[2],1)[1] if numbers[2] in after else ""
                    fritak = rest_after_third.strip().strip(",")
                    rows.append([adresse, eiendom, takst, skniv, bunn, grunn, prom, skatt, fritak])
                    continue
                else:
                    bad_lines.append(("no_bunn_candidates", line))
                    rows.append([adresse, eiendom, takst, skniv, "", "", "", "", ""])
                    continue

# skriv CSV og logg uparsa linjer til eiga fil
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(rows)

if bad_lines:
    with open("skatteliste_parse_issues.txt", "w", encoding="utf-8") as g:
        for tag, L in bad_lines:
            g.write(f"{tag}\t{L}\n")

print("Ferdig. Skrive:", OUT)
if bad_lines:
    print("Merk: nokre linjer kunne ikkje parseast automatisk. Sjå skatteliste_parse_issues.txt")
