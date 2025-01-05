import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import json
import threading


class FaceDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Face Detection App")
        self.root.geometry("800x900")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.image_tab = ttk.Frame(self.notebook)
        self.video_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.image_tab, text="Image Processing")
        self.notebook.add(self.video_tab, text="Video Processing")
        self.notebook.add(self.settings_tab, text="Settings")

        self.setup_image_tab()
        self.setup_video_tab()
        self.setup_settings_tab()

        self.image = None
        self.video_capture = None
        self.is_processing_video = False

        self.cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.load_settings()

    def setup_image_tab(self):
        self.upload_button = ttk.Button(self.image_tab, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.detect_button = ttk.Button(self.image_tab, text="Detect Faces", command=self.detect_faces,
                                        state=tk.DISABLED)
        self.detect_button.pack(pady=10)

        self.save_button = ttk.Button(self.image_tab, text="Save Image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        self.display_label = ttk.Label(self.image_tab)
        self.display_label.pack(expand=True)

    def setup_video_tab(self):
        self.video_source = tk.StringVar(value="0")
        self.video_source_entry = ttk.Entry(self.video_tab, textvariable=self.video_source)
        self.video_source_entry.pack(pady=10)

        self.start_video_button = ttk.Button(self.video_tab, text="Start Video Processing",
                                             command=self.start_video_processing)
        self.start_video_button.pack(pady=10)

        self.stop_video_button = ttk.Button(self.video_tab, text="Stop Video Processing",
                                            command=self.stop_video_processing, state=tk.DISABLED)
        self.stop_video_button.pack(pady=10)

        self.video_label = ttk.Label(self.video_tab)
        self.video_label.pack(expand=True)

    def setup_settings_tab(self):
        self.scale_factor = tk.DoubleVar(value=1.1)
        self.min_neighbors = tk.IntVar(value=5)
        self.min_size = tk.IntVar(value=30)

        ttk.Label(self.settings_tab, text="Scale Factor:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.settings_tab, textvariable=self.scale_factor).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.settings_tab, text="Min Neighbors:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.settings_tab, textvariable=self.min_neighbors).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.settings_tab, text="Min Size:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(self.settings_tab, textvariable=self.min_size).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.settings_tab, text="Save Settings", command=self.save_settings).grid(row=3, column=0,
                                                                                             columnspan=2, padx=5,
                                                                                             pady=5)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.image = cv2.imread(file_path)
            self.show_image(self.image)
            self.detect_button.config(state=tk.NORMAL)

    def detect_faces(self):
        if self.image is None:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor.get(),
            minNeighbors=self.min_neighbors.get(),
            minSize=(self.min_size.get(), self.min_size.get())
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(self.image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        self.show_image(self.image)
        self.save_button.config(state=tk.NORMAL)

    def show_image(self, cv_img):
        cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(cv_img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.display_label.imgtk = img_tk
        self.display_label.configure(image=img_tk)

    def save_image(self):
        if self.image is None:
            messagebox.showwarning("Warning", "No processed image to save!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
        if file_path:
            cv2.imwrite(file_path, self.image)
            messagebox.showinfo("Success", "Image saved successfully!")

    def start_video_processing(self):
        try:
            source = int(self.video_source.get())
        except ValueError:
            source = self.video_source.get()

        self.video_capture = cv2.VideoCapture(source)
        if not self.video_capture.isOpened():
            messagebox.showerror("Error", "Could not open video source")
            return

        self.is_processing_video = True
        self.start_video_button.config(state=tk.DISABLED)
        self.stop_video_button.config(state=tk.NORMAL)

        threading.Thread(target=self.process_video, daemon=True).start()

    def stop_video_processing(self):
        self.is_processing_video = False
        if self.video_capture:
            self.video_capture.release()
        self.start_video_button.config(state=tk.NORMAL)
        self.stop_video_button.config(state=tk.DISABLED)


    def process_video(self):
        while self.is_processing_video:
            try:
                ret, frame = self.video_capture.read()
            except:
                break
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor.get(),
                minNeighbors=self.min_neighbors.get(),
                minSize=(self.min_size.get(), self.min_size.get())
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            self.show_video_frame(frame)

        self.video_label.configure(image=None)


    def show_video_frame(self, frame):
        cv_img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(cv_img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.imgtk = img_tk
        self.video_label.configure(image=img_tk)


    def save_settings(self):
        settings = {
            "scale_factor": self.scale_factor.get(),
            "min_neighbors": self.min_neighbors.get(),
            "min_size": self.min_size.get(),
        }

        with open("face_detection_settings.json", "w") as f:
            json.dump(settings, f)

        messagebox.showinfo("Success", "Settings saved successfully!")


    def load_settings(self):
        try:
            with open("face_detection_settings.json", "r") as f:
                settings = json.load(f)

            self.scale_factor.set(settings.get("scale_factor", 1.1))
            self.min_neighbors.set(settings.get("min_neighbors", 5))
            self.min_size.set(settings.get("min_size", 30))
        except FileNotFoundError:
            pass


def main():
    root = tk.Tk()
    app = FaceDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
