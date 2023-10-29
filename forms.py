from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class RegisterForm(FlaskForm):
    """Form for adding users."""

    username = StringField("Enter Username", 
                           validators=[InputRequired(), Length(min=1, max=20)])

    password = PasswordField("Enter Password", 
                             validators=[InputRequired(), Length(min=6, max=100)])

    email = StringField("Enter Email", 
                        validators=[InputRequired(), Email(), Length(max=50)])

    first_name = StringField("Enter First Name", 
                             validators=[InputRequired(), Length(max=30)])

    last_name = StringField("Enter Last Name", 
                            validators=[InputRequired(), Length(max=30)])
    
class LoginForm(FlaskForm):
    """Form for Logging in users."""

    username = StringField("Enter Username", 
                           validators=[InputRequired(), Length(min=1, max=20)])
    
    password = PasswordField("Enter Password", 
                             validators=[InputRequired(), Length(min=1, max=100)])
    
class FeedbackForm(FlaskForm):
    """Form for users to add Feedback."""

    title = StringField("Enter Title", 
                        validators=[InputRequired(), Length(max=100)])
    
    content = StringField("Enter Content", 
                          validators=[InputRequired()])
    
class DeleteForm(FlaskForm):
    """This will 'delete' the form by being empty."""