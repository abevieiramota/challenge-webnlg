import os
import itertools
import math


def n_cr(n, r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)


listfiles = os.listdir(".")
# print(listfiles)


def significance_testing(metric, t):
    score = metric + '3ref-'    # "ter3ref-"
    cattype = '-' + t + '.blocks'    # new-cat, old-cat, all-cat
    finallistfiles = [item for item in listfiles if (item.startswith(score) and item.endswith(cattype))]
    finallistfiles.sort()

    system_blockbleu = {}
    for item in finallistfiles:
        system = item[len(score):(-1)*len(cattype)]
        # print(system)
        data = [float(line.split()[-1]) for line in open(item).read().strip().split("\n")]
        # print(len(data))
        # print(data)
        system_blockbleu[system] = data

    # Consider pairs of systems
    systems = list(system_blockbleu)
    systems.sort()
    combinations = list(itertools.combinations(systems, 2))
    # print(combinations)
    out = 'Results for ' + metric + ' ' + t + '\n\n'
    for item in combinations:
        # print(item)

        n = len(system_blockbleu[item[0]])

        # Find K, times first systems performs better than second
        k = 0
        for bidx in range(n):
            if system_blockbleu[item[0]][bidx] > system_blockbleu[item[1]][bidx]:
                k += 1
        # print(k)

        # sumpart
        sumpart = 0
        for i in range(k + 1):
            sumpart += n_cr(n, i)
        # print(sumpart)

        p = float(sumpart)/math.pow(2, n)
        # print(p)

        if (p < 0.05) or (p > 0.95):
            statement = '{} SIGNIFICANT-DIFFERENCE {} {}'.format(item, k, round(p, 4))
            print(statement)
            out += statement + '\n'
        else:
            statement = '{} NO-SIGNIFICANT-DIFFERENCE {} {}'.format(item, k, round(p, 4))
            print(statement)
            out += statement + '\n'

    with open('results-' + metric + '-' + t + '.txt', 'w+') as f:
        f.write(out)


types = ['all-cat', 'new-cat', 'old-cat']
metrics = ['bleu', 'meteor', 'ter']

for t in types:
    for metric in metrics:
        significance_testing(metric, t)
