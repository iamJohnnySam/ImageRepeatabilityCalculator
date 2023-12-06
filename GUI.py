import os
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from PIL import Image, ImageTk
import grapher
from Clicker import Clicker
import subprocess
from functools import partial
from auto_matcher import AutoMatcher
from documenter import Documenter
from kri_log_decoder import KRILogDecoder
from template_matcher import TemplateMatcher
from tkinter import messagebox


def open_directory():
    current_directory = os.getcwd()
    if os.name == 'nt':
        # On Windows, use the 'explorer' command
        subprocess.Popen(['explorer', current_directory], shell=True)
    else:
        # On Linux, use the 'xdg-open' command
        subprocess.Popen(['xdg-open', current_directory])


def on_validate(p):
    # This function is called when the Entry is being edited
    if p == "" or p.replace(".", "", 1).isdigit():
        return True
    return False


class GUI:
    checkbox_frame = None
    right_frame = None
    start_tm_auto_button = None
    image_button_frame = None
    camera_custom = None
    start_auto_button = None
    start_kri_auto_button = None
    image_label = None
    image_placeholder = None
    camera_cognex = None
    camera_basler = None
    btn_gen_report = None

    def __init__(self):
        self.output_images = {}
        self.output_coordinates = {}
        self.checked_images = []
        self.already_added_content = False
        self.x_px = None
        self.y_px = None
        self.x_mm = None
        self.y_mm = None
        self.already_added_graph = False
        self.img_path = None
        self.height_entry = None
        self.path = None
        self.start_clicker_button = None
        self.limit_entry = None
        self.root = tk.Tk()
        self.root.title("Image Repeatability Calculator")
        self.root.geometry("950x800")  # Set the window size

        self.camera_selected = tk.StringVar()
        self.camera_selected.set("Basler")  # Only "Basler" selected initially

        heading_label = tk.Label(self.root, text="Image Repeatability Calculator", font=("Helvetica", 16))
        heading_label.pack()

        folder_select_frame = tk.Frame(self.root)
        folder_select_frame.pack()

        instructions_label = tk.Label(folder_select_frame, text="Select folder which has photos")
        instructions_label.pack(side=tk.LEFT)

        self.open_folder_button = tk.Button(folder_select_frame, text="Select Folder", width=20,
                                            command=self.open_folder_dialog,
                                            state=tk.NORMAL)
        self.open_folder_button.pack(side=tk.RIGHT)

        self.selected_folder_label = tk.Label(self.root, text="Selected Folder: ")
        self.selected_folder_label.pack()

        self.folder_selected = tk.BooleanVar()
        self.folder_selected.set(False)

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()

        self.graph_type = tk.StringVar()
        self.graph_type.set("line")

    def show_info_popup(self, msg):
        info_popup = tk.Toplevel(self.root)
        info_popup.title("How to Use")
        info_popup.geometry("400x200")

        message_label = tk.Label(info_popup, text=msg, wraplength=350, justify=tk.LEFT)
        message_label.pack(padx=10, pady=10)

        ok_button = tk.Button(info_popup, text="OK", command=info_popup.destroy, width=20)
        ok_button.pack(side=tk.BOTTOM, pady=10)

        # Wait for the info_popup window to be closed
        self.root.wait_window(info_popup)

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
            self.start_auto_button.config(state=tk.NORMAL)
            self.start_tm_auto_button.config(state=tk.NORMAL)
            self.start_kri_auto_button.config(state=tk.NORMAL)

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

        validate_func = self.root.register(on_validate)

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

        limit_frame = tk.Frame(self.root)
        limit_frame.pack()

        limit_label = tk.Label(limit_frame, text="Enter Given Control Limit (microns): ")
        limit_label.pack(side=tk.LEFT)
        self.limit_entry = tk.Entry(limit_frame, width=15, validate="key", validatecommand=(validate_func, "%P"))
        self.limit_entry.insert(0, "150")
        self.limit_entry.pack(side=tk.LEFT)

        height_frame = tk.Frame(self.root)
        height_frame.pack()

        limit_label = tk.Label(height_frame, text="Enter Display Image height (pixels): ")
        limit_label.pack(side=tk.LEFT)
        self.height_entry = tk.Entry(height_frame, width=15, validate="key", validatecommand=(validate_func, "%P"))
        self.height_entry.insert(0, "1700")
        self.height_entry.pack(side=tk.LEFT)

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()

        button_frame = tk.Frame(self.root)
        button_frame.pack()

        self.start_clicker_button = tk.Button(button_frame, text="Manual Clicker", command=self.start_clicker,
                                              width=20, state=tk.DISABLED, padx=5, pady=5)
        self.start_clicker_button.pack(side=tk.LEFT)
        self.start_auto_button = tk.Button(button_frame, text="BF Matcher", command=self.start_auto,
                                           width=20, state=tk.DISABLED, padx=5, pady=5)
        self.start_auto_button.pack(side=tk.LEFT)
        self.start_tm_auto_button = tk.Button(button_frame, text="Template Matcher", command=self.start_tm_auto,
                                              width=20, state=tk.DISABLED, padx=5, pady=5)
        self.start_tm_auto_button.pack(side=tk.LEFT)
        self.start_kri_auto_button = tk.Button(button_frame, text="KRI Log File", command=self.start_kri_log,
                                               width=20, state=tk.DISABLED, padx=5, pady=5)
        self.start_kri_auto_button.pack(side=tk.LEFT)

        grapher_frame = tk.Frame(self.root)
        grapher_frame.pack()

        left_frame = tk.Frame(grapher_frame)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.right_frame = tk.Frame(grapher_frame)
        self.right_frame.pack(side=tk.LEFT, padx=10, pady=10)

        graph_type_frame = tk.Frame(left_frame)
        graph_type_frame.pack()

        radio_line = tk.Radiobutton(graph_type_frame, text="line", variable=self.graph_type, value="line", width=10)
        radio_line.pack(side=tk.LEFT)
        radio_scatter = tk.Radiobutton(graph_type_frame, text="scatter", variable=self.graph_type,
                                       value="scatter", width=10)
        radio_scatter.pack(side=tk.LEFT)

        self.checkbox_frame = tk.Frame(left_frame)
        self.checkbox_frame.pack()

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

        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, "1600")
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

        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, "1024")
        self.x_px.config(state=tk.DISABLED)
        self.y_px.config(state=tk.DISABLED)
        self.x_mm.config(state=tk.DISABLED)
        self.y_mm.config(state=tk.DISABLED)

    def disable_selections(self):
        self.camera_cognex.config(state="disabled")
        self.camera_basler.config(state="disabled")
        self.camera_custom.config(state="disabled")
        self.open_folder_button.config(state=tk.DISABLED)
        self.start_clicker_button.config(state=tk.DISABLED)
        self.x_px.config(state=tk.DISABLED)
        self.y_px.config(state=tk.DISABLED)
        self.x_mm.config(state=tk.DISABLED)
        self.y_mm.config(state=tk.DISABLED)
        self.start_tm_auto_button.config(state="disabled")
        self.start_auto_button.config(state="disabled")
        self.start_kri_auto_button.config(state="disabled")
        self.start_clicker_button.config(state="disabled")

    def enable_selections(self):
        self.camera_cognex.config(state="normal")
        self.camera_basler.config(state="normal")
        self.camera_custom.config(state="normal")
        self.open_folder_button.config(state=tk.NORMAL)
        self.start_clicker_button.config(state=tk.NORMAL)
        if self.camera_selected.get() == "Custom":
            self.x_px.config(state=tk.NORMAL)
            self.y_px.config(state=tk.NORMAL)
            self.x_mm.config(state=tk.NORMAL)
            self.y_mm.config(state=tk.NORMAL)
        self.start_tm_auto_button.config(state="normal")
        self.start_auto_button.config(state="normal")
        self.start_kri_auto_button.config(state="normal")
        self.start_clicker_button.config(state="normal")

    def start_clicker(self):
        self.disable_selections()
        msg = "Using your mouse, click on a feature you can continuously identify. Press any key on your keyboard to" \
              "go to the next photo. Once you have completed all photos in your folder your graph will be generated."
        self.show_info_popup(msg)

        if self.limit_entry.get().isdigit() and self.height_entry.get().isdigit():
            process = Clicker(self.path,
                              self.x_px.get(),
                              self.y_px.get(),
                              self.x_mm.get(),
                              self.y_mm.get(),
                              int(self.limit_entry.get()),
                              int(self.height_entry.get()))
            success, img_path, title, coordinates = process.run_clicker()
            self.add_graph_button(success, img_path, title, coordinates)
        self.enable_selections()

    def start_tm_auto(self):
        self.disable_selections()
        msg = "The first photo will open. Use your mouse to drag and select a suitable template to match other photos" \
              ". Once completed press any key on your keyboard. The selected template will open. Press any key on " \
              "your keyboard to continue template matching process."
        self.show_info_popup(msg)

        if self.limit_entry.get().isdigit() and self.height_entry.get().isdigit():
            process = TemplateMatcher(self.path,
                                      self.x_px.get(),
                                      self.y_px.get(),
                                      self.x_mm.get(),
                                      self.y_mm.get(),
                                      int(self.limit_entry.get()),
                                      int(self.height_entry.get()))
            success, img_path, title, coordinates = process.run_matcher()
            self.add_graph_button(success, img_path, title, coordinates)
        self.enable_selections()

    def start_auto(self):
        self.disable_selections()
        msg = "An image processed photo will be opened to show the template that is used to brute force match" \
              "features to the rest of the photos. Press any key on your keyboard to continue."
        self.show_info_popup(msg)
        if self.limit_entry.get().isdigit() and self.height_entry.get().isdigit():
            process = AutoMatcher(self.path,
                                  self.x_px.get(),
                                  self.y_px.get(),
                                  self.x_mm.get(),
                                  self.y_mm.get(),
                                  int(self.limit_entry.get()),
                                  int(self.height_entry.get()))
            success, img_path, title, coordinates = process.run_bf_matcher()
            self.add_graph_button(success, img_path, title, coordinates)
        self.enable_selections()

    def start_kri_log(self):
        self.disable_selections()
        # msg = "Select KRI Log file for cycling."
        # self.show_info_popup(msg)

        folder_path = filedialog.askopenfile(title='Select KRI file', filetypes=[("Log files", "*.log")])
        if folder_path:
            process = KRILogDecoder(folder_path, int(self.limit_entry.get()))
            success, img_path, title, coordinates = process.run_decoder()
            self.add_graph_button(success, img_path, title, coordinates)

        self.enable_selections()

    def add_graph_button(self, success, img_path, title, coordinates):
        if success and not self.already_added_graph:
            self.already_added_graph = True
            self.add_graph()

        if success and title not in self.output_images.keys():
            self.output_images[title] = img_path
            self.output_coordinates[title] = coordinates
            self.add_button(title)

    def add_graph(self):
        image_placeholder = PhotoImage()
        image_placeholder = image_placeholder.subsample(2, 3)
        self.image_label = tk.Label(self.right_frame, image=image_placeholder)
        self.image_label.pack()

        self.image_button_frame = tk.Frame(self.checkbox_frame, width=750)
        self.image_button_frame.pack()

        add_open = tk.Button(self.root, text="Open Output Folder", command=open_directory)
        add_open.pack()

        gap_label = tk.Label(self.root, text="")
        gap_label.pack()

        self.btn_gen_report = tk.Button(self.root, text="Generate Report", command=self.generate_report)
        self.btn_gen_report.pack()
        self.btn_gen_report.config(state=tk.DISABLED)

    def generate_report(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Document Details")
        form_window.geometry("400x200")  # Set the window size

        heading_label = tk.Label(form_window, text="Generate Report", font=("Helvetica", 16))
        heading_label.pack()

        gap_label = tk.Label(form_window, text="")
        gap_label.pack()

        def submit_form():
            messagebox.showinfo("Feature in Development")
            doc = Documenter(name_entry.get(), author_entry.get())
            doc.create_document()
            form_window.destroy()

        name_label = tk.Label(form_window, text="Device Serial Number:")
        name_label.pack()

        name_entry = tk.Entry(form_window)
        name_entry.pack()
        name_entry.insert(0, "90-SR23xxx-18-xx")

        author_label = tk.Label(form_window, text="Document Author:")
        author_label.pack()

        author_entry = tk.Entry(form_window)
        author_entry.pack()
        author_entry.insert(0, os.getlogin())

        submit_button = tk.Button(form_window, text="Submit", command=submit_form)
        submit_button.pack()

    def add_button(self, title):
        add_image_button = tk.Checkbutton(self.image_button_frame, text=title, variable=title,
                                          command=partial(self.checked_box, title))
        add_image_button.pack()

    def checked_box(self, title):
        if title in self.checked_images:
            self.checked_images.remove(title)
        else:
            self.checked_images.append(title)

        if len(self.checked_images) == 1:
            self.add_placeholder_image(self.checked_images[0])
        elif len(self.checked_images) > 1:
            self.checked_images.sort()
            print(self.checked_images)
            c_title = ""
            f_val = 0
            for val in self.checked_images:
                if f_val != 0:
                    c_title = c_title + ", "
                f_val = f_val + 1
                c_title = c_title + val
            if c_title in self.output_images:
                self.add_placeholder_image(c_title)
            else:
                plot_values = {}
                for a in self.checked_images:
                    plot_values[a] = self.output_coordinates[a]
                file = grapher.combined_grapher(int(self.limit_entry.get()), plot_values, c_title)
                self.output_images[c_title] = file
                self.add_placeholder_image(c_title)

        if len(self.checked_images) > 0:
            self.btn_gen_report.config(state=tk.NORMAL)
        else:
            self.btn_gen_report.config(state=tk.DISABLED)

    def add_placeholder_image(self, title):
        image_path = self.output_images[title][self.graph_type.get()]
        print("Showing ", self.output_images[title])
        if image_path:
            self.resize_and_display_image(image_path)

    def resize_and_display_image(self, image_path):
        image = Image.open(image_path)
        image = image.resize((800, 400))
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference to prevent image from being garbage collected

    def run_gui(self):
        self.root.mainloop()
