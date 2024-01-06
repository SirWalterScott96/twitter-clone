from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed

from app import app


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
