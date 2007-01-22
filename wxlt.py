import wx

class Frame( wx.Frame ):
	"Frame class that displays an image."

	def __init__( self, image, parent=None, id=-1, pos = wx.DefaultPosition, title="Hello, LT!" ):
		bmp = image.ConvertToBitmap()
		size = bmp.GetWidth(), bmp.GetHeight()
		wx.Frame.__init__( self, parent, id, title, pos, size )
		#self.bmp = wx.StaticBitmap( parent = self, bitmap = bmp )
		self.panel = wx.Panel( self, -1 )
		self.button = wx.Button( self.panel, -1, "button", pos = ( 20, 20 ) )
		self.incr_button_name( )
		self.button.Bind( wx.EVT_BUTTON, self.incr_button_name )

	def incr_button_name( self, None ):
		self.number = getattr( self, 'number', 0 )
		self.button.label = 'button %d' % self.number

import os
image_path = os.path.join( r'\\merciless\home\jaraco\my documents', 'projects', 'experimental', 'screen.png' )

class App( wx.App ):
	"Application class"

	def OnInit( self ):
		image = wx.Image( image_path )
		self.frame = Frame( image )
		self.frame.Show()
		self.SetTopWindow( self.frame )
		return True

if __name__ == '__main__':
	app = App()
	app.MainLoop()

