# importing packages
from pytube import YouTube
import os

# url input from user
yt = YouTube('https://www.youtube.com/watch?v=Opzd92zTUvU')
video = yt.streams.filter(only_audio=True).first()
destination = "music\\"
out_file = video.download(output_path=destination)
base, ext = os.path.splitext(out_file)
new_file = base + '.mp3'
os.rename(out_file, new_file)

print(destination + yt.title + ".mp3")