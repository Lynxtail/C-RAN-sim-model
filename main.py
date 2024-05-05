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
    
    samples_count = 10
    
    # ready_packs_count = 0 # число обслуженных пакетов
    ready_packs_count = [0]
    packs_count = [0]
    lost_packs_count = [0]

    # sum_packs_life_time = 0 # суммарная длительность пребывания всех обслуженных пакетов в системе
    sum_packs_life_time = [0] * samples_count
    
    subframes_count = [0]
    serviced_subframes_count = [0]
    lost_subframes_count = [0]
    
    time_for_plot = list()

    t_samples = tuple(np.linspace(0, t_max, samples_count))
    lambda_samples = tuple(np.linspace(system.lambda_, 10 * system.lambda_, samples_count))
    servers_count_samples = tuple(map(int, np.linspace(system.servers_count, system.servers_count * 3, samples_count)))
    print(t_samples, lambda_samples, servers_count_samples)
    pointer = 0

    while t < t_max: # происходит процесс имитации
        indicator = False # указывает на то, происходит сейчас какое-то событие или 
                          # нужно продвинуть модельное время
        print(f'{t}:')
        
        
        if t >= t_samples[pointer + 1]:
            print(f'При lambda = {system.lambda_} и {system.servers_count} приборах:')
            print(f'\tПакеты:\n\t\tполучено: {packs_count[-1]}\n\t\tобслужено: {ready_packs_count[-1]}\n\t\tпотеряно: {lost_packs_count[-1]}')
            print(f'\tСреднее время пребывания пакета в системе: {sum_packs_life_time[pointer] / ready_packs_count[-1] if ready_packs_count[-1] != 0 else 0}')
            print(f'\tФрагменты:\n\t\tполучено: {subframes_count[-1]}\n\t\tобслужено: {serviced_subframes_count[-1]}\n\t\tпотеряно {lost_subframes_count[-1]}')

            pointer += 1
            system.lambda_ = lambda_samples[pointer]
            if system.servers_count < servers_count_samples[pointer]:
                system.servers_states.append(True)
                schedule.append(t_max + 1)
            system.servers_count = servers_count_samples[pointer]
        
        print(f'Указатель на {pointer}\nПараметры lambda = {system.lambda_}, число приборов = {system.servers_count}')
        
        # генерация пакета
        if schedule[0] == t:
            indicator = True
            schedule[0] = t + system.arrival_time() # определение времени следующей генерации
            pack += 1 
            packs_count.append(pack)
            demands_count = system.pack_size(b) # определение размера пакета
            subframes_count.append(demands_count)
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
            serviced_subframes_count.append(serviced_subframes_count[-1] + 1)
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
                ready_packs_count.append(ready_packs_count[-1] + 1)
                sum_packs_life_time[pointer] += t - item[1][0]
            
            system.update_time_states(t)

        # если ни одно событие не произошло, то переход к новому моменту времени
        if not indicator:
            system.update_time_states(t)
            # print(schedule)
            time_for_plot.append(t)
            t = min(schedule)
            lost_packs_count.append(sum(packs_count) - sum(ready_packs_count))
            lost_subframes_count.append(sum(subframes_count) - sum(serviced_subframes_count))

        
        # system.export_demands()
        # system.demands.clear()

    print(f'\nВсего пакетов получено: {pack}')
    print(f'Обслужено пакетов: {sum(ready_packs_count)}')
    print(f'Среднее время пребывания пакета в системе: {sum(sum_packs_life_time) / sum(ready_packs_count) if sum(ready_packs_count) != 0 else 0}')
    with open('output.txt', 'w') as f:
        f.write(f'Оценка стационарного распределения вероятностей состояний системы:\n')
        [f.write(f'\tp(n = {n}) = {state / t_max}\n') for n, state in system.import_states().items()]
    print(f'Проверка оценки стационарного распределения: {sum([state / t_max for state in system.import_states().values()])}')

    plt.figure(1)
    plt.plot(servers_count_samples, [a / b if b != 0 else 0 for a, b in zip(lost_packs_count, packs_count)])
    plt.title(r'Зависимость $p_{lost}$ от количества приборов')
    plt.xlabel(r'количество приборов')
    plt.ylabel(r'$p_{lost}$')
    plt.savefig('servers+plost')

    plt.figure(2)
    plt.plot(lambda_samples, [a / b if b != 0 else 0 for a, b in zip(sum_packs_life_time, ready_packs_count)])
    plt.title(r'Зависимость $\overline{u}$ от $\lambda$')
    plt.xlabel(r'$\lambda$')
    plt.ylabel(r'$\overline{u}$')
    plt.savefig('lambda+lifetime')

if __name__ == "__main__":
    lambda_ = 1 / 10 # интенсивность входящего потока
    servers_count = 70 # число приборов
    mu = 1 / 281 # интенсивность обслуживания
    b = 5 # средний размер пакета
    service_time_threshold = 2000 # ограничение на время обслуживания пакета
    system = Mx_M_C(lambda_, servers_count, mu)
    simulation(system, b, service_time_threshold)