import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = {}
        
        # GUI Elements
        tk.Label(root, text="Amount:").grid(row=0, column=0)
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1)
        tk.Label(root, text="Category:").grid(row=1, column=0)
        self.category_entry = tk.Entry(root)
        self.category_entry.grid(row=1, column=1)
        tk.Button(root, text="Add Expense", command=self.add_expense).grid(row=2, column=0, columnspan=2)
        tk.Button(root, text="Show Chart", command=self.show_chart).grid(row=3, column=0, columnspan=2)

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        if amount and category:
            try:
                amount = float(amount)
                if category in self.expenses:
                    self.expenses[category] += amount
                else:
                    self.expenses[category] = amount
                messagebox.showinfo("Success", "Expense added!")
                self.amount_entry.delete(0, tk.END)
                self.category_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount.")
        else:
            messagebox.showerror("Error", "Please fill all fields.")

    def show_chart(self):
        if self.expenses:
            categories = list(self.expenses.keys())
            amounts = list(self.expenses.values())
            fig, ax = plt.subplots()
            ax.bar(categories, amounts)
            ax.set_title("Expenses by Category")
            canvas = FigureCanvasTkAgg(fig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().grid(row=4, column=0, columnspan=2)
        else:
            messagebox.showinfo("Info", "No expenses to display.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()