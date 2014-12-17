import sqlalchemy as sqla
import sqlalchemy.orm as sqlaorm
import sqlalchemy.sql as sqlasql
import sqlalchemy.schema as sqlaschema
import sqlalchemy.types as sqlatypes
#
import config as cf

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

#---------------------------------------------
class Board (Base):
    __tablename__ = 'boards'
    id = sqla.Column(sqla.Integer, primary_key=True)
    address = sqla.Column(sqla.String(31))
    tablename = sqla.Column(sqla.String(255))
    name = sqla.Column(sqla.String(255))
    fullname = sqla.Column(sqla.String(255))
    description = sqla.Column(sqla.String(255))
    def __repr__(self):
        return "<User(address = /%s/, name='%s', fullname='%s', description='%s')>" % (self.address, self.name, self.fullname, self.description)
#---------------------------------------------

#---------------------------------------------
class Post(): #(Base):
    #__tablename__ = 
    id = sqla.Column(sqla.Integer, primary_key=True)
    html_code = sqla.Column(sqla.String(cf.post_len))
    picture = sqla.Column(sqla.String(255))
    op_post = sqla.Column(sqla.Integer)
    def __repr__(self):
        return "<Post(id = №%d, html_code='%s', picture='%s', op_post='%d')>" % (self.id, self.html_code, self.picture, self.op_post)
#---------------------------------------------

def renew_board_cache(renew_cache_dict = True, renew_thread_cache = True):
    global board_cache#should be done by the request
    global board_cache_footer
    global board_cache_main_page
    boards = sess.query(Board).filter().all()#add 'order by'
    board_cache = {}
    if renew_cache_dict:
        for b in boards:
            board_post_class = type(b.name, (Post,Base), {'__tablename__':b.tablename}) #class post for table
            #here we need to get threads ordered by last post time
            threads = sess.query(coalesce(board_post_class.op_post, board_post_class.id)).filter().distinct().all() #getting threads list
            posts_dict = {}
            for thread in threads:
                posts_dict[thread] = []
            posts = sess.query(board_post_class.id, board_post_class.op_post).filter(board_post_class.op_post != None).all()
            for each_post in posts:
                posts_dict[each_post.op_post].append(each_post.id)
            board_cache[b.address] = (b.tablename, b.name, b.fullname, b.description, board_post_class, threads, posts_dict)#tablename, name, fullname, desc
            
    if cf.static_board_footer == True:
        board_cache_footer = cf.board_cache_footer
    else:
        board_cache_footer = ''#there must be html code generated
    if cf.static_board_main_page == True:
        board_cache_main_page = cf.board_cache_main_page
    else:
        board_cache_main_page = ''#there must be html code generated

def init():
    #checking sqldb
    global engine
    engine = sqla.create_engine(cf.sqldbtype+'://'+cf.user+':'+cf.passwd+'@'+cf.hostname+'/'+cf.dbname,echo = cf.sqllogging)
    Session = sessionmaker(bind = engine)
    global sess
    sess = Session()
    #---------------------------------------------------------------------------------------------
    #checking for admintable
    admint = sqlaschema.Table('admins',
                              sqlaschema.MetaData(bind = engine),
                              sqlaschema.Column('adminid', sqlatypes.Integer, primary_key = True),
                              sqlaschema.Column('login', sqlatypes.String(length = 255)),
                              sqlaschema.Column('password', sqlatypes.String(length = 255)),
                              sqlaschema.Column('permissions', sqlatypes.Integer)
                              )
    if admint.exists(bind = engine):
        #print('table exists')
        pass
    else:
        admint.create(bind = engine)
        admint.insert(bind = engine).values(login = 'admin', password = 'admin', permissions = 0).execute()
    #checking for boards table
    if Board.__table__.exists(bind = engine):
        pass
    else:
        Board.__table__.create(bind = engine)
    #creating board cache
    renew_board_cache() #the renewal function
    #-----------------------------------------------------------------------------------
    
    #init the variables
    global admin_cookie_list
    admin_cookie_list = []
    return

if __name__ == '__main__':
    pass
