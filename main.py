import numpy as np
from System import Mx_M_C

# основная функция, осуществляющая моделирование
def simulation(system:Mx_M_C, b:float):
    t = 0 # текущее модельное время
    t_max = round(10**6 / lambda_) # максимальное модельное время
    # t_max = 10**2
    pack = 0 # номер очередного пакета
    schedule = [t_max + 1] * (system.servers_count + 1) # таблица расписания событий
    schedule[0] = 0 # генерация очередного требования произойдёт в момент времени 0
    ready_packs_count = 0 # число обслуженных пакетов
    sum_packs_life_time = 0 # суммарная длительность пребывания всех обслуженных пакетов в системе

    while t < t_max: # происходит процесс имитации
        indicator = False # указывает на то, происходит сейчас какое-то событие или 
                          # нужно продвинуть модельное время
        print(f'{t}:')
        # system.import_demands()
        
        # генерация пакета
        if schedule[0] == t:
            indicator = True
            schedule[0] = t + system.arrival_time() # определение времени следующей генерации
            pack += 1 
            demands_count = system.pack_size(b) # определение размера пакета
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
        
        # system.export_demands()
        # system.demands.clear()

    print(f'\nВсего пакетов получено: {pack}')
    print(f'Обслужено пакетов: {ready_packs_count}')
    print(f'Среднее время пребывания пакета в системе: {sum_packs_life_time / ready_packs_count}')
    with open('output.txt', 'w') as f:
        f.write(f'Оценка стационарного распределения вероятностей состояний системы:\n')
        [f.write(f'\tp(n = {n}) = {state / t_max}\n') for n, state in system.import_states().items()]
    print(f'Проверка оценки стационарного распредления: {sum([state / t_max for state in system.import_states().values()])}')

if __name__ == "__main__":
    lambda_ = 1 / 10 # интенсивность входящего потока
    servers_count = 150 # число приборов
    mu = 1 / 281 # интенсивность обслуживания
    b = 5 # средний размер пакета
    system = Mx_M_C(lambda_, servers_count, mu)
    simulation(system, b)