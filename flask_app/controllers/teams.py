from flask_app import app
from flask import render_template, redirect, session, request, flash, jsonify
from flask_app.models.team import Team
from flask_app.models.user import User

@app.route('/add/team')
def addTeam():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    loggedUser = User.get_user_by_id(data)
    return render_template('addTeam.html', loggedUser=loggedUser)


@app.route('/create/team', methods = ['POST'])
def createTeam():
    if 'user_id' not in session:
        return redirect('/')
    if not Team.validate_team(request.form):
        return redirect(request.referrer)
    data = {
        'name': request.form['name'],
        'founded': request.form['founded'],
        'league': request.form['league'],
        'homeStadium': request.form['homeStadium'],
        'trophies': request.form['trophies'],
        'user_id': session['user_id']
    }
    Team.create(data)
    return redirect('/')


@app.route('/team/<int:id>')
def viewTeam(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'team_id': id,
        'id': session['user_id']
    }
    team = Team.get_team_by_id(data)
    loggedUser = User.get_user_by_id(data)
    usersWhoLiked = Team.get_likers(data)
    likersDetails = Team.get_likers_info(data)
    return render_template('team.html', team=team, loggedUser=loggedUser, usersWhoLiked=usersWhoLiked, likersDetails=likersDetails)


@app.route('/edit/team/<int:id>')
def editTeam(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'team_id': id,
        'id': session['user_id']
    }
    team = Team.get_team_by_id(data)
    if not team:
        return redirect('/')
    loggedUser = User.get_user_by_id(data)
    if team['user_id'] != loggedUser['id']:
        return redirect('/')

    return render_template('editTeam.html', team=team, loggedUser=loggedUser)


@app.route('/update/team/<int:id>', methods = ['POST'])
def updateTeam(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'team_id': id,
        'id': session['user_id']
    }
    team = Team.get_team_by_id(data)
    if not team:
        return redirect('/')
    loggedUser = User.get_user_by_id(data)
    if team['user_id'] != loggedUser['id']:
        return redirect('/')
    
    if len(request.form['founded'])<1 or len(request.form['league'])<1 or len(request.form['homeStadium'])<1 or len(request.form['trophies'])<1 or len(request.form['nrOfPlayers'])<1:
        flash('All fields required', 'allRequired')
        return redirect(request.referrer)
    
    updateData = {
        'name': team['name'],
        'founded': request.form['founded'],
        'league': request.form['league'],
        'homeStadium': request.form['homeStadium'],
        'trophies': request.form['trophies'],
        'nrOfPlayers': int(request.form['nrOfPlayers']),
        'id': id
    }
    if not Team.validate_team(updateData):
        return redirect(request.referrer)
    Team.update_team(updateData)
    return redirect('/team/'+ str(id))
    
    

@app.route('/delete/team/<int:id>')
def deleteTeam(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'team_id': id,
        'id': session['user_id']
    }
    team = Team.get_team_by_id(data)
    if not team:
        return redirect('/')
    loggedUser = User.get_user_by_id(data)
    if loggedUser['id'] == team['user_id']:
        Team.delete_all_likes(data)
        Team.delete_team(data)
    return redirect('/')


@app.route('/like/<int:id>')
def addLike(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'team_id': id,
        'id': session['user_id']
    }
    usersWhoLiked = Team.get_likers(data)
    if session['user_id'] not in usersWhoLiked:
        Team.addLike(data)
        return redirect(request.referrer)
    return redirect(request.referrer)


@app.route('/unlike/<int:id>')
def removeLike(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'team_id': id,
        'id': session['user_id']
    }    
    Team.removeLike(data)
        
    return redirect(request.referrer)