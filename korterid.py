import pandas as pd
import numpy as np
import json

# This is here just so you could easily install the package
# import openpyxl

# Read data to dataframe
with open("kv-ads-2020-11-03T09-39-44_TARMO.jl") as f:
    df = pd.DataFrame([json.loads(l) for l in f.readlines()])

# To display all columns
pd.set_option('display.max_columns', None)
# print(df.head())
# print(df.category.describe())
# print(df.category.unique())

# Dropping unnecessary columns; we only need apartment data
print("Size of original dataframe:", len(df))
df = df[df.isPassive == False]
df = df[df.propertyType == 'APARTMENT']
df = df[df.transactionType == 'RENTAL']
df.drop_duplicates(subset="id", keep='first', inplace=True)  # Remove rows with duplicate 'id' values
df = df.drop(columns=['images', 'isPassive', 'propertyType', 'transactionType', 'category', 'id', 'description'])

# Extract data from 'extra' and insert it into new column
df['numRooms'] = [i['numRooms'] for i in df['extra']]
df['area'] = [i['area'] for i in df['extra']]
df['yearConstructed'] = [i['yearConstructed'] for i in df['extra']]
df['state'] = [i['state'] for i in df['extra']]
df['energyClass'] = [d['energyClass'] for d in df['extra']]
df['floor'] = [i['floor'] for i in df['extra']]
# df['totalFloors'] = [i['totalFloors'] for i in df['extra']] # I'd say we don't need the total number of floors — Tarmo

# Extract address from 'title' and insert it into new column
df['address'] = ["-".join(i.split("-")[1:]) for i in df['title']]

df = df.drop(columns=['extra', 'title'])

# Move 'geo' column to the very end
geo = df.pop('geo')
df.insert(len(df.columns), 'geo', geo)

# Replace missing values with 0
df = df.fillna(np.nan)
df['energyClass'] = df['energyClass'].replace('Puudub', np.nan)
df['energyClass'] = df['energyClass'].replace('-', np.nan)

print("Size of cleaned dataframe:", len(df))
print("Existing columns:", list(df.columns))
print("NaN values in: " + str([i + ": " + str(df[i].isnull().sum()) + " NaNs" for i in df.columns if df[i].isnull().sum() > 0]) if df.isnull().values.any() else 'There are no null values in the dataframe')

# Write first 100 rows to csv file and to xlsx file (so you could look around)
# df.description = df.description.apply(lambda x: x.replace('\n', '\\n'))  # Have to replace newline with other symbol (otherwise Excel is a mess)
part = df.iloc[:100, :]
# part.to_csv(path_or_buf="korterid.csv", encoding="utf-8-sig", index=False)
# part.to_excel(excel_writer="korterid.xlsx")
