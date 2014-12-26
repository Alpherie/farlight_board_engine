#this is the file for the functions, shared beatween many modules

import time

import tornado.escape

import lxml
from lxml.html import builder as E
from lxml.builder import E as EE

import initiate
import config as cf

def posting(requesth, board): #working with posted form content
    action = requesth.get_body_argument('action')
    if action == 'post':#here we act when adding a new post
        post_content = {} #will be send as kwargs to database query
        
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
        if len(text) > cf.post_len:
            return 'Too long text' #should add html escaping
        elif text == '':
            return 'No text were entered'
        post_content['text'] = text
        
        #op referer
        op = requesth.get_body_argument('op')
        try: #prepairing op referer
            op = int(op)
        except ValueError:
            return 'Incorrect op referer'
        if op != 0:
            if op not in initiate.board_cache[board][6]:
                return 'Thread does not exist'
            post_content['op_post'] = op

        #need to add file management
        
        #adding ip
        post_content['ip'] = requesth.request.remote_ip
        print(requesth.request.remote_ip) #for testing
        
        #adding timestamp
        post_content['post_time'] = int(time.time())
        
        #preparing the post for database
            #posting should be done as a subfunction of the BOARD class
        new_post = initiate.board_cache[board][4](**post_content)
            #posting to the database
        initiate.sess.add(new_post)
        initiate.sess.commit()
            #adding the post to the cache
        if op == 0:
            initiate.board_cache[board][5].reverse() #reversing list for faster appending
            initiate.board_cache[board][5].append(new_post.id) 
            initiate.board_cache[board][5].reverse()
            initiate.board_cache[board][6][new_post.id] = []
        else:
            initiate.board_cache[board][5].remove(op) #not sure, if we should remove it from reversed list or not reversed
            initiate.board_cache[board][5].reverse() #reversing list for faster appending
            initiate.board_cache[board][5].append(op)
            initiate.board_cache[board][5].reverse()
            initiate.board_cache[board][6][op].append(new_post.id)
        return 'Luckily posted'
    else:
        return 'not implemented yet'
    #

def get_posts_code_by_num(requesth, received_objects): #function for returning the posts code for a list of posts ids
    return_object = {} #this is what we would return
    board = received_objects['board']
    if board not in initiate.board_cache: #all of this should be redone, it is fucking not good code
        return 'error'
    in_list = set()
    for postid in received_objects['ids']:
        if type(postid) is not int:
            return 'Incorrect post ids'
        in_list.add(postid)#probably should check, if adding an already existing in set element does not cause an error
    in_list2 = list(in_list)#converting to list for _in function
    if len(in_list2) != 0:
        database_responce = initiate.sess.query(initiate.board_cache[board][4]).filter(initiate.board_cache[board][4].id.in_(in_list2)).all()
        for row in database_responce:
            return_object[row.id] = row.to_dict()
            in_list.remove(row.id)
        for postid in in_list: #here we add all the posts that does not exist
            return_object[row.id] = None
    return tornado.escape.json_encode(return_object)
