from src import db

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import datetime
import uuid
from sqlalchemy.sql import func

class Device(db.Model):
    __tablename__ = 'Devices'

    id = db.Column(db.String(50), unique = True,primary_key = True,nullable = False)
    type = db.Column(db.String(50),nullable=True)
    name = db.Column(db.String(50),nullable = True)
    location = db.Column(db.JSON,nullable = False)
    region = db.Column(db.String(10),nullable = True)
    meta_data = db.Column(db.JSON,nullable = False)
    # stream_url = db.Column(db.String(100),nullable = False)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,type,name,location,region,meta_data):
        self.id = str(uuid.uuid4())
        self.type = type
        self.name = name
        self.region = region
        self.location = location
        self.meta_data = meta_data
        # self.stream_url = stream_url

    def __repr__(self):
        return f"{self.type}:{self.name}:{self.location}"

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

    def update(self,device_id,type,name,location,region,meta_data,log):
        try:
            devide = Device.query.filter_by(Device.id ==device_id).first()
            devide.type = type
            devide.name = name
            devide.location = location
            devide.region = region
            devide.meta_data = meta_data
            # devide.stream_url = stream_url
            devide.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        finally:
            db.session.close()

    def get_by_id(self,id,log):
        try:
            device = Device.query.filter_by(Device.id ==id).first()
            if device is not None:
                return device
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,detect_id,log):
        try:
            device = Device.query.filter_by(id=detect_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None       