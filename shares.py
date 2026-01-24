import tkinter as tk
from tkinter import messagebox, font

class ShareAllocator:
    def __init__(self, root):
        self.root = root
        root.title("25Ten Delta – Share DCA Allocator")
        root.geometry("1200x680")

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        root.option_add("*Font", default_font)

        self.rows = []

        # ─── Controls ─────────────────────────────────────────────
        control = tk.Frame(root)
        control.pack(anchor="w", padx=10, pady=8)

        tk.Label(control, text="Cash Available (£):").pack(side="left")
        self.entry_cash = tk.Entry(control, width=10)
        self.entry_cash.pack(side="left", padx=6)

        tk.Label(control, text="Monthly Contribution (£):").pack(side="left")
        self.entry_monthly = tk.Entry(control, width=8)
        self.entry_monthly.insert(0, "200")
        self.entry_monthly.pack(side="left", padx=6)

        tk.Button(control, text="Add Instrument", command=self.add_row).pack(side="left", padx=6)
        tk.Button(control, text="Calculate", command=self.calculate).pack(side="left")

        # ─── Table ────────────────────────────────────────────────
        headers = [
            "Instrument",
            "Live Price (£)",
            "Shares Held",
            "Target Weight (%)"
        ]

        table = tk.Frame(root)
        table.pack(padx=10, pady=10)

        for c, h in enumerate(headers):
            tk.Label(table, text=h, borderwidth=1, relief="solid", width=24).grid(row=0, column=c)

        self.table = table

        # ─── Default portfolio (LOCKED STRUCTURE) ─────────────────
        self.add_row(["S&P 500 ETF", "0", "0", "55"])
        self.add_row(["World ex-US ETF", "0", "0", "10"])
        self.add_row(["Bond ETF", "0", "0", "25"])
        self.add_row(["Gold ETC", "0", "0", "10"])

        # ─── Output ───────────────────────────────────────────────
        self.output = tk.Text(
            root, height=20, bg="#f7f7f7", font=("Courier", 11), state="disabled"
        )
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

    def add_row(self, values=None):
        row = len(self.rows) + 1
        entries = []

        e0 = tk.Entry(self.table, width=24)
        e0.insert(0, values[0] if values else "")
        e0.grid(row=row, column=0)
        entries.append(e0)

        e1 = tk.Entry(self.table, width=24)
        e1.insert(0, values[1] if values else "0")
        e1.grid(row=row, column=1)
        entries.append(e1)

        e2 = tk.Entry(self.table, width=24)
        e2.insert(0, values[2] if values else "0")
        e2.grid(row=row, column=2)
        entries.append(e2)

        e3 = tk.Entry(self.table, width=24)
        e3.insert(0, values[3] if values else "0")
        e3.grid(row=row, column=3)
        entries.append(e3)

        self.rows.append(entries)

    def calculate(self):
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)

        try:
            cash = float(self.entry_cash.get())
            monthly = float(self.entry_monthly.get())
            if cash < 0 or monthly < 0:
                raise ValueError
        except:
            messagebox.showerror("Input error", "Invalid cash or monthly contribution.")
            return

        instruments = []
        portfolio_value = cash
        total_weight = 0.0

        for r in self.rows:
            try:
                name = r[0].get().strip()
                price = float(r[1].get())
                shares = int(r[2].get())
                weight = float(r[3].get()) / 100

                value = price * shares
                portfolio_value += value
                total_weight += weight

                instruments.append({
                    "name": name,
                    "price": price,
                    "shares": shares,
                    "weight": weight,
                    "value": value
                })
            except:
                continue

        # ─── Weight validation ────────────────────────────────────
        if abs(total_weight - 1.0) > 0.001:
            messagebox.showerror(
                "Weight error",
                f"Target weights must sum to 100% (currently {total_weight*100:.1f}%)."
            )
            return

        all_zero = all(inst["shares"] == 0 for inst in instruments)

        self.output.insert(
            tk.END, f"PORTFOLIO VALUE (GBP): £{portfolio_value:,.2f}\n\n"
        )

        # ─── INITIAL BUILD (CASH-AWARE + EXPOSURE GUARANTEE) ──────
        if all_zero:
            remaining_cash = cash
            self.output.insert(tk.END, "INITIAL BUILD PLAN\n")
            self.output.insert(tk.END, "-" * 70 + "\n")

            # Core fix: allocate cash proportionally, highest weight first
            for inst in sorted(instruments, key=lambda x: x["weight"], reverse=True):
                if inst["price"] <= 0:
                    continue

                target_cash = cash * inst["weight"]
                max_affordable = int(remaining_cash // inst["price"])
                qty = int(min(target_cash // inst["price"], max_affordable))

                # Exposure guarantee for expensive assets (e.g. gold)
                if qty == 0 and remaining_cash >= inst["price"] and inst["weight"] > 0:
                    qty = 1

                cost = qty * inst["price"]

                if qty > 0:
                    remaining_cash -= cost
                    self.output.insert(
                        tk.END,
                        f"Buy {qty:>4d} × {inst['name']} @ £{inst['price']:.2f} "
                        f"(£{cost:.2f})\n"
                    )

            self.output.insert(tk.END, "-" * 70 + "\n")
            self.output.insert(tk.END, f"Cash remaining: £{remaining_cash:.2f}\n")

        # ─── DCA MODE (UNCHANGED LOGIC) ───────────────────────────
        else:
            cash += monthly
            portfolio_value += monthly

            for inst in instruments:
                inst["target"] = portfolio_value * inst["weight"]
                inst["gap"] = inst["target"] - inst["value"]
                inst["gap_pct"] = inst["gap"] / inst["target"] if inst["target"] > 0 else 0

            affordable = [
                inst for inst in instruments
                if inst["price"] <= cash and inst["gap"] > 0
            ]

            self.output.insert(tk.END, "DCA MODE\n")
            self.output.insert(tk.END, "-" * 70 + "\n")

            for inst in instruments:
                self.output.insert(
                    tk.END,
                    f"{inst['name']:25s} "
                    f"Value £{inst['value']:9.2f} "
                    f"Target £{inst['target']:9.2f} "
                    f"Gap £{inst['gap']:9.2f}\n"
                )

            if affordable:
                buy = max(affordable, key=lambda x: x["gap_pct"])
                self.output.insert(
                    tk.END,
                    f"\nRECOMMENDED BUY:\n"
                    f"Buy 1 × {buy['name']} @ £{buy['price']:.2f}\n"
                    f"Cash after buy: £{cash - buy['price']:.2f}\n"
                )
            else:
                self.output.insert(tk.END, "\nNo trade this month.\n")

        self.output.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShareAllocator(root)
    root.mainloop()
