import os
import logging
import sys
sys.path.append('/usr/src/Backend')
from src import db
from src.migrate.users import User
from src.migrate.violate import Violate
from src.const import ADMIN_ROLE,RULES


log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

if __name__ == '__main__':
    # Add Admin User
    u = db.session.query(User).filter(User.name == os.environ['ADMIN']).first()
    if not u:
        user = User(os.environ['ADMIN'],os.environ['PASSWORD'],ADMIN_ROLE)
        user.add(log)

    # Add violate rule
    violate_lst = []
    for i in list(RULES.values())[:-1]:
        violate = db.session.query(Violate).filter(Violate.type == i).first()
        if violate:
            continue
        violate_lst.append(Violate(i))
    if len(violate_lst)>0:
        db.session.add_all(violate_lst)
        db.session.commit()