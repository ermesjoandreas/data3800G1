# src/utforsking.py
# Steg 5: Utforsk sammenhengen mellom alkohol og legebesøk.
# Kjøres fra prosjektmappa med: python src/utforsking.py
# Krever at src/rensing.py er kjørt først.
#
# Hva skriptet gjør, kort:
# 1. Leser inn de rensede dataene
# 2. Teller hvor mange som er i hver gruppe
# 3. Finner hvor mange som har vært hos lege totalt: P(lege)
# 4. Finner andelen per alkoholgruppe: P(lege | alkoholgruppe)
# 5. Deler opp på alder og kjønn for å se om forskjellen holder seg
# 6. Ser på fyll i stedet for hvor ofte man drikker
# 7. Sammenligner drikkekultur mellom regioner (Norden, Vest, Sør, Øst)
# 8. Ser om alkohol og legebesøk henger sammen likt i alle regioner
# 9. Sjekker om vekting (anweight) endrer resultatet
# 10. Lagrer tabellene som CSV i figures/

import pandas as pd

pd.set_option("display.max_columns", None)

DATA = "data/processed/ess_renset.csv"
UT = "figures/"

# --- 1. Les inn ---
df = pd.read_csv(DATA)
print("Personer:", len(df))
print()

# --- 2. Hvor mange er i hver gruppe? ---
# Små grupper gir usikre andeler, så vi sjekker størrelsen først.
for kol in ["alkohol_kat", "kjonn", "aldersgruppe"]:
    print(df[kol].value_counts().sort_index())
    print()

# --- 3. P(lege) for alle ---
# Gjennomsnittet av en 0/1-kolonne er andelen som har 1.
# "fastlege" = snakket med fastlege siste 12 mnd.
p_lege = df["fastlege"].mean()
print(f"P(fastlege) for alle: {p_lege:.3f}")
print()

# --- 4. P(lege | alkoholgruppe) ---
# Betinget sannsynlighet: vi "krymper verden" til én alkoholgruppe
# og ser hvor stor andel av dem som har vært hos fastlegen.
per_alkohol = df.groupby("alkohol_kat").agg(
    personer=("fastlege", "size"),
    andel_fastlege=("fastlege", "mean"),
    andel_lege_noen=("lege_noen", "mean"),
    median_alder=("agea", "median"),
)
print("Per alkoholgruppe:")
print(per_alkohol.round(3))
print()

# --- 5a. Kontroll for alder ---
# Hvis forskjellen mellom alkoholgruppene bare skyldes alder,
# vil den forsvinne når vi ser på én aldersgruppe om gangen.
alder_tabell = df.pivot_table(
    index="alkohol_kat", columns="aldersgruppe",
    values="fastlege", aggfunc="mean",
)
print("P(fastlege) per alkoholgruppe og aldersgruppe:")
print(alder_tabell.round(3))
print()

# --- 5b. Kontroll for kjønn ---
kjonn_tabell = df.pivot_table(
    index="alkohol_kat", columns="kjonn",
    values="fastlege", aggfunc="mean",
)
print("P(fastlege) per alkoholgruppe og kjønn:")
print(kjonn_tabell.round(3))
print()

# --- 5c. Hvor mange personer ligger bak hver andel? ---
# Andeler fra små celler er usikre (som de 15 turene i lab 39).
antall = df.pivot_table(
    index="alkohol_kat", columns="aldersgruppe",
    values="fastlege", aggfunc="size",
)
print("Antall personer per celle (alkohol x alder):")
print(antall)
print()

# --- 6. Fyll i stedet for frekvens ---
# Oblig 1: er det fyll (mye på én gang) eller jevn drikking som henger
# sammen med legebesøk? fyll_kat mangler for noen få, så de tas ut her.
fyll = df.dropna(subset=["fyll_kat"])
per_fyll = fyll.groupby("fyll_kat").agg(
    personer=("fastlege", "size"),
    andel_fastlege=("fastlege", "mean"),
    median_alder=("agea", "median"),
)
print("Per fyllgruppe:")
print(per_fyll.round(3))
print()

fyll_alder = fyll.pivot_table(
    index="fyll_kat", columns="aldersgruppe",
    values="fastlege", aggfunc="mean",
)
print("P(fastlege) per fyllgruppe og aldersgruppe:")
print(fyll_alder.round(3))
print()

# --- 7. Drikkekultur per region ---
# Oblig 1: drikker Sør-Europa jevnt og Nord-Europa i fyll?
# Vi ser bare på Europa, så Israel ("Utenfor Europa") tas ut.
europa = fyll[fyll["region"] != "Utenfor Europa"]

# Andel i hver alkoholgruppe og fyllgruppe per region.
# normalize="index" gjør at hver rad summerer til 1 (andeler, ikke antall).
frekvens_region = pd.crosstab(europa["region"], europa["alkohol_kat"],
                              normalize="index")
fyll_region = pd.crosstab(europa["region"], europa["fyll_kat"],
                          normalize="index")
print("Hvor ofte man drikker, andel per region:")
print(frekvens_region.round(3))
print()
print("Fyll, andel per region:")
print(fyll_region.round(3))
print()

# --- 8. Legebesøk per region og alkoholgruppe ---
# Er sammenhengen mellom alkohol og legebesøk den samme i alle regioner?
region_tabell = europa.pivot_table(
    index="alkohol_kat", columns="region",
    values="fastlege", aggfunc="mean",
)
print("P(fastlege) per alkoholgruppe og region:")
print(region_tabell.round(3))
print()

# --- 9. Kontroll med vekting ---
# ESS anbefaler å vekte (anweight) når man sammenligner land,
# fordi landene er ulikt store og utvalgene er trukket ulikt.
# Et vektet snitt er sum(verdi * vekt) / sum(vekt).
def vektet_andel(gruppe):
    return (gruppe["fastlege"] * gruppe["anweight"]).sum() / gruppe["anweight"].sum()


uvektet = europa.groupby("region")["fastlege"].mean()
vektet = europa.groupby("region")[["fastlege", "anweight"]].apply(vektet_andel)
print("P(fastlege) per region, uvektet og vektet:")
print(pd.DataFrame({"uvektet": uvektet, "vektet": vektet}).round(3))
print()

# --- 10. Lagre tabellene ---
# CSV kan åpnes i Excel av folk som ikke bruker Python (som i lab 41).
per_alkohol.round(3).to_csv(UT + "per_alkohol.csv")
alder_tabell.round(3).to_csv(UT + "alkohol_x_alder.csv")
kjonn_tabell.round(3).to_csv(UT + "alkohol_x_kjonn.csv")
per_fyll.round(3).to_csv(UT + "per_fyll.csv")
fyll_region.round(3).to_csv(UT + "fyll_per_region.csv")
frekvens_region.round(3).to_csv(UT + "frekvens_per_region.csv")
region_tabell.round(3).to_csv(UT + "alkohol_x_region.csv")
print("Tabeller lagret i", UT)