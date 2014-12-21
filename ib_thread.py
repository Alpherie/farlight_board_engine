#this file is used for generating thread content
import lxml
from lxml.html import builder as E
from lxml.builder import ElementMaker as EM

import tornado.escape

import initiate
import utilfunctions

def html_page_return(board, thread):
    html = E.HTML(
        E.HEAD(
            E.LINK(rel="stylesheet", href="/css/great.css", type="text/css"), #css
            E.TITLE("/"+board+"/ - №"+str(thread)), #title
            E.SCRIPT(type = 'text/javascript', src = '/mainscript.js') #js
            ),
        E.BODY(
            E.H1(E.CLASS("heading"), "Farlight Engine Imageboard"),
            E.P(E.CLASS("board"), board, id = 'board'),
            E.P(E.CLASS("thread"), str(thread), id = 'thread'),
            E.FORM(E.CLASS("postform"), #postform
                   E.INPUT(type = 'hidden', name = 'action', value = 'post'),
                   E.INPUT(type = 'hidden', name = 'op', value = str(thread)),
                   'THEME ', E.INPUT(type = 'text', name = 'theme', value = ''),
                   E.BR(),
                   'TEXT ', E.INPUT(type = 'text', name = 'text', value = ''),
                   E.BR(),
                   E.INPUT(type = 'submit', value = 'POST'),
                   method = 'POST', action = ''),
            lxml.html.fromstring("<p>... and this is a parsed fragment ...</p>"),
            E.DIV('', id = 'mainframe'),
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
            if type(threadnum['threadnum']) is int and type(threadnum['begin']) is int and threadnum['begin'] > 0: #here we get the thread number and range
                if threadnum['threadnum'] not in return_object: #checking if threadnum is not already requested, we support only one request per thread
                    if threadnum['threadnum'] in initiate.board_cache[board][6]: #checking if thread exists
                        if type(threadnum['end']) is not int or threadnum['end'] > len(initiate.board_cache[board][6][threadnum['threadnum']]): #should add checking for begin to be less then len(list of posts in thread)
                            return_object[threadnum['threadnum']] = initiate.board_cache[board][6][threadnum['threadnum']][threadnum['begin']-1:]
                        elif threadnum['end'] > 0 and threadnum['begin'] < len(initiate.board_cache[board][6][threadnum['threadnum']]):
                            return_object[threadnum['threadnum']] = initiate.board_cache[board][6][threadnum['threadnum']][threadnum['begin']-1:threadnum['end']-1]
                        else:
                            return_object[threadnum['threadnum']] = []
                    else:
                        return_object[threadnum] = None
            else:
                return 'typeerror'
        return tornado.escape.json_encode(return_object)
    elif received_objects['action'] == 'get posts code by num': #i will do it later
        return utilfunctions.get_posts_code_by_num(requesth, received_objects)
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

def get(requesth): #requesth is tornadoweb requesthandler object
    board_exists, board, thread = get_board_and_thread(requesth.request.uri)
    if board_exists == False:
        return 'No such board'
    if thread is not None and thread in initiate.board_cache[board][6]: #checking if thread exists
        return html_page_return(board, thread)
    else:
        return 'No such thread'

def post(requesth):
    board_exists, board, thread = get_board_and_thread(requesth.request.uri)
    if board_exists == False:
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
