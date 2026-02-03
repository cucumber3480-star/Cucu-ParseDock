import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path

from docx_reader import read_docx_paragraphs
from order_header import extract_order_number, extract_order_date
from event_parser import parse_paragraph_as_event
from error_logger import log_error


CAT_LABELS = {
    "arrival": "Надходження",
    "departure": "Вибуття",
    "medical": "Лікування",
    "business_trip": "Відрядження",
    "szch": "СЗЧ/зниклий",
    "other": "Інше",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Order Parser — Абзац = Подія")
        self.geometry("1500x700")

        self.files: list[str] = []
        self.events: list[dict] = []

        top = tk.Frame(self)
        top.pack(fill=tk.X)

        tk.Button(top, text="Add DOCX", command=self.add_files).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Parse All", command=self.parse_all).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Журнал", command=self.open_log).pack(side=tk.LEFT, padx=8)

        self.files_label = tk.Label(top, text="0 файлів")
        self.files_label.pack(side=tk.LEFT, padx=12)

        self.tree = ttk.Treeview(self, columns=("date", "order", "category", "event"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("order", text="№ наказу")
        self.tree.heading("category", text="Категорія")
        self.tree.heading("event", text="Подія (snippet)")

        self.tree.column("date", width=110, anchor="w")
        self.tree.column("order", width=90, anchor="w")
        self.tree.column("category", width=160, anchor="w")
        self.tree.column("event", width=1100, anchor="w")

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.open_full_text)

        self.status = tk.Label(self, text="Готово", anchor="w")
        self.status.pack(fill=tk.X)

    def add_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("DOCX", "*.docx")])
        if not paths:
            return
        self.files = list(paths)
        self.files_label.config(text=f"{len(self.files)} файлів")
        self.status.config(text="Файли додано. Натисни Parse All.")

    def clear(self):
        self.files = []
        self.events = []
        self.files_label.config(text="0 файлів")
        self.tree.delete(*self.tree.get_children())
        self.status.config(text="Очищено.")

    def parse_all(self):
        if not self.files:
            messagebox.showinfo("Info", "Додайте хоча б один DOCX")
            return

        self.events = []
        self.tree.delete(*self.tree.get_children())

        total = 0
        produced = 0

        for p in self.files:
            try:
                paragraphs = read_docx_paragraphs(p)
                order_no = extract_order_number(paragraphs)
                order_dt = extract_order_date(paragraphs)

                for para in paragraphs:
                    total += 1
                    ev = parse_paragraph_as_event(para, order_no, order_dt)
                    if not ev:
                        continue
                    produced += 1
                    ev["file"] = Path(p).name
                    self.events.append(ev)
                    self.tree.insert("", "end", values=(
                        ev["date"],
                        ev["order"],
                        CAT_LABELS.get(ev["category"], ev["category"]),
                        ev["snippet"],
                    ))
            except Exception as e:
                log_error(f"{Path(p).name}: {type(e).__name__}: {e}")

        self.status.config(text=f"Готово: абзаців {total}, подій {produced}. Double-click по рядку → повний текст.")

    def open_log(self):
        log_path = Path("parse_errors.log")
        win = tk.Toplevel(self)
        win.title("Журнал")
        win.geometry("900x600")
        txt = tk.Text(win, wrap="word")
        txt.pack(fill=tk.BOTH, expand=True)

        if log_path.exists():
            txt.insert("1.0", log_path.read_text(encoding="utf-8"))
        else:
            txt.insert("1.0", "Журнал порожній.")

    def open_full_text(self, _evt):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if idx < 0 or idx >= len(self.events):
            return

        ev = self.events[idx]
        win = tk.Toplevel(self)
        win.title(f"Повний текст — {ev.get('file','')}")
        win.geometry("1000x700")
        txt = tk.Text(win, wrap="word")
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", ev.get("raw", ""))


if __name__ == "__main__":
    App().mainloop()
