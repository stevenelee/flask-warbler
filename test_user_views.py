"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()


class HomePageTestCase(UserBaseViewTestCase):
    def test_home_anon_route(self):

        with self.client as c:
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("New to Warbler?", html)


    def test_home_user_route(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("this is homepage and u1 is logged in", html)


class UserSignUpTestCase(UserBaseViewTestCase):

    def test_signup_user_valid(self):

        with self.client as c:
            resp = c.post("/signup",
                            data={"username":"u3",
                                "password":"password",
                                "email":"u3@email.com"},
                            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("this is homepage and u3 is logged in", html)


    def test_signup_user_invalid_username(self):

        with self.client as c:
            resp = c.post("/signup",
                            data={"username":"u1",
                                  "password":"password",
                                  "email":"u3@email.com"},
                            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username already taken", html)


class UserLogInTestCase(UserBaseViewTestCase):

    def test_valid_login(self):
        with self.client as c:

            resp = c.post("/login",
                          data={"username": "u1",
                                "password": "password"},
                          follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello, u1!", html)


    def test_invalid_login(self):
        with self.client as c:

            resp = c.post("/login",
                          data={"username": "u1",
                                "password": "passwor"},
                          follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)




class UserLogOutTestCase(UserBaseViewTestCase):

    def test_logout_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/logout",
                          follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Logged out successfully.", html)
            self.assertIn("user login page", html)







