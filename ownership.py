import os

def fix_ownership(path):
    """Change the owner of the file to SUDO_UID"""

    uid = os.environ.get('SUDO_UID')
    print(uid)
    gid = os.environ.get('SUDO_GID')
    print(gid)
    if uid is not None:
        os.chown(path, int(uid), int(gid))
