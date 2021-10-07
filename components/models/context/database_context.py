from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///packets.sqlite', echo =True)
# Base.metadata.create_all(bind=engine)  # here

Session = sessionmaker(bind=engine)
session = Session()
