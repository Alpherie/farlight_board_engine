import main_page
import initiate
import admin
import ib_thread
import ib_board
#
import tornado.ioloop
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):#probably should be redone for security
        return self.get_secure_cookie("user")
#-----------------------------------------------

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(main_page.main_page_gen())

class BoardHandler(BaseHandler):
    def get(self):
        self.write(ib_board.get(self))
    def post(self):
        self.write(ib_board.post(self))

class ThreadHandler(BaseHandler):
    def get(self):
        self.write(ib_thread.get(self))
    def post(self):
        self.write(ib_thread.post(self))

#-----------------------------------------------
class AdminLogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")

class AdminLoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(admin.login_page_gen())
    def post(self):
        self.write(admin.admin_login(self))

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write(admin.admin(self))
    def post(self):
        self.write(admin.admin_post(self))
#-----------------------------------------------

settings = {
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__", #put it into config
    "login_url": "/admin/login",
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/admin\/login\/?", AdminLoginHandler),
    (r"/admin\/logout\/?", AdminLogoutHandler),
    (r"/admin\/?", AdminHandler),
    (r"/[0-9A-Za-z]+\/res\/[0-9]+\/?", ThreadHandler),
    (r"/[0-9A-Za-z]+\/?[0-9]*", BoardHandler),
    (r"/([0-9A-Za-z]+\/img/[0-9]+\..+)", tornado.web.StaticFileHandler, {"path": "content/"}), #handling pictures
    (r"/([0-9A-Za-z]+\/thumbs/s[0-9]+\..+)", tornado.web.StaticFileHandler, {"path": "content/"}), #handling thumbs
    (r"/(mainscript\.js)", tornado.web.StaticFileHandler, {"path": "js/"}),
    (r"/css/(.+\.css)", tornado.web.StaticFileHandler, {"path": "css/"}),
    (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": ""})
], **settings)

if __name__ == "__main__":
    initiate.init()
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

