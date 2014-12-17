#this is the file for the functions, shared beatween many modules

import initiate

def posting(requesth, board): #working with posted form content
    actions = requesth.get_query_arguments('action')
    if actions == ['post']:#here we act when adding a new post
        theme = requesth.get_query_arguments('theme')
        if len(theme) > 255:
            return 'Incorrect theme' #should add html escaping
        text = requesth.get_query_arguments('text')
        if len(text) > :
            return 'Incorrect text' #should add html escaping
        op = requesth.get_query_arguments('op')
        #---
        #temporary for testing
        text = '<p>'+text+'</p>'
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
