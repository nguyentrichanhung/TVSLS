

def configure_log(mode,user,page_name,ip_add):
    info = '[SYSTEM LOG] - Configuration {} - User:{} - Page:"Setting"-"{}" - IP address: {}'.format(mode,user,page_name,ip_add)
    return info

def user_log(user,status,ip_add):
    info = '[USER LOG] - User {} - User: {} - IP address: {}'.format(status,user,ip_add)
    return info