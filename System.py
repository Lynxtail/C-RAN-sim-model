import json
from math import log
from numpy import random

class Mx_M_C:
    def __init__(self, id:int, servers_count:int, mu:float, gamma:float, state:bool=True, k_mu:int=1, k_gamma:int=1) -> None:
        self.servers_count = servers_count
        self.mu = mu
        self.servers_states = [True for _ in range(servers_count)]
        self.demands = dict() 
        # {
        #   [id требования] : 
        #       ([время генерации], 
        #       [id пакета],
        #       [состояние = 0 - очередь, ... - номер прибора, servers_count+1 - ожидает сборки])
        # }
        self.last_state = 0
        self.states = [0]
    
    def service_time(self):
        return -log(random.random()) / self.mu
    
    def export_demands(self):
        with open(f'demands.json', 'wb') as f:
            json.dump(self.demands, f)

    def export_states(self):
        with open(f'states.json', 'wb') as f:
            json.dump(self.states, f)
    
    def import_demands(self):
        with open(f'demands.json', 'rb') as f:
            return json.load(f)

    def import_states(self):
        with open(f'states.json', 'rb') as f:
            return json.load(f)

    def current_demands(self):
        return [item for item in self.demands.keys()]
    
    def update_time_states(self, t_now:float):
        states = self.import_states()

        if len(states) <= len(self.demands) + 1:
            states.extend([0])

        states[len(self.demands)] += t_now - self.last_state
        self.last_state = t_now
        self.export_states()

