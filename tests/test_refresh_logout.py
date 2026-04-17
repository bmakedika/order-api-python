def test_refresh_rotates_refresh_token_and_returns_new_access(client):
    client.post('/auth/register', json={
        'username': 'ruser',
        'email': 'ruser@example.com',
        'password': 'pw',
    })

    login = client.post('/auth/login', json={
        'email': 'ruser@example.com',
        'password': 'pw',
    })
    assert login.status_code == 200
    old_access = login.json()['access_token']
    
    # Refresh using cookie-only (no body)
    refreshed = client.post('/auth/refresh')
    assert refreshed.status_code == 200
    new_access = refreshed.json()['access_token']
    assert new_access != old_access

    # Refresh token should NOT be in Json
    assert 'refresh_token' not in refreshed.json()

    # Old refresh should now be invalid (rotation)
    old_refresh_cookie = login.cookies.get('refresh_token')
    assert old_refresh_cookie is not None

    again = client.post('/auth/refresh', json={
        'refresh_token': old_refresh_cookie,
    })
    assert again.status_code == 401


def test_logout_revokes_refresh_token(client):
    client.post('/auth/register', json={
        'username': 'luser',
        'email': 'luser@example.com',
        'password': 'pw',
    })

    login_response = client.post('/auth/login', json={
        'email': 'luser@example.com',
        'password': 'pw',
    })
    assert login_response

    refresh_cookie = login_response.cookies.get('refresh_token')
    assert refresh_cookie is not None

    # Log out (cookie-only is enough)
    out = client.post('/auth/logout')
    assert out.status_code == 200
    # After logout, the refresh token should be revoked and not work anymore
    refreshed = client.post('/auth/refresh', json={
        'refresh_token': refresh_cookie,
    })
    assert refreshed.status_code == 401