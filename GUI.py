import os
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from PIL import Image, ImageTk
from Clicker import Clicker
import subprocess


class GUI:
    def __init__(self):
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
        self.root.geometry("900x800")  # Set the window size

        self.camera_selected = tk.StringVar()
        self.camera_selected.set("Basler")  # Only "Basler" selected initially

        heading_label = tk.Label(self.root, text="Image Repeatability Calculator", font=("Helvetica", 16))
        heading_label.pack()

        instructions_label = tk.Label(self.root, text="Select folder which has photos")
        instructions_label.pack()

        self.open_folder_button = tk.Button(self.root, text="Select Folder", width=20, command=self.open_folder_dialog)
        self.open_folder_button.pack()

        self.selected_folder_label = tk.Label(self.root, text="Selected Folder: ")
        self.selected_folder_label.pack()

        self.folder_selected = tk.BooleanVar()
        self.folder_selected.set(False)

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()

    def open_folder_dialog(self):
        folder_path = filedialog.askdirectory()
        self.path = folder_path
        if folder_path:
            self.selected_folder_label.config(text="Selected Folder: " + folder_path)
            self.add_camera_selection()
            self.folder_selected.set(True)
            self.start_clicker_button.config(state=tk.NORMAL)

    def add_camera_selection(self):
        # Create radio buttons for camera selection
        camera_frame = tk.Frame(self.root)
        camera_frame.pack()
        camera_label = tk.Label(camera_frame, text="Select Camera:")
        camera_label.pack(side=tk.LEFT)

        self.camera_basler = tk.Radiobutton(camera_frame, text="Basler", variable=self.camera_selected, value="Basler",
                                            width=10)
        self.camera_basler.pack(side=tk.LEFT)
        self.camera_cognex = tk.Radiobutton(camera_frame, text="Cognex", variable=self.camera_selected, value="Cognex",
                                            width=10)
        self.camera_cognex.pack(side=tk.LEFT)

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()

        limit_label = tk.Label(self.root, text="Enter Limit (in microns):")
        limit_label.pack()
        self.limit_entry = tk.Entry(self.root, width=15)
        self.limit_entry.insert(0, "150")
        self.limit_entry.pack()

        limit_label = tk.Label(self.root, text="Enter Image height you are comfortable with (in pixels):")
        limit_label.pack()
        self.height_entry = tk.Entry(self.root, width=15)
        self.height_entry.insert(0, "1700")
        self.height_entry.pack()

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()
        instructions_label = tk.Label(self.root, wraplength=700, text="Once you click the Start button below an image "
                                                                      "will open. Using your mouse click on a feature "
                                                                      "you can continuously identify. Press any key on "
                                                                      "your keyboard to go to the next photo. Once "
                                                                      "done your graph will open")
        instructions_label.pack()

        self.start_clicker_button = tk.Button(self.root, text="Start Process", command=self.start_clicker, width=10,
                                              state=tk.DISABLED, )
        self.start_clicker_button.pack()

    def start_clicker(self):
        self.camera_cognex.config(state="disabled")
        self.camera_basler.config(state="disabled")
        self.open_folder_button.config(state=tk.DISABLED)
        self.start_clicker_button.config(state=tk.DISABLED)

        if self.limit_entry.get().isdigit() and self.height_entry.get().isdigit():
            limit = self.limit_entry.get()
            height = self.height_entry.get()
            camera = self.camera_selected.get()

            process = Clicker(self.path, camera, int(limit), int(height))
            success, self.img_path = process.run_clicker()

            self.open_folder_button.config(state=tk.NORMAL)
            self.start_clicker_button.config(state=tk.NORMAL)

            if success:
                self.add_graph()
                print(self.img_path)

    def add_graph(self):
        self.image_placeholder = PhotoImage()
        self.image_placeholder = self.image_placeholder.subsample(2, 3)
        self.image_label = tk.Label(self.root, image=self.image_placeholder)
        self.image_label.pack()

        add_image_button = tk.Button(self.root, text="Show Graph", command=self.add_placeholder_image)
        add_image_button.pack()

        add_open = tk.Button(self.root, text="Open Folder", command=self.open_directory)
        add_open.pack()

    def add_placeholder_image(self):
        image_path = self.img_path
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
