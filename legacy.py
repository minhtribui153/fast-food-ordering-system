# Government Details
GST = 0.09
# Restaurant Details
RESTAURANT_NAME = "Obama Fried Chicken"
ADDRESS = "#01-234 Serangoon Central, 23, Singapore 556083"
PHONE_NUMBER = "+65 9012 3456"
WEBSITE = "https://obama-fried-chicken.com.sg"
ALLOWED_ORDERS_PER_ITEM = 100

# Print Receipt Details
WIDTH_RECEIPT_TABLE_COLUMN_ID = 5
WIDTH_RECEIPT_TABLE_COLUMN_NAME = 17    # name field display width
WIDTH_RECEIPT_TABLE_COLUMN_TYPE = 12
WIDTH_RECEIPT_TABLE_COLUMN_PRICE = 9
WIDTH_RECEIPT_TABLE_COLUMN_QUANTITY = 4
WIDTH_RECEIPT_TABLE_COLUMN_DESCRIPTION = 20

import sys

# Datasets and dataset functions
from datetime import datetime

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
    {"id": "C03", "name": "Veggie Combo", "item_ref_ids": { "Main": (["B03"], 1), "Dessert": (["S04"], 1), "Drink": (["D04"], 1)}, "price": 8.20},
    {"id": "C04", "name": "Kids Meal", "item_ref_ids": { "Main": (["S03", "S04"], 1), "Fries": (["S01"], 1), "Dessert": (["DS"], 1), "Drink": (["D01", "D02", "D04"], 1)}, "price": 6.50}
]

DISCOUNT_RATES = {
    "student": 0.10,
    "staff": 0.08,
    "loyalty_member": 0.05
}

def generate_item_table(items: list[dict]):
    """Returns a 2D list of items as a table"""
    return [
        [item["id"], item["name"], f"${item["price"]:.2f}"]
        for item in items
    ]

def get_items_by_category_code(code: str):
    """Gets an item by category code"""
    return [item for item in MENU if split_item_code(item["id"])[0] == code]

def get_item_by_id(item_id: str):
    """Gets an item by its item ID"""
    found = [item for item in MENU if item["id"] == item_id]
    if len(found) == 0:
        raise Exception("Item not found")
    return found[0]

def get_items_by_ids(item_ids: list[str]):
    """
    Gets items by their ids specified
    if category_code only: Retrieves all items containing the specified category code
    """
    result = []
    for item_id in item_ids:
        [cat_code, item_num] = split_item_code(item_id)
        if item_num == "":
            result.extend(get_items_by_category_code(cat_code))
        else:
            result.append(get_item_by_id(item_id))
    return result

def parse_item_ref_ids(item_ref_ids: dict) -> list:
    """
    Parses the item_ref_ids dictionary from a combo meal.
    Returns a list of dictionaries with section as key and a dict as value:
    ```python
    {
        'section': str,
        'options': [...],
        'quantity': int,
        'locked': bool
        ...
    }
    ```
    - `'options'`: `list` of item IDs or category codes available for selection
    - `'quantity'`: how many can be selected from options
    - `'locked'`: `True` if `quantity == len(options)` (user cannot change selection)
    """
    parsed = []
    for section, (options, quantity) in item_ref_ids.items():
        if quantity > len(options):
            raise ValueError(f"Quantity for section '{section}' cannot be greater than number of options.")

        parsed_options = get_items_by_ids(options)
        parsed.append({
            'section': section,
            'options': parsed_options,
            'quantity': quantity,
            'locked': quantity == len(parsed_options)
        })
    return parsed

# Utility functions
def condense(text, max_len):
    """Truncates text for better display on screen to prevent misalignment"""
    return text if len(text) <= max_len else text[:max_len-3] + "..."

def split_item_code(item_code):
    """Splits an item code into its category code and category item number."""
    cat_code = ''
    item_num = ''
    for char in item_code:
        if char.isalpha(): cat_code += char
        else: item_num += char
    return cat_code, item_num

def compare_orders(item1, item2):
    cat_code1 = split_item_code(item1["id"])
    if item1["id"] != item2["id"]: return False
    elif cat_code1 == "C":
        for key in item1["item_ref_ids"].keys():
            if set(item1["item_ref_ids"][key]) != set(item2["item_ref_ids"][key]):
                return False
    return True

def display_table(data: list[list[str]], headers: list[str] = [], selected_index: int = -1, tab_space: int = 4):
    """Prints a formatted table (compatible with interactive menu selection)"""
    # Calculate max width for each column
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*([headers] + data if headers else data))]
    # Helper function to format a row
    def fmt_row(row): return "|" + "|".join(f" {str(cell):<{w}} " for cell, w in zip(row, col_widths)) + "|"
    # Helper function to format a line
    def fmt_line(): return "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    padding = " " * tab_space if selected_index > -1 else ""
    if len(headers) > 0:
        print(padding, fmt_line())
        print(padding, fmt_row(headers))
    print(padding, fmt_line())
    # enumerate() gives an iteration with both indexes and the element for each element
    for i, row in enumerate(data):
        # Highlight selected row if needed
        if selected_index > -1 and i == selected_index: print(f"{'> ':>{tab_space}}", fmt_row(row), "<")
        else: print(padding, fmt_row(row))
    print(padding, fmt_line())

# User data variables
cart = []

# Handling functions
def print_receipt(discount: float = 0.0):
    """Prints a receipt containing the items ordered as well as calculation"""
    # Name too long, convert to smaller variables for cleaner code
    col_id = WIDTH_RECEIPT_TABLE_COLUMN_ID
    col_name = WIDTH_RECEIPT_TABLE_COLUMN_NAME
    col_type = WIDTH_RECEIPT_TABLE_COLUMN_TYPE
    col_price = WIDTH_RECEIPT_TABLE_COLUMN_PRICE
    col_qty = WIDTH_RECEIPT_TABLE_COLUMN_QUANTITY
    col_desc = WIDTH_RECEIPT_TABLE_COLUMN_DESCRIPTION

    # Set headers accordingly
    header_fields = (
        f"{'No.':<3} {'ID':<{col_id}} {'Name':<{col_name}} "
        f"{'Description':<{col_desc}} {'Type':>{col_type}} "
        f"{'Price':>{col_price}} {'Qty':>{col_qty}}"
    )
    receipt_width = len(header_fields)

    # Calculations
    subtotal = sum(item["price"] * item["quantity"] for item in cart)
    discount_amt = round(subtotal * discount, 2)
    discounted_subtotal = subtotal - discount_amt
    gst = round(discounted_subtotal * GST, 2)
    total = round(discounted_subtotal + gst, 2)
    now = datetime.now().strftime("%d %b %Y   %H:%M")

    # Print Header
    print(f"\n{RESTAURANT_NAME:^{receipt_width}}")
    print(f"{ADDRESS:^{receipt_width}}")
    print(f"{'Tel: ' + PHONE_NUMBER:^{receipt_width}}")
    print(f"{WEBSITE:^{receipt_width}}")
    print("-" * receipt_width)
    print(f"Date: {now}")
    print("-" * receipt_width)

    # Table Body
    print(header_fields)
    print("-" * receipt_width)
    for i, item in enumerate(cart, 1):
        type_str = "Combo" if "options" in item else "À la carte"
        # Truncate name and description
        disp_name = condense(item.get('name', ''), col_name)
        disp_desc = condense(item.get('description', ''), col_desc)
        print(f"{i:<3} {item['id']:<{col_id}} {disp_name:<{col_name}} {disp_desc:<{col_desc}} {type_str:>{col_type}} "
              f"{item['price']:>{col_price}.2f} {item['quantity']:>{col_qty}}")

        # Options (for combos)
        if "options" in item:
            spaces = " " * (col_id + col_name + 6)
            for option_name, ids in item["options"].items():
                print(spaces + f"{condense(option_name, 12)}:")
                count = 1
                current_id = ""
                for item_id in ids:
                    # Check for similarity to display quantity
                    if current_id == item_id: count += 1
                    else:
                        count = 1
                        current_id = item_id
                    option_item_name = condense(str(count) + " " + get_item_by_id(item_id)['name'], col_name)
                    print(spaces + f"{option_item_name}")
    print("-" * receipt_width)

    # Display calculations
    print(f"{'Subtotal:':<{receipt_width - 10}}{subtotal:>10.2f}")
    if discount > 0.0:
        print(f"{f'Discount {discount*100:.0f}%:':<{receipt_width - 10}}-{discount_amt:>9.2f}")
    print(f"{f'GST {GST*100:.0f}%:':<{receipt_width - 10}}{gst:>10.2f}")
    print("-" * receipt_width)
    print(f"{'TOTAL:':<{receipt_width - 10}}{total:>10.2f}")
    print("-" * receipt_width)

    # Footer
    print()
    print(f"{'Thank you for dining with us!':^{receipt_width}}")
    print(f"{'We hope to see you again.':^{receipt_width}}\n")


def handle_ui_integer_selection(question: str, allowed_min: int = -sys.maxsize, allowed_max: int = sys.maxsize, back_button: bool = False):
    """Handles integer selection UI"""
    while True:
        try:
            print(question)
            if back_button: print("To go back, type 'B'")
            value = input(f">> ")
            if back_button and value == "B":
                return None
            converted_value = int(value)
            if converted_value < allowed_min:
                print(f"❌ Value cannot be below {allowed_min}")
            elif converted_value > allowed_max:
                print(f"❌ Value cannot be above {allowed_max}")
            else:
                return converted_value
        except ValueError:
            print("❌ Value must be an integer")

def handle_ui_menu_selection(
        question: str,
        options: list,
        option_icons: list = [],
        back_button: bool = False,
        confirm_button: bool = False,
        next_button: bool = False
    ):
    """Handles menu selection UI"""
    # Utility button icons
    back_icon = "⬅️ "
    confirm_icon = "✅"
    next_icon = "➡️"
    if not options:
        raise RuntimeError("Options cannot be empty")
    if option_icons and len(option_icons) != len(options):
        raise RuntimeError("Length of option_icons must match options")
    ui_icons = option_icons if len(option_icons) > 0 else [""] * len(options)
    while True:
        print(question)
        for i, (opt, icon) in enumerate(zip(options, ui_icons)):
            print(f"({i+1}) {icon + ' ' if icon else ''}{opt}")
        if confirm_button: print(f"(C) {confirm_icon} Confirm")
        if next_button: print(f"(N) {next_icon} Next")
        if back_button: print(f"(B) {back_icon} Back")
        sel = input(">> ")
        if sel == "C" and confirm_button: return "confirm"
        if sel == "N" and next_button: return "next"
        if sel == "B" and back_button: return "back"
        if sel.isdigit() and 1 <= int(sel) <= len(options): return int(sel) - 1
        print("❌ Invalid option!")

# User interface functions

def handle_edit_cart():
    """
    Handles viewing and editing the items inside the user cart
    """
    if len(cart) == 0:
        print("ℹ️  There are currently no items in your cart.")
        return
    
    table_headers = ["Index", "Code", "Category", "Name", "Price", "Quantity", "Total"]
    def show():
        """Output items in cart"""
        display_table([
            [
                str(i + 1), cart[i]["id"],
                MENU_ITEM_IDS[split_item_code(cart[i]["id"])[0]][1], cart[i]["name"],
                f"${cart[i]["price"]:.2f}",
                cart[i]["quantity"],
                f"${cart[i]["price"] * cart[i]["quantity"]:.2f}"
            ]
            for i in range(len(cart))
        ], table_headers)
        print(f"Total: ${sum(item["price"] * item["quantity"] for item in cart):.2f}")
    while True:
        show()
        print("Select items by their indices separated by commas or B to go back.")
        inputs = input(">> ").split(",")
        if len(inputs) == 0:
            print("💡 To go back, type B and press enter.")
            continue
        elif inputs[0] == "B":
            return None
        
        while True:
            # Index validation
            indices = []
            for inp in inputs:
                if not inp.strip().isdigit():
                    print(f"> '{inp.strip()}' is not a valid index")
                    continue
                elif int(inp) - 1 < 0 or int(inp) - 1 >= len(inputs):
                    print(f"> '{inp.strip()}' is out of range.")
                    continue
                indices.append(int(inp) - 1)
            if len(indices) != len(inputs):
                error_count = len(inputs) - len(indices)
                if error_count == 1:
                    print(f"Please fix this error in your input.")
                else:
                    print(f"Please fix these {len(inputs) - len(indices)} errors in your input.")
                break
            

            action = handle_ui_menu_selection(
                "What would you like to do?",
                ["Change quantity", "Edit item", "Delete item(s)"],
                ["↔️ ", "✏️ ", "🗑️ "],
                back_button=True
            )
            if action == 0:
                new_quantity = handle_ui_integer_selection("Please type in the new quantity.", allowed_min=1, allowed_max=100, back_button=True)
                if new_quantity:
                    for i in indices: cart[i]["quantity"] = new_quantity
                    break
            elif action == 1:
                if len(indices) > 1: print("❌ You can only edit 1 item at a time.")
                elif split_item_code(cart[indices[0]]["id"])[0] != "C": print("❌ Cannot edit à la carte items. You can only edit combo items.")
                else:
                    combo_selected_data = handle_edit_combo(cart[indices[0]]["id"], cart[indices[0]]["options"])
                    if combo_selected_data:
                        cart[indices[0]]["options"] = combo_selected_data
                        break
            elif action == 2:
                # Follow last index first method: Prevent errors from being raised when delete action is used
                # Sort out indices in descending order
                indices.sort(reverse=True)
                for i in indices: cart.pop(i)
                if len(cart) == 0:
                    print("ℹ️ There are currently no items in your cart.")
                    return None
                break
            elif action == "back": break
                    
def handle_edit_combo(item_id: str, preselected: dict = {}):
    """
    Handles editing of a combo meal by selecting items for each section.
    Optionally takes a `preselected` dict mapping section names to lists of selected option indices.
    """
    cat_code, _ = split_item_code(item_id)
    if cat_code != "C":
        raise ValueError("Only combo meals can be edited.")

    item_info = get_item_by_id(item_id)
    if not item_info:
        raise ValueError(f"Item with ID {item_id} not in Menu")

    # Get icon and parse combo sections
    parsed_sections = parse_item_ref_ids(item_info["item_ref_ids"])
    section_names = list(item_info["item_ref_ids"].keys())

    # Prepare initial selection state
    preselected = preselected or {}
    selected = []
    for i, section in enumerate(parsed_sections):
        sec_name = section_names[i]
        if section["locked"]:
            selected.append(list(range(len(section["options"]))))
        elif sec_name in preselected.keys():
            # Only accept valid items
            valid_indices = [i for i in range(len(section["options"])) if section["options"][i]["id"] in preselected[sec_name]]
            selected.append(valid_indices)
        else:
            selected.append([])
    
    # Legacy Menu (use input and handle_ui_menu_selection)
    result = preselected
    current_selection_index = 0
    back = False
    while current_selection_index < len(parsed_sections):
        if back:
            current_selection_index -= 1
            if current_selection_index < 0: return None
            back = False
            continue
        section = parsed_sections[current_selection_index]
        print("-" * 20)
        print(f"[ℹ️  Section {current_selection_index + 1}] {section["section"]}")
        if section.get("locked", False):
            # Locked section, just show the options
            print(f"🔒 This section is locked. Items included:")
            for option in section["options"]:
                item = get_item_by_id(option["id"])
                print(f" - {item['name']}")
            result[section["section"]] = [item["id"] for item in section["options"]]
            selected = handle_ui_menu_selection(
                "What do you want to do?",
                ["Next Section", "Previous Section"],
                ["➡️ ", "⬅️ "]
            )
            back = selected == 1
        else:
            chosen = []
            # Add saved data from result if any
            chosen += result.get(section["section"], [])

            # Do the selection part
            print(f"💡 You are allowed to select {section['quantity']} items for this section.")
            while True:
                option_names = []
                for option in section["options"]:
                    selected_mark = "✳️ " if option["id"] in chosen else "⬛"
                    option_names.append(f"{selected_mark} [{option["id"]}] {option['name']} (${option['price']:.2f})".strip())
                # Use handle_ui_menu_selection for selection, with back button
                sel = handle_ui_menu_selection(
                    f"Please select",
                    options=option_names,
                    back_button=True,
                    confirm_button=True
                )
                if sel == "confirm": break
                if sel == "back":
                    back = True
                    break
                # Find the index of the selected option
                selected_code = section["options"][sel]["id"]
                if selected_code in chosen:
                    chosen.remove(selected_code)
                else:
                    chosen.append(selected_code)
            if len(chosen) != section["quantity"] and not back:
                print(f"❌ You must select exactly {section['quantity']} item(s) for '{section["section"]}'")
                continue
            result[section["section"]] = chosen
        if not back: current_selection_index += 1
    return result

def handle_checkout():
    """Handles the checkout menu system, exits after printing receipt"""
    if len(cart) == 0:
        print("❌ No items to pay. Please order an item before proceeding to checkout.")
        return None
    
    identity = handle_ui_menu_selection(
        "Please select your identity:",
        options=["Student", "Staff", "Loyalty Member", "I am not any one of these"],
        option_icons=["🎓 ", "💼 ", "💎 ", "❌ "],
        back_button=True
    )

    if identity == 0: discount_rate = DISCOUNT_RATES["student"]
    elif identity == 1: discount_rate = DISCOUNT_RATES["staff"]
    elif identity == 2: discount_rate = DISCOUNT_RATES["loyalty_member"]
    elif identity == 3: discount_rate = 0.0
    else: return None
    
    print("Printing receipt...")
    print_receipt(discount_rate)
    exit(0)
        
def handle_food_menu(skip_to_order: bool = False):
    header_categories = [MENU_ITEM_IDS[code][1] for code in MENU_ITEM_IDS.keys()]
    header_category_icons = [MENU_ITEM_IDS[code][2] for code in MENU_ITEM_IDS.keys()]

    # Legacy UI
    while True:
        chosen_option = 1 if skip_to_order else handle_ui_menu_selection(
            "Browse menu or order?",
            options=["Browse Menu", "Order"],
            option_icons=["🔍", "✅"],
            back_button=True
        )

        if chosen_option == 0:
            while True:
                chosen_category = handle_ui_menu_selection(
                    "Select a category",
                    options=header_categories,
                    option_icons=header_category_icons,
                    back_button=True
                )
                if chosen_category == "back": break
                code = list(MENU_ITEM_IDS.keys())[int(chosen_category)]
                item_table = generate_item_table(get_items_by_category_code(code))
                display_table(item_table, ["Item ID", "Item Name", "Price"])
        elif chosen_option == 1:
            skip_to_order = False
            item_ids = [item_id["id"] for item_id in MENU]
            while True:
                print("-" * 20)
                print("Enter the item ID you would like to order")
                print("(or leave blank to go back)")
                item_id = input(">> ")

                if item_id == "":
                    break # Exit this loop, but goes back to the main food menu
                elif item_id in item_ids:
                    return item_id # Returns the item_id
                
                print("❌ Invalid item ID!")
                print("💡 If you have forgotten the item ID, you can go back and use the Browse Menu option.")
        elif chosen_option == "back": break

# Main code

# Just to make restaurant title nicer
title_header = "| " + RESTAURANT_NAME + " |"
bar_header = f"+{'-' * (len(title_header) - 2)}+"
while True:
    print(bar_header)
    print(title_header)
    print(bar_header)
    print()
    tab_selection = handle_ui_menu_selection("What would you like to do?",
        options=["Browse and Order", "View and Edit cart", "Checkout", "Quit"],
        option_icons=["🔍", "🛒", "💳", "🚪"]
    )

    if tab_selection == 0:
        selected_item = handle_food_menu()
        if selected_item == None:
            continue
        completed = False
        combo_preselected_data = {}
        while not completed:
            code, num = split_item_code(selected_item)
            if code == "C":
                # Enable combo editing
                combo_selected_data = handle_edit_combo(selected_item, combo_preselected_data)
                if combo_selected_data is None:
                    combo_preselected_data = {}
                    selected_item = handle_food_menu(True)
                    if selected_item is None:
                        # Since user chooses to go back break this loop to go back to the main loop
                        break
                    continue
                combo_preselected_data = combo_selected_data
            quantity = handle_ui_integer_selection(
                f"Please enter quantity for item {selected_item}:",
                allowed_min=1,
                allowed_max=ALLOWED_ORDERS_PER_ITEM,
                back_button=True
            )
            if quantity is None:
                if code != "C":
                    # If it is not a combo meal go back to menu selection
                    selected_item = handle_food_menu(True)
                    if selected_item is None:
                        # Since user chooses to go back break this loop to go back to the main loop
                        break
                continue
            # Store into an order variable
            added_item = get_item_by_id(selected_item)
            order: dict[str, dict | str | int] = { "id": selected_item, "name": added_item["name"], "price": added_item["price"], "quantity": quantity }
            if code == "C":
                order["options"] = combo_preselected_data
            
            overflow = False
            found_similar_item = False
            for i in range(len(cart)):
                if compare_orders(order, cart[i]):
                    total_quantity = cart[i]["quantity"] + order["quantity"]
                    if total_quantity > ALLOWED_ORDERS_PER_ITEM:
                        overflow = True
                        print(f"❌ You ordered {total_quantity} of this item. Max is {ALLOWED_ORDERS_PER_ITEM}.")
                    else:
                        cart[i]["quantity"] += order["quantity"]
                        found_similar_item = True
            
            if overflow: continue
            if not found_similar_item: cart.append(order)
            # Display added to cart message
            print(f"✅ Successfully added {quantity} item{"s" if quantity > 1 else ""} of ({order["id"]}) {order["name"]} to cart")
            completed = True
        if not completed: continue
    elif tab_selection == 1: handle_edit_cart()
    elif tab_selection == 2: handle_checkout()
    else:
        print("👋 Goodbye!")
        break