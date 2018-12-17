from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from clubmanager import db
from clubmanager.models import Club, User, Membership, Team
from clubmanager.teams.forms import TeamForm

teams = Blueprint('teams', __name__)

@teams.route("/club/<int:club_id>/new_team", methods=['GET', 'POST'])
@login_required
def new_team(club_id):
    form = TeamForm()
    club = Club.query.get_or_404(club_id)
    if form.validate_on_submit():
        team = Team(name=form.name.data, club_id=club_id)
        db.session.add(team)
        db.session.commit()
        flash('Your team has been created!', 'success')
        return redirect(url_for('clubs.club', club_id=club.id))
    return render_template('create_team.html', title='New Team',
        form=form, legend='New Team')

'''
@teams.route("/club/<int:club_id>/team/<int:team_id>/", methods=['GET', 'POST'])
@login_required
def team(club_id, team_id):

    club = Club.query.get_or_404(club_id)
    players = club.members
    user = User.query.get(user_id)
    membership = Membership.query.filter_by(user_id=user.id).filter_by(club_id=club.id)
    final = membership[0]

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
'''
