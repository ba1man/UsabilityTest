import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.optimize import curve_fit

from pre import init


collection, tags, mode, langs, tools, metrics = init()

plt.style.use('./my.mplstyle')


def draw(lang, data):
    plt.figure(num=f'{lang}')
    plt.xlabel('Completion Time (s)')
    plt.ylabel('Peak Memory Usage (GB)')

    # Universal pruning
    indices = []
    for index, value in enumerate(data['loc']):
        pass


    def draw_tool(name, loc, time, memory, color):
        def size_mapping():
            maximum = max(loc)
            # Map loc to point size between 4-100
            return list(map(lambda i: i / maximum * 96 + 4, loc))

        s = size_mapping()
        legend = plt.scatter(
            time,
            memory,
            s=s,
            linewidths=0.8,
            c=color,
        )
        return legend

    legends = []
    for tool in tools:
        const = tools[tool]
        l = draw_tool(
            const[0],
            data['loc'],
            data[f'{tool}-{metrics[0]}'],
            data[f'{tool}-{metrics[1]}'],
            const[1],
        )
        legends.append(l)

    if mode == 'view':
        plt.title(f'performance-{lang}')
    plt.legend(handles=legends, labels=map(lambda t: tools[t][0], tools), loc='upper right')
    plt.tight_layout()
    if mode == 'view':
        plt.show()
    else:
        plt.savefig(f'G:\\我的云端硬盘\\ASE 2022\\performance-{lang}.png')


for lang in langs:
    draw(lang, collection[lang])
