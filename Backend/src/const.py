CODE_DONE = 1000
CODE_FAIL = 1001
CODE_DATABASE_FAIL = 1002
CODE_PROCESSING = 1003
CODE_EMPTY = 1004
CODE_UNAUTHORIZE = 1005


### Folder
ROOTDIR = '/usr/src/Backend/src/AI'
STORAGE = '/usr/src/Backend/src/AI/storage'
# STORAGE = '/home/storage'
ROOT = '/'
EXTERNAL_STORAGE = '/home/storage'
LOG_FOLDER = './src/logs'


### Rule Type
RULES = {
    "SP" : "SPEED",
    "RL" : "RED LIGHT RUNNING",
    "WD" : "WRONG DIRECTION",
    "IP" : "ILLEGAL PARKING",
    "HD" : "HELMET DETECTION",
    "NF" : "NON-OFFENCE"
}

### Video
MAX_DURATION = 7


### Stream

CHANNELS_PTZ = {
    '0' : 'cam0_0',
    '1' : 'cam0_1',
    '2' : 'cam0_2'
}
CHANNELS_HUCOMS = {
    '0' : 'stream0',
    '1' : 'stream1',
    '2' : 'stream2'
}


### Roles
ADMIN_ROLE = 'admin'
NORMAL_ROLE = 'visitor'
OFFICER_ROLE = 'offcier'


### Hardware Unit

GB = 1024*1024*1024
MB = 1024*1024