Instruction from https://dev.twitch.tv/docs/api

1. Go to https://dev.twitch.tv/console/apps

2. generate new app with params
"my_test_api"
"http://localhost:17563"


3. 1.Download twitch cli from https://github.com/twitchdev/twitch-cli/releases/tag/v1.1.5
   2. Get acess token by `./twitch token`
   3. Input your Client ID from app. for ex `fthb6a0jfghj56uk9gd2u6t9p` 
   4. Get secret from the same page (you can create new). for ex `qtln7njjnj5gfh56havk7pmzkbl3qc`
   5. Output will be acess token. for ex. `8wcldc5fo3e2456456sy94owlq8r`
   6. Update `app_secret` output key in user_secrets.yaml from .4 and `app_id` from .3


install `sudo apt install ubuntu-restricted-extras`
install `sudo apt-get install wkhtmltopdf`
install `sudo apt  install ffmpeg`


Install MongoDB by https://docs.mongodb.com/manual/administration/install-on-linux/
Install MongoDB Compass https://www.mongodb.com/try/download/compass

## Runs clips dumping into mongodb
1. export PYTHONPATH=`pwd`
2. python stream_db/run_dumping.py 

## Dumping clips from mongo db
1. python stream_db/download_clips.py 

## Runs clips editor
1. export PYTHONPATH=`pwd`
2. python clips_editor/clip_editor.py

## Merging clips
1. export PYTHONPATH=`pwd`
3. python video_generator/video_generator.py

## Fast clips dumping
1. Run twitch_downloader.py

## Install superresolution library
git clone https://github.com/sberbank-ai/Real-ESRGAN
cd Real-ESRGAN
download weights https://drive.google.com/drive/folders/16PlVKhTNkSyWFx52RPb2hXPIQveNGbxS


# Making YouTube thumbnail
1. Find video and frame inside downloaded videos 
2. Run `ffmpeg -ss 00:00:26 -i 'input_video.mp4' -frames:v 1 -q:v 2 output.jpg`
3. Remove background on `https://www.remove.bg/ru/upload`