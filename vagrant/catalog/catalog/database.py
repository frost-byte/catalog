'''
This is the database module for the Catalog app.
The module provides a method for initialzing the database connection/session.

Attributes:
    engine:     The SQLAlchemy connection to the app's database.

    DBSession:  The SQLAlchemy database session for making queries against
        the models and data conatined in the database.

    session:    Provides a scoped session of the above session.
    Base:       The Base class of each class in the Database Model. Uses the
    scoped session to provide the query property to each class that inherits
    from it.

    app:        The Flask App instance, provides the Database directive.
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker
)

from app import app

engine = create_engine(app.config['APP_DATABASE'])

DBSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

session = scoped_session(DBSession)

Base = declarative_base()
Base.query = session.query_property()


def init_db():
    '''Initialize the Database.'''
    # Generate the Database, if necessary, and connect to it.
    Base.metadata.create_all(bind=engine)
