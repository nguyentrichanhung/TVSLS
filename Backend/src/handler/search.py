from src.migrate.track import Track
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.migrate.detection import Detection
from src.migrate.device import Device
from src.migrate.vehicle import Vehicle
from src.migrate.video import Video
from src.migrate.vehicle_management import VM
from src.migrate.classification import  Classification
from src.migrate.recognize import  Recognize
from src.migrate.track import Track
from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict


def search_by_time(start_time,end_time,log):
    try:
        data = []
        track = db.session.query(Track).filter(Track.created_at.between(start_time,end_time)).all()
        db.session.close()
        track_dict = row2dict(track)
        for i in track_dict:
            response = {
                'timestamp' : {},
                'license_plate' : '',
                'vehicle_type' : '',
                'meta_data' : {},
                'device_id' : None,
                'tracking_res': [],
                'license_plate_image' : [],
                'video_path' : ""
                
            }
            device = db.session.query(Device.id,Device.region).join(Video, Video.device_id == Device.id).where(Video.id == i['video_id']).first()
            # log.info(device)
            if device:
                response['device_id'] = device[0]
                response['region'] = device[1]
            else:
                response['device_id'] = None
                response['region']  = ''
            response['timestamp'] = {
                "start_time" : i['start_time'],
                "end_time" : i['end_time']
            }
            video =  db.session.query(Video.video_path).filter(Video.id == i['video_id']).first()
            response['video_path'] = video[0]
            track_res = db.session.query(Detection.full_image,Detection.type).where(Detection.tracking_id == i['id']).all()
            for t in track_res:
                response['tracking_res'].append({
                    'detect_type' : t[1],
                    'detect_img' : t[0]
                })
        
            classify = db.session.query(Classification.meta_data).filter(Classification.tracking_id == i['id']).first()
            response['meta_data'] = classify[0]
            recognize = db.session.query(Recognize.crop_image).filter(Recognize.tracking_id == i['id']).all()
            response['license_plate_image'] = [r[0] for r in recognize]
            data.append(response)
        return DataReponse(data = data)
    except  SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def search_vehicle_by_id(device_id,log):
    try:
        data = db.session.query(Vehicle,Device,Detection).filter(Vehicle.device_id == Device.id
                                                         ).filter(Device.id == device_id)
        db.session.close()
        return DataReponse(data = data)
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

