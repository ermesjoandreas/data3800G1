# src/figur.py
# Steg 7: Én figur som viser hovedfunnet.
# Kjøres fra prosjektmappa med: python src/figur.py
# Krever at src/rensing.py er kjørt først.
#
# Figuren viser andelen som har snakket med fastlege siste 12 måneder,
# per aldersgruppe og alkoholgruppe. Den viser at alder betyr mye mer
# enn alkohol for legebesøk.

import matplotlib.pyplot as plt
import pandas as pd

# Les inn de rensede dataene
df = pd.read_csv("data/processed/ess_renset.csv")

# Samme tabell som i utforsking.py: aldersgruppe nedover, alkoholgruppe bortover.
# Gjennomsnittet av fastlege (0/1) er andelen som har vært hos fastlegen.
tabell = df.pivot_table(index="aldersgruppe", columns="alkohol_kat",
                        values="fastlege", aggfunc="mean")

# Søylediagram: én gruppe søyler per aldersgruppe.
# Alkoholgruppene går fra "ofte" (mørk) til "aldri" (lys).
farger = ["#184f95", "#2a78d6", "#5598e7", "#86b6ef"]
ax = tabell.plot(kind="bar", color=farger, figsize=(8, 5), rot=0)

ax.set_title("Andel som har snakket med fastlege, per alder og alkoholbruk")
ax.set_xlabel("Aldersgruppe")
ax.set_ylabel("Andel siste 12 måneder")
ax.set_ylim(0, 1)
ax.legend(title="Drikker alkohol")

# Lagre figuren
plt.tight_layout()
plt.savefig("figures/fastlege_alder_alkohol.png", dpi=150)
print("Lagret figures/fastlege_alder_alkohol.png")