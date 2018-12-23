from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError
from clubmanager.models import Team


class TeamForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

    def validate_name(self, name):
        team = Team.query.filter_by(name=name.data).first()
        if team:
            raise ValidationError('That name is taken. Please choose a different one.')
