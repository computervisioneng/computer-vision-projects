import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
from matplotlib import pyplot as plt
from PIL import Image, ImageTk


class AdvancedImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Processing Tool")
        self.root.geometry("1200x800")

        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.processing_history = []

        self.create_gui()

    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Control panel (top part)
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Load image button
        load_button = ttk.Button(control_frame, text="Load Image", command=self.load_image)
        load_button.grid(row=0, column=0, padx=5, pady=5)

        # Save image button
        save_button = ttk.Button(control_frame, text="Save Image", command=self.save_image)
        save_button.grid(row=0, column=1, padx=5, pady=5)

        # Histogram equalization button
        equalize_button = ttk.Button(control_frame, text="Equalize Histogram", command=self.equalize_histogram)
        equalize_button.grid(row=0, column=2, padx=5, pady=5)

        # Gaussian blur button
        gaussian_blur_button = ttk.Button(control_frame, text="Gaussian Blur", command=self.gaussian_blur)
        gaussian_blur_button.grid(row=1, column=0, padx=5, pady=5)

        # Median blur button
        median_blur_button = ttk.Button(control_frame, text="Median Blur", command=self.median_blur)
        median_blur_button.grid(row=1, column=1, padx=5, pady=5)

        # Sharpen button
        sharpen_button = ttk.Button(control_frame, text="Sharpen", command=self.sharpen)
        sharpen_button.grid(row=1, column=2, padx=5, pady=5)

        # Edge detection button
        edge_detection_button = ttk.Button(control_frame, text="Edge Detection", command=self.edge_detection)
        edge_detection_button.grid(row=1, column=3, padx=5, pady=5)

        # Brightness adjustment
        brightness_frame = ttk.Frame(control_frame)
        brightness_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        ttk.Label(brightness_frame, text="Brightness:").pack(side=tk.LEFT)
        self.brightness_scale = ttk.Scale(brightness_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=200,
                                          command=self.adjust_brightness)
        self.brightness_scale.set(0)
        self.brightness_scale.pack(side=tk.LEFT)

        # Contrast adjustment
        contrast_frame = ttk.Frame(control_frame)
        contrast_frame.grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        ttk.Label(contrast_frame, text="Contrast:").pack(side=tk.LEFT)
        self.contrast_scale = ttk.Scale(contrast_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL, length=200,
                                        command=self.adjust_contrast)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(side=tk.LEFT)

        # Undo button
        undo_button = ttk.Button(control_frame, text="Undo", command=self.undo)
        undo_button.grid(row=3, column=0, padx=5, pady=5)

        # Reset button
        reset_button = ttk.Button(control_frame, text="Reset", command=self.reset)
        reset_button.grid(row=3, column=2, padx=5, pady=5)

        # Show histogram button
        histogram_button = ttk.Button(control_frame, text="Show Histogram", command=self.show_histogram)
        histogram_button.grid(row=3, column=3, padx=5, pady=5)

        # Image display area (moved to the bottom)
        self.image_frame = ttk.Frame(main_frame, borderwidth=2, relief="sunken")
        self.image_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True, fill=tk.BOTH)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            self.processed_image = self.original_image.copy()
            self.processing_history = [self.original_image.copy()]
            self.display_image(self.processed_image)
        else:
            messagebox.showinfo("Info", "No image selected.")

    def save_image(self):
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(
                title="Save Image As",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                cv2.imwrite(file_path, self.processed_image)
                messagebox.showinfo("Info", "Image saved successfully to {}".format(file_path))
        else:
            messagebox.showwarning("Warning", "No image to save.")

    def display_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_tk = ImageTk.PhotoImage(image_pil)
        self.image_label.config(image=image_tk)
        self.image_label.image = image_tk

    def equalize_histogram(self):
        if self.processed_image is not None:
            gray_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
            equalized_image = cv2.equalizeHist(gray_image)
            self.processed_image = cv2.cvtColor(equalized_image, cv2.COLOR_GRAY2BGR)
            self.update_processing_history()
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def gaussian_blur(self):
        if self.processed_image is not None:
            self.processed_image = cv2.GaussianBlur(self.processed_image, (5, 5), 0)
            self.update_processing_history()
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def median_blur(self):
        if self.processed_image is not None:
            self.processed_image = cv2.medianBlur(self.processed_image, 5)
            self.update_processing_history()
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def sharpen(self):
        if self.processed_image is not None:
            kernel = np.array([[-1, -1, -1],
                               [-1, 9, -1],
                               [-1, -1, -1]])
            self.processed_image = cv2.filter2D(self.processed_image, -1, kernel)
            self.update_processing_history()
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def edge_detection(self):
        if self.processed_image is not None:
            gray_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_image, 100, 200)
            self.processed_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            self.update_processing_history()
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def adjust_brightness(self, value):
        if self.processed_image is not None:
            brightness = int(float(value))
            if brightness != 0:
                if brightness > 0:
                    shadow = brightness
                    highlight = 255
                else:
                    shadow = 0
                    highlight = 255 + brightness
                alpha_b = (highlight - shadow) / 255
                gamma_b = shadow
                self.processed_image = cv2.addWeighted(self.processed_image, alpha_b, self.processed_image, 0, gamma_b)
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def adjust_contrast(self, value):
        if self.processed_image is not None:
            contrast = float(value)
            self.processed_image = cv2.convertScaleAbs(self.processed_image, alpha=contrast, beta=0)
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def update_processing_history(self):
        self.processing_history.append(self.processed_image.copy())

    def undo(self):
        if len(self.processing_history) > 1:
            self.processing_history.pop()
            self.processed_image = self.processing_history[-1]
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No more actions to undo.")

    def reset(self):
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.processing_history = [self.original_image.copy()]
            self.display_image(self.processed_image)
        else:
            messagebox.showwarning("Warning", "No image to reset.")

    def show_histogram(self):
        if self.processed_image is not None:
            gray_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
            plt.hist(gray_image.ravel(), bins=256, histtype='step', color='black')
            plt.title("Histogram")
            plt.show()
        else:
            messagebox.showwarning("Warning", "No image loaded.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedImageProcessingApp(root)
    root.mainloop()
