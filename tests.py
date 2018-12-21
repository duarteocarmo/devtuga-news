from datetime import datetime
import unittest
from app import create_app, db
from app.models import User, Post, Comment
from config import Config
from flask import current_app
from flask_login import login_user, logout_user, current_user, LoginManager


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    ELASTICSEARCH_URL = None
    LOGIN_DISABLED = "True"


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        lm = LoginManager()
        lm.init_app(self.app)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username="susan")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))

    def test_user_admin(self):
        admin_email = current_app.config["MAIL_ADMIN_ADDRESS"]
        admin_user = User(username="admin", email=admin_email)
        self.assertTrue(admin_user.is_admin())

    def test_user_login(self):
        u = User(username="susan")
        with self.app.test_request_context():
            result = login_user(u)
            self.assertTrue(result)

    def test_user_logout(self):
        u = User(username="susan")
        with self.app.test_request_context():
            login_user(u)
            logout_user()
            self.assertTrue(current_user.is_anonymous)


class PostModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_post_ownership(self):
        u = User(username="susan")
        p = Post(
            title="Test title",
            text="lorem ipsum",
            author=u,
            timestamp=datetime.utcnow(),
        )
        db.session.add_all([u, p])
        db.session.commit()
        self.assertEqual(p.author, u)

    def test_post_formatting(self):
        p = Post(
            title="Test title",
            url="http://flask.pocoo.org/docs/1.0/testing/",
            timestamp=datetime.utcnow(),
        )
        p.format_post(p.url)
        db.session.add(p)
        db.session.commit()
        self.assertEqual(p.url_base, "flask.pocoo.org")

    def test_post_upvote_score(self):
        u = User(username="susan")
        p = Post(
            title="Test title",
            text="lorem ipsum",
            author=u,
            timestamp=datetime.utcnow(),
        )
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        p.update_votes()
        self.assertEqual(p.score, 1)

    def test_post_delete(self):
        p = Post(
            title="Test title", text="lorem ipsum", timestamp=datetime.utcnow()
        )
        db.session.add(p)
        db.session.commit()
        p.delete_post()
        self.assertEqual(p.deleted, 1)

    def test_post_upvote_karma(self):
        u = User(username="susan")
        p = Post(
            title="Test title",
            text="lorem ipsum",
            author=u,
            timestamp=datetime.utcnow(),
        )
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        p.update_votes()
        self.assertEqual(u.karma, 2)

    def test_post_total_comments(self):
        u1 = User(username="susan")
        u2 = User(username="john")
        p = Post(title="Test Title", text="This is a test")
        db.session.add_all([u1, u2, p])
        db.session.commit()
        c1 = Comment(
            text="First Comment",
            author=u1,
            post_id=p.id,
            timestamp=datetime.utcnow(),
            thread_timestamp=datetime.utcnow(),
        )
        c2 = Comment(
            text="Second Comment",
            author=u2,
            post_id=p.id,
            timestamp=datetime.utcnow(),
            thread_timestamp=datetime.utcnow(),
        )
        c1.save()
        c2.save()
        self.assertEqual(p.total_comments(), 2)


class MainRoutesTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_view(self):
        client = self.app.test_client()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_newest_view(self):
        client = self.app.test_client()
        response = client.get("/newest")
        self.assertEqual(response.status_code, 200)

    def test_about_view(self):
        client = self.app.test_client()
        response = client.get("/sobre")
        self.assertEqual(response.status_code, 200)

    def test_submit_view(self):
        client = self.app.test_client()
        response = client.get("/submit")
        self.assertEqual(response.status_code, 200)

    def test_post_page(self):
        p = Post(
            title="Test Title", text="Lorem ipsum", timestamp=datetime.utcnow()
        )
        db.session.add(p)
        db.session.commit()
        client = self.app.test_client()
        response = client.get(f"/post/{p.id}")
        self.assertEqual(response.status_code, 200)

    def test_user_page(self):
        u = User(username="john", email="john@example.com")
        db.session.add(u)
        db.session.commit()
        client = self.app.test_client()
        response = client.get(f"/user/{u.username}")
        self.assertEqual(response.status_code, 200)

    def test_submissions_page(self):
        u = User(username="john", email="john@example.com")
        db.session.add(u)
        db.session.commit()
        client = self.app.test_client()
        response = client.get(f"/submissions/{u.username}")
        self.assertEqual(response.status_code, 200)


class ErrorRoutesTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_view(self):
        client = self.app.test_client()
        response = client.get("-.-.-.")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
