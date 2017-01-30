# -*- coding: utf-8 -*-


class TestAppViews(object):
    def test_root(self, client):
        result = client.get('/')
        assert result.status_code == 200
        assert result.get_data().decode('utf-8') == 'Hello, World! тест'
