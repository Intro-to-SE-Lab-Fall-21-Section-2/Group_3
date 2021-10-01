from django.shortcuts import render
from django.http import HttpResponse
import imapclient
import pyzmail
from .models import Email

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

def mailGetter(server: imapclient):
    server.select_folder('INBOX', readonly=True)
    return server.search(['ALL'])

def mailRender(server: imapclient, mailID: int):
    rawMessage = server.fetch([mailID], ['BODY[]', 'FLAGS'])
    return pyzmail.PyzMessage.factory(rawMessage[mailID][b'BODY[]'])

# Create your views here.
def login(request):
    return render(request, 'login/login.html')

def authentication(request):
    email = request.GET.get('emailaddress')
    psswd = request.GET.get('password')
    if not email and not psswd:
        return HttpResponse("You must enter an Email and a Password")
    if not email:
        return HttpResponse("You must enter an Email")
    if not psswd:
        return HttpResponse("You must enter an Password")
    msp = request.GET.get('msp')
    chosenMSP = servers[msp]
    server = IMAPlogin(email, psswd, chosenMSP.imap)
    if not server:    
        return render(request, 'login/authentication.html')
    emailIDList = mailGetter(server)
    print(emailIDList)
    for emailNum in emailIDList:
        email = mailRender(server, emailNum)
        html = email.html_part.get_payload().decode(email.html_part.charset)
        sentBy = email.get_addresses('from')[0][-1]
        sub = email.get_subject()
        mail = Email()
        mail.mailID = emailNum
        mail.sender = sentBy
        mail.subject = sub
        mail.body = html
        mail.save()
        content = Email.objects.all() 

        
    server.logout()
    return render(request, 'login/pulledMail.html', {'emails':content})

def view(request, ID):
    message = Email.objects.get(mailID=ID)
    return HttpResponse(message.body)
