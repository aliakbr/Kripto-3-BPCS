import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

root = tk.Tk()

WIDTH = 600
HEIGHT = 600
ENCRYPT = 1
DECRYPT = 2

img_input = ImageTk.PhotoImage(Image.open('gray.png'))
img_output = ImageTk.PhotoImage(Image.open('gray.png'))

def open_image():
    global img_input, left_image
    filepath = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    img_input = ImageTk.PhotoImage(Image.open(filepath))
    left_image.configure(image=img_input)
    left_image.image = img_input

mode = tk.IntVar()
mode.set(ENCRYPT)

# Top frame
title_frame = tk.Frame(root)
title_label = tk.Label(title_frame,
		         text="BPCS GAGA OH LALA",
		         fg = "dark green",
		         font = "Helvetica 16 bold italic").pack(pady=10)
title_frame.pack()

# Main Frame
main_frame = tk.Frame(root)
panel_width = 400
panel_height = 400

# Left frame
left_frame = tk.Frame(main_frame)
left_label = tk.Label(left_frame,
                text="Original Image",
                fg = "dark green",
                font = "Helvetica 14 bold").pack(pady=5)
left_image = tk.Label(left_frame,
                image=img_input,
                borderwidth=2,
                relief="groove",
                width=panel_width, height=panel_height)
left_image.pack(pady=5)
left_button = tk.Button(left_frame,
                text="Upload",
                fg="blue",
                command=open_image).pack(pady=5)
left_frame.pack(side=tk.LEFT, padx=10)

# Middle frame
middle_frame = tk.Frame(main_frame)
middle_label = tk.Label(middle_frame,
                text="BPCS Image",
                fg = "dark green",
                font = "Helvetica 14 bold").pack(pady=5)
middle_image = tk.Label(middle_frame,
                image=img_output,
                borderwidth=2,
                relief="groove",
                width=panel_width, height=panel_height).pack(pady=5)
middle_button = tk.Button(middle_frame,
                text="Save",
                fg="blue",
                command=open_image).pack(pady=5)
middle_frame.pack(side=tk.LEFT, padx=10)

# Right frame
right_frame = tk.Frame(main_frame)
right_label = tk.Label(right_frame,
                text="Message (In Bytes)",
                fg = "dark green",
                font = "Helvetica 14 bold").pack(pady=5)
right_image = tk.Label(right_frame,
                image=img_input,
                borderwidth=2,
                relief="groove",
                width=panel_width, height=panel_height).pack(pady=5)
filename_label = tk.Label(right_frame,
                text="Filename: mimi.exe",
                fg = "black",
                font = "Helvetica 12").pack(pady=5)
right_button = tk.Button(right_frame,
                text="Upload File",
                fg="blue",
                command=open_image).pack(pady=5)
right_frame.pack(side=tk.LEFT, padx=10)

main_frame.pack()

# Bottom frame
bottom_frame = tk.Frame(root)

# Mode frame
mode_frame = tk.Frame(bottom_frame)
tk.Label(mode_frame,
         text="Your Choice",
         justify=tk.LEFT,
         padx=20).pack()
tk.Radiobutton(mode_frame,
              text="Encrypt",
              padx=20,
              variable=mode,
              value=ENCRYPT).pack(anchor=tk.W)
tk.Radiobutton(mode_frame,
              text="Decrypt",
              padx=20,
              variable=mode,
              value=DECRYPT).pack(anchor=tk.W)
mode_frame.pack(side=tk.LEFT, pady=5)

# Input Frame
input_frame = tk.Frame(bottom_frame)
tk.Label(input_frame, text="BPCS Threshold").grid(row=0)
tk.Label(input_frame, text="Key").grid(row=1)
e1 = tk.Entry(input_frame)
e2 = tk.Entry(input_frame)
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
input_frame.pack(side=tk.LEFT, padx=5, pady=5)

# Button
start_button = tk.Button(bottom_frame,
                text="Start",
                fg="blue",
                command=open_image).pack(side=tk.RIGHT, pady=5)

bottom_frame.pack()

root.mainloop()
