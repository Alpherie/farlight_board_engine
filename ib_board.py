#this file is used for generating thread content
import lxml
from lxml.html import builder as E
from lxml.builder import ElementMaker as EM

import tornado.escape

import initiate
import utilfunctions

def html_page_return(board, page):
    html = E.HTML(
        E.HEAD(
            E.LINK(rel="stylesheet", href="/css/great.css", type="text/css"), #css
            E.TITLE("/"+board+"/ - page "+str(page)), #title
            E.SCRIPT(type = 'text/javascript', src = '/mainscript.js') #js
            ),
        E.BODY(
            E.H1(E.CLASS("heading"), "Farlight Engine Imageboard"),
            E.P(E.CLASS("board"), board, id = 'board'),
            E.P(E.CLASS("thread"), str(page), id = 'page'),
            E.FORM(E.CLASS("postform"), #postform
                   E.INPUT(type = 'hidden', name = 'op', value = 0),
                   'THEME ', E.INPUT(type = 'text', name = 'theme', value = ''),
                   E.BR(),
                   'TEXT ', E.INPUT(type = 'text', name = 'text', value = ''),
                   E.BR(),
                   E.INPUT(type = 'submit', value = 'POST'),
                   method = 'POST', action = ''),
            lxml.html.fromstring("<p>... and this is a parsed fragment ...</p>"),
            E.DIV('', id = 'mainframe'),
            onload = 'boardfunc()'
            )
        )
    return lxml.html.tostring(html)

def json_answer(requesth):
    received_objects = tornado.escape.json_decode(requesth.request.body)
    if received_objects['action'] == 'get threads ids for page': #this is when we need to return post ids for given threads
        return_object = []
        board = received_objects['board']
        if board not in initiate.board_cache: #all of this should be redone, it is fucking not good code
            return 'error'
        if received_objects['range']['begin'] <= 0 or received_objects['range']['end'] <= 0:
            return 'error, incorrect range' #checking the range
        if received_objects['range']['begin'] > len(initiate.board_cache[board][5]):
            return_object = [] #if begin goes out of range, return none
        elif received_objects['range']['end'] > len(initiate.board_cache[board][5]):
            return_object = initiate.board_cache[board][5][received_objects['range']['begin']-1:] #if end goes out of range, return everything from begin
        else:
            return_object = initiate.board_cache[board][5][received_objects['range']['begin']-1:received_objects['range']['end']-1] #if end and begin are in range, return their range
        return tornado.escape.json_encode(return_object)
    elif received_objects['action'] == 'get posts code by num': #i will do it later
        return_object = {} #this is what we would return
        board = received_objects['board']
        if board not in initiate.board_cache: #all of this should be redone, it is fucking not good code
            return 'error'
        in_list = set()
        for postid in received_objects['ids']:
            if postid is not int:
                return 'Incorrect post ids'
            in_list.add(postid)#probably should check, if adding an already existing in set element does not cause an error
        in_list2 = list(in_list)#converting to list for _in function
        database_responce = initiate.sess.Query(initiate.board_cache[board][4].id, initiate.board_cache[board][4].html_code).filter(initiate.board_cache[board][4].id._in(in_list2)).all()
        for row in database_responce:
            return_object[row.id] = row.html_code
            in_list.remove(row.id)
        for postid in in_list:
            return_object[row.id] = None
        #here i should add requesting the db
        return tornado.escape.json_encode(return_object)
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

def get(requesth): #requesth is tornadoweb requesthandler object
    board_exists, board, page = get_board_and_page(requesth.request.uri)
    if board_exists:
        return html_page_return(board, page)
    else:
        return 'No such board'

def post(requesth): #working over POST requests
    board_exists, board, page = get_board_and_page(requesth.request.uri)
    if board_exists == False:
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
