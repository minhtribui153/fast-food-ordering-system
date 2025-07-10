RESTAURANT_NAME = "🍽  Soviet Union Restaurant"
CART = []

import sys

from datasets import *
from utils import *
import time

# Helper functions

def handle_ui_integer_selection(question: str, allowed_min: int = -sys.maxsize, allowed_max: int = sys.maxsize, default: int = 0, back_button: bool = False):
    """Handles integer selection UI"""
    if sys.stdin.isatty():
        selected_number = default
        def show():
            clear_console()
            print(question)
            print(f"    | [Left] < (-) {selected_number} (+) > [Right]")
            print(f"    | [Enter] Confirm")
            if back_button:
                print(f"    | [Q] Back")
            print(f"    | Note: Use numbers to type, minus symbol to negate")
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
                    selected_number = 0
            elif key == "enter":
                return selected_number
            elif key == "minus":
                selected_number = min(-selected_number, allowed_min)
            elif key == "q" and back_button:
                return None
    else:
        while True:
            try:
                print(question)
                if back_button: print("To go back, type 'B'")
                value = input(f">> ")
                if back_button and value == "B":
                    return None
                converted_value = int(value)
                if converted_value < allowed_min:
                    print(f"Error: Value cannot be below {allowed_min}")
                elif converted_value > allowed_max:
                    print(f"Error: Value cannot be above {allowed_max}")
                else:
                    return converted_value
            except ValueError:
                print("Error: Value must be an integer")

def handle_ui_menu_selection(question: str, options: list, option_icons: list = [], back_button: bool = False):
    """Handles menu selection UI"""
    back_icon = "⬅️"
    if not options:
        raise RuntimeError("Options cannot be empty")
    if option_icons and len(option_icons) != len(options):
        raise RuntimeError("Length of option_icons must match options")
    ui_options = options[:] + (["Back"] if back_button else [])
    ui_icons = (option_icons[:] if option_icons else [""] * len(options)) + ([back_icon] if back_button else [])
    if sys.stdin.isatty():
        idx, last_lines = 0, 0
        while True:
            lines = [question] + [
                f"{' >> |' if i == idx else '    |'} {icon + ' ' if icon else ''}{opt}"
                for i, (opt, icon) in enumerate(zip(ui_options, ui_icons))
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
        return ui_options[idx]
    else:
        while True:
            print(question)
            for i, (opt, icon) in enumerate(zip(options, ui_icons)):
                print(f"({i+1}) {icon + ' ' if icon else ''}{opt}")
            if back_button:
                print(f"(B) {back_icon} Back")
            sel = input(">> ")
            if sel == "B" and back_button:
                return "Back"
            if sel.isdigit() and 1 <= int(sel) <= len(options):
                return options[int(sel) - 1]
            print("Error: Invalid option!")
            # Simplified and commented version of handle_edit_combo

# User interface functions

def handle_edit_cart():
    pass

def handle_edit_combo(item_id: str, preselected: dict = {}):
    """
    Allows editing of a combo meal by selecting items for each section.
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
        elif sec_name in preselected:
            # Only accept valid indices
            valid_indices = [idx for idx in preselected[sec_name] if 0 <= idx < len(section["options"])]
            selected.append(valid_indices[:section["quantity"]])
        else:
            selected.append([])

    if sys.stdin.isatty():
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
                print()
            else:
                # Show options for current section
                section = parsed_sections[tab - 1]
                items = generate_item_table(section["options"])
                allowed_items = len(items)
                if section["locked"]:
                    display_table(items, ["Item ID", "Item Name", "Price"])
                    print(" (Section is locked; cannot edit)")
                    print()
                else:
                    # Show selectable items with checkboxes
                    table = [
                        (["[X]"] if i in selected[tab - 1] else ["[ ]"]) + list(row)
                        for i, row in enumerate(items)
                    ]
                    display_table(table, ["", "Item ID", "Item Name", "Price"], sel_idx)
                    print()
                    print("| [Spacebar] Select/Deselect item")
                    print("| [Up/Down] Move dropdown cursor")
            print("| [Left/Right] Select section")
            print("| [Enter] Save changes")
            print("| [Q] Back")
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
                            section["options"][j]["id"] for j in selected[i]
                        ]
                if not incomplete_sections:
                    return result
                display_modal("Action(s) required", f"You have not completed {len(incomplete_sections)} section(s):\n" + "\n".join(incomplete_sections), "⚠️", 100)
            elif key == "q":
                return None
            # Clamp selection index
            if sel_idx >= max_idx:
                sel_idx = max(max_idx - 1, 0)
    else:
        # Legacy Menu (use input and handle_ui_menu_selection)
        result = {}
        for i, section in enumerate(parsed_sections):
            if section.get("locked", False):
                # Locked section, just show the options
                print(f"Section '{section["section"]}' is locked. Items included:")
                for option in section["options"]:
                    item = get_item_by_id(option["id"])
                    print(f" - {item['name']}")
                result[section["section"]] = section["options"]
            else:
                while True:
                    chosen = []
                    # Use preselected if available
                    pre = preselected.get(section["section"], [])
                    for code in pre:
                        try:
                            idx = section["options"].index(code)
                            chosen.append(idx)
                        except ValueError:
                            continue
                    while len(chosen) < section["quantity"]:
                        print(f"Select {section['quantity']} item(s) for section '{section["section"]}':")
                        option_names = []
                        for idx, option in enumerate(section["options"]):
                            item = get_item_by_id(option["id"])
                            selected_mark = "(selected)" if idx in chosen else ""
                            option_names.append(f"{item['name']} ${item['price']:.2f} {selected_mark}".strip())
                        # Use handle_ui_menu_selection for selection, with back button
                        sel = handle_ui_menu_selection(
                            f"Choose option {len(chosen)+1} for '{section["section"]}'",
                            options=option_names,
                            back_button=True
                        )
                        if sel == "Back":
                            # Go back to previous section if possible
                            if i == 0:
                                return None
                            # Remove previous section from result and restart from there
                            prev_section_name = parsed_sections[i-1]["section"]
                            if prev_section_name in result:
                                del result[prev_section_name]
                            # Restart the whole process from previous section
                            return handle_edit_combo(item_id, preselected)
                        # Find the index of the selected option
                        try:
                            idx = option_names.index(sel)
                        except ValueError:
                            print("Invalid selection.")
                            continue
                        if idx in chosen:
                            print("Already selected.")
                        else:
                            chosen.append(idx)
                    if len(chosen) != section["quantity"]:
                        print(f"Error: You must select exactly {section['quantity']} item(s) for '{section["section"]}'.")
                        continue
                    result[section["section"]] = [section["options"][i] for i in chosen]
                    break
        return result
        
def handle_food_menu(skip_to_order: bool = False):
    header_categories = [MENU_ITEM_IDS[code][1] for code in MENU_ITEM_IDS.keys()]
    header_category_icons = [MENU_ITEM_IDS[code][2] for code in MENU_ITEM_IDS.keys()]
    header_category_items = [get_items_by_category_code(code) for code in MENU_ITEM_IDS.keys()]

    if sys.stdin.isatty():
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
            print()
            print("[Left/Right arrows] Select category")
            print("[Up/Down arrows] Select item")
            print("[Enter] confirm selection")
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
    else:
        # Legacy UI
        while True:
            chosen_option = "Order" if skip_to_order else handle_ui_menu_selection(
                "Browse menu or order?",
                options=["Browse Menu", "Order"],
                option_icons=["🔍", "✅"],
                back_button=True
            )

            if chosen_option == "Browse Menu":
                while True:
                    chosen_category = handle_ui_menu_selection(
                        "Select a category",
                        options=header_categories,
                        option_icons=header_category_icons,
                        back_button=True
                    )
                    if chosen_category not in header_categories: break
                    code = list(MENU_ITEM_IDS.keys())[header_categories.index(chosen_category)]
                    item_table = generate_item_table(get_items_by_category_code(code))
                    display_table(item_table, ["Item ID", "Item Name", "Price"])
            elif chosen_option == "Order":
                item_ids = [item_id["id"] for item_id in MENU]
                while True:
                    print("| Enter the item ID you would like to order")
                    print("| (or leave blank to go back)")
                    item_id = input("| >> ")

                    if item_id == "":
                        break # Exit this loop, but goes back to the main food menu
                    elif item_id in item_ids:
                        return item_id # Returns the item_id
                    
                    print("Invalid item ID!")
                    print("If you have forgotten the item ID, you can go back and use the Browse Menu option.")
            elif chosen_option == "Back": break

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

    if tab_selection == "Browse and Order":
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
                if combo_selected_data == None:
                    selected_item = handle_food_menu(True)
                    if selected_item == None:
                        # Since user chooses to go back break this loop to go back to the main loop
                        break
                    continue
                combo_preselected_data = combo_selected_data
            quantity = handle_ui_integer_selection(f"Please enter quantity for item {selected_item}:", back_button=True)
            if quantity == None:
                if code != "C":
                    # If it is not a combo meal go back to menu selection
                    selected_item = handle_food_menu(True)
                    if selected_item == None:
                        # Since user chooses to go back break this loop to go back to the main loop
                        break
                continue
            # store into an order variable
            order: dict[str, dict | str] = { "code": selected_item }
            if code == "C":
                order["options"] = combo_preselected_data
            completed = True
        if not completed: continue
    elif tab_selection == "View and Edit cart": print("Not yet")
    elif tab_selection == "Checkout": print("Not yet")
    else:
        print("👋 Goodbye!")
        time.sleep(1)
        break