from src.migrate.recognize import Recognize
import json
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import and_

from src.migrate.track import Track
from src.migrate.vehicle import Vehicle
from src.migrate.detection import Detection
from src.migrate.classification import Classification

from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict


def create_or_update(license_plate,log):
    try:
        vehicle = db.session.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
        if vehicle:
            vehicle.updated_time = datetime.now()
            db.session.commit()
            return vehicle
        vehicle = Vehicle(license_plate)
        vehicle.add(log)
        return vehicle
    except  SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return None
    except  Exception as e :
        db.session.close()
        log.error(e)
        return None

def get_detect_result_by_vehicle_id(vehicle_id,log):
    try:
        data = db.session.query(Detection).join(Track,Detection.tracking_id == Track.id
                                                ).join(Vehicle,and_(Track.vehicle_id == Vehicle.id,Vehicle.id == vehicle_id)).all()
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

def get_classify_infor_by_vehicle_id(vehicle_id,log):
    try:
        data = db.session.query(Classification).filter(Classification.vehicle_id == vehicle_id).first()
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

def get_recognize_infor_by_vehicle_id(vehicle_id,log):
    try:
        data = db.session.query(Recognize).filter(Recognize.vehicle_id == vehicle_id).all()
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

def get_vehicle_information_by_license_plate(license_plate,log):
    try:
        response = {
            'license_plate' : license_plate,
            'meta_data' : {},
            'license_plate_image' : [],
            'detected_image' : [],
            'car_type' : ''
        }
        vehicle = db.session.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
        db.session.close()
        if vehicle:
            classify = get_recognize_infor_by_vehicle_id(vehicle.id,log)
            if classify.code is CODE_DONE:
                response['meta_data'] = classify.data['meta_data']
                recognize =  get_recognize_infor_by_vehicle_id(vehicle.id,log)
                if recognize.code is CODE_DONE:
                    for d in recognize.data:
                        response['license_plate_image'].append(d['crop_image'])
                    detect = get_detect_result_by_vehicle_id(vehicle.id,log)
                    if detect.code is CODE_DONE:
                        for d in detect.data:
                            response['detected_image'].append({
                                'image_path': d['full_image'],
                                'event_time': d['event_time']
                            })
                            response['car_type'] = d['type']
                        return DataReponse(data = response)
            return DataReponse(data = response,message='Not much information about this license plate!!!')
        return DataReponse(message= 'The License Plate not exist.',code = CODE_EMPTY)
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)