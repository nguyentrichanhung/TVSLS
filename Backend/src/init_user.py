import os
import logging
import sys
sys.path.append('/usr/src/Backend')
from src.migrate.users import User
from src.const import ADMIN_ROLE


log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

if __name__ == '__main__':
    user = User(os.environ['ADMIN'],os.environ['PASSWORD'],ADMIN_ROLE)
    user.add(log)