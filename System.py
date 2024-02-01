import json
from math import log
from numpy import random

class Mx_M_C:
    def __init__(self, lambda_:float, servers_count:int, mu:float) -> None:
        self.lambda_ = lambda_
        self.servers_count = servers_count
        self.mu = mu
        self.servers_states = [True for _ in range(servers_count)]
        self.demands = dict() 
        # {
        #   [id требования] : 
        #       [[время генерации], 
        #       [id пакета],
        #       [состояние = -1 - очередь, 0...servers_count-1 - номер прибора, servers_count - ожидает сборки]]
        # }
        self.last_state = 0
        self.states = {'0': 0}
        self.packs = 0
        self.export_demands()
        self.export_states()
    
    def arrival_time(self) -> float:
        return -log(random.random()) / self.lambda_

    def pack_size(self) -> int:
        return 3

    def service_time(self) -> float:
        return -log(random.random()) / self.mu
    
    def export_demands(self) -> None:
        with open(f'demands.json', 'w') as f:
            json.dump(self.demands, f)

    def export_states(self) -> None:
        with open(f'states.json', 'w') as f:
            json.dump(self.states, f)
    
    def import_demands(self) -> dict:
        with open(f'demands.json') as f:
            return json.load(f)

    def import_states(self) -> dict:
        with open(f'states.json') as f:
            return json.load(f)

    def current_demands(self) -> tuple:
        return (item for item in self.demands.keys())
    
    def update_time_states(self, t_now:float) -> None:
        self.states = self.import_states()

        # if len(states) <= len(self.demands):
        if len(self.states) <= self.packs:
            # states.extend([0] * (len(self.demands) - len(states) + 1))
            # states.update({state: 0 for state in range(len(states), len(self.demands) + 1)})
            self.states.update({str(state): 0 for state in range(len(self.states), self.packs + 1)})

        try:
            # states[len(self.demands)] += t_now - self.last_state
            self.states[str(self.packs)] += t_now - self.last_state
        except IndexError:
            print(self.states, len(self.states), len(self.demands), self.last_state)
            raise IndexError
        except KeyError:
            print(self.packs, self.states)
            raise KeyError

        self.last_state = t_now
        self.export_states()

