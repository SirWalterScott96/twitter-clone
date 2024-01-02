from flask import Flask, render_template, redirect, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'lapo4kado4ka'
app.config["UPLOAD_EXTENSIONS"] = ["jpg", "png"]
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath('static'), 'imgs')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100))
    image = db.Column(db.String(250))
    password = db.Column(db.String(250))


class RegisterForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired('A full name is required.'),
                                                Length(max=100, message='Your name cant be more than 100 characters')])
    username = StringField('Username', validators=[InputRequired('Username is required.'),
                                                   Length(max=100,
                                                          message='Your username should have below 100 characters')])

    password = PasswordField('Password', validators=[InputRequired('A password is required.')])
    image = FileField(validators=[FileAllowed(app.config["UPLOAD_EXTENSIONS"], 'only images allowed')])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/timeline')
def timeline():
    return render_template('timeline.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(name=form.name.data,
                    username=form.username.data,
                    password=generate_password_hash(form.password.data, method='pbkdf2:sha256'))

        image = form.image.data
        if image:
            image_name = str(uuid.uuid1()) + '_' + secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
            image.save(image_path)
            user.image = image_path

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
