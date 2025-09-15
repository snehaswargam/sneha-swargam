import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
import xml.etree.ElementTree as et

root = tk.Tk()
root.title("ARXML Viewer")
root.geometry("700x500")
ns = {"a": "http://autosar.org/schema/r4.0"}
# Row 0 → controls
entry = tk.Entry(root, text="File Name",width=50)
entry.grid(row=0, column=0, padx=10, pady=10)

tk.Button(root, text="Browse", command=lambda: browse_file()).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Submit", command=lambda: read_file()).grid(row=0, column=2, padx=10, pady=10)

# Row 1 → Treeview fills remaining space
treeview = ttk.Treeview(root, columns=("Value","newValue"), show="tree headings")
treeview.heading("#0", text="Tag")
treeview.heading("Value", text="Value")
treeview.heading("newValue", text="newValue")
treeview.grid(row=1, column=0, columnspan=3, sticky="nsew")

# make row 1 expand with window resize
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

op = None
tree = None
root1 = None

def browse_file():
    global op
    op = filedialog.askopenfilename(
        title="Select ARXML file",
        filetypes=[("ARXML files", "*.arxml"), ("All files", "*.*")]
    )
    if op:
        entry.delete(0, tk.END)
        entry.insert(0, op)

def read_file():
    global root1, tree
    if not op:
        return
    tree = et.parse(op)
    root1 = tree.getroot()
    parse_xml()
item_to_xml = {}
def parse_xml():
    for item in treeview.get_children():
        treeview.delete(item)

    for container in root1.findall(".//a:Test-CONTAINER-VALUE", ns):
        short_name = container.find("a:SHORT-NAME", ns)
        def_ref = container.find("a:DEFINITION-REF", ns)

        container_label = f"{short_name.text if short_name is not None else ''}"



        parent_id = treeview.insert("", "end", text=container_label, values=(""))

        # Add parameter values
        for param in container.findall(".//a:Test-NUMERICAL-PARAM-VALUE", ns):
            p_def = param.find("a:DEFINITION-REF", ns)
            p_val = param.find("a:VALUE", ns)
            param_label = p_def.text.split("/")[-1] if p_def is not None else "UnknownDef"
            param_value = p_val.text if p_val is not None else ""
            # store reference to the XML element so we can update it later
            treeview.insert(parent_id, "end", text=param_label, values=(param_value,), tags=("editable",))
            treeview.set(parent_id, "Value", "")  # parent container has no direct value
        for param in container.findall(".//a:Test-TEXTUAL-PARAM-VALUE", ns):
            p_def = param.find("a:DEFINITION-REF", ns)
            p_val = param.find("a:VALUE", ns)
            param_label = p_def.text.split("/")[-1] if p_def is not None else "UnknownDef"
            param_value = p_val.text if p_val is not None else ""
            # store reference to the XML element so we can update it later
            treeview.insert(parent_id, "end", text=param_label, values=(param_value,), tags=("editable",))
            treeview.set(parent_id, "Value", "")  # parent container has no direct value

def edit_value(event):
    selected_item = treeview.focus()
    if not selected_item:
        return
    old_value = treeview.item(selected_item, "values")[0]
    new_value = simpledialog.askstring("Edit Value", "Enter new value:", initialvalue=old_value)
    if new_value is not None:
        treeview.item(selected_item, values=(old_value,new_value))
        xml_elem = item_to_xml[selected_item]
        xml_elem.text = new_value

def save_file():
    if tree:
        save_path = filedialog.asksaveasfilename(defaultextension=".arxml",
                                                 filetypes=[("ARXML files", "*.arxml")])
        if save_path:
            et.register_namespace('', "http://autosar.org/schema/r4.0")
            tree.write(save_path, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
tk.Button(root, text="Save", command=save_file).grid(row=0, column=3, padx=10, pady=10)

treeview.bind("<Double-1>", edit_value)
et.register_namespace('', "http://autosar.org/schema/r4.0")

root.mainloop()
