import time
import customtkinter
from customtkinter import *
from threading import Thread
import yt_dlp
import uuid
import os
import math

is_cancelled = False
is_paused = False
download_url = ""
ydl_opts = {}

class DownloadCancelledException(Exception):
    pass

def bytesToMbFiles(bytes_size):
    mb_size = bytes_size / (1024 ** 2)
    return mb_size

def speedTestBytesToMb(size_bytes):
    i = int(math.floor(math.log(size_bytes, 1024)))
    power = math.pow(1024, i)
    size = round(size_bytes / power, 2)
    return f'{size} Mbps'

def formatETA(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)}m {int(seconds)}s"

def progressFunc(d):
    global is_cancelled, is_paused
    if is_cancelled:
        raise DownloadCancelledException("Download cancelled by user")
    if is_paused:
        raise DownloadCancelledException("Download paused by user")
    try:
        if d['status'] == 'downloading':
            current_bytes = d['downloaded_bytes']
            total_bytes = d['total_bytes']
            completed_dload = int(100 * current_bytes / total_bytes)
            eta = d.get('eta', 0)
            speed = d.get('speed', 0)
            formatted_eta = formatETA(eta)
            status = ("\r{}MB/{}MB".format("{:.2f}".format(bytesToMbFiles(current_bytes)),
                                               "{:.2f}".format(bytesToMbFiles(total_bytes))))

            status = status.strip()[:20].ljust(20)
            status_label.configure(text=f"Downloading: {status}", text_color="#676767")
            es_time.configure(text=f"Estimated Time: {formatted_eta}")
            percent_label.configure(text=f"{completed_dload}%")
            speed_label.configure(text=f"Wi-Fi: {speed / (1024 ** 2):.2f} M/S")
            status_label.update()
            es_time.update()
            percent_label.update()
            speed_label.update()
            my_progress.set(completed_dload / 100)
            my_progress.update()
    except:
        pass


def runThread():
    th = Thread(target=downloadAllVideos)
    th.start()

def generateRandomFilename(ext):
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    # Create the filename with the given extension
    filename = f"{random_uuid}.{ext}"
    return filename

def clearStatusBar():
    es_time.grid_forget()
    percent_label.grid_forget()
    speed_label.grid_forget()
    es_time.configure(text="")
    percent_label.configure(text="")
    speed_label.configure(text="")

def disableBtns():
    downbtn.configure(state=DISABLED)
    clear_btn.configure(state=DISABLED)

def enableBtns():
    downbtn.configure(state=NORMAL)
    clear_btn.configure(state=NORMAL)

def enablePrefBtns():
    cancel_btn.configure(state=NORMAL)
    pause_btn.configure(state=NORMAL)

def disablePrefBtns():
    cancel_btn.configure(state=DISABLED)
    pause_btn.configure(state=DISABLED)

path = os.path.join(os.path.expanduser("~"), "Videos")
def downloadAllVideos():
    disableBtns()
    global is_cancelled, is_paused, download_url, ydl_opts
    is_cancelled = False # Reset cancel state
    is_paused = False  # Reset paused state
    status_label.configure(text="")
    pause_btn.configure(text="Pause")
    clearStatusBar()
    speed_label.grid(row=0, column=0)
    status_label.grid(row=0, column=1, padx=10)
    percent_label.grid(row=0, column=2)
    es_time.grid(row=0, column=3, padx=10)
    download_url = url.get()
    if download_url == "" :
        status_label.configure(text="Empty", text_color="#ff3e3e", font=("Dafont", 14, "bold"))
        url.focus()
        url.configure(border_color="#ff3e3e")
        enableBtns()
    elif not download_url.startswith(("http://", "https://")):
        status_label.configure(text="Invalid URL", text_color="#ff3e3e", font=("Dafont", 14, "bold"))
        url.focus()
        url.configure(border_color="#ff3e3e")
        enableBtns()
    else:
        try:
            url.configure(border_color="#b73be9", state=DISABLED)
            my_progress.pack(side=BOTTOM, anchor=CENTER, pady=5)
            my_progress.set(0)
            status_label.configure(text="Processing...", text_color="#5f5f5f", font=("Dafont", 14, "bold"))
            if not os.path.exists(path):
                os.mkdir(path)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(download_url, download=False)
                    ext = info_dict.get('ext', 'mp4')
                    random_filename = generateRandomFilename(ext)
                    output_path = os.path.join(path, random_filename)
                    ydl_opts = {
                        'outtmpl': output_path,
                        'progress_hooks': [progressFunc],
                        'continuedl': True,
                    }
                    enablePrefBtns()
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([download_url])
                        disablePrefBtns()
                        clearStatusBar()
                        enableBtns()
                        pause_btn.configure(text="Pause")
                        my_progress.set(0)
                        my_progress.pack_forget()
                        status_label.configure(text="File has been saved to your Videos destination", text_color="#03d186", font=("Dafont", 14, "bold"))
                        url.configure(state=NORMAL)
                        time.sleep(1)
                        clearOnlyURLEntry()
            except DownloadCancelledException as e:
                if is_paused:
                    status_label.configure(text="Download paused.", text_color="#ffe957")
            except Exception as e:
                status_label.configure(text="Network error / Server error / URL not found! Try again.",
                                       text_color="#ff3e3e", font=("Dafont", 14, "bold"))
                my_progress.pack_forget()
                clearStatusBar()
                enableBtns()
                url.configure(state=NORMAL)
                disablePrefBtns()
        except Exception as e:
            status_label.configure(text="Something went wrong! We will fix it soon.", text_color="#ff3e3e", font=("Dafont", 14, "bold"))
            my_progress.pack_forget()
            clearStatusBar()
            enableBtns()
            url.configure(state=NORMAL)
            disablePrefBtns()

def clearEntry():
    [widget.delete(0, END) for widget in down_wrap_frame.winfo_children() if isinstance(widget, CTkEntry)]
    status_label.configure(text="")
    url.configure(border_color="#b73be9")
    root.focus()

def clearOnlyURLEntry():
    [widget.delete(0, END) for widget in down_wrap_frame.winfo_children() if isinstance(widget, CTkEntry)]
    root.focus()

def pauseDownload():
    global is_paused, download_url
    if(is_paused == True and download_url != ""):
        is_paused = False
        status_label.configure(text="Download resuming...", text_color="#ffe957")
        pause_btn.configure(text="Pause")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([download_url])
            download_url = ""
            disablePrefBtns()
            clearStatusBar()
            enableBtns()
            pause_btn.configure(text="Pause")
            status_label.configure(text="File has been saved to your Videos destination", text_color="#03d186",
                                   font=("Dafont", 14, "bold"))
            my_progress.set(0)
            my_progress.pack_forget()
            url.configure(state=NORMAL)
            time.sleep(1)
            clearOnlyURLEntry()
    else:
        is_paused = True
        pause_btn.configure(text="Resume")
        status_label.configure(text="Download paused.", text_color="#ffe957")
        speed_label.configure(text="")
        es_time.configure(text="")

def runPauseResumeThread():
    th = Thread(target=pauseDownload)
    th.start()

def cancelDownload():
    global is_cancelled, is_paused
    is_cancelled = True
    is_paused = False
    status_label.configure(text="Download cancelled.", text_color="#ff3e3e")
    my_progress.set(0)
    my_progress.pack_forget()
    clearStatusBar()
    disablePrefBtns()
    enableBtns() # Download and clear btn
    pause_btn.configure(text="Pause")
    url.configure(state=NORMAL)
    time.sleep(1)
    clearOnlyURLEntry()

def runCancelThread():
    th = Thread(target=cancelDownload)
    th.start()

def onEnter(event):
    pause_btn.configure(text_color="black", fg_color="#ffe957")

def onLeave(event):
    pause_btn.configure(text_color="white", fg_color="#494949")

if __name__ == "__main__":
    root = CTk()
    root.geometry('750x500')
    root.maxsize(750, 500)
    root.minsize(750, 500)
    root.title("PYTO")
    customtkinter.set_appearance_mode("dark")
    root.iconbitmap("D:\\CodePlayground\\Projects for public\\PYTO - Video Downloader\\pyto_icon.ico")
    title_font = ("Dafont", 30, "bold")
    label_first = ("Roboto", 18, "bold")
    entry_font = ("Roboto", 14, "bold")
    btn_font = ("Roboto", 14, "bold")
    status_font = ("Roboto", 16, "bold")

    main_frame = CTkFrame(root, fg_color="transparent")
    main_frame.pack(side=TOP, anchor=CENTER, fill=X)

    header_frame = CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(side=TOP, anchor=CENTER, pady=50)

    CTkLabel(header_frame, text="Video Downloader", font=title_font, fg_color="transparent").grid(row=0, column=1)

    download_frame = CTkFrame(main_frame, fg_color="#2e2e2e")
    download_frame.pack(side=TOP, anchor=CENTER)

    down_wrap_frame = CTkFrame(download_frame, fg_color="transparent")
    down_wrap_frame.pack(side=TOP, anchor=CENTER, padx=40, pady=40)

    url = CTkEntry(down_wrap_frame, width=350, height=40, font=entry_font, border_color="#b73be9" , placeholder_text="Enter the video url", placeholder_text_color="#818181")
    url.grid(row=1, column=0)
    downbtn = CTkButton(down_wrap_frame, text="Download", cursor="hand2", height=40 , fg_color="#b73be9", hover_color="#a635d3",text_color="white",
                        font=btn_font, command=runThread)
    downbtn.grid(row=1, column=1, padx=10)

    cancel_btn = CTkButton(down_wrap_frame, text="Cancel", cursor="hand2", state=DISABLED, font=btn_font, fg_color="#494949", hover_color="#ef4b4b", text_color="white",
              command=runCancelThread)
    cancel_btn.grid(row=2, column=0, sticky=W, pady=10)

    pause_btn = CTkButton(down_wrap_frame, text="Pause", cursor="hand2", state=DISABLED , font=btn_font, fg_color="#494949", text_color="white",
              command=runPauseResumeThread)
    pause_btn.grid(row=2, column=0, sticky=E, pady=10, padx=60)
    pause_btn.bind("<Enter>", onEnter)
    pause_btn.bind("<Leave>", onLeave)

    clear_btn = CTkButton(down_wrap_frame, text="Clear", cursor="hand2", font=btn_font, fg_color="#494949", hover_color="#ef4b4b", text_color="white",
              command=clearEntry)
    clear_btn.grid(row=2, column=1, sticky=W, pady=10, padx=10)

    my_progress = CTkProgressBar(root, orientation="horizontal", progress_color="#00d889", mode="determinate")

    status_frame = CTkFrame(root, fg_color="transparent")
    status_frame.pack(side=BOTTOM, anchor=CENTER, pady=10)
    speed_label = CTkLabel(status_frame, text="", text_color="#0481ff", font=status_font)
    status_label = CTkLabel(status_frame, text="", font=status_font)
    percent_label = CTkLabel(status_frame, text="", font=status_font, text_color="#00d889")
    es_time = CTkLabel(status_frame, text="", font=status_font, text_color="#b73be9")


    root.mainloop()