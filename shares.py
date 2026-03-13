import tkinter as tk
from tkinter import messagebox, font


class ShareAllocator:
    def __init__(self, root):
        self.root = root
        root.title("25Ten Delta – ISA Shares Allocator")
        root.geometry("1200x720")

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        root.option_add("*Font", default_font)

        self.rows = []

        # ─── Controls ─────────────────────────────────────────────
        control = tk.Frame(root)
        control.pack(anchor="w", padx=10, pady=8)

        tk.Label(control, text="Cash Available (£):").pack(side="left")
        self.entry_cash = tk.Entry(control, width=10)
        self.entry_cash.insert(0, "0")
        self.entry_cash.pack(side="left", padx=6)

        tk.Label(control, text="Monthly Contribution (£):").pack(side="left")
        self.entry_monthly = tk.Entry(control, width=8)
        self.entry_monthly.insert(0, "200")
        self.entry_monthly.pack(side="left", padx=6)

        tk.Button(control, text="Calculate", command=self.calculate).pack(side="left", padx=8)

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

        # Locked portfolio structure: 60/40 equities/bonds,
        # with equity sleeve split 60/40 S&P/ex-US
        self.add_row(["S&P 500 ETF", "0", "0", "36.0"])
        self.add_row(["World ex-US ETF", "0", "0", "24.0"])
        self.add_row(["Bond ETF", "0", "0", "40.0"])

        # ─── Output ───────────────────────────────────────────────
        self.output = tk.Text(
            root,
            height=24,
            bg="#f7f7f7",
            font=("Courier", 11),
            state="disabled"
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
        except ValueError:
            messagebox.showerror("Input error", "Invalid cash or monthly contribution.")
            self.output.config(state="disabled")
            return

        instruments = []
        invested_value = 0.0
        total_weight = 0.0

        for r in self.rows:
            try:
                name = r[0].get().strip()
                price = float(r[1].get())
                shares = int(r[2].get())
                weight = float(r[3].get()) / 100.0

                if price < 0 or shares < 0 or weight < 0:
                    raise ValueError

                value = price * shares
                invested_value += value
                total_weight += weight

                instruments.append({
                    "name": name,
                    "price": price,
                    "shares": shares,
                    "weight": weight,
                    "value": value
                })
            except ValueError:
                messagebox.showerror("Input error", "Invalid table input.")
                self.output.config(state="disabled")
                return

        if abs(total_weight - 1.0) > 0.001:
            messagebox.showerror(
                "Weight error",
                f"Target weights must sum to 100% (currently {total_weight * 100:.1f}%)."
            )
            self.output.config(state="disabled")
            return

        all_zero = all(inst["shares"] == 0 for inst in instruments)

        total_cash_for_cycle = cash + monthly
        current_portfolio_value = invested_value + cash
        target_portfolio_value_after_cash = invested_value + total_cash_for_cycle

        self.output.insert(tk.END, f"CURRENT PORTFOLIO VALUE (incl. cash): £{current_portfolio_value:,.2f}\n")
        self.output.insert(tk.END, f"INVESTED VALUE: £{invested_value:,.2f}\n")
        self.output.insert(tk.END, f"CASH AVAILABLE: £{cash:,.2f}\n\n")

        # ─── Current allocation ──────────────────────────────────
        self.output.insert(tk.END, "CURRENT ALLOCATION\n")
        self.output.insert(tk.END, "-" * 78 + "\n")
        for inst in instruments:
            current_weight = (inst["value"] / current_portfolio_value * 100.0) if current_portfolio_value > 0 else 0.0
            target_weight = inst["weight"] * 100.0
            drift = current_weight - target_weight
            self.output.insert(
                tk.END,
                f"{inst['name']:20s} "
                f"Value £ {inst['value']:8.2f}   "
                f"Current {current_weight:6.2f}%   "
                f"Target {target_weight:6.2f}%   "
                f"Drift {drift:+6.2f}%\n"
            )

        self.output.insert(tk.END, "\n")

        # ─── Rebalance analysis on currently invested value ──────
        self.output.insert(tk.END, "REBALANCE ANALYSIS\n")
        self.output.insert(tk.END, "-" * 78 + "\n")
        for inst in instruments:
            inst["target_now"] = invested_value * inst["weight"]
            inst["gap_now"] = inst["target_now"] - inst["value"]

            if inst["gap_now"] > 0:
                status = "UNDERWEIGHT"
            elif inst["gap_now"] < 0:
                status = "OVERWEIGHT"
            else:
                status = "HOLD"

            self.output.insert(
                tk.END,
                f"{inst['name']:20s} "
                f"Current £ {inst['value']:8.2f}   "
                f"Target £ {inst['target_now']:8.2f}   "
                f"Gap £ {inst['gap_now']:+8.2f}   "
                f"{status}\n"
            )

        self.output.insert(tk.END, "\n")

        # ─── Initial build logic ─────────────────────────────────
        if all_zero:
            remaining_cash = total_cash_for_cycle

            self.output.insert(tk.END, "INITIAL BUILD PLAN\n")
            self.output.insert(tk.END, "-" * 78 + "\n")

            planned_buys = []

            for inst in sorted(instruments, key=lambda x: x["weight"], reverse=True):
                if inst["price"] <= 0:
                    continue

                target_cash = total_cash_for_cycle * inst["weight"]
                qty = int(target_cash // inst["price"])

                if qty > 0:
                    cost = qty * inst["price"]
                    if cost > remaining_cash:
                        qty = int(remaining_cash // inst["price"])
                        cost = qty * inst["price"]

                    if qty > 0:
                        planned_buys.append((inst, qty, cost))
                        remaining_cash -= cost

            while True:
                affordable = [inst for inst in instruments if 0 < inst["price"] <= remaining_cash]
                if not affordable:
                    break

                best = max(
                    affordable,
                    key=lambda x: (total_cash_for_cycle * x["weight"]) - sum(
                        c for i, q, c in planned_buys if i["name"] == x["name"]
                    )
                )

                best_gap = (total_cash_for_cycle * best["weight"]) - sum(
                    c for i, q, c in planned_buys if i["name"] == best["name"]
                )

                if best_gap <= 0:
                    break

                found = False
                for idx, (i, q, c) in enumerate(planned_buys):
                    if i["name"] == best["name"]:
                        planned_buys[idx] = (i, q + 1, c + i["price"])
                        found = True
                        break

                if not found:
                    planned_buys.append((best, 1, best["price"]))

                remaining_cash -= best["price"]

            for inst, qty, cost in planned_buys:
                self.output.insert(
                    tk.END,
                    f"Buy {qty:>4d} × {inst['name']} @ £{inst['price']:.2f}   Cost £{cost:.2f}\n"
                )

            self.output.insert(tk.END, "-" * 78 + "\n")
            self.output.insert(tk.END, f"Cash remaining: £{remaining_cash:.2f}\n")

            self.output.config(state="disabled")
            return

        # ─── DCA / rebalance purchase plan ───────────────────────
        self.output.insert(tk.END, "DCA MODE\n")
        self.output.insert(tk.END, "-" * 78 + "\n")
        self.output.insert(tk.END, f"Monthly contribution added: £{monthly:.2f}\n")
        self.output.insert(tk.END, f"Cash available for this cycle: £{total_cash_for_cycle:.2f}\n\n")

        for inst in instruments:
            inst["target_after_cash"] = target_portfolio_value_after_cash * inst["weight"]
            inst["gap_after_cash"] = inst["target_after_cash"] - inst["value"]

            self.output.insert(
                tk.END,
                f"{inst['name']:20s} "
                f"Current £ {inst['value']:8.2f}   "
                f"Target(after cash) £ {inst['target_after_cash']:8.2f}   "
                f"Gap £ {inst['gap_after_cash']:+8.2f}\n"
            )

        self.output.insert(tk.END, "\n")

        underweight = [
            inst for inst in instruments
            if inst["gap_after_cash"] > 0 and inst["price"] > 0
        ]

        if not underweight:
            self.output.insert(tk.END, "RECOMMENDED BUY PLAN\n")
            self.output.insert(tk.END, "-" * 78 + "\n")
            self.output.insert(tk.END, "No underweight assets to buy.\n")
            self.output.config(state="disabled")
            return

        remaining_cash = total_cash_for_cycle
        buy_plan = {inst["name"]: 0 for inst in instruments}

        while True:
            affordable = [inst for inst in underweight if inst["price"] <= remaining_cash]
            if not affordable:
                break

            best = max(
                affordable,
                key=lambda x: x["gap_after_cash"] - (buy_plan[x["name"]] * x["price"])
            )

            remaining_gap = best["gap_after_cash"] - (buy_plan[best["name"]] * best["price"])

            if remaining_gap <= 0:
                break

            buy_plan[best["name"]] += 1
            remaining_cash -= best["price"]

        self.output.insert(tk.END, "RECOMMENDED BUY PLAN\n")
        self.output.insert(tk.END, "-" * 78 + "\n")

        total_spend = 0.0
        any_buys = False

        for inst in instruments:
            qty = buy_plan[inst["name"]]
            if qty > 0:
                cost = qty * inst["price"]
                total_spend += cost
                any_buys = True
                self.output.insert(
                    tk.END,
                    f"Buy {qty:>4d} × {inst['name']} @ £{inst['price']:.2f}   Cost £{cost:.2f}\n"
                )

        if not any_buys:
            self.output.insert(tk.END, "No purchases possible with available cash.\n")
        else:
            self.output.insert(tk.END, "-" * 78 + "\n")
            self.output.insert(tk.END, f"Total spend: £{total_spend:.2f}\n")
            self.output.insert(tk.END, f"Cash remaining: £{remaining_cash:.2f}\n\n")

            self.output.insert(tk.END, "POST-BUY PROJECTED HOLDINGS\n")
            self.output.insert(tk.END, "-" * 78 + "\n")

            new_invested_value = invested_value + total_spend

            for inst in instruments:
                qty_bought = buy_plan[inst["name"]]
                new_shares = inst["shares"] + qty_bought
                new_value = inst["value"] + qty_bought * inst["price"]
                new_weight = (new_value / new_invested_value * 100.0) if new_invested_value > 0 else 0.0
                target_weight = inst["weight"] * 100.0

                self.output.insert(
                    tk.END,
                    f"{inst['name']:20s} "
                    f"Shares {new_shares:5d}   "
                    f"Value £ {new_value:8.2f}   "
                    f"Weight {new_weight:6.2f}%   "
                    f"Target {target_weight:6.2f}%\n"
                )

        self.output.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShareAllocator(root)
    root.mainloop()
