RESTAURANT_NAME = "Obama Fried Chicken"
GST = 0.09
ALLOWED_ORDERS_PER_ITEM = 100
CART = []

import sys
from datasets import *
from utils import *
import time

if not sys.stdin.isatty():
    print("=== NOT SUPPORTED")
    print("This program cannot be run on pseudo-based terminals.")
    print("Please run the legacy.py python program instead.")
    exit(1)

# Helper functions

def handle_ui_integer_selection(question: str, allowed_min: int = -sys.maxsize, allowed_max: int = sys.maxsize, back_button: bool = False):
    """Handles integer selection UI"""
    default = allowed_min if allowed_min > 0 else 0
    selected_number = default
    def show():
        clear_console()
        print(question)
        print(f"    | [Left] < (-) {selected_number} (+) > [Right]")
        print(f"    | [Enter] Confirm")
        if back_button:
            print(f"    | [Q] Back")
        print(f"    | 💡 Use numbers to type, minus symbol to negate")
    while True:
        show()
        key = handle_input()
        if key is None: continue
        elif key == "left":
            selected_number = max(selected_number - 1, allowed_min)
        elif key == "right":
            selected_number = min(selected_number + 1, allowed_max)
        elif key in "1234567890":
            string_num = str(selected_number) + key
            try:
                converted_num = int(string_num)
            except ValueError:
                continue
            if allowed_min <= converted_num <= allowed_max:
                selected_number = converted_num
        elif key == "backspace":
            curr_string = str(selected_number)[:-1]
            try:
                selected_number = int(curr_string)
            except ValueError:
                selected_number = default
        elif key == "enter":
            return selected_number
        elif key == "minus":
            if selected_number > 0:
                selected_number = max(-selected_number, allowed_min)
            else:
                selected_number = min(-selected_number, allowed_max)
        elif key == "q" and back_button:
            return None

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
    back_icon = "⬅️"
    confirm_icon = "✅"
    next_icon = "➡️"
    if not options:
        raise RuntimeError("Options cannot be empty")
    if option_icons and len(option_icons) != len(options):
        raise RuntimeError("Length of option_icons must match options")
    ui_options = (
        options[:]
        + (["Confirm"] if back_button else [])
        + (["Next"] if next_button else [])
        + (["Back"] if confirm_button else [])
    )
    ui_icons = ((
        option_icons[:] if option_icons else [""] * len(options))
        + ([confirm_icon] if confirm_button else [])
        + ([next_icon] if next_button else [])
        + ([back_icon] if back_button else [])
    )
    idx, last_lines = 0, 0
    while True:
        lines = [question] + [
            f"{' >> |' if i == idx else '    |'} {icon + ' ' if icon else ''}{opt}"
            for i, (opt, icon) in enumerate(zip(ui_options, ui_icons))
        ] + [
            "-----",
            "[Up/Down arrows] Move selection cursor",
            "[Enter] Confirm selection"
        ]
        if last_lines > 0:
            sys.stdout.write('\r')
            for _ in range(last_lines):
                sys.stdout.write('\x1b[1A\x1b[2K')
        print("\n".join(lines), end='', flush=True)
        last_lines = len(lines)
        key = handle_input()
        print()
        if key == "up" and idx > 0: idx -= 1
        elif key == "down" and idx < len(ui_options) - 1: idx += 1
        elif key == "enter": break
    sys.stdout.write('\r')
    for _ in range(last_lines):
        sys.stdout.write('\x1b[1A\x1b[2K')
    sys.stdout.flush()
    # Utility buttons
    if ui_options[idx] == "Back": return "back"
    if ui_options[idx] == "Next": return "next"
    if ui_options[idx] == "Confirm": return "confirm"
    return idx

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
    current_index = 0
    def show():
        """Display to console terminal and return num of items allowed to choose"""
        clear_console()
        display_table([
            [
                str(i + 1), CART[i]["id"],
                MENU_ITEM_IDS[split_item_code(CART[i]["id"])[0]][1], CART[i]["name"],
                f"${CART[i]["item_price"]:.2f}",
                (f"- {CART[i]["quantity"]:^{len(table_headers[5])}} +" if current_index == i else f"  {CART[i]["quantity"]:^{len(table_headers[5])}}  "),
                f"${CART[i]["item_price"] * CART[i]["quantity"]:.2f}"
            ]
            for i in range(len(CART))
        ], table_headers, selected_index=current_index)
        print("---")
        print("[Up/Down arrows] Move selection cursor")
        print("[Left/Right arrows] Update quantity")
        print("[Enter] Edit selection")
        print("[Backspace] Delete selection")
    while True:
        show()
        key = handle_input()
        if key == "left":
            CART[current_index]["quantity"] = max(CART[current_index]["quantity"] - 1, 1)
        elif key == "right":
            CART[current_index]["quantity"] = min(CART[current_index]["quantity"] + 1, ALLOWED_ORDERS_PER_ITEM)
        elif key == "up":
            current_index = max(current_index - 1, 0)
        elif key == "down":
            current_index = min(current_index + 1, len(CART) - 1)
        elif key == "enter":
            current = CART[current_index]
            # Edit a combo meal
            category_code, _ = split_item_code(current["id"])
            if category_code == "C":
                # Enable combo editing
                combo_selected_data = handle_edit_combo(current["id"], current["options"])
                if combo_selected_data is None:
                    continue
                CART[current_index]["options"] = combo_selected_data
                display_modal(
                    "Saved changes to Cart",
                    f"Successfully saved new item data to cart:\n - ({order["id"]}) {order["name"]}",
                    "success",
                )
            else:
                display_modal("Cannot edit item", f"({current["id"]}) {current["name"]} is an à la carte item. You can only edit combo items.", "error")
        elif key == "backspace":
            CART.pop(current_index)
            current_index = 0
            if len(CART) == 0:
                display_modal("No items in Cart", (
                    "There are currently no items in your cart. "
                    "Please order an item through the Browse and Order section in order to view this section"
                ), max_characters_before_newline=60)
                break

        elif key == "q":
            return None

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
    icon = MENU_ITEM_IDS[cat_code][2]
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

    # UI state
    tab = 0  # 0 = info, 1+ = section index
    sel_idx = 0  # selection index within section

    def show():
        """Display to console terminal and return num of items allowed to choose"""
        clear_console()
        title = f"| {icon} Edit Combo Meal ({item_id}) |"
        line = f"+{'-' * (len(title) - 1)}+"
        allowed_items = 0
        print(line)
        print(title)
        display_topbar(["Information"] + section_names, tab, top_line=line)
        if tab == 0:
            # Show combo info and current selections
            info = [["Name", item_info['name']], ["Price", f"${item_info['price']:.2f}"]]
            section_items = []
            for i, section in enumerate(parsed_sections):
                if section["locked"]:
                    chosen = ", ".join(item["name"] for item in section["options"])
                elif len(selected[i]) == section["quantity"]:
                    chosen = ", ".join(section["options"][j]["name"] for j in selected[i])
                else:
                    chosen = "(Not completed)"
                section_items.append([section_names[i], chosen, section["quantity"]])
            display_table(info)
            display_table(section_items, ["Section", "Selected", "Quantity"])
            print("-----")
        else:
            # Show options for current section
            section = parsed_sections[tab - 1]
            items = generate_item_table(section["options"])
            allowed_items = len(items)
            if section["locked"]:
                display_table(items, ["Item ID", "Item Name", "Price"])
                print(" (Section is locked; cannot edit)")
                print("-----")
            else:
                # Show selectable items with checkboxes
                table = [
                    (["[X]"] if i in selected[tab - 1] else ["[ ]"]) + list(row)
                    for i, row in enumerate(items)
                ]
                display_table(table, ["", "Item ID", "Item Name", "Price"], sel_idx)
                print("-----")
                print("[Spacebar] Select/Deselect item")
                print("[Up/Down] Move selection cursor")
        print("[Left/Right] Move category cursor")
        print("[Enter] Save changes")
        print("[Q] Back")
        return allowed_items

    while True:
        max_idx = show()
        key = handle_input()
        if key == "left":
            tab = max(tab - 1, 0)
            sel_idx = 0
        elif key == "right":
            tab = min(tab + 1, len(section_names))
            sel_idx = 0
        elif key == "up":
            sel_idx = max(sel_idx - 1, 0)
        elif key == "down":
            sel_idx = min(sel_idx + 1, max(max_idx - 1, 0))
        elif key == "spacebar" and tab > 0:
            section = parsed_sections[tab - 1]
            if not section["locked"] and 0 <= sel_idx < max_idx:
                if sel_idx in selected[tab - 1]:
                    selected[tab - 1].remove(sel_idx)
                else:
                    if len(selected[tab - 1]) < section["quantity"]:
                        selected[tab - 1].append(sel_idx)
        elif key == "enter":
            # Validate selections
            result = {}
            incomplete_sections = []
            for i, section in enumerate(parsed_sections):
                if len(selected[i]) < section["quantity"]:
                    incomplete_sections.append(f">> {section['section']}")
                else:
                    result[section["section"]] = [
                        section["options"][j]["id"] for j in selected[i] # j is the selected index
                    ]
            if not incomplete_sections:
                return result
            display_modal("Action(s) required", f"You have not completed {len(incomplete_sections)} section(s):\n" + "\n".join(incomplete_sections), "warning", 100)
        elif key == "q":
            return None
        # Clamp selection index
        if sel_idx >= max_idx:
            sel_idx = max(max_idx - 1, 0)
        
def handle_food_menu():
    header_categories = [MENU_ITEM_IDS[code][1] for code in MENU_ITEM_IDS.keys()]
    header_category_items = [get_items_by_category_code(code) for code in MENU_ITEM_IDS.keys()]

    # Production UI
    cat_index = 0
    item_index = 0

    item_table = generate_item_table(header_category_items[cat_index])

    def display_content():
        title = f"| 📖 Menu |"
        line = f"+{'-' * (len(title) - 1)}+"
        clear_console()
        print(line)
        print(title)
        display_topbar(header_categories, cat_index, top_line=line)
        display_table(item_table, ["Item ID", "Item Name", "Price"], item_index)
        print("-----")
        print("[Left/Right arrows] Move category cursor")
        print("[Up/Down arrows] Move selection cursor")
        print("[Enter] Confirm selection")
        print("[Q] Go back")

    while True:
        display_content()
        key = handle_input()
        if key in ["left", "right", "up", "down", "enter", "q"]:
            # Clamp values for each key
            if key == "left":
                cat_index = max(cat_index - 1, 0)
                item_index = 0
            elif key == "right":
                cat_index = min(cat_index + 1, len(header_categories) - 1)
                item_index = 0
            elif key == "up":
                item_index = max(item_index - 1, 0)
            elif key == "down":
                item_index = min(item_index + 1, len(item_table) - 1)
            elif key == "enter":
                return str(item_table[item_index][0])  # Return selected item ID
            elif key == "q":
                return None
        item_table = generate_item_table(header_category_items[cat_index])
        # Clamp item_index if item_table shrinks
        if item_index >= len(item_table):
            item_index = max(len(item_table) - 1, 0)

# Main code

# Just to make restaurant title nicer
title_header = "| " + RESTAURANT_NAME + " |"
bar_header = f"+{'-' * (len(title_header) - 2)}+"
while True:
    clear_console()
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
                    selected_item = handle_food_menu()
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
                    selected_item = handle_food_menu()
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
                        display_modal(
                            "Order overflow",
                            f"You have reached to {total_quantity} orders for this item. Maximum orders allowed for each item is {ALLOWED_ORDERS_PER_ITEM}.",
                            "error"
                        )
                    else:
                        CART[i]["quantity"] += order["quantity"]
                        found_similar_item = True
            
            if overflow: continue
            if not found_similar_item: CART.append(order)
            # Display added to cart message
            display_modal(
                "Added to Cart",
                f"Successfully added this item to cart:\n - ({order["id"]}) {order["name"]}\n - Quantity: {quantity}",
                "success",
            )
            completed = True
        if not completed: continue
    elif tab_selection == 1: handle_edit_cart()
    elif tab_selection == 2: print("Not yet")
    else:
        print("👋 Goodbye!")
        time.sleep(1)
        break