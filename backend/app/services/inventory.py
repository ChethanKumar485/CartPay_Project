"""
CartPay — Inventory Service
Mock product catalogue. Replace with a database query in production.
"""

from datetime import date, timedelta
from app.models.schemas import Item

_today = date.today

def _exp(days: int) -> date:
    return _today() + timedelta(days=days)


ALL_ITEMS: list[Item] = [
    Item(item_id="I001", barcode="8901030123456", name="Basmati Rice 1kg",        category="Staples",       price=185,  reference_weight=1000, expiry_date=_exp(180)),
    Item(item_id="I002", barcode="8901030123457", name="Toor Dal 1kg",            category="Staples",       price=145,  reference_weight=1000, expiry_date=_exp(200)),
    Item(item_id="I003", barcode="8901030123458", name="Wheat Atta 5kg",          category="Staples",       price=260,  reference_weight=5000, expiry_date=_exp(120)),
    Item(item_id="I004", barcode="8901030123459", name="Toned Milk 1L",           category="Dairy",         price=64,   reference_weight=1030, expiry_date=_exp(2)),
    Item(item_id="I005", barcode="8901030123460", name="Salted Butter 500g",      category="Dairy",         price=270,  reference_weight=510,  expiry_date=_exp(90)),
    Item(item_id="I006", barcode="8901030123461", name="Fresh Curd 400g",         category="Dairy",         price=45,   reference_weight=410,  expiry_date=_exp(1),  discount_pct=10),
    Item(item_id="I007", barcode="8901030123462", name="Brown Bread 400g",        category="Bakery",        price=55,   reference_weight=400,  expiry_date=_exp(1),  discount_pct=10),
    Item(item_id="I008", barcode="8901030123463", name="Digestive Biscuits 250g", category="Snacks",        price=60,   reference_weight=255,  expiry_date=_exp(150)),
    Item(item_id="I009", barcode="8901030123464", name="Potato Chips 90g",        category="Snacks",        price=30,   reference_weight=92,   expiry_date=_exp(100)),
    Item(item_id="I010", barcode="8901030123465", name="Mixed Nuts 200g",         category="Snacks",        price=220,  reference_weight=205,  expiry_date=_exp(180)),
    Item(item_id="I011", barcode="8901030123466", name="Orange Juice 1L",         category="Beverages",     price=110,  reference_weight=1040, expiry_date=_exp(10)),
    Item(item_id="I012", barcode="8901030123467", name="Green Tea 25 bags",       category="Beverages",     price=150,  reference_weight=50,   expiry_date=_exp(365)),
    Item(item_id="I013", barcode="8901030123468", name="Shampoo 340ml",           category="Personal Care", price=210,  reference_weight=360,  expiry_date=_exp(365)),
    Item(item_id="I014", barcode="8901030123469", name="Toothpaste 150g",         category="Personal Care", price=95,   reference_weight=160,  expiry_date=_exp(365)),
    Item(item_id="I015", barcode="8901030123470", name="Dish Wash Liquid 500ml",  category="Household",     price=99,   reference_weight=520,  expiry_date=_exp(365)),
    Item(item_id="I016", barcode="8901030123471", name="Detergent Powder 1kg",    category="Household",     price=130,  reference_weight=1000, expiry_date=_exp(365)),
]

_barcode_index: dict[str, Item] = {i.barcode: i for i in ALL_ITEMS}


def get_item_by_barcode(barcode: str) -> Item | None:
    return _barcode_index.get(barcode)


def search_items(query: str) -> list[Item]:
    q = query.lower()
    return [i for i in ALL_ITEMS if q in i.name.lower() or q in i.category.lower()]
