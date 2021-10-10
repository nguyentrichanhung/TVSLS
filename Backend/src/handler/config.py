from src import db
from src.migrate.config import Config
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.service.response import *
from src.const import *
from src.service.response import new_alchemy_encoder,row2dict
import  datetime

def validate(data_video,data_stream):
    video_err = ''
    stream_err = ''
    for k,v in data_video.items():
        if k == 'resolution':
            if len(v) < 2 or len(v) > 2:
                video_err = video_err + 'Invalid resolution format'
        elif k == 'fps':
            if type(v) is not int:
                video_err = video_err + '-' + ' Invalid fps format'
        elif k == 'dbe':
            if type(v) is not int:
                video_err = video_err + '-' + ' Invalid dbe format'
            if v > MAX_DURATION:
                video_err = video_err + '-' + ' duration cannot over 7 seconds'
        elif k == 'extension':
            if v != 'webm':
                video_err = video_err + '-' + ' Not supported current extension. Please Contact for admin!'

    for k,v in data_stream.items():
        if k == 'resolution':
            if len(v) < 2 or len(v) > 2:
                stream_err = stream_err + 'Invalid resolution format'
        if k == 'channel':
            if v not in CHANNELS.values():
                stream_err = stream_err + '-' + ' Invalid channel'

    return video_err,stream_err

def creates(device_id,data_video,data_stream,log):
    try:
        config_data = {}
        video_err, stream_err = validate(data_video, data_stream)
        if len(video_err) > 0:
            return DataReponse(message= 'Invalid video data format. The errors list:\n{}'.format(video_err),code = CODE_FAIL)
        config_data['videos'] = data_video
        if len(stream_err) > 0:
            return DataReponse(message= 'Invalid stream data format. The errors list:\n{}'.format(stream_err),code = CODE_FAIL)
        config_data['stream'] = data_stream
        config = Config(device_id,config_data)
        config.add(log)
        return DataReponse(message= 'Insert successfully!',code = CODE_DONE)
    except  SQLAlchemyError as e:
        db.session.rollback()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e :
        db.session.rollback()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def get_config(log):
    try:
        data = db.session.query(Config).first()
        db.session.close()
        res_dict = row2dict(data)
        return DataReponse(data = res_dict,message='Successful')
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)

def updates(config_id,device_id,data_video,data_stream,log):
    try:
        config = db.session.query(Config).filter_by(Config.id == config_id).first()
        if config is None:
            return DataReponse(message= 'Not found config information with id :{}'.format(config_id),code = CODE_EMPTY)
        config_data = {}
        video_err,stream_err = validate(data_video,data_stream)
        if len(video_err) > 0:
            return DataReponse(message= 'Invalid video data format. The errors list:\n{}'.format(video_err),code = CODE_FAIL)
        config_data['videos'] = data_video
        if len(stream_err) > 0:
            return DataReponse(message= 'Invalid video data format. The errors list:\n{}'.format(video_err),code = CODE_FAIL)
        config_data['stream'] = data_stream
        config.device_id = device_id
        config.config_data = config_data
        config.updated_at = datetime.datetime.now()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.close()
        log.error(e)
        return DataReponse(message= 'Database error!!!',code = CODE_DATABASE_FAIL)
    except  Exception as e:
        db.session.close()
        log.error(e)
        return DataReponse(message = 'System error!!!',code= CODE_FAIL)




