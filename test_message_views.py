"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()

        user = User.query.filter(User.email == "test@test.com").all()[0]
        self.testmessage = Message(text="test message", user_id=user.id)

        db.session.add(self.testmessage)
        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_add_message(self):
        """When you’re logged in, can you add a message as yourself?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp.status_code, 302)

            # pick up created message - ([0] message created in setUp)
            msg = Message.query.all()[1]
            self.assertEqual(msg.text, "Hello")
    
    def test_delete_message(self):
        """When you’re logged in, can you delete a message as yourself?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # confirm message is in the databse before deletion - from setUp
            self.assertEqual(len(Message.query.all()), 1)

            message = Message.query.all()[0]
            resp = c.post(f"/messages/{message.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn('Hello', html)
            self.assertEqual(len(Message.query.all()), 0)

    def test_add_message_logged_out(self):
        """When you’re logged out, are you prohibited from adding messages?"""

        resp = self.client.get("/messages/new", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn("Access unauthorized.", html)
            
    def test_delete_message_logged_out(self):
        """When you’re logged out, are you prohibited from deleting messages?"""

        message = Message.query.all()[0]
        resp = self.client.post(f"/messages/{message.id}/delete", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertIn("Access unauthorized.", html)


        # """When you’re logged in, are you prohibited from adding a message as another user?"""
        # """When you’re logged in, are you prohibited from deleting a message as another user?"""
        

        # When you’re logged in, can you see the follower / following pages for any user?
        # When you’re logged out, are you disallowed from visiting a user’s follower / following pages?

        # When you’re logged in, are you prohibiting from adding a message as another user?
        # When you’re logged in, are you prohibiting from deleting a message as another user?