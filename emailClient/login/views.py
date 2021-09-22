from django.shortcuts import render

class IMAP_server:
    def __init__(self, dns: str, port: int):
        self.dns = dns
        self.port = port

servers = dict([("Gmail", IMAP_server("smtp.gmail.com", 587)),
                ("Outlook", IMAP_server("smtp-mail.outlook.com", 587)),
                ("Yahoo", IMAP_server("smtp.mail.yahoo.com", 587)),
                ("Comcast", IMAP_server("smtp.comcast.net", 587)),
                ("Verizon", IMAP_server("smtp.verizon.net", 465))])


# Create your views here.
def login(request):
    return render(request, 'login/login.html')


def authentication(request):
    email = request.GET.get('emailaddress')
    psswd = request.GET.get('password')
    msp = request.GET.get('msp')
    chosenIMAP = servers[msp]
    
    return render(request, 'login/authentication.html')
