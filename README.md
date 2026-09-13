# Nepal Income Tax Calculator — FY 2083/84 (Single File)

A single, dependency-free Python script that estimates Nepal
**personal income tax** for **Fiscal Year 2083/84** (Shrawan 2083 –
Ashadh 2084 BS, mid-July 2026 – mid-July 2027 AD), per **Finance Act
2083**, amending the Income Tax Act, 2058.

> ⚠️ **Disclaimer**: Educational estimate only, not tax advice. Nepal's
> tax rules can be revised by later IRD circulars. Verify current
> figures at [ird.gov.np](https://ird.gov.np) or with a chartered
> accountant before filing.

## File

```
calculate_tax.py   # everything — slabs, deductions, CLI, and library functions
```

No external packages required — only the Python standard library
(`argparse`, `sys`). Works with Python 3.7+.

## Tax slabs (FY 2083/84)

One unified table now applies to every resident individual, regardless
of marital status (the old single/couple split from FY 2082/83 was
removed):

| Taxable income (NPR) | Rate |
|---|---|
| 0 – 10,00,000 | 1% (Social Security Tax) |
| 10,00,001 – 15,00,000 | 10% |
| 15,00,001 – 25,00,000 | 20% |
| 25,00,001 – 40,00,000 | 27% |
| Above 40,00,000 | 29% |

Tax is applied **progressively** — each rate only applies to the slice
of income that falls within that band.

### The 1% slab isn't always "1%"

The first slab is a Social Security Tax (SST). It's waived (0%) for:
- Sole-proprietorship business income
- Pension / retirement fund income
- Salaried individuals contributing to a Social Security Fund (SSF)

## Deductions & credits supported

| Item | Rule |
|---|---|
| SSF / EPF / Citizen Investment Trust contribution | Deductible up to the lower of NPR 5,00,000 or 1/3 of gross income |
| Life insurance premium | Deductible up to NPR 40,000 |
| Health/medical insurance premium | Deductible up to NPR 20,000 |
| Incapacitated natural person | Extra deduction = 50% of the first slab threshold (NPR 5,00,000) |
| Medical tax credit | Lower of NPR 1,500 or 15% of approved medical expenses (applied *after* tax is computed) |
| Female employee rebate | 10% rebate on computed tax for female employees whose only income is employment income — **verify current applicability with IRD** |

## Usage

### Command line

```bash
python calculate_tax.py --income 1200000
```

```bash
python calculate_tax.py --income 1800000 --ssf \
  --life-insurance 30000 --health-insurance 15000 \
  --medical-expenses 10000 --female-single-income
```

All options:

```
--income FLOAT                 Gross annual income in NPR (required)
--income-type {salaried,business,pension}   (default: salaried)
--ssf                           Contribute to a Social Security Fund (waives 1% slab)
--retirement-contribution N     SSF/EPF/CIT contribution amount (NPR)
--life-insurance N              Life insurance premium paid (NPR)
--health-insurance N            Health insurance premium paid (NPR)
--incapacitated                 Qualify as incapacitated natural person
--medical-expenses N            Approved medical expenses (NPR)
--female-single-income          Female employee, employment income only (10% rebate)
```

Sample output:

```
========================================================
  Nepal Income Tax Estimate - FY 2083/84 (2026/27)
========================================================
Income type:          salaried
Gross income:         Rs 1,800,000.00
Total deductions:     Rs 30,000.00
Taxable income:       Rs 1,770,000.00
--------------------------------------------------------
Slab-wise breakdown:
          Rs 0.00 - Rs 1,000,000.00 @   0.0% on Rs 1,000,000.00 = Rs 0.00
  Rs 1,000,000.00 - Rs 1,500,000.00 @  10.0% on   Rs 500,000.00 = Rs 50,000.00
  Rs 1,500,000.00 - Rs 2,500,000.00 @  20.0% on   Rs 270,000.00 = Rs 54,000.00
--------------------------------------------------------
Tax before rebate:    Rs 104,000.00
Medical tax credit:   -Rs 0.00
Female rebate (10%):  -Rs 10,400.00
TOTAL TAX PAYABLE:    Rs 93,600.00
Effective tax rate:   5.2%
Net income after tax: Rs 1,706,400.00
========================================================
```

### As a Python library

```python
from calculate_tax import calculate_tax

result = calculate_tax(
    gross_income=1_800_000,
    ssf_contributor=True,
    life_insurance_premium=30_000,
)

print(result["taxable_income"])
print(result["total_tax"])
print(result["effective_rate_percent"])

for band in result["slab_breakdown"]:
    print(band["lower"], band["upper"], band["rate"], band["tax"])
```

`calculate_tax()` returns a plain `dict` with these keys:

| Key | Meaning |
|---|---|
| `gross_income` | Input income, echoed back |
| `total_deductions` | Sum of all applied deductions |
| `taxable_income` | Income after deductions |
| `slab_breakdown` | List of dicts, one per slab band actually used |
| `tax_before_rebate` | Tax after slabs, before medical/female adjustments |
| `medical_tax_credit` | Medical credit applied |
| `female_rebate` | 10% female rebate applied (0 if not applicable) |
| `total_tax` | Final tax payable |
| `effective_rate_percent` | `total_tax / gross_income * 100` |
| `net_income` | `gross_income - total_tax` |

## Quick self-test

```bash
python -c "
from calculate_tax import calculate_tax
r = calculate_tax(gross_income=5_000_000)
assert r['total_tax'] == 955000.0
print('OK:', r['total_tax'])
"
```

## Extending

- Add corporate tax rates (flat 25% for most companies, 30% for banks/financial institutions).
- Add a presumptive flat-rate option for freelancers/small traders.
- Wrap it in a tiny Flask/Streamlit app for a web form instead of CLI flags.
- Split into a package (models, CLI, tests) if the project grows — see the multi-file version of this calculator for that structure.

## License

MIT — free to use, modify, and share.