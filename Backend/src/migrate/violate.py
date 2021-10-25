from src import db

import datetime
import uuid
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func
class Violate(db.Model):
    __tablename__ = 'Violates'

    id = db.Column(db.String(50), unique = True,primary_key = True,nullable = False)
    type = db.Column(db.String(100),nullable=False,unique = True)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,type):
        self.id = str(uuid.uuid4())
        self.type = type

    def __repr__(self):
        return f"{self.type}"

    @classmethod
    def find_by_id(cls,id):
        return Violate.query.filter(Violate.id == id).first()
    
    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            return None
        finally:
            db.session.expunge_all()
            db.session.close()
        

    def update(self,violate_id,type,log):
        try:
            violate = Violate.query.filter_by(Violate.id ==violate_id).first()
            violate.type = type
            violate.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            violate = Violate.query.filter_by(Violate.id ==id).first()
            if violate is not None:
                return violate
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,violate_id,log):
        try:
            violate = Violate.query.filter_by(id=violate_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  