import json
import numpy as np
from math import log
from numpy import random
import scipy.stats


class Mx_M_C:

    # конструктор
    def __init__(self, lambda_:float, servers_count:float, mu:float) -> None:
        self.lambda_ = lambda_
        self.servers_count = servers_count
        self.servers_states = [True for _ in range(self.servers_count)]
        self.mu = mu
        self.demands = dict() 
        # требования описываются в виде элементов словаря:
        # {
        #   [id требования] : 
        #       [[время генерации], 
        #       [id пакета],
        #       [состояние = -1 - очередь, 0...servers_count-1 - номер прибора, servers_count - ожидает сборки]]
        # }
        self.last_state = 0 # момент времени, когда система закончила прибывать в предыдущем состоянии
        self.states = {'0': 0} # суммарные длительности пребывания системы в соответствующих состояниях
        self.packs = 0 # число пакетов в системе -- её состояние
        self.export_demands()
        self.export_states()


    # функции генерации случайных величин
    # ------------------------------------------------------------------
    # случайные величины генерируются методом обратного преобразования
    
    # промежуток времени между поступлением двух требований:
    # экспоненциальное распределение с параметром лямбда
    def arrival_time(self) -> float:
        random.seed()
        return -log(random.random()) / self.lambda_
    
    # время обслуживания требования:
    # экспоненциальное распределение с параметром мю
    def service_time(self) -> float:
        random.seed()
        return -log(random.random()) / self.mu

    # случайные величины генерируются методом обратного преобразования
    # размер поступившего пакета:
    # геометрическое распределение, b - средний размер пакета
    # def pack_size(self, b:float) -> int:
    #     random.seed()
    #     y = random.random()
    #     k = 1
    #     p = 1 - 1 / b
    #     q = 1 - p
    #     prod = p * q
    #     sum_ = p + prod
    #     while (y > sum_):
    #         prod *= q
    #         sum_ += prod
    #         k += 1
    #     return k

    # случайные величины генерируются библиотекой random
    # геометрическое распределение, b - средний размер пакета
    def pack_size(self, b:float) -> int:
        return random.geometric(1 / b)

    # запись данных о требованиях в файл
    def export_demands(self) -> None:
        with open(f'demands.json', 'w') as f:
            json.dump(self.demands, f)

    # запись данных о состояниях в файл
    def export_states(self) -> None:
        with open(f'states.json', 'w') as f:
            json.dump(self.states, f)
    
    # получение данных о требованиях из файла
    def import_demands(self) -> dict:
        with open(f'demands.json') as f:
            return json.load(f)

    # получение данных о состояних из файла
    def import_states(self) -> dict:
        with open(f'states.json') as f:
            return json.load(f)

    # перечисление текущих требований в системе
    def current_demands(self) -> tuple:
        return (item for item in self.demands.keys())
    
    # обновление данных о состояниях
    def update_time_states(self, t_now:float) -> None:
        self.states = self.import_states()

        if len(self.states) <= self.packs:
            self.states.update({str(state): 0 for state in range(len(self.states), self.packs + 1)})

        try:
            self.states[str(self.packs)] += t_now - self.last_state
        except IndexError:
            print(self.states, len(self.states), len(self.demands), self.last_state)
            raise IndexError
        except KeyError:
            print(self.packs, self.states)
            raise KeyError

        self.last_state = t_now
        self.export_states()

