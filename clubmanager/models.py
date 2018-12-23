from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from clubmanager import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class TeamMembership(db.Model):
    __tablename__ = 'teammembership'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    team_member = db.relationship("User", back_populates="teams")
    team = db.relationship("Team", back_populates="team_members")

    def __repr__(self):
        return f"TeamMembership('{self.user_id}', '{self.team_id}')"

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
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    clubs = db.relationship('Membership', back_populates="member")
    teams = db.relationship('TeamMembership', back_populates="team_member")

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

    def user_is_member(club_id, players):
        active_status = False
        for p in players:
            if p.member == current_user:
                if p.is_member == True:
                    active_status = True
        return active_status

    def user_is_admin(club_id, players):
        admin_status = False
        for p in players:
            if p.member == current_user:
                if p.is_admin == True:
                    admin_status = True
        return admin_status

    def user_is_pending(club_id, club):
        player_list = []
        pending_status = False
        for m in club.members:
            p = User(id=m.user_id)
            player_list.append(p)
        if current_user in player_list:
            pending_status = True
        else:
            pending_status = False
        return pending_status

class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    members = db.relationship("Membership", back_populates="club")
    teams = db.relationship('Team', backref='club_team', lazy=True)

    def __repr__(self):
        return f"Club('{self.name}', '{self.date_created}')"

class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    team_members = db.relationship("TeamMembership", back_populates="team", cascade="all, delete")

    def __repr__(self):
        return f"Team('{self.name}', '{self.date_created}', {self.club_id})"
