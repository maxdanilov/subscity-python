from mock import mock_open, patch, call


def test_update_database(mocker):
    from subscity.yandex_afisha_parser import YandexAfishaParser
    from subscity.scripts import update_database
    from subscity.models.cinema import Cinema

    mock_get_cinemas = mocker.patch.object(YandexAfishaParser, 'get_cinemas',
                                           side_effect=[[{'name': '1'}, {'name': '2'}],
                                                        [{'name': '3'}, {'name': '4'}]])
    mock_cinema_init = mocker.patch.object(Cinema, '__init__', return_value=None)
    mock_cinema_save = mocker.patch.object(Cinema, 'save_or_update')
    update_database()
    assert mock_get_cinemas.call_args_list == [call('moscow'), call('saint-petersburg')]
    assert mock_cinema_init.call_args_list == [call(name='1'), call(name='2'), call(name='3'),
                                               call(name='4')]
    assert mock_cinema_save.call_args_list == [call(), call(), call(), call()]


def test_update_test_fixtures(mocker):
    from subscity.scripts import update_test_fixtures
    from subscity.yandex_afisha_parser import YandexAfishaParser
    mock_file_open = mock_open()
    mock_urls = mocker.patch.object(YandexAfishaParser, 'url_places',
                                    side_effect=['url1', 'url2', 'url3', 'url4'])
    mock_fetch = mocker.patch.object(YandexAfishaParser, 'fetch',
                                     side_effect=['{"json": 1}', '{"json": 2}', '{"json": 3}',
                                                  '{"json": 4}'])
    with patch('subscity.scripts.open', mock_file_open, create=True):
        update_test_fixtures()
    assert mock_fetch.call_args_list == [call('url1'), call('url2'), call('url3'), call('url4')]
    assert mock_urls.call_args_list == [
        call(city='saint-petersburg', limit=20, offset=0),
        call(city='saint-petersburg', limit=20, offset=20),
        call(city='saint-petersburg', limit=20, offset=40),
        call(city='saint-petersburg', limit=20, offset=60)]
    assert mock_file_open.call_args_list == [
        call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset00-limit20.json', 'w'),
        call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset20-limit20.json', 'w'),
        call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset40-limit20.json', 'w'),
        call('tests/fixtures/cinemas/saint-petersburg/cinemas-offset60-limit20.json', 'w')]

    assert mock_file_open.mock_calls[2]  == call().write('{\n    "json": 1\n}')
    assert mock_file_open.mock_calls[6]  == call().write('{\n    "json": 2\n}')
    assert mock_file_open.mock_calls[10] == call().write('{\n    "json": 3\n}')
    assert mock_file_open.mock_calls[14] == call().write('{\n    "json": 4\n}')
