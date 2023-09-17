#! /usr/bin/env python3

import csv
import os
import matplotlib.pyplot as plt
import numpy as np

filename = "result.csv"

res = []
with open(filename, 'r') as f:
  reader = csv.reader(f, delimiter=',')
  next(reader, None)
  for row in reader:
    res.append({
      "name": row[0],
      "loc": float(row[6]),
      "time": float(row[4]),
      "memory": float(row[5]),
    })

filtered = []
for item in res:
  if item["loc"] < 2000:
    filtered.append(item)

res = sorted(filtered, key=lambda x : x["loc"])
x = np.array([x["loc"] for x in res])
y = np.array([x["time"] for x in res])
# labels = [x["name"] for x in res]

# fig, ax = plt.subplots()
# ax.scatter(x, y)

# for i, txt in enumerate(labels):
  # ax.annotate(txt, (x[i], y[i]))



plt.scatter(x, y)
plt.title("enre-cpp performance")
plt.xlabel("KLoC")
plt.ylabel("time (s)")

plt.legend()
plt.savefig("out.png")
