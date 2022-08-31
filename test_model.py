"""User/Recipe/Refrigerator model tests."""

# run these tests like:
#
#    python -m unittest test_model.py


from cProfile import label
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Recipe, Refrigerator

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///what_to_eat_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for Users"""

    def setUp(self):
        """Create test client, add sample data. """

        User.query.delete()
        Recipe.query.delete()
        Refrigerator.query.delete()
        

        self.user1 = User.signup("user1","password1","user1@test.com", None)
        self.user1.id=1111
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        user2 = User(
            username = "user2",
            email = "user2@test.com",
            password = "password2"
        )

        db.session.add(user2)
        db.session.commit()

        self.assertEqual(len(user2.recipe),0)
        self.assertEqual(len(user2.refrigerator),0)

    def test_signup(self):
        user1 = User.query.get(1111)
        self.assertIsNotNone(user1)
        self.assertEqual(user1.username,"user1")
        self.assertEqual(user1.email, "user1@test.com")
        self.assertNotEqual(user1.password, "password1")

    def test_invalid_username_signup(self):
        """test duplicated username"""
        invalid_user = User.signup("user1", "password", "invalid_username@test.com", None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """test duplicated email"""
        invalid_user = User.signup("user3","password3","user1@test.com",None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """test null password"""
        with self.assertRaises(ValueError) as context:
            User.signup("user4", None, "user4@test.com", None)

    def test_valid_authentication(self):
        user = User.authenticate(self.user1.username, "password1")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.user1.email)

    def test_invalid_username(self):
        user = User.authenticate("invaliduser", "password1")
        self.assertFalse(user)

    def test_invalid_password(self):
        user = User.authenticate(self.user1.username, "invalidpassword")
        self.assertFalse(user)

    def test_recipe_model(self):
        self.assertEqual(len(self.user1.recipe), 0)

        recipe = Recipe(label="test recipe",user_id=self.user1.id)
        db.session.add(recipe)
        db.session.commit()

        self.assertEqual(len(self.user1.recipe), 1)

    def test_refrigerator_model(self):
        self.assertEqual(len(self.user1.refrigerator), 0)

        refrigerator = Refrigerator(name="beef",type="meat",user_id=self.user1.id)
        db.session.add(refrigerator)
        db.session.commit()

        self.assertEqual(len(self.user1.refrigerator), 1)



        