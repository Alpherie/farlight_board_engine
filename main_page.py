import lxml
from lxml.html import builder as E
#
import config
import initiate
import utilfunctions

def main_page_gen(default_style):
    html = E.HTML(
        E.HEAD(
            E.META(**{'http-equiv':"Default-Style", 'content':default_style, 'id':'stylemetatag'}),
            E.TITLE("U2ch - Main Page"),
	    *initiate.style_cache
            ),
        E.BODY(
	    E.TABLE(
                E.CLASS("maintable"),
                E.THEAD(E.TR(E.TD(E.DIV(E.CLASS("mainslogandiv"),
                                        E.SPAN("U2CH"),
                                        E.SPAN("",
                                               style="display: inline-block; width: 5em;"),
                                        E.SPAN("Viewing above imageboards"),
                                        ),
                                  E.DIV(E.CLASS("mainimagediv"),
                                        E.IMG(src="u-2.jpg", style="width:496px;height:334px;"),
                                        ),
                                  )), id = 'header'),
                E.TBODY(E.TR(E.TD(
                    E.HR(E.CLASS("delimeter")),
                    E.DIV(
                          initiate.board_cache_main_page,
                          ),
                    E.HR(E.CLASS("delimeter")),
                    )), id = 'mainpart'),
                E.TFOOT(E.TR(E.TD(
                    E.DIV('powered by ',
                        E.A('Farlight Imageboard Engine',
                            href='https://github.com/Alpherie/farlight_board_engine',
                            target='_blank',
                            ),
                        id='credentials'),
                    )), id = 'footer'),
                )
            )
        )
    return lxml.html.tostring(html)


@utilfunctions.decorator_for_style
def get(requesth, **kwargs):
    return main_page_gen(kwargs['default_style'])

if __name__ == '__main__':
    print(main_page_gen())
