# E-Commerce Business Intelligence Dashboard

## Project Overview

The **E-Commerce Business Intelligence Dashboard** is an interactive data analytics application designed to help management understand e-commerce sales and profitability performance.

The dashboard focuses on five business intelligence areas:

- **KPIs** — What is happening?
- **Trends** — Where are we heading?
- **Drivers** — Why is performance changing?
- **Risks & Opportunities** — What requires attention or offers potential?
- **Management Actions** — What actions can be considered?

## Business Objective

The objective of this project is to provide management with an interactive dashboard for monitoring sales, profit, orders, product performance, customer segments, regional performance, trends, and other important business indicators.

## Dataset

**Dataset:** Global E-Commerce Sales & Customer Data

**Source:** Kaggle

**Dataset URL:**  
https://www.kaggle.com/datasets/muhammadaammartufail/global-ecommerce-sales-and-customer-data

**Period:** January 2023 – December 2025

**Records:** 2,000

**Fields:** 15

### Main Dataset Fields

- Order ID
- Order Date
- Customer Name
- Customer Segment
- Country
- Region
- Product Category
- Product Name
- Quantity
- Unit Price
- Discount Percent
- Total Sales
- Shipping Cost
- Profit
- Payment Method

## Key Performance Indicators

The dashboard provides the following KPIs:

- Total Sales
- Total Profit
- Total Orders
- Total Quantity Sold
- Average Order Value
- Profit Margin

### Overall Results

| KPI | Result |
|---|---:|
| Total Sales | $484,559.34 |
| Total Profit | $158,872.32 |
| Total Orders | 2,000 |
| Total Quantity Sold | 7,115 |
| Average Order Value | $242.28 |
| Profit Margin | 32.8% |

## Dashboard Analysis

### 1. Trends

The dashboard analyzes:

- Monthly Sales
- Monthly Profit
- Order Volume
- Profit Margin

This helps identify changes in business performance over time.

### 2. Performance Drivers

The dashboard analyzes performance by:

- Region
- Country
- Product Category
- Product
- Customer Segment
- Payment Method

### 3. Risks and Opportunities

The dashboard evaluates:

- Discount levels
- Profitability
- Shipping costs
- Low-margin products
- Sales versus profit margin
- Category performance

### 4. Management Actions

The dashboard provides management-oriented observations covering areas such as:

- Regional growth
- Discount governance
- Logistics costs
- Product/category profitability
- Customer segment performance
- Protection of high-performing products

## Technology Stack

- **Python 3.14**
- **Streamlit 1.64**
- **Pandas 3.0**
- **Plotly 7.1**

## Project Structure

```text
E-Commerce-Business-Intelligence-Dashboard/
│
├── app.py
├── requirements.txt
├── README.md
├── E-Commerce_BI_Report.docx
│
└── data/
    └── global_ecommerce_sales.csv
