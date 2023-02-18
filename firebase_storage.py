import requests
import pyrebase

firebase_config = {
  "apiKey": "AIzaSyBm-WT8CLjmL6Az1nTjkv5Idx9ZWdaOjXU",
  "authDomain": "upload-71456.firebaseapp.com",
  "projectId": "upload-71456",
  "storageBucket": "upload-71456.appspot.com",
  "messagingSenderId": "345506817418",
  "appId": "1:345506817418:web:c5390120ed82d7799ed473",
  "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebase_config)
fb_storage = firebase.storage()

def download_video(download_url, video_title):
    response = requests.get(download_url)

    with open(video_title, 'wb') as f:
        f.write(response.content)

def upload_edited_video(video_title, username):
    upload_path = f"{username}/edited_videos/{video_title}"
    fb_storage.child(upload_path).put(video_title)