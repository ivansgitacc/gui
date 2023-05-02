from tkinter import *
from PIL import Image, ImageTk

root = Tk()

def add_img():
    btn.grid_remove()
    photo_label.grid(row=0, column=0)

image_file = Image.open('C:/Users/Admin/Desktop/The Project/images/1649279368-Ent-2022Python.jpeg')
image_file = image_file.resize((200, 100))
photo = ImageTk.PhotoImage(image_file)
photo_label = Label(root, image=photo)

btn = Button(text='add', command=add_img)
btn.grid(row=0, column=0)

root.mainloop()