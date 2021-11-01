import time

from src.migrate.track import Track
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import and_

from src.migrate.detection import Detection
from src.migrate.device import Device
from src.migrate.vehicle import Vehicle
from src.migrate.video import Video
from src.migrate.vehicle_management import VM
from src.migrate.classification import  Classification
from src.migrate.recognize import  Recognize
from src.migrate.track import Track

from src.util.general import *

from src.handler.lanes import get_config_lst

from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict


def search_by_time(start_time,end_time,vehicle_type,log):
    try:
        data = {}
        start_time1 = time.time()
        # track = db.session.query(Track).filter(Track.created_at.between(start_time,end_time)).all()
        track_res = db.session.query(Track.id,Track.start_time,Track.end_time,
                            Video.video_path,Device.id,Device.region,Classification.meta_data,
                            Detection.full_image,Detection.type,Recognize.crop_image).distinct(Track.id).join(
                            Video,Video.id == Track.video_id).join(
                            Device,Device.id == Video.device_id).join(
                            Detection,and_(Detection.tracking_id == Track.id,Detection.type.in_(vehicle_type))).join(
                            Classification,Classification.detect_id == Detection.id).join(
                            Recognize,Recognize.detect_id == Detection.id).where(Track.created_at.between(start_time,end_time)).all()
        # image_list = db.session.query(Track.id,Detection.full_image,Detection.type,Recognize.crop_image).join(
        #                                 Detection,Detection.tracking_id == Track.id).join(
        #                                 Recognize,Recognize.tracking_id == Track.id).where(Track.created_at.between(start_time,end_time)).all()
        log.info('Done! Took {} seconds'.format(time.time()-start_time1))
        db.session.close()
        
        for t in track_res:
            data[t[0]] = {
                'timestamp': {
                    'start_time' : t[1],
                    'end_time' : t[2]
                },
                'device_id': t[4],
                'region': t[5],
                'video_path': t[3],
                'meta_data': t[6],
                'tracking_res': {
                    'detect_type' : t[7],
                    'detect_img' : t[8]
                },
                'license_plate_image' : t[9]
            }

        return DataReponse(data = data)
    except  SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def search_crop_image(detect_id,log):
    try:
        data = db.session.query(Recognize.crop_image).filter(Recognize.detect_id == detect_id).all()
        db.session.close()
        res = [i[0] for i in data]

        return DataReponse(data = res)
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def search_full_image(tracking_id,start_area,middle_area,end_area,log):
    try:
        data = db.session.query(Detection.id,Detection.bounding_box,Detection.full_image).join(
                            Track,Track.id ==Detection.tracking_id).where(Track.id == tracking_id).all()
        db.session.close()
        detect_list = {}
        start = {}
        middle = {}
        end = {}
        lane_info = get_config_lst(log)
        xmin,ymin,xmax,ymax = bounding_box(lane_info.data[0]['points'])
        ystart,yend = get_filter_region(ymin,ymax)
        for i in data:
            ycenter = (i[1]['y'] +i[1]['h'])/2
            if ycenter > ymin and ycenter <= ystart:
                start[i[0]] = {
                "image_path" : i[2]
            }
            elif ycenter > ystart and ycenter <= yend:
                middle[i[0]] = {
                "image_path" : i[2]
            }
            else:
                end[i[0]] = {
                "image_path" : i[2]
            }
        detect_list = {
            "start" : {i : start[i] for i in list(start.keys())[:start_area]},
            "middlde" : {i : middle[i] for i in list(middle.keys())[:middle_area]},
            "end" : {i : end[i] for i in list(end.keys())[:end_area]}
        }
        return DataReponse(data = detect_list)
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
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

