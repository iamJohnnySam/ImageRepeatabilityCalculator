import os
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from PIL import Image, ImageTk
from Clicker import Clicker
import subprocess
from functools import partial

class GUI:
    output_images = {}

    def __init__(self):
        self.already_added_content = False
        self.image_button_frame = None
        self.x_px = None
        self.y_px = None
        self.x_mm = None
        self.y_mm = None
        self.camera_custom = None
        self.already_added_graph = False
        self.start_auto_button = None
        self.image_label = None
        self.image_placeholder = None
        self.img_path = None
        self.height_entry = None
        self.path = None
        self.start_clicker_button = None
        self.limit_entry = None
        self.camera_cognex = None
        self.camera_basler = None
        self.root = tk.Tk()
        self.root.title("Image Repeatability Calculator")
        self.root.geometry("950x800")  # Set the window size

        self.camera_selected = tk.StringVar()
        self.camera_selected.set("Basler")  # Only "Basler" selected initially

        heading_label = tk.Label(self.root, text="Image Repeatability Calculator", font=("Helvetica", 16))
        heading_label.pack()

        instructions_label = tk.Label(self.root, text="Select folder which has photos")
        instructions_label.pack()

        self.open_folder_button = tk.Button(self.root, text="Select Folder", width=20, command=self.open_folder_dialog,
                                            state=tk.NORMAL)
        self.open_folder_button.pack()

        self.selected_folder_label = tk.Label(self.root, text="Selected Folder: ")
        self.selected_folder_label.pack()

        self.folder_selected = tk.BooleanVar()
        self.folder_selected.set(False)

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()

    def on_validate(self, P):
        # This function is called when the Entry is being edited
        if P == "" or P.replace(".", "", 1).isdigit():
            return True
        return False

    def open_folder_dialog(self):
        folder_path = filedialog.askdirectory()
        self.path = folder_path
        if folder_path:
            self.selected_folder_label.config(text="Selected Folder: " + folder_path)
            if not self.already_added_content:
                self.add_camera_selection()
                self.already_added_content = True
            self.folder_selected.set(True)
            self.start_clicker_button.config(state=tk.NORMAL)
            #self.start_auto_button.config(state=tk.NORMAL)

    def add_camera_selection(self):
        camera_frame = tk.Frame(self.root)
        camera_frame.pack()
        camera_label = tk.Label(camera_frame, text="Select Camera:")
        camera_label.pack(side=tk.LEFT)

        self.camera_basler = tk.Radiobutton(camera_frame, text="Basler", variable=self.camera_selected, value="Basler",
                                            width=10, command=self.camera_selection_basler)
        self.camera_basler.pack(side=tk.LEFT)
        self.camera_cognex = tk.Radiobutton(camera_frame, text="Cognex", variable=self.camera_selected, value="Cognex",
                                            width=10, command=self.camera_selection_cognex)
        self.camera_cognex.pack(side=tk.LEFT)
        self.camera_custom = tk.Radiobutton(camera_frame, text="Custom", variable=self.camera_selected, value="Custom",
                                            width=10, command=self.camera_selection_custom)
        self.camera_custom.pack(side=tk.LEFT)

        fov_label_frame = tk.Frame(self.root)
        fov_label_frame.pack()

        w = 15

        x_px = tk.Label(fov_label_frame, text="FoV X(px)", width=w)
        x_px.pack(side=tk.LEFT)
        y_px = tk.Label(fov_label_frame, text="FoV Y(px)", width=w)
        y_px.pack(side=tk.LEFT)
        x_mm = tk.Label(fov_label_frame, text="FoV X(mm)", width=w)
        x_mm.pack(side=tk.LEFT)
        y_mm = tk.Label(fov_label_frame, text="FoV Y(mm)", width=w)
        y_mm.pack(side=tk.LEFT)

        validate_func = self.root.register(self.on_validate)

        fov_frame = tk.Frame(self.root)
        fov_frame.pack()

        self.x_px = tk.Entry(fov_frame, width=w, validate="key", validatecommand=(validate_func, "%P"))
        self.x_px.insert(0, "4096")
        self.x_px.pack(side=tk.LEFT)
        self.y_px = tk.Entry(fov_frame, width=w, validate="key", validatecommand=(validate_func, "%P"))
        self.y_px.insert(0, "3000")
        self.y_px.pack(side=tk.LEFT)
        self.x_mm = tk.Entry(fov_frame, width=w, validate="key", validatecommand=(validate_func, "%P"))
        self.x_mm.insert(0, "2.355")
        self.x_mm.pack(side=tk.LEFT)
        self.y_mm = tk.Entry(fov_frame, width=w, validate="key", validatecommand=(validate_func, "%P"))
        self.y_mm.insert(0, "1.725")
        self.y_mm.pack(side=tk.LEFT)

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()

        limit_label = tk.Label(self.root, text="Enter Limit (in microns):")
        limit_label.pack()
        self.limit_entry = tk.Entry(self.root, width=15, validate="key", validatecommand=(validate_func, "%P"))
        self.limit_entry.insert(0, "150")
        self.limit_entry.pack()

        limit_label = tk.Label(self.root, text="Enter Image height you are comfortable with (in pixels):")
        limit_label.pack()
        self.height_entry = tk.Entry(self.root, width=15, validate="key", validatecommand=(validate_func, "%P"))
        self.height_entry.insert(0, "1700")
        self.height_entry.pack()

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()
        instructions_label = tk.Label(self.root, wraplength=700, text="Once you click the manual start button below an "
                                                                      "image will open. Using your mouse click on a "
                                                                      "feature you can continuously identify. Press "
                                                                      "any key on your keyboard to go to the next "
                                                                      "photo. Once done your graph will open")
        instructions_label.pack()

        button_frame = tk.Frame(self.root)
        button_frame.pack()

        self.start_clicker_button = tk.Button(button_frame, text="Start Manual Clicker", command=self.start_clicker,
                                              width=20, state=tk.DISABLED)
        self.start_clicker_button.pack(side=tk.LEFT)
        self.start_auto_button = tk.Button(button_frame, text="Start Auto Process", command=self.start_auto,
                                           width=20, state=tk.DISABLED)
        self.start_auto_button.pack(side=tk.LEFT)

    def camera_selection_custom(self):
        self.x_px.config(state=tk.NORMAL)
        self.y_px.config(state=tk.NORMAL)
        self.x_mm.config(state=tk.NORMAL)
        self.y_mm.config(state=tk.NORMAL)

    def camera_selection_basler(self):
        self.x_px.config(state=tk.NORMAL)
        self.y_px.config(state=tk.NORMAL)
        self.x_mm.config(state=tk.NORMAL)
        self.y_mm.config(state=tk.NORMAL)
        self.x_px.delete(0, tk.END)
        self.y_px.delete(0, tk.END)
        self.x_mm.delete(0, tk.END)
        self.y_mm.delete(0, tk.END)
        self.x_px.insert(0, "4096")
        self.y_px.insert(0, "3000")
        self.x_mm.insert(0, "2.355")
        self.y_mm.insert(0, "1.725")
        self.x_px.config(state=tk.DISABLED)
        self.y_px.config(state=tk.DISABLED)
        self.x_mm.config(state=tk.DISABLED)
        self.y_mm.config(state=tk.DISABLED)
    
    def camera_selection_cognex(self):
        self.x_px.config(state=tk.NORMAL)
        self.y_px.config(state=tk.NORMAL)
        self.x_mm.config(state=tk.NORMAL)
        self.y_mm.config(state=tk.NORMAL)
        self.x_px.delete(0, tk.END)
        self.y_px.delete(0, tk.END)
        self.x_mm.delete(0, tk.END)
        self.y_mm.delete(0, tk.END)
        self.x_px.insert(0, "1024")
        self.y_px.insert(0, "768")
        self.x_mm.insert(0, "31.127")
        self.y_mm.insert(0, "23.346")
        self.x_px.config(state=tk.DISABLED)
        self.y_px.config(state=tk.DISABLED)
        self.x_mm.config(state=tk.DISABLED)
        self.y_mm.config(state=tk.DISABLED)

    def start_clicker(self):
        self.camera_cognex.config(state="disabled")
        self.camera_basler.config(state="disabled")
        self.camera_custom.config(state="disabled")
        self.open_folder_button.config(state=tk.DISABLED)
        self.start_clicker_button.config(state=tk.DISABLED)

        if self.limit_entry.get().isdigit() and self.height_entry.get().isdigit():
            limit = self.limit_entry.get()
            height = self.height_entry.get()
            camera = self.camera_selected.get()
            x_px = self.x_px.get()
            y_px = self.y_px.get()
            x_mm = self.x_mm.get()
            y_mm = self.y_mm.get()

            process = Clicker(self.path, x_px, y_px, x_mm, y_mm, int(limit), int(height))
            success, self.img_path, title = process.run_clicker()

            self.open_folder_button.config(state=tk.NORMAL)
            self.start_clicker_button.config(state=tk.NORMAL)

            if success and not self.already_added_graph:
                self.already_added_graph = True
                self.add_graph()

            if success:
                self.output_images[title] = self.img_path

                self.add_button(title)

                self.camera_cognex.config(state="normal")
                self.camera_basler.config(state="normal")
                self.camera_custom.config(state="normal")
                self.open_folder_button.config(state=tk.NORMAL)
                self.start_clicker_button.config(state=tk.NORMAL)

    def start_auto(self):
        pass

    def add_graph(self):
        image_placeholder = PhotoImage()
        image_placeholder = image_placeholder.subsample(2, 3)
        self.image_label = tk.Label(self.root, image=image_placeholder)
        self.image_label.pack()

        self.image_button_frame = tk.Frame(self.root)
        self.image_button_frame.pack()

        add_open = tk.Button(self.root, text="Open Output Folder", command=self.open_directory)
        add_open.pack()

    def add_button(self, title):
        add_image_button = tk.Button(self.image_button_frame, text=title,
                                     command=partial(self.add_placeholder_image, title))
        add_image_button.pack(side=tk.LEFT)

    def add_placeholder_image(self, title):
        image_path = self.output_images[title]
        if image_path:
            self.resize_and_display_image(image_path)

    def open_directory(self):
        current_directory = os.getcwd()
        if os.name == 'nt':
            # On Windows, use the 'explorer' command
            subprocess.Popen(['explorer', current_directory], shell=True)
        else:
            # On Linux, use the 'xdg-open' command
            subprocess.Popen(['xdg-open', current_directory])

    def resize_and_display_image(self, image_path):
        image = Image.open(image_path)
        image = image.resize((800, 400))
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference to prevent image from being garbage collected

    def run_gui(self):
        self.root.mainloop()
