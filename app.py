from crypt import methods
import os
import random
import json
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from  sqlalchemy.sql.expression import func
import requests
from forms import UserAddForm, LoginForm, SearchForm, UserEditForm, RefrigeratorForm
from models import db, connect_db, User, Recipe, Refrigerator, DEFAULT_IMG_URL_USER
# from secret import app_id, app_key

# APP_ID = app_id
# APP_KEY = app_key
APP_ID = "d5bde7fd" #os.getenv('APP_ID',"optional-default")
APP_KEY = "2f20522258e440754a7a733104b92304"#os.getenv('APP_KEY', "optional-default")
API_BASE_URL = "https://api.edamam.com/api/recipes/v2"

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
uri = os.environ.get('DATABASE_URL', 'postgresql:///what_to_eat')
if uri.startswith("postgres://"):
 uri = uri.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`
app.config['SQLALCHEMY_DATABASE_URI'] = uri
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     os.environ.get('DATABASE_URL', 'postgresql:///what_to_eat'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
##############################################################################
# User signup/login/logout/edit/show/delete
##############################################################################
##############################################################################

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


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup."""

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
            return render_template('user/signup.html', form=form)

        do_login(user)
        return redirect("/")

    else:
        return render_template('user/signup.html', form=form)


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

    return render_template('user/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    # IMPLEMENT THIS
    do_logout()
    flash("Goodbye!","success")
    return redirect("/login")


@app.route('/user/<int:user_id>')
def show_user(user_id):
    """Show user's information"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    return render_template('user/show.html', user=user)

@app.route('/user/edit', methods=['GET','POST'])
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
        

    return render_template("user/edit.html",form=form, user_id=user.id)

@app.route('/user/delete')
def delete_user():
    """Delete user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/")

#################################################################
#################################################################
#search recipes / add to myrecipe / delete from  myrecipe
#################################################################
#################################################################

def singleQuoteToDoubleQuote(singleQuoted):
            '''
            convert a single quoted string to a double quoted one
            Args:
                singleQuoted(string): a single quoted string e.g. {'cities': [{'name': "Upper Hell's Gate"}]}
            Returns:
                string: the double quoted version of the string e.g. 
            see
               - https://stackoverflow.com/questions/55600788/python-replace-single-quotes-with-double-quotes-but-leave-ones-within-double-q 
            '''
            cList=list(singleQuoted)
            inDouble=False;
            inSingle=False;
            for i,c in enumerate(cList):
                #print ("%d:%s %r %r" %(i,c,inSingle,inDouble))
                if c=="'":
                    if not inDouble:
                        inSingle=not inSingle
                        cList[i]='"'
                elif c=='"':
                    inDouble=not inDouble
            doubleQuoted="".join(cList)    
            return doubleQuoted

def search_recipe(params):
    """search recipes via extarnal api and get recipe json data"""
    res = requests.get(f"{API_BASE_URL}", params = params)
    data = res.json() 
    recipes = []

    if data["count"] == 0:
        recipes = None

    for hit in data["hits"]:
        recipe = {k:v for k, v in {"image":hit["recipe"].get("image", "No"), 
                                   "label":hit["recipe"].get("label", "No"), 
                                   "url":hit["recipe"].get("url", "No"), 
                                   "ingredientLines":hit["recipe"].get("ingredientLines", "No"),
                                   "cuisineType":hit["recipe"].get("cuisineType", "No"),
                                   "dishType":hit["recipe"].get("dishType", "No"),
                                   "mealType":hit["recipe"].get("mealType", "No")}.items()}
        recipes.append(recipe)

    return recipes

@app.route('/', methods=['GET','POST'])
def home_page():
    """show home page"""
    form = SearchForm()
    food_list = ["beef","chicken","pork"]
    search_q = random.choice(food_list)
    if g.user:
        food = Refrigerator.query.filter(Refrigerator.user_id==g.user.id).order_by(func.random()).first()
        search_q = food.name if food else search_q
        params ={'q':search_q, 'app_id':APP_ID, 'app_key':APP_KEY, 'type':"public", 
                 'cuisineType':g.user.cuisineType}
    else:
        params ={'q':search_q, 'app_id':APP_ID, 'app_key':APP_KEY, 'type':"public"}

    if form.validate_on_submit():
        search_q = form.search_q.data
        cuisineType = form.cuisineType.data
        mealType = form.mealType.data
        dishType = form.dishType.data

        new_params= {k:v for k,v in {"q":search_q, "cuisineType":cuisineType, "mealType":mealType, "dishType":dishType}.items() if v != 'All'}
        params.update(new_params)

    recipes = search_recipe(params)
    
    return render_template("home.html", form=form, recipes=recipes)


@app.route('/myrecipe/add',methods=['GET','POST'])
def add_recipe():
    """add a recipe to myrecipe"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    recipe_str = singleQuoteToDoubleQuote(request.form["recipe"])
    recipe = json.loads(recipe_str)

    label=recipe["label"]
    image=recipe["image"]
    url=recipe["url"]
    cuisinetype = "/".join(recipe["cuisineType"])
    dishtype = "/".join(recipe["dishType"])
    mealtype = "/".join(recipe["mealType"])
    ingredient = "\n".join(recipe["ingredientLines"])

    try:
        recipe = Recipe(label=label, image=image, url=url, cuisinetype=cuisinetype, 
                        dishtype=dishtype, mealtype=mealtype,
                        ingredient=ingredient, user_id=g.user.id)
        
        db.session.add(recipe)
        db.session.commit()

    except IntegrityError:
        flash("This recipe is already in my recipes",'danger')
    
    return redirect("/")

@app.route('/myrecipe/delete/<int:recipe_id>')
def delete_recipe(recipe_id):
    """delete a recipe from myrecipe"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
        
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()

    return redirect('/myrecipe/show')

@app.route('/myrecipe/show')
def show_myrecipe():
    """show all recipes in myrecipe"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    recipes = Recipe.query.filter(Recipe.user_id==g.user.id).all()

    return render_template('myrecipe.html',recipes=recipes)

#################################################################
#################################################################
# add/delete some food to my refrigerator
#################################################################
#################################################################

@app.route("/myrefrigerator",methods=['GET','POST'])
def add_refrigerator():
    """display and add some food to my refrigerator"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    refrigerator = Refrigerator.query.filter(Refrigerator.user_id==g.user.id).all()
    form = RefrigeratorForm()
   
    if form.validate_on_submit():
        name=form.name.data,
        type=form.type.data
        
        refrigerator = Refrigerator(name=name, type=type, user_id = g.user.id)
        db.session.add(refrigerator)
        db.session.commit()

        return redirect("/myrefrigerator")

    else:
        return render_template('refrigerator.html', form=form, refrigerator=refrigerator)

@app.route("/myrefrigerator/delete/<int:refrigerator_id>")
def delete_refrigerator(refrigerator_id):
    """delete food from my refrigerator"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    food = Refrigerator.query.get_or_404(refrigerator_id)
    db.session.delete(food)
    db.session.commit()

    return redirect("/myrefrigerator")


# for js file api
# @app.route('/api/add-recipe', methods = ['POST'])
# def add_recipe_1():
#     """Add to my recipe"""
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     label = request.json["label"]
#     image = request.json["image"]
#     cuisinetype = request.json["cuisinetype"]
#     dishtype = request.json["dishtype"]
#     mealtype = request.json["mealtype"]
#     ingredient = request.json["ingredient"]

#     recipe = Recipe(label=label, image=image, cuisinetype=cuisinetype, dishtype=dishtype,mealtype=mealtype,ingredient=ingredient)
#     db.session.add(recipe)
#     db.session.commit()

#     return ("recipe", 201)




