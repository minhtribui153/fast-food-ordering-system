# Datasets
MENU = {
    "Burgers": {
        "B01": ("Classic Beef Burger", 5.50),
        "B02": ("Chicken Burger", 5.00),
        "B03": ("Veggie Burger", 4.80),
        "B04": ("Spicy Chicken Burger", 5.30),
    },
    "Sides": {
        "S01": ("French Fries", 2.50),
        "S02": ("Onion Rings", 2.80),
        "S03": ("Chicken Nuggets (6pc)", 3.50),
        "S04": ("Cheese Sticks (4pc)", 3.20),
    },
    "Drinks": {
        "D01": ("Coke", 1.80),
        "D02": ("Sprite", 1.80),
        "D03": ("Ice lemon Tea", 2.20),
        "D04": ("Mineral water", 1.50),
    },
    "Desserts": {
        "DS01": ("Chocolate sundae", 2.80),
        "DS02": ("Vanilla cone", 1.50),
        "DS03": ("Apple pie", 2.30),
        "DS04": ("Strawberry sundae", 2.80),
    },
    "Combos": {
        "C01": ("Burger + Fries + Drink", 8.80),
        "C02": ("Nuggets + Fries + Drink", 8.50),
        "C03": ("Veggie Combo", 8.20),
        "C04": ("Kids Meal", 6.50),
    }
}

DISCOUNT_RATES = {
    "student": 0.10,
    "staff": 0.08,
    "loyalty member": 0.05
}

sys = __import__("sys")

# Utility functions
def display_topbar(options: list[str] = [], selected_option: int = 0):
    """Shows a top bar with options given to the user"""
    converted_options = []

    for i in range(len(options)):
        if i == selected_option:
            converted_options.append(f"[{options[i]}]")
        else:
            converted_options.append(f" {options[i]} ")

    middle_content = "| " + " ".join(converted_options) + " |"
    bar_line = f"+{(len(middle_content) - 2) * "-"}+"
    print(bar_line)
    print(middle_content)
    print(bar_line)

def display_table(headers: list[str], data: list[list[str]]):
    """Displays a neat table for a 2D list"""
    col_widths = [max(len(str(row)) for row in col) for col in data]

    def format_row(row, sep="|"):
        return sep + sep.join(f" {str(cell):<{col_widths[i]}} " for i, cell in enumerate(row)) + sep

    def format_line(left, mid, right, fill):
        return left + mid.join(fill * (w + 2) for w in col_widths) + right

    res = ""
    res += format_line("+", "+", "+", "-") + "\n"
    res += format_row(headers)
    res += format_line("+", "+", "+", "=") + "\n"
    for row in data:
        res += format_row(row) + "\n"
    res += format_line("+", "+", "+", "-") + "\n"
    return res


def handle_input():
    """
    Detect key inputs using arrow prefixes
    All console terminals use this
    """
    global sys
    if sys.platform.startswith('win'):
        msvcrt = __import__("msvcrt")
        while True:
            # Get character to determine which key is pressed
            ch = msvcrt.getch() # type: ignore
            if ch == b'\xe0':  # Arrow prefix
                ch2 = msvcrt.getch() # type: ignore
                if ch2 == b'H': return 'up'
                elif ch2 == b'P': return 'down'
                elif ch2 == b'K': return 'left'
                elif ch2 == b'M': return 'right'
            elif ch == b'\r': return 'enter'
            elif ch == b' ': return 'spacebar'
            else:
                # Alphabets and letters
                ch = ch.decode()
                if ch.isalnum() or ch == " ": return ch
    else:
        tty = __import__("tty")
        termios = __import__("termios")
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        while True:
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    next1 = sys.stdin.read(1)
                    next2 = sys.stdin.read(1)
                    if next1 == '[':
                        if next2 == 'A': return 'up'
                        elif next2 == 'B': return 'down'
                        elif next2 == 'C': return 'right'
                        elif next2 == 'D': return 'left'
                elif ch == '\r' or ch == '\n': return 'enter'
                elif ch == " ": return 'spacebar'
                elif ch.isalnum(): return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def handle_ui_menu_selection(question: str, options: list, back_button: bool = False):
    """Handles menu selection UI"""
    if len(options) == 0:
        raise RuntimeError("Options cannot be empty")
    if sys.stdin.isatty():
        # Production UI
        ui_menu_options = []
        ui_menu_options.extend(options) # Copy from options array
        if back_button: ui_menu_options.append("Back")

        selected_index = 0
        while True:
            # Clear the terminal screen
            print("\033c", end="")
            print(question)
            for i in range(len(ui_menu_options)):
                if i == selected_index: print(f" >> | {options[i]}")
                else: print(f"    | {options[i]}")
            # Handle up/down inputs
            key = handle_input()
            if key == "up" and selected_index > 0: selected_index -= 1
            if key == "down" and selected_index < len(ui_menu_options) - 1: selected_index += 1
            if key == "enter": break
        return ui_menu_options[selected_index]
    else:
        # Legacy UI
        
        selection = ""
        while True:
            print(question)
            # Display all options
            for i in range(len(options)): print(f"({i + 1}) {options[i]}")
            if back_button: print("(B) Back")
            selection = input(">> ")

            if selection.isdigit() and int(selection) not in range(1, len(options) + 1):
                print("Error: Invalid option!")
                continue
            if back_button and selection != "B":
                print("Error: Invalid option!")
                continue
            break
        if selection == "B": return "Back"
        else: return options[int(selection) - 1]

def handle_menu():
    pass

# Main code function

# index = 0
# if sys.stdin.isatty():
#     print("\033c", end="")
#     display_topbar(list(MENU.keys()), index)

#     while True:
#         key = handle_input()
#         if key in ["left", "right", "quit"]:
#             if key == "left":
#                 index = max(index - 1, 0)
#             elif key == "right":
#                 index = min(index + 1, len(MENU.keys()) - 1)
#             elif key == "quit":
#                 break
#             print("\033c", end="")
#             display_topbar(list(MENU.keys()), index)
# else:
#     for i in range(len(MENU.keys())):
#         print(f"({i + 1}) {list(MENU.keys())[i]}")
#     print(f"(B) Back")
# print("Type anything. Press Enter to stop.")
# buffer = ""
# while True:
#     key = handle_input()
#     print(f"You pressed: {key}")
#     if key == "enter":
#         break

handle_ui_menu_selection("What would you like to do?",
    options=["Browse and Order", "View and Edit cart", "Checkout", "Quit"]
)