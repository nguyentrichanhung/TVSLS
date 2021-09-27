
import json
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import and_

from src.migrate.vehicle_management import VM

from src import db
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict


def create(vehicle_id,device_id,log):
    try:
        manager = db.session.query(VM).filter(and_(VM.vehicle_id == vehicle_id,VM.device_id == device_id)).first()
        if manager:
            manager.updated_time = datetime.now()
            db.session.commit()
            return manager
        manager = VM(device_id,vehicle_id)
        manager.add(log)
        return manager
    except  SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return None
    except  Exception as e :
        db.session.close()
        log.error(e)
        return None