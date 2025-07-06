# { id: (noun_name, plural_name, icon) }
MENU_ITEM_IDS = {
    "B": ("Burger", "Burgers", "🍔"),
    "S": ("Side", "Sides", "🍟"),
    "D": ("Drink", "Drinks", "🥤"),
    "DS": ("Dessert", "Desserts", "🍦"),
    "C": ("Combo", "Combos", "🥡")
}

MENU = [
    # Burgers
    {"id": "B01", "name": "Classic Beef Burger", "price": 5.50},
    {"id": "B02", "name": "Chicken Burger", "price": 5.00},
    {"id": "B03", "name": "Veggie Burger", "price": 4.80},
    {"id": "B04", "name": "Spicy Chicken Burger", "price": 5.30},
    # Sides
    {"id": "S01", "name": "French Fries", "price": 2.50},
    {"id": "S02", "name": "Onion Rings", "price": 2.80},
    {"id": "S03", "name": "Chicken Nuggets (6pc)", "price": 3.50},
    {"id": "S04", "name": "Cheese Sticks (4pc)", "price": 3.20},
    # Drinks
    {"id": "D01", "name": "Coke", "price": 1.80},
    {"id": "D02", "name": "Sprite", "price": 1.80},
    {"id": "D03", "name": "Ice lemon Tea", "price": 2.20},
    {"id": "D04", "name": "Mineral water", "price": 1.50},
    # Desserts
    {"id": "DS01", "name": "Chocolate sundae", "price": 2.80},
    {"id": "DS02", "name": "Vanilla cone", "price": 1.50},
    {"id": "DS03", "name": "Apple pie", "price": 2.30},
    {"id": "DS04", "name": "Strawberry sundae", "price": 2.80},
    # Combos (for item reference ids, just only the alphabet id = any)
    {"id": "C01", "name": "Burger + Fries + Drink", "item_ref_ids": { "Burger": (["B"], 1), "Fries": (["S01"], 1), "Drink": (["D"], 1) }, "price": 8.80},
    {"id": "C02", "name": "Nuggets + Fries + Drink", "item_ref_ids": { "Nuggets": (["S03"], 1), "Fries": (["S01"], 1), "Drink": (["D"], 1)}, "price": 8.50},
    {"id": "C03", "name": "Veggie Combo", "item_ref_ids": { "Main": (["B03"], 1), "Dessert": (["S04", "S04"], 1), "Drink": (["D04"], 1)}, "price": 8.20},
    {"id": "C04", "name": "Kids Meal", "item_ref_ids": { "Main": (["S03", "S04"], 1), "Fries": (["S01"], 1), "Dessert": (["DS"], 1), "Drink": (["D01", "D02", "D04"], 1)}, "price": 6.50}
]

DISCOUNT_RATES = {
    "student": 0.10,
    "staff": 0.08,
    "loyalty_member": 0.05
}