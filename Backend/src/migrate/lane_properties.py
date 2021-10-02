from src import db
from src.util.generate_random import generate_random
import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func


class LaneProperty(db.Model):
    __tablename__ = 'lane_properties'
    id = db.Column(db.String(24), unique = True,primary_key = True,nullable = False)
    device_id = db.Column(db.String(24),db.ForeignKey('Devices.id',ondelete='cascade'),nullable = False)
    name = db.Column(db.String(50),nullable = True)
    vehicle_type = db.Column(db.JSON,nullable = False)
    speed_limit = db.Column(db.Integer,nullable = False)
    direction = db.Column(db.String(10),nullable = False)
    points = db.Column(db.JSON,nullable = False)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,device_id,name,vehicle_type,speed_limit,direction,points):
        self.id = generate_random(24)
        self.device_id = device_id
        self.name = name
        self.vehicle_type = vehicle_type
        self.speed_limit = speed_limit
        self.direction = direction
        self.points = points

    def __repr__(self):
        return f"{self.id}:{self.start_time}"


    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            return None
        return self

    def update(self,lane_id,device_id,name,vehicle_type,speed_limit,direction,points,log):
        try:
            lane = LaneProperty.query.filter_by(LaneProperty.id ==lane_id).first()
            lane.device_id = device_id
            lane.name = name
            lane.vehicle_type = vehicle_type
            lane.speed_limit = speed_limit
            lane.direction = direction
            lane.points = points
            lane.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            recog = LaneProperty.query.filter_by(LaneProperty.id ==id).first()
            if recog is not None:
                return recog
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,lane_id,log):
        try:
            LaneProperty.query.filter_by(id=lane_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  