import os
import json
import datetime
import time
from bson.objectid import ObjectId
from flask.logging import default_handler
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData

from src.service.response import FlaskApp

from dotenv import load_dotenv
# from pathlib import Path
class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

load_dotenv('.env')
app = FlaskApp(__name__)
app.logger.removeHandler(default_handler)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{0}:{1}@{2}:5432/{3}".format(os.environ['POSTGRES_USER'],os.environ['POSTGRES_PASS'],
                                                                        os.environ['POSTGRES_SERVER'],os.environ['POSTGRES_NAME'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.update({
    'SQLALCHEMY_POOL_SIZE': None,
    'SQLALCHEMY_POOL_TIMEOUT': None
})
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif','.mp4','.webm']
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, session_options={"expire_on_commit": False}, metadata=metadata)
from src.migrate.vehicle import Vehicle
from src.migrate.device import Device
from src.migrate.classification import Classification
from src.migrate.detection import Detection
from src.migrate.vehicle_management import VM
from src.migrate.recognize import Recognize
from src.migrate.track import Track
from src.migrate.video import Video
from src.migrate.config import Config
from src.migrate.lane_properties import LaneProperty
migrate = Migrate(app, db)

# use the modified encoder class to handle ObjectId & datetime object while jsonifying the response.
app.json_encoder = JSONEncoder