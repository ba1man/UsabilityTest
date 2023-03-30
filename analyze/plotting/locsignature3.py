from math import trunc

import numpy
import numpy as np
import matplotlib.pyplot as plt

from pre import init, name_for

collection, tags, mode, langs, tools, metrics = init()

plt.style.use('./my.mplstyle')

fig = plt.figure(figsize=(8.5, 3.5))
ax = fig.gca()

data = []

for index, lang in enumerate(langs):
    loc = collection[lang]['loc']
    data.append(list(filter(lambda l: l > 0, loc)))

# data.reverse()

violinplot = ax.violinplot(
    data,
    positions=[0.85, 1.77, 2.75, 3.67],
    showmedians=True,
    widths=0.4,
)

for pc in violinplot['bodies']:
    pc.set_facecolor('#006CD9')

for index, lang in enumerate(langs):
    loc = collection[lang]['loc']
    milestone = np.sum(loc <= 6)
    plt.axhline(y=6, color='#990F7B', linewidth=1.2)
    plt.text(
        (4 - index) - 0.25,
        6,
        f'{trunc(milestone / len(loc) * 100)}%',
        size=12,
        weight='bold',
        color='#990F7B',
    )

star_data = []
min_loc = 100
max_loc = 0
for index, lang in enumerate(langs):
    min_loc = min(min_loc, min(collection[lang]['loc']))
    max_loc = max(max_loc, max(collection[lang]['loc']))

for index, lang in enumerate(langs):
    stars = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    temp = (max_loc - min_loc)/15
    test = set()
    for index, loc in enumerate(collection[lang]['loc']):
        new_index = int((loc-min_loc)/temp)
        if new_index == 15:
            new_index = 9
        stars[new_index].append(collection[lang]['stars'][index])
    star_data.append(stars)

max_star = 0
min_star = 10000
for index, lang in enumerate(langs):
    min_star = min(min_star, min(collection[lang]['stars']))
    max_star = max(max_star, max(collection[lang]['stars']))

star_temp = (max_star - min_star)
# star_temp = 0.15 / star_temp
start_temp = [0.15, 0.39, 0.63, 0.87]

loc_temp = (max_loc - min_loc) / 10
for index, stars in enumerate(star_data):
    start = start_temp[index]
    for temp_index, star in enumerate(stars):
        y = min_loc + temp * temp_index
        plt.axhline(y=y, xmin=start, xmax=start + 0.10, color='#DCDCDC', linewidth=5,alpha=0.3)
        if star.__len__() == 0:
            continue

        xmin = (min(star) - min_star) * 0.1 / star_temp + start
        xmax = (max(star) - min_star) * 0.1 / star_temp + start
        if xmin == xmax:
            xmax = xmax + 0.01
        print(f"xmin: {xmin}, xmax : {xmax}")
        print(f"star range: {min(star)} - {max(star)} ")

        plt.axhline(y=y, xmin=xmin, xmax=xmax, color='#FFCC00', linewidth=5)
    # plt.axhspan(ymin=min_loc-0.1, ymax=max_loc, xmin=start-0.001, xmax=start+0.101, facecolor='#DCDCDC', alpha=0.5)

column = [1.55, 2.48, 3.45, 4.35]
for index, lang in enumerate(langs):
    plt.text(
        column[index],
        min_loc,
        f'{max_star}',
        size=5,
        weight='bold',
    )
    plt.text(
        column[index]-0.5,
        min_loc,
        f'{min_star}',
        size=5,
        weight='bold',
    )

ax.set_xticks(np.arange(1, len(langs) + 1), labels=['C++', 'Java', 'Python', 'JS/TS'])
ax.set_yticks(np.arange(0, 7), labels=['0', '10', '100', '1k', '10k', '100k', '1M'], fontsize=12)
ax.set_ylabel('MLoC', fontsize=16)
ax.margins(y=0.03)
ax.set_xlim([0.55, 4.45])

fig.tight_layout()

plt.subplots_adjust(left=0.087, right=0.999, top=0.999, bottom=0.155)

if mode == 'view':
    fig.show()
else:
    fig.savefig(f'./performance-loc.png',)
