# Entity Linkage Project

A Python solution for mapping entities between disparate datasets using probabilistic record linkage. This project was developed to solve the common problem of identifying matching entities across different data sources where unique keys are not available.

## Overview

The project implements an automated entity linkage system that maps companies from procurement data (`a__company.csv`) to corresponding entities in finance data (`b__company.csv`). It uses the Splink probabilistic record linkage library to achieve high-precision matching based on multiple attributes including company names, addresses, and contact information.

## Requirements

### Python Dependencies

```bash
pip install requirements.txt
```

### Expected Output
- `linked_entities.csv`: Three-column file containing:
  - `vendor_id`: ID from procurement data
  - `entity_id`: Corresponding ID from finance data (or NA if no match)
  - `confidence_of_match`: Probability score (0-1) indicating match confidence

## Usage

### Basic Usage

1. **Place your data files** in a `data/` directory in the project root
2. **Run the main script**:
   ```bash
   python entity_linkage.py
   ```
3. **Check results** in the generated `linked_entities.csv` file

### Step-by-Step Process

The linkage process follows these steps:

1. **Data Loading**: Reads all CSV files from the data directory
2. **Data Cleaning**: Standardizes and cleans both datasets
3. **Model Fitting**: Trains the probabilistic linkage model
4. **Prediction**: Generates match predictions with confidence scores
5. **Post-processing**: Selects best matches and handles unmatched records


## Features

### Data Cleaning (`cleaning_fx.py`)

- **Abbreviation Removal**: Removes common business and address abbreviations
- **Address Parsing**: Splits addresses into number and street components
- **Duplicate Removal**: Keeps records with the least missing data
- **Special Character Handling**: Removes punctuation and standardizes text

### Linkage Model (`linkage_model.py`)

- **Blocking Strategy**: Uses multiple blocking rules to reduce comparison space
- **Similarity Measures**: 
  - Jaro-Winkler for company names and addresses 
  - Damerau-Levenshtein for numeric fields
  - Exact matching for iso (country) data
- **Probabilistic Framework**: Uses expectation-maximization for parameter estimation

### Blocking Rules (in order of specificity)

1. **Highly Specific**: zipcode + area_code, state + city + area_code
2. **Moderately Specific**: state + area_code, city + area_code
3. **General**: area_code, partial zipcode, partial name matches


### Future Additions?

1. Detect unit (apt, ste) numbers in addresses
2. Downweight city/state matches - currently, it gave too many false positives 
3. Clean website urls better 

---

For questions or issues, please review the source code comments for additional implementation details.