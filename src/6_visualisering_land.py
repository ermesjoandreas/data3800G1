# src/figur_land.py
# Figur: forskjell i bruk av helsetjenester mellom de som drikker
# og de som aldri drikker, per land.
# Kjøres fra prosjektmappa med: python src/figur_land.py
# Krever at src/rensing.py er kjørt først.

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/processed/ess_renset.csv")

# Hvor mange typer leger (fastlege + spesialist) har personen snakket med? 0, 1 eller 2
df["lege_antall"] = df["dshltgp"] + df["dshltms"]

# To alkoholgrupper per land, så hver gruppe blir stor nok
df["drikker"] = df["alcfreq"].apply(lambda f: "aldri" if f == 7 else "drikker")

# Gjennomsnittlig lege_antall per land og alkoholgruppe
tabell = df.pivot_table(index="cntry", columns="drikker",
                        values="lege_antall", aggfunc="mean")

# Forskjell: positiv = de som drikker bruker mer helsetjenester
tabell["forskjell"] = tabell["drikker"] - tabell["aldri"]
tabell = tabell.sort_values("forskjell")

# Blå når de som drikker bruker mer, oransje når de som aldri drikker bruker mer
farger = ["#2a78d6" if f > 0 else "#eb6834" for f in tabell["forskjell"]]

ax = tabell["forskjell"].plot(kind="barh", color=farger, figsize=(7, 9))
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Bruker de som drikker mer helsetjenester enn de som aldri drikker?")
ax.set_xlabel("Forskjell i antall legetyper (drikker minus aldri)")
ax.set_ylabel("Land")

# Forklaring av fargene
ax.text(0.98, 0.02, "Blå: de som drikker bruker mer\nOransje: de som aldri drikker bruker mer",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig("figures/forskjell_per_land.png", dpi=150)
print("Lagret figures/forskjell_per_land.png")