import pandas as pd
from sklearn.cluster import OPTICS
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import json

# This is here just so you could easily install the package
# import openpyxl

# Read data to dataframe
with open("kv-ads-2020-11-03T09-39-44_TARMO.jl") as f:
    df = pd.DataFrame([json.loads(l) for l in f.readlines()])

# To display all columns
pd.set_option('display.max_columns', None)

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

# Extracting municipality from address
municipality = [(i.split(",")[-2]).strip() for i in df['address']]
df.insert(len(df.columns), 'municipality', municipality)

# Move 'geo' column to the very end
geo = df.pop('geo')
df.insert(len(df.columns), 'geo', geo)

# Replace missing values with 0
df = df.fillna(np.nan)
df['energyClass'] = df['energyClass'].replace('Puudub', np.nan)
df['energyClass'] = df['energyClass'].replace('-', np.nan)

# Geo clustering using OPTICS clustering, because it works with geo-coordinates and it also deals with noise. Also it
# has the ability to have clusters with varying densities
koordinaadid = np.array([[i['lng'], i['lat']] for i in df['geo']])
# I chose min_samples=5, because it made decent amount of clusters(not too much and not too many) and I also used
# max_eps=0.1, to eliminate noise in clusters. max_eps=01 is around 10km. One bad thing here is that in Estonia one
# longitude is 111km and one latitude is ~57km, so longitude values have pretty much double the weight than latitude.
# Not sure if it's smth worth taking it to account or not.
clust = OPTICS(min_samples=5, max_eps=0.1).fit(koordinaadid)
labels = clust.labels_[clust.ordering_]
# Insert clusters to dataframe
df.insert(len(df.columns), 'cluster', labels)

# Down here is commented out cluster plotting
'''
space = np.arange(len(koordinaadid))
reachability = clust.reachability_[clust.ordering_]
plt.figure(figsize=(10, 10))
G = gridspec.GridSpec(2, 3)
ax1 = plt.subplot(G[0, :])
ax2 = plt.subplot(G[1, 1:])

# Reachability plot
colors = ['g.', 'r.', 'b.', 'y.', 'c.']
for i in range(len(labels)):
    Xk = space[labels == i]
    Rk = reachability[labels == i]
    ax1.plot(Xk, Rk, colors[i % 5], alpha=0.3)
ax1.plot(space[labels == -1], reachability[labels == -1], 'k.', alpha=0.3)
ax1.set_ylabel('Reachability (epsilon distance)')
ax1.set_title('Reachability Plot')

# OPTICS
colors = ['g.', 'r.', 'b.', 'y.', 'c.']
for i in range(len(labels)):
    Xk = koordinaadid[clust.labels_ == i]
    ax2.plot(Xk[:, 0], Xk[:, 1], colors[i % 5], alpha=0.3)
ax2.plot(koordinaadid[clust.labels_ == -1, 0], koordinaadid[clust.labels_ == -1, 1], 'k+', alpha=0.1)
ax2.set_title('Automatic Clustering\nOPTICS')

plt.tight_layout()
plt.show()
print("Total number of clusters:", (max(labels)+1))
'''
print("Size of selected dataframe:", len(df))
print("Existing columns:", list(df.columns))
print("NaN values in: " + str([i + ": " + str(df[i].isnull().sum()) + " NaNs" for i in df.columns if df[i].isnull().sum() > 0]) if df.isnull().values.any() else 'There are no null values in the dataframe')

# Write first 100 rows to csv file and to xlsx file (so you could look around)
# df.description = df.description.apply(lambda x: x.replace('\n', '\\n'))  # Have to replace newline with other symbol (otherwise Excel is a mess)
# part = df.iloc[:100, :]
# part.to_csv(path_or_buf="korterid.csv", encoding="utf-8-sig", index=False)
# part.to_excel(excel_writer="korterid.xlsx")
