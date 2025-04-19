import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta


# RECUPERER TOUTES LES OPTIONS SUR UNE DATE PAR MOIS

# Chargement du CSV et parsing de la colonne expirationDate
df = pd.read_csv("AAPL_options_chain.csv", parse_dates=["expiration"])
# On travaille sur des date Python (pas Timestamp)
df["expiration"] = df["expiration"].dt.date

# Détermination de la gamme de mois à couvrir
min_date = df["expiration"].min()
max_date = df["expiration"].max()

# liste des 1ers jours de chaque mois entre min_date et max_date
months = []
current = date(min_date.year, min_date.month, 1)
end = date(max_date.year, max_date.month, 1)
while current <= end:
    months.append(current)
    current += relativedelta(months=1)

# Pour chaque mois, trouver l'expiration la plus proche
filtered_parts = []
for first_of_month in months:
    # calcul de l'écart absolu entre chaque expiration et le 1er du mois
    df["delta"] = df["expiration"].apply(lambda d: abs(d - first_of_month))
    # index de la ligne la plus proche
    idx_min = df["delta"].idxmin()
    nearest_exp = df.at[idx_min, "expiration"]
    # extraire toutes les options de cette expiration
    part = df[df["expiration"] == nearest_exp].drop(columns="delta")
    filtered_parts.append(part)

# Concaténation et export
filtered = pd.concat(filtered_parts, ignore_index=True)
filtered.to_csv("AAPL_one_exp_per_month_full.csv", index=False)

print(
    f"{len(filtered_parts)} mois traités, CSV généré : AAPL_one_exp_per_month_full.csv"
)
