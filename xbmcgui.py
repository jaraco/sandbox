import wx

APP = None
PARENT = None
EMULATE_CONTROLLER = True

class XBoxController( wx.Frame ):
	# buttons defines name, action number, and button position
	buttons = (
		('Left', 1, (100, 100) ),
		('Right', 2, (150, 100) ),
		('Up', 3, (125, 70) ),
		('Down', 4, (125, 130) ),
		('X', 18, (210, 50) ),
		('Y', 34, (245, 35) ),
		('A', 7, (225, 90) ),
		('B', 9, (265, 70) ),
		('White', 0, (210, 130) ),
		('Black', 0, (270, 110) ),
		('Back', 10, (5, 90) ),
		('Start', 13, (5, 120) ),
		('L Trigger', 5, (5, 5) ),
		('R Trigger', 6, (290, 5) ),
		)
	
	def __init__( self, *args ):
		wx.Frame.__init__( self, *args )
		self.panel = wx.Panel( self, size = ( None, 190 ) )
		filename = os.path.join( os.path.dirname( __file__ ), 'controller.gif' )
		image = wx.Image( filename )
		self.controller_bitmap = wx.StaticBitmap( bg, image )
		self.draw_buttons()

	def draw_buttons( self ):
		for name, action, pos in self.buttons:
			btn = wx.Button( self, label = name, pos = pos )
			btn.action = action
			handler = lambda event: self.OnButton( event, btn )
			self.Bind( wx.EVT_BUTTON, handler, btn )

	def OnButton( self, event, button ):
		print 'button', button.GetName(), 'was pressed'
		self.onAction( button.action )
		
class Window( wx.Frame ):
	def __init__( self ):
		global APP, PARENT, EMULATE_CONTROLLER
		if not APP:
			app = wx.PySimpleApp()
		wx.Frame.__init__( self, parent = PARENT, size = ( 720, 480 ) )
		self.panel = wx.Panel( self )
		self.panel.SetBackgroundColor( 'black' )

		if EMULATE_CONTROLLER:
			self.controller = XBoxController( self )

