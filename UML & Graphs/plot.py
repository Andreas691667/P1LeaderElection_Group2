import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Change default path 
# sys.path.append('PROGMOD_')

# Function for formatting file to array of specific variables
# data = txt file
# sh_index = state history index, i.e. controller or environment
# var_index = variable index, i.e. timestamp, joint_angle etc...
def txt_to_variable_array (data, sh_index, var_index):
    sh = data.split("|")[sh_index]
    vars = sh.split("/")[var_index]
    seperated = vars.split("&")
    
    # Remove blank spaces
    index_to_remove = []
    for i, e in enumerate(seperated):
        if (e == ""):
            index_to_remove.append(i)
    for e in reversed(index_to_remove):
        seperated.pop(e)

    # Convert from strings to float
    in_numbers = [float(numerical_string) for numerical_string in seperated]

    return (in_numbers, seperated, vars)
        

def plotxy (x, y, y2, xlab, ylab, xunit, yunit):


    # PLOT XY DATA
    plt.plot(x, y, "ro-", color="blue", label="Original")
    plt.plot(x, y2, "ro-", color="red", label="Improved")
    plt.xlabel(xlab)
    plt.ylabel(ylab)

    # SET UNITS
    plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter(f'%.1f {xunit}'))
    plt.gca().yaxis.set_major_formatter(ticker.FormatStrFormatter(f'%.1f {yunit}'))

    plt.grid()
    plt.legend()
    plt.show()


# Main
def main():
    # Changing default matplotlib font: https://jonathansoma.com/lede/data-studio/matplotlib/changing-fonts-in-matplotlib/
    matplotlib.rcParams['font.serif'] = "Palatino Linotype" # Change default serif font
    matplotlib.rcParams['font.family'] = "serif" # Set default family to serif

    x_num =          [2, 5, 10, 15, 17, 20, 22, 25, 30, 32]
    y_num_original = [3 ,24, 99, 224, 288, 399, 483, 624, 899, 1023]
    y_num_improved = [4, 13, 28, 43, 49, 58, 64, 73, 88, 94]


    plotxy(x_num, y_num_original, y_num_improved, "No. of processes", "No. of messages", "", "")
    
    



if __name__ == "__main__":
    main()