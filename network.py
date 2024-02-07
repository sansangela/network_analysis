import numpy as np
from scipy.stats import weibull_min, uniform
from collections import deque

## Paremeters
N = 10**4                 # Number of nodes in both networks
# N = 10**5                 # Number of nodes in both networks
num_experiments = 100     # Number of independent experiments

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
            self.L_values = weibull_min.rvs(c=k, loc=0, scale=lam, size=self.num_nodes)

        elif L_distribution_type == 'uniform':
            if self.distribution_params is None:
                raise ValueError("Uniform distribution requires distribution parameters.")

            L_min = self.distribution_params['L_min']
            L_max = self.distribution_params['L_max']

            # Generate uniform-distributed L values
            self.L_values = uniform.rvs(loc=L_min, scale=L_max - L_min, size=self.num_nodes)

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
            self.S_values = uniform.rvs(loc=S_min, scale=S_max - S_min, size=self.num_nodes)

        else:
            raise ValueError("Invalid distribution type.")

        # Calculate C values
        self.C_values = self.L_values + self.S_values

        # Initialize mask for active nodes
        self.active_nodes_mask = np.ones(self.num_nodes, dtype=bool)
        self.num_remaining_nodes = self.num_nodes
        self.fail_nodes = set()


    def redistribute_load(self, fail_nodes):
        queue = deque()
        for fail_node in fail_nodes:
            queue.append(fail_node)

        while queue:
            fail_node = queue.popleft()

            if self.active_nodes_mask[fail_node] == False:
                continue

            self.active_nodes_mask[fail_node] = False
            self.num_remaining_nodes = np.count_nonzero(self.active_nodes_mask)

            # Redistribute Node
            if self.num_remaining_nodes == 0:
                # GG
                # print("GG")
                return

            self.L_values[self.active_nodes_mask] += self.L_values[fail_node] / self.num_remaining_nodes
            self.L_values[fail_node] = 0
            self.fail_nodes.add(fail_node)

            # Recursively fail nodes
            invalid_indices = np.where((self.L_values > self.C_values) & self.active_nodes_mask)[0]
            queue.extend(invalid_indices)
        self.num_remaining_nodes = np.count_nonzero(self.active_nodes_mask)

    def generate_fail_nodes(self, p):
        remaining_nodes_indices = np.where(self.active_nodes_mask)[0]
        num_nodes_to_select = int(np.ceil(p * self.num_remaining_nodes))
        selected_indices = np.random.choice(remaining_nodes_indices, size=num_nodes_to_select, replace=False)
        return selected_indices

    def reset_fail_node(self):
        self.fail_nodes = set()


# Case 1: L ~ Weibull(L_min, lam, k), S = alpha * L
# N = 100
# num_experiments = 1
n_case = 1
num_elements = 10

distribution_1 = {
    "L": "weibull",
    "S": "linear"
}
params_1 = {
    "L_min": 10,
    "lambda": 100,
    "k": 0.6,
    "alpha": 3.74
}

p_array = np.linspace(0, 1, num_elements)
print(f"Case {n_case}: N={N} num_experiments={num_experiments}")
for p in p_array:
    # print("*****************************************")
    total_remaining_A, total_remaining_B = 0, 0
    
    for i in range(num_experiments):
        network_A = Network(N, distribution_1, params_1)
        network_B = Network(N, distribution_1, params_1)
        fail_nodes = network_A.generate_fail_nodes(p)
        
        old_num_remaining_A, old_num_remaining_B = 0, 0
        num_remaining_A, num_remaining_B = N, N

        while num_remaining_A > 0 and num_remaining_B > 0 and (old_num_remaining_A != num_remaining_A or old_num_remaining_B != num_remaining_B):
            old_num_remaining_A, old_num_remaining_B = num_remaining_A, num_remaining_B
            
            # Reset Fail Nodes
            network_A.reset_fail_node()
            network_B.reset_fail_node()

            # Redistribute in Network A
            network_A.redistribute_load(fail_nodes)
            fail_nodes = network_A.fail_nodes

            # Redistribute in Network B
            network_B.redistribute_load(fail_nodes)
            fail_nodes = network_B.fail_nodes
            
            num_remaining_A = network_A.num_remaining_nodes
            num_remaining_B = network_B.num_remaining_nodes
            if num_remaining_A == 0 or num_remaining_B == 0:
                num_remaining_A, num_remaining_B = 0, 0
            print(f"\tExp {i} Remaining: {total_remaining_A} {total_remaining_B} Percentage: {num_remaining_A}/{N} {num_remaining_B}/{N}")
        total_remaining_A += num_remaining_A
        total_remaining_B += num_remaining_B

    total_remaining_A /= num_experiments
    total_remaining_B /= num_experiments

    print(f"p={p} Number of remaining nodes: {total_remaining_A/N} {total_remaining_B/N}")
    # print("*****************************************")