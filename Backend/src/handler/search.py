from src.migrate.track import Track
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.migrate.detection import Detection
from src.migrate.device import Device
from src.migrate.vehicle import Vehicle
from src.migrate.video import Video
from src.migrate.vehicle_management import VM
from src.migrate.classification import  Classification
from src.migrate.recognize import  Recognize
from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict


def search_by_region(region,log):
    try:
        data = db.session.query(Vehicle,Device,Detection).filter(Detection.vehicle_id == Vehicle.id
                                                    ).filter(Vehicle.device_id == Device.id
                                                    ).filter(Device.region == region)
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

def search_by_time(start_time,end_time,log):
    try:
        data = []
        vehicle = db.session.query(Vehicle).filter(Vehicle.created_at.between(start_time,end_time)).all()
        db.session.close()
        vehicle_dict = row2dict(vehicle)
        for i in vehicle_dict:
            response = {
                'timestamp' : None,
                'license_plate' : '',
                'region' : '',
                'vehicle_type' : '',
                'meta_data' : {},
                'device_id' : None,
                'tracking_res': [],
                'vehicle_id': '',
                'license_plate_image' : [],
                'video_path' : []
                
            }
            device = db.session.query(Device.id,Device.region).join(VM, VM.device_id == Device.id).where(VM.vehicle_id == i['id']).first()
            if device:
                response['device_id'] = device[0][0]
                response['region'] = device[0][1]
            else:
                response['device_id'] = None
                response['region']  = ''
            response['timestamp'] = i['created_at']
            response['vehicle_id'] = i['id']
            response['license_plate'] = i['license_plate']
            
            track_res = db.session.query(Track.id,Video.video_path).join(Video, Video.id == Track.video_id).where(Track.vehicle_id == i['id']).all()
            tmp = {}
            for t in track_res:
                tmp.setdefault(t[1], []).append(t[0])
            for k,v in tmp.items():
                response['video_path'].append(k)
                for j in v:
                    detect_img =  db.session.query(Detection.full_image).filter(Detection.tracking_id == j).all()
                    
                    response['tracking_res'].append({
                        'tracking_id' : v,
                        'detect_img' : [r[0] for r in detect_img]
                    })
            
            classify = db.session.query(Classification.meta_data).filter(Classification.vehicle_id == i['id']).first()
            response['meta_data'] = classify[0]
            recognize = db.session.query(Recognize.crop_image).filter(Recognize.vehicle_id == i['id']).all()
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

