from django.shortcuts import render
from django.http import HttpResponse
import imapclient
import pyzmail

class IMAP_server:
    def __init__(self, imap: str, smtp: str, port: int):
        self.imap = imap
        self.smtp = smtp
        self.port = port

servers = dict([("Gmail", IMAP_server("imap.gmail.com", "smtp.gmail.com", 587)),
                ("Outlook", IMAP_server("imap-mail.outlook.com", "smtp-mail.outlook.com", 587)),
                ("Yahoo", IMAP_server("imap.mail.yahoo.com", "smtp.mail.yahoo.com", 587)),
                ("Comcast", IMAP_server("imap.comcast.net", "smtp.comcast.net", 587)),
                ("Verizon", IMAP_server("incoming.verizon.net", "smtp.verizon.net", 465))])

def IMAPlogin(username: str, password: str, server: str) -> imapclient:
    imapObj = imapclient.IMAPClient(server, ssl=True)
    try:
        imapObj.login(username, password)
        
    except:
        return None
    return imapObj

def mailRender(server: imapclient, mailID: int) -> str:
    server.select_folder('INBOX', readonly=True)
    rawMessage = server.fetch([mailID], ['BODY[]', 'FLAGS'])
    email = pyzmail.PyzMessage.factory(rawMessage[mailID][b'BODY[]'])
    return email.html_part.get_payload().decode(email.html_part.charset)

# Create your views here.
def login(request):
    return render(request, 'login/login.html')

def authentication(request):
    email = request.GET.get('emailaddress')
    psswd = request.GET.get('password')
    msp = request.GET.get('msp')
    chosenMSP = servers[msp]
    server = IMAPlogin(email, psswd, chosenMSP.imap)
    if not server:    
        return render(request, 'login/authentication.html')
    email = mailRender(server, 9)
    server.logout()
    return HttpResponse(email)
