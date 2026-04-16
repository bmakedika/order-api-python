def test_logout_revokes_access_token_via_blacklist(client):
    # Register and login a user to get an access token
    client.post('/auth/register', json={
        'username': 'blkuser',
        'email': 'blkuser@example.com',
        'password': 'pw',
    })
    login = client.post('/auth/login', json={
        'email': 'blkuser@example.com',
        'password': 'pw'
    })
    access = login.json['access_token']

    # call a protected endpoint Ok
    ok = client.get('/users/me', headers={'Authorization': f'Bearer {access}'})
    assert ok.status_code == 200

    # Logout should blacklist access token jti
    out = client.post('/auth/logout', headers={'Authorization': f'Bearer {access}'})
    assert out.status_code == 200

    # Now access token must be rejected
    denied = client.get('/users/me', headers={'Authorization': f'Bearer {access}'})
    assert denied.status_code == 401