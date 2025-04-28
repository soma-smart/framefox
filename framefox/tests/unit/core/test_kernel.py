# from unittest.mock import Mock, patch

# import pytest

# from framefox.core.kernel import Kernel
# from framefox.core.config.settings import Settings

# """
# Framefox Framework developed by SOMA
# Github: https://github.com/soma-smart/framefox
# ----------------------------
# Author: BOUMAZA Rayen
# Github: https://github.com/RayenBou
# """


# class TestKernel:
#     @pytest.fixture
#     def mock_container(self):
#         with patch("framefox.core.di.service_container.ServiceContainer") as mock:
#             container = Mock()
#             def mock_get(arg):
#                 if arg.__class__ == "Settings":
#                     return Mock(spec=Settings)
#                 return Mock()

#             container.get.side_effect = mock_get
#             mock.return_value = container
#             yield mock

#     def test_singleton_pattern(self):
#         kernel1 = Kernel()
#         kernel2 = Kernel()
#         assert kernel1 is kernel2

#     @pytest.mark.asyncio
#     async def test_app_initialization(self, mock_container):
#         kernel = Kernel()
#         assert kernel._app is not None
#         assert kernel._initialized is True
