import datetime
import os
import pickle
import random
import shutil
import subprocess
import time
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
from video_generator.video_editor.concatenate import concatenate_videoclips
from video_generator.utils.moviepy_utils import numpad_alignment_to_moviepy
from video_generator.title_generator.render_html import render_text
from video_generator.subtitle_generator.twitch_data import TwitchData
from video_generator.video_upsampling.dummy_upsampling import DummySR
from video_generator.video_upsampling.simple_upsampling import SimpleSR


def duration_for_file(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)

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

def get_translation(path):
    if path is None:
        return {'clip': None, 'duration': None}
    else:
        video_id = os.path.splitext(os.path.basename(path))[0]
        rendered_path = os.path.join(vid_finishedvids, f'{video_id}_finished.mp4')
        os.system(
            f"ffmpeg -y -fflags genpts -i \"{path}\" \"{rendered_path}\"")

        time = duration_for_file(rendered_path)
        return {'clip': VideoFileClip(rendered_path), 'duration': time}


def render_video(twitch_video: dict, config, platform_data=None):
    clips = twitch_video['clips']
    color1 = getColour(twitch_video.get('color1', "Black"))
    color2 = getColour(twitch_video.get('color2', "White"))
    music_type = twitch_video.get('music_type', None)
    # self.colour2 = "White"
    # self.final_clips = None
    # self.audio_cat = "None"

    try:
        sr_callback = SimpleSR()
    except:
        sr_callback = DummySR()

    credits = []
    streamers_in_cred = []
    amount = 0
    for clip in clips:
        if clip.isUsed:
            amount += 1
    render_max_progress = amount * 3 + 1 + 1

    translation = get_translation(config.screen_transition)

    print("Beginning Rendering")
    final_clips = []
    timecodes = []
    summary_time = 0

    for i, clip in enumerate(clips):
        if config.intro_from_clip == i and config.intro_video is not None:
            video_id = os.path.splitext(os.path.basename(config.intro_video))[0]
            rendered_path = os.path.join(vid_finishedvids, f'{video_id}_finished.mp4')
            os.system(
                f"ffmpeg -y -fflags genpts -i \"{config.intro_video}\" \"{rendered_path}\"")

            final_clips.append(VideoFileClip(rendered_path))
            timecodes.append([time.strftime('%M:%S', time.gmtime(summary_time)), 'Intro'])
            summary_time += duration_for_file(rendered_path)


        clip: Clip
        if not clip.isUsed:
            continue
        name = clip.streamer_name
        video_path = clip.filename

        if name is not None and name not in streamers_in_cred:
            credits.append(f"Streamer: {clip.streamer_name}")
            streamers_in_cred.append(clip.streamer_name)

        if clip.start_cut is None:
            clip.start_cut = 0

        if clip.end_cut is None:
            clip.end_cut = 0

        start_trim = max(round(clip.start_cut, 2), 0.0)
        end_trim = max(round(clip.end_cut, 2), 0.0)
        final_duration = round(clip.end_cut - clip.start_cut, 2)

        timecodes.append([time.strftime('%M:%S', time.gmtime(summary_time)), f'{platform_data.get_raw_link(clip)} | {clip.title}'])
        volume = clip.volume

        video_id = os.path.splitext(os.path.basename(video_path))[0]


        rendered_path = os.path.join(vid_finishedvids, f'{video_id}_finished.mp4')

        if not clip.isIntro:
            print("%s duration %s" % (video_path, final_duration))
            if end_trim == 0 and start_trim == 0:
                print("%s no trim" % video_path)
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" \"{rendered_path}\"")
            elif end_trim > 0 and start_trim > 0:
                print("%s start trim %s and end trim %s" % (video_path, start_trim, end_trim))
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -ss {start_trim} -t {final_duration} \"{rendered_path}\"")
            elif end_trim > 0 and start_trim == 0:
                print("%s end trim %s" % (video_path, end_trim))

                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -t {end_trim} \"{rendered_path}\"")
            elif end_trim == 0 and start_trim > 0:
                print("%s start trim %s" % (video_path, start_trim))
                os.system(
                    f"ffmpeg -y -fflags genpts -i \"{video_path}\" -ss {start_trim} \"{rendered_path}\"")

        final_duration = duration_for_file(rendered_path)

        print('Adding text')
        if inclide_streamer_name and clip.subs_alignment > 0 and not clip.isIntro:
            alignment = clip.subs_alignment  #: Numpad-style alignment, eg. 7 is "top left" (that is, ASS alignment semantics)
            # Render streamer name
            subtitle_out_path = os.path.join(final_subtitles_path, f'{video_id}.png')
            subtitle_out_path = platform_data.generate_streamer_subtitle(clip, subtitle_out_path)
            if subtitle_out_path is None:
                subtitle_logo = None
            else:
                subtitle_logo = (ImageClip(subtitle_out_path)
                                 .set_duration(final_duration)
                                 # .fx(resize, height=50)  # if you need to resize...
                                 # .margin(right=8, top=8, opacity=0)  # (optional) logo-border padding
                                 .set_pos(numpad_alignment_to_moviepy(alignment)))
        else:
            subtitle_logo = None

        w, h = config.video_resolution

        summary_time += final_duration  # Update time after rendering
        if clip.isInterval and translation['clip'] is not None:
            summary_time += translation['duration']

        if not clip.isIntro:
            if clip.title_alignment > 0:
                title_out_path = os.path.join(final_titles_path, f'{video_id}.png')
                render_text(clip.title, width=w, out_path=title_out_path)
                logo = (ImageClip(title_out_path)
                        .set_duration(final_duration)
                        #.fx(resize, height=50)  # if you need to resize...
                        #.margin(right=8, top=8, opacity=0)  # (optional) logo-border padding
                        .set_pos(numpad_alignment_to_moviepy(clip.title_alignment)))
            else:
                logo = None

            if logo is not None or subtitle_logo is not None:
                video_clip = VideoFileClip(rendered_path).fx(afx.volumex, volume)
                if clip.apply_sr:
                    video_clip = video_clip.fl_image(sr_callback.super_resolution)
                video_clip = video_clip.fx(resize, newsize=(w, h))
                result_clips = [video_clip]
                for img_clip in [subtitle_logo, logo]:
                    if img_clip is not None:
                        result_clips.append(img_clip)
                finish = CompositeVideoClip(result_clips)
            else:
                video_clip = VideoFileClip(rendered_path).fx(afx.volumex, volume)
                if clip.apply_sr:
                    video_clip = video_clip.fl_image(sr_callback.super_resolution)
                video_clip = video_clip.fx(resize, newsize=(w, h))
                finish = video_clip
        else:
            finish = VideoFileClip(video_path).fx(afx.volumex, volume).fx(resize, newsize=(w, h))
        final_clips.append(finish)
        if clip.isInterval and translation['clip'] is not None and i < len(clips) - 1:
            final_clips.append(translation['clip'])

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
    with open(f'{timecodes_path}/TwitchMoments_{current_date}.txt', 'w') as f:
        timecodes_str = ''
        for str_time, description in timecodes:
            timecodes_str += f'{str_time} - {description}\n'
        f.write(timecodes_str)

inclide_streamer_name =True
fps = 30

out_folder = 'Assets'
vid_finishedvids = os.path.join(out_folder, 'rendered_clips')
final_clips_path = os.path.join(out_folder, 'Final Clips')
final_titles_path = os.path.join(out_folder, 'Titles')
final_subtitles_path = os.path.join(out_folder, 'Subtitles')
timecodes_path = os.path.join(out_folder, 'Timecodes')


if __name__ == '__main__':



    os.makedirs(out_folder, exist_ok=True)
    os.makedirs(vid_finishedvids, exist_ok=True)
    os.makedirs(final_clips_path, exist_ok=True)
    os.makedirs(final_titles_path, exist_ok=True)
    os.makedirs(timecodes_path, exist_ok=True)
    os.makedirs(final_subtitles_path, exist_ok=True)
    config = get_yaml_config('video_generator/video_generator_settings.yaml')
    clips_path = config.clips_path
    with open(clips_path, "rb") as f:
        twitch_video = pickle.load(f)
    # for clip in twitch_video['clips']:
    #     print(clip)
    test_existence(twitch_video)

    if config.platform == 'twitch':
        from twitchAPI import Twitch, AuthScope
        user_secrets = get_yaml_config('user_secrets.yaml')
        twitch = Twitch(user_secrets.app_id, user_secrets.app_secret,
                        target_app_auth_scope=[AuthScope.USER_READ_FOLLOWS])
        platform_data = TwitchData(twitch)

    render_video(twitch_video, config, platform_data=platform_data)