import cherrypy

def loadUserByUsername(login):
	ulist=[("user1","pass1"),("user2","pass2")]
	for u,p in ulist:
		if u==login:
			return (u,p)

def checkLoginAndPassword(login, password):
	user = loadUserByUsername(login)
	if user==None:
		return u'Wrong login/password'

class Root:
	_cp_config = {
		'tools.sessions.on': True,
		'tools.session_auth.on': True,
		'tools.session_auth.check_username_and_password': checkLoginAndPassword,
		'tools.session_auth.on_check': loadUserByUsername,
	}

	@cherrypy.expose
	def index(self):
		return " Hello, you passed auth"

cherrypy.quickstart(Root())