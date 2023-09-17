#! /usr/bin/env python3

import os
import csv
from collections import defaultdict

def read_csv(filepath):
  rows = []
  with open(filepath, 'r') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
      rows.append(row)
  return rows

def read_lines(filepath):
  with open(filepath, 'r') as f:
    lines = f.readlines()
  return lines

def write_csv(rows, filepath):
  with open(filepath, 'w') as f:
    writer = csv.writer(f)
    for row in rows:
      writer.writerow(row)
  return

def read_list():
  list_filepath = "./lists/c project list final.csv"
  rows = read_csv(list_filepath)
  return rows[1:]

def read_enre():
  out_dirpath = "./out/enre-c"
  res = set()
  for filename in os.listdir(out_dirpath):
    filepath = os.path.join(out_dirpath, filename)
    file_stat = os.stat(filepath)
    if file_stat.st_size == 52:
      continue
    res.add(filename.split("_out")[0])
  return res

def read_log():
  time_log_filepath = "./logs/2308281543.log"
  loc_log_filepath = "./logs/2308281549.log"
  time_lines = read_lines(time_log_filepath)
  loc_lines = read_lines(loc_log_filepath)
  name_map = defaultdict()
  for line in time_lines:
    if line.startswith("INFO:root:Running ENRE-c on"):
      sp = line.strip().split(" ")
      name = sp[3]
      time = sp[5]
      memory = sp[7]
      name_map[name] = [name, time, memory]

  for line in loc_lines:
    if line.startswith("INFO:root:LoC for"):
      sp = line.strip().split(" ")
      name = sp[2]
      loc = sp[4]
      if name not in name_map:
        print("{} has no time/memory result".format(name))
      else:
        name_map[name].append(loc)
  return name_map

def filter_and_fill(lists, enre_set, log_map):
  failed = []
  name_map = defaultdict()
  for item in lists:
    short_name = item[0].split("/")[1]
    if short_name not in enre_set:
      failed.append(item)
      continue
    log_res = log_map[short_name]
    name_map[short_name] = item + [
        "{:.3f}".format(float(log_res[1][:-1])),
        "{:.3f}".format(float(log_res[2][:-2]) / 1024),
        "{:.3f}".format(int(log_res[3]) / 1000),
    ]
  rows = [["name", "stars", "html url", "clone url", "time (s)", "memory (GB)", "KLoC"]]
  rows += list(name_map.values())
  return rows, failed

def write_result(result, failed):
  failed_filepath = "failed.csv"
  result_filepath = "result.csv"
  write_csv(result, result_filepath)
  write_csv(failed, failed_filepath)
  return

if __name__ == '__main__':
  lists = read_list()
  enre_set = read_enre()
  log_name_map = read_log()
  result_rows, failed_rows = filter_and_fill(lists, enre_set, log_name_map)
  write_result(result_rows, failed_rows)

