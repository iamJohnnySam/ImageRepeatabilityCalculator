import os
import numpy as np
from matplotlib import pyplot as plt


def cpi_cpx(x_set, y_set, limit):
    usl = limit / 1000
    lsl = -limit / 1000

    cpi_x = (np.mean(x_set) - lsl) / (3 * np.std(x_set))
    cpu_x = (usl - np.mean(x_set)) / (3 * np.std(x_set))
    print("Cpk in X:", min(cpi_x, cpu_x))

    cpi_y = (np.mean(y_set) - lsl) / (3 * np.std(y_set))
    cpu_y = (usl - np.mean(y_set)) / (3 * np.std(y_set))
    print("Cpk in Y:", min(cpi_y, cpu_y))

    return usl, lsl, cpi_x, cpu_x, cpi_y, cpu_y


def three_sig(x_set, y_set):
    return 3 * np.std(x_set), 3 * np.std(y_set)


def grapher(x_set, y_set, limit, directory, end):
    usl, lsl, cpi_x, cpu_x, cpi_y, cpu_y = cpi_cpx(x_set, y_set, limit)
    three_sig_x, three_sig_y = three_sig(x_set, y_set)

    # %% Figure
    fig1 = plt.figure()
    fig1.set_figwidth(30)
    fig1.set_figheight(15)
    plt.title("X and Y Offset")
    plt.plot(x_set, label="X Data")
    plt.plot(y_set, label="Y Data")
    plt.axhline(y=usl, color='r', linestyle='-', label="Control Limits")
    plt.axhline(y=lsl, color='r', linestyle='-')

    plt.axhline(y=three_sig_x, color='m', linestyle='--', label="3 sigma for X")
    plt.axhline(y=-three_sig_x, color='m', linestyle='--', label="3 sigma for X")
    plt.axhline(y=three_sig_y, color='c', linestyle='--', label="3 sigma for Y")
    plt.axhline(y=-three_sig_y, color='c', linestyle='--', label="3 sigma for Y")

    plt.title("Repeatability data for " + os.path.basename(directory))
    plt.xlabel("Iterations")
    plt.ylabel("Deviation in mm")
    plt.legend(loc="upper right")
    plt.text(0.5, usl, "Cpk in X: " + str(round(min(cpi_x, cpu_x), 3)), fontsize=12)
    plt.text(0.5, usl - 0.01, "Cpk in Y: " + str(round(min(cpi_y, cpu_y), 3)), fontsize=12)

    plt.text(0.5, three_sig_x, "3σ in X: " + str(round(three_sig_x, 3)), fontsize=12)
    plt.text(0.5, three_sig_y, "3σ in Y: " + str(round(three_sig_y, 3)), fontsize=12)

    fig_path = os.path.basename(directory) + end + '.png'
    plt.savefig(fig_path, dpi=100)
    plt.show()

    return True, os.path.join(os.getcwd(), fig_path)


def scatter_grapher(coordinates, limit, directory, end):
    x_set = []
    y_set = []

    for x in coordinates.keys():
        x_set.append(coordinates[x][0])
        y_set.append(coordinates[x][0])

    usl, lsl, cpi_x, cpu_x, cpi_y, cpu_y = cpi_cpx(x_set, y_set, limit)

    # %% Figure
    fig1 = plt.figure()
    fig1.set_figwidth(30)
    fig1.set_figheight(15)
    plt.title("X and Y Offset")
    plt.scatter(x=coordinates.keys(), y=x_set)
    plt.scatter(x=coordinates.keys(), y=y_set)
    plt.axhline(y=usl, color='r', linestyle='-', label="Control Limits")
    plt.axhline(y=lsl, color='r', linestyle='-')

    plt.title("Repeatability data for " + os.path.basename(directory))
    plt.xlabel("Iterations")
    plt.ylabel("Deviation in mm")
    plt.legend(loc="upper right")
    plt.text(0.5, usl, "Cpk in X: " + str(round(min(cpi_x, cpu_x), 3)), fontsize=12)
    plt.text(0.5, usl - 0.01, "Cpk in Y: " + str(round(min(cpi_y, cpu_y), 3)), fontsize=12)

    fig_path = os.path.basename(directory) + end + '.png'
    plt.savefig(fig_path, dpi=100)
    plt.show()

    return True, os.path.join(os.getcwd(), fig_path)


def combined_grapher(limit, output_x, output_y):
    file_name = "Combined"
    usl = limit / 1000
    lsl = -limit / 1000

    # %% Figure
    fig1 = plt.figure()
    fig1.set_figwidth(30)
    fig1.set_figheight(15)
    plt.title("X and Y Offset")
    for title in output_x.keys():
        file_name = file_name + " - " + title
        plt.plot(output_x[title], label="X Data for " + title)
        plt.plot(output_y[title], label="Y Data for " + title)

    plt.axhline(y=usl, color='r', linestyle='-', label="Control Limits")
    plt.axhline(y=lsl, color='r', linestyle='-')

    plt.title("Combined Repeatability data")
    plt.xlabel("Iterations")
    plt.ylabel("Deviation in mm")
    plt.legend(loc="upper right")

    fig_path = file_name + '.png'
    plt.savefig(fig_path, dpi=100)
    plt.show()
