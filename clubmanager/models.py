from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from clubmanager import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Membership(db.Model):
    __tablename__ = 'membership'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), primary_key=True)
    is_admin = db.Column(db.Boolean, unique=False, default=False)
    is_member = db.Column(db.Boolean, unique=False, default=False)
    member = db.relationship("User", back_populates="clubs")
    club = db.relationship("Club", back_populates="members")

    def __repr__(self):
        return f"Membership('{self.user_id}', '{self.club_id}', '{self.is_admin}', '{self.is_member}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=True, nullable=False)
    last_name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    clubs = db.relationship('Membership', back_populates="member")

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return none
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}', '{self.image_file}')"

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    members = db.relationship("Membership", back_populates="club")

    def __repr__(self):
        return f"Club('{self.name}', '{self.date_created}')"
