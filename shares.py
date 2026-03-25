import tkinter as tk
from tkinter import messagebox


class ShareAllocator:
    def __init__(self, root):
        self.root = root
        self.root.title("25Ten Delta – ISA Shares Allocator")
        self.root.geometry("1400x860")
        self.root.configure(bg="#111827")

        self.colors = {
            "bg": "#111827",
            "panel": "#1f2937",
            "panel2": "#0f172a",
            "fg": "#e5e7eb",
            "muted": "#9ca3af",
            "accent": "#60a5fa",
            "good": "#34d399",
            "warn": "#f59e0b",
            "bad": "#f87171",
            "entry_bg": "#0b1220",
            "button_blue": "#2563eb",
            "button_green": "#059669",
            "border": "#374151",
        }

        self.fonts = {
            "title": ("Liberation Sans", 20, "bold"),
            "subtitle": ("Liberation Sans", 10),
            "section": ("Liberation Sans", 13, "bold"),
            "body": ("Liberation Sans", 10),
            "body_bold": ("Liberation Sans", 10, "bold"),
            "mono": ("DejaVu Sans Mono", 10),
            "button": ("Liberation Sans", 10, "bold"),
            "card_label": ("Liberation Sans", 10),
            "card_value": ("Liberation Sans", 14, "bold"),
        }

        self.rows = []
        self.result_labels = {}

        self._build_ui()

    # ---------------- UI ----------------

    def _build_ui(self):
        top = tk.Frame(self.root, bg=self.colors["bg"])
        top.pack(fill="x", padx=10, pady=10)

        title = tk.Label(
            top,
            text="25Ten Delta – ISA Shares Allocator",
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            font=self.fonts["title"]
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            top,
            text="Manual allocation tool for monthly ISA purchases, drift control and buy planning",
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=self.fonts["subtitle"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        body = tk.Frame(self.root, bg=self.colors["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left = tk.Frame(body, bg=self.colors["bg"])
        left.pack(side="left", fill="y", padx=(0, 5), pady=0)

        right = tk.Frame(body, bg=self.colors["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=0)

        self._build_inputs(left)
        self._build_holdings(left)
        self._build_buttons(left)
        self._build_summary_cards(right)
        self._build_output(right)

    def _build_inputs(self, parent):
        panel = tk.Frame(parent, bg=self.colors["panel"], bd=1, relief="solid")
        panel.pack(fill="x", pady=(0, 10))

        tk.Label(
            panel,
            text="Inputs",
            bg=self.colors["panel"],
            fg=self.colors["accent"],
            font=self.fonts["section"]
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 12))

        tk.Label(
            panel,
            text="Cash Available (£)",
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            font=self.fonts["body"]
        ).grid(row=1, column=0, sticky="w", padx=12, pady=6)

        self.entry_cash = tk.Entry(
            panel,
            width=18,
            bg=self.colors["entry_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief="flat",
            font=self.fonts["body"]
        )
        self.entry_cash.insert(0, "0")
        self.entry_cash.grid(row=1, column=1, sticky="w", padx=(0, 12), pady=6)

        tk.Label(
            panel,
            text="Monthly Contribution (£)",
            bg=self.colors["panel"],
            fg=self.colors["fg"],
            font=self.fonts["body"]
        ).grid(row=2, column=0, sticky="w", padx=12, pady=6)

        self.entry_monthly = tk.Entry(
            panel,
            width=18,
            bg=self.colors["entry_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief="flat",
            font=self.fonts["body"]
        )
        self.entry_monthly.insert(0, "200")
        self.entry_monthly.grid(row=2, column=1, sticky="w", padx=(0, 12), pady=6)

    def _build_holdings(self, parent):
        panel = tk.Frame(parent, bg=self.colors["panel"], bd=1, relief="solid")
        panel.pack(fill="x", pady=(0, 10))

        tk.Label(
            panel,
            text="Holdings",
            bg=self.colors["panel"],
            fg=self.colors["accent"],
            font=self.fonts["section"]
        ).grid(row=0, column=0, columnspan=5, sticky="w", padx=12, pady=(10, 12))

        headers = [
            "Instrument",
            "Live Price (£)",
            "Shares Held",
            "Target Weight (%)"
        ]

        for c, h in enumerate(headers):
            tk.Label(
                panel,
                text=h,
                bg=self.colors["panel2"],
                fg=self.colors["fg"],
                width=18,
                relief="solid",
                bd=1,
                font=self.fonts["body_bold"]
            ).grid(row=1, column=c, padx=1, pady=1)

        self.table = panel

        self.add_row(["S&P 500 ETF", "0", "0", "42.0"])
        self.add_row(["World ex-US ETF", "0", "0", "28.0"])
        self.add_row(["Bond ETF", "0", "0", "30.0"])

    def _build_buttons(self, parent):
        btn_frame = tk.Frame(parent, bg=self.colors["bg"])
        btn_frame.pack(fill="x", pady=(0, 10))

        tk.Button(
            btn_frame,
            text="Calculate",
            command=self.calculate,
            bg=self.colors["button_blue"],
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
            font=self.fonts["button"]
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_frame,
            text="Clear Output",
            command=self.clear_output,
            bg=self.colors["button_green"],
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
            font=self.fonts["button"]
        ).pack(side="left")

    def _build_summary_cards(self, parent):
        cards = tk.Frame(parent, bg=self.colors["bg"])
        cards.pack(fill="x", pady=(0, 10))

        items = [
            "Portfolio Value",
            "Invested Value",
            "Cash This Cycle",
            "Largest Gap",
        ]

        for idx, item in enumerate(items):
            card = tk.Frame(cards, bg=self.colors["panel"], bd=1, relief="solid")
            card.grid(row=0, column=idx, padx=6, pady=6, sticky="nsew")
            cards.grid_columnconfigure(idx, weight=1)

            tk.Label(
                card,
                text=item,
                bg=self.colors["panel"],
                fg=self.colors["muted"],
                font=self.fonts["card_label"]
            ).pack(anchor="w", padx=10, pady=(8, 2))

            lbl = tk.Label(
                card,
                text="-",
                bg=self.colors["panel"],
                fg=self.colors["fg"],
                font=self.fonts["card_value"]
            )
            lbl.pack(anchor="w", padx=10, pady=(0, 10))
            self.result_labels[item] = lbl

    def _build_output(self, parent):
        panel = tk.Frame(parent, bg=self.colors["panel"], bd=1, relief="solid")
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="Allocation Analysis",
            bg=self.colors["panel"],
            fg=self.colors["accent"],
            font=self.fonts["section"]
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.output = tk.Text(
            panel,
            bg=self.colors["entry_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief="flat",
            height=30,
            font=self.fonts["mono"],
            state="disabled"
        )
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def add_row(self, values=None):
        row = len(self.rows) + 2
        entries = []

        for col in range(4):
            e = tk.Entry(
                self.table,
                width=18,
                bg=self.colors["entry_bg"],
                fg=self.colors["fg"],
                insertbackground=self.colors["fg"],
                relief="flat",
                font=self.fonts["body"]
            )
            e.insert(0, values[col] if values else "")
            e.grid(row=row, column=col, padx=1, pady=1)
            entries.append(e)

        self.rows.append(entries)

    # ---------------- Helpers ----------------

    def _set_output_text(self, text):
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state="disabled")

    def clear_output(self):
        self._set_output_text("")
        for lbl in self.result_labels.values():
            lbl.config(text="-", fg=self.colors["fg"])

    def _append(self, text):
        self.output.insert(tk.END, text)

    def _update_cards(self, portfolio_value, invested_value, cycle_cash, largest_gap_text, largest_gap_value):
        self.result_labels["Portfolio Value"].config(text=f"£{portfolio_value:,.2f}", fg=self.colors["fg"])
        self.result_labels["Invested Value"].config(text=f"£{invested_value:,.2f}", fg=self.colors["fg"])
        self.result_labels["Cash This Cycle"].config(text=f"£{cycle_cash:,.2f}", fg=self.colors["fg"])

        gap_color = self.colors["good"] if largest_gap_value >= 0 else self.colors["bad"]
        self.result_labels["Largest Gap"].config(
            text=f"{largest_gap_text}",
            fg=gap_color
        )

    # ---------------- Calculation ----------------

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

                if not name:
                    raise ValueError
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

        largest_gap_inst = None
        largest_gap_value = 0.0

        for inst in instruments:
            gap = (invested_value * inst["weight"]) - inst["value"]
            if largest_gap_inst is None or abs(gap) > abs(largest_gap_value):
                largest_gap_inst = inst["name"]
                largest_gap_value = gap

        if largest_gap_inst is None:
            largest_gap_text = "-"
        else:
            largest_gap_text = f"{largest_gap_inst} ({largest_gap_value:+.2f})"

        self._update_cards(
            portfolio_value=current_portfolio_value,
            invested_value=invested_value,
            cycle_cash=total_cash_for_cycle,
            largest_gap_text=largest_gap_text,
            largest_gap_value=largest_gap_value
        )

        self._append(f"CURRENT PORTFOLIO VALUE (incl. cash): £{current_portfolio_value:,.2f}\n")
        self._append(f"INVESTED VALUE:                    £{invested_value:,.2f}\n")
        self._append(f"CASH AVAILABLE:                    £{cash:,.2f}\n")
        self._append(f"MONTHLY CONTRIBUTION:              £{monthly:,.2f}\n")
        self._append(f"CASH AVAILABLE THIS CYCLE:         £{total_cash_for_cycle:,.2f}\n\n")

        self._append("CURRENT ALLOCATION\n")
        self._append("-" * 86 + "\n")
        for inst in instruments:
            current_weight = (inst["value"] / current_portfolio_value * 100.0) if current_portfolio_value > 0 else 0.0
            target_weight = inst["weight"] * 100.0
            drift = current_weight - target_weight
            self._append(
                f"{inst['name']:20s} "
                f"Value £ {inst['value']:9.2f}   "
                f"Current {current_weight:6.2f}%   "
                f"Target {target_weight:6.2f}%   "
                f"Drift {drift:+7.2f}%\n"
            )

        self._append("\n")
        self._append("REBALANCE ANALYSIS\n")
        self._append("-" * 86 + "\n")
        for inst in instruments:
            inst["target_now"] = invested_value * inst["weight"]
            inst["gap_now"] = inst["target_now"] - inst["value"]

            if inst["gap_now"] > 0:
                status = "UNDERWEIGHT"
            elif inst["gap_now"] < 0:
                status = "OVERWEIGHT"
            else:
                status = "HOLD"

            self._append(
                f"{inst['name']:20s} "
                f"Current £ {inst['value']:9.2f}   "
                f"Target £ {inst['target_now']:9.2f}   "
                f"Gap £ {inst['gap_now']:+9.2f}   "
                f"{status}\n"
            )

        self._append("\n")

        if all_zero:
            remaining_cash = total_cash_for_cycle

            self._append("INITIAL BUILD PLAN\n")
            self._append("-" * 86 + "\n")

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
                self._append(
                    f"Buy {qty:>4d} × {inst['name']} @ £{inst['price']:.2f}   Cost £{cost:.2f}\n"
                )

            self._append("-" * 86 + "\n")
            self._append(f"Cash remaining: £{remaining_cash:.2f}\n")

            self.output.config(state="disabled")
            return

        self._append("DCA MODE\n")
        self._append("-" * 86 + "\n")
        self._append(f"Monthly contribution added:        £{monthly:.2f}\n")
        self._append(f"Cash available for this cycle:     £{total_cash_for_cycle:.2f}\n\n")

        for inst in instruments:
            inst["target_after_cash"] = target_portfolio_value_after_cash * inst["weight"]
            inst["gap_after_cash"] = inst["target_after_cash"] - inst["value"]

            self._append(
                f"{inst['name']:20s} "
                f"Current £ {inst['value']:9.2f}   "
                f"Target(after cash) £ {inst['target_after_cash']:9.2f}   "
                f"Gap £ {inst['gap_after_cash']:+9.2f}\n"
            )

        self._append("\n")

        underweight = [
            inst for inst in instruments
            if inst["gap_after_cash"] > 0 and inst["price"] > 0
        ]

        if not underweight:
            self._append("RECOMMENDED BUY PLAN\n")
            self._append("-" * 86 + "\n")
            self._append("No underweight assets to buy.\n")
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

        self._append("RECOMMENDED BUY PLAN\n")
        self._append("-" * 86 + "\n")

        total_spend = 0.0
        any_buys = False

        for inst in instruments:
            qty = buy_plan[inst["name"]]
            if qty > 0:
                cost = qty * inst["price"]
                total_spend += cost
                any_buys = True
                self._append(
                    f"Buy {qty:>4d} × {inst['name']} @ £{inst['price']:.2f}   Cost £{cost:.2f}\n"
                )

        if not any_buys:
            self._append("No purchases possible with available cash.\n")
        else:
            self._append("-" * 86 + "\n")
            self._append(f"Total spend:    £{total_spend:.2f}\n")
            self._append(f"Cash remaining: £{remaining_cash:.2f}\n\n")

            self._append("POST-BUY PROJECTED HOLDINGS\n")
            self._append("-" * 86 + "\n")

            new_invested_value = invested_value + total_spend

            for inst in instruments:
                qty_bought = buy_plan[inst["name"]]
                new_shares = inst["shares"] + qty_bought
                new_value = inst["value"] + qty_bought * inst["price"]
                new_weight = (new_value / new_invested_value * 100.0) if new_invested_value > 0 else 0.0
                target_weight = inst["weight"] * 100.0

                self._append(
                    f"{inst['name']:20s} "
                    f"Shares {new_shares:5d}   "
                    f"Value £ {new_value:9.2f}   "
                    f"Weight {new_weight:6.2f}%   "
                    f"Target {target_weight:6.2f}%\n"
                )

        self.output.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ShareAllocator(root)
    root.mainloop()
