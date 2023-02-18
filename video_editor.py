import moviepy.editor as mpy
import math
import random
from pprint import pprint
import numpy as np 

def find_speaking_clips(audio, window_size=0.1, padding=0.25):
    num_windows = math.floor(audio.duration/window_size)
    threshold = 0.01

    levels = []
    for i in range(num_windows):
        s = audio.subclip(i * window_size, (i + 1) * window_size)
        max_vol = s.max_volume()
        levels.append(max_vol)

    q75, q25 = np.percentile(levels, [75, 25])
    IQR = q75 - q25
    threshold = IQR/2
    print("thressshold:", threshold)

    speaking_windows = []
    for i in range(num_windows):
        s = audio.subclip(i * window_size, (i + 1) * window_size)
        max_vol = s.max_volume()
        speaking_windows.append(max_vol > threshold)

    speaking_intervals = []
    for i in range(1, len(speaking_windows)):
        prev = speaking_windows[i - 1]
        curr = speaking_windows[i]

        if not prev and curr:
            speaking_start = i * window_size
        
        if prev and not curr:
            speaking_end = i * window_size
            new_speaking_interval = [speaking_start - padding, speaking_end + padding]

            # edge cases
            if new_speaking_interval[0] < 0:
                new_speaking_interval[0] = 0
            
            if new_speaking_interval[1] > audio.duration:
                new_speaking_interval[1] = audio.duration

            merge_needed = len(speaking_intervals) > 0 and speaking_intervals[-1][1] > new_speaking_interval[0]
            if merge_needed:
                merge_interval = [speaking_intervals[-1][0], new_speaking_interval[1]]
                speaking_intervals[-1] = merge_interval
            else:
                speaking_intervals.append(new_speaking_interval)
    return speaking_intervals

def edit_video(input_video_name, output_name, is_youtube, add_intro, add_outro):

    video = mpy.VideoFileClip(input_video_name)
    audio = video.audio

    clips = find_speaking_clips(audio)

    video_clips = []
    for clip in clips:
        video_clip = video.subclip(clip[0], clip[1])
        video_clips.append(video_clip)

    final_clip = mpy.concatenate_videoclips(video_clips)

    if add_intro:
        intro = mpy.VideoFileClip("intro.mov")
        final_clip = mpy.concatenate_videoclips([intro, final_clip])
    
    if add_outro:
        outro = mpy.VideoFileClip("outro.mov")
        final_clip = mpy.concatenate_videoclips([final_clip, outro])

    width, height = video.size
    if is_youtube and width > height:
        youtube_animation = mpy.VideoFileClip("youtube-green-screen.mp4")
        masked_clip = youtube_animation.fx(mpy.vfx.mask_color, color=[84,225,35], thr=100, s=5)
        masked_clip = masked_clip.set_pos(('center', 'bottom'))

        i = random.randint(60, 120)
        final_clip = mpy.CompositeVideoClip([
            final_clip,
            masked_clip.set_start(i),
            masked_clip.set_start(final_clip.duration-i),
            ])

    final_clip.write_videofile(output_name,
                            fps=60,
                            codec="libx264",
                            temp_audiofile="temp-audio.m4a",
                            remove_temp=True,
                            preset="superfast",
                            audio_codec="aac",
                            ffmpeg_params=["-crf","10"])

    video.close()
