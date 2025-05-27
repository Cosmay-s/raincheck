from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class City(Base):
    __tablename__ = "city"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    search_count: Mapped[int] = mapped_column(default=-1, nullable=False)

    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='uix_lat_lon'),
    )