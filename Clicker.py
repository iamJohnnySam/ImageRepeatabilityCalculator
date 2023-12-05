import os
import numpy as np
import cv2 as cv
import json
import grapher


class Clicker:

    def __init__(self, directory, img_w_px, img_h_px, img_w_mm, img_h_mm, limit=150, window_size=1700):
        self.x_arr = []
        self.y_arr = []
        self.click_coordinates = {}
        self.filename = "None"
        self.directory = directory
        self.h = window_size
        self.limit = limit
        self.img_w_px = int(img_w_px)
        self.img_h_px = int(img_h_px)
        self.img_w_mm = float(img_w_mm)
        self.img_h_mm = float(img_h_mm)
        self.physical_coordinates = {}

    def mouse_callback(self, event, x, y, a, b):
        if event == cv.EVENT_LBUTTONUP:
            self.click_coordinates[self.filename] = [x, y]

            x_adj = x * self.img_w_mm / (self.img_w_px * self.h / self.img_h_px)
            y_adj = y * self.img_h_mm / self.img_h_px

            print("Mouse clicked at X:", str(x) + " (" + str(x_adj) + "mm)", "Y:", str(y) + " (" + str(y_adj) + "mm)")

            self.x_arr.append(x_adj)
            self.y_arr.append(y_adj)
            self.physical_coordinates[self.filename] = [x_adj, y_adj]

    def run_clicker(self):
        self.physical_coordinates = {}
        self.x_arr = []
        self.y_arr = []
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

        json_object = json.dumps(self.click_coordinates, indent=4)
        with open(os.path.basename(self.directory) + "_click_coordinates.json", "w") as outfile:
            outfile.write(json_object)

        json_object = json.dumps(self.physical_coordinates, indent=4)
        with open(os.path.basename(self.directory) + "_physical_coordinates.json", "w") as outfile:
            outfile.write(json_object)

        if len(self.x_arr) == 0:
            return False, "", "", {}

        x_img = np.array(self.x_arr)
        y_img = np.array(self.y_arr)

        x_set = x_img - np.mean(x_img)
        y_set = y_img - np.mean(y_img)

        try:
            print("Min X: ", np.min(x_img), " | Max X: ", np.max(x_img), " | Pk-Pk X: ", np.max(x_img) - np.min(x_img))
            print("Min Y: ", np.min(y_img), " | Max Y: ", np.max(y_img), " | Pk-Pk Y: ", np.max(y_img) - np.min(y_img))
        except ValueError:
            return False, "", "", {}

        success, path = grapher.grapher(x_set, y_set, self.limit, self.directory, "_c")

        return success, path, os.path.basename(self.directory) + "_c", self.physical_coordinates
