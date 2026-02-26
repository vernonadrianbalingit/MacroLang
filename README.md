# MacroLang 🥗

A domain-specific programming language and interpreter for nutrition tracking and macro calculation, written in Python.

MacroLang lets you declare foods, set fitness goals, and run arithmetic — all in a clean, readable syntax purpose-built for the nutrition domain. The interpreter parses `.macro` files, evaluates expressions, and generates a full report with personalized daily intake recommendations and visual progress bars.

---

## Features

- **Custom language syntax** — declare foods, goals, and calculations in plain, readable `.macro` files
- **Full grammar specification** — formal grammar defined in `MacroLang.tx` using textX
- **Arithmetic engine** — supports `+`, `-`, `*`, `/` with variable references across expressions
- **BMR & TDEE calculation** — computes Basal Metabolic Rate and Total Daily Energy Expenditure using the Mifflin-St Jeor equation, adjusted for activity level and objective
- **Personalized macro targets** — generates recommended protein/carbs/fats based on `cut`, `bulk`, or `maintain` goals
- **Visual comparison report** — ASCII progress bars comparing actual intake vs. targets
- **Browser playground** — run MacroLang programs directly in `index.html` without any local setup

---

## Language Syntax

MacroLang has three statement types: `food`, `goal`, and `calculate`.

### Declare a food

```
food chicken_breast:
    protein 30
    carbs 0
    fats 3
```

### Set a fitness goal

```
goal:
    height 175
    weight 80
    activity moderate
    objective bulk
```

**Activity levels:** `sedentary` | `moderate` | `active`  
**Objectives:** `maintain` | `cut` | `bulk`

### Arithmetic with variables

Variables can be declared and reused across food declarations:

```
calculate protein_per_serving = 20
calculate double_protein = protein_per_serving * 2

food eggs:
    protein double_protein
    carbs 1
    fats 5
```

Supported operators: `+` `-` `*` `/`

### Comments

```
// This is a comment
```

---

## Example Program

```
calculate protein_per_serving = 20
calculate carbs_per_serving = 25

food oatmeal:
    protein 5
    carbs carbs_per_serving
    fats 3

food chicken_breast:
    protein protein_per_serving
    carbs 0
    fats 3

goal:
    height 175
    weight 80
    activity moderate
    objective bulk
```

---

## Running the Interpreter

**Requirements:** Python 3.x (no external dependencies)

```bash
python interpreter.py your_file.macro
```

**Example output:**

```
===== MacroLang Report =====

Total Macros:
  Protein: 45g
  Carbs: 55g
  Fats: 11g
  Calories: 497 kcal

Recommended Daily Intake:
  BMR: 1856 kcal
  Maintenance: 2877 kcal
  Target Calories: 3308 kcal
  Protein: 331g
  Carbs: 413g
  Fats: 73g

Comparison to Recommendations:
  Calories: [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 15.0% (too low)
  Protein:  [██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 13.6% (too low)
  Carbs:    [█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 13.3% (too low)
  Fats:     [███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 15.1% (too low)
```

---

## Example Programs Included

| File | Description |
|------|-------------|
| `basic_tracking.macro` | Simple single-meal macro tracking |
| `meal_planning.macro` | Full day of meals with variable-driven portions |
| `arithmetic.macro` | Arithmetic expression showcase |
| `variable_usage.macro` | Variable declaration and reference patterns |
| `fizzbuzz.macro` | Classic FizzBuzz implemented in MacroLang |
| `bulk.macro` | Example bulk goal configuration |
| `hello_macros.macro` | Minimal hello-world equivalent |

---

## Architecture

```
MacroLang/
├── interpreter.py        # Parser + interpreter + report generator
├── MacroLang.tx          # Formal grammar specification (textX)
├── index.html            # Browser-based playground
├── *.macro               # Example programs
└── README.md
```

**interpreter.py** is structured in two classes:

- `MacroLangParser` — single-pass line-by-line parser; builds an AST-equivalent internal representation of food declarations, goal blocks, and arithmetic statements
- `MacroLangInterpreter` — walks the parsed output, evaluates macro totals, computes BMR/TDEE recommendations, and generates the comparison report

**MacroLang.tx** defines the formal grammar using [textX](https://textx.github.io/textX/), a Python meta-language framework for building DSLs.

---

## Macro Calculation Logic

**BMR** is calculated using the Mifflin-St Jeor equation:

```
BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
```

**TDEE** applies an activity multiplier:

| Activity | Multiplier |
|----------|------------|
| `sedentary` | 1.2× |
| `moderate` | 1.55× |
| `active` | 1.725× |

**Calorie targets** are adjusted by objective:

| Objective | Adjustment | Macro Split (P/C/F) |
|-----------|------------|----------------------|
| `maintain` | 1.0× | 30 / 40 / 30 |
| `cut` | 0.8× (20% deficit) | 40 / 40 / 20 |
| `bulk` | 1.15× (15% surplus) | 40 / 50 / 10 |

---

## Calorie Constants

```
Protein:  4 kcal/g
Carbs:    4 kcal/g
Fats:     9 kcal/g
```

---

## Motivation

MacroLang was built as a project to learn language design from the ground up — writing a grammar spec, building a parser, and designing an interpreter — while solving a real problem (nutrition tracking) in a domain I work in daily through [MacroBud](https://github.com/vernonadrianbalingit).

---

## License

All rights reserved. This repository is publicly viewable for portfolio purposes. No part of this code may be used, copied, modified, or distributed without explicit written permission from the author.
