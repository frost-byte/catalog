from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///catalog.db")

DBSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

session = scoped_session(DBSession)

Base = declarative_base()
Base.query = session.query_property()

def init_db():

    from models import Category, Item, User
    Base.metadata.create_all(bind=engine)
