import pandas as pd

path = "data/finalisingcohorttables2024finalforupload.xlsx"

df = pd.read_excel(path, sheet_name="Table 2", header=7)
df = df.rename(columns={df.columns[0]: "birth_year"})

col_map = {
    "Age exact years - 16\n[note 4]": 16,
    "Final [note 5]": "final",
    "Proportion of women having \nhad no children [note 8]": "childless",
}
col_map.update({str(a): a for a in range(17, 46)})

df = df.rename(columns=col_map)
df["birth_year"] = df["birth_year"].astype(int)
df = df.set_index("birth_year")

cumulative = df[[a for a in range(16, 46)]]

ages = list(range(16, 45))
cond_asfr1 = pd.DataFrame(
    {age: (cumulative[age + 1] - cumulative[age]) / (1 - cumulative[age]) for age in ages},
    index=cumulative.index,
)
cond_asfr1.columns.name = "age"

cond_asfr1.to_csv("outputs/table2_cond_asfr1.csv")
print(cond_asfr1)
print("Saved outputs/table2_cond_asfr1.csv")
