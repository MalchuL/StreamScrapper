import datetime
import os
import pickle
import random
from time import sleep

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from pysubs2 import SSAFile, SSAStyle, SSAEvent, make_time

from clips_editor.widgets.list_items.video_item import Clip
import moviepy.audio.fx.volumex as afx

#bgr format with &h at start and & at end
def getColour(colourstring):
    if colourstring == "Blue":
        return "&hff0000&"
    elif colourstring == "Red":
        return "&h0000ff&"
    elif colourstring == "Green":
        return "&h00ff7f&"
    elif colourstring == "Orange":
        return "&h007fff&"
    elif colourstring == "Black":
        return "&h000000&"
    elif colourstring == "Purple":
        return "&hbf00bf&"
    elif colourstring == "Pink":
        return "&hff00ff&"
    elif colourstring == "White":
        return "&hffffff&"
    elif colourstring == "Yellow":
        return "&h00ffff&"

def render_video(twitch_video: dict):
    clips = twitch_video['clips']
    color1 = getColour(twitch_video.get('color1', "Black"))
    color2 = getColour(twitch_video.get('color2', "White"))
    music_type = twitch_video.get('music_type', None)
    # self.colour2 = "White"
    # self.final_clips = None
    # self.audio_cat = "None"

    credits = []
    streamers_in_cred = []
    amount = 0
    for clip in clips:
        if clip.isUsed:
            amount += 1
    render_max_progress = amount * 3 + 1 + 1
    print("Beginning Rendering")
    final_clips = []

    for i, clip in enumerate(clips):
        clip: Clip
        if not clip.isUsed:
            continue
        name = clip.streamer_name
        video_path = clip.filename
        subs = SSAFile()

        if name is not None and name not in streamers_in_cred:
            credits.append(f"Streamer: {clip.streamer_name}")
            streamers_in_cred.append(clip.streamer_name)

        if clip.start_cut is None:
            clip.start_cut = 0

        if clip.end_cut is None:
            clip.end_cut = 0

        start_trim = round(clip.start_cut, 1)
        end_trim = round(clip.end_cut, 1)
        final_duration = round(end_trim - start_trim, 1)

        volume = clip.volume

        print('Adding text')

        subs.styles['vidText'] = SSAStyle(alignment=7, fontname='Gilroy-ExtraBold', fontsize=25, marginl=4,
                                          marginv=-2.5, marginr=0, outline=2, outlinecolor=color2,
                                          primarycolor=color1, shadow=0)
        if inclide_streamer_name:
            subs.append(SSAEvent(start=make_time(s=0), end=make_time(s=60), style='vidText', text=f"twitch.tv/{name}"))
        subs.save(f'subtitleFile.ass')

        rendered_path = os.path.join(vid_finishedvids, f'{os.path.splitext(os.path.basename(video_path))[0]}_finished.mp4')

        if not clip.isInterval and not clip.isIntro:
            print("%s duration %s" % (video_path, final_duration))
            if end_trim == 0 and start_trim == 0:
                print("%s no trim" % video_path)
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -vf \"ass=subtitleFile.ass, scale=1920:1080\" \"{rendered_path}\"")
            elif end_trim > 0 and start_trim > 0:
                print("%s start trim %s and end trim %s" % (video_path, start_trim, end_trim))
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -ss {start_trim} -t {final_duration} -vf \"ass=subtitleFile.ass, scale=1920:1080\" \"{rendered_path}\"")
            elif end_trim > 0 and start_trim == 0:
                print("%s end trim %s" % (video_path, end_trim))

                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -t {end_trim} -vf \"ass=subtitleFile.ass, scale=1920:1080\" \"{rendered_path}\"")
            elif end_trim == 0 and start_trim > 0:
                print("%s start trim %s" % (video_path, start_trim))
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -ss {start_trim} -vf \"ass=subtitleFile.ass, scale=1920:1080\" \"{rendered_path}\"")

        if not clip.isInterval and not clip.isIntro:
            finish = VideoFileClip(rendered_path).fx(afx.volumex, volume)
        else:
            finish = VideoFileClip(video_path).fx(afx.volumex, volume)

        final_clips.append(finish)

    # TODO add music
    musicFiles = [] #getFileNames(f'{settings.asset_file_path}/Music')
    random.shuffle(musicFiles)

    print("done working out durations")
    final_concat = concatenate_videoclips(final_clips)
    print("done combining clips")
    print(musicFiles)
    if music_type is None:
        final_vid_with_music = final_concat.set_audio(final_concat.audio)
    else:
        final_vid_with_music = final_concat.set_audio(
            CompositeAudioClip([final_concat.audio, AudioFileClip(f'{settings.temp_path}/music-loop.mp3')]))


    sleep(5)
    current_date = datetime.datetime.today().strftime("%m-%d-%Y__%H-%M-%S")
    ffmpeg_audio = False
    if ffmpeg_audio:
        print("Rendering with audio fix")
        final_vid_with_music.write_videofile(f'{settings.final_video_path}/TwitchMoments_{current_date}.mp4',
                                             fps=settings.fps,
                                             threads=16,
                                             temp_audiofile=f'{settings.final_video_path}/TwitchMoments_{current_date}audio.mp3',
                                             remove_temp=False)
        sleep(5)
        os.system(
            f"ffmpeg -y -i \"{final_clips_path}/TwitchMoments_{current_date}.mp4\" -i \"{final_clips_path}/TwitchMoments_{current_date}audio.mp3\" -c:v copy -c:a aac \"{final_clips_path}/TwitchMoments_{current_date}fixaudio.mp4\"")
        sleep(5)
        os.remove(f'{final_clips_path}/TwitchMoments_{current_date}.mp4')
        os.remove(f'{final_clips_path}/TwitchMoments_{current_date}audio.mp3')
    else:
        final_vid_with_music.write_videofile(f'{final_clips_path}/TwitchMoments_{current_date}.mp4',
                                             fps=fps,
                                             threads=16)
        sleep(5)


DEFAULTS_CLIPS_FILE = 'out_clips.tmp'
inclide_streamer_name =True
fps = 30

out_folder = 'Assets'
vid_finishedvids = os.path.join(out_folder, 'rendered_clips')
final_clips_path = os.path.join(out_folder, 'Final Clips')


if __name__ == '__main__':
    clips_path = DEFAULTS_CLIPS_FILE


    os.makedirs(out_folder, exist_ok=True)
    os.makedirs(vid_finishedvids, exist_ok=True)
    os.makedirs(final_clips_path, exist_ok=True)

    with open(clips_path, "rb") as f:
        twitch_video = pickle.load(f)
    for clip in twitch_video['clips']:
        print(clip)

    render_video(twitch_video)