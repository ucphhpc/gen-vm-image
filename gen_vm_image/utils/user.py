# Copyright (C) 2024  The gen-vm-image Project by the Science HPC Center at UCPH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

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
