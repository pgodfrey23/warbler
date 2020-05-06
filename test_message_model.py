"""Message model tests."""

# run these tests like:
# 
# FLASK_ENV=production python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        self.client = app.test_client()

        user1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )

        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        message1 = Message(
            text="test1_message",
            user_id=user1.id  
        )

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        user1 = User.query.filter(User.email == "test1@test.com").all()[0]

        m = Message(
            text="test_message",
            user_id=user1.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertTrue(m)
        self.assertIn(m, Message.query.all())
    
