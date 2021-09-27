
import json
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import and_
from src.migrate.track import Track
from src.migrate.detection import Detection
from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict


def create_or_update(data,log):
    try:
        tracking = db.session.query(Track).filter(and_(Track.video_id == data['video_id'],Track.tracking_number == data['tracking_number'])).first()
        if tracking:
            tracking.end_time = data['end_time']
            tracking.updated_time = datetime.now()
            db.session.commit()
            return tracking
        tracking = Track(data['video_id'],data['vehicle_id'],data['tracking_number']
                            ,data['start_time'],data['end_time'])
        tracking.add(log)
        return tracking
    except  SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return None
    except  Exception as e :
        db.session.close()
        log.error(e)
        return None

def get_tracking_list_by_device(device_id,log):
    try:
        data = db.session.query(Track).filter(Track.device_id == device_id).all()
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

def get_detect_result_by_tracking(tracking_id,log):
    try:
        data = db.session.query(Detection).filter(Track.id == tracking_id
                                                    ).join(Track,Detection.tracking_id == Track.id).all()
        db.session.close()
        res_dict = row2dict(data)
        log.info("data return: {}".format(res_dict))
        return DataReponse(data = res_dict)
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)