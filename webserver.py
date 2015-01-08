import main_page
import initiate
import admin
import ib_thread
import ib_board
#
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(main_page.main_page_gen())
        
class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(admin.admin(self))
    def post(self):
        self.write(admin.admin_post(self))

class BoardHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ib_board.get(self))
    def post(self):
        self.write(ib_board.post(self))

class ThreadHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ib_thread.get(self))
    def post(self):
        self.write(ib_thread.post(self))

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/admin\/login\/?", AdminHandler),
    (r"/admin\/", AdminHandler),
    (r"/admin", AdminHandler),
    (r"/[0-9A-Za-z]+\/res\/[0-9]+\/?", ThreadHandler),
    (r"/[0-9A-Za-z]+\/?[0-9]*", BoardHandler),
    (r"/([0-9A-Za-z]+\/img/[0-9]+\..+)", tornado.web.StaticFileHandler, {"path": "content/"}), #handling pictures
    (r"/(mainscript\.js)", tornado.web.StaticFileHandler, {"path": "js/"}),
    (r"/css/(.+\.css)", tornado.web.StaticFileHandler, {"path": "css/"}),
    (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": ""})
])

if __name__ == "__main__":
    initiate.init()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

