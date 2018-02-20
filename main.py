import tkinter as tk
import threading
import os
import shutil
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from bpcs import BPCS

root = tk.Tk()

WIDTH = 600
HEIGHT = 600
INSERT = 1
EXTRACT = 2
PANEL_WIDTH = 300
PANEL_HEIGHT = 300

img_input = ImageTk.PhotoImage(Image.open('gray.png'))
img_output = ImageTk.PhotoImage(Image.open('gray.png'))
img_filepath = ''
plain_filepath = ''
bpcs = BPCS()

def open_image():
    global img_input, img_filepath, img_filename_label, left_image
    img_filepath = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=[("Image Files", "*.png *.bmp")])

    img_input = transform_image(img_filepath)
    left_image.configure(image=img_input)
    left_image.image = img_input

    filename = get_filename(img_filepath)
    img_filename_label.configure(text='Filename: ' + filename)

def handle_plain_file():
    global plain_filepath, filename_label

    if action.get() == INSERT:
        plain_filepath = filedialog.askopenfilename(initialdir="/", title="Select file")
        content = bpcs.read_byte_string(plain_filepath)[:100]

        filename = get_filename(plain_filepath)
        filename_label.configure(text='Filename: ' + filename)
    else:
        extension = get_extension(plain_filepath)
        user_filepath = filedialog.asksaveasfile(defaultextension=extension)
        user_filepath = user_filepath.name

        shutil.copy(plain_filepath, user_filepath)

def save_image_file():
    extension = get_extension(img_filepath)
    user_filepath = filedialog.asksaveasfile(defaultextension=extension)
    user_filepath = user_filepath.name

    shutil.copy("temp.png", user_filepath)

def start():
    global sequential, cgc, key_entry, threshold_entry, status_label, plain_filepath, filename_label

    plain_filename = get_filename(plain_filepath)
    if (not os.path.exists("./{}".format(plain_filename))):
        shutil.copy(plain_filepath, '.')
    if action.get() == INSERT:
        if can_encrypt():
            def process_encrypt():
                try:
                    results = bpcs.encrypt(img_filepath, plain_filename, "temp.png",
                        sequential=sequential.get(),
                        key=key_entry.get(),
                        cgc=cgc.get(),
                        threshold=float(threshold_entry.get()),
                        encrypted=encrypt.get())
                    if results == False:
                        messagebox.showerror("Error", "Payload is too big.")
                    else:
                        img_output = transform_image("temp.png")
                        psnr = bpcs.calculate_psnr(img_filepath, "temp.png")
                        middle_image.configure(image=img_output)
                        middle_image.image = img_output
                        status_label.configure(text='Status: Idle')
                        psnr_score.configure(text="{0:.2f}".format(psnr))
                        enable_buttons()
                except:
                    messagebox.showerror("Error", "Something wrong happened... Try again.")
                    enable_buttons_error()

            disable_buttons()
            status_label.configure(text='Status: Processing')
            t = threading.Thread(target=process_encrypt)
            t.start()
        else:
            show_error()
    else:
        if can_decrypt():
            def process_decrypt():
                try:
                    global plain_filepath
                    plain_filepath = bpcs.decrypt(img_filepath,
                        sequential=sequential.get(),
                        key=key_entry.get(),
                        cgc=cgc.get(),
                        threshold=float(threshold_entry.get()),
                        encrypted=encrypt.get())
                    status_label.configure(text='Status: Idle')
                    filename_label.configure(text='Filename: ' + plain_filepath)
                    enable_buttons()
                except:
                    messagebox.showerror("Error", "Something wrong hapened... Try again.")
                    enable_buttons_error()

            disable_buttons()
            status_label.configure(text='Status: Processing')
            t = threading.Thread(target=process_decrypt)
            t.start()
        else:
            show_error()

def change_action():
    global left_label, middle_label, middle_button, right_button
    if action.get() == INSERT:
        left_label.configure(text="Original Image")
        middle_label.configure(text="BPCS Image")
        middle_button.configure(state=tk.DISABLED)
        right_button.configure(state=tk.NORMAL, text="Upload File")
        reset_state()
    else:
        left_label.configure(text="BPCS Image")
        middle_label.configure(text="-")
        middle_button.configure(state=tk.DISABLED)
        right_button.configure(state=tk.DISABLED, text="Save Extracted")
        reset_state()

def reset_state():
    global plain_filepath, img_filepath, filename_label, img_filename_label, img_input, img_output, left_image, middle_image
    plain_filepath = img_filepath = ''
    filename_label.configure(text='Filename: -')
    img_filename_label.configure(text='Filename: -')

    img_input = ImageTk.PhotoImage(Image.open('gray.png'))
    left_image.configure(image=img_input)
    left_image.image = img_input

    img_output = ImageTk.PhotoImage(Image.open('gray.png'))
    middle_image.configure(image=img_output)
    middle_image.image = img_output

def disable_buttons():
    global middle_button, left_button, right_button, start_button
    middle_button.configure(state=tk.DISABLED)
    left_button.configure(state=tk.DISABLED)
    right_button.configure(state=tk.DISABLED)
    start_button.configure(state=tk.DISABLED)

def enable_buttons():
    global middle_button, left_button, right_button, start_button
    left_button.configure(state=tk.NORMAL)
    right_button.configure(state=tk.NORMAL)
    start_button.configure(state=tk.NORMAL)
    if action.get() == INSERT:
        middle_button.configure(state=tk.NORMAL)

def enable_buttons_error():
    global middle_button, left_button, right_button, start_button
    left_button.configure(state=tk.NORMAL)
    start_button.configure(state=tk.NORMAL)
    if action.get() == INSERT:
        right_button.configure(state=tk.NORMAL)

def can_encrypt():
    global key_entry, img_filepath, plain_filepath
    if key_entry.get() == '' or img_filepath == '' or plain_filepath == '':
        return False
    return True

def can_decrypt():
    global key_entry, img_filepath
    if key_entry.get() == '' or img_filepath == '':
        return False
    return True

def show_error():
    message = 'Please fill in those fields:\n'
    fields = []
    if key_entry.get() == '':
        fields.append('Key')
    if img_filepath == '':
        if action.get() == INSERT:
            fields.append('Original Image')
        else:
            fields.append('BPCS Image')
    if plain_filepath == '' and action.get() == INSERT:
        fields.append('Message')
    messagebox.showerror("Error", message + ', '.join(fields))

def transform_image(filepath):
    img = Image.open(filepath).convert('RGBA')
    background = Image.new('RGBA', img.size, (255, 255, 255))
    alpha_composite = Image.alpha_composite(background, img)
    alpha_composite = alpha_composite.resize((PANEL_WIDTH, PANEL_HEIGHT))
    img_input = ImageTk.PhotoImage(alpha_composite)
    return img_input

def get_extension(filepath):
    splits = filepath.split('.')
    if len(splits) == 1:
        return ''
    return '.' + splits[len(splits)-1]

def get_filename(filepath):
    splits = filepath.split('/')
    return splits[len(splits)-1]

# Variables
action = tk.IntVar()
action.set(INSERT)

cgc = tk.BooleanVar()
cgc.set(True)

encrypt = tk.BooleanVar()
encrypt.set(True)

sequential = tk.BooleanVar()
sequential.set(True)

# Top frame
title_frame = tk.Frame(root)
title_label = tk.Label(title_frame,
		         text="BPCS HUWALAUMBA",
		         fg = "dark green",
		         font = "Helvetica 16 bold italic").pack(pady=10)
title_frame.pack()

# Main Frame
main_frame = tk.Frame(root)

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
                width=PANEL_WIDTH, height=PANEL_HEIGHT)
left_image.pack(pady=5)
left_button = tk.Button(left_frame,
                text="Upload",
                fg="blue",
                command=open_image)
left_button.pack(pady=5)
img_filename_label = tk.Label(left_frame,
                text="Filename: -")
img_filename_label.pack(pady=5)
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
                width=PANEL_WIDTH, height=PANEL_HEIGHT)
middle_image.pack(pady=5)
middle_button = tk.Button(middle_frame,
                text="Save",
                fg="blue",
                state=tk.DISABLED,
                command=save_image_file)
middle_button.pack(pady=5)
middle_frame.pack(side=tk.LEFT, padx=10)

# Right frame
right_frame = tk.Frame(main_frame)
psnr_label = tk.Label(right_frame,
                text="PSNR",
                fg = "dark green",
                font = "Helvetica 14 bold")
psnr_label.pack()
psnr_score = tk.Label(right_frame,
                text="",
                fg = "dark green",
                font = "Helvetica 14 bold",
                width = 8,
                height = 2,
                borderwidth=2,
                relief="groove")
psnr_score.pack()

right_label = tk.Label(right_frame,
                text="Message File",
                fg = "dark green",
                font = "Helvetica 14 bold")
right_label.pack(pady=5)
filename_label = tk.Label(right_frame,
                text="Filename: -",
                fg = "black",
                font = "Helvetica 10")
filename_label.pack(pady=5)
right_button = tk.Button(right_frame,
                text="Upload File",
                fg="blue",
                command=handle_plain_file)
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
              text="Insert",
              padx=20,
              variable=action,
              command=change_action,
              value=INSERT).pack(anchor=tk.W)
tk.Radiobutton(action_frame,
              text="Extract",
              padx=20,
              variable=action,
              command=change_action,
              value=EXTRACT).pack(anchor=tk.W)
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
              value=True).pack(anchor=tk.W)
tk.Radiobutton(cgc_frame,
              text="No",
              padx=20,
              variable=cgc,
              value=False).pack(anchor=tk.W)
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
              value=True).pack(anchor=tk.W)
tk.Radiobutton(sequential_frame,
              text="Random",
              padx=20,
              variable=sequential,
              value=False).pack(anchor=tk.W)
sequential_frame.pack(side=tk.LEFT, pady=5)

# Encrypt frame
encrypt_frame = tk.Frame(bottom_frame)
tk.Label(encrypt_frame,
         text="Use Encryption?",
         justify=tk.LEFT,
         padx=20).pack()
tk.Radiobutton(encrypt_frame,
              text="Yes",
              padx=20,
              variable=encrypt,
              value=True).pack(anchor=tk.W)
tk.Radiobutton(encrypt_frame,
              text="No",
              padx=20,
              variable=encrypt,
              value=False).pack(anchor=tk.W)
encrypt_frame.pack(side=tk.LEFT, pady=5)

# Input frame
input_frame = tk.Frame(bottom_frame)
tk.Label(input_frame, text="BPCS Threshold").grid(row=0)
tk.Label(input_frame, text="Key").grid(row=1)

threshold_entry = tk.Entry(input_frame)
threshold_entry.insert(0, "0.3")
key_entry = tk.Entry(input_frame)

threshold_entry.grid(row=0, column=1)
key_entry.grid(row=1, column=1)
input_frame.pack(side=tk.LEFT, padx=5, pady=5)

# Final frame

final_frame = tk.Frame(bottom_frame)
start_button = tk.Button(final_frame,
                text="Start",
                fg="blue",
                command=start)
start_button.pack(pady=5)
status_label = tk.Label(final_frame,
         text="Status: Idle",
         justify=tk.LEFT,
         fg="red",
         padx=20)
status_label.pack()
final_frame.pack(side=tk.LEFT, padx=5, pady=5)
bottom_frame.pack()

root.mainloop()
