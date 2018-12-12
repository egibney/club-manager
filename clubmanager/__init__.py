from flask import Flask
from flask_sqlalchemy import SQLAlchemy, declarative_base
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from clubmanager.config import Config
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from clubmanager.users.routes import users
    from clubmanager.clubs.routes import clubs
    from clubmanager.main.routes import main
    from clubmanager.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(clubs)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app