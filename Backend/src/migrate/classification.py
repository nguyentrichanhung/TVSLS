from src import db

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import datetime
from sqlalchemy.sql import func
import uuid


class Classification(db.Model):
    __tablename__ = 'Classification'

    id = db.Column(db.String(50), unique = True,primary_key = True,nullable = False)
    tracking_id = db.Column(db.String(50),db.ForeignKey('Tracks.id',ondelete='cascade'),nullable = False)
    meta_data = db.Column(db.JSON,nullable = False)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,tracking_id,meta_data):
        self.id = str(uuid.uuid4())
        self.tracking_id = tracking_id
        self.meta_data = meta_data  

    def __repr__(self):
        return f"{self.tracking_id}:{self.meta_data}"

    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            return None
        return self

    def update(self,classify_id,tracking_id,meta_data,log):
        try:
            classify = Classification.query.filter_by(Classification.id ==classify_id).first()
            classify.tracking_id = tracking_id
            classify.meta_data = meta_data
            classify.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  

    def get_by_id(self,id,log):
        try:
            classify = Classification.query.filter_by(Classification.id ==id).first()
            if classify is not None:
                return classify
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,classify_id,log):
        try:
            classify = Classification.query.filter_by(id=classify_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None