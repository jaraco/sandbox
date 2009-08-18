<%@language=Python%>

<html>

<head>
<meta name="GENERATOR" content="Microsoft FrontPage 5.0">
<meta name="ProgId" content="FrontPage.Editor.Document">
<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
<title>Jason's Mail</title>
</head>

<body>

<%
import os, email, re

root = r'\inetpub\mailroot\mailbox\jaraco.com'
username = 'jaraco'
mailbox = 'P3_%(username)s.mbx' % vars()
messageListHeaders = ['From', 'Subject', 'Date']

mailboxpath = os.path.join( root, mailbox )
Response.Write( 'Mailbox path is %(mailboxpath)s<br/>' % vars() )

def isEmailFilename( filename ):
	return re.match( '.*\.eml', filename )
	
def getMailMessage( filename ):
	filepath = os.path.join( mailboxpath, filename )
	file = open( filepath, 'r' )
	msg = email.message_from_file( file )
	file.close()
	return msg

def doHeader( ):
	Response.Write( '<THead>\n\t' )
	for item in messageListHeaders:
		Response.Write( '<TD>%s</TD>' % item )
	Response.Write( '\n</THead>\n' )
	
def doMsg( msg ):
	listItems = map( msg.get, messageListHeaders )
	Response.Write( '<TR>\n\t' )
	for item in listItems:
		Response.Write( '<TD>%s</TD>' % item )
	Response.Write( '\n</TR>\n' )

allfiles = os.listdir( mailboxpath )
emailfiles = filter( isEmailFilename, allfiles )
messages = map( getMailMessage, emailfiles )
Response.Write( '<Table>\n' )
doHeader()
map( doMsg, messages )
Response.Write( '</Table>' )
%>

</body>

</html>