import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk


def rotate_document(image):
	# Convert the image to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Threshold the image: white areas become white (255), and all others are black (0)
	_, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

	# Invert the binary image: non-white areas are now white, and white areas are black
	binary = cv2.bitwise_not(binary)

	# Find all non-white pixels (i.e., content areas)
	coords = np.column_stack(np.where(binary > 0))

	# If no content is found, return the original image
	if len(coords) == 0:
		return image

	# Get the minimum area bounding box around the content
	rect = cv2.minAreaRect(coords)

	# Get the rotation angle from the bounding box
	angle = rect[2]
	if angle < 45:
		angle = - angle
	else:
		angle = 90 - angle

	# Get the center of the image
	(h, w) = image.shape[:2]
	center = (w // 2, h // 2)

	# Get the rotation matrix
	M = cv2.getRotationMatrix2D(center, angle, 1.0)

	# Perform the rotation
	rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

	return rotated


def load_image():
	filepath = filedialog.askopenfilename()
	if not filepath:
		return
	image = cv2.imread(filepath)
	aligned_image = rotate_document(image)
	if aligned_image is not None:
		display_image(aligned_image)
	else:
		messagebox.showerror("Error", "Could not detect document content!")


def display_image(cv_img):
	cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
	img = Image.fromarray(cv_img)
	img = ImageTk.PhotoImage(img)
	canvas.create_image(0, 0, anchor=tk.NW, image=img)
	canvas.image = img


# Set up the Tkinter interface
app = tk.Tk()
app.title("Document Aligner")
app.geometry("800x900")

canvas = tk.Canvas(app, width=800, height=800)
canvas.pack()

button_frame = tk.Frame(app)
button_frame.pack(fill=tk.X, side=tk.BOTTOM)

load_btn = tk.Button(button_frame, text="Load Image", command=load_image)
load_btn.pack(side=tk.LEFT, padx=10, pady=10)

app.mainloop()
