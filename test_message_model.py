"""Message model tests."""

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


class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        m1 = Message(text="test", user_id=u1.id)
        m2 = Message(text="test", user_id=u2.id)

        db.session.add_all([m1, m2])
        db.session.commit()

        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        # User should have no messages
        self.assertEqual(len(u1.messages), 1)
        self.assertEqual(len(u2.messages), 1)


class AddMessageModelTestCase(MessageModelTestCase):
    def test_add_message(self):
        """Test that message is added"""

        u1 = User.query.get(self.u1_id)
        m3 = Message(text="test", user_id=u1.id)

        db.session.add(m3)
        db.session.commit()

        self.assertEqual(len(u1.messages), 2)
        self.assertIn(m3, Message.query.all())

    def test_add_invalid_message(self):
        """Test the message with invalid inputs is not added"""

        u1 = User.query.get(self.u1_id)

        with self.assertRaises(IntegrityError):

            m3 = Message(text=None, user_id=u1.id)

            db.session.add(m3)
            db.session.commit()

class DeleteMessageModelTestCase(MessageModelTestCase):
    def test_delete_message(self):
        """Test that single message is deleted"""

        u1 = User.query.get(self.u1_id)
        m1 = Message.query.get(self.m1_id)

        db.session.delete(m1)
        db.session.commit()

        self.assertEqual(len(u1.messages), 0)
        self.assertNotIn(m1, Message.query.all())


    def test_delete_user_and_messages(self):
        """Test that messages are deleted when user is deleted"""

        u2 = User.query.get(self.u2_id)
        m2 = Message.query.get(self.m2_id)

        db.session.delete(u2)
        db.session.commit()

        self.assertNotIn(m2, Message.query.all())

class LikeMessageModelTestCase(MessageModelTestCase):
    def test_like_message(self):
        """Test that liked message is added to user.liked_messages"""

        u1 = User.query.get(self.u1_id)
        m2 = Message.query.get(self.m2_id)

        u1.liked_messages.append(m2)

        self.assertTrue(u1.is_liking(m2))
        self.assertEqual(len(u1.liked_messages), 1)

    def test_unlike_message(self):
        """Test that unliked message is removed from user.liked_messages"""

        u1 = User.query.get(self.u1_id)
        m2 = Message.query.get(self.m2_id)

        u1.liked_messages.append(m2)
        u1.liked_messages.remove(m2)

        self.assertFalse(u1.is_liking(m2))
        self.assertEqual(len(u1.liked_messages), 0)







