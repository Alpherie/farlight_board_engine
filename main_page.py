import lxml
from lxml.html import builder as E
#
import config

def main_page_gen():
    html = E.HTML(
        E.HEAD(
            E.LINK(rel="stylesheet", href="css/deeplight.css", type="text/css"),
            E.TITLE("Farlight - Main Page")
            ),
        E.BODY(
            E.H1(E.CLASS("heading"), "u2ch"),
            E.P(E.CLASS("nextstr"), "Welcome to Farlight Engine main page", style="font-size: 200%"),
            "Ah, and here's some more text, by the way.",
            lxml.html.fromstring("<p>... and this is a parsed fragment ...</p>")
            )
        )
    return lxml.html.tostring(html)

if __name__ == '__main__':
    print(main_page_gen())
