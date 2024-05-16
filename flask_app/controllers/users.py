from flask_app import app
from flask import render_template, redirect, session, request, flash
from flask_app.models.user import User
from flask_app.models.team import Team
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)

@app.route('/')
def controller():
    if 'user_id' not in session:
        return redirect('/logout')
    return redirect('/dashboard')
    
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
    data = {
        'username': request.form['username'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password']),
    }
    user_id = User.create(data)
    session['user_id'] = user_id

    return redirect('/')

@app.route('/dashboard')
def dashboardPage():
    if 'user_id' not in session:
        return redirect('/')
    teams = Team.getAllTeams()
    data = {
        'id': session['user_id']
    }
    loggedUser = User.get_user_by_id(data)
    return render_template('dashboard.html', teams=teams, loggedUser=loggedUser)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/')
    data ={
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    teams = Team.get_logged_teams(data)
    if user:
        return render_template('profile.html', loggedUser=user, teams=teams)
    return redirect('/')



# @app.route('/edit/user')
# def editProfile():
#     if 'user_id' not in session:
#         return redirect('/')
#     data ={
#         'id': session['user_id']
#     }
#     user = User.get_user_by_id(data)
#     return render_template('editProfile.html', user=user)

# @app.route('/update/user', methods = ['POST'])
# def updateUser():
#     if 'user_id' not in session:
#         return redirect('/')
#     data = {
#         'id': session['user_id'],
#         'username': request.form['username'],
#         'email': request.form['email']
#     }
#     User.update_user(data)
#     return redirect('/dashboard')

@app.route('/delete')
def delete():
    if 'user_id' not in session:
        return redirect('/')
    data ={
        'id': session['user_id']
    }
    User.delete_users_team(data)
    User.delete_user(data)
    return redirect('/logout')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')