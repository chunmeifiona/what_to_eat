from random import choices
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length

cuisines = ["All","American","Asian","British","Caribbean","Central Europe","Chinese",
            "Eastern Europe","French","Indian","Italian","Japanese","Kosher",
            "Mediterranean","Mexican","Middle Eastern","South American","South East Asian"]

meals = ["All","Breakfast", "Dinner","Lunch","Snack","Teatime"]

dishs = ["All","Biscuits and cookies","Bread","Cereals","Condiments and sauces","Desserts",
        "Drinks","Main course","Pancake","Preps","Preserve","Salad","Sandwiches",
        "Side dish","Soup","Starter","Sweets"]

class UserAddForm(FlaskForm):
    """Form for adding users. """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    

class UserEditForm(FlaskForm):
    """Form for editing users"""

    username = StringField("Username",validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    cuisineType = SelectField('CuisineType', choices=[(cu, cu) for cu in cuisines])

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class SearchForm(FlaskForm):
    """Search recipe form"""
    search_q = StringField('Search', validators=[DataRequired()])
    cuisineType = SelectField('CuisineType', choices=[(cu, cu) for cu in cuisines])
    mealType = SelectField('MealType', choices=[(m, m) for m in meals])
    dishType = SelectField('DishType', choices=[(d, d) for d in dishs])