#this file is used for generating thread content

import copy

import lxml
from lxml.html import builder as E
from lxml.builder import ElementMaker as EM

import tornado.escape

import initiate
import utilfunctions

def html_page_return(board, thread, default_style):
    html = E.HTML(
        E.HEAD(
            E.META(**{'http-equiv':"Default-Style", 'content':default_style}),
            E.TITLE("/"+board+"/ - №"+str(thread)), #title
            E.SCRIPT(type = 'text/javascript', src = '/mainscript.js'), #js
            *initiate.style_cache
            ),
        E.BODY(
            E.P(E.CLASS("board"), board, id = 'board'),
            E.P(E.CLASS("thread"), str(thread), id = 'thread'),
            E.TABLE(
                E.CLASS("maintable"),
                E.THEAD(E.TR(E.TD(
                    copy.copy(initiate.board_cache_footer),
                    E.HR(E.CLASS("delimeter")),
                    )), id = 'header'),
                E.TBODY(E.TR(E.TD(
                    E.H2(E.CLASS("boardname"),
                         E.A('/' + board + '/ - '+ initiate.board_cache[board].name, href = '/' + board),
                         ),
                    E.HR(E.CLASS("delimeter")),
                    initiate.board_cache[board].post_form, #need to make it depending on post_form_type
                    E.SCRIPT('function open_form() {document.getElementById("postform").style.display = "block"; document.getElementById("closeform").style.display = "block"; document.getElementById("threadcreate").style.display = "none";}'),
                    E.SCRIPT('function close_form() {document.getElementById("postform").style.display = "none"; document.getElementById("closeform").style.display = "none"; document.getElementById("threadcreate").style.display = "block";}'),
                    E.H3(E.A('Ответить в тред', href = "javascript:open_form();"), id = 'threadcreate'),
                    E.H4(E.A('Скрыть форму', href = "javascript:close_form();"), id = 'closeform'),
                    E.HR(E.CLASS("delimeter")),
                    E.DIV('', id = 'mainframe'),
                    E.DIV('', id = 'optionsdiv'),
                    )), id = 'mainpart'),
                E.TFOOT(E.TR(E.TD(
                    E.DIV(
                        E.HR(E.CLASS("delimeter"), id = 'end')
                        ),
                    initiate.board_cache_footer,
                    E.DIV('powered by ',
                          E.A('Farlight Imageboard Engine',
                              href='https://github.com/Alpherie/farlight_board_engine',
                              target='_blank',
                              ),
                          id='credentials'),
                    )), id = 'footer'),#we make it a footer
                ),
            onload = 'threadfunc()'
            )
        )
    return lxml.html.tostring(html)

def json_answer(requesth):
    received_objects = tornado.escape.json_decode(requesth.request.body)
    if received_objects['action'] == 'get post ids for threads': #this is when we need to return post ids for given threads
        return_object = {}
        board = received_objects['board']
        if board not in initiate.board_cache: #all of this should be redone, it is fucking not good code
            return 'error'
        for threadnum in received_objects['threads']:
            if isinstance(threadnum['threadnum'], int) and isinstance(threadnum['begin'], int) and threadnum['begin'] > 0: #here we get the thread number and range
                if threadnum['threadnum'] not in return_object: #checking if threadnum is not already requested, we support only one request per thread
                    if threadnum['threadnum'] in initiate.board_cache[board].posts_dict: #checking if thread exists
                        if not isinstance(threadnum['end'], int) or threadnum['end'] > len(initiate.board_cache[board].posts_dict[threadnum['threadnum']]): #should add checking for begin to be less then len(list of posts in thread)
                            return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][threadnum['begin']-1:].tolist()
                        elif threadnum['end'] > 0 and threadnum['begin'] < len(initiate.board_cache[board].posts_dict[threadnum['threadnum']]):
                            return_object[threadnum['threadnum']] = initiate.board_cache[board].posts_dict[threadnum['threadnum']][threadnum['begin']-1:threadnum['end']-1].tolist()
                        else:
                            return_object[threadnum['threadnum']] = []
                    else:
                        return_object[threadnum] = None
            else:
                return 'typeerror'
        return tornado.escape.json_encode(return_object)
    elif received_objects['action'] == 'get posts code by num': #i will do it later
        return utilfunctions.get_posts_code_by_num(requesth, received_objects)
    #delete post actions
    elif received_objects['action'] == 'delete posts by ids':
        return utilfunctions.delete_posts_by_ids(requesth, received_objects)
    #mod functions
    elif received_objects['action'] == 'ban by ip':
        return utilfunctions.ban_by_ip(requesth, received_objects)
    else:
        return 'incorrect action'
    return 'not implemented yet'

def get_board_and_thread(uri):
    split_uri = uri.split(r'/') #need to get the boardname and pagenum
    board = split_uri[1]
    if len(split_uri) > 3:
        if split_uri[3] != '': #we check if page exists in uri
            thread = int(split_uri[3])
        else:
            thread = None
    else:
        thread = None
    if board in initiate.board_cache: #checking if board exists
        return True, board, thread
    else:
        return False, None, None

@utilfunctions.decorator_for_style
def get(requesth, **kwargs): #requesth is tornadoweb requesthandler object
    """default_style we get from decorator"""
    board_exists, board, thread = get_board_and_thread(requesth.request.uri)
    if not board_exists:
        return 'No such board'
    if thread is not None and thread in initiate.board_cache[board].posts_dict: #checking if thread exists
        return html_page_return(board, thread, kwargs['default_style'])
    else:
        return 'No such thread'

def post(requesth):
    board_exists, board, thread = get_board_and_thread(requesth.request.uri)
    if not board_exists:
        return 'no such board'
    try:
        content_type = requesth.request.headers['Content-Type']
    except KeyError:
        pass
    else:
        if 'application/json' in content_type:
            return json_answer(requesth)
    return utilfunctions.posting(requesth, board) #and here we suppose it is posting

if __name__ == '__main__':
    pass
