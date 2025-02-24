import pytest
from unittest.mock import Mock
from framefox.core.events.event_dispatcher import EventDispatcher

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: Boumaza Rayen
Github: https://github.com/RayenBou
"""


class TestListener:
    def __init__(self):
        self.called = False
        self.payload = None

    def register_listeners(self, dispatcher):
        dispatcher.add_listener("test.event", self.on_test_event)

    def on_test_event(self, payload):
        self.called = True
        self.payload = payload


class TestEventDispatcher:
    @pytest.fixture
    def dispatcher(self):
        return EventDispatcher()

    def test_add_listener(self, dispatcher):
        mock_listener = Mock()
        dispatcher.add_listener("test.event", mock_listener)

        assert "test.event" in dispatcher.listeners
        assert mock_listener in dispatcher.listeners["test.event"]

    def test_dispatch_with_no_listeners(self, dispatcher):
        # Should not raise an exception
        dispatcher.dispatch("test.event", "test_payload")

    def test_dispatch_with_payload(self, dispatcher):
        mock_listener = Mock()
        dispatcher.add_listener("test.event", mock_listener)

        test_payload = {"data": "test"}
        dispatcher.dispatch("test.event", test_payload)

        mock_listener.assert_called_once_with(test_payload)

    def test_multiple_listeners_same_event(self, dispatcher):
        mock_listener1 = Mock()
        mock_listener2 = Mock()

        dispatcher.add_listener("test.event", mock_listener1)
        dispatcher.add_listener("test.event", mock_listener2)

        dispatcher.dispatch("test.event", "test_payload")

        mock_listener1.assert_called_once_with("test_payload")
        mock_listener2.assert_called_once_with("test_payload")

    def test_dispatch_to_specific_listener(self, dispatcher):
        test_listener = TestListener()
        dispatcher.add_listener("test.event", test_listener.on_test_event)

        payload = {"message": "test"}
        dispatcher.dispatch("test.event", payload)

        assert test_listener.called
        assert test_listener.payload == payload
