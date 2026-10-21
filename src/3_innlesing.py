import pandas as pd


# HVA dette skriptet gjør:
#Åpner ESS-Filen , plukker ut kolonenne vi trenger, og teller hvor mange svar some er ekte og
# hvor mange som egentlig betyr "svarte ikke", uten å endre i dataen
# FORMÅL: Finne ut hvor rotete dataen er før vi rydder i dem 


# Bare variablene vi trenger til problemstillingen.
# Fila har over 600 kolonner, og usecols gjør at vi leser inn kun disse 10.
cols = [
    "cntry",     # land (nominal)
    "gndr",      # kjønn (nominal) – kontrollvariabel
    "agea",      # alder i år (ratio) – kontrollvariabel
    "alcfreq",   # hvor ofte man drikker alkohol (ordinal)
    "alcwkdy",   # gram alkohol siste ukedag (ratio)
    "alcwknd",   # gram alkohol siste helgedag (ratio)
    "alcbnge",   # hvor ofte man drikker mye på én gang (ordinal)
    "dshltgp",   # snakket med fastlege siste 12 mnd (avkrysning 0/1) – utfall
    "dshltms",   # snakket med spesialist siste 12 mnd (avkrysning 0/1) – utfall
    "anweight",  # vekt for å sammenligne på tvers av land
    "dshltref",   # snakket med annet helsepersonell siste 12 mnd (avkrysning 0/1) – utfall
    "dshltdk",
    "dshltna",
]

# Les inn fila.
df = pd.read_csv("data/raw/ESS11e04_2.csv", usecols=cols)
# --- Oversikt ---
print("Rader og kolonner:", df.shape)
print()
df.info()
print()
print(df.describe().round(1))
print()

# --- Telling ---
# Ordinale variabler: tell hver verdi i stedet for å ta snitt
print("alcfreq (1 = hver dag ... 7 = aldri, 77/88/99 = mangler):")
print(df["alcfreq"].value_counts(dropna=False).sort_index())
print()

print("alcbnge (1 = daglig ... 5 = aldri, 6-9 = mangler):")
print(df["alcbnge"].value_counts().sort_index())
print()

# Gram-variablene: hvor mange har en kode i stedet for et ekte tall?
koder = [6666, 7777, 8888, 9999]
print("alcwkdy-koder (6666 = drikker aldri, resten = mangler):")
print(df.loc[df["alcwkdy"].isin(koder), "alcwkdy"].value_counts())
print()

# Helsespørsmålet og alder
print("Nektet helsespørsmålet:", (df["dshltref"] == 1).sum())
print("Vet ikke:", (df["dshltdk"] == 1).sum())
print("Ikke svar:", (df["dshltna"] == 1).sum())
print("Alder = 999:", (df["agea"] == 999).sum())
print()

# Hvilke land har de tomme alcfreq-verdiene?
print("Land med tom alcfreq:")
print(df.loc[df["alcfreq"].isna(), "cntry"].value_counts())
