from src import db

import datetime
import uuid
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func


class LaneProperty(db.Model):
    __tablename__ = 'lane_properties'
    id = db.Column(db.String(50), unique = True,primary_key = True,nullable = False)
    device_id = db.Column(db.String(50),db.ForeignKey('Devices.id',ondelete='cascade'),nullable = False)
    name = db.Column(db.String(50),nullable = True)
    vehicle_properties = db.Column(db.JSON,nullable = False)
    direction = db.Column(db.String(10),nullable = False)
    points = db.Column(db.JSON,nullable = False)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,device_id,name,vehicle_properties,direction,points):
        self.id = str(uuid.uuid4())
        self.device_id = device_id
        self.name = name
        self.vehicle_properties = vehicle_properties
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

    def update(self,lane_id,device_id,name,vehicle_properties,direction,points,log):
        try:
            lane = LaneProperty.query.filter_by(LaneProperty.id ==lane_id).first()
            lane.device_id = device_id
            lane.name = name
            lane.vehicle_properties = vehicle_properties
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