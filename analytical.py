import numpy as np
from scipy.stats import weibull_min
from scipy.integrate import quad
from scipy.optimize import minimize, minimize_scalar

LARGE_UPPER_BOUND = 1e12

## Case 1
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

class AnalyticalEvaluation:
    def __init__(self, network_A=distribution_1, network_B=distribution_1, A_params=params_1, B_params=params_1):
        self.L_A = network_A["L"]
        self.S_A = network_A["S"]
        self.L_B = network_B["L"]
        self.S_B = network_B["S"]
        self.A_params = A_params
        self.B_params = B_params

    def caculate_S_A_greater_than_x(self, x):
        # P[S_A > x]
        if self.L_A == "weibull" and self.S_A == "linear":
            # = P[L_A > x/alpha]
            L_min = self.A_params['L_min']
            lam = self.A_params['lambda']
            k = self.A_params['k']
            alpha = self.A_params['alpha']
            
            return weibull_min.sf((x / alpha - L_min) / lam, k)
    
    def caculate_S_B_greater_than_x(self, x):
        # P[S_B > x]
        if self.L_B == "weibull" and self.S_B == "linear":
            # = P[L_B > x/alpha]
            L_min = self.B_params['L_min']
            lam = self.B_params['lambda']
            k = self.B_params['k']
            alpha = self.B_params['alpha']
            
            return weibull_min.sf((x / alpha - L_min) / lam, k)
                

    def calculate_expected_L_A_given_S_A_greater_than_x(self, x):
        # E[L_A | S_A > x]
        if self.L_A == "weibull" and self.S_A == "linear":
            L_min = self.A_params['L_min']
            lam = self.A_params['lambda']
            k = self.A_params['k']
            alpha = self.A_params['alpha']

            lower_bound = max(L_min, x / alpha)
            integrand = lambda l: l * weibull_min.pdf(l, k, scale=lam, loc=L_min)
            numerator, _ = quad(integrand, lower_bound, np.inf)
            denominator = self.caculate_S_A_greater_than_x(x)

            res =  numerator / denominator if denominator else 0
            return res
    
    def calculate_expected_L_B_given_S_B_greater_than_x(self, x):
        # E[L_B | S_B > x]
        if self.L_B == "weibull" and self.S_B == "linear":
            L_min = self.B_params['L_min']
            lam = self.B_params['lambda']
            k = self.B_params['k']
            alpha = self.B_params['alpha']

            lower_bound = max(L_min, x / alpha)
            integrand = lambda l: l * weibull_min.pdf(l, k, scale=lam, loc=L_min)
            numerator, _ = quad(integrand, lower_bound, np.inf)
            denominator = self.caculate_S_B_greater_than_x(x)

            res =  numerator / denominator if denominator else 0
            return res

    def calculate_S_A_greater_than_given(self, Q_2i_plus_1, Q_2i_minus_1):
        # P[S_A > Q_2i_plus_1 | S_A > Q_2i_minus_1]
        numerator = self.caculate_S_A_greater_than_x(Q_2i_plus_1)
        denominator = self.caculate_S_A_greater_than_x(Q_2i_minus_1)
        
        res =  numerator / denominator if denominator else 0
        return res

    def calculate_S_B_greater_than_given(self, Q_2i_plus_2, Q_2i):
        # P[S_B > Q_2i_plus_2 | S_B > Q_2i]
        numerator = self.caculate_S_A_greater_than_x(Q_2i_plus_2)
        denominator = self.caculate_S_A_greater_than_x(Q_2i)
        
        res =  numerator / denominator if denominator else 0
        return res


    def calculate_Q_2i_plus_1(self, Q_2i_minus_1, p_A):

        def objective(x):
            return x
        
        def constraint_function(x):
            numerator = self.caculate_S_A_greater_than_x(Q_2i_minus_1+x)
            denominator = self.caculate_S_A_greater_than_x(Q_2i_minus_1)
            
            exp_1 = self.calculate_expected_L_A_given_S_A_greater_than_x(x+Q_2i_minus_1)
            exp_2 = self.calculate_expected_L_A_given_S_A_greater_than_x(Q_2i_minus_1)
    
            P_ratio = numerator / denominator
            lhs = P_ratio * (x + Q_2i_minus_1 + exp_1)
            rhs = (Q_2i_minus_1 + exp_2) / p_A
            return lhs - rhs           

        constraints = ({'type': 'ineq', 'fun': lambda x: constraint_function(x)})
        x0 = [1.0]
        result = minimize(objective, x0, constraints=constraints, bounds=[(0, None)])

        if result.success:
            optimal_x = result.x[0]
            # print(f"The optimal x is: {optimal_x}")

            Q_2i_plus_1 = Q_2i_minus_1 + optimal_x
            return Q_2i_plus_1
        else:
            print("Optimization was unsuccessful.")
            return None
        
        

    def calculate_Q_2i_plus_2(self, Q_2i, p_B):
        
        def objective(x):
            return x
        
        def constraint_function(x):
            numerator = self.caculate_S_B_greater_than_x(Q_2i+x)
            denominator = self.caculate_S_B_greater_than_x(Q_2i)
            
            exp_1 = self.calculate_expected_L_B_given_S_B_greater_than_x(x+Q_2i)
            exp_2 = self.calculate_expected_L_B_given_S_B_greater_than_x(Q_2i)
    
            P_ratio = numerator / denominator
            lhs = P_ratio * (x + Q_2i + exp_1)
            rhs = (Q_2i + exp_2) / p_B
            return lhs - rhs        
        
            
        constraints = ({'type': 'ineq', 'fun': lambda x: constraint_function(x)})
        x0 = [1.0]
        result = minimize(objective, x0, constraints=constraints, bounds=[(0, None)])

        if result.success:
            optimal_x = result.x[0]
            # print(f"The optimal x is: {optimal_x}")

            Q_2i_plus_2 = Q_2i + optimal_x
            return Q_2i_plus_2
        else:
            print("Optimization was unsuccessful.")
        

    def calculate_f_A_2i_plus_1(self, f_A_2i_minus_1, p_A_2i_plus_1, Q_2i_plus_1, Q_2i_minus_1):
        cond_prob = self.calculate_S_A_greater_than_given(Q_2i_plus_1, Q_2i_minus_1)
        print("cond_prob:", cond_prob)
        f_A = f_A_2i_minus_1 * p_A_2i_plus_1 * cond_prob
        return f_A
    
    def calculate_f_B_2i_plus_2(self, f_B_2i, p_B_2i, Q_2i_plus_2, Q_2i):
        cond_prob = self.calculate_S_B_greater_than_given(Q_2i_plus_2, Q_2i)
        f_B = f_B_2i * p_B_2i * cond_prob
        return f_B

    def evaluate(self, p=0.9, num_cycles=10):
        # Initial Conditions
        Q_minus_1, Q_0 = 0, 0
        f_A, f_B = 1, p
        p_A, p_B = p, p

        for _ in range(num_cycles):
            # Network A Updates
            p_A = 1.0 * f_B / f_A
            print("Q_minus_1, p_A:", Q_minus_1, p_A)
            Q_plus_1 = self.calculate_Q_2i_plus_1(Q_minus_1, p_A)
            if not Q_plus_1:
                print("Network failed...")
                f_A, f_B = 0, 0
                break
            f_A = self.calculate_f_A_2i_plus_1(f_A, p_A, Q_plus_1, Q_minus_1)
            
            
            # Network B Updates
            p_B = p_B * f_A / f_B
            Q_plus_2 = self.calculate_Q_2i_plus_2(Q_0, p_B)
            if not Q_plus_2:
                print("Network failed...")
                f_A, f_B = 0, 0
                break
            f_B = self.calculate_f_B_2i_plus_2(f_B, p_B, Q_plus_2, Q_0)
            print(f"f_A={f_A} f_B={f_B} Q_plus_1={Q_plus_1} Q_plus_2={Q_plus_2}")

            Q_minus_1, Q_0 = Q_plus_1, Q_plus_2



if __name__ == "__main__":
    print("Hello")
    A_1_B_1_evaluate = AnalyticalEvaluation(network_A=distribution_1, network_B=distribution_1, A_params=params_1, B_params=params_1)
    A_1_B_1_evaluate.evaluate(p=0.9, num_cycles=2)