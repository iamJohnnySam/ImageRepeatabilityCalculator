import os

import numpy as np

import grapher


class KRILogDecoder:
    def __init__(self, file_path, limit):
        self.physical_coordinates = {}
        self.file = file_path
        self.limit = limit

    def run_decoder(self):
        self.physical_coordinates = {}
        x_arr = []
        y_arr = []
        detect = False
        with open(self.file.name, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if "RAOF" in line:
                    detect = True
                if detect and "Success" in line:
                    detect = False
                    values = line.split(",")
                    t_id = values[0].replace("<", "")
                    x = float(values[2])
                    y = float(values[3])
                    x_arr.append(x)
                    y_arr.append(y)
                    self.physical_coordinates[t_id] = [x, y]
                    print(values)

        x_img = np.array(x_arr)
        y_img = np.array(y_arr)

        x_set = x_img - np.mean(x_img)
        y_set = y_img - np.mean(y_img)

        success, path = grapher.grapher(x_set, y_set, self.limit, self.file.name, "_log")

        return success, path, self.file.name + "_log", self.physical_coordinates

