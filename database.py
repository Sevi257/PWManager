from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from flask_sqlalchemy import SQLAlchemy

engine = create_engine(f'sqlite:///C:/Users/sevi1/PycharmProjects/pythonProject3/tmp/test.db')
db = SQLAlchemy()
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

