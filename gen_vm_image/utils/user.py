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


def find_user_with_username(username):
    for user in pwd.getpwall():
        if username in user.pw_name:
            return user.pw_name
    return False


def find_group_with_groupname(groupname):
    for group in grp.getgrall():
        if groupname in group.gr_name:
            return group.gr_name
    return False
