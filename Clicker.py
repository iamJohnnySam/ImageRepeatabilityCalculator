import os
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv


class Clicker:
    def __init__(self, directory, camera, limit=150, window_size=1700):
        self.directory = directory
        self.x_arr = np.array([0])
        self.y_arr = np.array([0])
        self.h = window_size
        self.limit = limit
        if camera == "Basler":
            self.camera = 0
        elif camera == "Cognex":
            self.camera = 1
        else:
            self.camera = 1

    def mouse_callback(self, event, x, y, a, b):
        if event == cv.EVENT_LBUTTONUP:
            print("Mouse clicked at X:", x, "Y:", y)
            self.x_arr = np.append(self.x_arr, x)
            self.y_arr = np.append(self.y_arr, y)

    def run_clicker(self):
        for filename in os.listdir(self.directory):
            f = os.path.join(self.directory, filename).replace("\\", "/")
            if os.path.isfile(f):
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

        if self.camera == 0:
            img_w_px = 4096
            img_h_px = 3000
            img_w_mm = 2.355
            img_h_mm = 1.725
        elif self.camera == 1:
            img_w_px = 1024
            img_h_px = 768
            img_w_mm = 31.127
            img_h_mm = 23.346
        else:
            img_w_px = 0
            img_h_px = 0
            img_w_mm = 0
            img_h_mm = 0

        img_w_spx = img_w_px * self.h / img_h_px
        img_h_spx = img_h_px

        x_img = x_arr * img_w_mm / img_w_spx
        y_img = y_arr * img_h_mm / img_h_spx

        x_set = x_img - np.mean(x_img)
        y_set = y_img - np.mean(y_img)

        print("Min X: ", np.min(x_img), " | Max X: ", np.max(x_img), " | Pk-Pk X: ", np.max(x_img) - np.min(x_img))
        print("Min Y: ", np.min(y_img), " | Max Y: ", np.max(y_img), " | Pk-Pk Y: ", np.max(y_img) - np.min(y_img))

        usl = self.limit / 1000
        lsl = -self.limit / 1000

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

        plt.title("Repeatability data for " + os.path.basename(self.directory))
        plt.xlabel("Iterations")
        plt.ylabel("Deviation in mm")
        plt.legend(loc="upper right")
        plt.text(1, usl, "Cpk in X: " + str(min(cpi_x, cpu_x)), fontsize=12)
        plt.text(1, usl - 0.01, "Cpk in Y: " + str(min(cpi_y, cpu_y)), fontsize=12)

        fig_path = os.path.basename(self.directory) + '.png'
        plt.savefig(fig_path, dpi=100)
        plt.show()

        return True, os.path.join(os.getcwd(), fig_path)
