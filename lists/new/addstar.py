import csv
import requests
import time
import sys

FILE_NAME = 'python-160917.csv'
BREAKPOINT = None

container = []
header = None

with open(FILE_NAME, 'r', encoding='utf8') as f:
  r = csv.reader(f)
  for row in r:
    if header is None:
      header = list(row)
    else:
      obj = {}
      for i, key in enumerate(header):
        obj[key] = row[i]
      container.append(obj)

with open(f'loc-{FILE_NAME}', 'w') as f:
  w = csv.writer(f)
  if BREAKPOINT == None:
    w.writerow(header + ['loc'])

  for repo in container:
    print(repo["name"], end='')

    if BREAKPOINT != None:
      if repo['name'] == BREAKPOINT:
        BREAKPOINT = None
      print(' - (Skipped)')
      continue

    res = requests.get(
      f'https://api.codetabs.com/v1/loc?github={repo["name"]}'
      ).json()
    for item in res:
      if item == 'Error':
        repo['loc'] = -1
      elif item['language'] == 'Python':
        repo['loc'] = item['linesOfCode']
        break
    if 'loc' not in repo.keys():
      repo['loc'] = -1
    w.writerow([repo[key] for key in (header + ['loc'])])

    # To not overcross Third-party's request rate limit
    print(f' - {repo["loc"]}', end='')
    for i in range(5):
      print('.', end='')
      time.sleep(1)
    print('')
