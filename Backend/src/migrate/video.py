from src import db

import datetime
import uuid
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func


class Video(db.Model):
    __tablename__ = 'Videos'
    id = db.Column(db.String(50), unique = True,primary_key = True,nullable = False)
    device_id = db.Column(db.String(50),db.ForeignKey('Devices.id',ondelete='cascade'),nullable = False)
    video_path = db.Column(db.String(200),nullable = False,unique = True)
    start_time = db.Column(db.DateTime(),nullable = False)
    end_time = db.Column(db.DateTime(),nullable = True)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,device_id,video_path,start_time,end_time):
        self.id = str(uuid.uuid4())
        self.device_id = device_id
        self.video_path = video_path
        self.start_time = start_time
        self.end_time = end_time

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

    def update(self,video_id,video_path,start_time,end_time,log):
        try:
            video = Video.query.filter_by(Video.id ==video_id).first()
            video.video_path = video_path
            video.start_time = start_time
            video.end_time = end_time
            video.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None

    def get_by_id(self,id,log):
        try:
            recog = Video.query.filter_by(Video.id ==id).first()
            if recog is not None:
                return recog
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,video_id,log):
        try:
            Video.query.filter_by(id=video_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None  