from skatetrax.utils.common import minutes_to_hours, currency_usd

# run via PYTHONPATH=. pytest tests/test_utils.py


def test_decorator_time():

    @minutes_to_hours
    def test_format_time():
        time_in_minutes = 90.5
        return time_in_minutes

    assert test_format_time() == {'hours': 1, 'minutes': 30.5}


def test_decorator_usd():

    @currency_usd
    def test_usd_currency():
        cost = 08.20
        return cost

    assert test_usd_currency() == "%0.2f" % 8.2
