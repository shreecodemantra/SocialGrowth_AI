"""
Declarative base for all ORM models.

`app/db/base_all.py` imports every model module so Alembic's autogenerate
can discover them via this Base's metadata. Individual model modules should
import `Base` from here, not create their own.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
