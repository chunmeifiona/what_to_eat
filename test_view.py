"""User/Recipe/Refrigerator View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_view.py


import os
from unittest import TestCase

from models import db, connect_db, User, Recipe, Refrigerator

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///what_to_eat_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class ViewTestCase(TestCase):
    """Test views for User/Recipe/Refrigerator"""

    def setUp(self):
        """Create test client, add sample data. """
        User.query.delete()
        Recipe.query.delete()
        Refrigerator.query.delete()
        
        self.user1 = User.signup("user1","password1","user1@test.com", None)
        self.user1.id=1111
        self.user1.cuisineType = "American"

        recipe = Recipe(label="test recipe",user_id=self.user1.id)
        db.session.add(recipe)

        refrigerator = Refrigerator(name="beef",type="meat",user_id=self.user1.id)
        db.session.add(refrigerator)

        db.session.commit()

        self.client = app.test_client()
    
    def tearDown(self):
        db.session.rollback()

    def test_show_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/user/{self.user1.id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("user1@test.com",str(resp.data))

    def test_delete_user(self):
        user1 = User.query.get(1111)
        self.assertIsNotNone(user1)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/user/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
        
        user1 = User.query.get(1111)
        self.assertIsNone(user1)

    def test_home_logged_in(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            resp = c.post("/")
            self.assertEqual(resp.status_code,200)
            self.assertIn("American",str(resp.data))

    def test_show_myrefrigerator(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/myrefrigerator")
            self.assertEqual(resp.status_code,200)
            self.assertIn("beef",str(resp.data))

    def test_show_myrecipe(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get("/myrecipe/show")
            self.assertEqual(resp.status_code,200)
            self.assertIn("test recipe",str(resp.data))