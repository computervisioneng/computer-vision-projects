import cv2
import numpy as np
from tkinter import Tk, Label, Button, filedialog, Scale, HORIZONTAL

class LineDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hough Transform Line Detection")
        
        self.label = Label(root, text="Select an Image for Line Detection")
        self.label.pack()

        self.select_button = Button(root, text="Choose Image", command=self.select_image)
        self.select_button.pack()

        self.canny_scale = Scale(root, from_=50, to=150, orient=HORIZONTAL, label='Canny Threshold')
        self.canny_scale.set(100)
        self.canny_scale.pack()

        self.hough_thresh_scale = Scale(root, from_=50, to=200, orient=HORIZONTAL, label='Hough Threshold')
        self.hough_thresh_scale.set(100)
        self.hough_thresh_scale.pack()

        self.detect_button = Button(root, text="Detect Lines", command=self.detect_lines)
        self.detect_button.pack()

        self.image_path = None

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        self.label.config(text="Selected image: {}".format(self.image_path))

    def detect_lines(self):
        if not self.image_path:
            self.label.config(text="No image selected!")
            return

        image = cv2.imread(self.image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, self.canny_scale.get(), self.canny_scale.get() * 2)

        lines = cv2.HoughLines(edges, 1, np.pi / 180, self.hough_thresh_scale.get())
        if lines is not None:
            for rho, theta in lines[:, 0]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imshow('Detected Lines', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = Tk()
    app = LineDetectionApp(root)
    root.mainloop()
