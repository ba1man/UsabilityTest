import math
from functools import reduce

from colour import Color
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.collections import LineCollection
import matplotlib.patheffects as path_effects
from shapely.geometry import LineString, Point
import descartes


from pre import init

collection, tags, mode, langs, tools, metrics = init()

plt.style.use('./my.mplstyle')


def draw(lang, original_data):
    fig, ax = plt.subplots(num=f'{lang}', tight_layout=True)
    plt.xlabel('Completion Time (s)')
    plt.ylabel('Peak Memory Usage (GB)')

    # if lang == 'python':
    #     ax.set_ylim([0, 3])

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
            # Map loc to point size between (2-14)^2
            return list(map(lambda i: i / maximum * 192 + 4, loc))

        s = size_mapping()
        legend = plt.scatter(
            time,
            memory,
            marker='+',
            s=s,
            linewidths=0.8,
            color=color,
            # alpha=0.6,
            zorder=50,
        )
        return legend

    def draw_trend(tool, _loc, _time, _memory, color, bgcolor):
        if lang != 'python':
            milestone = 1 * 10 ** 6
            milestone_str = '1MLoC'
        else:
            milestone = 2 * 10 ** 5
            milestone_str = '200KLoC'

        # Manually remove obvious abnormal point
        indices = []
        if lang == 'java' and tool == 'sourcetrail':
            # This does not affect the result too many
            # indices.append(2)
            # indices.append(25)
            pass
        elif lang == 'cpp' and tool == 'depends':
            indices.append(14)
            indices.append(55)
        if len(indices) != 0:
            loc = np.delete(_loc, indices)
            time = np.delete(_time, indices)
            memory = np.delete(_memory, indices)
        else:
            loc = _loc
            time = _time
            memory = _memory

        popt, _ = curve_fit(lambda x, a, b, c: a * x ** b + c,
                            time,
                            memory,
                            # A lower number will cause interation fails on python-st
                            maxfev=2400 if lang == 'python' and tool == 'sourcetrail' else 800)

        def trend(x):
            return popt[0] * x ** popt[1] + popt[2]

        # Helper functions
        def trend_inverse(y):
            return ((y - popt[2]) / popt[0]) ** -popt[1]

        def d_trend(x):
            return popt[0] * popt[1] * x ** (popt[1] - 1)

        def sampling():
            pairs = []
            for x in range(0, 1200, 1):
                pairs.append((x, trend(x)))
            pline = LineString(pairs)
            projection = []
            for index, value in enumerate(time):
                opoint = Point(value, memory[index])
                projection.append(pline.project(opoint))

            # Calculate the LoC~CurveLength function
            params, _ = curve_fit(lambda x, a, b: a * x + b, loc, projection)

            def loc2len(x):
                return params[0] * x + params[1]

            # If maximum LoC is less than 1M / 200K, then extend the right-most
            # coords to that milestones
            suggested_eol = pline.interpolate(max(max(projection), loc2len(milestone)))

            return suggested_eol, lambda loc: pline.interpolate(loc2len(loc)).x

        eol, loc2x = sampling()
        valid_x = max(0, trend_inverse(0))
        x = np.linspace(valid_x, eol.x, 100)
        y = trend(x)
        vwidth = 4 + x[:-1] / max(x) * 16
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments,
                            linewidths=vwidth,
                            color=bgcolor,
                            path_effects=[path_effects.Stroke(capstyle="round")])
        ax.add_collection(lc)

        # Draw milestone
        mx = loc2x(milestone)
        my = trend(mx)
        plt.plot(mx,
                 my,
                 'x',
                 ms=12,
                 mew=2,
                 c='#202020',
                 zorder=99)
        # Case-by-case place the text label
        offsetx = 20
        offsety = -0.45
        if lang == 'java' and tool == 'sourcetrail':
            offsetx = -75
        elif lang == 'cpp':
            offsetx = 12
            offsety = -0.45
        elif lang == 'python':
            offsety = -0.14
            if tool == 'sourcetrail':
                offsetx = -110
            else:
                offsetx = 15
        plt.text(mx + offsetx,
                 my + offsety,
                 milestone_str,
                 size=10,
                 zorder=100)

        # Calculate R2
        residuals = memory - trend(time)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((memory - np.mean(memory)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        print(f'{lang}-{tool}-r2: {r_squared}')

        return trend, trend_inverse, d_trend

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
            pass
        except RuntimeError:
            print(f'Failed to calculate the trend for {fixture[0]}')
        t, _, __ = draw_trend(tool,
                              loc,
                              time,
                              memory,
                              Color(fixture[1]).rgb,
                              Color(fixture[2]).rgb)
        legends.append(l)

    ax.legend(handles=legends,
              labels=map(lambda t: tools[t][0], tools),
              prop={'size': 14},
              loc='upper right' if lang != 'python' else 'lower right')
    if mode == 'view':
        ax.title.set_text(f'performance-{lang}')
        fig.show()
    else:
        fig.savefig(f'G:\\我的云端硬盘\\ASE 2022\\performance-{lang}.png')


for lang in langs:
    draw(lang, collection[lang])
