from .style import Style


class ExampleStyle(Style):
    def html(self, text):
        return f"""<h1 class="text">{text}</h1>"""

    def css(self):
        return """
                h1 {
                  align-items: center;
                  text-align: center;
                  justify-content: center;
                  background: linear-gradient(to right, #FDFBFB, #EBEDEE 70%);
                  border-radius: 10px;
                  background-color: #F8F8FF;
                }
                
                .text {
                  text-transform: uppercase;
                  background: linear-gradient(to right, #30CFD0 0%, #330867 100%);
                  font-family: "Poppins", sans-serif;
                }
                """