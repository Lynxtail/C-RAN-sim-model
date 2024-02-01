import numpy as np
from System import Mx_M_C

def calculate_characteristics(pack:int, ready_packs_count:int, sum_packs_life_time:float, t:float):
    print(f'\nВсего пакетов получено: {pack}')
    # print(f'Обслужено пакетов: {ready_packs_count}')
    # print(f'Оценка стационарного распределения вероятностей состояний системы:')
    # [print(f'') for ]

def simulation(system:Mx_M_C):
    t = 0 # текущее модельное время
    t_max = 10**4 # максимальное модельное время
    pack = 0
    schedule = [t_max + 1] * (system.servers_count + 1)
    schedule[0] = 0
    ready_packs_count = 0
    sum_packs_life_time = 0

    while t < t_max: # происходит процесс имитации
        indicator = False
        print(f'{t}:')

        if schedule[0] == t:
            indicator = True
            schedule[0] = t + system.arrival_time()
            pack += 1
            demands_count = system.pack_size()
            print(f'\tПакет {pack} из {demands_count} требований поступил в систему')
            for i in range(demands_count):
                system.demands[i] = [t, pack, 0]
        
        if any(system.servers_states) and len(system.demands) > 0:
            indicator = True
            server = system.servers_states.index(True)
            system.servers_states[server] = False
            for demand in system.demands.keys():
                if system.demands[demand][-1] == 0:
                    system.demands[demand][-1] = server
                    break
            schedule[server] = t + system.service_time()
            print(f'\tтребование {demand} начало обслуживаться на приборе {server}')

        if any(schedule[1:] == t):
            indicator = True
            server = schedule[1:].index(t)
            system.servers_states[server] = True
            for serviced_demand in system.demands.keys():
                if system.demands[serviced_demand][-1] == server:
                    system.demands[serviced_demand][-1] = system.servers_count + 1
                    break
            schedule[server] = t_max + 1
            print(f'\tтребование {serviced_demand} завершило обслуживаться на приборе {server} и ожидает сборки')

            # проверка: если все требования одного пакета ожидают сборки, то требование выходит из системы
            new_pack = list()
            for other_demand in system.demands.keys():
                if system.demands[other_demand][1] == system.demands[serviced_demand][1]:
                    new_pack.append((other_demand, system.demands[other_demand]))
            flag = True
            for item in new_pack:
                if item[1][-1] != system.servers_count + 1:
                    flag = False
                    break
            if flag:
                print('\tтребования', end='')
                for item in new_pack:
                    print(f', {item[0]}', end='')
                    system.demands.pop(item[0])
                print(f'\n\tсобраны в пакет {item[1][1]} и покидают систему')
                system.update_time_states(t)
                ready_packs_count += 1
                sum_packs_life_time += t - item[1][0]
        
        if not indicator:
            system.update_time_states(t)
            t = min(schedule)

        print(f'\nВсего пакетов получено: {pack}')
        print(f'Обслужено пакетов: {ready_packs_count}')
        print(f'Оценка стационарного распределения вероятностей состояний системы:')
        [print(f'\t{n}: {state}') for n, state in enumerate(system.import_states())]

        # return pack, ready_packs_count, sum_packs_life_time, t

if __name__ == "__main__":
    lambda_ = 1
    servers_count = 1
    mu = 1
    system = Mx_M_C(lambda_, servers_count, mu)
    simulation(system)
    # pack, ready_packs_count, sum_packs_life_time, t = simulation(system)
    # calculate_characteristics(simulation(system))