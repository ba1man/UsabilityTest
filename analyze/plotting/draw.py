import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.optimize import curve_fit

from pre import init


collection, tags, mode, langs, tools, metrics = init()

# Plotting
print('Start plotting')
plt.style.use('./my.mplstyle')


def xlabel_formatter(x, pos):
    if x >= 10**6:
        return '{:.1f}'.format(x / 10**6) + 'M'
    elif x >= 10**3:
        return '{:.1f}'.format(x / 10**3) + 'K'


def filter_time(lang, loc, subject, tool=None):
    indices = []
    for index, value in enumerate(subject):
        # Remove NaN points
        if np.isnan(value):
            indices.append(index)
        # Remove incorrect points
        if lang == 'java':
            if value < loc[index] * 100 / (5 * 10 ** 6) - 20:
                indices.append(index)
        elif lang == 'cpp':
            if tool == 'depends':
                if value < 50 / (5 * 10 ** 5) * loc[index]:
                    indices.append(index)
            else:
                if value < loc[index] * 100 / (5 * 10 ** 6) - 20:
                    indices.append(index)
        elif lang == 'python':
            if tool == 'sourcetrail':
                if value < 100 / (2 * 10 ** 5) * loc[index]:
                    indices.append(index)
            else:
                if value < 50 / (10**6-5*10**4) * (loc[index]-5*10*4):
                    indices.append(index)
        else:
            pass
    return np.delete(loc, indices), np.delete(subject, indices)


def filter_memory(lang, loc, subject, tool=None):
    indices = []
    # Default range
    range = [0, 3*10**6]
    for index, value in enumerate(subject):
        # Remove NaN points
        if np.isnan(value):
            indices.append(index)
        # Only track memory usage from LoC=2W, for all language
        if loc[index] < 2*10**4:
            indices.append(index)
        # Remove abnormal points and assign observation plot range
        if lang == 'java':
            if value < 1 / (1 * 10 ** 6) * loc[index]:
                indices.append(index)
            if tool == 'depends':
                range[0] = 1*10**5
            elif tool == 'understand':
                range[0] = 10**5
                if loc[index] < range[0]:
                    indices.append(index)
        elif lang == 'cpp':
            pass
        elif lang == 'python':
            if tool == 'enre':
                if value < 0.5 / (2 * 10 ** 5) * loc[index]:
                    indices.append(index)
        else:
            pass
    return np.delete(loc, indices), np.delete(subject, indices), np.linspace(range[0], range[1], 1000)


# The range used by drawing linear trend line for 'time'
trendx = np.array([0, 3*10**6])


def linear_func(fx, a, b):
    return a * fx + b


def power_func(fx, a, b, c):
    return a * fx ** b + c


def draw(lang, metric, loc, enre, depends, sourcetrail, understand):
    plt.figure(num=f'{lang}-{metric}')
    plt.xlabel('LoC')

    if lang == 'java' or lang == 'cpp' or lang == 'ts':
        plt.xlim([0, 2.25*10**6])
    else:
        plt.xlim([0, 1.1*10**6])

    if metric == 'time':
        plt.ylabel('Completion Time (s)')
        plt.ylim([0, 450])
    else:
        plt.ylabel('Peak Memory Usage (GB)')
        plt.ylim([0, 6])

    plt.gca().xaxis.set_major_formatter(xlabel_formatter)

    general_lw = 0.8
    general_s = 36
    general_m = '+'

    # ENRE
    e = plt.scatter(loc, enre, linewidths=general_lw, s=general_s, marker=general_m, c=tools['enre'][1])
    if metric == 'time':
        _loc, _enre = filter_time(lang, loc, enre, 'enre')
        res = sm.OLS(_enre, _loc).fit()
        plt.plot(trendx, res.params[0] * trendx, c=tools['enre'][1])
        print(f'Standard consumption on time for ENRE in {lang} is {res.params[0] * 10**6}s')
        print(f'R-squared value for ENRE in {lang}-{metric} is {res.rsquared}')
    else:
        _loc, _enre, _range = filter_memory(lang, loc, enre, 'enre')
        popt, pcov = curve_fit(power_func, _loc, _enre)
        plt.plot(_range, popt[0] * _range ** popt[1] + popt[2], c=tools['enre'][1])

    # Depends
    # d = plt.scatter(loc, depends, linewidths=general_lw, s=general_s, marker=general_m, c=tools['depends'][1])
    # if metric == 'time':
    #     _loc, _depends = filter_time(lang, loc, depends, 'depends')
    #     res = sm.OLS(_depends, _loc).fit()
    #     plt.plot(trendx, res.params[0] * trendx, c=tools['depends'][1])
    #     print(f'Standard consumption on time for Depends in {lang} is {res.params[0] * 10 ** 6}s')
    #     print(f'R-squared value for Depends in {lang}-{metric} is {res.rsquared}')
    # else:
    #     _loc, _depends, _range = filter_memory(lang, loc, depends, 'depends')
    #     popt, pcov = curve_fit(power_func, _loc, _depends)
    #     plt.plot(_range, popt[0] * _range ** popt[1] + popt[2], c=tools['depends'][1])

    # SourceTrail
    # s = plt.scatter(loc, sourcetrail, linewidths=general_lw, s=general_s, marker=general_m, c=tools['sourcetrail'][1])
    # if metric == 'time':
    #     _loc, _sourcetrail = filter_time(lang, loc, sourcetrail, 'sourcetrail')
    #     res = sm.OLS(_sourcetrail, _loc).fit()
    #     plt.plot(trendx, res.params[0] * trendx, c=tools['sourcetrail'][1])
    #     print(f'Standard consumption on time for SourceTrail in {lang} is {res.params[0] * 10 ** 6}s')
    #     print(f'R-squared value for SourceTrail in {lang}-{metric} is {res.rsquared}')
    # else:
    #     _loc, _sourcetrail, _range = filter_memory(lang, loc, sourcetrail, 'sourcetrail')
    #     popt, pcov = curve_fit(power_func, _loc, _sourcetrail, maxfev=5000)
    #     plt.plot(_range, popt[0] * _range ** popt[1] + popt[2], c=tools['sourcetrail'][1])

    # Understand
    u = plt.scatter(loc, understand, linewidths=general_lw, s=general_s, marker=general_m, c=tools['understand'][1])
    if metric == 'time':
        _loc, _understand = filter_time(lang, loc, understand, 'understand')
        res = sm.OLS(_understand, _loc).fit()
        plt.plot(trendx, res.params[0] * trendx, c=tools['understand'][1])
        print(f'Standard consumption on time for Understand in {lang} is {res.params[0] * 10 ** 6}s')
        print(f'R-squared value for Understand in {lang}-{metric} is {res.rsquared}')
    else:
        _loc, _understand, _range = filter_memory(lang, loc, understand, 'understand')
        popt, pcov = curve_fit(power_func, _loc, _understand)
        plt.plot(_range, popt[0] * _range ** popt[1] + popt[2], c=tools['understand'][1])

    # if mode == 'view':
    #     plt.title(f'{lang}-{metric}')
    plt.legend(handles=[e, u], labels=['ENRE', 'Depends', 'SourceTrail', 'Understand'], loc='upper right')
    plt.tight_layout()
    if mode == 'view':
        plt.show()
    else:
        plt.savefig(f'G:\\我的云端硬盘\\ASE 2022\\{metric}-{lang}.png')


for lang in langs:
    curr = collection[lang]
    for metric in ['time', 'memory']:
        draw(
            lang,
            metric,
            curr['loc'],
            curr[f'enre-{metric}'],
            curr[f'depends-{metric}'],
            curr[f'sourcetrail-{metric}'],
            curr[f'understand-{metric}']
        )
