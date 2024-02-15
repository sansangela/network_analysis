import matplotlib.pyplot as plt
import re
from collections import defaultdict
from params import case_list

# Function to read and parse the log file
def parse_log_file(filepath):
    data = defaultdict(lambda: defaultdict(list))
    current_a_case = ""
    with open(filepath, 'r') as file:
        for line in file:
            if "Network A:Case" in line:
                match = re.search(r'Network A:Case (.*?): (.*?)', line)
                if match:
                    current_a_case = match.group(1)
            elif "Network B:Case" in line:
                match = re.search(r'Network B:Case (.*?): (.*?)', line)
                if match:
                    current_b_case = match.group(1)
            else:
                match = re.search(r'p=(.*?) num_iter=.*? fraction_A=(.*?) fraction_B=.*?', line)
                if match:
                    p_value = float(match.group(1))
                    fraction_A = float(match.group(2))
                    data[current_a_case][current_b_case].append((p_value, fraction_A))
    return data


# Function to plot the data
def plot_data(data):
    for a_case_idx, (a_case, b_cases) in enumerate(data.items(), start=1):
        plt.figure(figsize=(10, 6))
        for b_case, values in b_cases.items():
            p_values, fraction_A_values = zip(*values)
            plt.plot(p_values, fraction_A_values, marker='o', linestyle='-', label=f'{case_list[int(b_case)-1]}')
        
        plt.title(f'{a_case}')
        plt.xlabel('P-value')
        plt.ylabel('Fraction_A')
        plt.legend()
        plt.grid(True)
        
        filename = f'plot_{a_case_idx}.png'  # Filename based on a_case index
        plt.savefig(filename, dpi=300)
        print(f'Saved plot to {filename}')
        plt.close()  # Close the figure to free memory

file_path = "log/network_0214.txt"
data = parse_log_file(file_path)
plot_data(data)