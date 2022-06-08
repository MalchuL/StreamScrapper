from .style import Style


class ExampleStyle(Style):
    def html(self, text):
        return f"""<div><h1 class="text">{text}</h1></div>"""

    def css(self):
        return """
                div {
                  background-color: #f3e6e8;
                  background-image: linear-gradient(315deg, #d5d0e5 0%, #f3e6e8 74%);
                  align-items: center;
                  text-align: center;
                  justify-content: center;
                  border-radius: 10px;
                }
                
                .text {
                  text-transform: uppercase;
                  font-size: 50px;
                  font-weight: 600;
                  background-image: linear-gradient(to left, #33245c, #4a3a59);
                  font-family: Raleway;
                  padding-top: 10px;
                  padding-bottom: 10px;
                  color: transparent;
                  background-clip: text;
                  -webkit-background-clip: text;
                }
                """