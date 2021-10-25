from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.migrate.violate import Violate
from src.migrate.violate_manage import Violate_Manager
from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict

def search_violate_by_vehicle_id(vehicle_id,log):
    try:
        data = db.session.query(Violate).join(Violate_Manager, Violate.id == Violate_Manager.violate_id).where(Violate_Manager.vehicle_id == vehicle_id).all()
        db.session.close()
        res_dict = row2dict(data)
        return DataReponse(data = res_dict)
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def add_new_violate(violate,log):
    try:
        violate = Violate(violate['type'])
        violate.add(log)
        return DataReponse(message= 'Insert successfully!',data=violate.id,code = CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def modify_violate(violate,log):
    try:
        violate = db.session.query(Violate).filter(Violate.id == violate['id']).first()
        if violate:
            violate.type = violate['type']
            violate.updated_at = datetime.now()
            db.session.commit()
            return DataReponse(message= 'Update successfully!',code = CODE_DONE)
        return DataReponse(message= 'Violate not exist!',code = CODE_EMPTY)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

