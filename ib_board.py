#this file is used for generating thread content
import copy

import lxml
from lxml.html import builder as E
from lxml.builder import ElementMaker as EM

import tornado.escape

import initiate
import utilfunctions
import config as cf

def html_page_return(board, page, default_style):
    html = E.HTML(
        E.HEAD(
            E.META(**{'http-equiv':"Default-Style", 'content':default_style, 'id':'stylemetatag'}),
            E.TITLE("/"+board+"/ - page "+str(page)), #title
            E.SCRIPT(type = 'text/javascript', src = '/mainscript.js'), #js
            *initiate.style_cache
            ),
        E.BODY(
            E.P(E.CLASS("board"), board, id = 'board'),
            E.P(E.CLASS("page"), str(page), id = 'page'),
            E.P(E.CLASS("thread"), '0', id = 'thread'),
            E.TABLE(
                E.CLASS("maintable"),
                E.THEAD(E.TR(E.TD(
                    E.TABLE(E.TR(E.TD(E.CLASS('left'), copy.copy(initiate.board_cache_navigation)),
                                 E.TD(E.CLASS('right'), utilfunctions.generate_right_up_corner_menu()),
                                 ),
                            id='headblock'),
                    E.HR(E.CLASS("delimeter")),
                    )), id = 'header'),
                E.TBODY(E.TR(E.TD(
                    E.H2(E.CLASS("boardname"),
                         E.A('/' + board + '/ - '+ initiate.board_cache[board].name, href = '/' + board),
                         ),
                    E.HR(E.CLASS("delimeter")),
                    initiate.board_cache[board].post_form,
                    E.SCRIPT('function open_form() {document.getElementById("postform").style.display = "block"; document.getElementById("closeform").style.display = "block"; document.getElementById("threadcreate").style.display = "none";}'),
                    E.SCRIPT('function close_form() {document.getElementById("postform").style.display = "none"; document.getElementById("closeform").style.display = "none"; document.getElementById("threadcreate").style.display = "block";}'),
                    E.H3(E.A('Создать тред', href = "javascript:open_form();"), id = 'threadcreate'),
                    E.H4(E.A('Скрыть форму', href = "javascript:close_form();"), id = 'closeform'),
                    E.HR(E.CLASS("delimeter")),
                    E.DIV('', id = 'mainframe'),
                    )), id = 'mainpart'),
                E.TFOOT(E.TR(E.TD(
                    E.DIV(E.TABLE(E.TR(E.TD(E.A('Предыдущая', id='prevpagelink')),
                                       E.TD('', id='pageslist'),
                                       E.TD(E.A('Следующая', id='nextpagelink')),
                                       ),
                                  id='pagestable'),
                          E.SPAN(str(len(initiate.board_cache[board].threads)),
                                 id='threadsnumber'),
                          id = 'pages'),
                    E.DIV(
                        E.HR(E.CLASS("delimeter"), id='end')
                        ),#we make it a footer
                    initiate.board_cache_navigation,
                    E.DIV('powered by ',
                          E.A('Farlight Imageboard Engine',
                              href='https://github.com/Alpherie/farlight_board_engine',
                              target='_blank',
                              ),
                          id='credentials'),
                    )), id = 'footer'),
                ),
                onload = 'boardfunc()'
            )
        )
    return lxml.html.tostring(html)

def json_answer(requesth):
    """Giving back the requested by JSON content"""
    received_objects = tornado.escape.json_decode(requesth.request.body)
    if received_objects['action'] == 'get threads ids for page': #this is when we need to return post ids for given threads
        board = received_objects['board']
        if board not in initiate.board_cache: #all of this should be redone, it is fucking not good code
            return 'error'
        if received_objects['range']['begin'] <= 0 or received_objects['range']['end'] <= 0:
            return 'error, incorrect range' #checking the range
        if received_objects['range']['begin'] > len(initiate.board_cache[board].threads):
            return_object = [] #if begin goes out of range, return none
        elif received_objects['range']['end'] > len(initiate.board_cache[board].threads):
            return_object = initiate.board_cache[board].threads[received_objects['range']['begin']-1:].tolist() #if end goes out of range, return everything from begin
        else:
            return_object = initiate.board_cache[board].threads[received_objects['range']['begin']-1:received_objects['range']['end']-1].tolist() #if end and begin are in range, return their range
        return tornado.escape.json_encode(return_object)
    elif received_objects['action'] == 'get posts code by num': #i will do it later
        return utilfunctions.get_posts_code_by_num(requesth, received_objects)
    #should be moved to utilfunctions
    elif received_objects['action'] == 'get post ids for threads': #this is when we need to return post ids for given threads
        return_object = {}
        board = received_objects['board']
        if board not in initiate.board_cache: #all of this should be redone, it is fucking not good code
            return 'error'
        for threadnum in received_objects['threads']:
            if threadnum['threadnum'] not in return_object: #checking if threadnum is not already requested, we support only one request per thread
                if threadnum['threadnum'] in initiate.board_cache[board].posts_dict: #checking if thread exists
                    if isinstance(threadnum['threadnum'], int) and isinstance(threadnum['begin'], int) and isinstance(threadnum['end'], int): #checking types
                        if threadnum['begin'] <= threadnum['end']:
                            if threadnum['begin'] < 0 and threadnum['end'] < 0:
                                if threadnum['end'] < -len(initiate.board_cache[board].posts_dict[threadnum['threadnum']]): #should add checking for begin to be less then len(list of posts in thread)
                                    return_object[threadnum['threadnum']] = []
                                elif threadnum['begin'] < -len(initiate.board_cache[board].posts_dict[threadnum['threadnum']]):
                                    if threadnum['end'] == -1:
                                        return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][:].tolist()
                                    else:
                                        return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][:threadnum['end']].tolist()
                                else:
                                    if threadnum['end'] == -1:
                                        return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][threadnum['begin']:].tolist()
                                    else:
                                        return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][threadnum['begin']:threadnum['end']].tolist()
                            elif threadnum['begin'] >= 0 and threadnum['end'] >= 0:
                                if threadnum['begin'] >= len(initiate.board_cache[board].posts_dict[threadnum['threadnum']]):
                                    return_object[threadnum['threadnum']] = []
                                elif threadnum['end'] >= len(initiate.board_cache[board].posts_dict[threadnum['threadnum']]):
                                    return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][threadnum['begin']-1:].tolist()
                                else:
                                    return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][threadnum['begin']-1:threadnum['end']-1].tolist()
                            else:
                                return 'incorrect range' #both begin and end should be < 0 or >= 0
                        else:
                            return 'incorrect range' #both begin should be <= end
                    else:
                        return 'typeerror'
                else:
                    return_object[threadnum] = None
        return tornado.escape.json_encode(return_object)
    #delete post actions
    elif received_objects['action'] == 'delete posts by ids':
        return utilfunctions.delete_posts_by_ids(requesth, received_objects)
    #mod functions
    elif received_objects['action'] == 'ban by ip':
        return utilfunctions.ban_by_ip(requesth, received_objects)
    else:
        return 'incorrect action'
    return 'not implemented yet'

def get_board_and_page(uri):
    split_uri = uri.split(r'/') #need to get the boardname and pagenum
    board = split_uri[1]
    if len(split_uri) > 2:
        if split_uri[2] != '': #we check if page exists in uri
            page = int(split_uri[2])
        else:
            page = 0
    else:
        page = 0
    if board in initiate.board_cache: #checking if board exists
        return True, board, page
    else:
        return False, None, None

@utilfunctions.decorator_for_style
def get(requesth, **kwargs): #requesth is tornadoweb requesthandler object
    """default_style we get from decorator"""
    board_exists, board, page = get_board_and_page(requesth.request.uri)
    if board_exists:
        return html_page_return(board, page, kwargs['default_style'])
    else:
        return 'No such board'

def post(requesth): #working over POST requests
    board_exists, board, page = get_board_and_page(requesth.request.uri)
    if not board_exists:
        return 'No such board'
    try:
        content_type = requesth.request.headers['Content-Type']
    except KeyError:
        pass
    else:
        if 'application/json' in content_type:
            return json_answer(requesth)#here we work we json requests
    return utilfunctions.posting(requesth, board) #and here we suppose it is posting

if __name__ == '__main__':
    pass
