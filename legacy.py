RESTAURANT_NAME = "Obama Fried Chicken"
ALLOWED_ORDERS_PER_ITEM = 100
CART = []

import sys
from datasets import *
from utils import *

# Helper functions

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
    ui_icons = ((
        option_icons[:] if option_icons else [""] * len(options))
        + ([confirm_icon] if confirm_button else [])
        + ([next_icon] if next_button else [])
        + ([back_icon] if back_button else [])
    )
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
    if len(CART) == 0:
        if sys.stdin.isatty():
            display_modal("No items in Cart", (
                "There are currently no items in your cart. "
                "Please order an item through the Browse and Order section in order to view this section"
            ), max_characters_before_newline=60)
        else:
            print("ℹ️ There are currently no items in your cart.")
        return
    
    table_headers = ["Index", "Code", "Category", "Name", "Price", "Quantity", "Total"]
    def show():
        """Output items in cart"""
        display_table([
            [
                str(i + 1), CART[i]["id"],
                MENU_ITEM_IDS[split_item_code(CART[i]["id"])[0]][1], CART[i]["name"],
                f"${CART[i]["item_price"]:.2f}",
                CART[i]["quantity"],
                f"${CART[i]["item_price"] * CART[i]["quantity"]:.2f}"
            ]
            for i in range(len(CART))
        ], table_headers)
    while True:
        show()
        print("Select items their indices separated by commas or B to go back.")
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
        
            print("What would you like to do?")
            print("(C)hange quantity")
            print("(E)Edit item")
            print("(D)elete item(s)")
            print("(B)ack")
            action = input(">> ").upper()
            if action not in ['C', 'E', 'D', 'B']: print("❌ Invalid option!")
            elif action == "C":
                new_quantity = handle_ui_integer_selection("Please type in the new quantity.", allowed_min=1, allowed_max=100, back_button=True)
                if new_quantity:
                    for i in indices: CART[i]["quantity"] = new_quantity
                    break
            elif action == "E":
                if len(indices) > 1: print("❌ You can only edit 1 item at a time.")
                elif split_item_code(CART[indices[0]]["id"])[0] != "C": print("❌ Cannot edit à la carte items. You can only edit combo items.")
                else:
                    combo_selected_data = handle_edit_combo(CART[indices[0]]["id"], CART[indices[0]]["options"])
                    if combo_selected_data:
                        CART[indices[0]]["options"] = combo_selected_data
                        break
            elif action == "D":
                # Follow last index first method: Prevent errors from being raised when delete action is used
                # Sort out indices in descending order
                indices.sort(reverse=True)
                for i in indices: CART.pop(i)
                if len(CART) == 0:
                    print("ℹ️ There are currently no items in your cart.")
                    return None
                break
            elif action == "B": break
                    
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
            result[section["section"]] = section["options"]
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
            order: dict[str, dict | str | int] = { "id": selected_item, "name": added_item["name"], "item_price": added_item["price"], "quantity": quantity }
            if code == "C":
                order["options"] = combo_preselected_data
            
            overflow = False
            found_similar_item = False
            for i in range(len(CART)):
                if compare_orders(order, CART[i]):
                    total_quantity = CART[i]["quantity"] + order["quantity"]
                    if total_quantity > ALLOWED_ORDERS_PER_ITEM:
                        overflow = True
                        print(f"❌ You ordered {total_quantity} of this item. Max is {ALLOWED_ORDERS_PER_ITEM}.")
                    else:
                        CART[i]["quantity"] += order["quantity"]
                        found_similar_item = True
            
            if overflow: continue
            if not found_similar_item: CART.append(order)
            # Display added to cart message
            print(f"✅ Successfully added {quantity} item{"s" if quantity > 1 else ""} of ({order["id"]}) {order["name"]} to cart")
            completed = True
        if not completed: continue
    elif tab_selection == 1: handle_edit_cart()
    elif tab_selection == 2: print("Not yet")
    else:
        print("👋 Goodbye!")
        break