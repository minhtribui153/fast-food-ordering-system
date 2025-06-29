# Assignment Analysis
This is an overview of students' perspective on how to approach this assignment.

The fast food ordering system requires data inside a menu to be separated into different collections (so-called schemas).

> This data separation is inspired by how SQL databases work.

These collections are separated into each table as follows:
* Category `category`
* Discount Types `discount_types`
* Menu `menu`

Each collection will be stored in a CSV (Comma-Separated Visualizer) document.


| Advantages | Disadvantages |
| - | - |
| Data is __more structured with clear relationships__ and __removes redundancy of adding more keys__, making it __convenient__ for users to make changes to the collection file | __Limited scalability__ (difficult to expand/collapse database collections because of how tedious the process is to add/remove another column of data) |
