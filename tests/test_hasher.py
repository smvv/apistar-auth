from .testutil import TestCaseUnauthenticatedBase
from apistar_auth import User, enable_bcrypt_hasher


class TestCaseUsers(TestCaseUnauthenticatedBase):
    def test_password_is_hashed(self, user_data):
        # Enable bcrypt for password hashing for this specific test. This
        # hasher is slow and therefore generally disabled during testing.
        enable_bcrypt_hasher(rounds=4)

        u = User(**user_data)
        assert u.password[:18] == '$bcrypt-sha256$2b,'
        assert len(u.password.split('$')) == 5
        assert len(u.password.split('$')[3]) > 20
        assert u.verify_password(user_data['password'])

        # Check that passwords are not truncated. This is a limitation of the
        # original bcrypt algorithm. Current implementation applies sha256 on
        # the input password before feeding it to bcrypt.
        user_data['password'] = '#' * 73
        u = User(**user_data)
        assert not u.verify_password('#' * 72)
