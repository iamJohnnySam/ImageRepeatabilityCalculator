import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse


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


def save_and_show(directory, type, end):
    fig_path = "images/" + os.path.basename(directory) + type + end + '.png'
    plt.savefig(fig_path, dpi=100)
    plt.show()
    return fig_path


def grapher(x_set, y_set, limit, directory, end):
    paths = {}
    a, b = line_grapher(x_set, y_set, limit, directory, end)
    c, d = scatter_grapher(x_set, y_set, limit, directory, end)
    success = a and c

    paths["line"] = b
    paths["scatter"] = d

    return success, paths


def line_grapher(x_set, y_set, limit, directory, end):
    usl, lsl, cpi_x, cpu_x, cpi_y, cpu_y = cpi_cpx(x_set, y_set, limit)
    three_sig_x, three_sig_y = three_sig(x_set, y_set)

    # %% Figure
    fig1 = plt.figure()
    fig1.set_figwidth(30)
    fig1.set_figheight(15)
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

    fig_path = save_and_show(directory, '_line', end)

    return True, os.path.join(os.getcwd(), fig_path)


def scatter_grapher(x_set, y_set, limit, directory, end):
    usl, lsl, cpi_x, cpu_x, cpi_y, cpu_y = cpi_cpx(x_set, y_set, limit)
    three_sig_x, three_sig_y = three_sig(x_set, y_set)

    fig, ax = plt.subplots()
    fig.set_figwidth(20)
    fig.set_figheight(20)
    plt.scatter(x_set, y_set, alpha=0.5)

    circle1 = plt.Circle((0, 0), usl, fill=False, color='r', linestyle='-', label="Control Limit")
    circle2 = Ellipse((0, 0), 2 * three_sig_x, 2 * three_sig_y,
                      fill=False, color='m', linestyle='--', label="3 sigma")

    ax.add_patch(circle1)
    ax.add_patch(circle2)

    plt.title("Repeatability data for " + os.path.basename(directory))
    plt.xlabel("X-Deviation")
    plt.ylabel("Y-Deviation")
    plt.legend(loc="upper right")

    min_x_point = min(lsl, -three_sig_x)
    min_y_point = min(lsl, -three_sig_y)
    font_size = 12
    distance = -(min_x_point / 20)

    ax.text(min_x_point, min_y_point + 3 * distance, "Cpk in X: " + str(round(min(cpi_x, cpu_x), 3)),
            fontsize=font_size)
    ax.text(min_x_point, min_y_point + 2 * distance, "Cpk in Y: " + str(round(min(cpi_y, cpu_y), 3)),
            fontsize=font_size)

    ax.text(min_x_point, min_y_point + distance, "3σ in X: " + str(round(three_sig_x, 3)), fontsize=font_size)
    ax.text(min_x_point, min_y_point, "3σ in Y: " + str(round(three_sig_y, 3)), fontsize=font_size)

    fig_path = save_and_show(directory, '_scatter', end)

    return True, os.path.join(os.getcwd(), fig_path)


def x_y_extractor(plot_values):
    data = {}
    for title in plot_values.keys():
        x = []
        y = []
        for coordinates in plot_values[title].keys():
            x.append(float(plot_values[title][coordinates][0]))
            y.append(float(plot_values[title][coordinates][1]))

        x_img = np.array(x)
        x_set = x_img - np.mean(x_img)

        y_img = np.array(y)
        y_set = y_img - np.mean(y_img)

        data[title] = {"x": x_set,
                       "y": y_set}
    return data


def combined_grapher(limit, plot_values, file_name):
    paths = {"line": combined_line_grapher(limit, plot_values, file_name),
             "scatter": combined_scatter_grapher(limit, plot_values, file_name)}
    return paths


def combined_line_grapher(limit, plot_values, file_name):
    usl = limit / 1000
    lsl = -limit / 1000

    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    color_val = 0

    # %% Figure
    fig1 = plt.figure()
    fig1.set_figwidth(30)
    fig1.set_figheight(15)

    data = x_y_extractor(plot_values)

    for title in data:
        color_val = color_val + 1
        if color_val == len(colors):
            color_val = 0
        plt.plot(data[title]['x'], label="X Data for " + title, color=colors[color_val])

        color_val = color_val + 1
        if color_val == len(colors):
            color_val = 0
        plt.plot(data[title]['y'], label="Y Data for " + title, color=colors[color_val])

    plt.axhline(y=usl, color='r', linestyle='-', label="Control Limits")
    plt.axhline(y=lsl, color='r', linestyle='-')

    plt.title("Repeatability data - " + file_name)
    plt.xlabel("Iterations")
    plt.ylabel("Deviation in mm")
    plt.legend(loc="upper right")

    fig_path = "images/" + file_name + '_line.png'
    plt.savefig(fig_path, dpi=100)
    plt.show()

    return fig_path


def combined_scatter_grapher(limit, plot_values, file_name):
    usl = limit / 1000

    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    color_val = 0

    fig, ax = plt.subplots()
    fig.set_figwidth(20)
    fig.set_figheight(20)

    data = x_y_extractor(plot_values)

    for title in data:
        color_val = color_val + 1
        if color_val == len(colors):
            color_val = 0
        plt.scatter(data[title]['x'], data[title]['y'], alpha=0.5, color=colors[color_val], label=title)

    circle1 = plt.Circle((0, 0), usl, fill=False, color='r', linestyle='-', label="Control Limit")

    ax.add_patch(circle1)

    plt.title("Repeatability data - " + file_name)
    plt.xlabel("X-Deviation")
    plt.ylabel("Y-Deviation")
    plt.legend(loc="upper right")

    fig_path = "images/" + file_name + '_scatter.png'
    plt.savefig(fig_path, dpi=100)
    plt.show()

    return fig_path
