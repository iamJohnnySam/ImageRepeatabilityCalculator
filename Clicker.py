import os
import numpy as np
import cv2 as cv
import json

import grapher


class Clicker:
    x_arr = np.array([0])
    y_arr = np.array([0])
    coordinates = {}

    def __init__(self, directory, img_w_px, img_h_px, img_w_mm, img_h_mm, limit=150, window_size=1700):
        self.x_set = None
        self.y_set = None
        self.filename = "None"
        self.directory = directory
        self.h = window_size
        self.limit = limit
        self.img_w_px = int(img_w_px)
        self.img_h_px = int(img_h_px)
        self.img_w_mm = float(img_w_mm)
        self.img_h_mm = float(img_h_mm)


    def mouse_callback(self, event, x, y, a, b):
        if event == cv.EVENT_LBUTTONUP:
            print("Mouse clicked at X:", x, "Y:", y)
            self.x_arr = np.append(self.x_arr, x)
            self.y_arr = np.append(self.y_arr, y)
            self.coordinates[self.filename] = [x, y]

    def run_clicker(self):
        for filename in os.listdir(self.directory):
            f = os.path.join(self.directory, filename).replace("\\", "/")
            if os.path.isfile(f):
                self.filename = filename
                img = cv.imread(f)
                dim = (int(self.h * img.shape[1] / img.shape[0]), self.h)
                img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
                cv.namedWindow(f)
                cv.setWindowProperty(f, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
                cv.moveWindow(f, 0, 0)
                cv.setMouseCallback(f, self.mouse_callback)
                cv.imshow(f, img)
                cv.waitKey(0)
                cv.destroyAllWindows()

        x_arr = np.delete(self.x_arr, 0)
        y_arr = np.delete(self.y_arr, 0)

        json_object = json.dumps(self.coordinates, indent=4)
        with open(os.path.basename(self.directory) + ".json", "w") as outfile:
            outfile.write(json_object)

        img_w_spx = self.img_w_px * self.h / self.img_h_px
        img_h_spx = self.img_h_px

        x_img = x_arr * self.img_w_mm / img_w_spx
        y_img = y_arr * self.img_h_mm / img_h_spx

        if x_img.size == 0:
            return False, "", "", None, None

        self.x_set = x_img - np.mean(x_img)
        self.y_set = y_img - np.mean(y_img)

        try:
            print("Min X: ", np.min(x_img), " | Max X: ", np.max(x_img), " | Pk-Pk X: ", np.max(x_img) - np.min(x_img))
            print("Min Y: ", np.min(y_img), " | Max Y: ", np.max(y_img), " | Pk-Pk Y: ", np.max(y_img) - np.min(y_img))
        except ValueError:
            return False, "", "", None, None

        success, path, = grapher.grapher(self.x_set, self.y_set, self.limit, self.directory, "_c")
        return success, path, os.path.basename(self.directory) + "_c", self.x_set, self.y_set
