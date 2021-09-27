from src import db
import datetime
from src.util.generate_random import generate_random
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func

class VM(db.Model):
    __tablename__ = 'vehicle_management'

    id = db.Column(db.Integer, unique = True,primary_key = True,nullable = False,autoincrement = True)
    device_id = db.Column(db.String(24),db.ForeignKey('Devices.id',ondelete='cascade'),nullable = True)
    vehicle_id = db.Column(db.String(24),db.ForeignKey('Vehicles.id',ondelete='cascade'),nullable = True)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,device_id,vehicle_id):
        self.device_id = device_id
        self.vehicle_id = vehicle_id

    def __repr__(self):
        return f"{self.device_id}:{self.vehicle_id}"

    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            return None
        return self

    def update(self,manage_id,vehicle_id,devide_id,log):
        try:
            manager = VM.query.filter_by(VM.id ==manage_id).first()
            manager.vehicle_id = vehicle_id
            manager.device_id = devide_id
            manager.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            manager = VM.query.filter_by(VM.id ==id).first()
            if manager is not None:
                return manager
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,detect_id,log):
        try:
            manager = VM.query.filter_by(id=detect_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None       