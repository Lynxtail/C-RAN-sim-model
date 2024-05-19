import json
import os
import os.path
import numpy as np
import subprocess
import matplotlib.pyplot as plt

# ввод параметров
samples = 10
# параметры по умолчанию
lambda_ = np.linspace(1/10, 1/10, samples)
kappa = np.linspace(70, 70, samples)
# изменяемые параметры
lambda_ = np.linspace(1/20, 1/5, samples)
# kappa = np.linspace(0, 150, samples)

# неизменяемые параметры
mu = np.linspace(1 / 281, 1 / 281, samples)
b = np.linspace(1, 1, samples)
service_time_threshold = np.linspace(100, 100, samples)

if 'out' not in os.listdir():
    os.mkdir('out')
else:
    for file in os.listdir('out'):
        os.remove(os.path.join('out', file))

if lambda_[0] != lambda_[-1]:
    focus_parameter = 'lambda'
    for i in range(samples):
        subprocess.run(['python3', 'main.py', str(lambda_[i]), str(kappa[i]), str(mu[i]), str(b[i]), str(service_time_threshold[i])])
elif kappa[0] != kappa[-1]:
    focus_parameter = 'kappa'
    for i in range(samples):
        subprocess.run(['python3', 'main.py', str(lambda_[i]), str(kappa[i]), str(mu[i]), str(b[i]), str(service_time_threshold[i])])
else:
    subprocess.run(['python3', 'main.py', str(lambda_[0]), str(kappa[0]), str(mu[0]), str(b[0]), str(service_time_threshold[0])])

lambdas = []
kappas = []
mus = []
bs = []
thresholds = []
files = []

# собираем все использованные значения параметров
for item in os.listdir('out'):
    files.append(item)
    tmp_lambda, tmp_kappa, tmp_mu, tmp_b, tmp_service_time_threshold = tuple(map(float, item[:-5].split('-')))
    lambdas.append(tmp_lambda)
    kappas.append(tmp_kappa)
    mus.append(tmp_mu)
    bs.append(tmp_b)
    thresholds.append(tmp_service_time_threshold)
lambdas = sorted(lambdas)
kappas = sorted(kappas)
mus = sorted(mus)
bs = sorted(bs)
thresholds = sorted(thresholds)
files = sorted(files)

# загрузка всех результатов
results_list = []
counter = 0
# for parameter in (lambdas, kappas, mus, bs, thresholds):
for file in files:
    try:
        print(f'open {file}')
        results = dict()
        with open(os.path.join('out', file)) as f:
            print(f'read {file}')
            results = json.load(f)
            print(f'close {file}')
        results_list.append(results)
        print(f'{file} — done')
        counter += 1
    except Exception:
        print(f'{file} — error')
        raise Exception
print(f'Total: {counter}/{len(files)}\n')


results_list = sorted(results_list, key=lambda item: item[focus_parameter])

lost_packs_count = []
packs_count = []
mean_packs_life_time = []
u_for_plots = []
p_lost_for_plots = []
for results in results_list:
    lost_packs_count.append(results['Lost packages'])
    packs_count.append(results['Total packages'])
    mean_packs_life_time.append(results['Mean package lifetime'])
    u_for_plots.append(results['u_for_plots'])
    p_lost_for_plots.append(results['p_lost_for_plots'])
    t_max = results['t_max']
    print(f"\nlambda = {results['lambda']}, kappa = {results['kappa']}")
    print(f"\tLost packages: {results['Lost packages']}")
    print(f"\tTotal packages: {results['Total packages']}")
    print(f"\tMean package lifetime: {results['Mean package lifetime']}")
print(f'Results sorted by {focus_parameter}')




plt.rcParams.update({'font.size' : 10})
if kappa[0] != kappa[-1]:
    plt.figure(1)
    plt.plot(kappas, [a / b if b != 0 else 0 for a, b in zip(lost_packs_count, packs_count)])
    plt.title(r'Зависимость $p_{lost}$ от количества приборов')
    plt.xlabel(r'$\kappa$')
    plt.ylabel(r'$p_{lost}$')
    plt.grid(True)
    plt.savefig('kappa+plost.png', format='png', dpi=1000.)

    plt.figure(2)
    plt.grid(True)
    for i in range(len(p_lost_for_plots)):
        time_for_plot = np.linspace(0, t_max, len(p_lost_for_plots[i]))
        plt.plot(time_for_plot, p_lost_for_plots[i], label=r'$\kappa = $' + f'{kappas[i]}')
    plt.legend()
    plt.title(r'Изменение $p_{lost}$ в течение времени $t$')
    plt.xlabel(r'$t$')
    plt.ylabel(r'$p_{lost}$')
    plt.savefig('p_lost_for_all_kappas.png', format='png', dpi=1000.)

if lambda_[0] != lambda_[-1]:
    plt.figure(3)
    plt.grid(True)
    plt.plot(lambdas, [a for a in mean_packs_life_time])
    plt.title(r'Зависимость $\overline{u}$ от $\lambda$')
    plt.xlabel(r'$\lambda$')
    plt.ylabel(r'$\overline{u}$')
    plt.savefig('lambda+lifetime.png', format='png', dpi=1000.)

    plt.figure(4)
    plt.grid(True)
    plt.title(r'Изменение $\overline{u}$ в течение времени $t$')
    for i in range(len(u_for_plots)):
        time_for_plot = np.linspace(0, t_max, len(u_for_plots[i]))
        plt.plot(time_for_plot, u_for_plots[i], label=r'$\lambda = $' + f'{lambdas[i]}')
    plt.legend(loc='lower right')
    plt.xlabel(r'$t$')
    plt.ylabel(r'$\overline{u}$')
    plt.savefig('lifetime_for_all_lambdas.png', format='png', dpi=1000.)

