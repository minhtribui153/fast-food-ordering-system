
import sys

from datasets import *
from utils import *

# Utility functions
def get_items_by_category_code(code: str):
    """Gets an item by category code"""
    return [item for item in MENU if split_item_code(item["id"])[0] == code]

def get_item_by_id(item_id: str):
    """Gets an item by its item ID"""
    found = [item for item in MENU if item["id"] == item_id]
    return found[0] if len(found) > 0 else None


def handle_ui_menu_selection(question: str, options: list, option_icons: list = [], back_button: bool = False):
    """Handles menu selection UI"""
    back_icon = "⬅️"
    if not options:
        raise RuntimeError("Options cannot be empty")
    if option_icons and len(option_icons) != len(options):
        raise RuntimeError("Length of option_icons must match options")
    ui_options = options[:]
    ui_icons = option_icons[:] if option_icons else [""] * len(options)
    if back_button:
        ui_options.append("Back")
        ui_icons.append(back_icon)
    if sys.stdin.isatty():
        idx = 0
        while True:
            print("\033c", end="")
            print(question)
            for i, (opt, icon) in enumerate(zip(ui_options, ui_icons)):
                prefix = " >> |" if i == idx else "    |"
                print(f"{prefix} {icon + ' ' if icon else ''}{opt}")
            key = handle_input()
            if key == "up" and idx > 0: idx -= 1
            elif key == "down" and idx < len(ui_options) - 1: idx += 1
            elif key == "enter": break
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
def handle_edit_combo(item_id: str, side = 0):
    cat_code, item_num = split_item_code(item_id)
    if cat_code != "C": raise ValueError("Bro you are supposed to edit a combo meal.")
    item_info = get_item_by_id(item_id)
    if not item_info: raise ValueError(f"Item with ID {item_id} not in Menu")

    [_, _, icon] = MENU_ITEM_IDS[cat_code]
    uncompleted_sections = list(item_info["item_ref_ids"].keys())

    if sys.stdin.isatty():
        def display_content():
            title = f"| {icon} Edit Combo Meal ({item_id}) |"
            line = f"+{"-" * (len(title) - 1)}+" # - 1 more because of icon misalignment
            print("\033c", end="")
            print(line)
            print(title)
            display_topbar(["Information"] + uncompleted_sections, 0, top_line=line)
            print(f"| Name  | {item_info["name"]}")
            print(f"| Price | ${item_info["price"]:.2f}")
        display_content()

def handle_food_menu():
    header_categories = [MENU_ITEM_IDS[code][1] for code in MENU_ITEM_IDS.keys()]
    header_category_icons = [MENU_ITEM_IDS[code][2] for code in MENU_ITEM_IDS.keys()]
    header_category_codes = list(MENU_ITEM_IDS.keys())
    if sys.stdin.isatty():
        # Production UI
        cat_index = 0
        item_index = 0
        header_categories = [MENU_ITEM_IDS[code][1] for code in MENU_ITEM_IDS.keys()]
        header_category_codes = list(MENU_ITEM_IDS.keys())

        item_table = [
            [item["id"], item["name"], item["price"]]
            for item in get_items_by_category_code(header_category_codes[cat_index])
        ]

        def display_content():
            title = f"| 📖 Menu |"
            line = f"+{"-" * (len(title) - 1)}+"
            print("\033c", end="")
            print(line)
            print(title)
            display_topbar(header_categories, cat_index, top_line=line)
            display_table(["Item ID", "Item Name", "Price"], item_table, item_index)
        display_content()
        while True:
            key = handle_input()
            if key in ["left", "right", "up", "down", "q"]:
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
                elif key == "q":
                    break
            item_table = [
                [item["id"], item["name"], item["price"]]
                for item in get_items_by_category_code(header_category_codes[cat_index])
            ]
            display_content()
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
                    item_table = [
                        [item["id"], item["name"], item["price"]]
                        for item in get_items_by_category_code(code)
                    ]
                    display_table(["Item ID", "Item Name", "Price"], item_table)
            elif chosen_option == "Order":
                print("your mom as well")
            elif chosen_option == "Back": break



handle_edit_combo("C01")
exit(0)
# Main code function
RESTAURANT_NAME = "Soviet Union Restaurant"

# Just to make restaurant title nicer
title_header = "| " + RESTAURANT_NAME + " |"
bar_header = f"+{'-' * (len(title_header) - 2)}+"
space = "    |"


while True:
    tab_selection = handle_ui_menu_selection(bar_header + "\n" + title_header + "\n" + bar_header + "\n" + space,
        options=["Browse and Order", "View and Edit cart", "Checkout", "Quit"],
        option_icons=["🔍", "🛒", "💳", "🚪"]
    )

    if tab_selection == "Browse and Order": handle_food_menu()
    elif tab_selection == "View and Edit cart": print("Not yet")
    elif tab_selection == "Checkout": print("Not yet")
    else: break