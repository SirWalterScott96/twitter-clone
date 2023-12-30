from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired, Length
# import flask_script

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'lapo4kado4ka'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    image = db.Column(db.String(250))
    password = db.Column(db.String(250))


class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('A full name is required.'),
                                                Length(max=100, message='Your name cant be more than 100 characters')])
    username = StringField('Username', validators=[InputRequired('Username is required.'),
                                                   Length(max=100, message='Your username should have below 100 characters')])

    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    image = FileField()
    submit = SubmitField('Sumbit')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/timeline')
def timeline():
    return render_template('timeline.html')


@app.route('/register')
def register():
    form = RegisterForm()
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
