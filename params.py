case_list = [
    "Case 1: L ~ Weibull(L_min, lam, k), S = alpha * L",
    "Case 2: L ~ Weibull(L_min, lam, k), S = Uniform(S_min, S_max)",
    "Case 3: L ~ Uniform(L_min, L_max), S = alpha * L",
    "Case 4: L ~ Uniform(L_min, L_max), S ~ Uniform(S_min, S_max)",
    "Case 5: L ~ Pareto(L_min, b), S = alpha * L"
]

distribution_list = []
params_list = []

# Case 1: L ~ Weibull(L_min, lam, k), S = alpha * L
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
distribution_list.append(distribution_1)
params_list.append(params_1)

# Case 2: L ~ Weibull(L_min, lam, k), S = Uniform(S_min, S_max)
distribution_2 = {
    "L": "weibull",
    "S": "uniform"
}
params_2 = {
    "L_min": 10,
    "lambda": 100,
    "k": 0.6,
    "S_min": 60,
    "S_max": 80
}
distribution_list.append(distribution_2)
params_list.append(params_2)

# Case 3: L ~ Uniform(L_min, L_max), S = alpha * L
distribution_3 = {
    "L": "uniform",
    "S": "linear"
}
params_3 = {
    "L_min": 10,
    "L_max": 30,
    "alpha": 2.74
}
distribution_list.append(distribution_3)
params_list.append(params_3)

# Case 4: L ~ Uniform(L_min, L_max), S ~ Uniform(S_min, S_max)
distribution_4 = {
    "L": "uniform",
    "S": "uniform"
}
params_4 = {
    "L_min": 10,
    "L_max": 30,
    "S_min": 40,
    "S_max": 50
}
distribution_list.append(distribution_4)
params_list.append(params_4)


# Case 5: L ~ Pareto(L_min, b), S = alpha * L
distribution_5 = {
    "L": "pareto",
    "S": "linear"
}
params_5 = {
    "L_min": 10,
    "b": 2,
    "alpha": 2.3,
}
distribution_list.append(distribution_5)
params_list.append(params_5)