from utils import CONFIG, CSVCollection, Table
import re

category_collection = CSVCollection("menu")


print(category_collection.fetch_rows(lambda row: re.split(r'(\d+)', row["item_code"])[0] == "C"))
category_collection.wait_for_update()