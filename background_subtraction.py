import cv2
import tkinter as tk
from tkinter import filedialog, ttk
import os


class BackgroundSubtractionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Subtraction App")

        # Video file selection
        self.video_label = tk.Label(root, text="Video Path:")
        self.video_label.grid(row=0, column=0, padx=5, pady=5)

        self.video_entry = tk.Entry(root, width=50)
        self.video_entry.grid(row=0, column=1, padx=5, pady=5)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_video)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        # Options for toggling displays
        self.display_options_label = tk.Label(root, text="Display Options:")
        self.display_options_label.grid(row=1, column=0, padx=5, pady=5)

        self.show_original_var = tk.BooleanVar(value=True)
        self.show_original_checkbox = tk.Checkbutton(root, text="Original Frame", variable=self.show_original_var)
        self.show_original_checkbox.grid(row=1, column=1, padx=5, pady=5)

        self.show_mask_var = tk.BooleanVar(value=True)
        self.show_mask_checkbox = tk.Checkbutton(root, text="Foreground Mask", variable=self.show_mask_var)
        self.show_mask_checkbox.grid(row=1, column=2, padx=5, pady=5)

        # Option to save processed video
        self.save_video_var = tk.BooleanVar(value=False)
        self.save_video_checkbox = tk.Checkbutton(root, text="Save Processed Video", variable=self.save_video_var)
        self.save_video_checkbox.grid(row=2, column=1, padx=5, pady=5)

        # Start and quit buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_processing)
        self.start_button.grid(row=3, column=1, columnspan=2, pady=5)

        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.grid(row=4, column=1, columnspan=2, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, pady=10)

    def browse_video(self):
        filename = filedialog.askopenfilename(title="Select Video File",
                                              filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")))
        if filename:
            self.video_entry.delete(0, tk.END)
            self.video_entry.insert(0, filename)

    def start_processing(self):
        video_path = self.video_entry.get()
        if not video_path:
            return

        # Check if video file exists
        if not os.path.isfile(video_path):
            print("Invalid file path")
            return

        # Start capturing the video
        cap = cv2.VideoCapture(video_path)

        # Create Background Subtractor object
        back_sub = cv2.createBackgroundSubtractorMOG2()

        # Frame count for progress
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.progress["maximum"] = total_frames

        # Video writer for saving processed video
        save_video = self.save_video_var.get()
        out = None
        if save_video:
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            out = cv2.VideoWriter('out.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height), isColor=False)

        frame_index = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Apply background subtraction
            fg_mask = back_sub.apply(frame)

            # Save frame to video if enabled
            if save_video and out:
                out.write(fg_mask)

            # Display the video and/or the foreground mask based on user settings
            if self.show_original_var.get():
                cv2.imshow('Original Frame', frame)
            if self.show_mask_var.get():
                cv2.imshow('Foreground Mask', fg_mask)

            # Update progress bar
            frame_index += 1
            self.progress["value"] = frame_index
            self.root.update_idletasks()

            # Break on 'q' key press
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()

        if save_video:
            print("Processed video saved as 'out.mp4'")


if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundSubtractionApp(root)
    root.mainloop()
