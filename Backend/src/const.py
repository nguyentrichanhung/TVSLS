CODE_DONE = 1000
CODE_FAIL = 1001
CODE_DATABASE_FAIL = 1002
CODE_PROCESSING = 1003
CODE_EMPTY = 1004


### Root Folder
ROOTDIR = '/usr/src/Backend/src/AI'
STORAGE = '/usr/src/Backend/src/AI/storage'
ROOT = ''


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

CHANNELS = {
    '0' : 'cam0_0',
    '1' : 'cam0_1',
    '2' : 'cam0_2'
}