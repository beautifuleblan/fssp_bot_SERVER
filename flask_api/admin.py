from flask import Flask, render_template, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
import secrets

app = Flask(__name__)
app_secret_key = secrets.token_hex()
login_manager = LoginManager()

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'



admin = Admin(app, name='admin', template_mode='bootstrap3')
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.get()


if __name__ == '__main__':
    # print(secrets.token_hex())
    app.run()