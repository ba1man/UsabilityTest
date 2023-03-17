from math import trunc
import numpy as np
import matplotlib.pyplot as plt

from pre import init, name_for

collection, tags, mode, langs, tools, metrics = init()

plt.style.use('./my.mplstyle')

fig, axs = plt.subplots(4, 1, figsize=(8.5, 3))
plt.subplots_adjust(left=0.145, right=0.98, top=0.98, bottom=0.22)
magics = [0.84, 0.58, 0.31, 0.1]
for index, lang in enumerate(langs):
    curr = axs[index]
    loc = collection[lang]['loc']
    curr.eventplot(loc / 10 ** 6, colors='#004C99', alpha=0.6)
    curr.get_xaxis().set_visible(False)
    curr.set_yticks([])
    curr.set_xlim([0, 6])
    plt.figtext(0.02, magics[index], name_for[lang])
    if index == 2:
        curr.get_xaxis().set_visible(True)
        curr.set_xlabel('MLoC')
    milestone = np.sum(loc <= 10 ** 6)
    curr.axvline(x=1, color='#990F7B')
    curr.text(1.05,
              0,
              f'{trunc(milestone / len(loc) * 100)}%',
              size=12,
              weight='bold',
              color='#990F7B')


if mode == 'view':
    fig.show()
else:
    fig.savefig(f'G:\\My Drive\\ASE 2022\\performance-loc.png')
