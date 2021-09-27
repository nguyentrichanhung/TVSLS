from src import db
from src.util.generate_random import generate_random
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import datetime
from sqlalchemy.sql import func

class Detection(db.Model):
    __tablename__ = 'Detection'

    id = db.Column(db.String(24), unique = True,primary_key = True,nullable = False)
    tracking_id = db.Column(db.String(24),db.ForeignKey('Tracks.id',ondelete='cascade'),nullable = False)
    type = db.Column(db.String(20),nullable = False)
    full_image = db.Column(db.String(200),nullable = False)
    bounding_box = db.Column(db.JSON,nullable = False)
    event_time = db.Column(db.DateTime(), nullable = False)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,tracking_id,type,full_image,bounding_box,event_time):
        self.id = generate_random(24)
        self.tracking_id = tracking_id
        self.type = type
        self.full_image = full_image
        self.bounding_box =  bounding_box
        self.event_time = event_time

    def __repr__(self):
        return f"{self.tracking_id}:{self.bounding_box}"

    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
        finally:
            db.session.close()
        

    def update(self,detect_id,tracking_id,type,full_image,bounding_box,log):
        try:
            detect = Detection.query.filter_by(Detection.id ==detect_id).first()
            detect.tracking_id = tracking_id
            detect.type = type
            detect.full_image = full_image
            detect.bounding_box = bounding_box
            detect.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        finally:
            db.session.expunge_all()
            db.session.close()

    def get_by_id(self,id,log):
        try:
            detect = Detection.query.filter_by(Detection.id ==id).first()
            if detect is not None:
                return detect
        except SQLAlchemyError as e:
            log.error(e)
            return None
        finally:
            db.session.expunge_all()
            db.session.close()
    def delete(self,detect_id,log):
        try:
            classify = Detection.query.filter_by(id=detect_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        finally:
            db.session.expunge_all()
            db.session.close()
        