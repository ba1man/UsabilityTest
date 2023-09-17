#! /usr/bin/env python3

import csv
import sys

# 0~10K
# 10K~100K
# 100K~200K
# 200K~300K

res = [[], [], [], []]
with open("result.csv", "r") as f:
  reader = csv.reader(f)
  next(reader, None)
  for row in reader:
    time = row[4]
    loc = float(row[6])
    if loc < 10:
      res[0].append(row)
    elif loc > 10 and loc < 100:
      res[1].append(row)
    elif loc > 100 and loc < 200:
      res[2].append(row)
    elif loc > 200 and loc < 300:
      res[3].append(row)

index = 0
for scope in res:
  max_val = 0
  min_val = sys.float_info.max
  avg_val = 0
  total = 0
  for item in scope:
    time = float(item[4])
    total += time
    if max_val < time:
      max_val = time
    if min_val > time:
      min_val = time
  avg_val = total / len(scope)
  print("scope: {}, max: {}, min: {}, avg: {}".format(index, max_val, min_val, avg_val))
  index += 1


