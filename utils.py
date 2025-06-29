from datetime import datetime
from pprint import pprint

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
    def __init__(self, collection_name: str) -> None:
        """Loads a CSV file and converts it into a collection"""
        self.collection_name = collection_name
        self.file_path = os.path.join(os.getcwd(), CONFIG["database"]["dir"], collection_name) + ".csv"
        self.data = []
        self.__data_csv = []
        
        column_names = []
        column_types = []

        with open(self.file_path, "r") as file:
            csv_data = file.readlines()
            for i in range(len(csv_data)):
                if i == 0:
                    # Handle column names
                    column_names = [self.__to_key(column_name) for column_name in csv_data[i].split(",")]
                else:
                    row_data = {}
                    csv_row_data = [row_column.strip() for row_column in csv_data[i].split(",")]
                    self.__data_csv.append(csv_row_data)
                    # Handle each data
                    for j in range(len(csv_row_data)):
                        if len(column_types) == j: column_types.append([])
                        converted_data = self.__handle_data_conversion(csv_row_data[j])
                        row_data[column_names[j]] = converted_data
                        if type(converted_data) not in column_types[j]: column_types[j].append(type(converted_data))
                    self.data.append(row_data)
        
        self.columns = []
        for k in range(len(column_names)):
            self.columns.append({
                "name": column_names[k],
                "types": column_types[k]
            })
    
    def __to_key(self, text):
        """Converts text into a JSON-standard key name"""
        text_spaces_only = re.sub(r'\([^)]*\)', '', text).lower()
        column = re.sub(r'\s+', ' ', text_spaces_only).strip()
        key = column.replace(" ", "_")
        return key

    def __handle_data_conversion(self, data: str):
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
                return self.data[item]
            except KeyError:
                raise IndexError(f"No such row with index {item}")
           
        elif type(item) == str:
            try:
                return [row_data[item] for row_data in self.data]
            except KeyError:
                raise KeyError(f"No such column name called '{item}'")
        elif type(item) == tuple:
            column_name, row_index = item
            if len(item) == 2 and type(column_name) == str and type(row_index) == int:
                try:
                    return self.data[row_index][column_name]
                except KeyError:
                    raise KeyError(f"Element does not exist")
        
        raise ReferenceError("Invalid key arguments to find data in this collection")
            
    
    def __repr__(self) -> str:
        headers = [column["name"] for column in self.columns]
        all_rows = [headers] + self.__data_csv
        col_widths = [max(len(str(row[i])) for row in all_rows) for i in range(len(headers))]

        def format_row(row, sep="|"):
            return sep + sep.join(f" {str(cell):<{col_widths[i]}} " for i, cell in enumerate(row)) + sep

        def format_line(left, mid, right, fill):
            return left + mid.join(fill * (w + 2) for w in col_widths) + right

        res = ""
        res += format_line("+", "+", "+", "-") + "\n"
        res += format_row(headers) + "\n"
        res += format_line("+", "+", "+", "-") + "\n"
        for row in self.__data_csv:
            res += format_row(row) + "\n"
        res += format_line("+", "+", "+", "-") + "\n"
        return res
    
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