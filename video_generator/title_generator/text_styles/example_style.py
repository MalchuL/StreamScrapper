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
                  font-size: 70px;
                  font-weight: 600;
                  background-image: linear-gradient(to left, #553c9a, #b393d3);
                  color: transparent;
                  background-clip: text;
                  -webkit-background-clip: text;
                }
                """