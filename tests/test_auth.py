def test_register(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'testuser'
    assert data['email'] == 'testuser@example.com'
    assert data['role'] == 'user'


def test_login_success_returns_access_token_only(client):
    client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'testuser2@example.com',
        'password': 'testpassword'
    })

    response = client.post('/auth/login', json={
        'email': 'testuser2@example.com',
        'password': 'testpassword',
    })

    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert isinstance(data['access_token'], str)
    assert len(data['access_token']) > 10
    assert data['token_type'] == 'bearer'
    assert 'refresh_token' not in data


def test_login_sets_refresh_token_cookie(client):
    client.post('/auth/register', json={
        'username': 'cookieuser',
        'email': 'cookieuser@example.com',
        'password': 'pw'
    })

    response = client.post('/auth/login', json={
        'email': 'cookieuser@example.com',
        'password': 'pw'
    })

    assert response.status_code == 200
    set_cookie = response.headers.get('set-cookie')
    assert set_cookie is not None
    assert 'refresh_token=' in set_cookie
    assert 'HttpOnly' in set_cookie
    assert 'Path=/auth' in set_cookie


def test_login_wrong_password_returns_401(client):
    client.post('/auth/register', json={
        'username': 'testuser3',
        'email': 'testuser3@example.com',
        'password': 'correct-password'
    })

    response = client.post('/auth/login', json={
        'email': 'testuser3@example.com',
        'password': 'wrong-password'
    })

    assert response.status_code == 401