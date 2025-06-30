from datetime import datetime

import re
import time
import os
import json

def load_config():
    """Loads the project configuration"""
    with open("config.json", "r") as file:
        return json.loads(file.read())
    
CONFIG = load_config()

class CSVCollection:
    """An SQL-inspired collection that uses data from CSV files"""
    def __init__(self, collection_name: str) -> None:
        """Loads a CSV file and converts it into a collection. If the file does not exist, creates an empty collection."""
        self.collection_name = collection_name
        self.file_path = os.path.join(os.getcwd(), CONFIG["database"]["dir"], collection_name) + ".csv"
        self.__data: list[list] = []
        self.columns = []

        if not os.path.exists(self.file_path): return

        column_names = []
        column_names_original = []
        column_types = []

        with open(self.file_path, "r") as file:
            csv_data = file.readlines()
            for i in range(len(csv_data)):
                if i == 0:
                    # Handle column names
                    column_names = [self.__to_key(column_name) for column_name in csv_data[i].split(",")]
                    column_names_original = [column_name.strip() for column_name in csv_data[i].split(",")]
                else:
                    csv_row_data = [row_column.strip() for row_column in csv_data[i].split(",")]
                    converted_csv_row_data = []
                    # Handle each data
                    for j in range(len(csv_row_data)):
                        if len(column_types) == j: column_types.append(None)
                        converted_data = self.__handle_data_conversion(column_types[j], csv_row_data[j])
                        converted_csv_row_data.append(converted_data)
                        column_types[j] = type(converted_data)
                        
                    self.__data.append(converted_csv_row_data)
        
        for k in range(len(column_names)):
            self.columns.append({
                "name": column_names[k],
                "original_name": column_names_original[k],
                "type": column_types[k]
            })
    
    def __contains__(self, item):
        return len([True for row in self.__data for col in row if col == item]) > 0
    
    def __to_key(self, text):
        """Converts text into a JSON-standard key name"""
        text_spaces_only = re.sub(r'\([^)]*\)', '', text).lower()
        column = re.sub(r'\s+', ' ', text_spaces_only).strip()
        key = column.replace(" ", "_")
        return key

    def __handle_data_conversion(self, previous_type, data: str):
        if previous_type == str: return data
        try: return datetime.fromisoformat(data)
        except ValueError:
            try: return int(data)
            except ValueError:
                try: return float(data)
                except ValueError:
                    return data
    
    def __getitem__(self, item):
        if type(item) == int:
            try:
                return self.__data[item]
            except KeyError:
                raise IndexError(f"No such row with index {item}")
        elif type(item) == str:
            try:
                column_index = [i for i in range(len(self.columns)) if self.columns[i]["name"] == item][0]
                return [row_data[column_index] for row_data in self.__data]
            except KeyError:
                raise KeyError(f"No such column name called '{item}'")
        elif type(item) == tuple:
            column_name, row_index = item
            if len(item) == 2 and type(column_name) == str and type(row_index) == int:
                try:
                    column_index = [i for i in range(len(self.columns)) if self.columns[i]["name"] == column_name][0]
                    return self.__data[row_index][column_index]
                except IndexError:
                    raise KeyError(f"Element does not exist")
        
        raise ReferenceError("Invalid key arguments to find data in this collection")
            
    
    def __repr__(self) -> str:
        if not self.columns or not self.__data:
            return "(empty)"
        headers = [column["name"] for column in self.columns]
        all_rows = [headers] + self.__data
        col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]

        def format_row(row, sep="|"):
            return sep + sep.join(f" {'(null)' if cell == None else str(cell):<{col_widths[i]}} " for i, cell in enumerate(row)) + sep

        def format_line(left, mid, right, fill):
            return left + mid.join(fill * (w + 2) for w in col_widths) + right

        res = ""
        res += format_line("+", "+", "+", "-") + "\n"
        res += format_row(headers) + "\n"
        res += format_line("+", "+", "+", "-") + "\n"
        for row in self.__data:
            res += format_row(row) + "\n"
        if len(self.__data) > 0: 
            res += format_line("+", "+", "+", "-") + "\n"
        return res
    
    def get_row_by_value(self, column_name: str, value):
        for i in range(len(self[column_name])):
            if value == self[column_name][i]:
                return self[i]
        return None
    
    def add_row(self, values: list, insert_at: int = -1):
        """
        Adds a new row to the collection
        """
        
        if len(self.columns) == 0:
            raise RuntimeError("No columns defined, please create.")
        # Validate values from columns
        if len(values) != len(self.columns):
            raise ValueError(f"Expected {len(self.columns)} values, got {len(values)}")

        converted_values = []
        for i, value in enumerate(values):
            expected_type = self.columns[i]["type"]
            # Try to convert value to expected type if not already
            if not isinstance(value, expected_type):
                try:
                    if value == None:
                        if expected_type == str: value = ""
                        elif expected_type == int: value = 0
                        elif expected_type == float: value = 0.0
                        else: value = None
                    elif expected_type == datetime and not isinstance(value, datetime):
                        value = datetime.fromisoformat(value)
                    else:
                        value = expected_type(value)
                except Exception:
                    raise TypeError(f"'{value}' at column '{self.columns[i]['name']}' cannot be converted to '{expected_type.__name__}'")
            converted_values.append(value)

        # Determine the insertion index
        if insert_at < 0 or insert_at > len(self.__data):
            insert_at = len(self.__data)
        self.__data.insert(insert_at, converted_values)
    
    def add_column(self, column_name: str, value_type, expected_value = None, insert_at: int = -1):
        """
        Adds a new column to the collection
        """
        if value_type not in [str, int, float, datetime]:
            raise ValueError("value_type must be str, int, float, or datetime.")
        key = self.__to_key(column_name)
        # Check if column already exists
        if any(col["name"] == key for col in self.columns):
            raise ValueError(f"Column '{column_name}' already exists.")

        # Determine the insertion index
        if insert_at < 0 or insert_at > len(self.columns):
            insert_at = len(self.columns)

        # Add default value to all existing rows at the correct position

        for row in self.__data:
            try:
                if expected_value == None:
                    if value_type == str: value = ""
                    elif value_type == int: value = 0
                    elif value_type == float: value = 0.0
                    else: value = None
                elif value_type == datetime and not isinstance(expected_value, datetime):
                    value = datetime.fromisoformat(expected_value)
                elif not isinstance(expected_value, value_type):
                    value = value_type(expected_value)
                else:
                    value = expected_value
            except Exception:
                raise TypeError(f"Default value '{expected_value}' cannot be converted to '{value_type.__name__}'")
            row.insert(insert_at, value)

        # Add new column metadata at the correct position
        self.columns.insert(insert_at, {
            "name": key,
            "original_name": column_name,
            "type": value_type
        })
    
    def remove_row(self, index: int):
        """
        Removes a row from the collection by index
        """
        if index < 0 or index >= len(self.__data):
            raise IndexError(f"Row index {index} out of range")
        del self.__data[index]

    def remove_column(self, column_name: str):
        """
        Removes a column from the collection by column name
        """
        key = self.__to_key(column_name)
        col_indices = [i for i, col in enumerate(self.columns) if col["name"] == key]
        if not col_indices:
            raise KeyError(f"No such column '{column_name}'")
        col_index = col_indices[0]
        del self.columns[col_index]
        for row in self.__data:
            del row[col_index]

    def save(self):
        """
        Saves this collection to the CSV file
        """
        with open(self.file_path, "w") as file:
            # Write header
            headers = [col["original_name"] for col in self.columns]
            file.write(",".join(headers) + "\n")
            # Write data rows
            for row in self.__data:
                row_str = []
                for i, value in enumerate(row):
                    if isinstance(value, datetime):
                        row_str.append(value.isoformat())
                    else:
                        row_str.append(str(value))
                file.write(",".join(row_str) + "\n")
    
    def wait_for_update(self, interval: int = 0):
        last_modified_time = os.path.getmtime(self.file_path)
        while True:
            if interval > 0: time.sleep(interval)
            current_modified_time = os.path.getmtime(self.file_path)
            if current_modified_time != last_modified_time:
                return
        

class Table:
    def __init__(self, data: list[list[str]]) -> None:
        self.data = data
        self.col_widths = [max(len(str(row)) for row in col) for col in data]
        pass

    def format_row(self, row, sep="|"):
            return sep + sep.join(f" {str(cell):<{self.col_widths[i]}} " for i, cell in enumerate(row)) + sep

    def format_line(self, left, mid, right, fill):
        return left + mid.join(fill * (w + 2) for w in self.col_widths) + right
    
    def __repr__(self) -> str:
        res = ""
        res += self.format_line("+", "+", "+", "-") + "\n"
        for row in self.data:
            res += self.format_row(row) + "\n"
            res += self.format_line("+", "+", "+", "-") + "\n"
        return res