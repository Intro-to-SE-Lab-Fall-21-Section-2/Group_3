from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def inbox(request):
    return render(request, 'inbox/inbox.html')
