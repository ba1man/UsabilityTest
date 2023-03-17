from math import trunc
import numpy as np
import matplotlib.pyplot as plt

from pre import init, name_for

collection, tags, mode, langs, tools, metrics = init()

plt.style.use('./my.mplstyle')

fig = plt.figure(figsize=(8.5, 3.5))
ax = fig.gca()

data = []

for index, lang in enumerate(langs):
    loc = collection[lang]['loc'] / 10 ** 6
    data.append(list(filter(lambda l: l > 0, loc)))

data.reverse()

violinplot = ax.violinplot(
    data,
    vert=False,
    showmedians=True,
    widths=0.8,
)

for pc in violinplot['bodies']:
    pc.set_facecolor('#006CD9')

for index, lang in enumerate(langs):
    loc = collection[lang]['loc']
    milestone = np.sum(loc <= 10 ** 6)
    plt.axvline(x=1, color='#990F7B', linewidth=1.2)
    plt.text(
        0.7,
        (4 - index) - 0.25,
        f'{trunc(milestone / len(loc) * 100)}%',
        size=12,
        weight='bold',
        color='#990F7B',
    )

ax.set_yticks(np.arange(1, len(langs) + 1), labels=['JS/TS', 'Python', 'Java', 'C++'])
ax.set_xticks(np.arange(0, 6))
ax.set_xlabel('MLoC')
ax.margins(x=0.02)
ax.set_ylim([0.55, 4.45])

# ax.relim()
# ax.autoscale()

fig.tight_layout()

plt.subplots_adjust(left=0.087, right=0.999, top=0.999, bottom=0.155)

if mode == 'view':
    fig.show()
else:
    fig.savefig(f'G:\\My Drive\\ASE 2022\\performance-loc.png',)
