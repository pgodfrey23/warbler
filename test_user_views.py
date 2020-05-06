"""User View tests."""

# run these tests like:
#
# FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, User, Message, Follows, Likes

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


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        Likes.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="test1user",
                                     email="test1@test.com",
                                     password="testuser",
                                     image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                     email="test2@test.com",
                                     password="testuser",
                                     image_url=None)

        db.session.commit()

        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        self.testmessage1 = Message(text="test message", user_id=user1.id)

        user2 = User.query.filter(User.email == "test2@test.com").all()[0]
        self.testmessage2 = Message(text="test message", user_id=user2.id)

        db.session.add(self.testmessage1)
        db.session.add(self.testmessage2)
        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_view_users_logged_out(self):
        """Does users page render if not logged in?"""

        resp = self.client.get("/users")
        self.assertEqual(resp.status_code, 200)

    def test_view_own_profile_logged_in(self):
        """Does user's own profile page render correctly when logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"/users/{self.testuser1.id}")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)

            # confirm 'delete message button' renders
            self.assertIn('<i class="far fa-trash-alt">', html)
    
    def test_edit_profile_logged_in(self):
        """Does user's own edit profile page render correctly when logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get("/users/profile", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn('Edit Your Profile', html)
    
    def test_edit_profile_logged_out(self):
        """Does user's own edit profile page not render when logged out?"""

        resp = self.client.get("/users/profile", follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertNotIn('Edit Your Profile', html)
        self.assertIn('You must be logged in to access this page', html)

    def test_view_user_profile_logged_in(self):
        """Does user profile page render correctly when logged in?"""

        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"/users/{user2.id}")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)

            # confirm 'like message button' renders
            self.assertIn('<i class="far fa-heart">', html)

            # confirm 'delete message button' does not render
            self.assertNotIn('<i class="far fa-trash-alt">', html)

    def test_view_user_profile_logged_out(self):
        """Does user profile page render correctly when logged out?"""
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        resp = self.client.get(f"/users/{user2.id}")
        self.assertEqual(resp.status_code, 200)

        html = resp.get_data(as_text=True)

        # confirm 'like message button' does not render
        self.assertNotIn('<i class="far fa-heart">', html)

        # confirm 'delete message button' does not render
        self.assertNotIn('<i class="far fa-trash-alt">', html)

    def test_view_following_logged_in(self):
        """When you’re logged in, can you see the following page for any user?"""
        
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"/users/{user2.id}/following")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn('You must be logged in to access this page', html)

    def test_view_following_logged_out(self):
        """When you’re logged out, are you disallowed from visiting a user’s following page?"""
        
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]
        resp = self.client.get(f"/users/{user2.id}/following", follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertIn('You must be logged in to access this page', html)

    def test_view_followers_logged_in(self):
        """When you’re logged in, can you see the followers pages for any user?"""
        
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"/users/{user2.id}/followers")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn('You must be logged in to access this page', html)

    def test_view_followers_logged_out(self):
        """When you’re logged out, are you disallowed from visiting a user’s followers page?"""
        
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]
        resp = self.client.get(f"/users/{user2.id}/followers", follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertIn('You must be logged in to access this page', html)

    def test_view_likes_logged_in(self):
        """When you’re logged in, can you see the likes page for any user?"""
        
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"/users/{user2.id}/likes")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertNotIn('You must be logged in to access this page', html)

    def test_view_likes_logged_out(self):
        """When you’re logged out, are you disallowed from visiting a user’s likes page?"""
        
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]
        resp = self.client.get(f"/users/{user2.id}/likes", follow_redirects=True)

        html = resp.get_data(as_text=True)
        self.assertIn('You must be logged in to access this page', html)
    
    def test_follower_user_logged_in(self):
        """Can a user follow another user when logged in?"""

        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            self.assertEqual(len(Follows.query.all()), 0)

            resp = c.post(f"/users/follow/{user2.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertEqual(len(Follows.query.all()), 1)
            follow_instance = Follows.query.all()[0]

            self.assertEqual(follow_instance.user_being_followed_id, user2.id)
            self.assertEqual(follow_instance.user_following_id, self.testuser1.id)

            html = resp.get_data(as_text=True)
            self.assertNotIn('You must be logged in to access this page', html)

    def test_follower_user_logged_out(self):
        """Is a user prohibited from following another user when logged out?"""

        user2 = User.query.filter(User.email == "test2@test.com").all()[0]
        self.assertEqual(len(Follows.query.all()), 0)

        resp = self.client.post(f"/users/follow/{user2.id}", follow_redirects=True)
        self.assertEqual(len(Follows.query.all()), 0)

        html = resp.get_data(as_text=True)
        self.assertIn('You must be logged in to access this page', html)
    
    def test_unfollow_user_logged_in(self):
        """Can a user unfollow another user when logged in?"""

        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            self.assertEqual(len(Follows.query.all()), 0)

            # create and confirm following instance
            resp = c.post(f"/users/follow/{user2.id}", follow_redirects=True)
            self.assertEqual(len(Follows.query.all()), 1)

            resp = c.post(f"/users/stop-following/{user2.id}", follow_redirects=True)
            self.assertEqual(len(Follows.query.all()), 0)

            html = resp.get_data(as_text=True)
            self.assertNotIn('You must be logged in to access this page', html)


    def test_unfollow_user_logged_out(self):
        """Is a user prohibited from unfollowing another user when logged out?"""
         
        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2 = User.query.filter(User.email == "test2@test.com").all()[0]

        user1.following.append(user2)
        db.session.commit()

        self.assertEqual(len(Follows.query.all()), 1)

        resp = self.client.post(f"/users/stop-following/{user2.id}", follow_redirects=True)
        self.assertEqual(len(Follows.query.all()), 1)

        html = resp.get_data(as_text=True)
        self.assertIn('You must be logged in to access this page', html)

    
    def test_like_message_logged_in(self):
        """Can a user like another user's message when logged in?"""

        user2_message = Message.query.all()[1]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            self.assertEqual(len(Likes.query.all()), 0)

            resp = c.post(f"/users/add_like/{user2_message.id}", follow_redirects=True)

            self.assertEqual(len(Likes.query.all()), 1)
            message_like = Likes.query.all()[0]

            self.assertEqual(message_like.user_id, self.testuser1.id)
            self.assertEqual(message_like.message_id, user2_message.id)

            html = resp.get_data(as_text=True)
            self.assertNotIn('You must be logged in to access this page', html)


    def test_like_message_logged_out(self):   
        """Is a user prohibited from liking another user's message when logged out?"""

        user2_message = Message.query.all()[1]

        self.assertEqual(len(Likes.query.all()), 0)

        resp = self.client.post(f"/users/add_like/{user2_message.id}", follow_redirects=True)
        self.assertEqual(len(Likes.query.all()), 0)

        html = resp.get_data(as_text=True)
        self.assertIn('You must be logged in to access this page', html)


    def test_unlike_message_logged_in(self): 
        """Can a user unlike another user's message when logged in?"""

        user2_message = Message.query.all()[1]

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            self.assertEqual(len(Likes.query.all()), 0)

            # create and confirm message like
            resp = c.post(f"/users/add_like/{user2_message.id}", follow_redirects=True)
            self.assertEqual(len(Likes.query.all()), 1)

            resp = c.post(f"/users/remove_like/{user2_message.id}", follow_redirects=True)
            self.assertEqual(len(Likes.query.all()), 0)

            html = resp.get_data(as_text=True)
            self.assertNotIn('You must be logged in to access this page', html)
    
    def test_unlike_message_logged_out(self): 
        """Is a user prohibited from unliking another user's message when logged out?"""

        user1 = User.query.filter(User.email == "test1@test.com").all()[0]
        user2_message = Message.query.all()[1]

        user1.likes.append(user2_message)
        db.session.commit()

        self.assertEqual(len(Likes.query.all()), 1)

        resp = self.client.post(f"/users/remove_like/{user2_message.id}", follow_redirects=True)
        self.assertEqual(len(Likes.query.all()), 1)

        html = resp.get_data(as_text=True)
        self.assertIn('You must be logged in to access this page', html)
