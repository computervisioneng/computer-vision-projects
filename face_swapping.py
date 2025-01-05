import cv2
import numpy as np
import dlib
from tkinter import filedialog, messagebox, ttk
from tkinter import *
from PIL import Image, ImageTk
import os
import threading
from scipy.spatial import Delaunay

# Initialize face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# Global variables
image_path_a = ""
image_path_b = ""
panelA = None
panelB = None
panelC = None
root = None
progress_bar = None
is_processing = False

def get_landmarks(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        return None
    return np.matrix([[p.x, p.y] for p in predictor(image, faces[0]).parts()])

def transformation_from_points(points1, points2):
    points1 = points1.astype(np.float64)
    points2 = points2.astype(np.float64)
    c1 = np.mean(points1, axis=0)
    c2 = np.mean(points2, axis=0)
    points1 -= c1
    points2 -= c2
    s1 = np.std(points1)
    s2 = np.std(points2)
    points1 /= s1
    points2 /= s2
    u, s, vt = np.linalg.svd(points1.T * points2)
    r = (u * vt).T
    transform = np.vstack([np.hstack(((s2 / s1) * r, c2.T - (s2 / s1) * r * c1.T)), np.matrix([0., 0., 1.])])
    return transform

def warp_image(image, transform, shape):
    warped = cv2.warpAffine(image, transform[:2], (shape[1], shape[0]), flags=cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    return warped

def correct_colors(im1, im2, landmarks1):
    blur_amount = 0.4 * np.linalg.norm(np.mean(landmarks1[36:42], axis=0) - np.mean(landmarks1[42:48], axis=0))
    blur_amount = int(blur_amount)
    if blur_amount % 2 == 0:
        blur_amount += 1
    im1_blur = cv2.GaussianBlur(im1, (blur_amount, blur_amount), 0)
    im2_blur = cv2.GaussianBlur(im2, (blur_amount, blur_amount), 0)
    return np.clip(im2.astype(np.float32) + im1.astype(np.float32) - im1_blur.astype(np.float32), 0, 255).astype(np.uint8)

def select_image(is_first_image=True):
    global panelA, panelB, image_path_a, image_path_b

    image_path = filedialog.askopenfilename()
    if len(image_path) > 0:
        image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        if is_first_image:
            image_path_a = image_path
            if panelA is None:
                panelA = Label(image=image)
                panelA.image = image
                panelA.pack(side="left", padx=10, pady=10)
            else:
                panelA.configure(image=image)
                panelA.image = image
        else:
            image_path_b = image_path
            if panelB is None:
                panelB = Label(image=image)
                panelB.image = image
                panelB.pack(side="right", padx=10, pady=10)
            else:
                panelB.configure(image=image)
                panelB.image = image

def swap_faces_thread():
    global is_processing
    is_processing = True
    progress_bar.start(10)
    swap_faces()
    progress_bar.stop()
    is_processing = False

def swap_faces():
    global panelC

    if not image_path_a or not image_path_b:
        messagebox.showerror("Error", "Please select both images first.")
        return

    image_a = cv2.imread(image_path_a)
    image_b = cv2.imread(image_path_b)

    landmarks1 = get_landmarks(image_a)
    landmarks2 = get_landmarks(image_b)

    if landmarks1 is None or landmarks2 is None:
        messagebox.showerror("Error", "Could not detect faces. Make sure the detector model is available and faces are clearly visible.")
        return

    # Get bounding box for each face based on landmarks
    x1, y1, w1, h1 = cv2.boundingRect(np.array(landmarks1))
    x2, y2, w2, h2 = cv2.boundingRect(np.array(landmarks2))

    # Get the center of the bounding box for each face
    center1 = (x1 + w1 // 2, y1 + h1 // 2)
    center2 = (x2 + w2 // 2, y2 + h2 // 2)

    # Calculate transformation to swap faces
    transform = transformation_from_points(landmarks1, landmarks2)
    warped_mask = warp_image(image_b, transform, image_a.shape)
    correct_image = correct_colors(image_a, warped_mask, landmarks1)

    # Create mask using convex hull for face region
    mask = np.zeros(image_a.shape, dtype=image_a.dtype)
    cv2.fillConvexPoly(mask, cv2.convexHull(landmarks1), (255, 255, 255))

    # Adjust position for seamless clone, use the center of the bounding box
    final_output1 = cv2.seamlessClone(correct_image, image_a, mask, center1, cv2.NORMAL_CLONE)

    # Repeat the process for the second face
    transform = transformation_from_points(landmarks2, landmarks1)
    warped_mask = warp_image(image_a, transform, image_b.shape)
    correct_image = correct_colors(image_b, warped_mask, landmarks2)

    mask = np.zeros(image_b.shape, dtype=image_b.dtype)
    cv2.fillConvexPoly(mask, cv2.convexHull(landmarks2), (255, 255, 255))

    final_output2 = cv2.seamlessClone(correct_image, image_b, mask, center2, cv2.NORMAL_CLONE)

    # Combine the two output faces
    output_image = np.hstack((final_output1, final_output2))
    output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
    output_image = Image.fromarray(output_image)
    output_image = ImageTk.PhotoImage(output_image)

    if panelC is None:
        panelC = Label(root)
        panelC.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

    panelC.configure(image=output_image)
    panelC.image = output_image

def save_image():
    if panelC is None or not hasattr(panelC, 'image'):
        messagebox.showerror("Error", "No image to save. Please swap faces first.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".png")
    if file_path:
        image = ImageTk.getimage(panelC.image)
        image.save(file_path)
        messagebox.showinfo("Success", "Image saved successfully to {}".format(file_path))

def create_gui():
    global root, progress_bar

    root = Tk()
    root.title("Face Swapper")

    # Create main frame
    main_frame = Frame(root)
    main_frame.pack(padx=10, pady=10)

    # Create buttons frame
    buttons_frame = Frame(main_frame)
    buttons_frame.pack(side="top", fill="x")

    btnSelect1 = Button(buttons_frame, text="Select Image 1", command=lambda: select_image(True))
    btnSelect1.pack(side="left", padx=5)

    btnSelect2 = Button(buttons_frame, text="Select Image 2", command=lambda: select_image(False))
    btnSelect2.pack(side="left", padx=5)

    btnSwap = Button(buttons_frame, text="Swap Faces", command=lambda: threading.Thread(target=swap_faces_thread).start())
    btnSwap.pack(side="left", padx=5)

    # Create save button
    btnSave = Button(main_frame, text="Save Image", command=save_image)
    btnSave.pack(side="top", fill="x", pady=5)

    # Create progress bar
    progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.pack(side="top", fill="x", pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
