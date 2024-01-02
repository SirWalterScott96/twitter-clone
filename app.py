from flask import Flask, render_template, redirect, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from flask_login import LoginManager, UserMixin, login_required, current_user, logout_user, login_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'lapo4kado4ka'
app.config["UPLOAD_EXTENSIONS"] = ["jpg", "png"]
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath('static'), 'imgs')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100))
    image = db.Column(db.String(250))
    password = db.Column(db.String(250))
    join_date = db.Column(db.DateTime)
    tweet = db.relationship('Tweet', backref='user', lazy=True)


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(140))
    date_created = db.Column(db.DateTime)


class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('A full name is required.'),
                                                Length(max=100, message='Your name cant be more than 100 characters')])
    username = StringField('Username', validators=[InputRequired('Username is required.'),
                                                   Length(max=100,
                                                          message='Your username should have below 100 characters')])

    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    image = FileField(validators=[FileAllowed(app.config["UPLOAD_EXTENSIONS"], 'only images allowed')])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Username is required.')])
    password = PasswordField('Password', validators=[InputRequired('Password is required.')])
    remember = BooleanField('Remember me')


class TweetForm(FlaskForm):
    text = TextAreaField('Text', validators=[InputRequired('You should write some text!')])
    submit = SubmitField('Post')
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


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/timeline', methods=['GET', 'POST'])
@login_required
def timeline():
    form = TweetForm()
    tweets = Tweet.query.filter_by(user_id=current_user.id).order_by(Tweet.date_created.desc()).all()
    return render_template('timeline.html', form=form, tweets=tweets)


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
            user.image = os.path.join('static', 'imgs')

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
