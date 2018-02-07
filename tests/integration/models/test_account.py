# -*- coding: utf-8 -*-
from subscity.models.account import Account


class TestModelAccount(object):
    def test_add(self, dbsession):
        result = Account.add('sometoken', 'app-user')

        result_db = dbsession.query(Account).all()
        assert len(result_db) == 1

        assert result == result_db[0]
        assert result.api_token == 'sometoken'
        assert result.name == 'app-user'
        assert result.active is True

    def test_add_duplicate(self, dbsession):
        from sqlalchemy.exc import IntegrityError
        import pytest

        Account.add('sometoken', 'app-user')

        with pytest.raises(IntegrityError) as excinfo:
            Account.add('sometoken', 'admin')

        assert "Duplicate entry" in str(excinfo.value)

    def test_check_empty(self, dbsession):
        assert Account.check('some-non-existing-token') is False

    def test_check_inactive(self, dbsession):
        account = Account(api_token='sometoken', name='app-user', active=False)
        dbsession.add(account)
        dbsession.commit()

        assert Account.check('sometoken') is False

    def test_check_valid(self, dbsession):
        account = Account(api_token='sometoken', name='app-user', active=True)
        dbsession.add(account)
        dbsession.commit()

        assert Account.check('sometoken') is True
        assert Account.check('someothertoken') is False
