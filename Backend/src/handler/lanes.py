from src import db
from src.migrate.lane_properties import LaneProperty
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict

import  datetime

def creates(data,device_id,log):
    try:
        if len(data) == 0:
            return DataReponse(message= 'Invalid lane properties',code = CODE_EMPTY)
        lane_lst = []
        for k,v in data.items():
            lane_lst.append(LaneProperty(device_id,v['name'],v['vehicle_properties'],v['direction'],v['points']))
        db.session.add_all(lane_lst)
        db.session.commit()
        return DataReponse(message= 'Insert successfully!',code = CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def get_config_lst(log):
    try:
        data = db.session.query(LaneProperty).all()
        db.session.close()
        res_dict = row2dict(data)
        if len(res_dict) == 0:
            return DataReponse(data = None,message='Config not setup yet!!',code = CODE_EMPTY)
        return DataReponse(data = res_dict,message='Successful')
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def updates(data,device_id,log):
    try:
        if len(data) == 0:
            return DataReponse(message= 'Invalid update info',code = CODE_EMPTY)
        for k,v in data.items():
            lane = db.session.query(LaneProperty).filter(LaneProperty.id ==k).first()
            if lane is None:
                return DataReponse(message= 'Not found lane information with id: {}'.format(k),code = CODE_EMPTY)
            lane.device_id = device_id
            lane.name = v['name']
            lane.vehicle_properties = v['vehicle_properties']
            lane.direction = v['direction']
            lane.points = v['points']
            lane.updated_at = datetime.datetime.now()
            db.session.commit()
        return DataReponse(message= 'Update successfully!',data=lane,code = CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def delete(lane_id,log):
    try:
        lane = db.session.query(LaneProperty).filter_by(LaneProperty.id == lane_id).first()
        if lane :
            db.session.delete(lane)
            db.session.commit()
            return DataReponse(message= 'Delete successfully',code = CODE_DONE)
        return DataReponse(message= 'Invalid lane id',code = CODE_EMPTY)
    except  SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)       