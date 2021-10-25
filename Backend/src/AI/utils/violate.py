
from src.AI.utils.check_inside import *

def wrong_lanes(lanes,vehicle,log):
    for l in lanes:
        if is_inside_polygon(l['points'],vehicle['point']):
            if vehicle['type'] in l['vehilce_properties'].values():
                log.debug("Found violated vehilce")
                return True
        continue
    log.debug("Not found violate vehicle")
    return False

def wrong_direction(vehicle_pos,lanes,log):
    for l in lanes:
        if is_inside_polygon(l['points'],vehicle_pos['point']):
            if vehicle_pos['direction'] == l['direction']:
                return True
        continue
    log.debug("Not found violate vehicle")
    return False