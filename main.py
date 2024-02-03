import numpy as np
from System import Mx_M_C


def simulation(system:Mx_M_C, b:float):
    t = 0 # текущее модельное время
    t_max = 10*6 // round(lambda_) # максимальное модельное время
    pack = 0
    schedule = [t_max + 1] * (system.servers_count + 1)
    schedule[0] = 0
    ready_packs_count = 0
    sum_packs_life_time = 0

    while t < t_max: # происходит процесс имитации
        indicator = False
        print(f'{t}:')
        system.import_demands()
        
        if schedule[0] == t:
            indicator = True
            schedule[0] = t + system.arrival_time()
            pack += 1
            demands_count = system.pack_size(b)
            system.packs += 1
            print(f'\tПакет {pack} из {demands_count} требований поступил в систему')
            for i in range(1, demands_count + 1):
                system.demands[pack + i * 10 ** -(demands_count // 10 + 1)] = [t, pack, -1]
            system.update_time_states(t)
        
        if any(system.servers_states) and any([demand[-1] == -1 for demand in system.demands.values()]):
            indicator = True
            server = system.servers_states.index(True)
            system.servers_states[server] = False
            for demand in system.demands.keys():
                if system.demands[demand][-1] == -1:
                    system.demands[demand][-1] = server
                    break
            schedule[server + 1] = t + system.service_time()
            print(f'\tтребование {demand} начало обслуживаться на приборе {server + 1}')

        if any([process == t for process in schedule[1:]]):
            indicator = True
            server = schedule.index(t) - 1
            if server == -1:
                raise Exception
            system.servers_states[server] = True
            for serviced_demand in system.demands.keys():
                if system.demands[serviced_demand][-1] == server:
                    system.demands[serviced_demand][-1] = system.servers_count
                    break
            schedule[server + 1] = t_max + 1
            print(f'\tтребование {serviced_demand} завершило обслуживаться на приборе {server + 1} и ожидает сборки')

            # проверка: если все требования одного пакета ожидают сборки, то требование выходит из системы
            new_pack = list()
            for other_demand in system.demands.keys():
                if system.demands[other_demand][1] == system.demands[serviced_demand][1]:
                    new_pack.append((other_demand, system.demands[other_demand]))
            flag = True
            for item in new_pack:
                if item[1][-1] != system.servers_count:
                    flag = False
                    break
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

        if not indicator:
            system.update_time_states(t)
            print(schedule)
            t = min(schedule)
        
        system.export_demands()
        system.demands.clear()

    print(f'\nВсего пакетов получено: {pack}')
    print(f'Обслужено пакетов: {ready_packs_count}')
    print(f'Среднее время пребывания пакета в системе: {sum_packs_life_time / ready_packs_count}')
    with open('output.txt', 'w') as f:
        f.write(f'Оценка стационарного распределения вероятностей состояний системы:\n')
        [f.write(f'\tp(n = {n}) = {state / t_max}\n') for n, state in system.import_states().items()]
    print(f'Проверка оценки стационарного распредления: {sum([state / t_max for state in system.import_states().values()])}')

if __name__ == "__main__":
    lambda_ = 1 / 10
    servers_count = 150
    mu = 1 / 281
    b = 5
    system = Mx_M_C(lambda_, servers_count, mu)
    simulation(system, b)