from src import db
from src.util.generate_random import generate_random
import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func
class Vehicle(db.Model):
    __tablename__ = 'Vehicles'

    id = db.Column(db.String(24), unique = True,primary_key = True,nullable = False)
    license_plate = db.Column(db.String(30),nullable=False,unique = True)
    type = db.Column(db.String(100), nullable= False,unique = False)
    status = db.Column(db.String(100),nullable = False)
    violation_type = db.Column(db.String(100),nullable=False,unique = False)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,license_plate,type,status,violation_type):
        self.id = generate_random(24)
        self.license_plate = license_plate
        self.type = type
        self.status = status
        self.violation_type = violation_type

    def __repr__(self):
        return f"{self.vehicle_owner}"

    @classmethod
    def find_by_id(cls,id):
        return Vehicle.query.filter(Vehicle.id == id).first()
    
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
        

    def update(self,vehicle_id,license_plate,type,status,violation_type,log):
        try:
            vehicle = Vehicle.query.filter_by(Vehicle.id ==vehicle_id).first()
            vehicle.license_plate = license_plate
            vehicle.type = type
            vehicle.status = status
            vehicle.violation_type = violation_type
            vehicle.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            vehicle = Vehicle.query.filter_by(Vehicle.id ==id).first()
            if vehicle is not None:
                return vehicle
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,detect_id,log):
        try:
            vehicle = Vehicle.query.filter_by(id=detect_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  