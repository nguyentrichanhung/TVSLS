from src import db
from src.util.generate_random import generate_random
import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func

class Recognize(db.Model):
    __tablename__ = 'Recognize'

    id = db.Column(db.String(24), unique = True,primary_key = True,nullable = False)
    tracking_id = db.Column(db.String(24),db.ForeignKey('Tracks.id',ondelete='cascade'),nullable = False)
    lisence_pate = db.Column(db.String(20),nullable = True,unique = False)
    crop_image = db.Column(db.String(120),nullable = False,unique = True)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,tracking_id,lisence_pate,crop_image):
        self.id = generate_random(24)
        self.tracking_id = tracking_id
        self.lisence_pate = lisence_pate
        self.crop_image = crop_image

    def __repr__(self):
        return f"{self.tracking_id}:{self.lisence_pate}"


    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            return None
        return self

    def update(self,recognize_id,lisence_pate,log):
        try:
            recog = Recognize.query.filter_by(Recognize.id ==recognize_id).first()
            recog.lisence_pate = lisence_pate
            recog.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            recog = Recognize.query.filter_by(Recognize.id ==id).first()
            if recog is not None:
                return recog
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,detect_id,log):
        try:
            recog = Recognize.query.filter_by(id=detect_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  