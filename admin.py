import string
import random
#tornadoweb
import tornado.escape
#lxml
import lxml
from lxml.html import builder as E
from lxml.builder import ElementMaker as EM
#sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
#my modules
import config
import initiate

#initing the classes
Base = declarative_base()
class Adminc(Base):
    __tablename__ = 'admins'
    adminid = Column(Integer, primary_key=True)
    login = Column(String(255))
    password = Column(String(255))
    permissions = Column(Integer)
    
    def __repr__(self):
        return "<User(login='%s', password='%s')>" % (self.login, self.password)

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
                   'LOGIN ', E.INPUT(type = 'text', name = 'login', value = ''),
                   E.BR(),
                   'PASSWORD ', E.INPUT(type = 'text', name = 'password', value = ''),
                   E.BR(),
                   E.INPUT(type = 'submit', value = 'LOGIN'),
                   method = 'POST', action = '/admin/login'),
            lxml.html.fromstring("<p>... and this is a parsed fragment ...</p>")
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
            E.BR(),
            lxml.html.fromstring("<p>... and this is a parsed fragment ...</p>")
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
            E.P(E.CLASS("loginmessage"), "You need to login"),
            E.FORM(E.CLASS("loginform"),
                   E.INPUT(type = 'hidden', name = 'action', value = 'create'),
                   E.INPUT(type = 'hidden', name = 'instance', value = 'board'),
                   'ADDRESS ', E.INPUT(type = 'text', name = 'address', value = ''),
                   E.BR(),
                   'Tablename ', E.INPUT(type = 'text', name = 'tablename', value = ''),
                   E.BR(),
                   'Name ', E.INPUT(type = 'text', name = 'name', value = ''),
                   E.BR(),
                   'Fullname ', E.INPUT(type = 'text', name = 'fullname', value = ''),
                   E.BR(),
                   'Description ', E.INPUT(type = 'text', name = 'description', value = ''),
                   E.BR(),
                   E.INPUT(type = 'submit', value = 'Create'),
                   method = 'POST', action = '/admin/'),
            lxml.html.fromstring("<p>... and this is a parsed fragment ...</p>")
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
            if purpose == 'admin':
                return str(board_list)
            if purpose == 'moderator':
                return str(board_list)
            else:
                requesth.write_error(400)
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
    result = session.query(Adminc).filter(Adminc.login==requesth.get_body_argument('login')).first()
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
                #should add checking for incorrect boardnames or tablenames
                board_list = initiate.sess.query(initiate.Board).filter(initiate.Board.address==requesth.get_body_argument('address')).all()
                if board_list != []: #need to add the checking of 'forbidden pages'
                    return 'board with such address exists!'
                board_list = initiate.sess.query(initiate.Board).filter(initiate.Board.tablename==requesth.get_body_argument('tablename')).all()
                if board_list != [] or requesth.get_body_argument('tablename') in initiate.engine.table_names():
                    return 'table with such name exists!'
                #we checked, now we should add this to board cache, create table and write down it to database
                new_board = initiate.Board(address = requesth.get_body_argument('address'), tablename = requesth.get_body_argument('tablename'), name = requesth.get_body_argument('name'), fullname = requesth.get_body_argument('fullname'), description = requesth.get_body_argument('description')) #creating new board in Boards table
                initiate.sess.add(new_board)
                initiate.board_cache[requesth.get_body_argument('address')] = initiate.board_cache_class(new_board, table_exists = False)
                #initiate.board_cache[requesth.get_body_argument('address')] = (requesth.get_body_argument('tablename'), requesth.get_body_argument('name'), requesth.get_body_argument('fullname'), requesth.get_body_argument('description'), type(requesth.get_body_argument('description'), (initiate.Post,initiate.Base), {'__tablename__':requesth.get_body_argument('tablename')}))#add to boardcache and creating the table class
                initiate.board_cache[requesth.get_body_argument('address')].post_class.__table__.create(bind = initiate.engine)#creating table
                initiate.sess.commit()#committing changes to boards table
                initiate.renew_board_cache(renew_cache_dict=False) #here we fuck with the board cache again
                return 'created board successfully' #add redirection
            else:
                requesth.write_error(400)#probably should describe the error
                #it goes when instance creation is not supported
        else:
            requesth.write_error(400)#probably should describe the error
            #it goes when action is not supported
    return 'TO DO'


if __name__ == '__main__':
    print(admin(''))
