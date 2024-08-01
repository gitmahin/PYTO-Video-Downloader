from customtkinter import *
from threading import Thread
import yt_dlp
import uuid
import os

def bytes_to_mb(bytes_size):
    mb_size = bytes_size / (1024 ** 2)
    return mb_size

def progress_func(d):
    try:
        if d['status'] == 'downloading':
            current_bytes = d['downloaded_bytes']
            total_bytes = d['total_bytes']
            completed_dload = int(100 * current_bytes / total_bytes)
            status = ("\r{} MB / {} MB".format("{:.2f}".format(bytes_to_mb(current_bytes)),
                                               "{:.2f}".format(bytes_to_mb(total_bytes))))

            status_label.configure(text=f"Downloading... [File size:{status}]", text_color="#5f5f5f", font=("Dafont", 14, "bold"))
            status_label.update()
            my_progress.set(completed_dload / 100)
            my_progress.update()
    except:
        pass


def runThread():
    th = Thread(target=downloadAllVideos)
    th.start()

def generate_random_filename(ext):
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    # Create the filename with the given extension
    filename = f"{random_uuid}.{ext}"
    return filename

root = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(root, "pyto_downloads")

ydl_opts = {
    'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
    'progress_hooks': [progress_func],
}

def downloadAllVideos():

    if url.get() == "" :
        status_label.configure(text="Empty", text_color="#ff3e3e", font=("Dafont", 14, "bold"))
        url.focus()
        url.configure(border_color="#ff3e3e")
    elif not url.get().startswith(("http://", "https://")):
        status_label.configure(text="Invalid URL", text_color="#ff3e3e", font=("Dafont", 14, "bold"))
        url.focus()
        url.configure(border_color="#ff3e3e")
    else:
        try:
            url.configure(border_color="#b73be9")
            my_progress.pack(side=BOTTOM, anchor=CENTER, pady=5)
            my_progress.set(0)
            downbtn['state'] = DISABLED
            status_label.configure(text="Processing...", text_color="#5f5f5f", font=("Dafont", 14, "bold"))
            if not os.path.exists(path):
                os.mkdir(path)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url.get(), download=False)
                    ext = info_dict.get('ext', 'mp4')
                    random_filename = generate_random_filename(ext)
                    output_path = os.path.join(path, random_filename)
                    ydl_opts['outtmpl'] = output_path
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url.get()])
                        downbtn['state'] = NORMAL
                        status_label.configure(text="Download successful. Check your PYTO-Downloads folder.", text_color="#03d186", font=("Dafont", 14, "bold"))
                my_progress.set(0)
                my_progress.pack_forget()
            except:
                status_label.configure(text="Server error! Try again.", text_color="#ff3e3e", font=("Dafont", 14, "bold"))
                downbtn['state'] = NORMAL
                my_progress.pack_forget()
        except:
            status_label.configure(text="Something went wrong!", text_color="#ff3e3e", font=("Dafont", 14, "bold"))
            downbtn['state'] = NORMAL
            my_progress.pack_forget()

def clearEntry():
    [widget.delete(0, END) for widget in down_wrap_frame.winfo_children() if isinstance(widget, CTkEntry)]
    status_label.configure(text="")
    url.configure(border_color="#b73be9")
    root.focus()

if __name__ == "__main__":
    root = CTk()
    root.geometry('700x500')
    root.maxsize(700, 500)
    root.minsize(700, 500)
    root.title("PYTO")

    title_font = ("Dafont", 30, "bold")
    label_first = ("Roboto", 18, "bold")
    entry_font = ("Roboto", 14, "bold")
    btn_font = ("Roboto", 14, "bold")
    status_font = ("Roboto", 11, "bold")

    main_frame = CTkFrame(root, fg_color="transparent")
    main_frame.pack(side=TOP, anchor=CENTER, fill=X)

    header_frame = CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(side=TOP, anchor=CENTER, pady=50)

    CTkLabel(header_frame, text="Video Downloader", font=title_font, fg_color="transparent").grid(row=0, column=1)

    download_frame = CTkFrame(main_frame, fg_color="#2e2e2e")
    download_frame.pack(side=TOP, anchor=CENTER)

    down_wrap_frame = CTkFrame(download_frame, fg_color="transparent")
    down_wrap_frame.pack(side=TOP, anchor=CENTER, padx=40, pady=40)

    url = CTkEntry(down_wrap_frame, width=350, height=40, font=entry_font, border_color="#b73be9" , placeholder_text="Enter the URL (Facebook / Twitter / YouTube)", placeholder_text_color="#818181")
    url.grid(row=1, column=0)
    downbtn = CTkButton(down_wrap_frame, text="Download", cursor="hand2", height=40 , fg_color="#b73be9", hover_color="#a635d3",text_color="white",
                        font=btn_font, command=runThread)
    downbtn.grid(row=1, column=1, padx=10)
    CTkButton(down_wrap_frame, text="Clear", cursor="hand2", font=btn_font, fg_color="#494949", hover_color="#ef4b4b", text_color="white",
              command=clearEntry).grid(row=2, column=0, sticky=W, pady=10)

    my_progress = CTkProgressBar(root, orientation="horizontal", progress_color="#03d186", mode="determinate")

    status_label = CTkLabel(root, text="", font=status_font)
    status_label.pack(side=BOTTOM, anchor=CENTER, fill=X, pady=10)

    root.mainloop()