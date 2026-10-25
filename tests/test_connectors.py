
import pytest

from dbmonitor.connectors.base import BaseConnector


def test_base_connector_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseConnector()


def test_concrete_connector_must_implement_all_methods():
    class IncompleteConnector(BaseConnector):
        def connect(self):
            pass

    with pytest.raises(TypeError):
        IncompleteConnector()
