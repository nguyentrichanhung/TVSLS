from src import db

import datetime
import  uuid
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func

class DeviceManager(db.Model):
    __tablename__ = 'device_managers'

    id = db.Column(db.String(50), unique = True,primary_key = True,nullable = False)
    user_id = db.Column(db.String(50),db.ForeignKey('Users.id',ondelete='cascade'),nullable = True)
    device_id = db.Column(db.String(50),db.ForeignKey('Devices.id',ondelete='cascade'),nullable = True)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,user_id,device_id):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.device_id = device_id
        # self.stream_url = stream_url

    def __repr__(self):
        return f"{self.user_id}:{self.device_id}"

    def add(self,log):
        message = ''
        try:
            
            db.session.add(self)
            db.session.commit()

        except  IntegrityError as e:
            log.error(e)
            message = 'The device {self.device_code} already exists!!!'
            return message
        except SQLAlchemyError as e:
            log.error(e)
            
            db.session.rollback()
            return None
        finally:
            # db.session.expunge_all()
            # db.session.close()    
            return self 

    def update(self,dm_id,user_id,device_id,log):
        try:
            dm = DeviceManager.query.filter_by(DeviceManager.id ==dm_id).first()
            dm.user_id = user_id
            dm.device_id = device_id
            dm.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        finally:
            db.session.close()

    def get_by_id(self,id,log):
        try:
            dm = DeviceManager.query.filter_by(DeviceManager.id ==id).first()
            if dm is not None:
                return dm
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,dm_id,log):
        try:
            DeviceManager.query.filter_by(id=dm_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None       