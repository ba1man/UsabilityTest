from colour import Color
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch
import math

from pre2 import init

collection, tags, mode, langs, tools, metrics = init()
features = [{'key': 'time', 'text': 'Completion Time (s)', 'settings': {'xlim0': 25, 'xlim1': 600}},
            {'key': 'memory', 'text': 'Peak Memory Usage (GB)', 'settings': {'xlim0': 1.2, 'xlim1': 3}}]
SLICE_POINT = 10000 # LoC that divide the whole data set into two parts

# Draw Variables
HEIGHT = 1
BOX_WIDTH = 0.6
LIGHT_GRAY = '#f0f0f0'
DARKER_GRAY = '#9f9f9f'
GRADIENT_BASE = '#66b3ff'
HEAT_RESOLUTION = 200
HEAT_COLOR_DOWN = -0.4 # Smaller is brighter (if apply to luminance)
HEAT_COLOR_KEY = 'hue'
LOC_LABEL_FONT_SIZE = 12

plt.style.use('./my.mplstyle')

lang = langs[0] # Should be Python only

fig = plt.figure(figsize=(17,8))
subs = fig.subfigures(len(features), 1)
axs = []
for i, _ in enumerate(features):
    subs[i].subplots(1, 3, width_ratios=[30, 1, 30])
    subs[i].subplots_adjust(wspace=0.12)
    subs[i].suptitle(features[i]['text'])
    axs.append([subs[i].axes[0], subs[i].axes[2], subs[i].axes[1]])

    heat_indicator = subs[i].axes[1]
    heat_indicator.set_xticks([0.5], ['LoC'], fontdict={'fontsize': LOC_LABEL_FONT_SIZE})
    for i in range(HEAT_RESOLUTION):
        color = Color(GRADIENT_BASE)
        getattr(color, f'set_{HEAT_COLOR_KEY}')(getattr(color, f'get_{HEAT_COLOR_KEY}')() - HEAT_COLOR_DOWN * i / HEAT_RESOLUTION)
        heat_indicator.add_patch(pch.Rectangle(
            (0, i / HEAT_RESOLUTION),
            1, 1 / HEAT_RESOLUTION,
            facecolor=color.web,
        ))
        heat_indicator.set_ylim(0, 1)
        heat_indicator.set_yticks([0, 0.5, 1], labels=[0, '5k', '10k'], fontdict={'fontsize': LOC_LABEL_FONT_SIZE})
        heat_indicator.twinx().set_yticks([0, 0.5, 1], labels=[0, '325k', '750k'], fontdict={'fontsize': LOC_LABEL_FONT_SIZE})

# Common data
raw_data = collection[lang]
heat_min = math.floor(raw_data['loc'].min() / 100) * 100
heat_max = {
    'lower': SLICE_POINT,
    'higher': math.ceil(max(list(filter(lambda i: i > SLICE_POINT, raw_data['loc']))) / 10000) * 10000,
}

for inf, feature in enumerate(features):
    # Data preparation
    data = {'pycg-time-higher': [], 'pycg-memory-higher': []}

    for tool in tools:
        inkey = f'{tool}-{feature["key"]}'
        for iv, value in enumerate(raw_data[inkey]):
            loc = raw_data['loc'][iv]

            if loc <= SLICE_POINT:
                outkey = inkey + '-lower'
            else:
                outkey = inkey + '-higher'

            if outkey not in data:
                data[outkey] = []
            
            data[outkey].append({'loc': loc, 'value': value})

    for ins, slice in enumerate(['lower', 'higher']):
        ax = axs[inf][ins]
        # Draw box plot
        ax.set_xlim([0, feature['settings'][f'xlim{ins}']])
        bp = ax.boxplot(
            [list(map(lambda r: r['value'], data[f'{tool}-{feature["key"]}-{slice}'])) for tool in tools],
            widths=BOX_WIDTH,
            vert=False,
            positions=np.array(range(len(tools))) * HEIGHT,
            patch_artist=True,
            boxprops={
                'facecolor': LIGHT_GRAY,
                'linewidth': 0,
            },
            whiskerprops={
                'color': DARKER_GRAY,
            },
            capprops={
                'color': DARKER_GRAY,
            },
            flierprops={
                'marker': 'o',
                'markersize': 5,
                'markerfacecolor': LIGHT_GRAY,
                'markeredgecolor': LIGHT_GRAY,
            },
            medianprops={
                'color': LIGHT_GRAY,
            },
        )
        if ins == 0:
            ax.set_yticks(np.array(range(len(tools))) * HEIGHT,
                          labels=list(map(lambda key: tools[key][0], tools)),
                          fontdict={'fontsize': 14})
        else:
            ax.set_yticks([])

        statistic_values = [whiskers.get_xdata() for whiskers in bp["whiskers"]]
        for it, tool in enumerate(tools):
            # Draw heat
            curr_data = data[f'{tool}-{feature["key"]}-{slice}']
            box_left = statistic_values[it*2][0]
            box_right = statistic_values[it*2+1][0]
            max_right = feature['settings'][f'xlim{ins}']
            step_size = max_right / HEAT_RESOLUTION
            for step in range(HEAT_RESOLUTION):
                cell_x = 0 + step * step_size
                if box_left - step_size <= cell_x <= box_right:
                    cell_left = max(box_left, cell_x)
                    cell_width = min(step_size, cell_x + step_size)

                    items_in_range = list(filter(lambda item: cell_left <= item['value'] < cell_left + cell_width, curr_data))
                    # Use recent two points to do interpolation
                    if len(items_in_range) == 0:
                        items_in_range.append(list(sorted(list(filter(lambda item: item['value'] < cell_left, curr_data)), key=lambda item: item['value']))[-1])
                        items_in_range.append(list(sorted(list(filter(lambda item: cell_left + cell_width < item['value'], curr_data)), key=lambda item: item['value']))[0])
                    avg_loc = sum([item['loc'] for item in items_in_range]) / len(items_in_range)

                    color = Color(GRADIENT_BASE)
                    getattr(color, f'set_{HEAT_COLOR_KEY}')(
                        getattr(color, f'get_{HEAT_COLOR_KEY}')() - HEAT_COLOR_DOWN * (avg_loc - heat_min) / heat_max[slice])
                    ax.add_patch(pch.Rectangle(
                        (cell_left, it - BOX_WIDTH / 2),
                        cell_width, BOX_WIDTH,
                        facecolor=color.web,
                        zorder=100,
                    ))
            # Draw flier
            cap_left = statistic_values[it*2][1]
            cap_right = statistic_values[it*2+1][1]
            for item in filter(lambda item: item['value'] < cap_left or cap_right < item['value'], curr_data):
                color = Color(GRADIENT_BASE)
                getattr(color, f'set_{HEAT_COLOR_KEY}')(
                    getattr(color, f'get_{HEAT_COLOR_KEY}')() - HEAT_COLOR_DOWN * (item['loc'] - heat_min) / heat_max[slice])
                # ax.add_patch(pch.Circle(
                #     (item['value'], it),
                #     color=color.web,
                #     zorder=100,
                # ))
                ax.plot(
                    [item['value']], [it],
                    marker='o',
                    color=color.web,
                )

# fig.tight_layout()

# plt.subplots_adjust(left=0.035, right=0.996, top=0.999, bottom=0.15)

if mode == 'save':
    fig.show()
else:
    fig.savefig(f'G:\\My Drive\\ASE 2022\\performance-python-v2.png')
