#!/usr/bin/env python3
"""
nepal_tax_2083_84.py
=====================
Single-file Nepal personal income tax calculator for FY 2083/84
(Finance Act 2083, in force from Shrawan 1, 2083 BS / mid-July 2026).

DISCLAIMER: Educational estimate only, not tax advice. Slabs and rules
can be amended by IRD circulars. Verify at https://ird.gov.np or with
a chartered accountant before filing.

Tax slabs (unified for all individuals, married or not):
    Up to        10,00,000  -> 1%  (Social Security Tax / SST)
    10,00,001 -  15,00,000 -> 10%
    15,00,001 -  25,00,000 -> 20%
    25,00,001 -  40,00,000 -> 27%
    Above        40,00,000 -> 29%

The 1% SST is waived (0%) for: sole-proprietorship business income,
pension/retirement income, and salaried people contributing to the
Social Security Fund (SSF).

Usage (CLI):
    python nepal_tax_2083_84.py --income 1200000
    python nepal_tax_2083_84.py --income 1800000 --ssf --life-insurance 30000
    python nepal_tax_2083_84.py --help

Usage (as a library):
    from nepal_tax_2083_84 import calculate_tax
    result = calculate_tax(gross_income=1_200_000, ssf_contributor=True)
    print(result["total_tax"])
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# Constants (FY 2083/84)
# ---------------------------------------------------------------------------

TAX_SLABS = [
    (1_000_000, 0.01),
    (1_500_000, 0.10),
    (2_500_000, 0.20),
    (4_000_000, 0.27),
    (float("inf"), 0.29),
]

FIRST_SLAB_THRESHOLD = 1_000_000
RETIREMENT_CONTRIBUTION_CAP = 500_000  # SSF/EPF/CIT combined, also capped at 1/3 of income
LIFE_INSURANCE_CAP = 40_000
HEALTH_INSURANCE_CAP = 20_000
MEDICAL_CREDIT_CAP = 1_500
MEDICAL_CREDIT_RATE = 0.15
FEMALE_REBATE_RATE = 0.10  # verify current applicability with IRD


def calculate_tax(
    gross_income: float,
    income_type: str = "salaried",          # "salaried" | "business" | "pension"
    ssf_contributor: bool = False,
    retirement_contribution: float = 0.0,
    life_insurance_premium: float = 0.0,
    health_insurance_premium: float = 0.0,
    incapacitated: bool = False,
    medical_expenses: float = 0.0,
    female_single_income: bool = False,
) -> dict:
    """Calculate FY 2083/84 Nepal personal income tax. Returns a breakdown dict."""

    if gross_income < 0:
        raise ValueError("gross_income cannot be negative")
    if income_type not in ("salaried", "business", "pension"):
        raise ValueError('income_type must be "salaried", "business" or "pension"')

    # --- Deductions ---
    retirement_cap = min(RETIREMENT_CONTRIBUTION_CAP, gross_income / 3 if gross_income else 0)
    retirement_deduction = min(retirement_contribution, retirement_cap)
    life_deduction = min(life_insurance_premium, LIFE_INSURANCE_CAP)
    health_deduction = min(health_insurance_premium, HEALTH_INSURANCE_CAP)
    incapacitated_deduction = 0.5 * FIRST_SLAB_THRESHOLD if incapacitated else 0.0

    total_deductions = (
        retirement_deduction + life_deduction + health_deduction + incapacitated_deduction
    )
    taxable_income = max(0.0, gross_income - total_deductions)

    # --- Slab-wise tax (waive 1% SST where applicable) ---
    exempt_first_slab = income_type in ("business", "pension") or ssf_contributor
    slabs = list(TAX_SLABS)
    if exempt_first_slab:
        slabs[0] = (slabs[0][0], 0.0)

    breakdown = []
    lower = 0.0
    remaining = taxable_income
    for upper, rate in slabs:
        if remaining <= 0:
            break
        amount_in_band = min(remaining, upper - lower)
        if amount_in_band > 0:
            tax = amount_in_band * rate
            breakdown.append(
                {"lower": lower, "upper": upper, "rate": rate, "amount": amount_in_band, "tax": tax}
            )
            remaining -= amount_in_band
        lower = upper
    tax_before_rebate = sum(b["tax"] for b in breakdown)

    # --- Medical tax credit ---
    medical_credit = min(MEDICAL_CREDIT_CAP, MEDICAL_CREDIT_RATE * medical_expenses)
    medical_credit = min(medical_credit, tax_before_rebate)
    tax_after_medical = tax_before_rebate - medical_credit

    # --- Female employee rebate (10%, only-employment-income) ---
    female_rebate = FEMALE_REBATE_RATE * tax_after_medical if female_single_income else 0.0

    total_tax = round(tax_after_medical - female_rebate, 2)

    return {
        "gross_income": gross_income,
        "total_deductions": round(total_deductions, 2),
        "taxable_income": round(taxable_income, 2),
        "slab_breakdown": breakdown,
        "tax_before_rebate": round(tax_before_rebate, 2),
        "medical_tax_credit": round(medical_credit, 2),
        "female_rebate": round(female_rebate, 2),
        "total_tax": total_tax,
        "effective_rate_percent": round(total_tax / gross_income * 100, 2) if gross_income else 0.0,
        "net_income": round(gross_income - total_tax, 2),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _fmt(amount: float) -> str:
    return f"Rs {amount:,.2f}"


def main():
    parser = argparse.ArgumentParser(
        description="Estimate Nepal personal income tax for FY 2083/84 (Finance Act 2083)."
    )
    parser.add_argument("--income", type=float, required=True, help="Gross annual income (NPR)")
    parser.add_argument("--income-type", choices=["salaried", "business", "pension"], default="salaried")
    parser.add_argument("--ssf", action="store_true", help="Contributes to Social Security Fund (waives 1%% SST)")
    parser.add_argument("--retirement-contribution", type=float, default=0.0, help="SSF/EPF/CIT contribution (NPR)")
    parser.add_argument("--life-insurance", type=float, default=0.0, help="Life insurance premium paid (NPR)")
    parser.add_argument("--health-insurance", type=float, default=0.0, help="Health insurance premium paid (NPR)")
    parser.add_argument("--incapacitated", action="store_true", help="Qualifies as incapacitated natural person")
    parser.add_argument("--medical-expenses", type=float, default=0.0, help="Approved medical expenses (NPR)")
    parser.add_argument("--female-single-income", action="store_true", help="Female employee, employment income only (10%% rebate)")
    args = parser.parse_args()

    try:
        result = calculate_tax(
            gross_income=args.income,
            income_type=args.income_type,
            ssf_contributor=args.ssf,
            retirement_contribution=args.retirement_contribution,
            life_insurance_premium=args.life_insurance,
            health_insurance_premium=args.health_insurance,
            incapacitated=args.incapacitated,
            medical_expenses=args.medical_expenses,
            female_single_income=args.female_single_income,
        )
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 1

    print("=" * 56)
    print("  Nepal Income Tax Estimate - FY 2083/84 (2026/27)")
    print("=" * 56)
    print(f"Income type:          {args.income_type}")
    print(f"Gross income:         {_fmt(result['gross_income'])}")
    print(f"Total deductions:     {_fmt(result['total_deductions'])}")
    print(f"Taxable income:       {_fmt(result['taxable_income'])}")
    print("-" * 56)
    print("Slab-wise breakdown:")
    for b in result["slab_breakdown"]:
        upper_display = "and above" if b["upper"] == float("inf") else _fmt(b["upper"])
        print(
            f"  {_fmt(b['lower']):>15} - {upper_display:<15} @ {b['rate']*100:5.1f}% "
            f"on {_fmt(b['amount']):>15} = {_fmt(b['tax'])}"
        )
    print("-" * 56)
    print(f"Tax before rebate:    {_fmt(result['tax_before_rebate'])}")
    print(f"Medical tax credit:   -{_fmt(result['medical_tax_credit'])}")
    if result["female_rebate"]:
        print(f"Female rebate (10%):  -{_fmt(result['female_rebate'])}")
    print(f"TOTAL TAX PAYABLE:    {_fmt(result['total_tax'])}")
    print(f"Effective tax rate:   {result['effective_rate_percent']}%")
    print(f"Net income after tax: {_fmt(result['net_income'])}")
    print("=" * 56)
    print("Note: Estimate only (Finance Act 2083, FY 2083/84). Verify with ird.gov.np before filing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
