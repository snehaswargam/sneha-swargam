import tkinter as tk
from tkinter import filedialog, ttk, simpledialog, messagebox
import xml.etree.ElementTree as et

ns = {"a": "http://autosar.org/schema/r4.0"}

# ---- UI setup ----
root = tk.Tk()
root.title("ARXML Viewer")
root.geometry("900x600")

top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=8, pady=6)

entry = tk.Entry(top_frame, width=70)
entry.pack(side="left", padx=(0, 6))

tk.Button(top_frame, text="Browse", width=10, command=lambda: browse_file()).pack(side="left", padx=4)
tk.Button(top_frame, text="Load", width=8, command=lambda: read_file()).pack(side="left", padx=4)
tk.Button(top_frame, text="Bulk Edit", width=10, command=lambda: bulk_edit()).pack(side="left", padx=4)
tk.Button(top_frame, text="Save As...", width=10, command=lambda: save_file()).pack(side="left", padx=4)

# Treeview
treeview = ttk.Treeview(root, columns=("Value", "Edited"), show="tree headings", selectmode="extended")
treeview.heading("#0", text="Parameter")
treeview.heading("Value", text="Value")
treeview.heading("Edited", text="Edited")
treeview.pack(fill="both", expand=True, padx=8, pady=8)

# ---- Globals ----
file_path = None          # path chosen by user
et_tree = None            # ElementTree object
root_elem = None          # root XML element
item_to_param = {}        # mapping: treeview_iid -> param element (the whole param node)

# ------------------------
# Functions
# ------------------------
def browse_file():
    global file_path
    p = filedialog.askopenfilename(title="Select ARXML file", filetypes=[("ARXML files", "*.arxml"), ("All files", "*.*")])
    if p:
        file_path = p
        entry.delete(0, tk.END)
        entry.insert(0, p)

def read_file():
    global et_tree, root_elem, file_path
    if not file_path:
        messagebox.showinfo("Info", "Please choose a file first.")
        return
    et_tree = et.parse(file_path)
    root_elem = et_tree.getroot()
    parse_xml()

def parse_xml():
    """Populate treeview and build item_to_param mapping.
       Each displayed parameter row maps to its parameter element (not to VALUE child).
    """
    treeview.delete(*treeview.get_children())
    item_to_param.clear()

    # iterate Test-CONTAINER-VALUE containers
    for container in root_elem.findall(".//a:Test-CONTAINER-VALUE", ns):
        short = container.find("a:SHORT-NAME", ns)
        parent_label = short.text if short is not None else "NoName"
        parent_id = treeview.insert("", "end", text=parent_label, values=("", ""))

        # gather both numerical and textual params (direct children under PARAMETER-VALUES)
        # Use direct child search to avoid deep accidental matches
        param_area = container.find("a:PARAMETER-VALUES", ns)
        if param_area is None:
            continue

        # find parameter elements inside PARAMETER-VALUES
        param_elems = []
        param_elems.extend(param_area.findall("a:Test-NUMERICAL-PARAM-VALUE", ns))
        param_elems.extend(param_area.findall("a:Test-TEXTUAL-PARAM-VALUE", ns))

        for param in param_elems:
            # param is the whole parameter element (we will map to this)
            def_ref = param.find("a:DEFINITION-REF", ns)
            val_elem = param.find("a:VALUE", ns)
            param_label = def_ref.text.split("/")[-1] if def_ref is not None and def_ref.text else "UnknownDef"
            param_value = val_elem.text if (val_elem is not None and val_elem.text is not None) else ""
            item_id = treeview.insert(parent_id, "end", text=param_label, values=(param_value, ""))
            item_to_param[item_id] = param  # store the whole param element

# Edit single or ask for bulk (double-click)
def on_double_click(event):
    edit_value()

def edit_value():
    """Double-click edit for selected item (single selection). Ask whether bulk or single edit."""
    selected = treeview.focus()
    if not selected:
        return
    if selected not in item_to_param:
        messagebox.showinfo("Info", "Please select a parameter row (not a container).")
        return

    param_elem = item_to_param[selected]            # whole param element
    def_ref = param_elem.find("a:DEFINITION-REF", ns)
    if def_ref is None or not def_ref.text:
        messagebox.showinfo("Info", "Cannot find DEFINITION-REF for this parameter.")
        return
    param_name = def_ref.text.split("/")[-1]

    val_elem = param_elem.find("a:VALUE", ns)
    old_value = val_elem.text if (val_elem is not None and val_elem.text is not None) else ""

    # Ask whether bulk edit (all params with same parameter name)
    choice = messagebox.askyesno("Bulk Edit?",
                                 f"Do you want to update ALL parameters named '{param_name}'?\n\n"
                                 "Yes = update all occurrences\nNo = update only this one")

    new_value = simpledialog.askstring("Edit Value", f"Enter new value for '{param_name}':", initialvalue=old_value)
    if new_value is None:
        return

    if choice:
        # Bulk edit across both numerical & textual params
        count = 0
        # find all parameter elements in the whole document under PARAMETER-VALUES
        for container in root_elem.findall(".//a:Test-CONTAINER-VALUE", ns):
            param_area = container.find("a:PARAMETER-VALUES", ns)
            if param_area is None:
                continue
            all_params = []
            all_params.extend(param_area.findall("a:Test-NUMERICAL-PARAM-VALUE", ns))
            all_params.extend(param_area.findall("a:Test-TEXTUAL-PARAM-VALUE", ns))
            for p in all_params:
                p_def = p.find("a:DEFINITION-REF", ns)
                if p_def is not None and p_def.text and p_def.text.split("/")[-1] == param_name:
                    p_val = p.find("a:VALUE", ns)
                    if p_val is None:
                        # create VALUE element if missing
                        p_val = et.SubElement(p, "{%s}VALUE" % ns["a"])
                    p_val.text = new_value
                    count += 1
                    # update treeview row that maps to this param (if any)
                    for iid, mapped_param in item_to_param.items():
                        if mapped_param is p:
                            old_ui = treeview.item(iid, "values")[0]
                            treeview.item(iid, values=(old_ui, new_value))
        messagebox.showinfo("Bulk Edit", f"Updated {count} parameter(s) named '{param_name}'.")
    else:
        # single edit
        if val_elem is None:
            # create value element if absent
            val_elem = et.SubElement(param_elem, "{%s}VALUE" % ns["a"])
        val_elem.text = new_value
        old_ui = treeview.item(selected, "values")[0]
        treeview.item(selected, values=(old_ui, new_value))
        messagebox.showinfo("Edit", f"Updated parameter '{param_name}' to '{new_value}'.")

def bulk_edit():
    """Bulk edit by selecting one row (or selecting none then prompt)."""
    selected = treeview.focus()
    if not selected:
        messagebox.showinfo("Info", "Select a parameter row to choose parameter name for bulk edit.")
        return
    # simply reuse edit_value's bulk branch by forcing choice True
    # but we call a minimal version: ask new value and update all params with same def-ref
    if selected not in item_to_param:
        messagebox.showinfo("Info", "Please select a parameter row (not a container).")
        return

    param_elem = item_to_param[selected]
    def_ref = param_elem.find("a:DEFINITION-REF", ns)
    if def_ref is None or not def_ref.text:
        messagebox.showinfo("Info", "Cannot find DEFINITION-REF for this parameter.")
        return
    param_name = def_ref.text.split("/")[-1]
    new_value = simpledialog.askstring("Bulk Edit", f"Enter new value for all parameters named '{param_name}':")
    if new_value is None:
        return

    # apply the same logic as in edit_value bulk branch
    count = 0
    for container in root_elem.findall(".//a:Test-CONTAINER-VALUE", ns):
        param_area = container.find("a:PARAMETER-VALUES", ns)
        if param_area is None:
            continue
        all_params = []
        all_params.extend(param_area.findall("a:Test-NUMERICAL-PARAM-VALUE", ns))
        all_params.extend(param_area.findall("a:Test-TEXTUAL-PARAM-VALUE", ns))
        for p in all_params:
            p_def = p.find("a:DEFINITION-REF", ns)
            if p_def is not None and p_def.text and p_def.text.split("/")[-1] == param_name:
                p_val = p.find("a:VALUE", ns)
                if p_val is None:
                    p_val = et.SubElement(p, "{%s}VALUE" % ns["a"])
                p_val.text = new_value
                count += 1
                for iid, mapped_param in item_to_param.items():
                    if mapped_param is p:
                        old_ui = treeview.item(iid, "values")[0]
                        treeview.item(iid, values=(old_ui, new_value))
    messagebox.showinfo("Bulk Edit", f"Updated {count} parameter(s) named '{param_name}'.")

def save_file():
    global et_tree
    if et_tree is None:
        messagebox.showinfo("Info", "Nothing loaded to save.")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".arxml", filetypes=[("ARXML files", "*.arxml")])
    if not save_path:
        return
    # Register default namespace so output doesn't get ns0: prefixes
    et.register_namespace('', ns["a"])
    et_tree.write(save_path, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
    messagebox.showinfo("Saved", f"Saved to: {save_path}")

# bind double click
treeview.bind("<Double-1>", on_double_click)

# run
root.mainloop()
