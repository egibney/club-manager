from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from clubmanager import db
from clubmanager.models import Club, User, Membership, Team, TeamMembership
from clubmanager.teams.forms import TeamForm

teams = Blueprint('teams', __name__)

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

@teams.route("/club/<int:club_id>/new_team", methods=['GET', 'POST'])
@login_required
def new_team(club_id):
    form = TeamForm()
    if form.validate_on_submit():
        club = Club.query.get_or_404(club_id)
        team = Team(name=form.name.data, club_id=club_id)
        db.session.add(team)
        db.session.commit()
        flash('Your team has been created!', 'success')
        return redirect(url_for('clubs.club', club_id=club.id))
    return render_template('create_team.html', legend='New Team', title='New Team', form=form)

@teams.route("/club/<int:club_id>/team/<int:team_id>/team_moderate", methods=['GET', 'POST'])
@login_required
def team_moderate(club_id, team_id):
    team = Team.query.get_or_404(team_id)
    club = Club.query.get_or_404(club_id)
    players = club.members
    team_members = team.team_members
    player_list = []
    for p in players:
        player_list.append(p)
    for t in team_members:
        for p in players:
            if t.user_id == p.user_id:
                player_list.remove(p)
    '''I want to see if the user is an admin'''
    admin_status = user_is_admin(club_id, players)
    '''I want to see if the user is in the list of members'''
    pending_status = user_is_pending(club_id, club)
    '''I want to see if the user has an approved membership'''
    active_status = user_is_member(club_id, players)
    return render_template('team_moderate.html', club=club, player_list=player_list,
                        teams=teams, active_status=active_status, team_members=team_members,
                        pending_status=pending_status, admin_status=admin_status,
                        title='Team', team=team, legend='Team')

@teams.route("/club/<int:club_id>/team/<int:team_id>/add/<int:user_id>", methods=['GET', 'POST'])
@login_required
def add_player_team(club_id, team_id, user_id):
    '''
    Check to see if the player is already on the team, and change the action
    options if they are on the team.
    '''
    team_membership = TeamMembership(user_id=user_id, team_id=team_id)
    db.session.add(team_membership)
    db.session.commit()
    flash('The player has been added to the team!', 'success')
    return redirect(url_for('teams.team_moderate', club_id=club_id, team_id=team_id))

@teams.route("/club/<int:club_id>/team/<int:team_id>/remove/<int:user_id>")
@login_required
def remove_team_member(club_id, team_id, user_id):
    '''Load the club, user and corresponding membership object'''
    club = Club.query.get_or_404(club_id)
    team = Team.query.get_or_404(team_id)
    players = team.team_members
    user = User.query.get(user_id)
    team_membership = TeamMembership.query.filter_by(user_id=user.id).filter_by(team_id=team.id)
    final = team_membership[0]
    db.session.delete(final)
    db.session.commit()
    flash('The player has been removed from the team!', 'success')
    return redirect(url_for('clubs.club', club_id=club.id))

@teams.route("/club/<int:club_id>/team/<int:team_id>/delete_team")
@login_required
def delete_team(club_id, team_id):
    '''Load the club, user and corresponding membership object'''
    club = Club.query.get_or_404(club_id)
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash('The team has been deleted!', 'success')
    return redirect(url_for('clubs.club', club_id=club.id))
