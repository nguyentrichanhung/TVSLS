from src import db
import datetime

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func

class Violate_Manager(db.Model):
    __tablename__ = 'violate_management'

    id = db.Column(db.Integer, unique = True,primary_key = True,nullable = False,autoincrement = True)
    violate_id = db.Column(db.String(50),db.ForeignKey('Violates.id',ondelete='cascade'),nullable = True)
    vehicle_id = db.Column(db.String(50),db.ForeignKey('Vehicles.id',ondelete='cascade'),nullable = True)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,violate_id,vehicle_id):
        self.violate_id = violate_id
        self.vehicle_id = vehicle_id

    def __repr__(self):
        return f"{self.violate_id}:{self.vehicle_id}"

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
            manager = Violate_Manager.query.filter_by(Violate_Manager.id ==manage_id).first()
            manager.vehicle_id = vehicle_id
            manager.violate_id = devide_id
            manager.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            manager = Violate_Manager.query.filter_by(Violate_Manager.id ==id).first()
            if manager is not None:
                return manager
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,detect_id,log):
        try:
            manager = Violate_Manager.query.filter_by(id=detect_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None       