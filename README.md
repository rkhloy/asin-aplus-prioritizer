# ASIN A+ Prioritizer

A Streamlit-based listing quality and prioritization tool for eCommerce and marketplace teams. The app analyzes product listing data from CSV or Excel files, evaluates listing quality signals, assigns an optimization score, and helps teams identify which ASINs should be reviewed first.

## Business Problem

Commerce teams often manage product data across Amazon, Shopify, ERP systems, marketplaces, and spreadsheets. Manual review is slow, inconsistent, and difficult to scale. As a result, weak listings can remain live with incomplete content, missing images, pricing errors, and cross-channel inconsistencies.

This project was built to turn listing data into a structured prioritization workflow by identifying weak listings, surfacing failure reasons, and generating action-oriented optimization recommendations.

## Target Users

- eCommerce Managers
- Marketplace Specialists
- Catalog Analysts
- Merchandising Teams
- Product Content Specialists
- Digital Operations Analysts

## What Decision This Tool Improves

The app helps teams answer three practical questions:

1. Which listings need optimization first?
2. What issues are causing poor listing quality?
3. Where should limited content and merchandising resources be focused?

## Current Version

The current version supports:

- CSV and Excel upload
- Sidebar-based column mapping
- Weighted listing quality scoring
- Priority classification
- Failure reasons and optimization tips
- Dashboard charts
- Exportable results for internal review

## V2 Enhancements

V2 expands the app into a more robust catalog governance and listing quality tool with the following improvements:

### Expanded Data Fields
- SKU
- Brand
- Category
- Bullet1-Bullet4
- Feature1-Feature4
- Image1-Image5 completeness
- Default price and sale price
- Meta title
- Channel / source

### Smarter Validation
- Required vs optional field mapping
- Image slot validation
- Feature and bullet completeness
- Pricing integrity checks
- Meta/title consistency analysis
- Failure reason tracking
- Optimization tips by issue type

### Upgraded Scoring Model
A weighted 100-point framework covering:

- Content completeness
- Image readiness
- Pricing integrity
- Search and merchandising quality
- Reviews / social proof
- Channel/source governance readiness

### Dashboard Visuals
- Priority distribution
- Top failure reasons
- Score bands

### Stronger Outputs
- Optimization score
- Priority
- Score band
- Completeness %
- Failure reasons
- Optimization tips
- Image completeness %
- Feature completeness %
- Pricing issue flag
- Title/meta consistency flag
- Channel/source flag
- Smart A+ readiness

## Example Input Fields

- ASIN
- SKU
- Title
- Brand
- Category
- Description
- Bullet1-Bullet4
- Feature1-Feature4
- Image1-Image5
- Default Price
- Sale Price
- Meta Title
- Reviews
- Channel / Source

## Example Output Fields

- Optimization Score
- Priority
- Score Band
- Completeness %
- Issue Count
- Failure Reasons
- Optimization Tips
- Image Completeness %
- Missing Image Count
- Feature Completeness %
- Bullet Completeness %
- Pricing Issue Flag
- Discount %
- Title/Meta Consistency Flag
- Channel Mismatch Flag
- Smart A+ Readiness

## Example Use Cases

- Prioritize Amazon listings for content improvement
- Identify weak product detail pages at scale
- Spot missing images and incomplete product attributes
- Flag pricing logic issues before updates go live
- Prepare internal review files for catalog and merchandising teams
- Support cross-channel governance planning

## Tech Stack

- Python
- Streamlit
- Pandas
- openpyxl

## Project Structure


asin-aplus-prioritizer/
├── archive/
│   ├── app_v1.py
│   └── README_v1.md
├── data/
│   ├── sample_input/
│   ├── sample_output/
│   └── archive/
├── screenshots/
│   ├── current/
│   └── archive/
├── .gitattributes
├── app.py
├── README.md
└── requirements.txt

## Run Locally
Clone the repository
git clone https://github.com/rkhloy/asin-aplus-prioritizer.git
cd asin-aplus-prioritizer

## Install dependencies
pip install -r requirements.txt

## Start the app
streamlit run app.py

## Screenshots

### Upload and Column Mapping
![Upload and Mapping](screenshots/current/upload_mapping_v2.jpg)

### Results Table
![Results Table](screenshots/current/output_results_v2.jpg)

### Dashboard Charts
![Dashboard Charts](screenshots/current/output_summary_v2.jpg)

## Sample Files
Use the sample input file in the data/sample_input/ folder to test uploads and scoring behavior.
Save a sample exported results file in data/sample_output/ for demonstration.

## Roadmap
Near-Term
Add stronger multi-channel comparison logic
Improve title/meta similarity scoring
Add category-aware scoring rules
Expand issue categorization
Add cleaner sample files and screenshots

## Future
Multi-file channel comparison
Seller and buy box analysis
Review quality logic
Custom scoring weights by marketplace
AI-assisted optimization suggestions
Why This Project Matters

This project demonstrates how product data quality, marketplace operations, and prioritization logic can be turned into a practical internal decision-support tool for digital commerce teams.
```text