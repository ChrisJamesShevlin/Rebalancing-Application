import tkinter as tk
from tkinter import messagebox, font

class PortfolioPositionSizerDynamic:
    def __init__(self, root):
        self.root = root
        root.title('25Ten Delta Capital')
        root.geometry('1300x670')

        default_font = font.nametofont('TkDefaultFont')
        default_font.configure(size=12)
        root.option_add('*Font', default_font)

        self.rows = []
        self.headers = [
            "Instrument", "Sector", "Live Price", "Min Stake",
            "Margin @ Min", "Notional @ Min", "Weight (%)"
        ]

        self.dynamic_frame = tk.Frame(root)
        self.dynamic_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Controls
        control_frame = tk.Frame(self.dynamic_frame)
        control_frame.pack(anchor='w')

        tk.Label(control_frame, text="Account Balance (£):").pack(side='left')
        self.entry_balance = tk.Entry(control_frame, width=10)
        self.entry_balance.pack(side='left', padx=(0,10))

        tk.Label(control_frame, text="Desired Margin Usage (%):").pack(side='left')
        self.entry_margin_pct = tk.Entry(control_frame, width=6)
        self.entry_margin_pct.pack(side='left', padx=(0,10))

        tk.Button(control_frame, text="Add Instrument", command=self.add_row).pack(side='left')
        tk.Button(control_frame, text="Calculate Stakes", command=self.calculate).pack(side='left')

        # Table
        self.table_frame = tk.Frame(self.dynamic_frame)
        self.table_frame.pack(fill='x', pady=10)

        for col, header in enumerate(self.headers):
            tk.Label(self.table_frame, text=header, borderwidth=1, relief='solid', width=16).grid(row=0, column=col)

        tk.Label(self.table_frame, text='', width=6).grid(row=0, column=len(self.headers))

        # Default rows
        self.add_row(["US 500", "Equity", "", "", "", "", ""])
        self.add_row(["US Treasury Bond", "Bond", "", "", "", "", ""])
        self.add_row(["Gold", "Commodity", "", "", "", "", ""])

        # Output
        self.output = tk.Text(self.dynamic_frame, height=16, font=('Courier', 12), bg='#f9f9f9', state='disabled')
        self.output.pack(fill='both', expand=True, pady=(10,0))

    def add_row(self, values=None):
        row_idx = len(self.rows) + 1
        entries = []

        for col in range(len(self.headers)):
            ent = tk.Entry(self.table_frame, width=16)
            if values and col < len(values):
                ent.insert(0, str(values[col]))
            ent.grid(row=row_idx, column=col, padx=1, pady=2)
            entries.append(ent)

        btn = tk.Button(self.table_frame, text="Delete", command=lambda idx=row_idx: self.delete_row(idx))
        btn.grid(row=row_idx, column=len(self.headers), padx=1)

        self.rows.append((entries, btn))

    def delete_row(self, idx):
        if idx-1 < len(self.rows):
            entries, btn = self.rows[idx-1]
            for ent in entries:
                ent.grid_forget()
            btn.grid_forget()
            self.rows.pop(idx-1)

            for i in range(idx-1, len(self.rows)):
                for col, ent in enumerate(self.rows[i][0]):
                    ent.grid(row=i+1, column=col)
                self.rows[i][1].grid(row=i+1, column=len(self.headers))

    def calculate(self):
        self.output.config(state='normal')
        self.output.delete('1.0', tk.END)

        # Account inputs
        try:
            balance = float(self.entry_balance.get())
            margin_pct = float(self.entry_margin_pct.get()) / 100
            if balance <= 0 or not (0 < margin_pct < 1):
                raise ValueError
        except Exception:
            messagebox.showerror('Input Error', 'Enter valid account balance and margin %.')
            return

        target_total_margin = balance * margin_pct

        instruments = []
        for entries, _ in self.rows:
            try:
                inst = {
                    'name': entries[0].get().strip(),
                    'sector': entries[1].get().strip().lower(),
                    'price': float(entries[2].get()),
                    'min_stake': float(entries[3].get()),
                    'margin_min': float(entries[4].get()),
                    'notional_min': float(entries[5].get())
                }
                inst['margin_per_unit'] = inst['margin_min'] / inst['min_stake']
                inst['notional_per_unit'] = inst['notional_min'] / inst['min_stake']
                instruments.append(inst)
            except Exception:
                continue

        if not instruments:
            messagebox.showerror('Input Error', 'Enter at least one valid instrument.')
            return

        equity_idx = None
        fixed_idxs = []

        for i, inst in enumerate(instruments):
            if inst['sector'] == 'equity':
                equity_idx = i
            else:
                fixed_idxs.append(i)

        if equity_idx is None:
            messagebox.showerror('Input Error', 'One Equity instrument (US500) is required.')
            return

        stakes = [0.0] * len(instruments)
        margins = [0.0] * len(instruments)
        notionals = [0.0] * len(instruments)

        fixed_margin = 0.0

        # Fixed instruments (gold/bonds)
        for i in fixed_idxs:
            stakes[i] = instruments[i]['min_stake']
            margins[i] = stakes[i] * instruments[i]['margin_per_unit']
            notionals[i] = stakes[i] * instruments[i]['notional_per_unit']
            fixed_margin += margins[i]

        # Equity instrument (risk dial)
        eq = instruments[equity_idx]
        remaining_margin = target_total_margin - fixed_margin

        if remaining_margin <= 0:
            stakes[equity_idx] = eq['min_stake']
        else:
            stakes[equity_idx] = max(
                eq['min_stake'],
                remaining_margin / eq['margin_per_unit']
            )

        margins[equity_idx] = stakes[equity_idx] * eq['margin_per_unit']
        notionals[equity_idx] = stakes[equity_idx] * eq['notional_per_unit']

        total_margin = sum(margins)
        total_notional = sum(notionals)

        # Output
        self.output.insert(tk.END, f"{'Instrument':25s} {'Sector':10s} {'Stake (£/pt)':>15s} {'Notional £':>13s} {'Margin £':>12s}\n")
        self.output.insert(tk.END, '-' * 85 + '\n')

        for i, inst in enumerate(instruments):
            self.output.insert(
                tk.END,
                f"{inst['name']:25s} {inst['sector'].capitalize():10s} "
                f"{stakes[i]:15.4f} {notionals[i]:13.2f} {margins[i]:12.2f}\n"
            )

        self.output.insert(tk.END, '-' * 85 + '\n')
        self.output.insert(
            tk.END,
            f"{'TOTAL MARGIN USED:':<55s}{total_margin:12.2f} "
            f"(target {target_total_margin:.2f}, actual {(total_margin/balance)*100:.2f}%)\n"
        )

        self.output.config(state='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    app = PortfolioPositionSizerDynamic(root)
    root.mainloop()
