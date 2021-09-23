from django.shortcuts import render

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


# Create your views here.
def login(request):
    return render(request, 'login/login.html')


def authentication(request):
    email = request.GET.get('emailaddress')
    psswd = request.GET.get('password')
    msp = request.GET.get('msp')
    chosenMSP = servers[msp]
    print(chosenMSP.imap)
    
    return render(request, 'login/authentication.html')
