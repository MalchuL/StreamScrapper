import datetime
import os
import pickle
import random
from time import sleep

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from pysubs2 import SSAFile, SSAStyle, SSAEvent, make_time

from clips_editor.widgets.list_items.video_item import Clip
import moviepy.audio.fx.volumex as afx

#bgr format with &h at start and & at end
from twitch_parser.config.config_parser import get_yaml_config
from video_editor.concatenate import concatenate_videoclips


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

def test_existence(video_data):
    for clip in video_data['clips']:
        assert clip.isUsed in [True, False]

        if clip.isUsed:
            try:
                name = clip.streamer_name
                video_path = clip.filename
                assert os.path.exists(video_path)
                start_trim = round(clip.start_cut, 1)
                end_trim = round(clip.end_cut, 1)
                assert start_trim < end_trim
                assert clip.volume >= 0
                _ = clip.isInterval
                _ = clip.isIntro
            except Exception as e:
                print('Error in clip', clip)
                raise

def render_video(twitch_video: dict, config):
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
        alignment = max(clip.subs_alignment, 1)  #: Numpad-style alignment, eg. 7 is "top left" (that is, ASS alignment semantics)
        subs.styles['vidText'] = SSAStyle(alignment=alignment, fontname='Gilroy-ExtraBold', fontsize=25, marginl=4,
                                          marginv=-2.5, marginr=0, outline=2, outlinecolor=color2,
                                          primarycolor=color1, shadow=0)
        if inclide_streamer_name:
            subs.append(SSAEvent(start=make_time(s=0), end=make_time(s=60), style='vidText', text=f"twitch.tv/{name}" if clip.subs_alignment > 0 else 0))
        subs.save(f'subtitleFile.ass')

        rendered_path = os.path.join(vid_finishedvids, f'{os.path.splitext(os.path.basename(video_path))[0]}_finished.mp4')
        w, h = config.video_resolution
        if not clip.isInterval and not clip.isIntro:
            print("%s duration %s" % (video_path, final_duration))
            if end_trim == 0 and start_trim == 0:
                print("%s no trim" % video_path)
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -vf \"ass=subtitleFile.ass, scale={w}:{h}\" \"{rendered_path}\"")
            elif end_trim > 0 and start_trim > 0:
                print("%s start trim %s and end trim %s" % (video_path, start_trim, end_trim))
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -ss {start_trim} -t {final_duration} -vf \"ass=subtitleFile.ass, scale={w}:{h}\" \"{rendered_path}\"")
            elif end_trim > 0 and start_trim == 0:
                print("%s end trim %s" % (video_path, end_trim))

                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -t {end_trim} -vf \"ass=subtitleFile.ass, scale={w}:{h}\" \"{rendered_path}\"")
            elif end_trim == 0 and start_trim > 0:
                print("%s start trim %s" % (video_path, start_trim))
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -ss {start_trim} -vf \"ass=subtitleFile.ass, scale={w}:{h}\" \"{rendered_path}\"")

        if not clip.isInterval and not clip.isIntro:
            if clip.title_alignment > 0:
                logo = (ImageClip("/home/malchul/work/streams/stream_parser/video_generator/title_generator/out.png")
                        .set_duration(final_duration)
                        .fx(resize, height=50)  # if you need to resize...
                        #.margin(right=8, top=8, opacity=0)  # (optional) logo-border padding
                        .set_pos(("center", "top")))

                finish = CompositeVideoClip([VideoFileClip(rendered_path).fx(afx.volumex, volume), logo])
            else:
                finish = VideoFileClip(rendered_path).fx(afx.volumex, volume)
        else:
            finish = VideoFileClip(video_path).fx(afx.volumex, volume)

        final_clips.append(finish)

    # TODO add music
    musicFiles = [] #getFileNames(f'{settings.asset_file_path}/Music')
    random.shuffle(musicFiles)

    print("done working out durations")
    final_concat = concatenate_videoclips(final_clips, size=config.video_resolution)
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


inclide_streamer_name =True
fps = 30

out_folder = 'Assets'
vid_finishedvids = os.path.join(out_folder, 'rendered_clips')
final_clips_path = os.path.join(out_folder, 'Final Clips')


if __name__ == '__main__':



    os.makedirs(out_folder, exist_ok=True)
    os.makedirs(vid_finishedvids, exist_ok=True)
    os.makedirs(final_clips_path, exist_ok=True)
    config = get_yaml_config('video_generator/video_generator_settings.yaml')
    clips_path = config.clips_path
    with open(clips_path, "rb") as f:
        twitch_video = pickle.load(f)
    for clip in twitch_video['clips']:
        print(clip)
    test_existence(twitch_video)
    render_video(twitch_video, config)