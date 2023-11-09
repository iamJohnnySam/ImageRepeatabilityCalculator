import os

import cv2
import numpy as np
import grapher


class TemplateMatcher:
    reference_center_x = 0
    reference_center_y = 0
    ref_image_take = False
    x_arr = np.array([0])
    y_arr = np.array([0])
    template_w = 0
    template_h = 0
    cropped = False

    x_start, y_start, x_end, y_end = 0, 0, 0, 0

    def __init__(self, directory, img_w_px, img_h_px, img_w_mm, img_h_mm, limit=150, window_size=1700):
        self.w = None
        self.reference_image_w = None
        self.reference_image_h = None
        self.reference_image = None
        self.template = None
        self.directory = directory
        self.h = window_size
        self.limit = limit
        self.img_w_px = int(img_w_px)
        self.img_h_px = int(img_h_px)
        self.img_w_mm = float(img_w_mm)
        self.img_h_mm = float(img_h_mm)

    def run_matcher(self):
        reference_image = None
        for filename in os.listdir(self.directory):
            f = os.path.join(self.directory, filename).replace("\\", "/")
            if os.path.isfile(f):
                current_image = cv2.imread(f)

                if not self.ref_image_take:
                    self.ref_image_take = True

                    self.reference_image = current_image
                    self.reference_image_w = self.reference_image.shape[1]
                    self.reference_image_h = self.reference_image.shape[0]

                    self.w = int(self.h * self.reference_image_w / self.reference_image_h)
                    display_image = cv2.resize(self.reference_image, (self.w, self.h), interpolation=cv2.INTER_AREA)

                    cv2.namedWindow(f)
                    cv2.setWindowProperty(f, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    cv2.imshow(f, display_image)
                    cv2.setMouseCallback(f, self.mouse_crop)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                    if self.template is None:
                        print("Template failed")
                        return False, "", ""

                    if (self.x_start == self.x_end) or (self.y_start == self.y_end):
                        print("Template too small")
                        return False, "", ""

                    cv2.imshow(f, self.template)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                    self.template_w = self.template.shape[0]
                    self.template_h = self.template.shape[1]

                    loc = cv2.matchTemplate(self.reference_image, self.template, cv2.TM_CCOEFF_NORMED)

                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(loc)
                    top_left = max_loc
                    bottom_right = (top_left[0] + self.template_w, top_left[1] + self.template_h)
                    cv2.rectangle(current_image, top_left, bottom_right, 255, 2)

                    self.reference_center_x = top_left[0] + (self.template_w / 2)
                    self.reference_center_y = top_left[1] + (self.template_h / 2)

                else:
                    loc = cv2.matchTemplate(current_image, self.template, cv2.TM_CCOEFF_NORMED)

                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(loc)
                    top_left = max_loc
                    bottom_right = (top_left[0] + self.template_w, top_left[1] + self.template_h)
                    cv2.rectangle(current_image, top_left, bottom_right, 255, 2)

                    x = top_left[0] + (self.template_w / 2)
                    y = top_left[1] + (self.template_h / 2)

                    x = (x - self.reference_center_x) * self.img_w_mm / self.img_w_px
                    y = (y - self.reference_center_y) * self.img_h_mm / self.img_h_px

                    self.x_arr = np.append(self.x_arr, x)
                    self.y_arr = np.append(self.y_arr, y)

                    print(filename + '  -  ' + str(x) + ', ' + str(y))

        self.x_arr = np.delete(self.x_arr, 0)
        self.y_arr = np.delete(self.y_arr, 0)

        self.x_arr = self.x_arr - np.mean(self.x_arr)
        self.y_arr = self.y_arr - np.mean(self.y_arr)

        success, path, = grapher.grapher(self.x_arr, self.y_arr, self.limit, self.directory, "_tm")
        return success, path, os.path.basename(self.directory) + "_tm"

    def mouse_crop(self, event, x, y, flags, param):

        y = y * self.reference_image_h / self.h
        x = x * self.reference_image_w / self.w

        if event == cv2.EVENT_LBUTTONDOWN:
            self.x_start, self.y_start, self.x_end, self.y_end = x, y, x, y
            print("template started", x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            self.x_end, self.y_end = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            self.x_end, self.y_end = x, y
            self.cropped = True
            print("template ended", x, y)

            self.template = self.reference_image[int(min(self.y_start, self.y_end)):int(max(self.y_start, self.y_end)),
                                                 int(min(self.x_start, self.x_end)):int(max(self.x_start, self.x_end))]
