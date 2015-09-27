#this is the file for the functions, shared beatween many modules

import time
import regex
import hashlib
import os.path
import string
import random

import tornado.escape

import sqlalchemy.exc

import lxml
from lxml.html import builder as E
from lxml.builder import E as EE

import wand.image

import initiate
import config as cf

import sqlalchemy

def get_user_permissions(user, board, action):
    if user is None:
        return False
    else:
        #if action == 'some action':
        #    get permissions from db
        #    return True/False
        return True

def generate_new_path(board, extension):
    """Here we generate pathes for saving the files ad thumbs"""
    newname = str(int(time.mktime(time.localtime()))) + ''.join(random.choice(string.digits) for _ in range(3))  + extension 
    return os.path.join('content', board, 'img', newname), newname, os.path.join('content', board, 'thumbs', 's'+newname)

#--------------------------------------
class PicFile():
    def __init__(self, file, board):
        self.board = board
        self.blob = file['body']
        m = hashlib.md5()
        m.update(self.blob)
        self.hash = m.hexdigest()
        self.extension = os.path.splitext(file['filename'])[1]
        self.path, self.fname, self.thumbpath = generate_new_path(self.board, self.extension)
        while os.path.exists(self.path):
            self.path, self.fname, self.thumbpath = generate_new_path(self.board, self.extension)

    def save_file_and_preview(self):
        """File saving and preview generation"""
        with wand.image.Image(blob=self.blob) as img: #probably should add hint file format
            img.save(filename=self.path)
            resize_coeff = 300/max(img.width, img.height)
            if resize_coeff >= 1.0:
                resize_coeff = 1
            img.sample(int(img.width*resize_coeff), int(img.height*resize_coeff))
            img.save(filename=self.thumbpath)
        return
#--------------------------------------
    

def find_replacement(match):
    if match.lastgroup == 'newline':
        return (match.end()-match.start())*'<br>'
    elif match.lastgroup == 'newlineatend':
        return ''
    elif match.lastgroup == 'postlink': #make a separate handler for it
        return '<a class = "rl" href=javascript:highlight(' + match.group('postlink')[8:] + ');>'+match.group('postlink')+'</a>'
    elif match.lastgroup == 'wakabab':
        return '<strong>' + match.group('wakabab')[2:-2] + '</strong>'
    elif match.lastgroup == 'wakabaspoiler':
        return '<span class="s">' + match.group('wakabaspoiler')[2:-2] + '</span>'
    elif match.lastgroup == 'wakabai':
        return '<i>' + match.group('wakabai')[1:-1] + '</i>'
    elif match.lastgroup == 'wakabaquote':
        return '<span class = "q">' + match.group('wakabaquote') + '</span>'
    elif match.lastgroup == 'url':
        return '<a href=' + match.group('url') + '>'+ match.group('url') +'</a>'

nl2br = regex.compile('(?P<newline>\n+)(?<!$)|(?P<newlineatend>\n+)(?=$)|(?P<postlink>&gt;&gt;[0-9]+)|(?P<wakabab>(?<=^|[^\*])\*\*[^\*\n]+?\*\*(?=[^\*]|$))|(?P<wakabai>(?<=^|[^\*])\*[^\*\n]+\*(?=[^\*]|$))|(?P<wakabaspoiler>(?<=^|[^%])%%[^%\n]+?%%(?=[^%]|$))|(?P<wakabaquote>(?<!&gt;)&gt;.+?(?=$|\n))|(?P<url>^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)([a-zA-Z0-9\-‌​\.\?\,\'\/\\\+&%\$#_]*)?$)')

def add_markup(text):
    text = text.replace('\r\n', '\n')
    text = text.replace('\n\r', '\n')
    #print('==========================')
    #heads = []
    #tails = []
    #for m in nl2br.finditer(text, overlapped = True):
        #print(m.group())
        #heads.append((m.start(), m))
        #tails.append((m.end(), m))
    text = nl2br.sub(find_replacement, text)
    #print('==========================')
    return text

def posting(requesth, board): #working with posted form content
    action = requesth.get_body_argument('action')
    if action == 'post':#here we act when adding a new post

        #checking if user is banned
        #should add board level for bans not applyed on some boards
        ban = initiate.sess.query(initiate.Ban).filter(initiate.Ban.ip == requesth.request.remote_ip).first()
        if ban is not None:
            return 'Your ip '+ban.ip+' was banned '+ time.strftime('%d-%m-%Y %H:%M', time.localtime(ban.date)) +' (server time) by '+ban.initiator
        
        post_content = {} #will be send as kwargs to database query

        #op referer
        op = requesth.get_body_argument('op')
        try: #prepairing op referer
            op = int(op)
        except ValueError:
            return 'Incorrect op referer'
        if op != 0:
            if op not in initiate.board_cache[board].posts_dict:
                return 'Thread does not exist'
            post_content['op_post'] = op
        
        #theme
        theme = tornado.escape.xhtml_escape(requesth.get_body_argument('theme'))
        if len(theme) > 255:
            return 'Too long theme' #should add html escaping
        if theme != '':
            post_content['theme'] = theme
        
        #email #need to add sage option
        email = tornado.escape.xhtml_escape(requesth.get_body_argument('email'))
        if len(email) > 255:
            return 'Too long email'
        if email != '':
            post_content['email'] = email
        
        #name #here should be added tripcodes
        name = tornado.escape.xhtml_escape(requesth.get_body_argument('name'))
        if len(name) > 255:
            return 'Too long name'
        if name != '':
            post_content['name'] = name
        else:
            post_content['name'] = 'Аноним'
        
        #text of post
        text = tornado.escape.xhtml_escape(requesth.get_body_argument('text'))
        text = add_markup(text)
        if len(text) > cf.post_len:
            return 'Too long text'
        elif text == '':
            return 'No text were entered'
        post_content['text'] = text

        #file management
        there_are_files = False
        filesnum = len(requesth.request.files)
        if filesnum != 0: #would be redone for multiple file management
            if filesnum > initiate.board_cache[board].pictures:
                return 'Too much files!'
            there_are_files = True
            i = 0
            j = 0
            files = []
            while j < filesnum and i < initiate.board_cache[board].pictures: #second case is not needed, probably, but to be sure i add it
                try:
                    the_file = requesth.request.files['file'+str(i)][0]
                except KeyError:
                    pass
                else:
                    files.append(PicFile(the_file, board))
                    post_content['pic'+str(j)] = files[j].fname
                    post_content['hash'+str(j)] = files[j].hash
                    j += 1
                i+=1
        #that's not all, file is written after post is committed to db
        
        #adding ip
        post_content['ip'] = requesth.request.remote_ip
        
        #adding timestamp
        post_content['post_time'] = int(time.time())

        #password
        passwd = requesth.get_body_argument('password')
        if len(passwd):
            post_content['passwd_for_del'] = passwd
        else:
            post_content['passwd_for_del'] = None
        
        #preparing the post for database
            #posting should be done as a subfunction of the BOARD class
        new_post = initiate.board_cache[board].post_class(**post_content)
            #posting to the database
        initiate.sess.add(new_post)
        try:
            initiate.sess.commit()
        except sqlalchemy.exc.IntegrityError:
            initiate.sess.rollback()
            return 'This picture has already been posted'
            #adding the post to the cache
        initiate.board_cache[board].add_post(op, new_post.id)

        #adding the file and generating preview
        if there_are_files:
            for each_file in files:
                each_file.save_file_and_preview()            
        
        #returning redirect on success
        if op == 0:
            location = '/'+board+'/'
        else:
            location = '/'+board+'/res/'+str(op)+'#'+str(new_post.id)
        requesth.set_header('Location', location)
        requesth.set_status(302)
        return 'Luckily posted'
    else:
        return 'not implemented yet'
    #

def _delete_pictures(board, row):
    for i in range(initiate.board_cache[board].pictures): #deleting pics
        fname = getattr(row, 'pic'+str(i))
        if fname is not None:
            try:
                os.remove(os.path.join('content', board, 'img', fname))
            except OSError:
                pass
            fname = 's'+fname #deleting preview
            try:
                os.remove(os.path.join('content', board, 'thumbs', fname))
            except OSError:
                pass
    return

def delete_posts_by_ids(requesth, received_objects):
    board = received_objects['board']
    if board not in initiate.board_cache:
        return 'Incorrect board name'
    posts = received_objects['posts_to_del']
    if not isinstance(posts, list):
        return 'Incorrect list of posts'
    for post in posts:
        if not isinstance(post, int):
            return 'Incorrect types!'
    #should add checking if board supports deleting
    #also should add support for thread deleting
    board_post_class = initiate.board_cache[board].post_class
    if get_user_permissions(requesth.current_user, board, 'delete posts by ids'):
        if get_user_permissions(requesth.current_user, board, 'delete threads'):
            print('-------------------------------------------')
            print(board_post_class.picture_attrs_list())
            posts_deleted = initiate.sess.query(board_post_class.id, board_post_class.op_post, *board_post_class.picture_attrs_list()).filter(board_post_class.id.in_(posts)).order_by(board_post_class.op_post)
        else:
            posts_deleted = initiate.sess.query(board_post_class.id, board_post_class.op_post).filter(board_post_class.op_post != None).filter(board_post_class.id.in_(posts)).order_by(board_post_class.op_post)
    else:
        passwd = received_objects['passwd']
        if passwd == '' or passwd is None:
            return 'Incorrect password!'
        if initiate.board_cache[board].delete_threads:
            posts_deleted = initiate.sess.query(board_post_class.id, board_post_class.op_post).filter(board_post_class.id.in_(posts)).filter(board_post_class.passwd_for_del == passwd).order_by(board_post_class.op_post)
        else:
            posts_deleted = initiate.sess.query(board_post_class.id, board_post_class.op_post, *board_post_class.picture_attrs_list()).filter(board_post_class.id.in_(posts)).filter(board_post_class.op_post != None).filter(board_post_class.passwd_for_del == passwd).order_by(board_post_class.op_post)
            
    ids_for_del = set()
    ops_for_del = []
    only_picture = False
    for row in posts_deleted:
        if row.op_post is None:
            try:
                initiate.board_cache[board].threads.remove(row.id)
                del initiate.board_cache[board].posts_dict[row.id]
            except (KeyError, ValueError):
                pass
            ops_for_del.append(row.id)
        else:
            try:
                initiate.board_cache[board].posts_dict[row.op_post].remove(row.id)
            except (KeyError, ValueError):
                pass
        ids_for_del.add(row.id)
        _delete_pictures(board, row)

    if len(ops_for_del) > 0:
        posts_deleted = initiate.sess.query(board_post_class.id, board_post_class.op_post, *board_post_class.picture_attrs_list()).filter(board_post_class.op_post.in_(ops_for_del))
        for row in posts_deleted:
            try:
                initiate.board_cache[board].posts_dict[row.op_post].remove(row.id)
            except (KeyError, ValueError):
                pass
            ids_for_del.add(row.id)
            _delete_pictures(board, row)
        
    ids_for_del = list(ids_for_del)
    
    if len(ids_for_del) > 0:
        posts_deleted_num = initiate.sess.query(board_post_class).filter(board_post_class.id.in_(ids_for_del)).delete(synchronize_session='fetch')
        initiate.sess.commit()
    else:
        posts_deleted_num = 0
    return tornado.escape.json_encode(posts_deleted_num)

def ban_by_ip(requesth, received_objects):
    if not get_user_permissions(requesth.current_user, '', 'ban by ip'):
        return 'You have no permissions to ban'
    ip = received_objects['ip']
    if not isinstance(ip, str):
        return 'Incorrect IP!'
    ban = initiate.sess.query(initiate.Ban).filter(initiate.Ban.ip == ip).first()
    if ban is not None:
        return 'IP ' + ip + ' is already banned by ' + ban.initiator + ' ' + time.strftime('%d/%m/%Y %H:%M', time.localtime(ban.date)) + ' with level ' + str(ban.level)
    new_ban = initiate.Ban(initiator = requesth.current_user,
                           ip = ip,
                           date = int(time.time())
                           )#ban levels would be added
    initiate.sess.add(new_ban)
    initiate.sess.commit()
    return 'Ban on ip ' + ip + ' is added'

def get_posts_code_by_num(requesth, received_objects): #function for returning the posts code for a list of posts ids
    board = received_objects['board']
    if board not in initiate.board_cache: #all of this should be redone, it is fucking not good code
        return 'error'
    
    post_kwargs = {} #probably should be redone to make db return what we need
    if get_user_permissions(requesth.current_user, board, 'get posts code by num'):
        post_kwargs = {'ip':True}
    return_object = {} #this is what we would return
    
    in_list = set()
    for postid in received_objects['ids']:
        if not isinstance(postid, int):
            return 'Incorrect post ids'
        in_list.add(postid)#probably should check, if adding an already existing in set element does not cause an error
    in_list2 = list(in_list)#converting to list for _in function
    if in_list2:
        database_responce = initiate.sess.query(initiate.board_cache[board].post_class).filter(initiate.board_cache[board].post_class.id.in_(in_list2)).all()
        for row in database_responce:
            return_object[row.id] = row.to_dict(**post_kwargs)#probably need to be redone
            in_list.remove(row.id)
        for postid in in_list: #here we add all the posts that does not exist
            return_object[postid] = None
    return tornado.escape.json_encode(return_object)

def decorator_for_style(func):
    """Make it sure, that the first arg is tornado.web.RequestHandler object"""
    def inner(*args, **kwargs):
        """Adding default_style variable depending on cookie"""
        cook = args[0].get_cookie('stylename')
        if cook is None:
            kwargs['default_style']=cf.default_style
        else:
            kwargs['default_style']=cook
        return func(*args, **kwargs)
    return inner
    
def generate_right_up_corner_menu():
    html = E.SPAN(E.CLASS('rightupmenu'),
                  E.SPAN('[', E.A('Стили', href='#', onclick='stylechanger(this);'), ']'),
                  E.SPAN('[', E.A('Главная', href='/'), ']'),
                  E.SPAN('[', E.A('A', href='/admin'), ']'),
                  )
    return html
