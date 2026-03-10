from uuid import UUID
from typing import Optional
from app.storage.fake_db import products


def get_product_by_id(product_id: UUID):
    for product in products:
        if product.id == product_id and product.is_active:
            return product
    return None


def list_products(
    page: int = 1,
    page_size: int = 10,
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort: Optional[str] = None,
):
    # 1. only active products are filtering
    filtered = [p for p in products if p.is_active]
    
    # 2. filtering
    if category:
        filtered = [p for p in filtered if p.category == category]

    if min_price is not None:
        filtered = [p for p in filtered if p.price_cents >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p.price_cents <= max_price]

    # 3. sorting
    if sort == 'price_asc':
        filtered = sorted(filtered, key=lambda p: p.price_cents)
    elif sort == 'price_desc':
        filtered = sorted(filtered, key=lambda p: p.price_cents, reverse=True)
    elif sort == 'newest':
        filtered = sorted(filtered, key=lambda p: p.created_at, reverse=True)

    # 4. total after filtration
    total = len(filtered)

    # 5. paginating
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]

    return {
        'items': items,
        'page': page,
        'page_size': page_size,
        'total': total,
    }