from colour import Color
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.collections import LineCollection
import matplotlib.patheffects as path_effects

from pre import init

collection, tags, mode, langs, tools, metrics = init()

plt.style.use('./my.mplstyle')


def draw(lang, original_data):
    fig, ax = plt.subplots(num=f'{lang}', tight_layout=True)
    plt.xlabel('Completion Time (s)')
    plt.ylabel('Peak Memory Usage (GB)')

    # Universal pruning, remove the project's data for all
    # if one tool's is bad
    data = {}
    indices = set([])
    for key in original_data:
        for index, value in enumerate(original_data[key]):
            # Not for SourceTrail, its data is originally unfulfilled,
            # this will be handled later in a sandbox
            if not key.startswith('sourcetrail') and np.isnan(value):
                indices.add(index)
    for key in original_data:
        data[key] = np.delete(original_data[key], list(indices))

    def draw_tool(loc, time, memory, color):
        def size_mapping():
            maximum = max(loc)
            # Map loc to point size between (2-12)^2
            return list(map(lambda i: i / maximum * 140 + 4, loc))

        s = size_mapping()
        legend = plt.scatter(
            time,
            memory,
            s=s,
            linewidths=0.8,
            color=color,
            alpha=0.6,
            zorder=50,
        )
        return legend

    def draw_trend(loc, time, memory, color, bgcolor):
        popt, _ = curve_fit(lambda x, a, b, c: a * x ** b + c, time, memory)

        def farthest(x, y):
            if len(x) != len(y):
                raise ValueError('Point-pair must be the same size')
            last_index = -1
            last_val = 0
            for i, v in enumerate(x):
                # Use distance to origin for approximate,
                # should use fancy geometry for more accurate result
                if (val := x[i] ** 2 + y[i] ** 2) > last_val:
                    last_index = i
                    last_val = val
            return last_index

        def trend(x):
            return popt[0] * x ** popt[1] + popt[2]

        # Helper functions
        def trend_inverse(y):
            return ((y - popt[2]) / popt[0]) ** -popt[1]

        def d_trend(x):
            return popt[0] * popt[1] * x ** (popt[1] - 1)

        index = farthest(time, memory)
        x = np.linspace(0, time[index], 100)
        y = trend(x)
        vwidth = 4 + x[:-1] / max(x) * 16
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments,
                            linewidths=vwidth,
                            color=bgcolor,
                            path_effects=[path_effects.Stroke(capstyle="round")])
        ax.add_collection(lc)
        return trend, trend_inverse, d_trend

    def draw_loc(loc, time, func):
        # Milestone (LoC) is deeply relevant to language
        if lang == 'cpp':
            milestone = 1 * 10 ** 6
            milestone_str = '1 MLoC'
        if lang == 'java':
            milestone = 8 * 10 ** 5
            milestone_str = '800 KLoC'
        elif lang == 'python':
            milestone = 2 * 10 ** 5
            milestone_str = '200 KLoC'

        temp = np.concatenate((loc, time)).reshape(2, len(loc)).T
        # Sort by LoC ascending
        temp = temp[temp[:, 0].argsort()]
        # Find the first item whose loc exceeds 1m
        first = -1
        for i, v in np.ndenumerate(temp[:, 0]):
            if v > milestone:
                first = i
                break
        if first == -1:
            print(f'Can not find a sample with LoC greater than {milestone_str}')
        else:
            x = temp[first, 1]
            y = func(temp[first, 1])
            plt.plot(x,
                     y,
                     'x',
                     ms=12,
                     mew=2,
                     c='#202020',
                     zorder=99)
            plt.text(x + 6,
                     y - 0.3,
                     milestone_str,
                     size=10,
                     zorder=100)

    legends = []
    for tool in tools:
        fixture = tools[tool]
        loc = data['loc']
        time = data[f'{tool}-{metrics[0]}']
        memory = data[f'{tool}-{metrics[1]}']
        # Remove any nan for SourceTrail and re-assign variable
        # This won't pollute the original data,
        # thus performs the functionality of a sandbox
        if tool.startswith('sourcetrail'):
            indices = set([])
            for metric in metrics:
                for i, v in enumerate(data[f'{tool}-{metric}']):
                    if np.isnan(v):
                        indices.add(i)
            indices = list(indices)
            loc = np.delete(loc, indices)
            time = np.delete(time, indices)
            memory = np.delete(memory, indices)

        l = draw_tool(loc,
                      time,
                      memory,
                      Color(fixture[1]).rgb)
        try:
            t, _, __ = draw_trend(loc,
                                  time,
                                  memory,
                                  Color(fixture[1]).rgb,
                                  Color(fixture[2]).rgb)
        except RuntimeError:
            print(f'Failed to calculate the trend for {fixture[0]}')
        else:
            draw_loc(loc,
                     time,
                     t)
        legends.append(l)

    ax.legend(handles=legends, labels=map(lambda t: tools[t][0], tools), loc='upper right')
    if mode == 'view':
        ax.title.set_text(f'performance-{lang}')
        fig.show()
    else:
        fig.savefig(f'G:\\我的云端硬盘\\ASE 2022\\performance-{lang}.png')


for lang in langs:
    draw(lang, collection[lang])
