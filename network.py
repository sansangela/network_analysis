import random
import numpy as np
from scipy.stats import weibull_min, uniform, pareto
from collections import deque



class Network:
    def __init__(self, num_nodes, distribution_type, distribution_params=None):
        self.num_nodes = num_nodes
        self.distribution_type = distribution_type
        self.distribution_params = distribution_params
        self.initialize_capacity()

    def initialize_capacity(self):
        L_distribution_type, S_distribution_type = self.distribution_type["L"], self.distribution_type["S"]

        ## Initialize L
        if L_distribution_type == 'weibull':
            if self.distribution_params is None:
                raise ValueError("Weibull distribution requires distribution parameters.")

            L_min = self.distribution_params['L_min']
            lam = self.distribution_params['lambda']
            k = self.distribution_params['k']

            # Generate Weibull-distributed L values
            self.L_values = weibull_min.rvs(c=k, loc=L_min, scale=lam, size=self.num_nodes)

        elif L_distribution_type == 'uniform':
            if self.distribution_params is None:
                raise ValueError("Uniform distribution requires distribution parameters.")

            L_min = self.distribution_params['L_min']
            L_max = self.distribution_params['L_max']

            # Generate uniform-distributed L values
            self.L_values = uniform.rvs(loc=L_min, scale=L_max - L_min, size=self.num_nodes)
        
        elif L_distribution_type == 'pareto':
            if self.distribution_params is None:
                raise ValueError("Pareto distribution requires distribution parameters.")

            L_min = self.distribution_params['L_min'] 
            b = self.distribution_params['b'] 

            # Generate pareto-distributed L values
            self.L_values = pareto.rvs(b, scale=L_min, size=self.num_nodes)

        ## Initialize S
        if S_distribution_type == 'linear':
            if self.distribution_params is None:
                raise ValueError("Weibull distribution requires distribution parameters.")

            # Generate linear S values
            alpha = self.distribution_params['alpha']
            self.S_values = alpha * self.L_values

        elif S_distribution_type == 'uniform':
            if self.distribution_params is None:
                raise ValueError("Uniform distribution requires distribution parameters.")

            S_min = self.distribution_params['S_min']
            S_max = self.distribution_params['S_max']

            # Generate uniform-distributed S values
            # self.S_values = uniform.rvs(loc=S_min, scale=S_max - S_min, size=self.num_nodes)  # scipy.stats uniform
            self.S_values = np.random.uniform(S_min, S_max, self.num_nodes)                     # numpy uniform
        
        else:
            raise ValueError("Invalid distribution type.")

        # Calculate C values
        self.C_values = self.L_values + self.S_values

    def generate_fail_nodes(self, p):
        fail_node_list = []
        fail_node_initial = []
        fail_node_size = np.floor(p*self.num_nodes)

        if fail_node_size == 0:
            print("Zero initial failure in network.")
            return fail_node_list
        
        fail_node_initial = random.sample(range(0,self.num_nodes), int(fail_node_size))
        fail_node_list = self.update_network(fail_node_initial)
        fail_node_list = fail_node_list + fail_node_initial
        return fail_node_list

    
    def update_network(self, fail_nodes):
        fail_load = 0.0
        for node in fail_nodes:
            self.C_values[node] = 0
            fail_load += self.L_values[node]
            self.L_values[node] = 0
        fail_node_list = self.redistribute_load(fail_load)
        return fail_node_list

    def redistribute_load(self, fail_load):
        fail_node_list = []

        while fail_load != 0:
            num_remaining = np.count_nonzero(self.L_values)

            if num_remaining == 0:
                # print("Network vanished...")
                return fail_node_list
            
            extra_load_per_node = 1.0 * fail_load / num_remaining
            fail_load = 0

            for i in range(self.num_nodes):     #TODO: Optimize
                if self.C_values[i] != 0:
                    self.L_values[i] += extra_load_per_node
                    if self.L_values[i] >= self.C_values[i]:
                        # Overload -> fail next time ??
                        fail_load += self.L_values[i]
                        fail_node_list.append(i)
                        self.L_values[i] = 0
                        self.C_values[i] = 0

        return fail_node_list

            

def test(N, p, distribution_A, params_A, distribution_B, params_B):
    network_A = Network(N, distribution_A, params_A)
    network_B = Network(N, distribution_B, params_B)

    # Init Failure
    fail_node_list = network_A.generate_fail_nodes(p)

    num_iter = 0
    old_num_remaining_A, old_num_remaining_B = 0, 0
    num_remaining_A, num_remaining_B = N, N

    while num_remaining_A > 0 and num_remaining_B > 0 and (old_num_remaining_A != num_remaining_A or old_num_remaining_B != num_remaining_B):
        num_iter += 1
        
        old_num_remaining_A, old_num_remaining_B = num_remaining_A, num_remaining_B

        # Redistribute in Network B
        fail_node_list = network_B.update_network(fail_node_list)
        num_remaining_B = np.count_nonzero(network_B.L_values)

        # Redistribute in Network A
        fail_node_list = network_A.update_network(fail_node_list)
        num_remaining_A = np.count_nonzero(network_A.L_values)

        if num_remaining_A == 0 and num_remaining_B == 0:
            # print("Network vanished...")
            return num_iter, num_remaining_A/N, num_remaining_B/N
    
    return num_iter, num_remaining_A/N, num_remaining_B/N



def main(N, case_A, case_B, num_experiments, p_array, distribution_A, params_A, distribution_B, params_B):
    print(f"Network A:{case_A}\nNetwork B:{case_B}\n\tN={N} num_experiments={num_experiments}")
    for p in p_array:
        total_fraction_A, total_fraction_B, total_iter = 0, 0, 0
        
        for i in range(num_experiments):
            num_iter, fraction_A, fraction_B = test(N, p, distribution_A, params_A, distribution_B, params_B)
            total_fraction_A += fraction_A
            total_fraction_B += fraction_B
            total_iter += num_iter
        total_fraction_A /= num_experiments
        total_fraction_B /= num_experiments
        total_iter = 1.0 * total_iter / num_experiments
        print(f"\t\tp={p} num_iter={total_iter} fraction_A={total_fraction_A} fraction_B={total_fraction_B}")