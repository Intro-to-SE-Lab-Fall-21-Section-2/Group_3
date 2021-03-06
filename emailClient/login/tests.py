from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from .views import *
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
# Create your tests here.



class clientTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()


    def test_IMAPlogin(self):
        username = "nonsense"
        password = "login"
        server = "imap.gmail.com"
        self.assertEqual(IMAPlogin(username, password, server), None)
    
    def test_authentication(self):
        request = self.factory.get('/login')
        response = authentication(request)
        self.assertEqual(response.status_code, 200)

    # make sure anonymous user cannot send mail
    def test_send(self):
        request = self.factory.get('/send')
        response = send(request)
        self.assertEqual(response.status_code, 200)

    # handle smtp connection failure correctly
    def test_sendFail(self):
        request = self.factory.post('/send')
        session = self.client.session
        session['username'] = "userPass"
        session['password'] = "thatFails"
        session['msp'] = "invalidMailserver"
        session.save()
        response = send(request)
        self.assertEqual(response.status_code, 200)

    def test_forward(self):
        request = self.factory.get('/forward/9')
        response = send(request)
        self.assertEqual(response.status_code, 200)

    def test_forwardFail(self):
        request = HttpRequest()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['username'] = "userPass"
        request.session['password'] = "thatFails"
        request.session['msp'] = "invalidMailserver"
        request.session.save()
        response = send(request)
        self.assertEqual(response.status_code, 200)

    #make sure user does not attempt to downlod invalid file
    def test_download(self):
        filename = "fakeFilepath.txt"
        request = self.factory.get('/attach/files/' + filename)
        response = download(request, filename)
        self.assertEqual(response.status_code, 200)

    #check that unauthenticated user cannot crash logout function
    def test_logout(self):
        request = HttpRequest()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request = self.factory.get('/logout')
        request.user = AnonymousUser()
        response = logout(request)
        self.assertEqual(response.status_code, 200)
    
    #test cases for added draft and trash functionality
    
    #make sure request works when no drafts are found in db
    def test_drafts(self):
        request = HttpRequest()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['username'] = "TestAccount"
        response = drafts(request)
        self.assertEqual(response.status_code, 200)

    #make sure invalid db primary key does not cause failure
    def test_draftCompose(self):
        request = HttpRequest()
        id = -10
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['username'] = "TestAccount"
        
        response = draftCompose(request, id)
        self.assertEqual(response.status_code, 200)
    
    #make sure response succeeds with empty query
    def test_trash(self):
        request = HttpRequest()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['username'] = "TestAccount"
        response = trash(request)
        self.assertEqual(response.status_code, 200)
    
    #handle empty queryset properly
    def test_moveTrash(self):
        request = HttpRequest()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['username'] = "TestAccount"
        id = -17
        response = moveTrash(request, id)
        self.assertEqual(response.status_code, 200)

    #handle empty queryset properly
    def test_fromTrash(self):
        request = HttpRequest()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session['username'] = "TestAccount"
        id = -17
        response = fromTrash(request, id)
        self.assertEqual(response.status_code, 200)
