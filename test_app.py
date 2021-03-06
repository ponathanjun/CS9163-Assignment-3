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

# Check that query page is working properly
def test_query(app):
    # Check that you can't access page before logging in (should redirect to home page)
    result = app.get('/history/query1', follow_redirects=True)
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

    # Check that you can access your own queries, but not anyone elses
    result = app.get('/history/query2', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="queryid">Query ID: 2</div>' in result.data
    assert b'<div id="username">User Who Submitted: jonathan</div>' in result.data
    assert b'<div id="querytext">Text Submitted: my dawg is kewl.</div>' in result.data
    assert b'<div id="queryresults">Misspelled Words: dawg, kewl</div>' in result.data
    result = app.get('/history/query3', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="queryid">Query ID: 3</div>' in result.data
    assert b'<div id="username">User Who Submitted: jonathan</div>' in result.data
    assert b'<div id="querytext">Text Submitted: second query</div>' in result.data
    assert b'<div id="queryresults">Misspelled Words: </div>' in result.data
    result = app.get('/history/query1', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Showing results for: jonathan' in result.data
    assert b'<div id="queryid">Query ID: 1</div>' not in result.data
    assert b'<div id="username">User Who Submitted: brian</div>' not in result.data
    assert b'<div id="querytext">Text Submitted: test quiery</div>' not in result.data
    assert b'<div id="queryresults">Misspelled Words: quiery</div>' not in result.data

    # Check that admin can access all queries
    app.get('/logout', follow_redirects=True)
    app.post('/login', data = {'uname':"admin", 'pword':"Administrator@1", '2fa':"12345678901"}, follow_redirects=True)
    result = app.get('/history', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<form name="userquery" id="userquery" action="/history" method="POST">' in result.data
    assert b'Showing results for: admin' in result.data
    result = app.get('/history/query2', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="queryid">Query ID: 2</div>' in result.data
    assert b'<div id="username">User Who Submitted: jonathan</div>' in result.data
    assert b'<div id="querytext">Text Submitted: my dawg is kewl.</div>' in result.data
    assert b'<div id="queryresults">Misspelled Words: dawg, kewl</div>' in result.data
    result = app.get('/history/query3', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<div id="queryid">Query ID: 3</div>' in result.data
    assert b'<div id="username">User Who Submitted: jonathan</div>' in result.data
    assert b'<div id="querytext">Text Submitted: second query</div>' in result.data
    assert b'<div id="queryresults">Misspelled Words: </div>' in result.data
    result = app.get('/history/query1', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Showing results for: jonathan' not in result.data
    assert b'<div id="queryid">Query ID: 1</div>' in result.data
    assert b'<div id="username">User Who Submitted: brian</div>' in result.data
    assert b'<div id="querytext">Text Submitted: test quiery</div>' in result.data
    assert b'<div id="queryresults">Misspelled Words: quiery</div>' in result.data

# Check that log page is working properly
def test_login_history(app):
    # Check that you can't access page before logging in (should redirect to home page)
    result = app.get('/login_history', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Home Page' in result.data

    # Check that you can't access page if you're not logged into admin (should redirect to home page)
    # Register and log in
    app.post('/register', data = {'uname':"brian", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)    
    app.post('/login', data = {'uname':"brian", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    result = app.get('/login_history', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Home Page' in result.data
    app.get('/logout', follow_redirects=True)

    # Register another user and log in and out
    app.post('/register', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.post('/login', data = {'uname':"jonathan", 'pword':"password", '2fa':"6316827788"}, follow_redirects=True)
    app.get('/logout', follow_redirects=True)
    
    # Log into admin
    app.post('/login', data = {'uname':"admin", 'pword':"Administrator@1", '2fa':"12345678901"}, follow_redirects=True)
    # Check that log link are in nav bar and home page
    result = app.get('/', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<a  href="/login_history">Logs</a>' in result.data
    assert b'<a style = "color: white" href = "/login_history">LOGS</a>' in result.data
    # Check that page works when logged into admin
    result = app.get('/login_history', follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'Home Page' not in result.data
    assert b'<form name="userid" id="userid" action="/login_history" method="POST">' in result.data
    assert b'Showing results for: admin' not in result.data
    assert b'<ul class="list">' not in result.data
    # Check if you can see logs of another user
    result = app.post('/login_history', data = {'uname':"brian"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<form name="userid" id="userid" action="/login_history" method="POST">' in result.data
    assert b'Showing results for: brian' in result.data
    assert b'<div id="login1_time">Login Time:' in result.data
    assert b'<div id="logout1_time">Logout Time:' in result.data
    # Check that a user's log are in the right place
    assert b'<div id="login2_time">Login Time:' not in result.data
    # Check that logout time N/A. is working
    result = app.post('/login_history', data = {'uname':"admin"}, follow_redirects=True)
    # Check if loaded successfully
    assert result.status_code == 200
    assert b'<form name="userid" id="userid" action="/login_history" method="POST">' in result.data
    assert b'Showing results for: admin' in result.data
    assert b'<div id="login3_time">Login Time:' in result.data
    assert b'<div id="logout3_time">Logout Time: N/A.</div>' in result.data
    
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

    

    

    
    





    
    
