import pandas as pd

path = "data/GBR_NP/GBR_NPasfrRRbo.txt"

df = pd.read_csv(path, sep=r"\s+", skiprows=3, names=[
    "year", "age", "asfr", "asfr1", "asfr2", "asfr3", "asfr4", "asfr5p",
])

df["age"] = df["age"].str.replace("-", "", regex=False).str.replace("+", "", regex=False).astype(int)
df["birth_year"] = df["year"] - df["age"]

table = df.pivot(index="birth_year", columns="age", values="asfr1").sort_index()

table.to_csv("outputs/asfr1_by_birth_year.csv")

html = (
    table.style
    .background_gradient(cmap="YlOrRd", axis=None)
    .format(precision=4, na_rep="")
    .to_html()
)
with open("outputs/asfr1_by_birth_year.html", "w") as f:
    f.write(html)

print(table)
print("Saved outputs/asfr1_by_birth_year.csv and outputs/asfr1_by_birth_year.html")
