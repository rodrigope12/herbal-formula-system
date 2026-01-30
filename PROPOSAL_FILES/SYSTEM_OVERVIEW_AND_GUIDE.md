# Personalized Herbal Formula System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg) ![Status](https://img.shields.io/badge/status-Production-green.svg)

A professional-grade algorithmic engine designed to generate personalized liquid herbal formulas. This system mimics the clinical decision-making of an expert herbalist by applying rigorous biological constraints, safety filters, and synergistic blending rules.

## Key Features

- **Clinical Precision**: Implements complex "Transversal Adjustments" to limit botanical family redundancy (e.g., limiting *Lamiaceae* overload).
- **Safety First**: Automatic exclusion of contraindications for pregnancy, medication interactions, and specific health conditions.
- **Smart Balancing**: Ensures formulas are not over-stimulating or over-sedating by enforcing strict composition rules.
- **Dynamic Dosing**: Calculates precise gram-based dosages for a standard 30-day course.

## Project Structure

| File/Directory | Description |
| :--- | :--- |
| `app.py` | The Streamlit-based Admin Interface for Formula Generation. |
| `herbal_engine.py` | The core Python class containing the scoring and filtering algorithms. |
| `plants_db.json` | The JSON knowledge base of ~40 medicinal plants, scores, and attributes. |
| `docs/Architecture.md` | Detailed technical documentation of the algorithm's pipeline. |

## Quick Start

### Prerequisites
- Python 3.8 or higher.

### Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

3.  **Access**:
    Open your browser to `http://localhost:8501`.

## Usage Guide

1.  **Input Profile**: Enter the user's health priorities (e.g., "Sleep", "Anxiety") and safety flags (e.g., "Pregnancy").
2.  **Generate**: The system processes the profile through the 4-stage pipeline.
3.  **Review**: Inspect the selected plants, their assigned roles (Primary, Secondary, Support), and dosage.
4.  **Export**: Download the formula instructions as a CSV file for production.

---
**Developed with precision by Rodrigo Perez Cordero**  
*Physics Student | Python Developer | Logistics Optimization Specialist*
