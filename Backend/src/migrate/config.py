from src import db
from src.util.generate_random import generate_random
import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func

class Config(db.Model):
    __tablename__ = 'Configs'
    id = db.Column(db.String(24), unique = True,primary_key = True,nullable = False)
    device_id = db.Column(db.String(24),db.ForeignKey('Devices.id',ondelete='cascade'),nullable = False)
    config_data = db.Column(db.JSON,nullable = False)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,device_id,config_data):
        self.id = generate_random(24)
        self.device_id = device_id
        self.config_data = config_data

    def __repr__(self):
        return f"{self.id}:{self.config_data}"


    def add(self,log):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            return None
        return self

    def update(self,config_id,device_id,config_data,log):
        try:
            config = Config.query.filter_by(Config.id ==config_id).first()
            config.device_id = device_id
            config.config_data = config_data
            config.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            recog = Config.query.filter_by(Config.id ==id).first()
            if recog is not None:
                return recog
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,config_id,log):
        try:
            Config.query.filter_by(id=config_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  