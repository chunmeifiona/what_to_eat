from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

DEFAULT_IMG_URL_USER = "https://media.istockphoto.com/photos/woman-in-superhero-costume-picture-id1140379193?b=1&k=20&m=1140379193&s=170667a&w=0&h=p_47HyiXchDOz7Vwu0Kxhwuh1jSTpbO7MT88ENAVHCo="
DEFAULT_IMG_URL_RECIPE = "https://images.unsplash.com/photo-1485921325833-c519f76c4927?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTh8fHJlY2lwZXxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=400&q=60"

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
        
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    image_url = db.Column(db.Text, default = DEFAULT_IMG_URL_USER)
    # cuisine_id = db.Column(db.Integer, db.ForeignKey('cuisine.id'))
    # health_id = db.Column(db.Integer, db.ForeignKey('health.id'))

    recipe = db.relationship("Recipe", secondary="userrecipes", backref="user", cascade="all, delete")

    @classmethod
    def signup(cls, username, password, email, image_url):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")

        user = User(
            username=username,
            email=email,
            password=hashed_utf8,
            image_url=image_url,
        )

        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False."""
        user=User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False
class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    ingredient = db.Column(db.Text, nullable=False)
    mealtype = db.Column(db.Text, nullable=False)
    dishtype = db.Column(db.Text, nullable=False)
    # health_id = db.Column(db.Integer, db.ForeignKey('health.id'))
    # cuisine_id = db.Column(db.Integer, db.ForeignKey('cuisine.id'))

class UserRecipe(db.Model):
    """Mapping of a user to a recipes"""
    __tablename__ = 'userrecipes'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id=db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)

# class Cuisine(db.Model):
#     __tablename__ = 'cuisines'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     cuisinetype = db.Column(db.Text, nullable=False)

# class Health(db.Model):
#     __tablename__ = 'healths'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     healthtype = db.Column(db.Text, nullable=False)
