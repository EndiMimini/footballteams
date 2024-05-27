from flask_app import app
from flask import render_template, redirect, session, request, flash, jsonify
from flask_app.models.tvshow import Show
from flask_app.models.user import User
import os
from datetime import datetime
from .env import UPLOAD_FOLDER
from .env import ALLOWED_EXTENSIONS
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from werkzeug.utils import secure_filename

# Check if the format is right 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add/show')
def addshow():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    loggedUser = User.get_user_by_id(data)
    if loggedUser['isVerified'] != 1:
        return redirect('/')
    return render_template('addShow.html', loggedUser=loggedUser)


@app.route('/create/show', methods = ['POST'])
def createshow():
    if 'user_id' not in session:
        return redirect('/')
    dataL = {
        'id': session['user_id']
    }
    user = User.get_user_by_id(dataL)
    if user['isVerified'] != 1:
        return redirect('/')
    if not Show.validate_show(request.form):
        return redirect(request.referrer)
    
    if not request.files['image']:
        flash('Show image is required!', 'image')
        return redirect(request.referrer)
   
    image = request.files['image']
    if not allowed_file(image.filename):
        flash('Image should be in png, jpg, jpeg format!', 'image')
        return redirect(request.referrer)
    
    if image and allowed_file(image.filename):
        filename1 = secure_filename(image.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename1
        filename1 = time
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))

    data = {
        'name': request.form['name'],
        'releaseDate': request.form['releaseDate'],
        'network': request.form['network'],
        'description': request.form['description'],
        'image': filename1,
        'user_id': session['user_id']
    }
    Show.create(data)
    return redirect('/')


@app.route('/show/<int:id>')
def viewshow(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'tvshow_id': id,
        'id': session['user_id']
    }
    show = Show.get_show_by_id(data)
    loggedUser = User.get_user_by_id(data)
    if loggedUser['isVerified'] != 1:
        return redirect('/')
    usersWhoLiked = Show.get_likers(data)
    likersDetails = Show.get_likers_info(data)
    return render_template('show.html', show=show, loggedUser=loggedUser, usersWhoLiked=usersWhoLiked, likersDetails=likersDetails)


@app.route('/edit/show/<int:id>')
def editshow(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'tvshow_id': id,
        'id': session['user_id']
    }
    show = Show.get_show_by_id(data)
    if not show:
        return redirect('/')
    loggedUser = User.get_user_by_id(data)
    if loggedUser['isVerified'] != 1:
        return redirect('/')
    if show['user_id'] != loggedUser['id']:
        return redirect('/')

    return render_template('editShow.html', show=show, loggedUser=loggedUser)


@app.route('/update/show/<int:id>', methods = ['POST'])
def updateshow(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'tvshow_id': id,
        'id': session['user_id']
    }
    show = Show.get_show_by_id(data)
    if not show:
        return redirect('/')
    loggedUser = User.get_user_by_id(data)
    if loggedUser['isVerified'] != 1:
        return redirect('/')
    if show['user_id'] != loggedUser['id']:
        return redirect('/')
    
    if len(request.form['releaseDate'])<1 or len(request.form['network'])<1 or len(request.form['description'])<3:
        flash('All fields required', 'allRequired')
        return redirect(request.referrer)
    
    updateData = {
        'name': show['name'],
        'releaseDate': request.form['releaseDate'],
        'network': request.form['network'],
        'description': request.form['description'],
        'id': id
    }
    if not Show.validate_show(updateData):
        return redirect(request.referrer)
    Show.update_show(updateData)
    return redirect('/show/'+ str(id))
    
    

@app.route('/delete/show/<int:id>')
def deleteshow(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'tvshow_id': id,
        'id': session['user_id']
    }
    show = Show.get_show_by_id(data)
    if not show:
        return redirect('/')
    loggedUser = User.get_user_by_id(data)
    if loggedUser['isVerified'] != 1:
        return redirect('/')
    if loggedUser['id'] == show['user_id']:
        Show.delete_all_likes(data)
        Show.delete_show(data)
    return redirect('/')


@app.route('/like/<int:id>')
def addLike(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'tvshow_id': id,
        'id': session['user_id']
    }
    user = User.get_user_by_id(data)
    if user['isVerified'] != 1:
        return redirect('/')
    usersWhoLiked = Show.get_likers(data)
    if session['user_id'] not in usersWhoLiked:
        Show.addLike(data)
        return redirect(request.referrer)
    return redirect(request.referrer)


@app.route('/unlike/<int:id>')
def removeLike(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'tvshow_id': id,
        'id': session['user_id']
    }    
    user = User.get_user_by_id(data)
    if user['isVerified'] != 1:
        return redirect('/')
    Show.removeLike(data)
        
    return redirect(request.referrer)