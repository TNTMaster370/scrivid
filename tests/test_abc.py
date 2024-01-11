import scrivid

import pytest


def test_defined_adjustment():
    class Mock(scrivid.abc.Adjustment):
        @property
        def activation_time(self):
            return None

        def _enact(self):
            return None

    Mock()


def test_defined_qualm():
    class Mock(scrivid.abc.Qualm):
        def _comparison(self):
            return None

        def _message(self):
            return None

        @classmethod
        def check(cls):
            return None

    Mock()


def test_undefined_adjustment_activation_time_property():
    class Mock(scrivid.abc.Adjustment):
        def _enact(self):
            return None

    with pytest.raises(TypeError):
        Mock()


def test_undefined_adjustment_activation_time_not_property():
    with pytest.raises(scrivid.errors.TypeError):
        class _(scrivid.abc.Adjustment):
            def activation_time(self):
                return None

            def _enact(self):
                return None


def test_undefined_adjustment_enact():
    class Mock(scrivid.abc.Adjustment):
        @property
        def activation_time(self):
            return None

    with pytest.raises(TypeError):
        Mock()


def test_undefined_qualm_check():
    class Mock(scrivid.abc.Qualm):
        def _comparison(self):
            return None

        def _message(self):
            return None

    with pytest.raises(TypeError):
        Mock()


def test_undefined_qualm_comparison():
    class Mock(scrivid.abc.Qualm):
        def _message(self):
            return None

        @classmethod
        def check(cls):
            return None

    with pytest.raises(TypeError):
        Mock()


def test_undefined_qualm_message():
    class Mock(scrivid.abc.Qualm):
        def _comparison(self):
            return None

        @classmethod
        def check(cls):
            return None

    with pytest.raises(TypeError):
        Mock()
