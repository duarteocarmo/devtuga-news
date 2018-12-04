from datetime import datetime
from urllib.parse import urlparse
from time import time
import jwt

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login
from flask import current_app


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    about_me = db.Column(db.String(140))
    karma = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except Exception:
            return
        return User.query.get(id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_post(self):
        if (
            len(
                Post.query.filter(
                    Post.timestamp
                    >= datetime.strftime(datetime.now(), "%Y-%m-%d")
                )
                .filter_by(author=self, deleted=0)
                .all()
            )
            > current_app.config["USER_POSTS_PER_DAY"]
        ):
            return False
        else:
            return True

    def can_comment(self):
        if (
            len(
                Comment.query.filter(
                    Comment.timestamp
                    >= datetime.strftime(datetime.now(), "%Y-%m-%d")
                )
                .filter_by(author=self)
                .all()
            )
            > current_app.config["USER_COMMENTS_PER_DAY"]
        ):
            return False
        else:
            return True

    def __repr__(self):
        return f"<User {self.username}>"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    url = db.Column(db.String(120))
    url_base = db.Column(db.String(50))
    text = db.Column(db.String(280))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    score = db.Column(db.Integer, default=0)
    pop_score = db.Column(db.Float, default=0)
    deleted = db.Column(db.Integer, default=0)

    def format_post(self, url):
        if url is not None:
            parsed_uri = urlparse(url)
            self.url_base = "{uri.netloc}".format(uri=parsed_uri)
        else:
            self.url_base = None

        if str(url).endswith(".pdf"):
            self.title += " [pdf]"

    def delete_post(self):
        self.deleted = 1

    def update_votes(self):
        self.score += 1
        self.author.karma += 1

    def total_comments(self):
        return len(Comment.query.filter_by(post_id=self.id).all())

    def update(self, gravity=1.8):
        datetime_difference = datetime.utcnow() - self.timestamp
        hours_passed = (
            datetime_difference.days * 24 + datetime_difference.seconds / 3600
        )
        self.pop_score = (self.score - 1) / pow((hours_passed + 2), gravity)

    def __repr__(self):
        return f"<Post {self.title}>"


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

    def __repr__(self):
        return f"<User: {self.user_id} Post: {self.post_id}>"


class Comment_Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"))

    def __repr__(self):
        return f"<User: {self.user_id} Post: {self.comment_id}>"


class Comment(db.Model):
    _N = 6

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    path = db.Column(db.String(60), index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    replies = db.relationship(
        "Comment",
        backref=db.backref("parent", remote_side=[id]),
        lazy="dynamic",
    )
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    thread_timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow()
    )
    score = db.Column(db.Integer, default=0)
    thread_score = db.Column(db.Integer, default=0)

    def update_votes(self):
        self.score += 1
        if self.parent_id is None:
            self.thread_score = self.score
            for child_comment in Comment.query.filter(
                Comment.path.like(self.path + "%")
            ):
                child_comment.thread_score = self.thread_score
                db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + "." if self.parent else ""
        self.path = prefix + "{:0{}d}".format(self.id, self._N)
        db.session.commit()

    def level(self):
        return len(self.path) // self._N - 1

    def __repr__(self):
        return (
            f"<Comment: {self.text} Post: {self.post_id} User: {self.user_id}>"
        )
