import pytest

from framefox.core.security.password.password_hasher import PasswordHasher

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestPasswordHasher:
    @pytest.fixture
    def password_hasher(self):
        """Fixture for PasswordHasher instance"""
        return PasswordHasher()

    def test_hash_password(self, password_hasher):
        """Test password hashing"""
        # Setup
        raw_password = "test_password123"

        # Execute
        hashed_password = password_hasher.hash(raw_password)

        # Assert
        assert hashed_password is not None
        assert hashed_password != raw_password
        # Verify that it is indeed a bcrypt hash
        assert hashed_password.startswith("$2b$")

    def test_verify_valid_password(self, password_hasher):
        """Test password verification with valid password"""
        # Setup
        raw_password = "test_password123"
        hashed_password = password_hasher.hash(raw_password)

        # Execute
        is_valid = password_hasher.verify(raw_password, hashed_password)

        # Assert
        assert is_valid is True
