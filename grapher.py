import os
import numpy as np
from matplotlib import pyplot as plt


def grapher(x_set, y_set, limit, directory, end):
    usl = limit / 1000
    lsl = -limit / 1000

    cpi_x = (np.mean(x_set) - lsl) / (3 * np.std(x_set))
    cpu_x = (usl - np.mean(x_set)) / (3 * np.std(x_set))
    print("Cpk in X:", min(cpi_x, cpu_x))

    cpi_y = (np.mean(y_set) - lsl) / (3 * np.std(y_set))
    cpu_y = (usl - np.mean(y_set)) / (3 * np.std(y_set))
    print("Cpk in Y:", min(cpi_y, cpu_y))

    # %% Figure
    fig1 = plt.figure()
    fig1.set_figwidth(30)
    fig1.set_figheight(15)
    plt.title("X and Y Offset")
    plt.plot(x_set, label="X Data")
    plt.plot(y_set, label="Y Data")
    plt.axhline(y=usl, color='r', linestyle='-', label="Control Limits")
    plt.axhline(y=lsl, color='r', linestyle='-')

    plt.axhline(y=3 * np.std(x_set), color='m', linestyle='--', label="3 sigma for X")
    plt.axhline(y=-3 * np.std(x_set), color='m', linestyle='--', label="3 sigma for X")
    plt.axhline(y=3 * np.std(y_set), color='c', linestyle='--', label="3 sigma for Y")
    plt.axhline(y=-3 * np.std(y_set), color='c', linestyle='--', label="3 sigma for Y")

    plt.title("Repeatability data for " + os.path.basename(directory))
    plt.xlabel("Iterations")
    plt.ylabel("Deviation in mm")
    plt.legend(loc="upper right")
    plt.text(1, usl, "Cpk in X: " + str(min(cpi_x, cpu_x)), fontsize=12)
    plt.text(1, usl - 0.01, "Cpk in Y: " + str(min(cpi_y, cpu_y)), fontsize=12)

    fig_path = os.path.basename(directory) + end + '.png'
    plt.savefig(fig_path, dpi=100)
    plt.show()

    return True, os.path.join(os.getcwd(), fig_path)