from src import db
from src.migrate.device import Device
from src.migrate.vehicle import Vehicle
from src.migrate.track import Track
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.service.response import *
from src.const import *

def validate_id(id,log):
    try:
        data = db.session.query(Device).filter(Device.id == id).first()
        return DataReponse(data = data)
    except SQLAlchemyError as e:
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def validate_track_id(id,log):
    try:
        data = db.session.query(Track).filter(Track.id == id).first()
        if data:
            return DataReponse(data = data)
        return DataReponse(message= 'Cannot found track information',code = CODE_EMPTY) 
    except SQLAlchemyError as e:
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def validate_vehicle_id(id,log):
    try:
        data = db.session.query(Vehicle).filter(Vehicle.id == id).first()
        return DataReponse(data = data)
    except SQLAlchemyError as e:
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)