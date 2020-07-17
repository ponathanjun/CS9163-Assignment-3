from flask import Flask, render_template, redirect, url_for, request, session
import os
import subprocess
import bleach
from flask_wtf.csrf import CSRFProtect
import bcrypt

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY = os.urandom(32),
        SESSION_COOKIE_HTTPONLY = True,
        SESSION_COOKIE_SAMESITE = 'Strict',
        PERMANENT_SESSION_LIFETIME = 600
    )
    csrf = CSRFProtect(app)
    information = {}
    
    def register_with_user_info(uname, pword, twofa):
        if uname not in information:
            hashed_pword = bcrypt.hashpw(pword.encode('utf8'), bcrypt.gensalt())
            hashed_twofa = bcrypt.hashpw(twofa.encode('utf8'), bcrypt.gensalt())
            information[uname] = [hashed_pword, hashed_twofa]
            return 0
        else:
            return 1
    def login_with_user_info(uname, pword, twofa):
        if uname not in information:
            return 2
        if bcrypt.checkpw(pword.encode('utf8'), information[uname][0]) == False:
            return 2
        if bcrypt.checkpw(twofa.encode('utf8'), information[uname][1]) == False:
            return 1
        return 0

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods = ['GET', 'POST'])
    def register():
        success = ""
        if 'username' not in session:
            if request.method == 'POST':
                uname = bleach.clean(request.form['uname'])
                pword = bleach.clean(request.form['pword'])
                twofa = bleach.clean(request.form['2fa'])
                status = register_with_user_info(uname, pword, twofa)
                if status == 0:
                    success = "Registration Success!"
                else:
                    success = "Registration Failure!"
            return render_template("register.html", id = success)
        else:
            success = "Already logged in!"
            return render_template("register.html", id = success)

    @app.route("/login", methods = ['GET', 'POST'])
    def login():
        result = ""
        if 'username' not in session:
            if request.method == 'POST':
                uname = bleach.clean(request.form['uname'])
                pword = bleach.clean(request.form['pword'])
                twofa = bleach.clean(request.form['2fa'])
                status = login_with_user_info(uname, pword, twofa)
                if status == 2:
                    result = "Incorrect username or password!"
                elif status == 1:
                    result = "Two-factor failure!"
                else:
                    result = "Success!"
                    session.permanent = True
                    session['username'] = uname
            return render_template("login.html", id = result)
        else:
            result = "Already logged in!"
            return render_template("login.html", id = result)

    @app.route("/spell_check", methods = ['GET', 'POST'])
    def spell_check():
        if 'username' in session:
            textout = ""
            misspelled = ""
            if request.method == 'POST':
                textout = bleach.clean(request.form['inputtext'])
                with open("test.txt", "w+") as fo:
                    fo.write(textout)
                misspelled = subprocess.check_output(["./a.out", "test.txt", "wordlist.txt"])
                misspelled = misspelled.decode('utf-8').strip().split('\n')
                misspelled = ", ".join(misspelled)
                fo.close()
                os.remove("test.txt")
            return render_template("spell_check.html", textout = textout, misspelled = misspelled)
        else:
            return redirect(url_for("home"))

    @app.route("/logout")
    def logout():
        if 'username' in session:
            session.pop('username', None)
        return redirect(url_for("home"))

    @app.after_request
    def add_headers(response):
        response.headers['Strict-Transport-Security'] = "max-age=31536000 ; includeSubDomains"
        response.headers['Content-Security-Policy'] = "default-src 'self' ; style-src 'self' 'unsafe-inline'"
        response.headers['Set-Cookie'] = "HTTPOnly ; Secure"
        response.headers['X-FrameOptions'] = "DENY"
        response.headers['X-XSS-Protection'] = "1 ; mode=block"
        response.headers['X-Content-Type-Options'] = "nosniff"
        return response

    return app

if __name__ == "__main__":
    app.create_app()
