import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter


class GlitchArtGenerator:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("Advanced Image Glitch Art Generator")
        self.app.geometry("1000x800")

        self.canvas = tk.Canvas(self.app, width=800, height=600)
        self.canvas.pack(pady=10)

        self.btn_frame = tk.Frame(self.app)
        self.btn_frame.pack(pady=10)

        self.effect_frame = tk.Frame(self.app)
        self.effect_frame.pack(pady=10)

        self.create_buttons()
        self.create_effect_options()

        self.original_image = None
        self.current_image = None
        self.undo_stack = []
        self.redo_stack = []

        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app.mainloop()

    def create_buttons(self):
        buttons = [
            ("Load Image", self.load_image),
            ("Apply Glitch", self.glitch_image),
            ("Save Image", self.save_image),
            ("Undo", self.undo),
            ("Redo", self.redo),
            ("Reset", self.reset_image)
        ]

        for text, command in buttons:
            btn = tk.Button(self.btn_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)

    def create_effect_options(self):
        effects = [
            ("Brightness", self.adjust_brightness),
            ("Contrast", self.adjust_contrast),
            ("Saturation", self.adjust_saturation),
            ("Blur", self.apply_blur),
            ("Sharpen", self.apply_sharpen),
            ("Pixelate", self.apply_pixelate),
            ("Invert Colors", self.invert_colors),
            ("Add Noise", self.add_noise),
            ("Vignette", self.apply_vignette),
            ("Retro Filter", self.apply_retro_filter)
        ]

        for text, command in effects:
            btn = tk.Button(self.effect_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=3)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.current_image = self.original_image.copy()
            self.show_image(self.current_image)
            self.undo_stack.clear()
            self.redo_stack.clear()

    def show_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_pil = image_pil.resize((800, 600), Image.LANCZOS)
        image_tk = ImageTk.PhotoImage(image_pil)
        self.canvas.create_image(0, 0, anchor='nw', image=image_tk)
        self.canvas.image_tk = image_tk

    def apply_glitch(self, image, intensity):
        glitched_image = image.copy()
        height, width, _ = image.shape
        for _ in range(intensity):
            offset = np.random.randint(-10, 11, size=3)
            slice_height = np.random.randint(height//20, height//5)
            start_row = np.random.randint(0, height - slice_height)
            glitched_image[start_row:start_row+slice_height] = np.roll(
                glitched_image[start_row:start_row+slice_height], offset, axis=1
            )
        return glitched_image

    def glitch_image(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        intensity = simpledialog.askinteger("Input", "Enter glitch intensity (1-20)", minvalue=1, maxvalue=20)
        if intensity is not None:
            self.add_to_undo_stack()
            glitched_image = self.apply_glitch(self.current_image, intensity)
            self.current_image = glitched_image
            self.show_image(self.current_image)

    def save_image(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image to save")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("BMP files", "*.bmp")])
        if file_path:
            cv2.imwrite(file_path, self.current_image)
            messagebox.showinfo("Success", "Image saved as {}".format(file_path))

    def add_to_undo_stack(self):
        self.undo_stack.append(self.current_image.copy())
        self.redo_stack.clear()

    def undo(self):
        if len(self.undo_stack) > 0:
            self.redo_stack.append(self.current_image.copy())
            self.current_image = self.undo_stack.pop()
            self.show_image(self.current_image)

    def redo(self):
        if len(self.redo_stack) > 0:
            self.undo_stack.append(self.current_image.copy())
            self.current_image = self.redo_stack.pop()
            self.show_image(self.current_image)

    def reset_image(self):
        if self.original_image is not None:
            self.add_to_undo_stack()
            self.current_image = self.original_image.copy()
            self.show_image(self.current_image)

    def adjust_brightness(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        factor = simpledialog.askfloat("Input", "Enter brightness factor (0.1-2.0)", minvalue=0.1, maxvalue=2.0)
        if factor is not None:
            self.add_to_undo_stack()
            image_pil = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
            enhancer = ImageEnhance.Brightness(image_pil)
            enhanced_image = enhancer.enhance(factor)
            self.current_image = cv2.cvtColor(np.array(enhanced_image), cv2.COLOR_RGB2BGR)
            self.show_image(self.current_image)

    def adjust_contrast(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        factor = simpledialog.askfloat("Input", "Enter contrast factor (0.1-2.0)", minvalue=0.1, maxvalue=2.0)
        if factor is not None:
            self.add_to_undo_stack()
            image_pil = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
            enhancer = ImageEnhance.Contrast(image_pil)
            enhanced_image = enhancer.enhance(factor)
            self.current_image = cv2.cvtColor(np.array(enhanced_image), cv2.COLOR_RGB2BGR)
            self.show_image(self.current_image)

    def adjust_saturation(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        factor = simpledialog.askfloat("Input", "Enter saturation factor (0.0-2.0)", minvalue=0.0, maxvalue=2.0)
        if factor is not None:
            self.add_to_undo_stack()
            image_pil = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
            enhancer = ImageEnhance.Color(image_pil)
            enhanced_image = enhancer.enhance(factor)
            self.current_image = cv2.cvtColor(np.array(enhanced_image), cv2.COLOR_RGB2BGR)
            self.show_image(self.current_image)

    def apply_blur(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        radius = simpledialog.askinteger("Input", "Enter blur radius (1-10)", minvalue=1, maxvalue=10)
        if radius is not None:
            self.add_to_undo_stack()
            image_pil = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
            blurred_image = image_pil.filter(ImageFilter.GaussianBlur(radius=radius))
            self.current_image = cv2.cvtColor(np.array(blurred_image), cv2.COLOR_RGB2BGR)
            self.show_image(self.current_image)

    def apply_sharpen(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        self.add_to_undo_stack()
        image_pil = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
        sharpened_image = image_pil.filter(ImageFilter.SHARPEN)
        self.current_image = cv2.cvtColor(np.array(sharpened_image), cv2.COLOR_RGB2BGR)
        self.show_image(self.current_image)

    def apply_pixelate(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        pixel_size = simpledialog.askinteger("Input", "Enter pixel size (2-50)", minvalue=2, maxvalue=50)
        if pixel_size is not None:
            self.add_to_undo_stack()
            height, width = self.current_image.shape[:2]
            small = cv2.resize(self.current_image, (width // pixel_size, height // pixel_size), interpolation=cv2.INTER_LINEAR)
            self.current_image = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)
            self.show_image(self.current_image)

    def invert_colors(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        self.add_to_undo_stack()
        self.current_image = cv2.bitwise_not(self.current_image)
        self.show_image(self.current_image)

    def add_noise(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        amount = simpledialog.askinteger("Input", "Enter noise amount (1-50)", minvalue=1, maxvalue=50)
        if amount is not None:
            self.add_to_undo_stack()
            noise = np.random.randint(0, amount, self.current_image.shape, dtype=np.uint8)
            self.current_image = cv2.add(self.current_image, noise)
            self.show_image(self.current_image)

    def apply_vignette(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        intensity = simpledialog.askfloat("Input", "Enter vignette intensity (0.0-1.0)", minvalue=0.0, maxvalue=1.0)
        if intensity is not None:
            self.add_to_undo_stack()
            rows, cols = self.current_image.shape[:2]
            kernel_x = cv2.getGaussianKernel(cols, cols/2)
            kernel_y = cv2.getGaussianKernel(rows, rows/2)
            kernel = kernel_y * kernel_x.T
            mask = 255 * kernel / np.linalg.norm(kernel)
            mask = mask * intensity + (1 - intensity)
            self.current_image = self.current_image * mask[:,:,np.newaxis]
            self.current_image = np.clip(self.current_image, 0, 255).astype(np.uint8)
            self.show_image(self.current_image)

    def apply_retro_filter(self):
        if self.current_image is None:
            messagebox.showerror("Error", "No image loaded")
            return
        self.add_to_undo_stack()
        image_pil = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
        r, g, b = image_pil.split()
        r = r.point(lambda i: i * 1.3)
        b = b.point(lambda i: i * 0.8)
        image_pil = Image.merge('RGB', (r, g, b))
        enhancer = ImageEnhance.Contrast(image_pil)
        image_pil = enhancer.enhance(1.2)
        self.current_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        self.show_image(self.current_image)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.app.destroy()

if __name__ == "__main__":
    GlitchArtGenerator()
