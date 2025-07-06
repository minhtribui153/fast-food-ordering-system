import sys

def split_item_code(item_code):
    """Splits an item code into its category code and category item number."""
    cat_code = ''
    item_num = ''
    for char in item_code:
        if char.isalpha(): cat_code += char
        else: item_num += char
    return cat_code, item_num

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

def display_table(headers: list[str], data: list[list[str]], selected_index: int = -1, tab_space: int = 4):
    """Prints a formatted table (compatible with interactive menu selection)"""
    # Calculate max width for each column
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*([headers] + data))]
    # Helper function to format a row
    def fmt_row(row): return "|" + "|".join(f" {str(cell):<{w}} " for cell, w in zip(row, col_widths)) + "|"
    # Helper function to format a line
    def fmt_line(): return "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    padding = " " * tab_space if selected_index > -1 else ""
    print(padding, fmt_line())
    print(padding, fmt_row(headers))
    print(padding, fmt_line())
    for i, row in enumerate(data):
        # Highlight selected row if needed
        if selected_index > -1 and i == selected_index: print(f"{'> ':>{tab_space}}", fmt_row(row), "<")
        else: print(padding, fmt_row(row))
    print(padding, fmt_line())


def handle_input():
    """Detect key inputs (arrows, enter, space, alphanum) cross-platform."""
    if sys.platform.startswith('win'):
        msvcrt = __import__("msvcrt")
        while True:
            ch = msvcrt.getch()
            if ch == b'\xe0':
                ch2 = msvcrt.getch()
                return {'H': 'up', 'P': 'down', 'K': 'left', 'M': 'right'}.get(ch2.decode(), None)
            if ch == b'\r': return 'enter'
            if ch == b' ': return 'spacebar'
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
                if ch.isalnum(): return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)