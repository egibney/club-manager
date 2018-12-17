from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from clubmanager import db
from clubmanager.models import Club, User, Membership
from clubmanager.clubs.forms import ClubForm


clubs = Blueprint('clubs', __name__)

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


@clubs.route("/")
@login_required
def home():
    page = request.args.get('page',1, type=int)
    clubs = Club.query.all()
    return render_template('home.html', clubs=clubs)

@clubs.route("/club/new", methods=['GET', 'POST'])
@login_required
def new_club():
    form = ClubForm()
    if form.validate_on_submit():
        club = Club(name=form.name.data)
        db.session.add(club)
        db.session.commit()
        flash('Your club has been created!', 'success')
        return redirect(url_for('clubs.home'))
    return render_template('create_club.html', title='New Club',
        form=form, legend='New Club')

@clubs.route("/club/<int:club_id>")
@login_required
def club(club_id):
    club = Club.query.get_or_404(club_id)
    players = club.members
    teams = club.teams
    '''I want to see if the user is an admin'''
    admin_status = user_is_admin(club_id, players)
    '''I want to see if the user is in the list of members'''
    pending_status = user_is_pending(club_id, club)
    '''I want to see if the user has an approved membership'''
    active_status = user_is_member(club_id, players)
    return render_template('club.html', club=club, players=players, teams=teams, active_status=active_status,
                        pending_status=pending_status, admin_status=admin_status)

@clubs.route("/club/<int:club_id>/join", methods=['GET', 'POST'])
@login_required
def join_club(club_id):
    club = Club.query.get_or_404(club_id)
    user = current_user
    membership = Membership(user_id=user.id, club_id=club.id)
    db.session.add(membership)
    db.session.commit()
    return redirect(url_for('clubs.club', club_id=club.id))

@clubs.route("/club/<int:club_id>/leave", methods=['GET', 'POST'])
@login_required
def leave_club(club_id):
    club = Club.query.get_or_404(club_id)
    user = User.query.get(current_user.id)
    membership = Membership.query.filter_by(user_id=user.id).filter_by(club_id=club.id)
    final = membership[0]
    db.session.delete(final)
    db.session.commit()
    return redirect(url_for('clubs.club', club_id=club.id))

@clubs.route("/club/<int:club_id>/user/<int:user_id>/approve_member", methods=['GET', 'POST'])
@login_required
def approve_member(club_id, user_id):
    '''Load the club, user and corresponding membership object'''
    club = Club.query.get_or_404(club_id)
    players = club.members
    user = User.query.get(user_id)
    membership = Membership.query.filter_by(user_id=user.id).filter_by(club_id=club.id)
    final = membership[0]
    '''I need to do a check to make sure the current user is an admin of the club'''
    admin_status = False
    for p in players:
        if p.member == current_user:
            if p.is_admin == True:
                admin_status = True
    if admin_status == True:
        final.is_member = True
        db.session.add(final)
        db.session.commit()
    return redirect(url_for('clubs.club', club_id=club.id))

@clubs.route("/club/<int:club_id>/user/<int:user_id>/make_admin", methods=['GET', 'POST'])
@login_required
def make_admin(club_id, user_id):
    '''Load the club, user and corresponding membership object'''
    club = Club.query.get_or_404(club_id)
    players = club.members
    user = User.query.get(user_id)
    membership = Membership.query.filter_by(user_id=user.id).filter_by(club_id=club.id)
    final = membership[0]
    '''I need to do a check to make sure the current user is an admin of the club'''
    admin_status = False
    for p in players:
        if p.member == current_user:
            if p.is_admin == True:
                admin_status = True
    if admin_status == True:
        final.is_admin = True
        db.session.add(final)
        db.session.commit()
    return redirect(url_for('clubs.club', club_id=club.id))

@clubs.route("/club/<int:club_id>/user/<int:user_id>/remove_member", methods=['GET', 'POST'])
@login_required
def remove_member(club_id, user_id):
    '''Load the club, user and corresponding membership object'''
    club = Club.query.get_or_404(club_id)
    players = club.members
    user = User.query.get(user_id)
    membership = Membership.query.filter_by(user_id=user.id).filter_by(club_id=club.id)
    final = membership[0]
    '''I need to do a check to make sure the current user is an admin of the club'''
    admin_status = False
    for p in players:
        if p.member == current_user:
            if p.is_admin == True:
                admin_status = True
    if admin_status == True:
        db.session.delete(final)
        db.session.commit()
    return redirect(url_for('clubs.club', club_id=club.id))


@clubs.route("/club/<int:club_id>/user/<int:user_id>")
@login_required
def member_profile(club_id, user_id):
    '''Load the club, user and corresponding membership object'''
    club = Club.query.get_or_404(club_id)
    user = User.query.get_or_404(user_id)
    club_teams = []
    for t in user.teams:
        if t.club.id == club_id:
            club_teams.append(t)
    club_list = []
    for c in user.clubs:
        i = Club(id=c.club_id)
        club_list.append(i)
    return render_template('member_profile.html', club=club, user=user,
        club_list=club_list, club_teams=club_teams)
