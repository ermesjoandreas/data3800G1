# src/rensing.py
# Steg 2: Rens ESS runde 11 og lagre en renset fil.
# Kjøres fra prosjektmappa med: python src/rensing.py
#
# Hva skriptet gjør, kort:
# 1. Leser inn variablene vi trenger
# 2. Fjerner personer som ikke svarte på helsespørsmålet
# 3. Setter 0 gram og "aldri fyll" for de som aldri drikker
# 4. Gjør koder som 77, 999 og 6666 om til manglende verdier (NaN)
# 5. Fjerner personer som mangler svar vi trenger
# 6. Lager lesbare kategorier (alkohol, fyll, alder, kjønn, region, legebesøk)
# 7. Lagrer resultatet i data/processed/ess_renset.csv

import numpy as np
import pandas as pd

pd.set_option("display.max_columns", None)

RAW = "data/raw/ESS11e04_2.csv"
OUT = "data/processed/ess_renset.csv"

cols = [
    "cntry", "gndr", "agea",
    "alcfreq", "alcwkdy", "alcwknd", "alcbnge",
    "dshltgp", "dshltms", "dshltref", "dshltdk", "dshltna",
    "anweight",
]


def tell(df, steg):
    """Skriver ut hvor mange rader vi har etter et steg."""
    print(f"{steg:<45} {len(df):>7,} rader")


# --- 1. Les inn ---
# data/raw endres aldri, vi bare leser fra den.
df = pd.read_csv(RAW, usecols=cols)
tell(df, "1. Lest inn")

# --- 2. Fjern de som ikke svarte på helsespørsmålet ---
# dshltgp har ingen egen kode for "mangler": 0 kan bety "nei" ELLER "nektet".
# De som nektet, ikke visste eller ikke svarte er markert i egne kolonner.
# For dem betyr 0 i dshltgp ikke "nei", så de må ut.
svarte = (df["dshltref"] == 0) & (df["dshltdk"] == 0) & (df["dshltna"] == 0)
df = df[svarte].copy()
tell(df, "2. Svarte på helsespørsmålet")

# --- 3. Fyll inn svar vi vet for de som aldri drikker ---
# Personer som svarte "aldri" (alcfreq = 7) fikk ikke spørsmålene om gram
# og fyll, og har koden "ikke aktuelt" (6666 for gram, 6 for fyll).
# Vi vet likevel svaret: 0 gram, og fyll = 5 ("aldri").
# Dette må skje FØR vi gjør resten av kodene om til NaN (steg 4).
aldri = df["alcfreq"] == 7
for kol in ["alcwkdy", "alcwknd"]:
    df.loc[aldri & (df[kol] == 6666), kol] = 0
df.loc[aldri & (df["alcbnge"] == 6), "alcbnge"] = 5

# --- 4. Koder -> NaN ---
# Tallene under er ikke ekte svar, men koder for nektet / vet ikke / ikke svar.
# isna() finner dem ikke, fordi de ser ut som vanlige tall (som i lab 41).
# Kodene er hentet fra kodeboka (ESS11e04_2 codebook.html).
koder = {
    "agea":    [999],
    "alcfreq": [77, 88, 99],
    "alcbnge": [6, 7, 8, 9],          # 6 = ikke aktuelt (drikker aldri)
    "alcwkdy": [6666, 7777, 8888, 9999],
    "alcwknd": [6666, 7777, 8888, 9999],
    "gndr":    [9],
}
for kol, verdier in koder.items():
    antall = df[kol].isin(verdier).sum()
    df.loc[df[kol].isin(verdier), kol] = np.nan
    print(f"   {kol:<10} {antall:>6,} koder gjort om til NaN")

# --- 5. Fjern rader som mangler det vi trenger ---
# Vi trenger alkoholfrekvens, legebesøk, kjønn og alder for hver person.
# Gram og fyll (alcwkdy, alcwknd, alcbnge) får beholde NaN, fordi
# hovedanalysen bruker alcfreq. Da mister vi færre personer.
df = df.dropna(subset=["alcfreq", "dshltgp", "gndr", "agea"])
tell(df, "5. Har alkohol, legebesøk, kjønn og alder")

# --- 6. Lag lesbare kategorier ---
# alcfreq er ordinal (1 = hver dag ... 7 = aldri), så vi grupperer den
# i stedet for å regne gjennomsnitt.
def alkohol_kategori(f):
    if f <= 2:
        return "1 ofte"        # hver dag eller flere ganger i uka
    elif f <= 5:
        return "2 av og til"   # ukentlig til månedlig
    elif f == 6:
        return "3 sjelden"     # sjeldnere enn månedlig
    else:
        return "4 aldri"


def aldersgruppe(alder):
    if alder < 30:
        return "15-29"
    elif alder < 45:
        return "30-44"
    elif alder < 65:
        return "45-64"
    else:
        return "65+"


def fyll_kategori(b):
    # alcbnge: 1 = daglig, 2 = ukentlig, 3 = månedlig, 4 = sjeldnere, 5 = aldri
    if pd.isna(b):
        return np.nan
    elif b <= 2:
        return "1 ukentlig+"
    elif b <= 4:
        return "2 av og til"
    else:
        return "3 aldri"


# Regioner etter drikkekultur (oblig 1: Sør-Europa mot Nord-Europa).
# Dette er et valg gruppa har tatt, og det må stå i rapporten.
# Israel (IL) er ikke i Europa og holdes utenfor regionsammenligningen.
REGIONER = {
    "Norden": ["NO", "SE", "FI", "IS"],
    "Vest":   ["AT", "BE", "CH", "DE", "FR", "NL", "GB", "IE"],
    "Sør":    ["ES", "IT", "PT", "GR", "CY"],
    "Øst":    ["BG", "EE", "HU", "LT", "LV", "PL", "SK", "UA",
               "HR", "SI", "ME", "RS"],
}
land_til_region = {land: region
                   for region, liste in REGIONER.items()
                   for land in liste}

df["alkohol_kat"] = df["alcfreq"].apply(alkohol_kategori)
df["fyll_kat"] = df["alcbnge"].apply(fyll_kategori)
df["region"] = df["cntry"].map(land_til_region).fillna("Utenfor Europa")
df["aldersgruppe"] = df["agea"].apply(aldersgruppe)
df["kjonn"] = df["gndr"].map({1: "mann", 2: "kvinne"})

# Utfall: har personen snakket med fastlege eller spesialist siste 12 mnd?
df["fastlege"] = df["dshltgp"]
df["lege_noen"] = ((df["dshltgp"] == 1) | (df["dshltms"] == 1)).astype(int)

# Tall som egentlig er hele tall, tilbake til int (NaN gjorde dem til float)
for kol in ["alcfreq", "gndr", "agea"]:
    df[kol] = df[kol].astype(int)

# Kolonnene vi bare trengte til å rense, kan fjernes
df = df.drop(columns=["dshltref", "dshltdk", "dshltna"])

# --- 7. Sjekk resultatet ---
print()
print(df.describe().round(1))
print()
for kol in ["alkohol_kat", "fyll_kat", "aldersgruppe", "kjonn", "region"]:
    print(df[kol].value_counts().sort_index())
    print()

# Kontroll: ingen koder skal være igjen
for kol, verdier in koder.items():
    assert not df[kol].isin(verdier).any(), f"{kol} har fortsatt koder"
print("Kontroll OK: ingen koder igjen.")

# --- 8. Lagre ---
df.to_csv(OUT, index=False)
print(f"Lagret {len(df):,} rader til {OUT}")