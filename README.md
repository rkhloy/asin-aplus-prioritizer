# Amazon ASIN Content Prioritization Tool

A Streamlit app that analyzes Amazon product listing data and applies a weighted scoring framework to prioritize A+ Content optimization opportunities.

## Overview


Amazon catalogs often contain too many listings to optimize all at once. This project helps identify which ASINs have the greatest potential for A+ Content improvement by evaluating listing quality, business value, and content gaps.

The tool uploads Amazon product data from a CSV or Excel file, validates and standardizes the inputs, applies a weighted scoring model totaling 100 points, and outputs a ranked list of ASINs with recommended optimization actions.

## Business Problem

Amazon brands and ecommerce teams often face a resource allocation problem:

- Large catalogs create too many possible optimization targets
- Not every product should receive A+ Content investment first
- Missing A+ Content alone does not indicate priority
- Teams need a more consistent way to decide which listings deserve attention first

This tool reframes A+ optimization as a prioritization problem rather than a manual listing review process.

## Solution

The app evaluates product listing data and uses a weighted scoring framework to rank ASINs by improvement opportunity.

It is designed to:

- Upload and read ASIN listing data
- Validate and standardize key input fields
- Apply a weighted scoring framework totaling 100 points
- Identify which listing elements need optimization
- Rank ASINs by priority
- Export action-ready results to CSV

## Framework

The scoring model is based on three layers:

1. **Listing Quality Audit**  
   Measures current content strength using fields such as A+ status, image count, bullet count, description length, review count, and rating.

2. **Business Priority Score**  
   Estimates the likely business value of improving a listing using weighted criteria.

3. **Scope Recommendation**  
   Converts the analysis into an action category such as Must Do, Should Do, Could Do, or Defer.

## Example Weighted Criteria

The priority model uses weighted scoring across factors such as:

- Missing A+ Content
- Reach Potential
- Value / Margin Proxy
- Customer Validation
- Image Weakness
- Bullet Weakness
- Description Weakness

The total priority score is capped at 100.

## Core Features

- CSV and Excel upload
- Column mapping for flexible input files
- Input validation and type cleaning
- Weighted scoring for A+ optimization potential
- Priority labeling and action recommendations
- Sorted results table
- CSV export

## Planned Output Columns

The app is designed to output a ranked file including fields such as:

- ASIN
- Product Title
- Listing Quality Score
- Priority Score
- Scope Bucket
- Recommended Action
- Optimization Needed
- Review Count
- Image Count
- Price

## Tech Stack

- Python
- Streamlit
- Pandas
- OpenPyXL

## Project Structure

```text
asin-aplus-prioritizer/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── data/
└── screenshots/