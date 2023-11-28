from GUI import GUI
import os

if not os.path.exists("images/"):
    os.makedirs("images/")

program = GUI()
program.run_gui()
