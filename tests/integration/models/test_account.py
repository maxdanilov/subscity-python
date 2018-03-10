# -*- coding: utf-8 -*-
import pytest
from subscity.models.account import Account, AccountRole

parametrize = pytest.mark.parametrize


class TestModelAccount(object):
    @parametrize('user_role, check_role, result',
                 [(AccountRole.ADMIN, AccountRole.ADMIN, True),
                  (AccountRole.ADMIN, AccountRole.API_WRITE, True),
                  (AccountRole.ADMIN, AccountRole.API_READ, True),
                  (AccountRole.API_WRITE, AccountRole.ADMIN, False),
                  (AccountRole.API_WRITE, AccountRole.API_WRITE, True),
                  (AccountRole.API_WRITE, AccountRole.API_READ, True),
                  (AccountRole.API_READ, AccountRole.ADMIN, False),
                  (AccountRole.API_READ, AccountRole.API_WRITE, False),
                  (AccountRole.API_READ, AccountRole.API_READ, True)])
    def test_check_role(self, user_role, check_role, result):
        account = Account(role=user_role)
        assert account.check_role(check_role) == result

    def test_add(self, dbsession):
        result = Account.add('sometoken', 'app-user', AccountRole.API_READ)

        result_db = dbsession.query(Account).all()
        assert len(result_db) == 1

        assert result == result_db[0]
        assert result.api_token == 'sometoken'
        assert result.name == 'app-user'
        assert result.role == AccountRole.API_READ
        assert result.active is True

    def test_add_duplicate(self, dbsession):
        from sqlalchemy.exc import IntegrityError
        import pytest

        Account.add('sometoken', 'app-user', AccountRole.API_READ)

        with pytest.raises(IntegrityError) as excinfo:
            Account.add('sometoken', 'admin', AccountRole.ADMIN)

        assert "Duplicate entry" in str(excinfo.value)

    def test_check_non_existing(self, dbsession):
        assert Account.check('some-non-existing-token', 'admin') is False

    @parametrize('user_check_role', [AccountRole.ADMIN, AccountRole.API_READ])
    def test_check_stronger_role(self, user_check_role, dbsession):
        account = Account(api_token='sometoken', name='app-user', role=AccountRole.ADMIN,
                          active=True)
        dbsession.add(account)
        dbsession.commit()

        assert Account.check('sometoken', user_check_role) is True

    def test_check_weaker_role(self, dbsession):
        account = Account(api_token='sometoken', name='app-user', role=AccountRole.API_READ,
                          active=True)
        dbsession.add(account)
        dbsession.commit()

        assert Account.check('sometoken', AccountRole.ADMIN) is False

    def test_check_inactive(self, dbsession):
        account = Account(api_token='sometoken', name='app-user', role=AccountRole.API_READ,
                          active=False)
        dbsession.add(account)
        dbsession.commit()

        assert Account.check('sometoken', AccountRole.API_READ) is False

    @parametrize('api_token, result', [('sometoken', True), ('someothertoken', False),
                                       ('', False), (None, False)])
    def test_check_valid(self, api_token, result, dbsession):
        account = Account(api_token='sometoken', name='app-user', role=AccountRole.API_READ,
                          active=True)
        dbsession.add(account)
        dbsession.commit()

        assert Account.check(api_token, AccountRole.API_READ) == result
