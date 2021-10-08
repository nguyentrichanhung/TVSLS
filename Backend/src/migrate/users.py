from src import db

import datetime
import  uuid
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.sql import func
from  werkzeug.security import generate_password_hash
class User(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.String(50), unique = True,primary_key = True,nullable = False)
    status = db.Column(db.String(50),nullable=True)
    name = db.Column(db.String(50),nullable = False,unique = True)
    hash_password = db.Column(db.String(200),nullable = False)
    role = db.Column(db.String(50),nullable = False,unique = False)
    created_at = db.Column(db.DateTime(),default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.now())
    deleted_at = db.Column(db.DateTime(), default=None,nullable = True)

    def __init__(self,name,hash_password,role):
        self.id = str(uuid.uuid4())
        self.name = name
        self.hash_password = generate_password_hash(hash_password)
        self.role = role
        # self.stream_url = stream_url

    def __repr__(self):
        return f"{self.name}:{self.role}"

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

    def update(self,user_id,status,name,hash_password,role,log):
        try:
            user = User.query.filter_by(User.id ==user_id).first()
            user.name = name
            user.status = status
            user.hash_password = hash_password
            user.role = role
            user.updated_at = datetime.datetime.now()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        finally:
            db.session.close()

    def get_by_id(self,id,log):
        try:
            user = User.query.filter_by(User.id ==id).first()
            if user is not None:
                return user
        except SQLAlchemyError as e:
            log.error(e)
            return None

    def delete(self,user_id,log):
        try:
            User.query.filter_by(id=user_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            log.error(e)
            return None
        return None       