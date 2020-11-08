import pandas as pd
import json
# This is here just so you could easily install the package
# import openpyxl

# Read data to dataframe
with open("kv-ads-2020-11-03T09-39-44_TARMO.jl") as f:
    df = pd.DataFrame([json.loads(l) for l in f.readlines()])

# To display all columns
pd.set_option('display.max_columns', None)
print(df.head())

# Write first 100 rows to csv file and to xlsx file (so you could look around)
# Replace newline with other symbol (otherwise Excel is a mess)
# df.description = df.description.apply(lambda x: x.replace('\n', '\\n'))
# part = df.iloc[:100, :]
# part.to_csv(path_or_buf="korterid.csv", encoding="utf-8-sig", index=False)
# part.to_excel(excel_writer="korterid.xlsx")
