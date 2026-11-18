import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import json
import os

DATA_FILE = "expenses.json"

CATEGORIES = [
    "Food", "Transport", "Housing", "Utilities",
    "Entertainment", "Health", "Shopping", "Other"
]

# Color palette
COLOR_BG = "#1e293b"          # dark slate background
COLOR_PANEL = "#273449"       # slightly lighter panel
COLOR_ACCENT = "#38bdf8"      # sky blue accent
COLOR_ACCENT_DARK = "#0ea5e9"
COLOR_TEXT = "#f1f5f9"
COLOR_SUBTEXT = "#94a3b8"
COLOR_SUCCESS = "#22c55e"
COLOR_DANGER = "#ef4444"
COLOR_ROW_ALT1 = "#1e293b"
COLOR_ROW_ALT2 = "#243248"

CATEGORY_COLORS = {
    "Food": "#f97316",
    "Transport": "#3b82f6",
    "Housing": "#a855f7",
    "Utilities": "#eab308",
    "Entertainment": "#ec4899",
    "Health": "#22c55e",
    "Shopping": "#06b6d4",
    "Other": "#64748b",
}


class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💰 Expense Tracker")
        self.geometry("820x560")
        self.configure(bg=COLOR_BG)
        self.minsize(720, 480)

        self.expenses = []
        self.load_data()

        self._build_style()
        self._build_ui()
        self._refresh_table()

    # ---------- Styling ----------
    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=COLOR_ROW_ALT1,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_ROW_ALT1,
            rowheight=28,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=COLOR_ACCENT_DARK,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", COLOR_ACCENT)])
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])

        style.configure("TCombobox", fieldbackground="white", padding=4)

    # ---------- UI ----------
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLOR_ACCENT_DARK, height=70)
        header.pack(fill="x", side="top")
        tk.Label(
            header, text="💰 Expense Tracker", bg=COLOR_ACCENT_DARK,
            fg="white", font=("Segoe UI", 20, "bold")
        ).pack(side="left", padx=20, pady=15)

        self.total_label = tk.Label(
            header, text="Total: RS:0.00", bg=COLOR_ACCENT_DARK,
            fg="white", font=("Segoe UI", 14, "bold")
        )
        self.total_label.pack(side="right", padx=20)

        # Input panel
        form = tk.Frame(self, bg=COLOR_PANEL, pady=15, padx=15)
        form.pack(fill="x", padx=10, pady=10)

        # Date
        tk.Label(form, text="Date (YYYY-MM-DD)", bg=COLOR_PANEL, fg=COLOR_SUBTEXT,
                  font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(form, width=14, font=("Segoe UI", 10))
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=0, padx=(0, 10), pady=(2, 0))

        # Category
        tk.Label(form, text="Category", bg=COLOR_PANEL, fg=COLOR_SUBTEXT,
                  font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w")
        self.category_box = ttk.Combobox(form, values=CATEGORIES, width=14, state="readonly")
        self.category_box.current(0)
        self.category_box.grid(row=1, column=1, padx=(0, 10), pady=(2, 0))

        # Description
        tk.Label(form, text="Description", bg=COLOR_PANEL, fg=COLOR_SUBTEXT,
                  font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w")
        self.desc_entry = tk.Entry(form, width=28, font=("Segoe UI", 10))
        self.desc_entry.grid(row=1, column=2, padx=(0, 10), pady=(2, 0))

        # Amount
        tk.Label(form, text="Amount (Rs)", bg=COLOR_PANEL, fg=COLOR_SUBTEXT,
                  font=("Segoe UI", 9)).grid(row=0, column=3, sticky="w")
        self.amount_entry = tk.Entry(form, width=12, font=("Segoe UI", 10))
        self.amount_entry.grid(row=1, column=3, padx=(0, 10), pady=(2, 0))

        # Add button
        add_btn = tk.Button(
            form, text="+ Add Expense", bg=COLOR_SUCCESS, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=6,
            activebackground="#16a34a", cursor="hand2",
            command=self.add_expense
        )
        add_btn.grid(row=1, column=4, padx=(10, 0), pady=(2, 0))

        self.date_entry.bind("<Return>", lambda e: self.add_expense())
        self.desc_entry.bind("<Return>", lambda e: self.add_expense())
        self.amount_entry.bind("<Return>", lambda e: self.add_expense())

        # Table
        table_frame = tk.Frame(self, bg=COLOR_BG)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text="Amount")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("description", width=320, anchor="w")
        self.tree.column("amount", width=100, anchor="e")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for cat, color in CATEGORY_COLORS.items():
            self.tree.tag_configure(cat, foreground=color)

        # Bottom action bar
        bottom = tk.Frame(self, bg=COLOR_BG)
        bottom.pack(fill="x", padx=10, pady=(0, 10))

        del_btn = tk.Button(
            bottom, text="🗑 Delete Selected", bg=COLOR_DANGER, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=6,
            activebackground="#dc2626", cursor="hand2",
            command=self.delete_selected
        )
        del_btn.pack(side="left")

        clear_btn = tk.Button(
            bottom, text="Clear All", bg=COLOR_SUBTEXT, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=6,
            activebackground="#64748b", cursor="hand2",
            command=self.clear_all
        )
        clear_btn.pack(side="left", padx=8)

    # ---------- Logic ----------
    def add_expense(self):
        d = self.date_entry.get().strip()
        cat = self.category_box.get().strip()
        desc = self.desc_entry.get().strip()
        amt = self.amount_entry.get().strip()

        if not d or not cat or not amt:
            messagebox.showwarning("Missing info", "Please fill date, category, and amount.")
            return
        try:
            amt_val = round(float(amt), 2)
            if amt_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a positive number.")
            return

        try:
            year, month, day = d.split("-")
            date(int(year), int(month), int(day))
        except Exception:
            messagebox.showerror("Invalid date", "Date must be in YYYY-MM-DD format.")
            return

        self.expenses.append({
            "date": d, "category": cat, "description": desc or "-", "amount": amt_val
        })
        self.save_data()
        self._refresh_table()

        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.focus_set()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select a row to delete first.")
            return
        index = self.tree.index(selected[0])
        del self.expenses[index]
        self.save_data()
        self._refresh_table()

    def clear_all(self):
        if not self.expenses:
            return
        if messagebox.askyesno("Clear all", "Delete ALL expenses? This cannot be undone."):
            self.expenses = []
            self.save_data()
            self._refresh_table()

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        sorted_expenses = sorted(self.expenses, key=lambda x: x["date"])
        total = 0.0
        for i, exp in enumerate(sorted_expenses):
            tag = exp["category"] if exp["category"] in CATEGORY_COLORS else "Other"
            self.tree.insert(
                "", "end",
                values=(exp["date"], exp["category"], exp["description"], f"${exp['amount']:.2f}"),
                tags=(tag,)
            )
            total += exp["amount"]

        self.total_label.config(text=f"Total: ${total:.2f}")

    # ---------- Persistence ----------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.expenses = json.load(f)
            except Exception:
                self.expenses = []

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.expenses, f, indent=2)


if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()