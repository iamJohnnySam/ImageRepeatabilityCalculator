import os
import cv2
import numpy as np

import grapher


class AutoMatcher:
    ref_image_take = False
    x_arr = np.array([0])
    y_arr = np.array([0])

    def __init__(self, directory, img_w_px, img_h_px, img_w_mm, img_h_mm, limit=150, window_size=1700):
        self.directory = directory
        self.h = window_size
        self.limit = limit
        self.img_w_px = int(img_w_px)
        self.img_h_px = int(img_h_px)
        self.img_w_mm = float(img_w_mm)
        self.img_h_mm = float(img_h_mm)

    def run_bf_matcher(self):
        reference_image = None
        for filename in os.listdir(self.directory):
            f = os.path.join(self.directory, filename).replace("\\", "/")
            if os.path.isfile(f):
                if not self.ref_image_take:
                    reference_image = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
                    self.ref_image_take = True
                else:
                    image = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
                    result = self.calculate_offset(reference_image, image)
                    if result is not None:
                        x_offset, y_offset = result
                        print(x_offset, y_offset)
                        self.x_arr = np.append(self.x_arr, x_offset)
                        self.y_arr = np.append(self.y_arr, y_offset)

        x_arr = np.delete(self.x_arr, 0)
        y_arr = np.delete(self.y_arr, 0)

        img_w_spx = self.img_w_px * self.h / self.img_h_px
        img_h_spx = self.img_h_px

        x_img = x_arr * self.img_w_mm / img_w_spx
        y_img = y_arr * self.img_h_mm / img_h_spx

        success, path, = grapher.grapher(x_img, y_img, self.limit, self.directory, "_bf")
        return success, path, os.path.basename(self.directory) + "_bf"

    def calculate_offset(self, reference, image):
        # Find key points and descriptors for both images using AKAZE
        akaze = cv2.AKAZE_create(threshold=0.001, nOctaves=4)
        kp1, des1 = akaze.detectAndCompute(reference, None)
        kp2, des2 = akaze.detectAndCompute(image, None)

        # Create a Brute Force Matcher
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        # Apply ratio test to find good matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        # Check if there are enough good matches to calculate the offset
        if len(good_matches) > 10:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            h, w = reference.shape

            # Transform the reference corners to the image
            corners = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            transformed_corners = cv2.perspectiveTransform(corners, M)

            # Calculate the x and y offsets
            x_offset = transformed_corners[0][0][0]
            y_offset = transformed_corners[0][0][1]
            return x_offset, y_offset
        else:
            return None