from src import db
from src.migrate.classification import Classification
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.service.response import *
from src.const import *


def get_classify_by_track_id(tracking_id,log):
    try:
        data = db.session.query(Classification).filter(Classification.tracking_id == tracking_id).first()
        db.session.close()
        log.info("data: {}".format(data))
        if data:
            res_dict = row2dict(data)
            log.info("data return: {}".format(res_dict))
            return DataReponse(data = res_dict)
        return DataReponse(data = None,code=CODE_EMPTY)
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)