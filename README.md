# Personalized Herbal Formula System

A clinical-grade algorithmic engine for generating personalized herbal formulas.

## Overview
This application helps practitioners or users generate safe, effective herbal formulas by analyzing:
- **Patient Profile**: Symptoms (Anxiety, Insomnia, etc.), conditions (Pregnancy, Gastritis), and medications.
- **Plant Data**: A database of plants with properties, safety constraints, synergies, and antagonisms.

## Features
- **Dynamic Scoring**: Prioritizes plants that match the user's top symptoms.
- **Safety Constraints**: Strictly enforces safety rules (e.g., excluding plants unsafe for pregnancy).
- **Synergy Optimization**: Boosts scores for plants that work well together.
- **Dosage Calculation**: Computes exact percentages and grams for the final blend.
- **Streamlit UI**: A modern, responsive interface.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the app using Streamlit:
```bash
streamlit run app.py
```

## Structure
- `app.py`: Main Streamlit application.
- `herbal_engine.py`: Core logic for scoring, constraints, and formulation.
- `plants_db.json`: Database of medicinal plants and their properties.
