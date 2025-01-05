import cv2
import numpy as np
from tkinter import Tk, filedialog, Button, Label
from tkinter import N, S, E, W

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")])
    if file_path:
        convert_to_grayscale(file_path)

def convert_to_grayscale(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow('Grayscale Image', gray_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def setup_ui(root):
    root.title("Image Grayscale Converter")
    root.geometry("300x150")
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    label = Label(root, text="Select an Image to Convert to Grayscale", wraplength=250)
    label.grid(row=0, column=0, padx=10, pady=10, sticky=N)

    open_button = Button(root, text="Open Image", command=open_file)
    open_button.grid(row=1, column=0, padx=10, pady=10, sticky=S+E+W)

if __name__ == "__main__":
    root = Tk()
    setup_ui(root)
    root.mainloop()
