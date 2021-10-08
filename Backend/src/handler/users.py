import json
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import and_
from src.migrate.users import User
from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict
from  werkzeug.security import generate_password_hash
from src.util.auth import *

def get_user_by_id(id,log):
    try:
        data = db.session.query(User).filter(User.id == id).first()
        db.session.close()
        res_dict = row2dict(data)
        if not res_dict:
            return DataReponse(message='User does not exist !!',code = CODE_EMPTY)
        return DataReponse(data = res_dict,message='Successful')
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)   

def get_user_by_name(name,log):
    try:
        data = db.session.query(User).filter(User.name == name).first()
        db.session.close()
        res_dict = row2dict(data)
        if not res_dict:
            return DataReponse(message='User does not exist !!',code = CODE_EMPTY)
        return DataReponse(data = res_dict,message='Successful')
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)


def add_new_user(name,password,role,log):
    try:
        if role not in [ADMIN_ROLE,OFFICER_ROLE,NORMAL_ROLE]:
            return DataReponse(message= 'role not valid',code = CODE_FAIL)
        ok, msg = validate_password(password,log)
        if not ok:
            return DataReponse(message= msg,code = CODE_FAIL)
        user = User(name,password,role)
        user.add(log)
        return DataReponse(message= 'Insert successfully!',code = CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)


def update_user_role(user_id,name,log):
    try:
        user = db.session.query(User).filter(User.id == user_id).first()
        if user:
            user.role = name
            user.updated_at = datetime.datetime.now()
            db.session.commit()
            return DataReponse(message= 'Update successfully!',code = CODE_DONE)
        return DataReponse(message= 'User not exist!',code = CODE_EMPTY)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def update_user_password(user_id,password,log):
    try:
        user = db.session.query(User).filter(User.id == user_id).first()
        if user:
            user.password = generate_password_hash(password)
            user.updated_at = datetime.datetime.now()
            db.session.commit()
            return DataReponse(message= 'Update successfully!',code = CODE_DONE)
        return DataReponse(message= 'User not exist!',code = CODE_EMPTY)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)       
def delete_user_by_name(name,log):
    try:
        db.session.query(User).filter(User.name == name).delete()
        db.session.commit()
        return DataReponse(message= 'Delete successfully!',code = CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def get_users(log):
    try:
        data = db.session.query(User).first()
        db.session.close()
        res_dict = row2dict(data)
        return DataReponse(data = res_dict,message='Successful')
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)     