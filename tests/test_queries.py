from skatetrax.models import equipment as equip


def test_coaches():

    expected = 1
    # expected = {'id': 1, 'coach_Fname': '-', 'coach_Lname': '-', 'coach_rate': 0.0, 'uSkaterUUID': 0}

    result = equip.list_all.coaches_list_disconnected()

    '''
    result.id
    result.coach_Fname
    result.coach_Lname
    result.coach_rate
    result.uSkaterUUID
    '''

    assert result.id == expected
