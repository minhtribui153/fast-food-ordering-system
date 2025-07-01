from utils import CONFIG, CSVCollection, Table
import re

category_collection = CSVCollection("category")
discount_types_collection = CSVCollection("discount_types")
menu_collection = CSVCollection("menu")

def handle_main_menu():
    print("(1) View food menu")
    print("(2) View & Edit cart")
    print("(3) Check out")
    print("(4) Quit")

    while True:
        main_menu_choice = input("Select an option: ")
        if main_menu_choice.isdigit() and int(main_menu_choice) in range(1, 5): break
        print("Invalid option!")
    
    return int(main_menu_choice)

def handle_food_menu():
    pass
print("=" * len(CONFIG["restaurant_name"]))
print(CONFIG["restaurant_name"])
print("=" * len(CONFIG["restaurant_name"]))
running = True
try:
    while running:
        try:
            main_menu_choice = handle_main_menu()
            
            if main_menu_choice == 1: handle_food_menu()
            elif main_menu_choice == 4: raise KeyboardInterrupt()
        except KeyboardInterrupt:
            print()
            confirm_quit = ""
            while confirm_quit not in ["Y", "N"]:
                confirm_quit = input("Are you sure you want to quit? (Y/N): ").upper()
            running = confirm_quit == "N"
except KeyboardInterrupt:
    print()
    exit(0)

print(menu_collection.fetch_rows(lambda row: re.split(r'(\d+)', row["item_code"])[0] == "C"))