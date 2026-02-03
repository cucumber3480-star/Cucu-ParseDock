import tkinter as tk
from tkinter import ttk, messagebox

from config_store import (
    get_units, get_arrival_types, get_departure_types,
    save_mapping
)

class ConfigEditor(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Довідники")
        self.geometry("900x500")

        self._mode = tk.StringVar(value="units")
        self._data = {}

        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        tk.Radiobutton(top, text="Підрозділи", variable=self._mode, value="units",
                       command=self.load).pack(side=tk.LEFT)
        tk.Radiobutton(top, text="Типи надходження", variable=self._mode, value="arrival_types",
                       command=self.load).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(top, text="Типи вибуття", variable=self._mode, value="departure_types",
                       command=self.load).pack(side=tk.LEFT)

        btns = tk.Frame(self)
        btns.pack(fill=tk.X, padx=8, pady=6)
        tk.Button(btns, text="+ Додати", command=self.add_row).pack(side=tk.LEFT)
        tk.Button(btns, text="– Видалити", command=self.delete_row).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Зберегти", command=self.save).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Закрити", command=self.destroy).pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self, columns=("key", "value"), show="headings")
        self.tree.heading("key", text="Ключ (код)")
        self.tree.heading("value", text="Значення (назва)")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self.tree.bind("<Double-1>", self._begin_edit)

        self._edit = None
        self.load()

    def _current_spec(self):
        m = self._mode.get()
        if m == "units":
            return "units.yaml", "units", get_units()
        if m == "arrival_types":
            return "arrival_types.yaml", "arrival_types", get_arrival_types()
        return "departure_types.yaml", "departure_types", get_departure_types()

    def load(self):
        _, _, mapping = self._current_spec()
        self._data = dict(mapping)

        self.tree.delete(*self.tree.get_children())
        for k in sorted(self._data.keys(), key=lambda s: s.lower()):
            self.tree.insert("", "end", values=(k, self._data[k]))

    def add_row(self):
        # add empty row and start editing key
        iid = self.tree.insert("", "end", values=("", ""))
        self.tree.selection_set(iid)
        self.tree.see(iid)
        self._begin_edit_cell(iid, "key")

    def delete_row(self):
        sel = self.tree.selection()
        if not sel:
            return
        for iid in sel:
            self.tree.delete(iid)

    def save(self):
        # build dict from tree
        mapping = {}
        for iid in self.tree.get_children():
            k, v = self.tree.item(iid, "values")
            k = (k or "").strip()
            v = (v or "").strip()
            if not k:
                continue
            if k in mapping:
                messagebox.showerror("Помилка", f"Дубль ключа: {k}")
                return
            mapping[k] = v

        fname, root_key, _ = self._current_spec()
        try:
            save_mapping(fname, root_key, mapping)
            messagebox.showinfo("OK", "Збережено.")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def _begin_edit(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        iid = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)  # '#1' or '#2'
        field = "key" if col == "#1" else "value"
        if iid:
            self._begin_edit_cell(iid, field)

    def _begin_edit_cell(self, iid, field):
        if self._edit is not None:
            self._end_edit(commit=True)

        col = 0 if field == "key" else 1
        bbox = self.tree.bbox(iid, column=f"#{col+1}")
        if not bbox:
            return
        x, y, w, h = bbox
        value = self.tree.item(iid, "values")[col]

        self._edit = tk.Entry(self.tree)
        self._edit.place(x=x, y=y, width=w, height=h)
        self._edit.insert(0, value)
        self._edit.focus_set()

        self._edit.bind("<Return>", lambda e: self._end_edit(True))
        self._edit.bind("<Escape>", lambda e: self._end_edit(False))
        self._edit.bind("<FocusOut>", lambda e: self._end_edit(True))

        self._edit_iid = iid
        self._edit_col = col

    def _end_edit(self, commit: bool):
        if self._edit is None:
            return
        if commit:
            new_val = self._edit.get()
            vals = list(self.tree.item(self._edit_iid, "values"))
            while len(vals) < 2:
                vals.append("")
            vals[self._edit_col] = new_val
            self.tree.item(self._edit_iid, values=tuple(vals))
        self._edit.destroy()
        self._edit = None
