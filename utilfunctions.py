#this is the file for the functions, shared beatween many modules

import tornado.escape

import initiate
import config as cf

def posting(requesth, board): #working with posted form content
    action = requesth.get_body_argument('action')
    if action == 'post':#here we act when adding a new post
        theme = requesth.get_body_argument('theme')
        if len(theme) > 255:
            return 'Too long theme' #should add html escaping
        text = requesth.get_body_argument('text')
        if len(text) > cf.post_len:
            return 'Too long text' #should add html escaping
        op = requesth.get_body_argument('op')
        #---
        #temporary for testing
        text = '<p>'+tornado.escape.xhtml_escape(text)+'</p>'
        if len(text) > cf.post_len:
            return 'Too long text after escaping'
        #---
        op = int(op)
        #preparing the post for database
        if op == 0:
            new_post = initiate.board_cache[board][4](html_code = text)
        else:
            if op not in initiate.board_cache[board][6]:
                return 'Incorrect op referer'
            new_post = initiate.board_cache[board][4](html_code = text, op_post = op)
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
