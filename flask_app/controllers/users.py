from flask_app import app
from flask import render_template, redirect, session, request, flash
from flask_app.models.user import User
from flask_app.models.tvshow import Show
from flask_bcrypt import Bcrypt      
import math  
import random
import smtplib
bcrypt = Bcrypt(app)

from .env import ADMINEMAIL
from .env import PASSWORD


@app.route('/')
def controller():
    if 'user_id' not in session:
        return redirect('/logout')
    return redirect('/verify/email')
    
@app.route('/register')
def registerPage():
    # this checks if user is logged in
    if 'user_id' in session:
        return redirect('/')
    # if its not, do the following
    return render_template('register.html')

@app.route('/login')
def loginPage():
    # this checks if user is logged in
    if 'user_id' in session:
        return redirect('/')
    # if its not, do the following
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def loginUser():
     # this checks if user is logged in
    if 'user_id' in session:
        return redirect('/')
    
    # if its not, do the following
    user = User.get_user_by_email(request.form)
    if not user:
        flash('This user doesnt exists! Check your email', 'emailLogin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        # if we get False after checking the password
        flash("Invalid password!", 'passwordLogin')
        return redirect(request.referrer)
    session['user_id']= user['id']
    return redirect('/')

@app.route('/register', methods = ['POST'])
def registerUser():
     # this checks if user is logged in
    if 'user_id' in session:
        return redirect('/')
    # if its not, do the following
    if not User.validate_user(request.form):
        return redirect(request.referrer)
    user = User.get_user_by_email(request.form)
    if user:
        flash('This user already exists! Try another email', 'emailRegister')
        return redirect(request.referrer)
    string = '0123456789ABCDEFGHIJKELNOPKQSTUV'
    vCode = ""
    length = len(string)
    for i in range(4) :
        vCode += string[math.floor(random.random() * length)]
    verificationCode = vCode

    data = {
        'username': request.form['username'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password']),
        'verificationCode': verificationCode
    }
    user_id = User.create(data)


    LOGIN = ADMINEMAIL
    TOADDRS  = request.form['email']
    SENDER = ADMINEMAIL
    SUBJECT = 'Verify Your Email'
    msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
        % ((SENDER), "".join(TOADDRS), SUBJECT) )
    msg += f'Use this verification code to activate your account: {verificationCode}'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.login(LOGIN, PASSWORD)
    server.sendmail(SENDER, TOADDRS, msg)
    server.quit()

    
    session['user_id'] = user_id

    return redirect('/')

@app.route('/dashboard')
def dashboardPage():
    if 'user_id' not in session:
        return redirect('/')
    shows = Show.getAlltvshows()
    data = {
        'id': session['user_id']
    }
    loggedUser = User.get_user_by_id(data)
    if loggedUser['isVerified'] != 1:
        return redirect('/')
    return render_template('dashboard.html', shows=shows, loggedUser=loggedUser)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/')
    data ={
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    if user['isVerified'] != 1:
        return redirect('/')
    shows = Show.get_logged_tvshows(data)
    if user:
        return render_template('profile.html', loggedUser=user, shows=shows)
    return redirect('/')



@app.route('/verify/email')
def verifyEmail():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    if user['isVerified'] == 1:
        return redirect('/dashboard')
    return render_template('verifyEmail.html', loggedUser = user)

@app.route('/activate/account', methods=['POST'])
def activateAccount():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    if user['isVerified'] == 1:
        return redirect('/dashboard')
    
    if not request.form['value1'] or not request.form['value2'] or not request.form['value3'] or not request.form['value4'] :
        flash('Verification Code is required', 'wrongCode')
        return redirect(request.referrer)
    
    totalVerificationCode = request.form['value1']+request.form['value2']+request.form['value3']+request.form['value4']
    
    if totalVerificationCode != user['verificationCode']:
        
        string = '0123456789'
        vCode = ""
        length = len(string)
        for i in range(4) :
            vCode += string[math.floor(random.random() * length)]
        verificationCode = vCode
        dataUpdate = {
            'verificationCode': verificationCode,
            'id': session['user_id']
        }
        User.updateVerificationCode(dataUpdate)
        LOGIN = ADMINEMAIL
        TOADDRS  = user['email']
        SENDER = ADMINEMAIL
        SUBJECT = 'Verify Your Email'
        msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
            % ((SENDER), "".join(TOADDRS), SUBJECT) )
        msg += f'Use this verification code to activate your account: {verificationCode}'
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.login(LOGIN, PASSWORD)
        server.sendmail(SENDER, TOADDRS, msg)
        server.quit()
        


        flash('Verification Code is wrong. We just sent you a new one', 'wrongCode')
        return redirect(request.referrer)
    
    User.activateAccount(data)
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')