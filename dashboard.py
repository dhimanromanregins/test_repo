#!/usr/bin/env python3
"""
dashboard.py - Create interactive SaaS dashboard
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

def ensure_output_directory():
    """Create output directory if it doesn't exist"""
    if not os.path.exists("output"):
        os.makedirs("output")

def load_data():
    """Load all data files"""
    try:
        metrics = pd.read_csv("data/metrics.csv")
        channel = pd.read_csv("data/channel_acquisition.csv", parse_dates=["date"])
        arr = pd.read_csv("data/arr_movement.csv")
        funnel = pd.read_csv("data/funnel_data.csv")
        cohort = pd.read_csv("data/cohort_data.csv")
        additional = pd.read_csv("data/additional_metrics.csv", parse_dates=["date"])
        
        return metrics, channel, arr, funnel, cohort, additional
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        print("Please run data_gen.py first to generate the data files.")
        return None

def create_kpi_indicators(metrics):
    """Create KPI indicator cards"""
    indicator_figs = []
    
    for i, row in metrics.iterrows():
        prefix = "" if pd.isna(row["prefix"]) else row["prefix"]
        suffix = "" if pd.isna(row["suffix"]) else row["suffix"]
        
        # Determine delta color and symbol
        delta_color = "green" if row["delta"] > 0 else "red"
        delta_symbol = "↑" if row["delta"] > 0 else "↓"
        
        indicator_figs.append(
            go.Figure(go.Indicator(
                mode="number",
                title={
                    "text": f"<b>{str(row['metric']).upper()}</b>",
                    "font": {"size": 14, "color": "#2c3e50"}
                },
                value=row["value"],
                number={
                    "prefix": prefix,
                    "suffix": suffix,
                    "font": {"size": 32, "weight": "bold", "color": "#34495e"}
                }
            )).update_layout(
                height=120,
                margin=dict(t=30, b=20, l=10, r=10),
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
        )
    
    return indicator_figs

def create_channel_acquisition_chart(channel):
    """Create stacked area chart for channel acquisition"""
    # Prepare data for better visualization
    N = 2
    tick_dates = channel["date"][N:-N:3] if len(channel["date"]) > 2*N else channel["date"][::3]
    
    fig = go.Figure()
    
    # Color palette for channels
    colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#34495e', '#1abc9c']
    
    for i, ch in enumerate([c for c in channel.columns if c != "date"]):
        fig.add_trace(
            go.Scatter(
                x=channel["date"],
                y=channel[ch],
                name=ch,
                stackgroup="one",
                mode="lines",
                line=dict(width=0.5),
                fillcolor=colors[i % len(colors)],
                hovertemplate=f"<b>{ch}</b><br>Date: %{{x}}<br>Customers: %{{y:,}}<extra></extra>"
            )
        )
    
    fig.update_xaxes(
        tickmode="array",
        tickvals=tick_dates,
        ticktext=[d.strftime("%b %Y") for d in tick_dates],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.1)"
    )
    
    fig.update_yaxes(
        title_text="New Customers",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.1)"
    )
    
    fig.update_layout(
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.15,
            x=0.5,
            xanchor="center",
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=10, r=10, t=60, b=80),
        height=400,
        title=dict(
            text="<b>Channel Acquisition Trends</b>",
            x=0.02,
            xanchor="left",
            y=0.95,
            yanchor="top",
            font=dict(size=18, color="#2c3e50")
        ),
        hovermode="x unified"
    )
    
    return fig

def create_arr_waterfall(arr):
    """Create ARR waterfall chart"""
    # Format values for better display
    formatted_values = []
    for val in arr["value"]:
        if abs(val) >= 1_000_000:
            formatted_values.append(f"${val/1_000_000:.1f}M")
        else:
            formatted_values.append(f"${val/1_000:.0f}K")
    
    fig = go.Figure(go.Waterfall(
        x=arr["category"].tolist(),
        y=arr["value"].tolist(),
        measure=arr["measure"].tolist(),
        text=formatted_values,
        textposition="outside",
        connector={"line": {"color": "rgba(0, 0, 0, 0.15)", "width": 1}},
        increasing={"marker": {"color": "#27ae60"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#3498db"}},
        hovertemplate="<b>%{x}</b><br>Value: $%{y:,.0f}<extra></extra>"
    ))
    
    fig.update_xaxes(
        tickangle=-45,
        showgrid=True,
        gridcolor="rgba(0,0,0,0.1)"
    )
    
    fig.update_yaxes(
        tickformat="~s",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.1)"
    )
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=60, b=80),
        height=400,
        title=dict(
            text="<b>ARR Movement Analysis</b>",
            x=0.02,
            xanchor="left",
            y=0.95,
            yanchor="top",
            font=dict(size=18, color="#2c3e50")
        )
    )
    
    return fig

def create_funnel_sankey(funnel):
    """Create Sankey diagram for conversion funnel"""
    labels = list(pd.unique(funnel[["source", "target"]].values.ravel()))
    
    # Create source and target indices
    source_indices = funnel["source"].apply(lambda x: labels.index(x)).tolist()
    target_indices = funnel["target"].apply(lambda x: labels.index(x)).tolist()
    
    # Color scheme
    node_colors = ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#34495e', '#1abc9c'] * 3
    
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors[:len(labels)]
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=funnel["value"].tolist(),
            hovertemplate="<b>%{source.label}</b> → <b>%{target.label}</b><br>Volume: %{value:,}<extra></extra>"
        )
    ))
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=60, b=10),
        height=350,
        title=dict(
            text="<b>Customer Acquisition Funnel</b>",
            x=0.02,
            xanchor="left",
            y=0.95,
            yanchor="top",
            font=dict(size=18, color="#2c3e50")
        )
    )
    
    return fig

def create_cohort_heatmap(cohort):
    """Create cohort retention heatmap"""
    cohort_columns = cohort.columns[1:13]  # M0 to M11
    cohort_matrix = cohort.set_index("cohort")[cohort_columns].values
    
    # Create custom colorscale
    colorscale = [
        [0, '#fee0d2'],
        [0.25, '#fcae91'],
        [0.5, '#fb7050'],
        [0.75, '#de2d26'],
        [1, '#a50f15']
    ]
    
    fig = go.Figure(go.Heatmap(
        z=cohort_matrix,
        x=cohort_columns.tolist(),
        y=cohort["cohort"].tolist(),
        colorscale=colorscale,
        colorbar=dict(
            title="Retention %",
            tickmode="linear",
            tick0=40,
            dtick=10
        ),
        zmin=40,
        zmax=100,
        hovertemplate="<b>Cohort:</b> %{y}<br><b>Month:</b> %{x}<br><b>Retention:</b> %{z:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=60, b=10),
        height=350,
        xaxis=dict(
            side="top",
            ticks="outside",
            ticklen=6,
            tickcolor="#ecf0f7",
            tickangle=0,
            title=""
        ),
        yaxis=dict(
            title="",
            autorange="reversed"
        ),
        title=dict(
            text="<b>Cohort Retention Analysis</b>",
            x=0.02,
            xanchor="left",
            y=0.95,
            yanchor="top",
            font=dict(size=18, color="#2c3e50")
        )
    )
    
    return fig

def create_dashboard_html(metrics, channel, arr, funnel, cohort, output="output/dashboard.html"):
    """Create the complete dashboard HTML"""
    # Create all visualizations
    indicator_figs = create_kpi_indicators(metrics)
    area_fig = create_channel_acquisition_chart(channel)
    waterfall_fig = create_arr_waterfall(arr)
    sankey_fig = create_funnel_sankey(funnel)
    heatmap_fig = create_cohort_heatmap(cohort)
    
    # Custom CSS and HTML layout
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SaaS Business Dashboard</title>
        <meta charset="utf-8">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            
            .dashboard-container {{
                max-width: 1800px;
                margin: 0 auto;
            }}
            
            .dashboard-title {{
                text-align: center;
                color: #2c3e50;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 30px;
                text-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            
            .card {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.06);
                padding: 20px;
                margin: 8px;
                transition: all 0.3s ease;
                border: 1px solid #e9ecef;
            }}
            
            .card:hover {{
                box-shadow: 0 8px 25px rgba(0,0,0,0.15), 0 3px 10px rgba(0,0,0,0.10);
                transform: translateY(-2px);
            }}
            
            .kpi-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .kpi-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
                transform: translateX(-100%);
                transition: transform 0.5s;
            }}
            
            .kpi-card:hover::before {{
                transform: translateX(100%);
            }}
            
            .delta-indicator {{
                background: rgba(255,255,255,0.2);
                border-radius: 20px;
                padding: 8px 16px;
                margin-top: 10px;
                font-size: 14px;
                font-weight: bold;
                display: inline-block;
                backdrop-filter: blur(10px);
            }}
            
            .positive {{
                color: #27ae60;
            }}
            
            .negative {{
                color: #e74c3c;
            }}
            
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                grid-template-rows: 160px 420px 370px;
                gap: 16px;
                width: 100%;
            }}
            
            .chart-container {{
                position: relative;
                height: 100%;
            }}
            
            @media (max-width: 1200px) {{
                .dashboard-grid {{
                    grid-template-columns: repeat(3, 1fr);
                    grid-template-rows: auto;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <h1 class="dashboard-title">📊 SaaS Business Health Dashboard</h1>
            
            <div class="dashboard-grid">
                <!-- KPI Cards Row -->
                {generate_kpi_cards_html(metrics, indicator_figs)}
                
                <!-- Chart Row 1 -->
                <div class="card" style="grid-row: 2; grid-column: 1/4;">
                    <div class="chart-container">
                        {area_fig.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
                
                <div class="card" style="grid-row: 2; grid-column: 4/6;">
                    <div class="chart-container">
                        {waterfall_fig.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
                
                <!-- Chart Row 2 -->
                <div class="card" style="grid-row: 3; grid-column: 1/3;">
                    <div class="chart-container">
                        {sankey_fig.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
                
                <div class="card" style="grid-row: 3; grid-column: 3/6;">
                    <div class="chart-container">
                        {heatmap_fig.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output, "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    
    return dashboard_html

def generate_kpi_cards_html(metrics, indicator_figs):
    """Generate HTML for KPI cards"""
    cards_html = ""
    
    for i in range(len(metrics)):
        row = metrics.iloc[i]
        delta_class = "positive" if row["delta"] > 0 else "negative"
        delta_symbol = "↗" if row["delta"] > 0 else "↘"
        
        # Format delta value
        if pd.notna(row["suffix"]) and row["suffix"] == "M":
            delta_text = f"{delta_symbol} {row['delta']:.1f}%"
        else:
            prefix = row["prefix"] if pd.notna(row["prefix"]) else ""
            suffix = row["suffix"] if pd.notna(row["suffix"]) else ""
            delta_text = f"{delta_symbol} {prefix}{row['delta']}{suffix}"
        
        cards_html += f"""
        <div class="card kpi-card" style="grid-row: 1; grid-column: {i+1};">
            {indicator_figs[i].to_html(full_html=False, include_plotlyjs='cdn' if i == 0 else False)}
            <div class="delta-indicator">
                <span class="{delta_class}">{delta_text}</span>
            </div>
        </div>
        """
    
    return cards_html

def main():
    """Main function to create the dashboard"""
    print("Creating SaaS Business Dashboard...")
    
    # Load data
    data = load_data()
    if data is None:
        return
    
    metrics, channel, arr, funnel, cohort, additional = data
    
    # Ensure output directory exists
    ensure_output_directory()
    
    # Create dashboard
    dashboard_html = create_dashboard_html(metrics, channel, arr, funnel, cohort)
    
    print("Dashboard created successfully!")
    print("Open 'output/dashboard.html' in your web browser to view the dashboard.")

if __name__ == "__main__":
    main()