import os
from fastapi import FastAPI
import video_editor
from pydantic import BaseModel
import firebase_storage as storage

app = FastAPI()

class VideoItem(BaseModel):
    VideoTitle: str
    VideoDownloadURL: str
    Username: str
    

@app.get('/')
def hello():
    return {"hello world": "this worked!!"}

@app.post('/edit-video')
def edit_video(video: VideoItem):
    filename = video.VideoTitle
    index = filename.index('.')
    title = filename[:index]
    input_filename = f"{title}.mp4"
    output_filename = f"{title}-edited.mp4"

    storage.download_video(download_url=video.VideoDownloadURL, video_title=input_filename)
    video_editor.edit_video(input_filename, output_filename, is_youtube=True, add_intro=True, add_outro=False)
    storage.upload_edited_video(video_title=output_filename, username=video.Username)

    try:
        os.remove(path=input_filename)
        os.remove(path=output_filename)
    except:
        print("unable to remove files")

    return {filename: "finished editing!!!"}

