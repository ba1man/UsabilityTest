import csv
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm


langs = ['cpp', 'java', 'python']
tools = ['enre', 'depends', 'sourcetrail', 'understand']
metrics = ['time', 'memory']

collection = {}

# Loading data
print('Start loading data...')
for lang in langs:
    print(f'Loading {lang} data')
    curr = collection[lang] = {}
    try:
        # Using 'sig' to suppress the BOM generated from Excel
        with open(f'../data/{lang}.csv', 'r', encoding='utf-8-sig') as file:
            data = csv.reader(file)
            curr['loc'] = []
            for tool in tools:
                for metric in metrics:
                    curr[f'{tool}-{metric}'] = []

            for row in data:
                curr['loc'].append(int(row[0]))
                c = 1
                for tool in tools:
                    for metric in metrics:
                        curr[f'{tool}-{metric}'].append(float(row[c]))
                        c += 1
    except EnvironmentError:
        print(f'No {lang}.csv file found, skipping to the next')
        continue
    # Convert to numpy array
    for key in curr.keys():
        if key != 'loc':
            curr[key] = np.array(curr[key])
            # Convert 0 or -1 to NaN
            curr[key][curr[key] == 0] = np.nan
            curr[key][curr[key] == -1] = np.nan

# Filtering
print('Start lang-relative filtering')

# Plotting
print('Start plotting')
plt.style.use('./my.mplstyle')
# for lang in langs:
#     curr = collection[lang]
#     for metric in metrics:
#         print(f'Plotting {lang}-{metric}')
#         plt.scatter(curr['loc'], curr[f'enre-{metric}'])
# plt.style.use(['science', 'no-latex'])


def xlabel_formatter(x, pos):
    if x >= 10**6:
        return '{:.0f}'.format(x / 10**6) + 'M'
    elif x >= 10**3:
        return '{:.0f}'.format(x / 10**3) + 'K'


def filter_time(lang, loc, subject):
    indices = []
    for index, value in enumerate(subject):
        # Remove NaN points
        if np.isnan(value):
            indices.append(index)
        # Remove incorrect points
        if lang == 'java':
            if value < loc[index] * 100 / (5*10**6) - 20:
                indices.append(index)
        elif lang == 'cpp':
            if value < loc[index] * 100 / (5 * 10 ** 6) - 20:
                indices.append(index)
        else:
            if loc[index] > 10**4 and value < 4:
                indices.append(index)
    return np.delete(loc, indices), np.delete(subject, indices)


trendx = np.array([0, 5*10**6])


def draw(lang, metric, loc, enre, depends, sourcetrail, understand):
    plt.figure(num=f'{lang}-{metric}', dpi=300)
    plt.xlabel('LoC')
    plt.ylabel('Completion Time (s)')
    if lang == 'java' or lang == 'cpp':
        plt.xlim([0, 4.5*10**6])
    else:
        plt.xlim([0, 1.1*10**6])
    plt.ylim([0, 450])
    plt.gca().xaxis.set_major_formatter(xlabel_formatter)
    # ENRE
    e = plt.scatter(loc, enre)
    _loc, _enre = filter_time(lang, loc, enre)
    res = sm.OLS(_enre, _loc).fit()
    plt.plot(trendx, res.params[0] * trendx)
    # Depends
    d = plt.scatter(loc, depends)
    _loc, _depends = filter_time(lang, loc, depends)
    res = sm.OLS(_depends, _loc).fit()
    plt.plot(trendx, res.params[0] * trendx)
    # SourceTrail
    s = plt.scatter(loc, sourcetrail)
    _loc, _sourcetrail = filter_time(lang, loc, sourcetrail)
    res = sm.OLS(_sourcetrail, _loc).fit()
    plt.plot(trendx, res.params[0] * trendx)
    # Understand
    u = plt.scatter(loc, understand)
    _loc, _understand = filter_time(lang, loc, understand)
    res = sm.OLS(_understand, _loc).fit()
    plt.plot(trendx, res.params[0] * trendx)

    # plt.title(f'{lang}-{metric}')
    plt.legend(handles=[e, d, s, u], labels=['ENRE', 'Depends', 'SourceTrail', 'Understand'], loc='upper right')
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'G:\\我的云端硬盘\\ASE 2022\\{metric}-{lang}.png')


for lang in langs:
    curr = collection[lang]
    for metric in ['time']:
        draw(
            lang,
            metric,
            curr['loc'],
            curr[f'enre-{metric}'],
            curr[f'depends-{metric}'],
            curr[f'sourcetrail-{metric}'],
            curr[f'understand-{metric}']
        )
