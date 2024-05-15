from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import PIL.Image
from pytube import YouTube
import urllib.request
import io
from threading import *
import tkinter.messagebox as tmsg

def showLogo():
    global imgtk
    try:
        with urllib.request.urlopen("https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png") as ur:
            imgURL = ur.read()
        img = Image.open(io.BytesIO(imgURL))
        resize_img = img.resize((60, 40), PIL.Image.Resampling.LANCZOS)
        imgtk = ImageTk.PhotoImage(resize_img)
        root.iconphoto(False, imgtk)
        Label(header_frame, image=imgtk).grid(row=0, column=0, padx=10)
    except:
        tmsg.showerror("Error", "Connection error!")

def bytes_to_mb(bytes_size):
    mb_size = bytes_size / (1024 ** 2)
    return mb_size

def progress_func(stream, chunk, remainingBytes):
    try:
        current_bytes = stream.filesize - remainingBytes
        completed_dload = int(100 * current_bytes / stream.filesize)
        status = ("\r{} MB / {} MB".format("{:.2f}".format(bytes_to_mb(current_bytes)), "{:.2f}".format(bytes_to_mb(stream.filesize))))
        
        status_label.configure(text=f"Downloading... [File size:{status}]", fg="#003C43")
        status_label.update()
        my_progress['value'] = completed_dload
        my_progress.update()
    except:
        pass

def runThread(): 
    th=Thread(target=downloadYTVideo) 
    th.start()     
   
def downloadYTVideo():
        
    try:
        downbtn['state'] = DISABLED
        status_label.configure(text="Processing...", fg="#003C43")
        youtubeobject = YouTube(urlVal.get(), on_progress_callback=progress_func)
        youtubeobject = youtubeobject.streams.get_highest_resolution()

        try:
            youtubeobject.download()
            status_label.configure(text="Download successfull", fg="green")
            my_progress['value'] = 0
            downbtn['state'] = NORMAL
        except:
            status_label.configure(text="Server error! Try again.", fg="red")
            downbtn['state'] = NORMAL


    except:
        status_label.configure(text="You have not input URL", fg="red")
        downbtn['state'] = NORMAL

def clearEntry():
    [widget.delete(0, END) for widget in download_frame.winfo_children() if isinstance(widget, Entry)]
    status_label.configure(text="")


if __name__ == "__main__":

    root = Tk()
    root.geometry('700x500')
    root.maxsize(700, 500)
    root.minsize(700, 500)
    root.title("PYTO")

    title_font = ("Dafont", "30", "bold")
    label_first = "Roboto 13 bold"
    entry_font = "Roboto 10 bold"
    btn_font = "Roboto 10 bold"
    status_font = "Roboto 11 bold"

    main_frame = Frame(root)
    main_frame.pack(side=TOP, anchor=CENTER, fill=X)

    header_frame = Frame(main_frame, pady=50)
    header_frame.pack(side=TOP, anchor=CENTER)
   
    showLogo()
    Label(header_frame, text="Video Download", font=title_font, padx=10).grid(row=0, column=1)

    download_frame = Frame(main_frame)
    download_frame.pack(side=TOP, anchor=CENTER)

    urlVal = StringVar()

    Label(download_frame, text="Enter the url:", font=label_first, pady=10).grid(row=0, column=0, sticky=W)
    Entry(download_frame, textvariable=urlVal, width=50, font=entry_font).grid(row=1, column=0)
    downbtn = Button(download_frame, text="Download", padx=15, cursor="hand2", bg="#14C38E", font=btn_font, command= runThread )
    downbtn.grid(row=1, column=1, padx=10)
    Button(download_frame, text="Clear", padx=15, cursor="hand2", bg="#E72929", font=btn_font, fg="white", command=clearEntry).grid(row=2, column=0, sticky=W, pady=10)

    
    my_progress = ttk.Progressbar(root, orient=HORIZONTAL, length=470, mode="determinate")
    my_progress.pack(side=BOTTOM, anchor=CENTER, pady=10)

    status_label = Label(root, text="", font=status_font, pady=10)
    status_label.pack(side=BOTTOM, anchor=CENTER, fill=X)


    root.mainloop()
