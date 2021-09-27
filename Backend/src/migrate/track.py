from src import db
from src.util.generate_random import generate_random
import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func

class Track(db.Model):
    __tablename__ = 'Tracks'

    id = db.Column(db.String(24), unique = True,primary_key = True,nullable = False)
    video_id = db.Column(db.String(24),db.ForeignKey('Videos.id',ondelete='cascade'),nullable = True)
    vehicle_id = db.Column(db.String(24),db.ForeignKey('Vehicles.id',ondelete='cascade'),nullable = True)
    tracking_number = db.Column(db.Integer,nullable = False,unique = False)
    start_time = db.Column(db.DateTime(),nullable = False)
    end_time = db.Column(db.DateTime(),nullable = False)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,video_id,vehicle_id,tracking_number,start_time,end_time):
        self.id = generate_random(24)
        self.video_id = video_id
        self.vehicle_id = vehicle_id
        self.tracking_number = tracking_number
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"{self.video_id}:{self.vehicle_id}"


    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            return None
        return self

    def update(self,tracking_id,tracking_number,video_id,vehicle_id,start_time,end_time,log):
        try:
            tracking = Track.query.filter_by(Track.id ==tracking_id).first()
            tracking.tracking_number = tracking_number
            tracking.video_id = video_id
            tracking.vehicle_id = vehicle_id
            tracking.start_time = start_time
            tracking.end_time = end_time
            tracking.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            tracking = Track.query.filter_by(Track.id ==id).first()
            if tracking is not None:
                return tracking
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,tracking_id,log):
        try:
            Track.query.filter_by(id=tracking_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  