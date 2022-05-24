import imgkit

from video_generator.title_generator.text_styles.style import Style
from video_generator.title_generator.text_styles.example_style import ExampleStyle

# body = f"""
#    <html>
#      <head>
#        <meta name="imgkit-width" content="{width}"/>
#        <meta name="imgkit-height" content="0"/>
#        <meta name="imgkit-transparent" content="1"/>
#      </head>
#      {style.html(text)}
#    </html>
#    """
from video_generator.title_generator.text_styles.twitch_subtitle_style import TwitchSubtitleStyle as SubtitleStyle


def render_text(text, width=1024, out_path='out.png', style: Style=ExampleStyle(), css_kwargs=None):
    # You can get params for <meta> from `wkhtmltoimage --help` and `wkhtmltoimage --readme`
    # You can find examples on CodePen
    if css_kwargs is None:
        css_kwargs = {}
    body = f"""
        <html>
          <head>
            <style>
            {style.css(**css_kwargs)}
            </style>
            <meta name="imgkit-width" content="{width}"/>
            <meta name="imgkit-height" content="0"/>
            <meta name="imgkit-transparent" content="1"/>
          </head>
          {style.html(text)}
        </html>
        """
    imgkit.from_string(body, out_path)

if __name__ == '__main__':
    render_text('twitch.tv/uselessmouth', width=0, style=SubtitleStyle(), css_kwargs=dict(user_profile_link='https://static-cdn.jtvnw.net/jtv_user_pictures/6b6b478a-e651-4d81-81c8-064c40b1aa97-profile_image-70x70.png'))