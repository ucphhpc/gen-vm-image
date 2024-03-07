import pwd
import grp


def lookup_uid(username):
    try:
        return pwd.getpwnam(username).pw_uid
    except Exception as err:
        print("Failed to discover user uid: {} - {}".format(username, err))
    return False


def lookup_gid(groupname):
    try:
        return grp.getgrnam(groupname).gr_gid
    except Exception as err:
        print("Failed to discover group gid: {} - {}".format(groupname, err))
    return False
