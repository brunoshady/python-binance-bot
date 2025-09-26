from typing import Generic, TypeVar, Type, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, InstrumentedAttribute

from src.database import Base, engine

Base.metadata.create_all(bind=engine)

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def add(self, instance: T) -> T:
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def update(self, instance: T) -> T:
        merged = self.session.merge(instance)
        self.session.commit()
        self.session.refresh(merged)
        return merged

    def select_first_by_filter(self, **filters) -> Optional[T]:
        return self.session.query(self.model).filter_by(**filters).first()

    def select_all_by_filter(self, **filters) -> Optional[List[T]]:
        return self.session.query(self.model).filter_by(**filters).all()
