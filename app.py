from crypt import methods
import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from forms import UserAddForm, LoginForm, SearchForm, UserEditForm
from models import db, connect_db, User, Recipe, DEFAULT_IMG_URL_USER
from secret import app_id, app_key

APP_ID = app_id
APP_KEY = app_key
API_BASE_URL = "https://api.edamam.com/api/recipes/v2"

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///what_to_eat'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def search_recipe(params):
    """search recipes"""
    res = requests.get(f"{API_BASE_URL}", params = params)
    data = res.json() 
    recipes = []
    
    for hit in data["hits"]:
        recipe = {k:v for k, v in {"image":hit["recipe"]["image"], 
                                   "label":hit["recipe"]["label"], 
                                   "url":hit["recipe"]["url"], 
                                   "ingredientLines":hit["recipe"]["ingredientLines"],
                                   "cuisineType":hit["recipe"]["cuisineType"],
                                   "dishType":hit["recipe"]["dishType"],
                                   "mealType":hit["recipe"]["mealType"]}.items()}
        recipes.append(recipe)

    return recipes

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username/email already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    do_logout()
    flash("Goodbye!","success")
    return redirect("/login")

@app.route('/', methods=['GET','POST'])
def home_page():
    """show home page"""
    form = SearchForm()
    if g.user:
        params ={'q':'beef', 'app_id':APP_ID, 'app_key':APP_KEY, 'type':"public", 'cuisineType':g.user.cuisineType}
    else:
        params ={'q':'beef', 'app_id':APP_ID, 'app_key':APP_KEY, 'type':"public"}

    if form.validate_on_submit():
        search_q = form.search_q.data
        cuisineType = form.cuisineType.data
        mealType = form.mealType.data
        dishType = form.dishType.data

        new_params= {k:v for k,v in {"q":search_q, "cuisineType":cuisineType, "mealType":mealType, "dishType":dishType}.items() if v != 'All'}
        params.update(new_params)

    recipes = search_recipe(params)
    return render_template("home.html", form=form, recipes=recipes)

@app.route('/user/<int:user_id>')
def show_user(user_id):
    """Show user's information"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    return render_template('show.html', user=user)

@app.route('/user/profile', methods=['GET','POST'])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or DEFAULT_IMG_URL_USER
            user.cuisineType = form.cuisineType.data

            db.session.commit()
            return redirect(f"/user/{user.id}")


        flash("Wrong password, please try again!", 'danger')
        

    return render_template("edit.html",form=form, user_id=user.id)

@app.route('/users/delete')
def delete_user():
    """Delete user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")