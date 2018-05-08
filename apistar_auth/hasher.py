from passlib.hash import bcrypt_sha256, ldap_sha1


# Number of bcrypt rounds (default=12). During testing, bcrypt is not used
# (see also `setup_method()` in ./testutil.py) to speed up the unit tests.
bcrypt_rounds = 12


def enable_bcrypt_hasher(rounds=12):
    global bcrypt_rounds
    bcrypt_rounds = rounds


def disable_bcrypt_hasher():
    global bcrypt_rounds
    bcrypt_rounds = 0


def hasher():
    if bcrypt_rounds:
        return bcrypt_sha256.using(rounds=bcrypt_rounds)
    # During testing, a weaker password hasher is used.
    return ldap_sha1
