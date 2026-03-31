from fastapi.testclient import TestClient


def test_create_order(client):
    response = client.post("/orders", json={
        "customer_id": "user-123",
        "currency": "EUR"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "draft"
    assert data["total_cents"] == 0
    assert data["items"] == []


def test_add_item_to_order(client):
    # create product
    product = client.post("/products", json={
        "name": "Keyboard",
        "description": "Mechanical keyboard",
        "price_cents": 8900,
        "currency": "EUR",
        "category": "tech"
    }).json()

    # create order
    order = client.post("/orders", json={
        "customer_id": "user-123",
        "currency": "EUR"
    }).json()

    # add product to order
    response = client.post(f"/orders/{order['id']}/items", json={
        "product_id": product["id"],
        "quantity": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total_cents"] == 17800
    assert len(data["items"]) == 1


def test_pay_order(client):
    # create product + create order + add item
    product = client.post("/products", json={
        "name": "Keyboard",
        "description": "Mechanical keyboard",
        "price_cents": 8900,
        "currency": "EUR",
        "category": "tech"
    }).json()

    order = client.post("/orders", json={
        "customer_id": "user-123",
        "currency": "EUR"
    }).json()

    client.post(f"/orders/{order['id']}/items", json={
        "product_id": product["id"],
        "quantity": 1
    })

    # payment
    response = client.post(
        f"/orders/{order['id']}/pay",
        headers={"Idempotency-Key": "test-pay-001"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paid"


def test_pay_order_idempotent(client):
    # create product + create order + add item
    product = client.post("/products", json={
        "name": "Keyboard",
        "description": "Mechanical keyboard",
        "price_cents": 8900,
        "currency": "EUR",
        "category": "tech"
    }).json()

    order = client.post("/orders", json={
        "customer_id": "user-123",
        "currency": "EUR"
    }).json()

    client.post(f"/orders/{order['id']}/items", json={
        "product_id": product["id"],
        "quantity": 1
    })

    # premier paiement first payment
    client.post(
        f"/orders/{order['id']}/pay",
        headers={"Idempotency-Key": "test-idem-001"}
    )

    # second payment - same key
    response = client.post(
        f"/orders/{order['id']}/pay",
        headers={"Idempotency-Key": "test-idem-001"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "paid"


def test_pay_order_empty(client):
    order = client.post("/orders", json={
        "customer_id": "user-123",
        "currency": "EUR"
    }).json()

    response = client.post(
        f"/orders/{order['id']}/pay",
        headers={"Idempotency-Key": "test-empty-001"}
    )
    assert response.status_code == 400


def test_remove_item(client):
    product = client.post("/products", json={
        "name": "Keyboard",
        "description": "Mechanical keyboard",
        "price_cents": 8900,
        "currency": "EUR",
        "category": "tech"
    }).json()

    order = client.post("/orders", json={
        "customer_id": "user-123",
        "currency": "EUR"
    }).json()

    updated = client.post(f"/orders/{order['id']}/items", json={
        "product_id": product["id"],
        "quantity": 1
    }).json()

    item_id = updated["items"][0]["id"]

    response = client.delete(f"/orders/{order['id']}/items/{item_id}")
    assert response.status_code == 200

    order_after = client.get(f"/orders/{order['id']}").json()
    assert order_after["total_cents"] == 0
    assert order_after["items"] == []



def test_update_order_status(client):
    order = client.post('/orders', json={
        'customer_id': 'user-123',
        'currency': 'EUR'
    }).json()
    response = client.patch(
        f"/orders/{order['id']}/status",
        json={"status": "shipped"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'shipped'



def test_update_order_status_not_found(client):
    response = client.patch(
        f'/orders/00000000-0000-0000-0000-000000000000/status',
        json={'status': 'shipped'}
    )
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Order not found'



def test_get_invoice(client):
    # create product + order + item
    product = client.post("/products", json={
        "name": "Keyboard",
        "description": "Mechanical keyboard",
        "price_cents": 8900,
        "currency": "EUR",
        "category": "tech"
    }).json()

    order = client.post("/orders", json={
        "customer_id": "user-123",
        "currency": "EUR"
    }).json()

    client.post(f"/orders/{order['id']}/items", json={
        "product_id": product["id"],
        "quantity": 1
    })

    # pay → invoice created automatically
    client.post(
        f"/orders/{order['id']}/pay",
        headers={"Idempotency-Key": "test-invoice-001"}
    )

    # get invoices by order
    invoices = client.get(f"/orders/{order['id']}/invoices").json()
    assert len(invoices) == 1
    invoice_id = invoices[0]['id']

    # get invoice by id
    response = client.get(f"/invoices/{invoice_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == invoice_id
    assert data['total_cents'] == 8900
    assert data['tax'] == 1780


def test_get_invoice_not_found(client):
    response = client.get(
        f"/invoices/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
    assert response.json()['detail'] == "Invoice not found"