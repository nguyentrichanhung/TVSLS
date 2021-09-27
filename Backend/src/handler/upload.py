from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import imghdr

from src import db
from src.migrate.video import Video
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict


def validate_video(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'webm' else 'mp4')


def download_file(video_id,log):
    try:
        res = db.session.query(Video.video_path).filter(Video.id == video_id).first()
        log.info(res)
        return DataReponse(data = res[0])
    except SQLAlchemyError as e:
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)