"""Utility to create DB tables (development only).

Run this once to initialize the local SQLite DB schema when not
using migrations.
"""
from db import engine
from models import Base


def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done")


if __name__ == '__main__':
    main()
