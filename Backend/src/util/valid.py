import dataclasses
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
import json


@dataclass_json
@dataclass
class ValidateRegister:
    username: str
    password: str
    role: str
    def validate(self) -> [bool,str]:
        if not self.username or not self.role or not self.password:
            return False, 'Invalid register info data'
        return True, ''

@dataclass_json
@dataclass
class ValidateRoleInfo:
    user_id: str
    role: str
    def validate(self) -> [bool,str]:
        if not self.user_id or not self.role:
            return False, 'Invalid role info data'
        return True, ''

@dataclass_json
@dataclass
class ValidateLogin:
    name: str
    password: str
    def validate(self) -> [bool,str]:
        if not self.name or not self.password:
            return False, 'Invalid login data'
        return True, ''

@dataclass_json
@dataclass
class ValidateDevce:
    data: json

    def validate(self) -> [bool,str]:
        if not self.data:
            return False, 'Invalid data'
        return True, ''

@dataclass_json
@dataclass
class ValidateData:
    start_time: datetime
    end_time: datetime
    def validate(self) -> [bool,str]:
        if not self.start_time or not self.end_time:
            return False, 'Invalid data'
        return True, ''

@dataclass_json
@dataclass
class ValidateConfig:
    stream : json
    videos : json
    device_id: str
    def validate(self)-> [bool,str]:
        if not self.stream or not self.videos or not self.device_id:
            return False, 'Invalid config info'
        return True, ''

@dataclass_json
@dataclass
class ValidateLanes:
    lanes : json
    device_id : str
    def validate(self)-> [bool,str]:
        if not self.lanes or not self.device_id:
            return False, 'Invalid lanes info'
        return True, ''