import imgkit

from title_generator.text_styles.example_style import ExampleStyle

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

def render_text(text, width=1024, out_path='out.png'):
    # You can get params for <meta> from `wkhtmltoimage --help` and `wkhtmltoimage --readme`
    # You can find examples on CodePen
    style = ExampleStyle()


    body = f"""
        <html>
          <head>
            <style>
            {style.css()}
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
    render_text('Hello html')