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
import time

if not sys.stdin.isatty():
    print("=== NOT SUPPORTED")
    print("This program cannot be run on pseudo-based terminals.")
    print("Please run the legacy.py python program instead.")
    exit(1)

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

def clear_console():
    """Clears the console screen"""
    # 033 = Code for terminal controls
    # C = Clears the console buffer output
    print("\033c", end="")

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

def colourize_text(text: str, color="white"):
    """Colourizes text for console terminals"""
    colors = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
    # \033 counts as 1 character
    # returns: (string with colourized text with length, character offset for UI design)
    return f"\033[0;3{colors.index(color)}m{text}\033[0m", 11

def display_modal(title: str, content: str, report_type: str = "info", max_characters_before_newline: int = 50):
    if report_type == "info": icon, color, offset = "ℹ️", "blue", 3
    elif report_type == "warning": icon, color, offset = "⚠️", "yellow", 2
    elif report_type == "success": icon, color, offset = "✅", "green", 1
    elif report_type == "error": icon, color, offset = "❌", "red", 1
    else: raise ValueError("report_type must be info, warning, error, or success!")
    colourized_title, char_offset = colourize_text(title, color)
    header = f"| {icon}  {colourized_title} |"
    bar_line = f"+{'-' * (len(header) - offset - char_offset)}+"

    # Split content into lines first (to preserve explicit newlines)
    lines = content.split('\n')
    formatted_lines = []
    old_stdout = sys.stdout
    for line in lines:
        words = line.split(" ")
        curr_line = ""
        for i, word in enumerate(words):
            if curr_line == "":
                curr_line = word
            elif len(curr_line) + 1 + len(word) > max_characters_before_newline:
                formatted_lines.append(curr_line)
                curr_line = word
            else:
                curr_line += " " + word
        if curr_line != "":
            formatted_lines.append(curr_line)

    clear_console()
    print(bar_line)
    print(header)
    print(bar_line)
    for fl in formatted_lines:
        print("| " + fl)
    print("|\n| [Enter] OK")
    while True:
        if handle_input() == "enter":
            break
    clear_console()
    sys.stdout = old_stdout

def display_topbar(options=None, selected_option: int = 0, top_line: str = ""): 
    """Shows a top bar with options given to the user"""
    if options is None: options = []
    converted_options = []
    for i in range(len(options)):
        converted_options.append(f"[{options[i]}]" if i == selected_option else f" {options[i]} ")

    middle_content = "| " + " ".join(converted_options) + " |"
    bar_line = f"+{(len(middle_content) - 2) * "-"}+"
    print(top_line if len(top_line) > len(bar_line) else bar_line)
    print(middle_content)
    print(bar_line)

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
    for i, row in enumerate(data):
        # Highlight selected row if needed
        if selected_index > -1 and i == selected_index: print(f"{'> ':>{tab_space}}", fmt_row(row), "<")
        else: print(padding, fmt_row(row))
    print(padding, fmt_line())


def handle_input():
    """Detect key inputs (arrows, enter, space, backspace, alphanum, plus, minus) cross-platform."""
    if sys.platform.startswith('win'):
        msvcrt = __import__("msvcrt")
        while True:
            ch = msvcrt.getch()
            if ch == b'\xe0':
                ch2 = msvcrt.getch()
                return {'H': 'up', 'P': 'down', 'K': 'left', 'M': 'right'}.get(ch2.decode(), None)
            if ch == b'\r': return 'enter'
            if ch == b' ': return 'spacebar'
            if ch in (b'\x08', b'\x7f'): return 'backspace'  # Backspace (Windows)
            if ch == b'-': return 'minus'
            if ch == b'+': return 'plus'
            ch = ch.decode()
            if ch.isalnum() or ch == " ": return ch
    else:
        tty = __import__("tty")
        termios = __import__("termios")
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch == '\x1b' and sys.stdin.read(1) == '[':
                    return {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(sys.stdin.read(1), None)
                if ch in ('\r', '\n'): return 'enter'
                if ch == " ": return 'spacebar'
                if ch in ('\x08', '\x7f'): return 'backspace'  # Backspace (Unix)
                if ch == '-': return 'minus'
                if ch == '+': return 'plus'
                if ch.isalnum(): return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

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
    header_fields = f"{'No.':<3} {'ID':<{col_id}} {'Name':<{col_name}} {'Description':<{col_desc}} {'Type':>{col_type}} {'Price':>{col_price}} {'Qty':>{col_qty}}"
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
    back_icon = "⬅️  "
    confirm_icon = "✅  "
    next_icon = "➡️  "
    if not options:
        raise RuntimeError("Options cannot be empty")
    if option_icons and len(option_icons) != len(options):
        raise RuntimeError("Length of option_icons must match options")
    ui_options = (
        options[:]
        + (["Confirm"] if confirm_button else [])
        + (["Next"] if next_button else [])
        + (["Back"] if back_button else [])
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
    if len(cart) == 0:
        display_modal("No items in Cart", (
            "There are currently no items in your cart. "
            "Please order an item through the Browse and Order section in order to view this section"
        ), max_characters_before_newline=60)
        return None
    
    table_headers = ["Index", "Code", "Category", "Name", "Price", "Quantity", "Total"]
    current_index = 0
    def show():
        """Display to console terminal and return num of items allowed to choose"""
        clear_console()
        display_table([
            [
                str(i + 1), cart[i]["id"],
                MENU_ITEM_IDS[split_item_code(cart[i]["id"])[0]][1], cart[i]["name"],
                f"${cart[i]["price"]:.2f}",
                (f"- {cart[i]["quantity"]:^{len(table_headers[5])}} +" if current_index == i else f"  {cart[i]["quantity"]:^{len(table_headers[5])}}  "),
                f"${cart[i]["price"] * cart[i]["quantity"]:.2f}"
            ]
            for i in range(len(cart))
        ], table_headers, selected_index=current_index)
        print("---")
        print(f"Total: ${sum(item["price"] * item["quantity"] for item in cart):.2f}")
        print("---")
        print("[Up/Down arrows] Move selection cursor")
        print("[Left/Right arrows] Update quantity")
        print("[Enter] Edit selection")
        print("[Backspace] Delete selection")
        print("[Q] Back")
    while True:
        show()
        key = handle_input()
        if key == "left":
            cart[current_index]["quantity"] = max(cart[current_index]["quantity"] - 1, 1)
        elif key == "right":
            cart[current_index]["quantity"] = min(cart[current_index]["quantity"] + 1, ALLOWED_ORDERS_PER_ITEM)
        elif key == "up":
            current_index = max(current_index - 1, 0)
        elif key == "down":
            current_index = min(current_index + 1, len(cart) - 1)
        elif key == "enter":
            current = cart[current_index]
            # Edit a combo meal
            category_code, _ = split_item_code(current["id"])
            if category_code == "C":
                # Enable combo editing
                combo_selected_data = handle_edit_combo(current["id"], current["options"])
                if combo_selected_data is None:
                    continue
                cart[current_index]["options"] = combo_selected_data
                display_modal(
                    "Saved changes to Cart",
                    f"Successfully saved new item data to cart:\n - ({order["id"]}) {order["name"]}",
                    "success",
                )
            else:
                display_modal("Cannot edit item", f"({current["id"]}) {current["name"]} is an à la carte item. You can only edit combo items.", "error")
        elif key == "backspace":
            cart.pop(current_index)
            current_index = 0
            if len(cart) == 0:
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

def handle_checkout():
    """Handles the checkout menu system, exits after printing receipt"""
    if len(cart) == 0:
        display_modal("No items to pay", "Please order an item before proceeding to checkout.", "info", 60)
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
                        display_modal(
                            "Order overflow",
                            f"You have reached to {total_quantity} orders for this item. Maximum orders allowed for each item is {ALLOWED_ORDERS_PER_ITEM}.",
                            "error"
                        )
                    else:
                        cart[i]["quantity"] += order["quantity"]
                        found_similar_item = True
            
            if overflow: continue
            if not found_similar_item: cart.append(order)
            # Display added to cart message
            display_modal(
                "Added to Cart",
                f"Successfully added this item to cart:\n - ({order["id"]}) {order["name"]}\n - Quantity: {quantity}",
                "success",
            )
            completed = True
        if not completed: continue
    elif tab_selection == 1: handle_edit_cart()
    elif tab_selection == 2: handle_checkout()
    else:
        print("👋 Goodbye!")
        time.sleep(1)
        break