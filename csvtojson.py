from tkinter.filedialog import askopenfile
from tkinter import *
import os
import csv
import json
from io import StringIO

# --------------- Input Functions ---------------

def format_file_as_string(filename):
    # Opens a file and returns its contents as a string
    with open(filename, "rt") as csv_file:
        return ''.join(csv_file)

# --------------- Process Functions ---------------

def parse_number(value):
    """
    Takes a string and converts it to its respective type, and returns it.
    "one" -> "one" | "1.2" -> 1.2 | "1" -> 1
    """
      # Check if value is a string
    if value.isdigit():  # Check if the string represents an integer
        return int(value)
    elif value.replace('.', '', 1).isdigit():  # Check if the string represents a float
        return float(value)
    else:
        return value
    
def make_related_list_key(p_list):
    # Takes a list and makes it a dictionary in this format.
    # ie. ["one", "two", "three", "", ""] --> {one: 0, two: 0, three: 3}
    list_dict = {}
    for key in p_list:
        if key != '':
            list_dict[key] = 0
            last_key = key
        elif list_dict[last_key]:
            list_dict[last_key] += 1
        else:
            list_dict[last_key] += 2
    return list_dict

def parse_numbers_compound_list(p_list):
    # Gets a compound list and returns it having parsed all of the numbers
    def convert_sublist(sublist):
        return list(parse_number(item) for item in sublist)
    return list(map(convert_sublist, p_list))

def transpose_compound_list(data, column_names, keep_outside_object=False, keep_inside_array=False, include_keys=False):
    # Take a list's columns and make them into rows.
    # Also specify what datatype to store it in
    
    # Create the new compound object structure
    outside_object = {} if keep_outside_object else []
    not_first_iteration = False
    for key in column_names:
        if not_first_iteration or include_keys:
            if keep_outside_object:
                outside_object[key] = [] if keep_inside_array else {}
            else:
                outside_object.append([] if keep_inside_array else {})
        not_first_iteration = True
    
    # Transfer all values to the object in the specified format
    def process_inside_list(inside_list):
        for i, value in enumerate(inside_list):
            if i != 0 or include_keys:
                if keep_outside_object:
                    if keep_inside_array:
                        outside_object[column_names[i]].append(value)
                    else:
                        outside_object[column_names[i]][inside_list[0]] = value
                else:
                    if keep_inside_array:
                        outside_object[i if include_keys else i-1].append(value)
                    else:
                        outside_object[i if include_keys else i-1][inside_list[0]] = value
    list(map(process_inside_list, data))
        
    return outside_object

def reformat_compound_list(data, columns_names, keep_outside_object=False, keep_inside_array=False, include_keys=False):
    # Reformats a list to the specified format, using the first items as keys if dictionary
    outside_object = {} if keep_outside_object else []
    if not(include_keys):
        columns_names = columns_names[1:]
    def process_inside_list(inside_list):
        row_key = inside_list[0]
        if not(include_keys):
            inside_list = inside_list[1:]
        if keep_inside_array:
            if keep_outside_object:
                outside_object[row_key] = inside_list
            else:
                outside_object.append(inside_list)
        else:
            if keep_outside_object:
                outside_object[row_key] = dict(zip(columns_names, inside_list))
            else:
                outside_object.append(dict(zip(columns_names, inside_list)))
    list(map(process_inside_list, data)) 
    # function has no return, but map() won't run alone in python, so list() is neccessary. Will return ie. [None, None]

    return outside_object

def change_file_extension(filename, new_extension):
    # Removes the old extension (not including the period) and adds a new one
    return filename[0:filename.rfind('.')+1] + new_extension

def group_related_list_values(p_list, p_related_items_dict, exclude_empty_strings=0):
    # Takes a list and an ordered dictionary that describes related values. 
        # If a value is zero, it belongs on it's own.
        # If a value not zero, it's the related values list length.
    # Optional parameter of exclude_empty_strings specifies if "" values are to be excluded from the related lists
    outside_list = []
    for line in p_list:
        inside_list_index = 0
        inside_list = []
        for value in p_related_items_dict.values():
            if value:
                if exclude_empty_strings:
                    related_values_list = []
                    for item in line[inside_list_index:inside_list_index+value]:
                        if item != "":
                            related_values_list.append(item)
                    inside_list.append(related_values_list)
                else:
                    inside_list.append(line[inside_list_index:inside_list_index+value])
                inside_list_index += value
            else:
                inside_list.append(line[inside_list_index])
                inside_list_index += 1
        outside_list.append(inside_list)
    return outside_list

def conditionally_add_quotes(value, include_numbers=True):
    # Adds quotes if it fits the parameter type.
    if isinstance(value, (int, float)):
        return json.dumps(str(value)) if include_numbers else value
    elif isinstance(value, (str, list)):
        return json.dumps(value)
    else:
        raise ValueError("Unsupported parameter type")

# --------------- Output/Gui Functions ---------------

def config_text_frame(parent_frame, parent_text, width=20, height=22):
    parent_frame.config(width=width, height=height, borderwidth="2px", relief="solid")
    parent_text.config(width=width, height=height,  wrap=NONE, highlightthickness=0)
    parent_scrollbar_y = Scrollbar(parent_frame, orient=VERTICAL, command=parent_text.yview)
    parent_scrollbar_x = Scrollbar(parent_frame, orient=HORIZONTAL, command=parent_text.xview)
    parent_text.config(yscrollcommand=parent_scrollbar_y.set, xscrollcommand=parent_scrollbar_x.set)
    parent_scrollbar_x.pack(side=BOTTOM, fill=X)
    parent_scrollbar_y.pack(side=RIGHT, fill=Y)
    parent_text.pack(side=LEFT, fill=BOTH, expand=True) 

def move_file_to_downloads(file):
    # Attempts to move a file and displays whether it was successful or not
    filename = file if isinstance(file, str) else file.name
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    if os.path.exists(downloads_path):
        moved_file = os.path.join(downloads_path, filename)
        os.rename(file, moved_file)
        return True
    else:
        return False

def write_json_from_string(json_string, file="output.json"):
    with open(file, "w") as json_file:
        json_file.write(json_string)

def make_example_table(parent_frame, data=0):
    # Add data to a tkinter table
    # parent_frame is a Frame element. 
    # optional parameter to pass in custom data
    if data == 0:
        data = [
            ["key", "str", "int", "list", ""],
            ["key1", "one", 1, 1.1, 1.2],
            ["key2", "two", 2, 2.3, ""],
            ["key3", "three", 3, 3.4, 3.5]
        ]
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            label = Label(parent_frame, text=value, borderwidth=1, relief="solid", width=7, height=1)
            label.grid(row=i, column=j)

def display_gui():
    gui = Tk()
    
    # GUI settings
    gui.title("CSV to JSON Converter")
    gui.geometry("700x340")
    gui.maxsize(740, 380)
    

    # Input/Output Text Box
    input_frame = Frame(gui)
    input_text = Text(input_frame)
    config_text_frame(input_frame, input_text)
    input_frame.place(x=350, y=25)
    input_text.insert('end', "key,str,int,list,\nkey1,one,1,1.1,1.2\nkey2,two,2,2.3,\nkey3,three,3,3.4,3.5")

    output_frame = Frame(gui)
    output_text = Text(output_frame)
    config_text_frame(output_frame, output_text)
    output_frame.place(x=525, y=25)
    
    # Functions to run when buttons are pressed
    def handle_file():
        ''' Function ran after choose file button is pressed
        1. Users chooses the file
        2. If a file was chosen, runs format_file_as_string to read it
        3. changes a label to display the name of the file
        '''  
        filename = askopenfile(filetypes=[("CSV files", "*.csv")], title="Select a CSV file")
        if filename:
            file_path = filename.name
            short_filename = os.path.basename(file_path)
            file_label.config(text=short_filename)
            input_text.delete('1.0', 'end')
            input_text.insert('end', format_file_as_string(file_path))
        else:
            file_label.config(text="None Chosen")

    def download_output():
        ''' Function ran after save to download button is pressed
        1. Checks if a csv file was chosen
        2. If a file was chosen, names JSON file similarly, otherwise output.json
        3. runs write_json_from_string to write the json file with relative pathing
        4. Runs move_file_to_downloads to move the file if a downloads directory exists
        5. Updates the user on the location of the file
        '''  
        filename = file_label.cget('text')
        if filename == "None Chosen":
            filename = "output.json"
        else:
            filename = change_file_extension(filename, "json")
        write_json_from_string(output_text.get("1.0", "end-1c"), filename)
        if move_file_to_downloads(filename):
            destination_label.config(text=f"{filename} is in downloads")
        else: 
            destination_label.config(text=f"{filename} is in same folder as\ncsv_to_json.py; downloads\ndirectory doesn't exist", justify="right")

    def update_json_format_labels():
        ''' Function ran after any checkbutton or spinbox is pressed
        1. Gets variables from each "button"
        2. Updates the format lable to inform the user the format of json output
        3. Convert the CSV to the JSON format
        4. Place the JSON data in the correct
        5. 
        '''  
        parse_numbers = number_string_option_var.get()
        inside_array = inside_array_option_var.get()
        outside_object = outside_object_option_var.get()
        include_keys = include_keys_var.get()
        transpose_option = transpose_option_var.get()
        spacing = spacing_var.get()

        # Change JSON format label
        if outside_object:
            if inside_array:
                format_label.config(text=f'JSON format: Object with key/array pairs')
            else:
                format_label.config(text=f'JSON format: Object with key/object pairs')
        else:
            if inside_array:
                format_label.config(text=f'JSON format: Array of Arrays')
            else:
                format_label.config(text=f'JSON format: Array of Objects')
        
        # Change output_text
        csv_string = input_text.get("1.0", "end-1c")
        csv_file = StringIO(csv_string)
        reader_object = csv.reader(csv_file)
        first_line = next(reader_object)
        input_data = list(reader_object)
        
        first_line_key = make_related_list_key(first_line)

        if not(parse_numbers):
            input_data = parse_numbers_compound_list(input_data)
        input_data = group_related_list_values(input_data, first_line_key, exclude_empty_strings=1)
        column_names = list(first_line_key.keys())
        if transpose_option:
            json_format = transpose_compound_list(input_data, column_names, outside_object, inside_array, include_keys)
        else:
            json_format = reformat_compound_list(input_data, column_names, outside_object, inside_array, include_keys)
        
        def write_json_as_string():
            out_open_bracket, out_closed_bracket = ('{', '}') if outside_object else ('[', ']')
            in_open_bracket, in_closed_bracket = ('[', ']') if inside_array else ('{', '}')
            
            output_text.delete(1.0, "end")
            def output_insert(text):
                output_text.insert('end', text)
            
            match spacing:
                case 0:
                    output_insert(json.dumps(json_format))
                case 1:
                    output_insert(f"{out_open_bracket}\n")
                    if outside_object:
                        for key, inside_json_object in json_format.items():
                            output_insert(f'  "{key}": {json.dumps(inside_json_object)},\n')
                    else:
                        for inside_json_object in json_format:
                            output_insert(f'  {json.dumps(inside_json_object)},\n')
                    output_text.delete("end-3c", "end") # Delete the final comma
                    output_insert(f"\n{out_closed_bracket}")   
                case 2:
                    def output_insert_inside(inside_json_object):
                        if inside_array:
                            for value in inside_json_object:
                                output_insert(f'    {conditionally_add_quotes(value, parse_numbers)},\n')
                        else:
                            for key, value in inside_json_object.items():
                                output_insert(f'    "{key}": {conditionally_add_quotes(value, parse_numbers)},\n')
                        output_text.delete("end-3c", "end") # Delete the final comma
                        output_insert(f"\n  {in_closed_bracket},\n") 
                    output_insert(f"{out_open_bracket}\n")
                    if outside_object:
                        for key, inside_json_object in json_format.items():
                            output_insert(f'  "{key}": {in_open_bracket}\n')
                            output_insert_inside(inside_json_object)
                    else:
                        for inside_json_object in json_format:
                            output_insert(f'  {in_open_bracket}\n')
                            output_insert_inside(inside_json_object)
                    output_text.delete("end-3c", "end") # Delete the final comma
                    output_insert(f"\n{out_closed_bracket}") 
                case _:
                    output_insert(f"{spacing} is not an option for spacing")
        write_json_as_string()

    # Buttons
    file_button = Button(gui, text="Choose File", command=handle_file)
    file_button.place(x=5, y=5)
    download_button = Button(gui, text="Download JSON", command=download_output)
    download_button.place(x=5, y=35)

    # Button Labels
    file_label = Label(gui, text="None Chosen")
    file_label.place(x=120, y=5)
    destination_label = Label(gui, text="File will Appear in Downloads")
    destination_label.place(x=145, y=35)

    # Button Variables
    number_string_option_var = IntVar()
    outside_object_option_var = IntVar()
    inside_array_option_var = IntVar()
    transpose_option_var = IntVar()
    include_keys_var = IntVar()
    spacing_var = IntVar()

    # JSON formating option checkbuttons
    number_string_option = Checkbutton(gui, text="Parse numbers as strings", variable=number_string_option_var, command=update_json_format_labels)
    number_string_option.place(x=5, y=80)
    outside_object_option = Checkbutton(gui, text="Contain CSV rows in an object (default is array)", variable=outside_object_option_var, command=update_json_format_labels)
    outside_object_option.place(x=5, y=100)
    inside_array_option = Checkbutton(gui, text="Row data format as an array (default is object)", variable=inside_array_option_var, command=update_json_format_labels)
    inside_array_option.place(x=5, y=120)
    include_keys_option = Checkbutton(gui, text="Include first column as items", variable=include_keys_var, command=update_json_format_labels)
    include_keys_option.place(x=5, y=140)
    transpose_option = Checkbutton(gui, text="Transpose", variable=transpose_option_var, command=update_json_format_labels)
    transpose_option.place(x=5, y=160)

    format_label = Label(gui, text="JSON format: Objects contained inside an Array")
    format_label.place(x=5, y=200)

    spacing_frame = Frame(gui, relief="sunken", border="2px")
    spacing_frame.place(x=230, y=160)
    spacing_spinbox = Spinbox(spacing_frame, from_=0, to=2, width=1, textvariable=spacing_var, command=update_json_format_labels, state="readonly")
    spacing_spinbox.grid(row=0, column=0)
    spacing_label = Label(spacing_frame, text="Spacing")
    spacing_label.grid(row=0, column=1)
    
    # Other Labels
    example_table_label = Label(gui, text="Example                  (leave title cells blank for a list)")
    example_table_label.place(x=5, y=230)
    input_label = Label(gui, text="Input")
    input_label.place(x=350, y=5)
    output_label = Label(gui, text="Output")
    output_label.place(x=525, y=5)

    # Example table format of example CSV data
    table_frame = Frame(gui)
    table_frame.pack(padx=10, pady=10)
    table_frame.place(x=5, y=250)
    make_example_table(table_frame)

    gui.mainloop()

def main():
    display_gui()

if __name__ == "__main__":
    main()