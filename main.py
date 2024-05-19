import sys
import os
import json
import numpy as np
from System import Mx_M_C
import matplotlib.pyplot as plt

# основная функция, осуществляющая моделирование
def simulation(system:Mx_M_C, b:float, service_time_threshold):
    t = 0 # текущее модельное время
    t_max = round(10**6 / lambda_) # максимальное модельное время
    t_max = 10**3
    pack = 0 # номер очередного пакета
    schedule = [t_max + 1] * (system.servers_count + 1) # таблица расписания событий
    schedule[0] = 0 # генерация очередного требования произойдёт в момент времени 0
     
    ready_packs_count = 0 # число обслуженных пакетов
    sum_packs_life_time = 0 # суммарная длительность пребывания всех обслуженных пакетов в системе
    
    lost_packs_count = 0 # число потерянных пакетов
    subframes_count = 0 # общее число фрагментов
    serviced_subframes_count = 0 # число обслуженных фрагментов
    lost_subframes_count = 0 # число потерянных фрагментов

    u_for_plots = [] # значения м.о. времени пребывания требования
    p_lost_for_plots = [] # значения вероятности потерь

    while t < t_max: # происходит процесс имитации
        indicator = False # указывает на то, происходит сейчас какое-то событие или 
                          # нужно продвинуть модельное время
        print(f'\n{t}:')
        # system.demands = system.import_demands()
        
        # генерация пакета
        if schedule[0] == t:
            indicator = True
            schedule[0] = t + system.arrival_time() # определение времени следующей генерации
            pack += 1 
            demands_count = system.pack_size(b) # определение размера пакета
            subframes_count += demands_count
            system.packs += 1
            print(f'\tПакет {pack} из {demands_count} требований поступил в систему')
            # создание требований из пакета
            for i in range(1, demands_count + 1):
                system.demands[pack + i * 10 ** -(demands_count // 10 + 1)] = [t, pack, -1]
            system.update_time_states(t)
        
        # начало обслуживание очередного требования из очереди
        if any(system.servers_states) and any([demand[-1] == -1 for demand in system.demands.values()]):
            indicator = True
            # определение номера свободного прибора
            server = system.servers_states.index(True)
            system.servers_states[server] = False
            # "привязка" взятого требования к этому прибору
            for demand in system.demands.keys():
                if system.demands[demand][-1] == -1:
                    system.demands[demand][-1] = server
                    break
            # определение времени завершения обслуживания
            schedule[server + 1] = t + system.service_time()
            print(f'\tтребование {demand} начало обслуживаться на приборе {server + 1}')

        # завершение обслуживания требования
        if any([process == t for process in schedule[1:]]):
            indicator = True
            server = schedule.index(t) - 1
            if server == -1:
                raise Exception
            system.servers_states[server] = True
            # переход требования в состояние "готово к сборке"
            for serviced_demand in system.demands.keys():
                if system.demands[serviced_demand][-1] == server:
                    system.demands[serviced_demand][-1] = system.servers_count
                    break
            schedule[server + 1] = t_max + 1
            serviced_subframes_count += 1
            print(f'\tтребование {serviced_demand} завершило обслуживаться на приборе {server + 1} и ожидает сборки')

            # проверка: если все требования одного пакета ожидают сборки, то требование выходит из системы

            # сборка всех требований одного пакета в список
            new_pack = list()
            for other_demand in system.demands.keys():
                if system.demands[other_demand][1] == system.demands[serviced_demand][1]:
                    new_pack.append((other_demand, system.demands[other_demand]))
            
            # проверка, все ли требования этого списка обслужились
            flag = True
            for item in new_pack:
                if item[1][-1] != system.servers_count:
                    flag = False
                    break
            
            # при успешной проверке, пакет покидает систему,
            # а его требования удаляются
            if flag:
                print('\tтребования:', end=' ')
                for item in new_pack:
                    print(f'{item[0]}', end=' ')
                    system.demands.pop(item[0])
                print(f'\n\tсобраны в пакет {item[1][1]} и покидают систему')
                system.packs -= 1
                ready_packs_count += 1
                sum_packs_life_time += t - item[1][0]
            
            system.update_time_states(t)

        # если ни одно событие не произошло, то переход к новому моменту времени
        if not indicator:
            system.update_time_states(t)
            # print(schedule)
            t = min(schedule)

            # проверка: если какие-то фрагменты обслуживаются дольше порога
            # то заносятся в список new pack
            new_pack = list()
            for demand in system.demands.keys():
                if t - system.demands[demand][0] > service_time_threshold:
                    new_pack.append(demand)
            # если new pack не пустой, то
            if new_pack:
                print('\tтребования:', end=' ')
                for item in new_pack:
                    if system.demands[item][-1] != -1 and system.demands[item][-1] != system.servers_count:
                        server = system.demands[item][-1]
                        try:
                            system.servers_states[server] = True
                            schedule[server + 1] = t_max + 1
                        except Exception:
                            print(server, system.servers_count, len(system.servers_states))
                            raise Exception
                    print(f'{item}', end=' ')
                    try:
                        system.demands.pop(item)
                        lost_subframes_count += 1
                    except KeyError:
                        print(new_pack)
                        raise KeyError
                print(f'\n\tтеряются')
                system.packs -= 1
                lost_packs_count += 1

            u_for_plots.append(sum_packs_life_time / ready_packs_count if ready_packs_count != 0 else 0)
            p_lost_for_plots.append(lost_packs_count / pack)
        # system.export_demands()

    lost_packs_count += system.packs
    lost_subframes_count += len(system.demands)

    print(f'\nВсего пакетов получено: {pack}')
    print(f'Обслужено пакетов: {ready_packs_count}')
    print(f'Потеряно пакетов: {lost_packs_count}')
    print(f'Среднее время пребывания пакета в системе: {sum_packs_life_time / ready_packs_count if ready_packs_count != 0 else 0}')
    print(f'\nВсего фрагментов получено: {subframes_count}')
    print(f'Обслужено фрагментов: {serviced_subframes_count}')
    print(f'Потеряно фрагментов: {lost_subframes_count}')
    with open('output.txt', 'w') as f:
        f.write(f'Оценка стационарного распределения вероятностей состояний системы:\n')
        sum_np = 0
        for n, state in system.import_states().items():
            p_tmp = state / t_max
            sum_np += int(n) * p_tmp
        f.write(f'\tp(n = {n}) = {p_tmp}\n')
    print(f'Проверка оценки стационарного распределения: {sum([state / t_max for state in system.import_states().values()])}')
    print(f'Среднее число фрагментов в системе: {sum_np}')

    results = {'lambda': lambda_,
               'kappa': kappa,
               'Total packages': pack,
               'Mean package lifetime': sum_packs_life_time / ready_packs_count if ready_packs_count != 0 else 0,
               'Serviced packages': ready_packs_count,
               'Lost packages': lost_packs_count,
               'Total jobs': subframes_count,
               'Serviced jobs': serviced_subframes_count,
               'Lost jobs': lost_subframes_count,
               'Mean jobs': sum_np,
               'u_for_plots': u_for_plots,
               'p_lost_for_plots': p_lost_for_plots}

    file = f'{round(lambda_, 3)}-{kappa}-{round(mu, 3)}-{b}-{service_time_threshold}.json'
    with open(f'out/{file}', 'w') as f:
        json.dump(results, f)
    
    print('\n\nDone!')
    exit()

if len(sys.argv) == 1:
    lambda_ = 1 / 10 # интенсивность входящего потока
    kappa = 70 # число приборов
    kappa = 0 # число приборов
    mu = 1 / 281 # интенсивность обслуживания
    b = 1 # средний размер пакета
    service_time_threshold = 100 # ограничение на время обслуживания пакета
else:
    lambda_ = float(sys.argv[1]) # интенсивность входящего потока
    kappa = int(float(sys.argv[2])) # число приборов
    mu = float(sys.argv[3]) # интенсивность обслуживания
    b = float(sys.argv[4]) # средний размер пакета
    service_time_threshold = float(sys.argv[5]) # ограничение на время обслуживания пакета
system = Mx_M_C(lambda_, kappa, mu)
simulation(system, b, service_time_threshold)