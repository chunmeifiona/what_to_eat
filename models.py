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
    cuisineType = db.Column(db.Text)

    recipe = db.relationship("Recipe", backref="user", cascade="all, delete")
    refrigerator = db.relationship("Refrigerator", backref="user", cascade="all, delete")

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
    label = db.Column(db.Text, nullable=False, unique=True)
    image = db.Column(db.Text, default = DEFAULT_IMG_URL_RECIPE)
    url = db.Column(db.Text)
    ingredient = db.Column(db.Text)
    mealtype = db.Column(db.Text)
    dishtype = db.Column(db.Text)
    cuisinetype = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    

class Refrigerator(db.Model):
    __tablename__ = 'refrigerators'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)