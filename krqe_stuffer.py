from urllib2 import urlopen
from ClientForm import ParseResponse

response = urlopen( 'http://www.krqe.com' )
forms = ParseResponse( response, backwards_compat=False )
form = forms[1]
print form
form['optResponse']=['response5']
req = form.click()
while 1:
	urlopen(req).read()
	print 'sent'