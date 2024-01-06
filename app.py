from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os


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


@app.template_filter('time_since')
def how_long_since(delta):
    seconds = delta.total_seconds()

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days > 0:
        return '{}d'.format(int(days))
    elif hours > 0:
        return '{}h'.format(int(hours))
    elif minutes > 0:
        return '{}m'.format(int(minutes))
    else:
        return 'Just now'


from views import *


if __name__ == '__main__':
    app.run(debug=True)
