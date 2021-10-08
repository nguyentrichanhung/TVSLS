import sys
import json
sys.path.append('..')

from typing import Any, Optional

import dataclasses
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from flask import Response, jsonify, Flask
from datetime import datetime
from src.const import *
from sqlalchemy.ext.declarative import DeclarativeMeta
@dataclass_json
@dataclass
class DataReponse:
    code: int = CODE_DONE
    message: str = "success"
    data : Optional[Any] = None


@dataclass
class ApiResponse(Response):
    default_minetype = 'application/json'
    data: Optional[Any] = None
    success: bool = False
    message: Optional[str] = None
    code: Optional[int] = None
    

class FlaskApp(Flask):
    def make_response(self, rv):
        if isinstance(rv, ApiResponse):
            return super().make_response(make_json(rv))

        if isinstance(rv, tuple) and isinstance(rv[0], ApiResponse):
            print("data rv:",rv[0])
            print("data rv1:",rv[1])
            rv = (make_json(rv[0]),) + rv[1:]
        return super().make_response(rv)

def del_none(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d


def make_json(d):
    return jsonify(del_none(dataclasses.asdict(d)))

def new_alchemy_encoder():
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    fields[field] = obj.__getattribute__(field)
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder

def row2dict(row):
    if isinstance(row, list):
        d = []
        for r in row:
            dd = {}
            for column in r.__table__.columns:
                dd[column.name] = str(getattr(r, column.name))
            d.append(dd)
        return d
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d