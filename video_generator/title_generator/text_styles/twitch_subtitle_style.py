from .style import Style


class TwitchSubtitleStyle(Style):
    def html(self, text):
        return f"""
                  <h1 class="created" class="text">{text}</h1>
                   """

    def css(self, user_profile_link):
        return f"""
                h1 {{
                  align-items: center;
                  text-align: center;
                  justify-content: center;
                  font-family: "Raleway", "Avant Garde", Avantgarde, "Century Gothic", CenturyGothic, "AppleGothic", sans-serif;
                  color: #274046;
                  -webkit-text-stroke: 15px #E6DADA;
                  font-size: 300%;
                  padding-left: 2.5em;
                  padding-right: 30px;
                  padding-top: 15px;
                  padding-bottom: 15px;
                  height: 50px;
                }}
                .created {{
                  background: 
                    url({user_profile_link}),
                    linear-gradient(to right, #A770EF, #CF8BF3, #FDB99B);
                  background-size: contain;
                  background-repeat: no-repeat;
                  position: absolute;
                  top: 0;
                  left: 0;
                  border-radius: 10px;
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                }}
                """