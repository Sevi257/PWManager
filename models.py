import sqlalchemy.types
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class UserDB(Base, UserMixin):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(200), unique=False)
    salt = Column(String(200), unique=True)
    authenticated = Column(Boolean, unique=False, default=False)

    sites = relationship('Sites', backref='user', lazy=True)

    def __init__(self, email=None, password=None, salt=None):
        self.email = email
        self.password = password
        self.salt = salt

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return str(self.id)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Sites(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    website = Column(String(50), unique=False)
    username = Column(String(120), unique=False)
    password = Column(String(200), unique=False)
    salt = Column(String(200), unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, website=None, username=None, password=None, salt=None, user_id=None):
        self.website = website
        self.username = username
        self.password = password
        self.salt = salt
        self.user_id = user_id
