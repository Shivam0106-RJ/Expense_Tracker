import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json, os
import ttkbootstrap as tb
from ttkbootstrap.constants import *

DATA_FILE = 'expenses.json'
MONTHLY_BUDGET = 1000  # Set your monthly budget here

class ExpenseTrackerApp(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")  # modern themes: cosmo, flatly, superhero, morph…
        self.title("💰 Expense Tracker")
        self.geometry("800x600")
        self.resizable(False, False)

        self.expenses = []
        self.load_expenses()

        self.create_widgets()
        self.refresh_expense_list()

    def create_widgets(self):
        # Notebook (tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # ---------------- Tab 1: Add Expense ----------------
        frame1 = ttk.Frame(notebook, padding=10)
        notebook.add(frame1, text="➕ Add Expense")

        ttk.Label(frame1, text="Amount ($):").grid(row=0, column=0, sticky="w", pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(frame1, textvariable=self.amount_var).grid(row=0, column=1, pady=5, sticky="ew")

        ttk.Label(frame1, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        categories = ["Food", "Travel", "Shopping", "Bills", "Health", "Miscellaneous"]
        ttk.Combobox(frame1, textvariable=self.category_var, values=categories).grid(row=1, column=1, pady=5, sticky="ew")

        ttk.Label(frame1, text="Date:").grid(row=2, column=0, sticky="w", pady=5)
        self.date_var = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
        ttk.Entry(frame1, textvariable=self.date_var).grid(row=2, column=1, pady=5, sticky="ew")

        ttk.Label(frame1, text="Description:").grid(row=3, column=0, sticky="w", pady=5)
        self.desc_var = tk.StringVar()
        ttk.Entry(frame1, textvariable=self.desc_var).grid(row=3, column=1, pady=5, sticky="ew")

        frame1.columnconfigure(1, weight=1)

        tb.Button(frame1, text="✅ Add Expense", bootstyle=SUCCESS, command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=10)

        # ---------------- Tab 2: Expenses List ----------------
        frame2 = ttk.Frame(notebook, padding=10)
        notebook.add(frame2, text="📜 Expenses List")

        columns = ("Date", "Amount", "Category", "Description")
        self.tree = ttk.Treeview(frame2, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, pady=5)

        tb.Button(frame2, text="❌ Delete Selected", bootstyle=DANGER, command=self.delete_selected).pack(pady=5)

        # ---------------- Tab 3: Statistics ----------------
        frame3 = ttk.Frame(notebook, padding=10)
        notebook.add(frame3, text="📊 Statistics")

        # Budget progress
        ttk.Label(frame3, text="Monthly Budget Progress:", font=("Segoe UI", 11, "bold")).pack(pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame3, orient="horizontal", length=500, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(pady=5)

        # Summary tables
        ttk.Label(frame3, text="Summary by Category:", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.category_tree = ttk.Treeview(frame3, columns=("Category", "Total"), show="headings", height=5)
        self.category_tree.heading("Category", text="Category")
        self.category_tree.heading("Total", text="Total ($)")
        self.category_tree.pack(pady=5)

        ttk.Label(frame3, text="Summary by Date:", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.date_tree = ttk.Treeview(frame3, columns=("Date", "Total"), show="headings", height=5)
        self.date_tree.heading("Date", text="Date")
        self.date_tree.heading("Total", text="Total ($)")
        self.date_tree.pack(pady=5)

    def add_expense(self):
        try:
            amount = float(self.amount_var.get())
            if amount <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter a valid positive number for amount")
            return

        category = self.category_var.get() or "Miscellaneous"
        date_str = self.date_var.get()
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format")
            return

        desc = self.desc_var.get()
        expense = {"amount": amount, "category": category, "date": date_str, "description": desc}
        self.expenses.append(expense)
        self.save_expenses()
        self.refresh_expense_list()
        self.update_statistics()

        # clear fields
        self.amount_var.set(""); self.category_var.set(""); self.date_var.set(datetime.today().strftime('%Y-%m-%d')); self.desc_var.set("")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select an expense to delete")
            return
        idx = self.tree.index(selected[0])
        confirm = messagebox.askyesno("Confirm", "Delete selected expense?")
        if confirm:
            del self.expenses[idx]
            self.save_expenses()
            self.refresh_expense_list()
            self.update_statistics()

    def refresh_expense_list(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for exp in self.expenses:
            self.tree.insert("", "end", values=(exp["date"], f"${exp['amount']:.2f}", exp["category"], exp["description"]))
        self.update_statistics()

    def save_expenses(self):
        with open(DATA_FILE, "w") as f: json.dump(self.expenses, f, indent=4)

    def load_expenses(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f: self.expenses = json.load(f)

    def update_statistics(self):
        # Budget Progress
        total_spent = sum(exp["amount"] for exp in self.expenses)
        progress = min((total_spent / MONTHLY_BUDGET) * 100, 100)
        self.progress_var.set(progress)

        # Category summary
        for i in self.category_tree.get_children(): self.category_tree.delete(i)
        sums = {}
        for exp in self.expenses:
            sums[exp['category']] = sums.get(exp['category'], 0) + exp['amount']
        for cat, total in sums.items():
            self.category_tree.insert("", "end", values=(cat, f"${total:.2f}"))

        # Date summary
        for i in self.date_tree.get_children(): self.date_tree.delete(i)
        sums = {}
        for exp in self.expenses:
            sums[exp['date']] = sums.get(exp['date'], 0) + exp['amount']
        for date, total in sorted(sums.items()):
            self.date_tree.insert("", "end", values=(date, f"${total:.2f}"))

if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
