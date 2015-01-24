import string
import random
import os
import re
#tornadoweb
import tornado.escape
#lxml
import lxml
from lxml.html import builder as E
from lxml.builder import ElementMaker as EM
#sqlalchemy
from sqlalchemy.orm import sessionmaker
#my modules
import config
import initiate

def login_page_gen():
    html = E.HTML(
        E.HEAD(
            E.LINK(rel="stylesheet", href="/css/deeplight.css", type="text/css"),
            E.TITLE("Administration and moderation")
            ),
        E.BODY(
            E.H1(E.CLASS("heading"), "Farlight Engine Imageboard"),
            E.P(E.CLASS("loginmessage"), "You need to login"),
            E.FORM(E.CLASS("loginform"),
                   E.TABLE(
                       E.TR(E.TD('LOGIN'), E.TD(E.INPUT(type = 'text', name = 'login', value = ''))),
                       E.TR(E.TD('PASSWORD'), E.TD(E.INPUT(type = 'text', name = 'password', value = ''))),
                       ),
                   E.INPUT(type = 'submit', value = 'LOGIN'),
                   method = 'POST',
                   action = '/admin/login'
                   )
            )
        )
    return lxml.html.tostring(html)

def main_page_gen():
    html = E.HTML(
        E.HEAD(
            E.LINK(rel="stylesheet", href="/css/deeplight.css", type="text/css"),
            E.TITLE("Administration and moderation")
            ),
        E.BODY(
            E.H1(E.CLASS("heading"), "Farlight Engine Imageboard"),
            E.P(E.CLASS("loginmessage"), "You are logged in"),
            E.A("create board", href = '?action=create&create=board'),
            E.BR(),
            E.A("manage boards", href = '?action=list&list=boards&purpose=admin'),
            E.BR(),
            E.A("moderate boards", href = '?action=list&list=boards&purpose=moderator'),
            E.BR(),
            E.A("manage users", href = '?action=list&list=users&purpose=admin'),
            E.BR()
            )
        )
    return lxml.html.tostring(html)

def board_creation_menu(): #here is the html board creation menu
    html = E.HTML(
        E.HEAD(
            E.LINK(rel="stylesheet", href="/css/deeplight.css", type="text/css"),
            E.TITLE("Creating board")
            ),
        E.BODY(
            E.H1(E.CLASS("heading"), "Farlight Engine Imageboard"),
            E.FORM(E.CLASS("loginform"),
                   E.INPUT(type = 'hidden', name = 'action', value = 'create'),
                   E.INPUT(type = 'hidden', name = 'instance', value = 'board'),
                   E.TABLE(
                       E.TR(E.TD('Address'), E.TD(E.INPUT(type = 'text', name = 'address', value = ''))),
                       E.TR(E.TD('Tablename'), E.TD(E.INPUT(type = 'text', name = 'tablename', value = ''))),
                       E.TR(E.TD('Name'), E.TD(E.INPUT(type = 'text', name = 'name', value = ''))),
                       E.TR(E.TD('Fullname'), E.TD(E.INPUT(type = 'text', name = 'fullname', value = ''))),
                       E.TR(E.TD('Description'), E.TD(E.INPUT(type = 'text', name = 'description', value = ''))),
                       E.TR(E.TD('Pics number'), E.TD(E.INPUT(type = 'number', name = 'picsnum', value = '', min = '0'))),
                       ),
                   E.INPUT(type = 'submit', value = 'Create'),
                   method = 'POST',
                   action = '/admin/'
                   )
            )
        )
    return lxml.html.tostring(html)

def list_boards_menu(board_list, purpose):
    """need to put boards table creating to a separate function in future"""
    tablerows = [E.TR(E.TD(E.A(b.address, href = '/'+b.address)),E.TD(b.tablename),E.TD(str(b.name)),E.TD(str(b.fullname)),E.TD(str(b.description)),E.TD(str(b.category))) for b in board_list]
    #purpose will be applyed later
    html = E.HTML(
        E.HEAD(
            E.LINK(rel="stylesheet", href="/css/deeplight.css", type="text/css"), 
            E.TITLE("Creating board")
            ),
        E.BODY(
            E.H1(E.CLASS("heading"), "Listing boards"),
            E.TABLE(
                E.CLASS("boardstable"),
                E.TR(E.TH('Адрес'),E.TH('Таблица'),E.TH('Название'),E.TH('Полное название'),E.TH('Описание'),E.TH('Категория')),
                *tablerows
                )
            )
        )
    return lxml.html.tostring(html)

def admin(requesth):
    if requesth.current_user == None:
        requesth.set_header('Location', '/admin/login')
        requesth.set_status(302)
        return 'Redirecting to login'
    actions = requesth.get_query_arguments('action')
    if actions == []:
        return main_page_gen()
    elif actions == ['list']:
        what_to_list = requesth.get_query_argument('list')
        purpose = requesth.get_query_argument('purpose')
        #add purpose checking
        if what_to_list == 'boards': #here we list boards for management
            board_list = initiate.sess.query(initiate.Board).all()
            return list_boards_menu(board_list, purpose)
        elif what_to_list == 'users':#here we list users for management
            return 'users list'
        else:
            return 'No such list'
    elif actions == ['create']:
        create = requesth.get_query_argument('create')
        if create == 'board':
            return board_creation_menu()
        else:
            return 'There are other create menu'
    else:
        requesth.write_error(400)

def admin_login(requesth):
    Session = sessionmaker(bind=initiate.engine)
    session = Session()
    result = session.query(initiate.Admin).filter(initiate.Admin.login==requesth.get_body_argument('login')).first()
    if result == None:
        return 'Incorrect Login\Password'
    if requesth.get_body_argument('password') != result.password:
        return 'Incorrect Login\Password'
    #запилить проверку результата
    
    requesth.set_secure_cookie("user", tornado.escape.xhtml_escape(requesth.get_body_argument('login')))
    requesth.set_header('Location', '/admin/')
    requesth.set_status(302)
    return 'Logged successfully' #checking should be added

def admin_post(requesth):        
    if requesth.current_user == None:
        requesth.set_header('Location', '/admin/login')
        requesth.set_status(302)
        return 'Redirecting to login'
    else:
        action = requesth.get_body_argument('action')
        if action == 'login':#what we do to login
            return 'TO DO'
        elif action == 'create':#here it goes when we create smth
            instance = requesth.get_body_argument('instance')
            if instance == 'board': #we create the board here
                #to do the board creation
                match = re.match('[a-z0-9]+', requesth.get_body_argument('address'))
                if match == None or match.group() != requesth.get_body_argument('address'):
                    return 'Incorrect address'
                match = re.match('[a-z0-9]+', requesth.get_body_argument('tablename'))
                if match == None or match.group() != requesth.get_body_argument('tablename'):
                    return 'Incorrect tablename'
                try:
                    picsnum = int(requesth.get_body_argument('picsnum'))
                    if picsnum < 0 or picsnum > 10: #should add limit from config
                        return 'Incorrect pictures number!'
                except ValueError:
                    return 'Incorrect pictures number!'
                board_list = initiate.sess.query(initiate.Board).filter(initiate.Board.address==requesth.get_body_argument('address')).all()
                if board_list != []: #need to add the checking of 'forbidden pages'
                    return 'board with such address exists!'
                board_list = initiate.sess.query(initiate.Board).filter(initiate.Board.tablename==requesth.get_body_argument('tablename')).all()
                if board_list != [] or requesth.get_body_argument('tablename') in initiate.engine.table_names():
                    return 'table with such name exists!'
                #we checked, now we should add this to board cache, create table and write down it to database
                new_board = initiate.Board(address = requesth.get_body_argument('address'), tablename = requesth.get_body_argument('tablename'), name = requesth.get_body_argument('name'), fullname = requesth.get_body_argument('fullname'), description = requesth.get_body_argument('description'), pictures = picsnum) #creating new board in Boards table
                try:
                    os.makedirs(os.path.join('content', new_board.address, 'img'))
                    os.makedirs(os.path.join('content', new_board.address, 'thumbs'))
                except OSError:
                    return 'Failed to create folders'
                initiate.sess.add(new_board)
                initiate.board_cache[requesth.get_body_argument('address')] = initiate.board_cache_class(new_board, table_exists = False)
                #initiate.board_cache[requesth.get_body_argument('address')] = (requesth.get_body_argument('tablename'), requesth.get_body_argument('name'), requesth.get_body_argument('fullname'), requesth.get_body_argument('description'), type(requesth.get_body_argument('description'), (initiate.Post,initiate.Base), {'__tablename__':requesth.get_body_argument('tablename')}))#add to boardcache and creating the table class
                initiate.board_cache[requesth.get_body_argument('address')].post_class.__table__.create(bind = initiate.engine)#creating table
                initiate.sess.commit()#committing changes to boards table
                initiate.renew_board_cache(renew_cache_dict=False) #here we fuck with the board cache again
                return 'created board successfully<br><a href = "/'+new_board.address+'">'+new_board.address+'</a>' #add redirection
            else:
                requesth.write_error(400)#probably should describe the error
                #it goes when instance creation is not supported
        else:
            requesth.write_error(400)#probably should describe the error
            #it goes when action is not supported
    return 'TO DO'


if __name__ == '__main__':
    print(admin(''))
