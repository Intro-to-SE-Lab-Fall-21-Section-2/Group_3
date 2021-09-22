from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, 'login/login.html')


def authentication(request):
    email = request.GET.get('emailaddress')
    psswd = request.GET.get('password')
    
    return render(request, 'login/authentication.html')
