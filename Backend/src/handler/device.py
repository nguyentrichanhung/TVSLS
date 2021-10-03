from src import db
from src.migrate.device import Device
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict



def creates(device,log):
    try:
        device = Device(device['type'],device['name'],device['location'],device['region'],device['metadata'])
        device.add(log)
        return DataReponse(message= 'Insert successfully!',data=device.id,code = CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)


def get_device(device_id,log):
    try:
        device = db.session.query(Device).filter_by(Device.id == device_id).first()
        db.session.close()
        if not device:
            return DataReponse(message= 'Invalid device_id',code = CODE_EMPTY)
        res_dict = row2dict(device)
        return DataReponse(message = "Successful",data=res_dict,code=CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def edit_device(device_id,device_info,log):
    try:
        device = db.session.query(Device).filter_by(Device.id == device_id).first()
        db.session.close()
        if not device:
            return DataReponse(message= 'Invalid device_id',code = CODE_EMPTY)
        device.type = device_info['type']
        device.name = device_info['name']
        device.location  = device_info['location']
        device.region =device_info['region']
        device.metadata  =device_info['metadata']
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)
