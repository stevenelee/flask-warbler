"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follow
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
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

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)


class UserFollowTestCase(UserModelTestCase):
    """Test cases for user following/followed by methods"""

    def test_is_following(self):
        """Test User class method .is_following == True"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)
        self.assertTrue(u1.is_following(u2))

    def test_is_not_following(self):
        """Test User class method .is_following == False"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_following(u2))

    def test_is_followed_by(self):
        """Test User class method .is_followed_by == True"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)
        self.assertTrue(u1.is_followed_by(u2))

    def test_is_not_followed_by(self):
        """Test User class method .is_followed_by == False"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u1.is_followed_by(u2))


class UserSignupTestCase(UserModelTestCase):
    """Test cases for valid and invalid user signup"""

    def test_signup_valid_user(self):
        """Test User class method .signup for valid user"""

        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.commit()

        self.assertIsNotNone(User.query.get(u3.id))

    def test_signup_invalid_user(self):
        """Test User class method .signup for invalid user"""

        #username already exists
        with self.assertRaises(IntegrityError):
            User.signup("u1", "u3@email.com", "password", None)
            db.session.commit()

        #empty string username and email
        with self.assertRaises(Exception):
            User.signup("", "", password="password", image_url=None)
            db.session.commit()


class UserAuthenticateTestCase(UserModelTestCase):
    """Test cases for valid and invalid user authentication"""

    def test_authenticate_valid_user(self):
        """Test user class method .authenticate for valid user"""

        u1 = User.query.get(self.u1_id)

        self.assertEqual(User.authenticate("u1", "password"), u1)

    def test_authenticate_invalid_user(self):
        """Test user class method .authenticate for invalid user"""

        self.assertFalse(User.authenticate("asdf", "password"))
        self.assertFalse(User.authenticate("u1", "awefawe"))
