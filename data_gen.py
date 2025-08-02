#!/usr/bin/env python3
"""
data_gen.py - Generate realistic SaaS business metrics data
"""

import numpy as np
import pandas as pd
import os

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists("data"):
        os.makedirs("data")

def generate_metrics(filename="data/metrics.csv"):
    """Generate top-level KPI metrics"""
    metrics = [
        ("Monthly Recurring Revenue", 3.2, 4.2, "$", "M"),
        ("CAC Payback Period", 14.2, -0.9, "", "mo"),
        ("Net Revenue Retention", 112, 4.5, "", "%"),
        ("Monthly Churn Rate", 4.2, -0.6, "", "%"),
        ("LTV:CAC Ratio", 4.8, 0.5, "", "x"),
    ]
    
    df = pd.DataFrame(metrics, columns=["metric", "value", "delta", "prefix", "suffix"])
    df.to_csv(filename, index=False)
    print(f"Generated metrics data: {filename}")

def generate_channel_acquisition(filename="data/channel_acquisition.csv"):
    """Generate customer acquisition data by channel over time"""
    dates = pd.date_range("2022-03-01", "2024-11-01", freq="MS")
    channels = [
        "Direct", "Referrals", "Email Marketing",
        "Content Marketing", "Social Media",
        "Paid Search", "Organic Search"
    ]
    
    np.random.seed(42)
    base = np.linspace(200, 800, len(dates))
    
    data = {"date": dates}
    
    for i, channel in enumerate(channels):
        # Add seasonal variation and growth trends
        noise = np.random.normal(scale=50, size=len(dates))
        seasonal = 50 * np.sin(np.linspace(0, 4*np.pi, len(dates)) + i)
        trend = base * (1 + 0.1 * np.sin(np.linspace(0, 3*np.pi, len(dates)) + i))
        
        # Different growth patterns for different channels
        if channel == "Organic Search":
            trend *= 1.3  # Stronger organic growth
        elif channel == "Paid Search":
            trend *= 1.1  # Moderate paid growth
        elif channel == "Social Media":
            trend *= 0.8  # Lower social conversion
            
        data[channel] = np.clip(trend + seasonal + noise, 50, None).astype(int)
    
    pd.DataFrame(data).to_csv(filename, index=False)
    print(f"Generated channel acquisition data: {filename}")

def generate_arr_movement(filename="data/arr_movement.csv"):
    """Generate ARR waterfall breakdown"""
    np.random.seed(123)
    
    starting_arr = 28_000_000
    new_business = np.random.uniform(1_500_000, 2_500_000)
    expansion = np.random.uniform(800_000, 1_500_000)
    contraction = -np.random.uniform(200_000, 600_000)
    churn = -np.random.uniform(100_000, 500_000)
    
    ending_arr = starting_arr + new_business + expansion + contraction + churn
    
    rows = [
        ("Starting ARR", "absolute", starting_arr),
        ("New Business", "relative", new_business),
        ("Expansion", "relative", expansion),
        ("Contraction", "relative", contraction),
        ("Churn", "relative", churn),
        ("Ending ARR", "total", ending_arr),
    ]
    
    pd.DataFrame(rows, columns=["category", "measure", "value"]).to_csv(filename, index=False)
    print(f"Generated ARR movement data: {filename}")

def generate_funnel_data(filename="data/funnel_data.csv"):
    """Generate conversion funnel data"""
    flows = [
        # Traffic sources to MQL
        ("Organic Search", "MQL", 5000),
        ("Paid Search", "MQL", 4000),
        ("Content Marketing", "MQL", 3000),
        ("Social Media", "MQL", 3500),
        ("Direct", "MQL", 4500),
        ("Email Marketing", "MQL", 3200),
        ("Referrals", "MQL", 2800),
        
        # MQL to SQL conversion
        ("MQL", "SQL", 6000),
        ("MQL", "Unqualified", 2500),
        
        # SQL to Opportunity
        ("SQL", "Opportunity", 1800),
        ("SQL", "No Opportunity", 2000),
        ("SQL", "Lost", 1500),
        ("SQL", "Won", 700),
    ]
    
    pd.DataFrame(flows, columns=["source", "target", "value"]).to_csv(filename, index=False)
    print(f"Generated funnel data: {filename}")

def generate_cohort_data(filename="data/cohort_data.csv", num_cohorts=12, months=12):
    """Generate cohort retention analysis data"""
    np.random.seed(456)
    
    # Create cohorts for the past 12 months
    cohorts = [f"2023-{m:02d}" for m in range(1, num_cohorts + 1)]
    
    data = []
    for cohort_idx, cohort in enumerate(cohorts):
        # Simulate realistic retention patterns
        # Higher initial retention, gradual decline with some stabilization
        base_retention = 100
        
        # Early months: moderate churn (2-6%)
        early_declines = np.random.uniform(2, 6, 6)
        # Later months: lower but consistent churn (1-4%)
        later_declines = np.random.uniform(1, 4, months - 6)
        
        declines = np.concatenate([early_declines, later_declines])
        
        # Calculate cumulative retention
        retention = base_retention - np.cumsum(declines)
        retention = np.clip(retention, 45, 100)  # Floor at 45%
        
        # Add some seasonal variation
        seasonal_adjustment = 2 * np.sin(np.linspace(0, 2*np.pi, months) + cohort_idx)
        retention += seasonal_adjustment
        retention = np.clip(retention, 45, 100)
        
        data.append(retention)
    
    df = pd.DataFrame(data, columns=[f"M{i}" for i in range(months)])
    df.insert(0, "cohort", cohorts)
    df.to_csv(filename, index=False)
    print(f"Generated cohort data: {filename}")

def generate_additional_metrics(filename="data/additional_metrics.csv"):
    """Generate additional business metrics for enhanced dashboard"""
    np.random.seed(789)
    
    # Monthly business metrics over time
    dates = pd.date_range("2022-01-01", "2024-11-01", freq="MS")
    
    data = {
        "date": dates,
        "active_customers": np.random.randint(8000, 12000, len(dates)),
        "trial_signups": np.random.randint(500, 800, len(dates)),
        "trial_conversion_rate": np.random.uniform(0.15, 0.25, len(dates)),
        "average_deal_size": np.random.uniform(15000, 25000, len(dates)),
        "sales_cycle_days": np.random.randint(45, 90, len(dates)),
    }
    
    pd.DataFrame(data).to_csv(filename, index=False)
    print(f"Generated additional metrics: {filename}")

def main():
    """Generate all data files"""
    print("Generating SaaS dashboard data...")
    
    ensure_data_directory()
    
    generate_metrics()
    generate_channel_acquisition()
    generate_arr_movement()
    generate_funnel_data()
    generate_cohort_data()
    generate_additional_metrics()
    
    print("\nAll data files generated successfully!")

if __name__ == "__main__":
    main()
