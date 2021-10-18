from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import imapclient
import pyzmail
import smtplib
import random
from email import message
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


def authentication(request):
    if request.method == 'POST':
        email = request.POST.get('emailaddress')
        psswd = request.POST.get('password')
        if not email and not psswd:
            return HttpResponse("You must enter an Email and a Password")
        if not email:
            return HttpResponse("You must enter an Email")
        if not psswd:
            return HttpResponse("You must enter an Password")
        msp = request.POST.get('msp')
        
        request.session['username'] = email
        request.session['password'] = psswd
        request.session['msp'] = msp
        chosenMSP = servers[msp]
        server = IMAPlogin(email, psswd, chosenMSP.imap)
        if not server:    
            return render(request, 'login/authentication.html')
        emailIDList = mailGetter(server)
        print(emailIDList)
        for emailNum in emailIDList:
            checkForMail = Email.objects.filter(recipient=email).filter(mailNum=emailNum)
            if not checkForMail:
                parsedMessage = mailRender(server, emailNum)
                mail = Email(mailNum = emailNum,
                       sender = parsedMessage.get_addresses('from')[0][-1],
                       recipient = email,
                       subject = parsedMessage.get_subject(),                        
                       body = parsedMessage.html_part.get_payload().decode(parsedMessage.html_part.charset))
                #store message in DB
                mail.save()
        
        content = Email.objects.filter(recipient=email)
      
        server.logout()
        return render(request, 'login/pulledMail.html', {'emails':content})
    else:
        return render(request, 'login/login.html')


def view(request, ID):
    message = Email.objects.filter(recipient=request.session['username']).get(mailNum=ID)
    return HttpResponse(message.body)

def send(request):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('Body')
        if request.FILES:
            uploadedFile = request.FILES['Attatch']
            fs = FileSystemStorage()
            name = fs.save(uploadedFile.name, uploadedFile)       

    print(request.session['username'])
    return render(request, 'login/compose.html')


def logout(request):
    try:
        del request.session['username']
        del request.session['password']
        del request.session['msp']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")
