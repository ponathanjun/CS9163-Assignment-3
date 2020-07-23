import pytest
from app import create_app
import os

@pytest.fixture
def app():
    if os.path.exists("spellchecker.db"):
        os.remove("spellchecker.db")
    app = create_app()
    # Turn off CSRF to prevent token issues (security tests not needed according to assignment)
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    return client

# Check if home page is loading properly
def test_home(app):
    # Before login
    result = app.get("/", follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    # Check if links are present
    assert b'<a style = "color: white" href = "/register">REGISTER</a>' in result.data
    assert b'<a style = "color: white" href = "/login">LOGIN</a>' in result.data
    
    # After login
    # Register and login (normal user)
    app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    result = app.get("/", follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    # Check if spell check, history, and logout link are now present
    assert b'<a style = "color: white" href = "/spell_check">SPELL CHECK</a>' in result.data
    assert b'<a style = "color: white" href = "/history">HISTORY</a>' in result.data
    assert b'<a style = "color: white" href = "/logout">LOGOUT</a>' in result.data
    assert b'<a style = "color: white" href = "/login_history">LOGS</a>' not in result.data
    # Logout
    app.get('/logout', follow_redirects=True)

    # Login (admin)
    app.post('/login', data = {'uname':"admin", 'pword':"Administrator@1", '2fa':"12345678901"}, follow_redirects=True)
    result = app.get("/", follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    # Check if log link is now present
    assert b'<a style = "color: white" href = "/login_history">LOGS</a>' in result.data

# Check if register page is working properly
def test_register(app):
    # Loading properly before login
    result = app.get("/register", follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'User Registration' in result.data

    # Check if correct information registration is working
    result = app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    # Check if registration was successful
    assert b'<div id="success" style = "color: black">Registration Success!</div>' in result.data

    # Check if repeated username registration error is working
    result = app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    # Check if registration was unsuccessful
    assert b'<div id="success" style = "color: black">Registration Failure!</div>' in result.data

    # Check if loading properly after login
    app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    result = app.get("/register", follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    # Check if login is recognized
    assert b'<div id="success" style = "color: black">Already logged in!</div>' in result.data

# Check if login page is working properly
def test_login(app):
    # Loading properly before login
    result = app.get("/login", follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Login Page' in result.data

    # Register
    app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)

    # Check if wrong username is working    
    result = app.post('/login', data = {'uname':"jon", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="result" style = "color: black">Incorrect username or password!</div>' in result.data

    # Check if wrong password is working
    result = app.post('/login', data = {'uname':"jonathan", 'pword':"pass", '2fa':"6316827788"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="result" style = "color: black">Incorrect username or password!</div>' in result.data

    # Check if two factor failure is working
    result = app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827777"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="result" style = "color: black">Two-factor failure!</div>' in result.data

    # Check if login is working
    result = app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="result" style = "color: black">Success!</div>' in result.data

    # Check if loading properly after login
    result = app.get('/login', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    # Check if login is recognized
    assert b'<div id="result" style = "color: black">Already logged in!</div>' in result.data

# Check that spell check is working properly
def test_spellcheck(app):
    # Check that you can't access page before logging in (should redirect to home page)
    result = app.get('/spell_check', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Home Page' in result.data

    # Register and login
    app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)

    # Check that you can access page after logging in
    result = app.get('/spell_check', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Add text here!' in result.data

    # Check that spell check is working
    result = app.post('/spell_check', data = {'inputtext':"my dawg is kewl."}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div style = "color: black">Text:</div>' in result.data
    assert b'<div id="textout" style = "color: black">my dawg is kewl.</div>' in result.data
    assert b'<div style = "color: black">Misspelled words:</div>' in result.data
    assert b'<div id="misspelled" style = "color: black">dawg, kewl</div>' in result.data

# Check that history is working properly
def test_history(app):
    # Check that you can't access page before logging in (should redirect to home page)
    result = app.get('/history', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Home Page' in result.data

    # Register, login, and input test query
    app.post('/register', data = {'uname':"brian", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/login', data = {'uname':"brian", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/spell_check', data = {'inputtext':"test quiery"}, follow_redirects=True)
    app.get('/logout', follow_redirects=True)
    app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/spell_check', data = {'inputtext':"my dawg is kewl."}, follow_redirects=True)
    app.post('/spell_check', data = {'inputtext':"second query"}, follow_redirects=True)

    # Check that you can access page after logging in (normal user)
    result = app.get('/history', follow_redirects=True)
    # Check if loaded successfully (only user's query and not others)
    assert result.status_code == 200
    assert b'Showing results for: jonathan' in result.data
    assert b'<div id="numqueries">Total number of queries: 2</div>' in result.data
    assert b'<a style="color: white" href="history/query1" id="query1">1</a>' not in result.data
    assert b'<a style="color: white" href="history/query2" id="query2">2</a>' in result.data
    assert b'<a style="color: white" href="history/query3" id="query3">3</a>' in result.data
    app.get('/logout', follow_redirects=True)

    # Check that you can access page after logging in (admin)
    app.post('/login', data = {'uname':"admin", 'pword':"Administrator@1", '2fa':"12345678901"}, follow_redirects=True)
    result = app.get('/history', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<form name="userquery" id="userquery" action="/history" method="POST">' in result.data
    assert b'Showing results for: admin' in result.data
    # Check ability to look at other user queries
    result = app.post('/history', data = {'uname':"brian"}, follow_redirects=True)
    assert b'Showing results for: brian' in result.data
    assert b'<div id="numqueries">Total number of queries: 1</div>' in result.data
    assert b'<a style="color: white" href="history/query1" id="query1">1</a>' in result.data
    result = app.post('/history', data = {'uname':"jonathan"}, follow_redirects=True)
    assert b'Showing results for: jonathan' in result.data
    assert b'<div id="numqueries">Total number of queries: 2</div>' in result.data
    assert b'<a style="color: white" href="history/query2" id="query2">2</a>' in result.data
    assert b'<a style="color: white" href="history/query3" id="query3">3</a>' in result.data
    
# Check that logout is working properly
def test_logout(app):
    # Check that you can't access page before logging in (should redirect to home page)
    result = app.get('/logout', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Home Page' in result.data

    # Register and login
    app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)

    # Check if login is recognized
    result = app.get('/login', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="result" style = "color: black">Already logged in!</div>' in result.data

    # Check if logout works
    app.get('/logout', follow_redirects=True)
    result = app.get('/login', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="result" style = "color: black">Already logged in!</div>' not in result.data

    

    

    
    





    
    
