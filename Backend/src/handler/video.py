from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.migrate.video import Video
from src.migrate.track import Track
from src.migrate.device import Device
from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict

def search_video_by_id(video_id,log):
    try:
        data = db.session.query(Video).filter(Video.id == video_id).first()
        # log.info("data return: {}".format(data))
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

def get_list_video_by_device_id(device_id,log):
    try:
        data = db.session.query(Video).join(Track,Video.id == Track.video_id
                                                        ).join(Device,and_(Track.device_id == Device.id,Device.id == device_id)).all()
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

def get_video_by_tracking_id(tracking_id,log):
    try:
        data = db.session.query(Video).join(Track,and_(Video.id == Track.video_id,Track.id == tracking_id)).first()
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
