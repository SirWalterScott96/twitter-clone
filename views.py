from flask import render_template, redirect, url_for, request, abort
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import uuid
import os
from datetime import datetime

from app import app, db
from forms import LoginForm, TweetForm, RegisterForm
from models import Tweet, User


@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            return render_template('index.html', form=form, message='Login Failed!')

        if check_password_hash(user.password, form.password.data):
            login_user(user)

            return redirect(url_for('profile'))

        return render_template('index.html', form=form, message='Login Failed!')

    return render_template('index.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile', defaults={'username': None})
@app.route('/profile/<username>')
def profile(username):

    if username:
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)
    else:
        user = current_user

    followed_by = user.followed_by.all()

    return render_template('profile.html', user=user, followed_by=followed_by)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user_to_follow = User.query.filter_by(username=username).first()

    current_user.following.append(user_to_follow)

    db.session.commit()

    return redirect(url_for('profile'))


@app.route('/timeline', defaults={'username': None}, methods=['GET', 'POST'])
@app.route('/timeline/<username>', methods=['GET', 'POST'])
@login_required
def timeline(username):
    form = TweetForm()

    if username:
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)
    else:
        user = current_user
    tweets = Tweet.query.filter_by(user_id=current_user.id).order_by(Tweet.date_created.desc()).all()
    current_time = datetime.now()

    return render_template('timeline.html', form=form, tweets=tweets, current_time=current_time, user=user)


@app.route('/post_tweet', methods=['GET', 'POST'])
@login_required
def post_tweet():
    form = TweetForm()
    if form.validate():
        tweet = Tweet(text=form.text.data,
                      user_id=current_user.id,
                      date_created=datetime.now())
        db.session.add(tweet)
        db.session.commit()
    return redirect(url_for('timeline'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(name=form.name.data,
                    username=form.username.data,
                    password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
                    join_date=datetime.now())

        image = form.image.data
        if image:
            image_name = str(uuid.uuid1()) + '_' + secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
            image.save(image_path)
            user.image = os.path.join('imgs', image_name)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('profile'))

    return render_template('register.html', form=form)