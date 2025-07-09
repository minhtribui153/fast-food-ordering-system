# Code Explanation: Fast Food Ordering System

This document explains the structure and logic of the fast food ordering system implemented in your workspace. The system is a Python console-based menu and order selection program for a fast food restaurant.

---

## File Overview

- [`main.py`](main.py): Main entry point and UI logic for menu navigation and order selection.
- [`datasets.py`](datasets.py): Contains menu data, category definitions, and helper functions for menu item retrieval and parsing.
- [`utils.py`](utils.py): Utility functions for console UI, input handling, and formatting.

---

## `main.py` — Main Program Logic

### High-Level Flow

1. **Startup:** Prints the restaurant name and a decorative header.
2. **Main Loop:** Continuously prompts the user with a main menu:
   - Browse and Order
   - View and Edit cart
   - Checkout
   - Quit
3. **Menu Navigation:** Uses interactive or legacy (input-based) UI depending on terminal capabilities.
4. **Order Handling:** Allows users to browse menu categories, select items, and edit combo meals.

---

### Key Functions

#### `handle_ui_menu_selection(question, options, option_icons=[], back_button=False)`

- **Purpose:** Presents a menu selection UI (interactive or input-based).
- **Parameters:**
  - `question`: Prompt/question to display.
  - `options`: List of option strings.
  - `option_icons`: Optional icons for each option.
  - `back_button`: If `True`, adds a "Back" option.
- **Behavior:**
  - Interactive mode: Uses arrow keys and enter to select.
  - Legacy mode: Uses numbered input or 'B' for back.
- **Returns:** The selected option as a string.

#### `handle_edit_combo(item_id, preselected={})`

- **Purpose:** Allows editing of a combo meal by selecting items for each section.
- **Parameters:**
  - `item_id`: Combo meal item ID.
  - `preselected`: (Optional) Dict mapping section names to selected option codes.
- **Behavior:**
  - Validates that the item is a combo.
  - Parses combo sections and options.
  - Interactive mode: Tabbed UI for each section, allows selection/deselection.
  - Legacy mode: Input-based selection for each section.
- **Returns:** Dict mapping section names to selected item IDs, or `None` if cancelled.

#### `handle_food_menu()`

- **Purpose:** Lets the user browse menu categories and select items to order.
- **Behavior:**
  - Interactive mode: Arrow-key navigation between categories and items.
  - Legacy mode: Presents options to browse or order by item ID.
- **Returns:** The selected item ID, or `None` if cancelled.

---

### Main Code Block

After defining the above functions, the main code:

1. Prints the restaurant header.
2. Enters a loop, repeatedly calling `handle_ui_menu_selection` to ask the user what they want to do.
3. Depending on the selection:
   - "Browse and Order": Calls `handle_food_menu()`.
   - "View and Edit cart" / "Checkout": Prints "Not yet" (placeholders).
   - "Quit": Exits the loop and ends the program.

---

## `datasets.py` — Menu Data and Helpers

### Key Data Structures

- **`MENU_ITEM_IDS`**: Maps category codes to (singular name, plural name, icon).
- **`MENU`**: List of menu items (burgers, sides, drinks, desserts, combos), each as a dict with `id`, `name`, `price`, and for combos, `item_ref_ids`.
- **`DISCOUNT_RATES`**: Discount rates for different customer types.

### Helper Functions

- **`generate_item_table(items)`**: Converts a list of item dicts to a 2D list for table display.
- **`get_items_by_category_code(code)`**: Returns all menu items in a given category.
- **`get_item_by_id(item_id)`**: Returns the menu item dict for a given ID.
- **`get_items_by_ids(item_ids)`**: Returns menu items for a list of IDs or category codes.
- **`parse_item_ref_ids(item_ref_ids)`**: Parses the combo meal's `item_ref_ids` into a list of section dicts, each with:
  - `section`: Section name
  - `options`: List of item dicts
  - `quantity`: Number of selections allowed
  - `locked`: If `True`, section cannot be edited

---

## `utils.py` — Console and Input Utilities

### Key Functions

- **`clear_console()`**: Clears the console screen.
- **`split_item_code(item_code)`**: Splits an item code into category code and item number.
- **`display_modal(title, content, icon="ℹ️", max_characters_before_newline=50)`**: Shows a modal dialog with formatted content and waits for Enter.
- **`display_topbar(options, selected_option=0, top_line="")`**: Displays a top bar with selectable options.
- **`display_table(data, headers=[], selected_index=-1, tab_space=4)`**: Prints a formatted table, highlighting the selected row if needed.
- **`handle_input()`**: Cross-platform function to detect key inputs (arrows, enter, space, alphanum).

---

## Example Flow

1. **User starts the program.**
2. **Main menu appears:** User chooses "Browse and Order".
3. **Menu navigation:** User browses categories (e.g., Burgers, Sides) and selects an item.
4. **If a combo is selected:** `handle_edit_combo` is called, letting the user customize the combo.
5. **Selections are returned:** (Further cart/checkout logic can be implemented.)

---

## Extensibility

- The code is modular, with clear separation between data, UI, and logic.
- Adding new menu items or categories is as simple as updating [`MENU`](datasets.py) and [`MENU_ITEM_IDS`](datasets.py).
- UI functions are reusable for other menu-driven features (e.g., cart, checkout).

---

## Summary

This system provides a robust, interactive console-based menu ordering experience for a fast food restaurant, with support for combo customization and clear, user-friendly