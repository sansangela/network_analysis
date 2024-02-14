from network import main
import numpy as np
from params import distribution_list, params_list, case_list

## Paremeters
# Debug Param
N = 10000                 # Number of nodes in both networks
# num_experiments = 1
# p_array = [0.01]

# N = 10**5                   # Number of nodes in both networks
num_experiments = 10        # Number of independent experiments
num_p = 10                  # Number of p values
p_array = np.linspace(0.01, 0.5, num_p)

for i in range(len(case_list)):
    for j in range(len(case_list)):

        print("**********************************")
        main(N, case_list[i], case_list[j], num_experiments, p_array, distribution_list[i], params_list[i], distribution_list[j], params_list[j])
        print("**********************************")
# # Case 1: A: L ~ Weibull(L_min, lam, k), S = alpha * L
# n_case = 1



# distribution_1 = {
#     "L": "weibull",
#     "S": "linear"
# }
# params_1 = {
#     "L_min": 10,
#     "lambda": 100,
#     "k": 0.6,
#     "alpha": 3.74
# }


# main(N, n_case, num_experiments, p_array, distribution_1, params_1)


# Case 1: L ~ Weibull(L_min, lam, k), S = alpha * L
# Case 2: L ~ Weibull(L_min, lam, k), S = Uniform(S_min, S_max)
# Case 3: L ~ Uniform(L_min, L_max), S = alpha * L
# Case 4: L ~ Uniform(L_min, L_max), S ~ Uniform(S_min, S_max)
# Case 5: L ~ Pareto(L_min, b), S = alpha * L

