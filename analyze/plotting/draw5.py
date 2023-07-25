from colour import Color
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch
import math

from pre2 import init

collection, tags, mode, langs, tools, metrics = init()
features = [{'key': 'time', 'text': 'Completion Time (s)', 'settings': {'xlim0': 25, 'xlim1': 600}},
            {'key': 'memory', 'text': 'Peak Memory Usage (GB)', 'settings': {'xlim0': 1.0, 'xlim1': 3}}]
SLICE_POINT = 10 * 1000  # kLoC that divide the whole data set into two parts

# Adjust drawing order
tools = {
    'enre-cfg': ['PyAnalyzer_ful'],
    'enre': ['PyAnalyzer_lgt'],
    'pycg': ['PyCG'],
    'pysonar2': ['PySonar2'],
    'enre-old': ['ENRE19'],
    'depends': ['Depends'],
    'sourcetrail': ['Sourcetrail'],
    'understand': ['Understand'],
}

# Draw Variables
HEIGHT = 1
BOX_WIDTH = 0.6
LIGHT_GRAY = '#f0f0f0'
DARKER_GRAY = '#9f9f9f'
GRADIENT_BASE = '#80bfff'
HEAT_RESOLUTION = 300
HEAT_COLOR_DOWN = [-0.45, 0.4]  # Smaller is brighter (if apply to luminance)
HEAT_COLOR_KEY = ['hue', 'luminance']
LOC_LABEL_FONT_SIZE = 12


def cmapping(percentage):
    color = Color(GRADIENT_BASE)
    for ih, _ in enumerate(HEAT_COLOR_KEY):
        getattr(color, f'set_{HEAT_COLOR_KEY[ih]}')(
            getattr(color, f'get_{HEAT_COLOR_KEY[ih]}')() - HEAT_COLOR_DOWN[ih] * percentage)
    return color.web


plt.style.use('./my.mplstyle')

lang = langs[0]  # Should be Python only

fig = plt.figure(figsize=(17, 8))
subs = fig.subfigures(len(features), 1)
axs = []
for i, _ in enumerate(features):
    subs[i].subplots(1, 3, width_ratios=[40, 1, 40])
    subs[i].subplots_adjust(wspace=0.11)
    subs[i].suptitle(features[i]['text'], weight='bold')
    axs.append([subs[i].axes[0], subs[i].axes[2], subs[i].axes[1]])

    heat_indicator = subs[i].axes[1]
    heat_indicator.set_xticks([0.5], ['kLoC'], fontdict={'fontsize': LOC_LABEL_FONT_SIZE})
    for i in range(HEAT_RESOLUTION):
        color = Color(GRADIENT_BASE)
        for ih, _ in enumerate(HEAT_COLOR_KEY):
            getattr(color, f'set_{HEAT_COLOR_KEY[ih]}')(
                getattr(color, f'get_{HEAT_COLOR_KEY[ih]}')() - HEAT_COLOR_DOWN[ih] * i / HEAT_RESOLUTION)
        heat_indicator.add_patch(pch.Rectangle(
            (0, i / HEAT_RESOLUTION),
            1, 1 / HEAT_RESOLUTION,
            facecolor=color.web,
        ))
        heat_indicator.set_ylim(0, 1)
        heat_indicator.set_yticks([0, 0.5, 1], labels=[0, int(SLICE_POINT/2000), int(SLICE_POINT/1000)], fontdict={'fontsize': LOC_LABEL_FONT_SIZE})
        heat_indicator.twinx().set_yticks([0, 0.5, 1], labels=[int(SLICE_POINT/1000), int((750*1000-SLICE_POINT)/2000), 750],
                                          fontdict={'fontsize': LOC_LABEL_FONT_SIZE})

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
        ax.set_ylim([-0.5, 7.8])
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

        statistic_values = [whisker.get_xdata() for whisker in bp['whiskers']]
        medians = [median.get_xdata() for median in bp['medians']]
        for it, tool in enumerate(tools):
            # Draw heat
            curr_data = data[f'{tool}-{feature["key"]}-{slice}']
            whisker_left = statistic_values[it * 2][1]
            box_left = statistic_values[it * 2][0]
            box_right = statistic_values[it * 2 + 1][0]
            whisker_right = statistic_values[it * 2 + 1][1]
            max_right = feature['settings'][f'xlim{ins}']
            step_size = max_right / HEAT_RESOLUTION
            for step in range(HEAT_RESOLUTION):
                cell_x = 0 + step * step_size
                drawing_types = []
                if box_left - step_size <= cell_x <= box_right:
                    drawing_types.append('box')
                if whisker_left - step_size <= cell_x <= box_left:
                    drawing_types.append('line-left')
                if box_right - step_size <= cell_x <= whisker_right:
                    drawing_types.append('line-right')

                if len(drawing_types) != 0:
                    for drawing_type in drawing_types:
                        if drawing_type == 'box':
                            cell_left = max(box_left, cell_x)
                            cell_width = min(box_right - cell_x, cell_x + step_size, box_right - box_left)
                        elif drawing_type == 'line-left':
                            cell_left = max(whisker_left, cell_x)
                            cell_width = min(box_left - cell_x, cell_x + step_size, box_left - whisker_left)
                        elif drawing_type == 'line-right':
                            cell_left = max(box_right, cell_x)
                            cell_width = min(whisker_right - cell_x, cell_x + step_size, whisker_right - box_right)

                        items_in_range = list(
                            filter(lambda item: cell_left <= item['value'] < cell_left + cell_width, curr_data))
                        # Use recent two points to do interpolation
                        if len(items_in_range) == 0:
                            try:
                                items_in_range.append(list(
                                    sorted(list(filter(lambda item: item['value'] < cell_left, curr_data)),
                                           key=lambda item: item['value']))[-1])
                                items_in_range.append(list(
                                    sorted(list(filter(lambda item: cell_left + cell_width < item['value'], curr_data)),
                                           key=lambda item: item['value']))[0])
                            except IndexError:
                                pass
                        avg_loc = sum([item['loc'] for item in items_in_range]) / len(items_in_range)
                        color = cmapping((avg_loc - heat_min) / heat_max[slice])
                        if drawing_type == 'box':
                            ax.add_patch(pch.Rectangle(
                                (cell_left, it - BOX_WIDTH / 2),
                                cell_width, BOX_WIDTH,
                                facecolor=color,
                                zorder=100,
                            ))
                        elif drawing_type.startswith('line'):
                            ax.plot(
                                [cell_left, cell_left + cell_width],
                                [it, it],
                                color=color,
                                zorder=100,
                            )
            # Draw median
            median = medians[it][0]
            if not math.isnan(median) and tool != 'pycg':
                ax.add_patch(pch.Rectangle(
                    (median, it - BOX_WIDTH / 2),
                    max_right / 300, BOX_WIDTH,
                    facecolor='white',
                    zorder=101,
                ))
                if feature['key'] == 'time':
                    median_txt = round(median, 1)
                else:
                    median_txt = round(median, 2)
                ax.text(
                    median, it + 0.3,
                    median_txt,
                    size=10,
                    ha='left',
                    va='bottom',
                    zorder=9999,
                    color=DARKER_GRAY,
                    weight='bold',
                )
            # Draw flier
            cap_left = statistic_values[it * 2][1]
            cap_right = statistic_values[it * 2 + 1][1]
            for item in filter(lambda item: item['value'] < cap_left or cap_right < item['value'], curr_data):
                ax.plot(
                    [item['value']], [it],
                    marker='o',
                    color=cmapping((item['loc'] - heat_min) / heat_max[slice]),
                )
            # Draw indicator for fliers that are out of bound
            outers = list(filter(lambda item: item['value'] > max_right, curr_data))
            if len(outers) != 0:
                outers_avg_loc = sum([item['loc'] for item in outers]) / len(outers)
                t = ax.text(
                    max_right * 99 / 100, it,
                    f' +{len(outers)} ',
                    size=10,
                    ha='right',
                    va='center',
                    zorder=9999,
                    color='white',
                    weight='bold',
                )
                t.set_bbox({
                    'facecolor': cmapping((item['loc'] - heat_min) / heat_max[slice]),
                    'linewidth': 0,
                    'boxstyle': 'round,pad=0.1,rounding_size=0.6',
                })
                upto = list(sorted([item["value"] for item in outers]))[-1]
                if feature['key'] == 'time':
                    if slice == 'higher':
                        upto = int(round(upto / 100, 0) * 100)
                    else:
                        upto = int(upto)
                else:
                    upto = round(upto, 1)
                ax.text(
                    max_right * 101 / 100, it,
                    f'Up to\n{upto}',
                    size=10,
                    ha='left',
                    va='center',
                    zorder=9999,
                    color=DARKER_GRAY,
                    weight='bold',
                )
            # PyCG Special
            if tool == 'pycg':
                gray_box_start = list(sorted(curr_data, key=lambda item: item['value']))[-1]['value'] if slice == 'lower' else 0
                ax.add_patch(pch.Rectangle(
                    (0, it - BOX_WIDTH / 2),
                    max_right, BOX_WIDTH,
                    facecolor=LIGHT_GRAY,
                    edgecolor='white',
                    hatch='/////',
                ))


if mode == 'view':
    fig.show()
else:
    fig.savefig(f'G:\\My Drive\\ASE 2022\\performance-python-v2.png')
