from utils import CONFIG, CSVCollection

category_collection = CSVCollection("test")
try:
    category_collection.add_column("test", float, 32.1)
except TypeError:
    print("error occurred")
print(category_collection.columns)