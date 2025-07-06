
import sys

from datasets import *
from utils import *
import time

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
            if last_lines:
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

# Program logic
def handle_edit_combo(item_id: str):
    cat_code, _ = split_item_code(item_id)
    if cat_code != "C": raise ValueError("Bro you are supposed to edit a combo meal.")

    item_info = get_item_by_id(item_id)
    if not item_info: raise ValueError(f"Item with ID {item_id} not in Menu")

    [_, _, icon] = MENU_ITEM_IDS[cat_code]
    parsed_item_ref_ids = parse_item_ref_ids(item_info["item_ref_ids"])
    sections = list(item_info["item_ref_ids"].keys())
    uncompleted_sections = [] + sections

    if sys.stdin.isatty():
        topbar_index = 0
        selection_index = 0
        selected_indices = []

        def display_content():
            selection_length = 0
            title = f"| {icon} Edit Combo Meal ({item_id}) |"
            line = f"+{'-' * (len(title) - 1)}+" # - 1 more because of icon misalignment
            clear_console()
            print(line)
            print(title)
            display_topbar(["Information"] + uncompleted_sections, topbar_index, top_line=line)
            if topbar_index == 0:
                selection_length = 0
                info_table = [
                    ["Name", item_info['name']],
                    ["Price", f"${item_info['price']:.2f}"]
                ]
                sections_table = [
                    [section, "Not completed"]
                    for section in sections
                ]
                display_table(info_table)
                display_table(sections_table, ["Section", "Items"])
            else:
                selected_section = parsed_item_ref_ids[topbar_index - 1]
                item_table = generate_item_table(selected_section["options"])
                if selected_section["locked"]:
                    selection_length = 0
                    display_table(item_table, ["Item ID", "Item Name", "Price"])
                    print(" (You are not allowed to make changes as this section is locked)")
                else:
                    selection_length = len(item_table)
                    item_selection_table = [
                        (["[X]"] + item_table[i]) if i in selected_indices
                        else (["[ ]"] + item_table[i])
                        for i in range(selection_length)
                    ]
                    display_table(item_selection_table, ["", "Item ID", "Item Name", "Price"], selection_index)
            return selection_length

        while True:
            selection_length = display_content()
            key = handle_input()
            if key in ["left", "right", "up", "down", "enter", "q", "spacebar"]:
                # Clamp values for each key
                if key == "left":
                    topbar_index = max(topbar_index - 1, 0)
                    selection_index = 0
                    selected_indices = []
                elif key == "right":
                    topbar_index = min(topbar_index + 1, len(uncompleted_sections))
                    selection_index = 0
                    selected_indices = []
                elif key == "up":
                    selection_index = max(selection_index - 1, 0)
                elif key == "down":
                    selection_index = min(selection_index + 1, max(selection_length - 1, 0))
                elif key == "spacebar":
                    # Only allow selection if not on info tab and section is not locked
                    if topbar_index > 0:
                        selected_section = parsed_item_ref_ids[topbar_index - 1]
                        if not selected_section["locked"] and 0 <= selection_index < selection_length:
                            if selection_index in selected_indices:
                                selected_indices.remove(selection_index)
                            else:
                                selected_indices.append(selection_index)
                elif key == "enter":
                    pass
                elif key == "q":
                    break
            # Clamp selection_index if item_table shrinks
            if selection_index >= selection_length:
                selection_index = max(selection_length - 1, 0)

        

def handle_food_menu():
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
                    if item_table:
                        return item_table[item_index][0]  # Return selected item ID
                    else:
                        return None
                elif key == "q":
                    break
            item_table = generate_item_table(header_category_items[cat_index])
            # Clamp item_index if item_table shrinks
            if item_index >= len(item_table):
                item_index = max(len(item_table) - 1, 0)
    else:
        # Legacy UI
        while True:
            chosen_option = handle_ui_menu_selection(
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



handle_edit_combo("C01")
exit(0)
# Main code function
RESTAURANT_NAME = "Soviet Union Restaurant"

# Just to make restaurant title nicer
title_header = "| " + RESTAURANT_NAME + " |"
bar_header = f"+{'-' * (len(title_header) - 2)}+"
space = "    |"

print(bar_header)
print(title_header)
print(bar_header)
while True:
    clear_console()
    tab_selection = handle_ui_menu_selection("What would you like to do?",
        options=["Browse and Order", "View and Edit cart", "Checkout", "Quit"],
        option_icons=["🔍", "🛒", "💳", "🚪"]
    )

    if tab_selection == "Browse and Order": handle_food_menu()
    elif tab_selection == "View and Edit cart": print("Not yet")
    elif tab_selection == "Checkout": print("Not yet")
    else: break