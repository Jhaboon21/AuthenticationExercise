from flask import Flask, request, render_template, redirect, flash, session
from werkzeug.exceptions import Unauthorized
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from psycopg2._psycopg import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///authentication'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'ihaveasecret'

connect_db(app)
with app.app_context():
    db.create_all()

@app.route("/")
def root():
    """Homepage"""

    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Handle registering users."""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)
        
        try:
            db.session.commit()
            session['username'] = user.username

            return redirect(f"/users/{user.username}")
        except IntegrityError as e:
            flash("User exists already. Try logging in or make a new username.") #this part doesn't work yet. need to do research on how to prevent duplicates
            db.session.rollback()
            return render_template("users/register.html", form=form)
    else:
        return render_template("users/register.html", form=form)
    
@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Handle logging in users."""

    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username or password."]
            return render_template("users/login.html", form=form)

    return render_template("users/login.html", form=form)

@app.route("/logout", methods=["GET"])
def logout_user():
    """Handle logging out user."""

    session.pop("username")

    return redirect("/login")

@app.route("/users/<username>", methods=["GET"])
def show_user(username):
    """Only authorized users are allowed on this page."""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()
    
    user = User.query.get(username)
    form = DeleteForm()
    
    return render_template("users/show.html", user=user, form=form)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Remove user from database and all of their feedback."""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    
    return redirect("/login")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Display form only to authorized users to add feedback."""

    if "username" not in session or username != session["username"]:
        raise Unauthorized()
    
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username
        )

        db.session.add(feedback)
        db.session.commit()
        
        return redirect(f"/users/{feedback.username}")
    else:
        return render_template("feedback/new.html", form=form)

@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Display form only to authorized users to edit a specific feedback."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm()

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    
    return render_template("/feedback/edit.html", form=form, feedback=feedback)

@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Display form only to authorized users to delete a specific feedback."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session["username"]:
        raise Unauthorized()
    
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")
