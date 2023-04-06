import sys
from math import trunc
from operator import add

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from pre import init, name_for

collection, tags, mode, langs, tools, metrics = init(True)

plt.style.use('./my.mplstyle')

fig = plt.figure(figsize=(8.5, 3.5))
ax = fig.gca()

data = []

for index, lang in enumerate(langs):
    loc = collection[lang]['loc']
    # Remove a Python project that only contains 20LoC
    data.append(list(filter(lambda l: l > 2, loc)))

# data.reverse()

violinplot = ax.violinplot(
    data,
    positions=[0.5, 1.5, 2.5, 3.5],
    showmedians=True,
    widths=0.7,
)

for pc in violinplot['bodies']:
    pc.set_facecolor('#006CD9')

all_min_star = sys.maxsize
all_max_star = -1
all_min_loc = sys.maxsize
all_max_loc = -1

star_grouping = {'cpp': [], 'java': [], 'python': [], 'ts': []}

round_offset = 0.531

for index, lang in enumerate(langs):
    loc = collection[lang]['loc']
    milestone = np.sum(loc <= 6)
    plt.axhline(y=6, color='#990F7B', linewidth=1.2)
    plt.text(
        index + 0.5 - 0.18,
        6.05,
        f'{trunc(milestone / len(loc) * 100)}%',
        size=12,
        weight='bold',
        color='#990F7B',
    )

    # Draw white background to cover the right part of the violin plot
    ax.add_patch(Rectangle((index + 0.505, 3.05), 0.5, 3.95,
                           fill=True,
                           facecolor='white',
                           zorder=100))

    all_min_star = min(all_min_star, min(collection[lang]['stars']))
    all_max_star = max(all_max_star, max(collection[lang]['stars']))
    # Use data[index] rather than collection[lang]['loc'] to apply filter
    local_min_loc = min(data[index])
    local_max_loc = max(data[index])

    all_min_loc = min(all_min_loc, local_min_loc)
    all_max_loc = max(all_max_loc, local_max_loc)

    # Draw star background for each lang
    qualified_min_loc = local_min_loc - local_min_loc % 0.2
    qualified_max_loc = local_max_loc + 0.2 - local_max_loc % 0.2
    star_grouping[f'{lang}-qmin'] = qualified_min_loc
    for i in np.arange(qualified_min_loc, qualified_max_loc, 0.2):
        plt.plot([index + round_offset, index + 0.8 + round_offset - 0.5], [i] * 2,
                 lw=8,
                 solid_capstyle='round',
                 zorder=101,
                 color='#F4F4F4',
                 )
        filtered_loc = [j for j in range(len(collection[lang]['loc'])) if i <= collection[lang]['loc'][j] < i + 0.2]
        star_grouping[lang].append(sorted(list(map(lambda j: collection[lang]['stars'][j], filtered_loc))))

star_len = all_max_star - all_min_star
for index, lang in enumerate(langs):
    for i, clist in enumerate(star_grouping[lang]):
        for ele in clist:
            plt.plot(list(map(add, [index + round_offset + (ele - all_min_star) / star_len * 0.3] * 2, [0, 0.01])),
                     [star_grouping[f'{lang}-qmin'] + i * 0.2] * 2,
                     lw=8,
                     solid_capstyle='round',
                     zorder=102,
                     color='#EAC54F',
                     )

plt.text(
        0.51,
        star_grouping['cpp-qmin']-0.45,
        'Star',
        size=9,
        color='#2F2F2F',
        zorder=9999,
    )
plt.text(
        0.51,
        star_grouping['cpp-qmin']-0.25,
        '10k',
        size=9,
        color='#2F2F2F',
        zorder=9999,
    )
plt.text(
        0.73,
        star_grouping['cpp-qmin']-0.25,
        '350k',
        size=9,
        color='#2F2F2F',
        zorder=9999,
    )

ax.set_xticks(np.arange(0.5, len(langs) + 0.5), labels=['C++', 'Java', 'Python', 'JS/TS'])
ax.set_yticks(np.arange(0, 8), labels=['0', '10', '100', '1k', '10k', '100k', '1M', '10M'], fontsize=12)
ax.set_ylabel('LoC', fontsize=16)
ax.margins(y=0.03)
ax.set_xlim([0, 4])
ax.set_ylim([2.85, 7.1])

fig.tight_layout()

plt.subplots_adjust(left=0.087, right=0.999, top=0.999, bottom=0.09)

if mode == 'view':
    fig.show()
else:
    fig.savefig('G:/My Drive/ASE 2022/performance-loc.png')
