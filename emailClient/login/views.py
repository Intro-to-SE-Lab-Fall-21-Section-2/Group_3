from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import imapclient
import pyzmail
import smtplib
from os.path import basename
from django.core.files.base import ContentFile
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from .models import Email, FeedFile, Draft

# hold the details for logging into a msp
class IMAP_server:
    def __init__(self, imap: str, smtp: str, port: int):
        self.imap = imap
        self.smtp = smtp
        self.port = port

#dictionary relating msp to related servers
servers = dict([("Gmail", IMAP_server("imap.gmail.com", "smtp.gmail.com", 587)),
                ("Outlook", IMAP_server("imap-mail.outlook.com", "smtp-mail.outlook.com", 587)),
                ("Yahoo", IMAP_server("imap.mail.yahoo.com", "smtp.mail.yahoo.com", 993)),
                ("Comcast", IMAP_server("imap.comcast.net", "smtp.comcast.net", 993)),
                ("ATT", IMAP_server("imap.att.yahoo.com", "smtp.mail.att.net", 993))])


#login to an imap server
def IMAPlogin(username: str, password: str, server: str) -> imapclient:
    imapObj = imapclient.IMAPClient(server, ssl=True)
    try:
        imapObj.login(username, password)
        
    except:
        return None
    return imapObj

#return valid mail ids for certain account
def mailGetter(server: imapclient):
    server.select_folder('INBOX', readonly=True)
    return server.search(['ALL'])

#fetch a specific email from imap server
def mailRender(server: imapclient, mailID: int):
    rawMessage = server.fetch([mailID], ['BODY[]', 'FLAGS'])
    return pyzmail.PyzMessage.factory(rawMessage[mailID][b'BODY[]'])

#Handle logging in when user submits login form
def authentication(request):
    if request.method == 'POST':
        email = request.POST.get('emailaddress')
        psswd = request.POST.get('password')
        if not email and not psswd:
            return render(request, 'login/authentication.html')
        if not email:
            return render(request, 'login/authentication.html')
        if not psswd:
            return render(request, 'login/authentication.html')
        msp = request.POST.get('msp')

        #store cookie for user, will need info later 
        request.session['username'] = email
        request.session['password'] = psswd
        request.session['msp'] = msp
        chosenMSP = servers[msp]
        server = IMAPlogin(email, psswd, chosenMSP.imap)
        if not server:    
            #if IMAP login fails, return a login failed message
            return render(request, 'login/authentication.html')
        emailIDList = mailGetter(server)
        #loop through all emails fetched
        for emailNum in emailIDList:
            checkForMail = Email.objects.filter(recipient=email).filter(mailNum=emailNum)
            if not checkForMail:
                parsedMessage = mailRender(server, emailNum)               
                
                try:
                    bodyContent = parsedMessage.html_part.get_payload().decode(parsedMessage.html_part.charset)
                except:
                    bodyContent = parsedMessage.text_part.get_payload().decode(parsedMessage.text_part.charset)
                #set field contents
                mail = Email()
                mail.mailNum = emailNum
                mail.sender = parsedMessage.get_addresses('from')[0][-1]
                mail.recipient = email
                mail.subject = parsedMessage.get_subject()
                mail.body = bodyContent
                #store message in DB
                mail.save()
                counter = 0
                #parse files and store them in MEDIA_ROOT
                for mailpart in parsedMessage.mailparts:
                    feed = FeedFile()
                    if mailpart.filename:
                        fileContent = ContentFile(mailpart.get_payload())
                        feed.file.save(mailpart.filename, fileContent)
                        mail.files.add(feed) 
                        counter = counter + 1
                mail.fileCount = counter
                mail.save()                         
        
        content = Email.objects.filter(recipient=email).filter(trashFolder=False)
      
        server.logout()
        return render(request, 'login/pulledMail.html', {'emails':content})
    else:
        #return login page if not POST
        return render(request, 'login/login.html')

#show the html version of body
def view(request, ID): 
    #check if user is logged in, else return to login page
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')   
    message = Email.objects.filter(recipient=request.session['username']).get(mailNum=ID)
    return HttpResponse(message.body)

#compose and transmit mail
def send(request):
    #check if user is logged in, else return to login page
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')

    if request.method == 'POST':
        #set fields to construct email
        if request.POST.get('action') == "Send":
            recipient = request.POST.get('recipient')
            splitRecipients = recipient.split(sep = "; ")
            subject = request.POST.get('subject')
            body = request.POST.get('Body')
            mspInfo: IMAP_server = servers[request.session['msp']]
            msg = MIMEMultipart()
            msg['from'] = request.session['username']
            msg['to'] = splitRecipients[0]
            msg['subject'] = subject
            body = MIMEText(body, 'plain')
            msg.attach(body)
            
            #If there are files attached, attach them to MIME message
            if request.FILES:
                uploadedFiles = request.FILES.getlist('Attach')
                print(uploadedFiles)
                for uploadedFile in uploadedFiles:
                    fs = FileSystemStorage()
                    fs.save(uploadedFile.name, uploadedFile)
                    filename = fs.base_location + uploadedFile.name
                    with open(filename, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload((f).read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(basename(uploadedFile.name)))                
                        msg.attach(part) 
                        fs.delete(uploadedFile.name)             
                    
                #connect to SMTP server and transmit the message
            try:
                smtpConnection = smtplib.SMTP(mspInfo.smtp, mspInfo.port)
                smtpConnection.ehlo()
                smtpConnection.starttls()
                smtpConnection.login(request.session['username'], request.session['password'])
                smtpConnection.send_message(msg, from_addr=request.session['username'], to_addrs=splitRecipients)
                smtpConnection.close()  
            except:
                return render(request, 'login/compose.html') 
        if request.POST.get('action') == "Save Draft":
            recipient = request.POST.get('recipient')
            subjectField = request.POST.get('subject')
            bodyField = request.POST.get('Body')
            draft = Draft()
            draft.recipients = recipient
            draft.subject = subjectField
            draft.body = bodyField
            draft.user = request.session['username']
            draft.save()

    return render(request, 'login/compose.html')

#forward email to list of clients 
def forward(request, ID):
    #check if user is logged in, else return to login page
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')

    if request.method == 'POST':
        message = Email.objects.filter(recipient=request.session['username']).get(mailNum=ID)
        recipient = request.POST.get('recipient')
        splitRecipients = recipient.split(sep = "; ")
        subject = message.subject
        body = message.body
        mspInfo: IMAP_server = servers[request.session['msp']]
        msg = MIMEMultipart()
        msg['from'] = request.session['username']
        msg['to'] = splitRecipients[0]
        msg['subject'] = subject
        body = MIMEText(body, 'plain')
        msg.attach(body)
        attachments = message.files.all()
        for feed in attachments:
            with open(feed.file.path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload((f).read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(basename(feed.file.name)))                
                    msg.attach(part) 
        #connect to SMTP server and transmit the message
        try:
            smtpConnection = smtplib.SMTP(mspInfo.smtp, mspInfo.port)
            smtpConnection.ehlo()
            smtpConnection.starttls()
            smtpConnection.login(request.session['username'], request.session['password'])
            smtpConnection.send_message(msg, from_addr=request.session['username'], to_addrs=splitRecipients)
            smtpConnection.close()
        except:
            return render(request, 'login/forward.html')

    return render(request, 'login/forward.html')
#check the attachments for email
def attach(request, ID):
    #check if user is logged in, else return to login page
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')
    message = Email.objects.filter(recipient=request.session['username']).get(mailNum=ID)
    feedFiles = message.files.all()
    paths = []
    for feed in feedFiles:
        paths.append(feed.file)
    return render(request, 'login/attach.html', {'files':paths})
#clickable link that allows user to download files
def download(request, filename):
    #check if user is logged in, else return to login page
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')
    try:
        fs = FileSystemStorage()
        fullPath = fs.base_location + "files/" + filename
        fd = open(fullPath, 'rb')
    except:
        return HttpResponse("Invalid download file")
    
    mime_type, _ = mimetypes.guess_type(fullPath) 
    response = HttpResponse(fd, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

#search in sender, subject, and body for string
def filter(request):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')
    filterStr = request.GET.get('filter')
    contentSender = Email.objects.filter(recipient=request.session['username']).filter(sender__contains=filterStr)
    contentSubject = Email.objects.filter(recipient=request.session['username']).filter(subject__contains=filterStr)
    contentBody = Email.objects.filter(recipient=request.session['username']).filter(body__contains=filterStr)
    content = contentSender | contentSubject | contentBody
    request.path = "/"
    return render(request, 'login/pulledMail.html', {'emails':content})

#logout by deleting cookie session for user
def logout(request):
    
    try:
        del request.session['username']
        del request.session['password']
        del request.session['msp']
    except:
        pass
    return render(request, 'login/logout.html')


#load the trash folder
def trash(request):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')
    
    request.path = "/"
    
    content = Email.objects.filter(recipient=request.session['username']).filter(trashFolder=True)
    return render(request, 'login/trash.html', {'emails':content})

def moveTrash(request, ID):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')
    
    request.path = "/"
    try:
        message = Email.objects.filter(recipient=request.session['username']).get(mailNum=ID)
        message.trashFolder = True
        message.save()
    except:
        pass

    content = Email.objects.filter(recipient=request.session['username']).filter(trashFolder=False)
    return render(request, 'login/pulledMail.html', {'emails':content})

def fromTrash(request, ID):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')

    request.path = "/"
    try:
        message = Email.objects.filter(recipient=request.session['username']).get(mailNum=ID)
        message.trashFolder = False
        message.save()
    except:
        pass

    content = Email.objects.filter(recipient=request.session['username']).filter(trashFolder=True)
    return render(request, 'login/trash.html', {'emails':content})

def delete(request, ID):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')
    
    message = Email.objects.filter(recipient=request.session['username']).get(mailNum=ID)
    message.delete()
    content = Email.objects.filter(recipient=request.session['username']).filter(trashFolder=True)
    request.path = "/trash/"
    return render(request, 'login/trash.html', {'emails':content})

def inbox(request):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')

    request.path = "/"
    content = Email.objects.filter(recipient=request.session['username']).filter(trashFolder=False)
    return render(request, 'login/pulledMail.html', {'emails':content})

def drafts(request):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')

    drafts = Draft.objects.filter(user=request.session['username'])
    return render(request, 'login/drafts.html', {'drafts':drafts})

def draftCompose(request, ID):
    try:
        request.session['username']
    except:
        return render(request, 'login/login.html')

    request.path = "/"
    draft = Draft.objects.filter(user=request.session['username']).filter(pk=ID)
    return render(request, 'login/draftCompose.html', {'draft':draft})



