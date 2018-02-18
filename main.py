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
filename = ''

def open_image():
    global img_input, left_image
    filepath = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"), ("all files","*.*")))
    img_input = ImageTk.PhotoImage(Image.open(filepath))
    left_image.configure(image=img_input)
    left_image.image = img_input
    ## Read image matrix di sini ya Ali. Pake filepath

def upload_file():
    global filename, right_image, filename_label
    filepath = filedialog.askopenfilename(initialdir = "/",title = "Select file")
    # Add code to read file content
    content = 'Ini isi filenya'

    splits = filepath.split('/')
    filename = splits[len(splits)-1]
    right_image.configure(text=content)
    right_image.configure(image=None)
    right_image.image = None
    filename_label.configure(text='Filename: ' + filename)

def start():
    if action.get() == ENCRYPT:
        # Kode encrypt
        pass
    else:
        # Kode decrypt
        pass

def change_action():
    global left_label, middle_label, middle_button, right_button
    if action.get() == ENCRYPT:
        left_label.configure(text="Original Image")
        middle_label.configure(text="BPCS Image")
        middle_button.configure(state=tk.NORMAL)
        right_button.configure(text="Upload File")
    else:
        left_label.configure(text="BPCS Image")
        middle_label.configure(text="-")
        middle_button.configure(state=tk.DISABLED)
        right_button.configure(text="Save Extracted")

# Variables
action = tk.IntVar()
action.set(ENCRYPT)
cgc = tk.BooleanVar()
cgc.set(True)
sequential = tk.BooleanVar()
sequential.set(True)

# Top frame
title_frame = tk.Frame(root)
title_label = tk.Label(title_frame,
		         text="BPCS GAGA OH LALA",
		         fg = "dark green",
		         font = "Helvetica 16 bold italic").pack(pady=10)
title_frame.pack()

# Main Frame
main_frame = tk.Frame(root)
panel_width = 300
panel_height = 300

# Left frame
left_frame = tk.Frame(main_frame)
left_label = tk.Label(left_frame,
                text="Original Image",
                fg = "dark green",
                font = "Helvetica 14 bold")
left_label.pack(pady=5)
left_image = tk.Label(left_frame,
                image=img_input,
                borderwidth=2,
                relief="groove",
                width=panel_width, height=panel_height)
left_image.pack(pady=5)
left_button = tk.Button(left_frame,
                text="Upload",
                fg="blue",
                command=open_image)
left_button.pack(pady=5)
left_frame.pack(side=tk.LEFT, padx=10)

# Middle frame
middle_frame = tk.Frame(main_frame)
middle_label = tk.Label(middle_frame,
                text="BPCS Image",
                fg = "dark green",
                font = "Helvetica 14 bold")
middle_label.pack(pady=5)
middle_image = tk.Label(middle_frame,
                image=img_output,
                borderwidth=2,
                relief="groove",
                width=panel_width, height=panel_height)
middle_image.pack(pady=5)
middle_button = tk.Button(middle_frame,
                text="Save",
                fg="blue",
                command=open_image)
middle_button.pack(pady=5)
middle_frame.pack(side=tk.LEFT, padx=10)

# Right frame
right_frame = tk.Frame(main_frame)
right_label = tk.Label(right_frame,
                text="Message (In Bytes)",
                fg = "dark green",
                font = "Helvetica 14 bold")
right_label.pack(pady=5)
right_image = tk.Label(right_frame,
                borderwidth=2,
                relief="groove",
                width=40, height=20)
right_image.pack(pady=5)
filename_label = tk.Label(right_frame,
                text="Filename: -",
                fg = "black",
                font = "Helvetica 10")
filename_label.pack(pady=5)
right_button = tk.Button(right_frame,
                text="Upload File",
                fg="blue",
                command=upload_file)
right_button.pack(pady=5)
right_frame.pack(side=tk.LEFT, padx=10)

main_frame.pack()

# Bottom frame
bottom_frame = tk.Frame(root)

# Action frame
action_frame = tk.Frame(bottom_frame)
tk.Label(action_frame,
         text="Action",
         justify=tk.LEFT,
         padx=20).pack()
tk.Radiobutton(action_frame,
              text="Encrypt",
              padx=20,
              variable=action,
              command=change_action,
              value=ENCRYPT).pack(anchor=tk.W)
tk.Radiobutton(action_frame,
              text="Decrypt",
              padx=20,
              variable=action,
              command=change_action,
              value=DECRYPT).pack(anchor=tk.W)
action_frame.pack(side=tk.LEFT, pady=5)

# CGC frame
cgc_frame = tk.Frame(bottom_frame)
tk.Label(cgc_frame,
         text="Use CGC?",
         justify=tk.LEFT,
         padx=20).pack()
tk.Radiobutton(cgc_frame,
              text="Yes",
              padx=20,
              variable=cgc,
              value=ENCRYPT).pack(anchor=tk.W)
tk.Radiobutton(cgc_frame,
              text="No",
              padx=20,
              variable=cgc,
              value=DECRYPT).pack(anchor=tk.W)
cgc_frame.pack(side=tk.LEFT, pady=5)

# Sequential frame
sequential_frame = tk.Frame(bottom_frame)
tk.Label(sequential_frame,
         text="Sequential/Random?",
         justify=tk.LEFT,
         padx=20).pack()
tk.Radiobutton(sequential_frame,
              text="Sequential",
              padx=20,
              variable=sequential,
              value=ENCRYPT).pack(anchor=tk.W)
tk.Radiobutton(sequential_frame,
              text="Random",
              padx=20,
              variable=sequential,
              value=DECRYPT).pack(anchor=tk.W)
sequential_frame.pack(side=tk.LEFT, pady=5)

# Input frame
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
                command=start).pack(side=tk.RIGHT, pady=5)

bottom_frame.pack()

root.mainloop()
