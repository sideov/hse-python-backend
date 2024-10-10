import datetime
from datetime import timedelta

import pytest
from starlette.testclient import TestClient

from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.api.contracts import *
from lecture_4.demo_service.core.users import UserInfo, UserService, password_is_longer_than_8

demo_service = create_app()
client = TestClient(demo_service)


@pytest.fixture(scope="function")
def register_user_request():
    return RegisterUserRequest(
        username="test",
        name="test",
        birthdate=datetime.now(),
        password=SecretStr("123456789")
    )


@pytest.fixture(scope="function")
def user_info():
    return UserInfo(
        username="test",
        name="test",
        birthdate=datetime.now(),
        role=UserRole.USER,
        password=SecretStr("123456789")
    )


@pytest.fixture(scope="function")
def user_entity(user_info):
    return UserEntity(
        uid=1,
        info=user_info
    )


@pytest.fixture(scope="function")
def user_auth_request():
    return UserAuthRequest(
        username="test",
        password=SecretStr("123456789")
    )


@pytest.fixture(scope="function")
def user_service():
    return UserService()


@pytest.fixture(scope="function")
def user_response():
    return UserResponse(
        uid=1,
        username="test",
        name="test",
        birthdate=datetime.now(),
        role=UserRole.USER
    )


def test_create_app():
    assert demo_service is not None


def test_password_no_longer_than_8():
    assert not password_is_longer_than_8("12345678")
    assert password_is_longer_than_8("123456789")


def test_user_role():
    user_role = UserRole.USER
    assert user_role == UserRole.USER


def test_user_info(user_info):
    assert user_info.username == "test"
    assert user_info.name == "test"
    assert user_info.birthdate - datetime.now() < timedelta(seconds=1)
    assert user_info.role == UserRole.USER
    assert user_info.password == SecretStr("123456789")


def test_user_entity(user_entity):
    assert user_entity.uid == 1
    assert user_entity.info.username == "test"
    assert user_entity.info.name == "test"
    assert user_entity.info.birthdate - datetime.now() < timedelta(seconds=1)
    assert user_entity.info.role == UserRole.USER
    assert user_entity.info.password == SecretStr("123456789")


def test_register_user_request(register_user_request):
    assert register_user_request.username == "test"
    assert register_user_request.name == "test"
    assert register_user_request.birthdate - datetime.now() < timedelta(seconds=1)
    assert register_user_request.password == SecretStr("123456789")


def test_user_response(user_response, user_entity):
    assert user_response.uid == 1
    assert user_response.username == "test"
    assert user_response.name == "test"
    assert user_response.birthdate - datetime.now() < timedelta(seconds=1)
    assert user_response.role == UserRole.USER

    user_response_from_entity = UserResponse.from_user_entity(user_entity)
    assert user_response_from_entity.uid == 1
    assert user_response_from_entity.username == "test"
    assert user_response_from_entity.name == "test"
    assert user_response_from_entity.birthdate - datetime.now() < timedelta(seconds=1)
    assert user_response_from_entity.role == UserRole.USER


def test_user_auth_request(user_auth_request):
    assert user_auth_request.username == "test"
    assert user_auth_request.password == SecretStr("123456789")


def test_user_service(user_service, user_info):
    user_entity = user_service.register(user_info)
    assert user_entity.info.username == user_info.username
    assert user_entity.info.name == user_info.name
    assert user_entity.info.birthdate == user_info.birthdate
    assert user_entity.info.role == user_info.role
    assert user_entity.info.password == user_info.password

    assert user_service.get_by_username(user_info.username) == user_entity
    assert user_service.get_by_id(user_entity.uid) == user_entity

    user_service.grant_admin(user_entity.uid)
    assert user_entity.info.role == UserRole.ADMIN

    with pytest.raises(ValueError):
        user_service.grant_admin(2)


@pytest.fixture(scope="function")
def demo_servicee():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_register_user(demo_servicee, user_service, register_user_request, user_response):
    request_data = register_user_request.model_dump()
    request_data['birthdate'] = request_data['birthdate'].isoformat()
    request_data['password'] = register_user_request.password.get_secret_value()

    response = demo_servicee.post("/user-register", json=request_data)
    assert response.status_code == 200
    assert response.json().get('name') == user_response.name
    assert response.json().get('username') == user_response.username
    assert response.json().get('role') == user_response.role
    assert datetime.fromisoformat(response.json().get('birthdate')) - user_response.birthdate < timedelta(seconds=1)


def test_get_user(demo_servicee, register_user_request, user_entity, user_response):
    request_data = register_user_request.model_dump()
    request_data['birthdate'] = request_data['birthdate'].isoformat()
    request_data['password'] = register_user_request.password.get_secret_value()

    first_post_resp = demo_servicee.post("/user-register", json=request_data)

    auth_headers = {
        "Authorization": "Basic dGVzdDoxMjM0NTY3ODk="
    }
    response = demo_servicee.post("/user-get", params={'id': first_post_resp.json().get("uid")}, headers=auth_headers)

    assert response.status_code == 200
    assert response.json().get('name') == user_response.name
    assert response.json().get('username') == user_response.username
    assert response.json().get('role') == user_response.role
    assert datetime.fromisoformat(response.json().get('birthdate')) - user_response.birthdate < timedelta(seconds=1)

    response = demo_servicee.post("/user-get", json={'id': user_entity.uid, 'username': user_entity.info.username})
    assert response.status_code == 401

    response = demo_servicee.post("/user-get", params={'id': user_entity.uid, 'username': user_entity.info.username},
                                  headers=auth_headers)

    assert response.status_code == 400

    response = demo_servicee.post("/user-get", params={}, headers=auth_headers)
    assert response.status_code == 400

    admin_request_data = {
        "username": "admin",
        "name": "admin",
        "birthdate": datetime.now().isoformat(),
        "password": "superSecretAdminPassword123"
    }
    admin_auth_headers = {
        "Authorization": "Basic YWRtaW46c3VwZXJTZWNyZXRBZG1pblBhc3N3b3JkMTIz"
    }
    demo_servicee.post("/user-register", json=admin_request_data)
    response = demo_servicee.post("/user-get", params={"username": "admin"}, headers=admin_auth_headers)
    assert response.status_code == 200

    demo_servicee.post("/user-register", json=admin_request_data)
    response = demo_servicee.post("/user-get", params={"username": "adminasd"}, headers=admin_auth_headers)
    assert response.status_code == 404

    auth_headers_bad = {
        "Authorization": "Basic YWRtaW46MTIz"
    }

    response = demo_servicee.post("/user-get", params={'id': first_post_resp.json().get("uid")},
                                  headers=auth_headers_bad)
    assert response.status_code == 401


def test_promote_user(demo_servicee, register_user_request, user_entity):
    admin_request_data = {
        "username": "admin",
        "name": "admin",
        "birthdate": datetime.now().isoformat(),
        "password": "superSecretAdminPassword123"
    }
    admin_auth_headers = {
        "Authorization": "Basic YWRtaW46c3VwZXJTZWNyZXRBZG1pblBhc3N3b3JkMTIz"
    }
    auth_headers_user = {
        "Authorization": "Basic dGVzdDoxMjM0NTY3ODk="
    }

    print(admin_request_data)
    demo_servicee.post("/user-register", json=admin_request_data)

    request_data = register_user_request.model_dump()
    request_data['birthdate'] = request_data['birthdate'].isoformat()
    request_data['password'] = register_user_request.password.get_secret_value()
    first_post_resp = demo_servicee.post("/user-register", json=request_data)
    assert first_post_resp.status_code == 200

    resp = demo_servicee.post("/user-promote", params={'id': first_post_resp.json().get("uid")},
                              headers=auth_headers_user)
    assert resp.status_code == 403

    response = demo_servicee.post("/user-promote", params={'id': first_post_resp.json().get("uid")},
                                  headers=admin_auth_headers)
    assert response.status_code == 200

    bad_admin_request_data = {
        "username": "admin2",
        "name": "admin2",
        "birthdate": datetime.now().isoformat(),
        "password": ""
    }

    response = demo_servicee.post("/user-register", json=bad_admin_request_data)
    assert response.status_code == 400
