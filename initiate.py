import array
import os
#
import sqlalchemy as sqla
import sqlalchemy.orm as sqlaorm
import sqlalchemy.sql as sqlasql
import sqlalchemy.schema as sqlaschema
import sqlalchemy.types as sqlatypes
#
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import sessionmaker
#
#
from lxml.html import builder as E
from lxml.builder import E as EM
#
#
import config as cf
#

Base = declarative_base()
#---------------------------------------------
class Admin(Base):
    __tablename__ = 'admins'
    adminid = sqla.Column(sqla.Integer, primary_key=True)
    login = sqla.Column(sqla.String(255))
    password = sqla.Column(sqla.String(255))
    permissions = sqla.Column(sqla.Integer)
    def __repr__(self):
        return "<Admin(login='%s', password='%s')>" % (self.login, self.password)
#---------------------------------------------

#---------------------------------------------
class Board (Base):
    """Board class for sql table. Bool settings: 1-delete posts, 2-delete threads"""
    __tablename__ = 'boards'
    id = sqla.Column(sqla.Integer, primary_key=True)
    address = sqla.Column(sqla.String(31))
    tablename = sqla.Column(sqla.String(255))
    name = sqla.Column(sqla.String(255))
    fullname = sqla.Column(sqla.String(255))
    description = sqla.Column(sqla.String(255))
    category = sqla.Column(sqla.String(255))
    pictures = sqla.Column(sqla.Integer)
    bumplimit = sqla.Column(sqla.Integer)
    maxthreads = sqla.Column(sqla.Integer)
    bool_settings = sqla.Column(sqla.Integer)
    def __repr__(self):
        return "<User(address = /%s/, name='%s', fullname='%s', description='%s')>" % (self.address, self.name, self.fullname, self.description)
#---------------------------------------------

#---------------------------------------------
class Post():
    id = sqla.Column(sqla.Integer, primary_key=True)
    theme = sqla.Column(sqla.String(255))
    name = sqla.Column(sqla.String(255))
    email = sqla.Column(sqla.String(255))
    text = sqla.Column(sqla.String(cf.post_len)) #this is the text of post. Should be renamed later
    op_post = sqla.Column(sqla.Integer)
    post_time = sqla.Column(sqla.Integer)
    passwd_for_del = sqla.Column(sqla.String(63))
    ip = sqla.Column(sqla.String(15))
    def to_dict(self, ip=False, undeletable=False): #converting the post to dict for javascript answer
        pics = []
        for i in range(self.pic_num):
            pic = getattr(self, 'pic'+str(i))
            if pic is not None:
                pics.append(pic)
        to_dict = {'id':self.id,
                   'theme':self.theme,
                   'name':self.name,
                   'email':self.email,
                   'text':self.text,#will rename
                   'pics':pics,#will be redone for dynamic generating of Post class with many pictures available
                   'op_post':self.op_post,
                   'post_time':self.post_time
                   }
        if ip:
            to_dict['ip'] = self.ip
        if undeletable and op_post is None and passwd_for_del is None:
            to_dict['undeletable'] = True
        return to_dict
    def __repr__(self):
        return "<Post(id = №%d, html_code='%s', picture='%s', op_post='%d')>" % (self.id, self.html_code, self.picture, self.op_post)
    
    @classmethod
    def picture_attrs_list(cls):
        pic_list = []
        for i in range(cls.pic_num):
            pic_list.append(getattr(cls, 'pic'+str(i)))
        return pic_list
#---------------------------------------------

#---------------------------------------------
class Ban(Base):
    __tablename__ = 'bans'
    id = sqla.Column(sqla.Integer, primary_key=True)
    ip = sqla.Column(sqla.String(31))
    initiator = sqla.Column(sqla.String(255))
    date = sqla.Column(sqla.Integer)
    level = sqla.Column(sqla.Integer, default=0)
    def __repr__(self):
        return "<User(ip = /%s/, initiator='%s', date='%d')>" % (self.ip, self.initiator, self.date)
#---------------------------------------------
    
#-----------------------------------------------------------------------------------------------------------------------------------
class board_cache_class(): 
    def __init__(self, b, table_exists=True):
        """table_exists flag is used when we do not need to ask table as it is not created yet"""
        self.address = b.address #will be needed for form generating
        self.tablename = b.tablename
        self.name = b.name
        self.fullname = b.fullname
        self.description = b.description
        self.pictures = b.pictures
        self.delete_posts = bool(b.bool_settings & 1)
        self.delete_threads = bool(b.bool_settings & 2) #will be redone to get values from sql
        self.bumplimit = b.bumplimit
        self.maxthreads = b.maxthreads
        self.post_form_type = 'lxml' #or html
        self.post_form = self._lxml_form_generator() #will be added the form generating, or reading from file

        self.generate_sql_class()
        
        self.threads = array.array('L') #we do this because we need a list of integers, not ordered tuples
        if table_exists:
            #here we need to get threads ordered by last post time and depending on bumplimit
            #a_alias = self.post_class
            subq2 = sess.query(coalesce(self.post_class.op_post, self.post_class.id).label('coalesce'), self.post_class.id).filter().subquery()
            subq = sess.query(self.post_class.id, subq2.c.id.label('threadid'), sqla.func.count(subq2.c.coalesce).label('posts_before')).outerjoin(subq2, subq2.c.coalesce == coalesce(self.post_class.op_post, self.post_class.id)).filter(subq2.c.id <= self.post_class.id).having(sqla.func.count(subq2.c.coalesce) <= self.bumplimit+1).group_by(self.post_class.id, subq2.c.coalesce).order_by(self.post_class.id.desc()).subquery()        
            threads_tuples = sess.query(subq.c.threadid).filter().distinct().all() #getting threads list
            for thread in threads_tuples:
                self.threads.append(thread[0])
            #self.threads.reverse()
            print(self.threads)
        self.posts_dict = {}
        for thread in self.threads:
            self.posts_dict[thread] = array.array('L') #array.array is faster
        if table_exists:
            posts = sess.query(self.post_class.id, self.post_class.op_post).filter(self.post_class.op_post != None).all()
            for each_post in posts:
                self.posts_dict[each_post.op_post].append(each_post.id)

    def generate_sql_class(self):
        """creating class for sql"""
        params_dict = {'__tablename__':self.tablename,
                       'pic_num':self.pictures}
        if self.pictures > 0:
            hashes_list = []
            for i in range(self.pictures):
                params_dict['pic'+str(i)] = sqla.Column(sqla.String(255))
                params_dict['hash'+str(i)] = sqla.Column(sqla.String(255))#need to make it lenght as long as hash
                hashes_list.append('hash'+str(i))
            params_dict['__table_args__'] = (sqla.UniqueConstraint(*hashes_list, name = '_'+self.tablename + '_picture_hash'),)
        self.post_class = type(self.tablename, (Post,Base), params_dict) #class post for table
        return

    def add_post(self, op, new_id): #will be redone, after limit of threads will be introduced
        """This function is adding new threads or bumping old ones"""
        if op == 0:
            if self.maxthreads != -1 and len(self.threads) >= self.maxthreads:
                self.threads.pop()
            self.threads.reverse() #reversing list for faster appending
            self.threads.append(new_id) 
            self.threads.reverse()
            self.posts_dict[new_id] = array.array('L')
        else:
            if len(self.posts_dict[op]) < self.bumplimit:
                self.threads.remove(op) #not sure, if we should remove it from reversed list or not reversed
                self.threads.reverse() #reversing list for faster appending
                self.threads.append(op)
                self.threads.reverse()
            self.posts_dict[op].append(new_id)
        return

    def remove_op_posts(self, posts):
        deleted = 0
        for post in posts:
            if post in self.posts_dict:
                deleted += 1
                try:
                    self.threads.remove(post)
                except ValueError:
                    pass
                del self.posts_dict[post]
        return deleted
    
    def _lxml_form_generator(self):
        """Is used for generating lxml post form"""
        formargs = []
        formargs.append(E.TR(
                              E.TD('EMAIL'),
                              E.TD(E.INPUT(type = 'text', name = 'email', value = '', id = 'emailfield'),
                                   E.INPUT(type = 'submit', value = 'POST', id = 'postbutton')
                                   ),
                              )
                        )
        formargs.append(E.TR(
                              E.TD('THEME'),
                              E.TD(E.INPUT(type = 'text', name = 'theme', value = '', size = '50')),
                              )
                        )
        formargs.append(E.TR(
                              E.TD('NAME'),
                              E.TD(E.INPUT(type = 'text', name = 'name', value = '', size = '50')),
                              )
                        )
        formargs.append(E.TR(
                              E.TD('TEXT'),
                              E.TD(E.TEXTAREA(name = 'text', rows = '8', cols = '50', placeholder = 'POST')),
                              )
                        )
        if self.pictures == 0:
            pass
        elif self.pictures == 1:
            formargs.append(E.TR(#should add checking if pics are available
                              E.TD('PICTURE'),
                              E.TD(E.INPUT(type = 'file', name = 'file0', accept = 'image/*'),
                                   id = 'filecellone'),
                              )
                            )
        else:
            formargs.append(E.TR(#should add checking if pics are available
                              E.TD('PICTURE'),
                              E.TD(E.INPUT(type = 'file', name = 'file0', accept = 'image/*'),
                                   E.BUTTON('+', type = 'button', onclick = 'add_file_input(this);', id = '0filebutton'),
                                   E.SPAN(str(self.pictures), style = 'display:none;', id = 'maxfiles'),
                                   id = 'filecellmany'),
                              )
                            )
        formargs.append(E.TR(#should add checking if deleting is available
                              E.TD('PASSWORD'),
                              E.TD(E.INPUT(type = 'password', name = 'password', value = '', size = '10'),
                                   id = 'passwordcell'),
                              )
                        )
        if True:#should add checking if captcha is available
            formargs.append(E.TR(
                              E.TD(
                                  E.CENTER('CAPTCHA WILL BE HERE'),
                                  colspan = '2'
                                  )
                              )
                            )
            formargs.append(E.TR(E.TD('CAPTCHA'),
                                 E.TD(E.INPUT(type = 'text', name = 'captcha', value = '')),
                                 )
                            )
            
        
        form = E.FORM(E.CLASS("postform"), #postform
                      E.INPUT(type = 'hidden', name = 'action', value = 'post'),
                      E.INPUT(type = 'hidden', name = 'op', value = '0', id = 'op_referer'),
                      E.SCRIPT('document.getElementById("op_referer").value = document.getElementById("thread").innerHTML;'),
                      E.TABLE(*formargs),
                      method = 'POST', action = '/'+self.address, enctype = 'multipart/form-data', id = 'postform')
        return form
#-----------------------------------------------------------------------------------------------------------------------------------

def generate_navigation_board_list(boards): #would be redone
    categories = {}
    for b in boards:
        #if b.hidden = none
        #should add for hidden boards
        if b.category in categories:
            categories[b.category].append((b.address, b.name))
        else:
            categories[b.category] = [((b.address, b.name))]
    spans = []
    iter_list = list(categories.keys())
    iter_list.sort()
    for category in iter_list: #probably another order would be better
        urls = []
        for params in categories[category]:
            urls.append(
                E.A(
                    params[0], #the name
                    title = params[1],#bydlocode, better to find another way
                    href = '/' + params[0] + '/',
                    )
                )
            urls.append('/')
        urls.pop()
        if category is None:
            category = ''
        urls = [E.CLASS('boardcategory'), category+' ['] + urls + [']']
        spans.append(E.SPAN(*urls))
    code = EM('nav',
        E.CLASS('boardlist'),
        *spans
        )
    return code
#-----------------------------------------------------------------------------------------------------------------------------------

def generate_main_page_board_list(boards):
    #categories = {}
    #for b in boards:
        #if b.hidden = none
        #should add for hidden boards
        #if b.category in categories:
            #categories[b.category].append((b.address, b.name))
        #else:
            #categories[b.category] = [((b.address, b.name))]
    divs = []
    #iter_list = list(categories.keys())
    #iter_list.sort()
    #for category in iter_list: #probably another order would be better
    blocks = []
    for b in boards:
        blocks.append(
                      E.A(
                          E.DIV(E.CLASS("mainboardlistitem"),
                                        E.DIV(E.CLASS("mbldiv"),
                                              E.SPAN(E.CLASS("mblboardaddress"),
                                                     '/'+b.address
                                                     ),
                                              E.SPAN(E.CLASS("mbldash"),
                                                     '-'
                                                     ),
                                              E.SPAN(E.CLASS("mblfullname"),
                                                     b.fullname
                                                     ),
                                              ),
                                        E.DIV(E.CLASS("mbldiv"),
                                              E.SPAN(E.CLASS("mbldescription"),
                                                     b.description
                                                     )
                                              ),
                                ),
                          href = '/' + b.address + '/',
                          )
                      )
    for i in range(3):
        blocks.append(E.DIV(E.CLASS("mblemptyfillers")))
    code = E.DIV(E.CLASS('mainboardlist'),
                 *blocks
                 )
    return code
#-----------------------------------------------------------------------------------------------------------------------------------

def renew_board_cache(renew_cache_dict=True, renew_thread_cache=True, renew_style_cache=True):
    global board_cache#should be done by the request
    global board_cache_navigation
    global board_cache_main_page
    global style_cache
    boards = sess.query(Board).filter().all()#add 'order by'
    if renew_cache_dict:
        board_cache = {}
        for b in boards:
            board_cache[b.address] = board_cache_class(b)
    if cf.static_board_footer:
        board_cache_navigation = cf.board_cache_footer
    else:
        board_cache_navigation = generate_navigation_board_list(boards) #there must be html code generated
    if cf.static_board_main_page:
        board_cache_main_page = cf.board_cache_main_page
    else:
        board_cache_main_page = generate_main_page_board_list(boards)#there must be html code generated
    if renew_style_cache:
        style_cache = []
        for f in os.listdir('css'):
            fname, ext = os.path.splitext(f)
            if ext == '.css':
                style_cache.append(E.LINK(E.CLASS('stylesheetlink'), rel="alternate stylesheet", title=fname, href='/css/'+f, type="text/css"))

def init():
    #checking sqldb
    global engine
    engine = sqla.create_engine(cf.sqldbtype+'://'+cf.user+':'+cf.passwd+'@'+cf.hostname+'/'+cf.dbname+'?charset=utf8',echo = cf.sqllogging, encoding='utf-8')
    Session = sessionmaker(bind = engine)
    global sess
    sess = Session()
    #---------------------------------------------------------------------------------------------
    #checking for tables
    if Admin.__table__.exists(bind = engine):
        pass
    else:
        Admin.__table__.create(bind = engine)
        Admin.__table__.insert(bind = engine).values(login = 'admin', password = 'admin', permissions = 0).execute()
    
    if Board.__table__.exists(bind = engine):
        pass
    else:
        Board.__table__.create(bind = engine)
    if Ban.__table__.exists(bind = engine):
        pass
    else:
        Ban.__table__.create(bind = engine)
    #creating board cache
    renew_board_cache() #the renewal function
    #-----------------------------------------------------------------------------------
    #init the variables
    return

if __name__ == '__main__':
    pass
