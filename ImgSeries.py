import tkinter as tk
import os
import PIL.Image
from PIL import ImageTk, ImageDraw
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import GlobalVar

class ImgSeries():
    def __init__(self, master):
        self.tk_ims = []
        self.im_copies = []
        self.im_paths = []
        self.im_sizes = []
        self.im_zoomPos = []
        self.container = tk.Frame(master)
        self.container.pack(expand = True, fill = "both")
        self.container.bind('<Configure>', self.resize_image)
        self.canvas = tk.Canvas(self.container, width=master.winfo_width(), height=master.winfo_height())
        self.canvas.pack(fill="both", expand=True)
        self.canvas.grid(row = 0, column = 0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.activeImg = -1

        ### rectangle zooming
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.x = self.y = 0
        self.zoomImg = []
        self.zoomed = False

    def resize_image(self,event):
        if len(self.tk_ims)==0:
            return
        new_width = event.width
        new_height = event.height
        GlobalVar.width, GlobalVar.height = new_width, new_height
        im = self.zoomImg.resize((new_width, new_height))
        self.zoomImg = im
        self.im_sizes[self.activeImg] = im.size
        tk_im = ImageTk.PhotoImage(im)
        self.tk_ims[self.activeImg] = tk_im
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_ims[self.activeImg], anchor='nw')
        self.container.config(width=GlobalVar.width, height=GlobalVar.height)
        self.canvas.config(width=GlobalVar.width, height=GlobalVar.height)

    def OpenFile(self):
        filename = askopenfilename(initialdir=os.getcwd(),
                            filetypes =(("Image File", "*.jpeg;*.jpg;*.png"),("All Files","*.*")),
                            title="Select file"
                            )
        im = PIL.Image.open(filename)
        GlobalVar.width, GlobalVar.height = im.size
        self.im_paths.append(filename)
        self.im_copies.append(im.copy())
        self.zoomImg = self.im_copies[-1]
        self.im_zoomPos.append([])
        self.im_sizes.append(im.size)
        self.activeImg = len(self.tk_ims)
        self.tk_ims.append(ImageTk.PhotoImage(im))
        self.canvas.create_image(0, 0, image=self.tk_ims[-1], anchor='nw')
        self.canvas.config(width=GlobalVar.width, height=GlobalVar.height)
        self.container.config(width=GlobalVar.width, height=GlobalVar.height)
        self.container.master.geometry('%dx%d' % (GlobalVar.width, GlobalVar.height))
        return im
    
    def reshow(self, index):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_ims[index], anchor='nw')
        self.activeImg = index
        self.zoomImg = self.im_copies[index]

        for i in range(len(self.im_zoomPos[self.activeImg])):
            im_c = self.zoomImg.crop(self.im_zoomPos[self.activeImg][i])
            self.zoomImg = im_c.resize((GlobalVar.width, GlobalVar.height))

        GlobalVar.width, GlobalVar.height = self.im_sizes[index]
        self.canvas.config(width=GlobalVar.width, height=GlobalVar.height)
        self.canvas.master.config(width=GlobalVar.width, height=GlobalVar.height)
        self.container.config(width=GlobalVar.width, height=GlobalVar.height)
        self.container.master.geometry('%dx%d' % (GlobalVar.width, GlobalVar.height))

    def Last(self):
        if self.activeImg > 0:
            self.reshow(self.activeImg-1)

    def Next(self):
        if self.activeImg < len(self.tk_ims)-1:
            self.reshow(self.activeImg+1)

    def Delete(self):
        if len(self.tk_ims)==0:
            return
        del self.tk_ims[self.activeImg]
        del self.im_copies[self.activeImg]
        del self.im_paths[self.activeImg]
        del self.im_sizes[self.activeImg]
        if self.activeImg<0:
            return
        elif self.activeImg==0 and len(self.tk_ims)==0:
            self.activeImg = -1
            self.canvas.delete("all")
        elif self.activeImg==0 and len(self.tk_ims)!=0:
            self.reshow(self.activeImg)
        elif self.activeImg>=len(self.tk_ims):
            self.reshow(self.activeImg-1)
        else :
            self.reshow(self.activeImg)
    
    def Reload(self):
        for i in range(len(self.tk_ims)):
            im = PIL.Image.open(self.im_paths[i])
            self.im_sizes[i] = im.size
            self.im_copies[i] = im.copy()
            self.tk_ims[i] = ImageTk.PhotoImage(im)
            self.reshow(i)

    ### Zoom
    def ZoomIn(self,event):
        if len(self.tk_ims)==0:
            return
        if self.rect == None:
            return
        if self.end_x < self.start_x:
            self.end_x, self.start_x = self.start_x, self.end_x
        if self.end_y < self.start_y:
            self.end_y, self.start_y = self.start_y, self.end_y  
        area = (self.start_x, self.start_y, self.end_x, self.end_y)
        self.im_zoomPos[self.activeImg].append(area)
        im_c = self.zoomImg.crop(area)
        im = im_c.resize((GlobalVar.width, GlobalVar.height))
        self.zoomImg = im
        tk_im = ImageTk.PhotoImage(im)
        self.tk_ims[self.activeImg] = tk_im
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_ims[self.activeImg], anchor='nw')
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.x = self.y = 0
    
    def ZoomBack(self,event):
        if len(self.tk_ims)==0:
            return
        if self.rect == None:
            return
        self.zoomImg = self.im_copies[self.activeImg]
        tk_im = ImageTk.PhotoImage(self.zoomImg)
        self.tk_ims[self.activeImg] = tk_im
        self.im_zoomPos[self.activeImg] = []
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_ims[self.activeImg], anchor='nw')
        GlobalVar.width, GlobalVar.height = self.im_sizes[self.activeImg]
        self.canvas.config(width=GlobalVar.width, height=GlobalVar.height)
        self.container.config(width=GlobalVar.width, height=GlobalVar.height)
        self.container.master.geometry('%dx%d' % (GlobalVar.width, GlobalVar.height))

    def ZoomClone(self,event):
        if len(self.im_zoomPos) == 0 :
            messagebox.showinfo("Error", "Please open one image first.")
            return
        if int(event.char)-1 >= len(self.im_zoomPos) or len(self.im_zoomPos[int(event.char)-1]) == 0:
            messagebox.showinfo("Error", "Please zoom in that image first.")
            return
        self.im_zoomPos[self.activeImg] = self.im_zoomPos[int(event.char)-1]
        for i in range(len(self.im_zoomPos[self.activeImg])):
            im_c = self.zoomImg.crop(self.im_zoomPos[self.activeImg][i])
            self.zoomImg = im_c.resize((GlobalVar.width, GlobalVar.height))
        tk_im = ImageTk.PhotoImage(self.zoomImg)
        self.tk_ims[self.activeImg] = tk_im
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.tk_ims[self.activeImg], anchor='nw')

    ### drawing rectangle and 
    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y
        # create rectangle if not yet exist
        #if not self.rect:
        self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1)
    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)
    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y
    ###