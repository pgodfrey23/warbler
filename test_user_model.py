"""User model tests."""

# run these tests like:
# 
# FLASK_ENV=production python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Like

from sqlalchemy.exc import IntegrityError

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


class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Like.query.delete()

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

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does the repr work."""
        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]
        # import pdb; pdb.set_trace()
        self.assertEqual(user1.__repr__(), f"<User #{user1.id}: {user1.username}, {user1.email}>")
        self.assertEqual(user2.__repr__(), f"<User #{user2.id}: {user2.username}, {user2.email}>")

    def test_following(self):
        """Test user1 is following user2 """
        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        user1.following.append(user2)
        db.session.commit()

        self.assertTrue(user1.is_following(user2))

    def test_not_following(self):
        """Test user1 is not following user2."""
        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        self.assertFalse(user1.is_following(user2))

    def test_is_followed_by(self):
        """Test user1 is followed by user2."""
        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        user1.followers.append(user2)
        db.session.commit()

        self.assertTrue(user1.is_followed_by(user2))

    def test_is_not_followed_by(self):
        """Test user1 is not followed by user2."""
        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        self.assertFalse(user1.is_followed_by(user2))


    def test_message_liked(self):
        """ Test user likes message."""

        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        # message written by user1
        message_1 = Message(
            text="test1_message",
            user_id=user1.id  
        )

        db.session.add(message_1)
        db.session.commit()

        # get message_1 from messages table
        message = Message.query.limit(1).all()[0]

        # user2 likes message
        like = Like(user_id=user2.id, message_id=message.id)
        db.session.add(like)
        db.session.commit()

        self.assertTrue(user2.likes_message(message.id))

    def test_message_not_liked(self):
        """ Test user does not like message."""

        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        # message written by user1
        message_1 = Message(
            text="test1_message",
            user_id=user1.id  
        )

        db.session.add(message_1)
        db.session.commit()

        # get message_1 from messages table
        message = Message.query.limit(1).all()[0]

        self.assertFalse(user2.likes_message(message.id))

    def test_user_create_success(self):
        """Test User.signup successfully creates a new user givev valid credentials."""

        user3 = User.signup(
            email="test3@test.com",
            username="testuser3",
            password="TEST_PASSWORD",
            image_url=User.image_url.default.arg
        )

        db.session.add(user3)
        db.session.commit()

        user = User.query.filter(User.email == "test3@test.com").all()[0]

        self.assertIn(user, User.query.all())

    def test_user_create_fail(self):
        """Test User.signup fails if validation requirements not met. """
        with self.assertRaises(IntegrityError):
            User.signup(
                email="test1@test.com",
                username="testuser1",
                password="TEST_PASSWORD",
                image_url=User.image_url.default.arg
            )

            db.session.commit()

    def test_user_authenticate_success(self):
        """Successfully return a user when given valid username and password."""

        unhashed_password = "TEST_PASSWORD"
        user3_signup = User.signup(
            email="test3@test.com",
            username="testuser3",
            password=unhashed_password,
            image_url=User.image_url.default.arg
        )

        db.session.add(user3_signup)
        db.session.commit()

        user3 = User.query.filter(User.email == "test3@test.com").all()[0]
        user = User.authenticate(user3.username, unhashed_password)

        self.assertEquals(user3, user)

    def test_user_authenticate_invalid_username(self):
        """Fail to return a user when given invalid username."""

        unhashed_password = "TEST_PASSWORD"
        
        user3_signup = User.signup(
            email="test3@test.com",
            username="testuser3",
            password=unhashed_password,
            image_url=User.image_url.default.arg
        )

        db.session.add(user3_signup)
        db.session.commit()

        user3 = User.query.filter(User.email == "test3@test.com").all()[0]
        user = User.authenticate('wrong_username', unhashed_password)

        self.assertFalse(user)
    
    def test_user_authenticate_invalid_password(self):
        """Fail to return a user when given invalid password."""

        unhashed_password = "TEST_PASSWORD"

        user3_signup = User.signup(
            email="test3@test.com",
            username="testuser3",
            password=unhashed_password,
            image_url=User.image_url.default.arg
        )

        db.session.add(user3_signup)
        db.session.commit()

        user3 = User.query.filter(User.email == "test3@test.com").all()[0]
        user = User.authenticate(user3.username, 'wrong_password')

        self.assertFalse(user)
