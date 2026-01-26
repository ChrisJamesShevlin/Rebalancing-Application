import math
import tkinter as tk
from tkinter import messagebox, font


def round_down_to_step(x: float, step: float) -> float:
    if step <= 0:
        return x
    return math.floor(x / step) * step


def safe_float(s: str):
    s = s.strip()
    if s == "":
        return None
    return float(s)


class PortfolioDepositAllocator:

    def __init__(self, root):
        self.root = root
        root.title("25Ten Delta – Deposit Allocator")
        root.geometry("1250x620")

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        root.option_add("*Font", default_font)

        # -----------------------------
        # Account controls
        # -----------------------------
        ctrl = tk.Frame(root)
        ctrl.pack(anchor="w", padx=10, pady=5)

        tk.Label(ctrl, text="Account Balance (£):").grid(row=0, column=0, sticky="w")
        self.entry_balance = tk.Entry(ctrl, width=10)
        self.entry_balance.grid(row=0, column=1, padx=5)

        tk.Label(ctrl, text="Target Margin %:").grid(row=0, column=2, sticky="w")
        self.entry_margin_pct = tk.Entry(ctrl, width=6)
        self.entry_margin_pct.grid(row=0, column=3, padx=5)

        tk.Button(ctrl, text="Calculate", command=self.calculate).grid(row=0, column=4, padx=10)

        # -----------------------------
        # Instrument table (FIXED ROWS)
        # -----------------------------
        table = tk.Frame(root)
        table.pack(fill="x", padx=10, pady=10)

        headers = [
            "Instrument",
            "Sector",
            "Live Price",
            "Min Stake",
            "Margin @ Min",
            "Notional @ Min",
            "Weight %"
        ]

        for c, h in enumerate(headers):
            tk.Label(table, text=h, font=("TkDefaultFont", 10, "bold")).grid(row=0, column=c, padx=5)

        self.rows = []

        fixed_instruments = [
            ("US500", "equity", "55"),
            ("Bonds", "bond", "35"),
            ("Gold", "commodity", "10")
        ]

        for r, (name, sector, weight) in enumerate(fixed_instruments, start=1):
            entries = []

            e_name = tk.Entry(table, width=14)
            e_name.insert(0, name)
            e_name.config(state="disabled")
            e_name.grid(row=r, column=0, padx=3)
            entries.append(e_name)

            e_sector = tk.Entry(table, width=14)
            e_sector.insert(0, sector)
            e_sector.config(state="disabled")
            e_sector.grid(row=r, column=1, padx=3)
            entries.append(e_sector)

            for c in range(2, 6):
                e = tk.Entry(table, width=14)
                e.grid(row=r, column=c, padx=3)
                entries.append(e)

            e_weight = tk.Entry(table, width=14)
            e_weight.insert(0, weight)
            e_weight.grid(row=r, column=6, padx=3)
            entries.append(e_weight)

            self.rows.append(entries)

        # -----------------------------
        # Output
        # -----------------------------
        self.output = tk.Text(root, height=18, width=145, state="disabled")
        self.output.pack(padx=10, pady=10)

    # --------------------------------------------------
    # Calculation logic (weights = NOTIONAL, margin = constraint)
    # --------------------------------------------------
    def calculate(self):
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)

        # ---- Account inputs ----
        try:
            balance = float(self.entry_balance.get())
            margin_pct = float(self.entry_margin_pct.get()) / 100.0
            if balance <= 0 or not (0 < margin_pct < 1):
                raise ValueError
        except Exception:
            messagebox.showerror("Input Error", "Enter a valid balance and margin %.") 
            self.output.config(state="disabled")
            return

        target_total_margin = balance * margin_pct

        # ---- Read instrument rows ----
        instruments = []
        for entries in self.rows:
            try:
                name = entries[0].get()
                sector = entries[1].get()
                price = safe_float(entries[2].get())
                min_stake = safe_float(entries[3].get())
                margin_min = safe_float(entries[4].get())
                notional_min = safe_float(entries[5].get())
                weight_pct = safe_float(entries[6].get())

                if None in (price, min_stake, margin_min, notional_min, weight_pct):
                    raise ValueError

                if min_stake <= 0 or margin_min <= 0 or notional_min <= 0 or weight_pct <= 0:
                    raise ValueError

                inst = {
                    "name": name,
                    "sector": sector,
                    "price": price,
                    "min_stake": min_stake,
                    "margin_per_unit": margin_min / min_stake,     # £ margin per £/pt
                    "notional_per_unit": notional_min / min_stake, # £ notional per £/pt
                    "weight_pct": weight_pct
                }
                instruments.append(inst)

            except Exception:
                messagebox.showerror("Input Error", f"Incomplete/invalid data for {entries[0].get()}")
                self.output.config(state="disabled")
                return

        total_weight = sum(i["weight_pct"] for i in instruments)
        if total_weight <= 0:
            messagebox.showerror("Input Error", "Weights must sum to > 0.")
            self.output.config(state="disabled")
            return

        # ---- Helper: given scale k, compute stakes (rounded down), margins, notionals ----
        # We define target_notional_i = k * (weight_i / total_weight)
        # Then stake_i = floor(target_notional_i / notional_per_unit_i) to min_stake increments.
        def compute_for_scale(k: float):
            stakes = []
            margins = []
            notionals = []
            for inst in instruments:
                target_notional_i = k * (inst["weight_pct"] / total_weight)

                raw_stake = target_notional_i / inst["notional_per_unit"]
                stake = round_down_to_step(raw_stake, inst["min_stake"])

                # IMPORTANT: allow zero during search; we’ll handle min-stake feasibility afterward
                if stake < 0:
                    stake = 0.0

                stakes.append(stake)
                margins.append(stake * inst["margin_per_unit"])
                notionals.append(stake * inst["notional_per_unit"])
            return stakes, margins, notionals

        # ---- First: check feasibility of holding ALL 3 at minimum stake under the margin cap ----
        min_stakes = [inst["min_stake"] for inst in instruments]
        min_margins = [ms * inst["margin_per_unit"] for ms, inst in zip(min_stakes, instruments)]
        min_total_margin = sum(min_margins)

        if min_total_margin > target_total_margin:
            # Not feasible to hold all three legs at min size within cap
            self.output.insert(tk.END, "ERROR: Margin cap too low to hold all three instruments at minimum stake.\n\n")
            self.output.insert(tk.END, f"Target margin cap: {target_total_margin:.2f}\n")
            self.output.insert(tk.END, f"Minimum margin needed (0.01 each): {min_total_margin:.2f}\n\n")
            self.output.insert(tk.END, "Fix: increase Target Margin %, increase balance, or reduce required legs.\n")
            self.output.config(state="disabled")
            return

        # ---- Binary search k to maximize total notional while staying within margin cap ----
        # Start with k_hi by growing until we exceed margin cap.
        k_lo = 0.0
        k_hi = 1.0

        # ensure k_hi is high enough to exceed the cap
        for _ in range(60):
            stakes, margins, notionals = compute_for_scale(k_hi)

            # enforce minimum stakes (since we know it's feasible)
            stakes2 = []
            for stake, inst in zip(stakes, instruments):
                if stake < inst["min_stake"]:
                    stake = inst["min_stake"]
                stakes2.append(stake)
            margins2 = [s * inst["margin_per_unit"] for s, inst in zip(stakes2, instruments)]
            total_margin2 = sum(margins2)

            if total_margin2 >= target_total_margin:
                break
            k_hi *= 2.0

        # binary search between lo/hi
        best = None
        for _ in range(80):
            k_mid = (k_lo + k_hi) / 2.0
            stakes, margins, notionals = compute_for_scale(k_mid)

            # enforce minimum stakes
            stakes = [max(s, inst["min_stake"]) for s, inst in zip(stakes, instruments)]
            margins = [s * inst["margin_per_unit"] for s, inst in zip(stakes, instruments)]
            notionals = [s * inst["notional_per_unit"] for s, inst in zip(stakes, instruments)]

            total_margin = sum(margins)

            if total_margin <= target_total_margin:
                best = (k_mid, stakes, margins, notionals)
                k_lo = k_mid
            else:
                k_hi = k_mid

        if best is None:
            messagebox.showerror("Sizing Error", "Unable to size portfolio under margin cap (unexpected).")
            self.output.config(state="disabled")
            return

        _, stakes, margins, notionals = best
        total_margin = sum(margins)
        total_notional = sum(notionals)

        # achieved weights (by notional)
        achieved = []
        for inst, n in zip(instruments, notionals):
            achieved_w = (n / total_notional * 100.0) if total_notional > 0 else 0.0
            achieved.append(achieved_w)

        # ---- Output ----
        self.output.insert(
            tk.END,
            f"{'Instrument':20s} {'Stake (£/pt)':>15s} {'Notional £':>14s} {'Margin £':>12s} {'Wgt % tgt':>10s} {'Wgt % act':>10s}\n"
        )
        self.output.insert(tk.END, "-" * 92 + "\n")

        for i, inst in enumerate(instruments):
            self.output.insert(
                tk.END,
                f"{inst['name']:20s} {stakes[i]:15.4f} {notionals[i]:14.2f} {margins[i]:12.2f} "
                f"{inst['weight_pct']:10.2f} {achieved[i]:10.2f}\n"
            )

        self.output.insert(tk.END, "-" * 92 + "\n")
        self.output.insert(
            tk.END,
            f"{'TOTAL NOTIONAL:':<55s}{total_notional:12.2f}\n"
            f"{'TOTAL MARGIN USED:':<55s}{total_margin:12.2f}\n"
            f"{'TARGET MARGIN CAP:':<55s}{target_total_margin:12.2f}\n"
            f"{'ACTUAL % USED:':<55s}{(total_margin / balance) * 100:11.2f}%\n"
        )

        self.output.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioDepositAllocator(root)
    root.mainloop()
