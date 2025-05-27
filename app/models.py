from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)


class SearchCount(Base):
    __tablename__ = "search_counts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    city_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
