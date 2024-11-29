def currency_usd(func):
    '''
    ensures currency formating is consistent
    '''

    def wrapper(*args, **kwargs):
        amount = func(*args, **kwargs)
        if amount is None:
            return ("%0.2f" % float(0))
        else:
            return ("%0.2f" % float(amount))
    return wrapper


def minutes_to_hours(func):
    '''
    ensures minutes are always divided into
    amount of hours and minutes cleanly
    '''

    def wrapper(*args, **kwargs):
        m = func(*args, **kwargs)
        h, m = divmod(m, 60)
        return {'hours': int(h), 'minutes': float(m)}
    return wrapper
