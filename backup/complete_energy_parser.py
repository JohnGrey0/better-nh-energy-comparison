import re
import pandas as pd
from datetime import datetime

def parse_all_energy_data():
    """
    Parse all the energy rate data from the complete fetched content
    """
    # More comprehensive raw data from the website
    raw_entries = [
        ("Winter Break 24", "Ambit Energy", 0.18800, "24", "0.00", "No", "1-877-282-6248"),
        ("Ultimate Perks 12", "Ambit Energy", 0.14250, "12", "0.00", "No", "1-877-282-6248"),
        ("Winter Break 12", "Ambit Energy", 0.18500, "12", "0.00", "No", "1-877-282-6248"),
        ("White Mountain Select 12 Month Term", "Ambit Energy", 0.13500, "12", "0.00", "No", "1-877-282-6248"),
        ("Amherst BASIC", "Amherst Community Power", 0.08840, "6", "25.20", "No", "866-968-8065"),
        ("Amherst GREEN Default", "Amherst Community Power", 0.08880, "6", "26.20", "No", "866-968-8065"),
        ("Amherst GREEN 50%", "Amherst Community Power", 0.10300, "6", "50.00", "No", "866-968-8065"),
        ("Amherst GREEN 100%", "Amherst Community Power", 0.11950, "6", "100.00", "No", "866-968-8065"),
        ("Bennington GREEN Default", "Bennington Community Power", 0.08860, "6", "26.20", "No", "866-968-8065"),
        ("Bennington GREEN 50%", "Bennington Community Power", 0.10280, "6", "50.00", "No", "866-968-8065"),
        ("Bennington GREEN 100%", "Bennington Community Power", 0.11930, "6", "100.00", "No", "866-968-8065"),
        ("Bennington BASIC", "Bennington Community Power", 0.08820, "6", "25.20", "No", "866-968-8065"),
        ("Embrace Green 6", "CleanSky Energy", 0.13490, "6", "100.00", "$50.00", "1-888-355-6205"),
        ("Ultra Clean Solar 24", "CleanSky Energy", 0.12790, "24", "100.00", "$150.00", "1-888-355-6205"),
        ("Embrace Green 12", "CleanSky Energy", 0.12990, "12", "100.00", "$75.00", "1-888-355-6205"),
        ("Embrace Green 24", "CleanSky Energy", 0.12490, "24", "100.00", "$150.00", "1-888-355-6205"),
        ("Affordable Wind 12", "CleanSky Energy", 0.13190, "12", "100.00", "$75.00", "1-888-355-6205"),
        ("Clean 100 - Residential", "Community Power Coalition of NH", 0.16819, "6", "100.00", "No", "1-866-603-7697"),
        ("Granite Basic - Residential", "Community Power Coalition of NH", 0.13419, "6", "25.20", "No", "1-866-603-7697"),
        ("Canterbury Basic - Residential", "Community Power Coalition of NH", 0.13619, "6", "25.20", "No", "1-866-603-7697"),
        ("Enfield Local - Residential", "Community Power Coalition of NH", 0.13619, "6", "25.20", "No", "1-866-603-7697"),
        ("Peterborough Local - Residential", "Community Power Coalition of NH", 0.13995, "6", "25.20", "No", "1-866-603-7697"),
        ("Granite Plus - Residential", "Community Power Coalition of NH", 0.14119, "6", "33.00", "No", "1-866-603-7697"),
        ("Clean 50 - Residential", "Community Power Coalition of NH", 0.14819, "6", "50.00", "No", "1-866-603-7697"),
        ("Live Brighter AE 15", "Direct Energy Services, LLC", 0.11790, "15", "0.00", "No", "888-836-6141"),
        ("Live Brighter SS 12", "Direct Energy Services, LLC", 0.12090, "12", "0.00", "No", "888-836-6141"),
        ("Go Green Lights 24", "Direct Energy Services, LLC", 0.13390, "24", "100.00", "No", "888-836-6141"),
        ("Live Brighter 15", "Direct Energy Services, LLC", 0.12290, "15", "0.00", "No", "888-836-6141"),
        ("Live Brighter AE 12", "Direct Energy Services, LLC", 0.12690, "12", "0.00", "No", "888-836-6141"),
        ("Live Brighter TO 15", "Direct Energy Services, LLC", 0.11690, "15", "0.00", "No", "888-836-6141"),
        ("Live Brighter 24", "Direct Energy Services, LLC", 0.12890, "24", "0.00", "No", "888-836-6141"),
        ("Easy Choice 3 - Residential", "ENH Power", 0.08890, "3", "0.00", "No", "1-833-488-3147"),
        ("Simple Power 12 - Residential", "ENH Power", 0.11790, "12", "0.00", "$100.00", "1-833-488-3147"),
        ("Optional Green 100", "Hampton Community Power Aggregation", 0.12918, "4", "100.00", "No", "1-866-485-5858"),
        ("Optional Green 33", "Hampton Community Power Aggregation", 0.10798, "4", "57.30", "No", "1-866-485-5858"),
        ("Standard", "Hampton Community Power Aggregation", 0.09425, "4", "24.30", "No", "1-866-485-5858"),
        ("Hillsborough GREEN Default", "Hillsborough Community Power", 0.08850, "7", "26.20", "No", "866-968-8065"),
        ("Hillsborough GREEN 50%", "Hillsborough Community Power", 0.10270, "7", "50.00", "No", "866-968-8065"),
        ("Hillsborough GREEN 100%", "Hillsborough Community Power", 0.11920, "7", "100.00", "No", "866-968-8065"),
        ("Hillsborough BASIC", "Hillsborough Community Power", 0.08810, "7", "25.20", "No", "866-968-8065"),
        ("Jaffrey BASIC", "Jaffrey Community Power", 0.10568, "20", "24.30", "No", "1-888-875-1711"),
        ("Jaffrey GREEN 50%", "Jaffrey Community Power", 0.11648, "20", "50.00", "No", "1-888-875-1711"),
        ("Jaffrey GREEN Default", "Jaffrey Community Power", 0.10968, "20", "34.30", "No", "1-888-875-1711"),
        ("Jaffrey GREEN 100%", "Jaffrey Community Power", 0.13648, "20", "100.00", "No", "1-888-875-1711"),
        ("Keene 100% Local Green", "Keene Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065"),
        ("Keene Basic", "Keene Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065"),
        ("Keene 50% Local Green", "Keene Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065"),
        ("Keene Local Green", "Keene Community Power", 0.11470, "30", "33.40", "No", "1-866-968-8065"),
        ("Marlborough Basic", "Marlborough Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065"),
        ("Marlborough 50", "Marlborough Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065"),
        ("Marlborough Standard", "Marlborough Community Power", 0.11471, "30", "33.40", "No", "1-866-968-8065"),
        ("Marlborough 100", "Marlborough Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065"),
        ("Milford PLUS 10%", "Milford Community Power", 0.10968, "20", "34.30", "No", "1-888-875-1711"),
        ("Milford GREEN 100%", "Milford Community Power", 0.13648, "20", "100.00", "No", "1-888-875-1711"),
        ("Milford GREEN 50%", "Milford Community Power", 0.11648, "20", "50.00", "No", "1-888-875-1711"),
        ("Milford DEFAULT", "Milford Community Power", 0.10568, "20", "24.30", "No", "1-888-875-1711"),
        ("New Boston GREEN Default", "New Boston Community Power", 0.10968, "20", "34.30", "No", "1-888-875-1711"),
        ("New Boston GREEN 50%", "New Boston Community Power", 0.11648, "20", "50.00", "No", "1-888-875-1711"),
        ("New Boston BASIC", "New Boston Community Power", 0.10568, "20", "24.30", "No", "1-888-875-1711"),
        ("New Boston GREEN 100%", "New Boston Community Power", 0.13648, "20", "100.00", "No", "1-888-875-1711"),
        ("14 Month Renewable Fixed", "North American Power & Gas, LLC", 0.13940, "14", "100.00", "$10.00", "877-572-9965"),
        ("14 Month Standard Fixed", "North American Power & Gas, LLC", 0.12990, "14", "0.00", "$10.00", "877-572-9965"),
        ("12 Month Standard Fixed", "North American Power & Gas, LLC", 0.12790, "12", "0.00", "$10.00", "877-572-9965"),
        ("Rollinsford BASIC", "Rollinsford Community Power", 0.08840, "7", "25.20", "No", "866-968-8065"),
        ("Rollinsford GREEN 100%", "Rollinsford Community Power", 0.11950, "7", "100.00", "No", "866-968-8065"),
        ("Rollinsford GREEN 50%", "Rollinsford Community Power", 0.10300, "7", "50.00", "No", "866-968-8065"),
        ("Rollinsford GREEN Default", "Rollinsford Community Power", 0.08880, "7", "26.20", "No", "866-968-8065"),
        ("SmartEnergy - Web Only Rate", "SmartEnergy", 0.10890, "4", "100.00", "No", "1-800-760-1207"),
        ("Swanzey 100", "Swanzey Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065"),
        ("Swanzey Basic", "Swanzey Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065"),
        ("Swanzey Standard", "Swanzey Community Power", 0.11471, "30", "33.40", "No", "1-866-968-8065"),
        ("Swanzey 50", "Swanzey Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065"),
        ("Think Clean 12", "Think Energy", 0.11900, "12", "100.00", "No", "1-833-669-3080"),
        ("Think Clean 36", "Think Energy", 0.12500, "36", "100.00", "No", "1-833-669-3080"),
        ("Think Basic 4", "Think Energy", 0.09900, "4", "0.00", "No", "1-833-669-3080"),
        ("Power Your Tomorrow Fixed - 18", "Town Square Energy", 0.11870, "18", "0.00", "No", "1-877-430-0093"),
        ("Power Your Tomorrow Variable - 1", "Town Square Energy", 0.08890, "1", "0.00", "No", "1-877-430-0093"),
        ("Power Your Today Fixed - 4", "Town Square Energy", 0.09770, "4", "0.00", "No", "1-877-430-0093"),
        ("Power Your Tomorrow Fixed - 4", "Town Square Energy", 0.12000, "4", "0.00", "$50.00", "1-877-430-0093"),
        ("Power Your Tomorrow - 4 Green", "Town Square Energy", 0.14740, "4", "100.00", "$50.00", "1-877-430-0093"),
        ("Power Your Tomorrow Variable - 1 Green", "Town Square Energy", 0.09890, "1", "100.00", "No", "1-877-430-0093"),
        ("Power Your Tomorrow Fixed - 12", "Town Square Energy", 0.11770, "12", "0.00", "No", "1-877-430-0093"),
        ("Wilton 100", "Wilton Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065"),
        ("Wilton Basic", "Wilton Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065"),
        ("Wilton 50", "Wilton Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065"),
        ("Wilton Standard", "Wilton Community Power", 0.11471, "30", "33.40", "No", "1-866-968-8065"),
        ("SureLock 12 - Residential", "XOOM Energy New Hampshire, LLC", 0.13090, "12", "0.00", "$110.00", "1-888-997-8979"),
        ("SimpleClean12 - Residential", "XOOM Energy New Hampshire, LLC", 0.13290, "12", "50.00", "$110.00", "1-888-997-8979"),
        ("RescueLock 12", "XOOM Energy New Hampshire, LLC", 0.13790, "12", "0.00", "$110.00", "1-888-997-8979"),
        ("SimpleClean", "XOOM Energy New Hampshire, LLC", 0.16490, "1", "50.00", "No", "1-888-997-8979"),
        ("SureLock 24", "XOOM Energy New Hampshire, LLC", 0.13190, "24", "0.00", "$200.00", "1-888-997-8979"),
        ("Eversource Default", "Eversource", 0.11196, "6", "23.40", "No", "1-800-662-7764")  # Adding the default utility rate for comparison
    ]
    
    suppliers = []
    for entry in raw_entries:
        suppliers.append({
            'plan_name': entry[0],
            'supplier': entry[1],
            'rate_per_kwh': entry[2],
            'term_months': entry[3],
            'renewable_energy_pct': entry[4],
            'cancellation_fee': entry[5],
            'phone': entry[6]
        })
    
    return suppliers

def create_comparison_table(suppliers):
    """
    Create a clean comparison table
    """
    df = pd.DataFrame(suppliers)
    
    # Convert renewable percentage to float for sorting
    df['renewable_float'] = pd.to_numeric(df['renewable_energy_pct'], errors='coerce')
    
    # Sort by rate (lowest to highest)
    df = df.sort_values('rate_per_kwh')
    
    # Select columns for display
    display_df = df[['plan_name', 'supplier', 'rate_per_kwh', 'term_months', 
                     'renewable_energy_pct', 'cancellation_fee', 'phone']].copy()
    
    # Rename columns
    display_df.columns = ['Plan Name', 'Supplier', 'Rate ($/kWh)', 'Term (Months)', 
                          'Renewable %', 'Cancel Fee', 'Phone']
    
    # Format the rate column
    display_df['Rate ($/kWh)'] = display_df['Rate ($/kWh)'].apply(lambda x: f"${x:.5f}")
    
    return display_df

def save_comparison_files(df):
    """
    Save the comparison to multiple file formats
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save to CSV
    csv_file = f"nh_energy_rates_comparison_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved to {csv_file}")
    
    # Save to Excel
    excel_file = f"nh_energy_rates_comparison_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Energy Rates Comparison")
        
        # Get the workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets["Energy Rates Comparison"]
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"✓ Saved to {excel_file}")
    
    # Create an enhanced HTML file
    html_file = f"nh_energy_rates_comparison_{timestamp}.html"
    
    # Calculate some statistics
    rates = [float(rate.replace('$', '')) for rate in df['Rate ($/kWh)']]
    min_rate = min(rates)
    max_rate = max(rates)
    avg_rate = sum(rates) / len(rates)
    
    # Find best deals by category
    renewable_100_df = df[df['Renewable %'].astype(float) == 100.0]
    best_renewable = renewable_100_df.iloc[0] if not renewable_100_df.empty else None
    
    short_term_df = df[df['Term (Months)'].astype(str).isin(['3', '4', '6'])]
    best_short = short_term_df.iloc[0] if not short_term_df.empty else None
    
    no_cancel_df = df[df['Cancel Fee'] == 'No']
    best_no_cancel = no_cancel_df.iloc[0] if not no_cancel_df.empty else None
    best_no_cancel = no_cancel_df.iloc[0] if not no_cancel_df.empty else None
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NH Energy Rate Comparison - Eversource Territory</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                border-bottom: 4px solid #3498db;
                padding-bottom: 15px;
                margin-bottom: 10px;
                font-size: 2.5em;
            }}
            .subtitle {{
                text-align: center;
                color: #7f8c8d;
                font-style: italic;
                margin-bottom: 30px;
                font-size: 1.1em;
            }}
            .stats {{
                background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                color: white;
                padding: 25px;
                border-radius: 10px;
                margin: 25px 0;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                text-align: center;
            }}
            .stat-item {{
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 8px;
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 0.9em;
                opacity: 0.9;
            }}
            .highlights {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}
            .highlight-card {{
                background: #f8f9fa;
                border-left: 5px solid #28a745;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .highlight-title {{
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}
            .highlight-content {{
                color: #5a6c7d;
            }}
            .table-container {{
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                font-size: 14px;
                background: white;
            }}
            th, td {{
                border: 1px solid #e9ecef;
                padding: 12px 8px;
                text-align: left;
            }}
            th {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: bold;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            tr:hover {{
                background-color: #e3f2fd;
                transform: scale(1.01);
                transition: all 0.2s ease;
                cursor: pointer;
            }}
            .rate-excellent {{
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%) !important;
                color: white;
                font-weight: bold;
            }}
            .rate-good {{
                background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%) !important;
                color: white;
            }}
            .rate-average {{
                background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%) !important;
                color: white;
            }}
            .rate-expensive {{
                background: linear-gradient(135deg, #e17055 0%, #d63031 100%) !important;
                color: white;
                font-weight: bold;
            }}
            .renewable-100 {{
                background: linear-gradient(135deg, #00b894 0%, #00cec9 100%) !important;
                color: white;
                font-weight: bold;
            }}
            .renewable-high {{
                background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%) !important;
                color: white;
            }}
            .renewable-medium {{
                background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%) !important;
                color: white;
            }}
            .supplier-community {{
                font-style: italic;
                color: #00b894;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 25px;
                border-top: 2px solid #e9ecef;
                color: #6c757d;
            }}
            .legend {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
            .legend-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
            }}
            .legend-title {{
                font-weight: bold;
                margin-bottom: 10px;
                color: #2c3e50;
            }}
            .legend-item {{
                display: inline-block;
                padding: 5px 10px;
                margin: 3px;
                border-radius: 5px;
                font-size: 0.9em;
            }}
            @media (max-width: 768px) {{
                .container {{ padding: 15px; }}
                h1 {{ font-size: 2em; }}
                table {{ font-size: 12px; }}
                th, td {{ padding: 8px 4px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ New Hampshire Energy Rate Comparison</h1>
            <div class="subtitle">
                Eversource Territory • Updated {datetime.now().strftime('%B %d, %Y')}
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">${min_rate:.5f}</div>
                    <div class="stat-label">Lowest Rate ($/kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${max_rate:.5f}</div>
                    <div class="stat-label">Highest Rate ($/kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${avg_rate:.5f}</div>
                    <div class="stat-label">Average Rate ($/kWh)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(rates)}</div>
                    <div class="stat-label">Total Plans Available</div>
                </div>
            </div>
    """
    
    # Add highlights section
    if (best_renewable is not None) or (best_short is not None) or (best_no_cancel is not None):
        html_content += '<div class="highlights">'
        
        if best_renewable is not None:
            html_content += f'''
            <div class="highlight-card">
                <div class="highlight-title">🌱 Best 100% Renewable Energy</div>
                <div class="highlight-content">
                    <strong>{best_renewable['Plan Name']}</strong><br>
                    {best_renewable['Supplier']}<br>
                    <strong>{best_renewable['Rate ($/kWh)']}/kWh</strong> • {best_renewable['Term (Months)']} months
                </div>
            </div>'''
        
        if best_short is not None:
            html_content += f'''
            <div class="highlight-card">
                <div class="highlight-title">⚡ Best Short-Term Rate</div>
                <div class="highlight-content">
                    <strong>{best_short['Plan Name']}</strong><br>
                    {best_short['Supplier']}<br>
                    <strong>{best_short['Rate ($/kWh)']}/kWh</strong> • {best_short['Term (Months)']} months
                </div>
            </div>'''
        
        if best_no_cancel is not None:
            html_content += f'''
            <div class="highlight-card">
                <div class="highlight-title">🚫 Best Rate (No Cancel Fee)</div>
                <div class="highlight-content">
                    <strong>{best_no_cancel['Plan Name']}</strong><br>
                    {best_no_cancel['Supplier']}<br>
                    <strong>{best_no_cancel['Rate ($/kWh)']}/kWh</strong> • {best_no_cancel['Term (Months)']} months
                </div>
            </div>'''
        
        html_content += '</div>'
    
    # Generate table HTML with enhanced color coding
    html_content += '''
    <div class="table-container">
        <table>
            <thead>
                <tr>'''
    
    for col in df.columns:
        html_content += f"<th>{col}</th>"
    
    html_content += "</tr></thead><tbody>"
    
    for _, row in df.iterrows():
        rate_value = float(row['Rate ($/kWh)'].replace('$', ''))
        renewable_value = float(row['Renewable %']) if row['Renewable %'] else 0
        
        # Rate color coding
        if rate_value <= 0.09:
            rate_class = "rate-excellent"
        elif rate_value <= 0.11:
            rate_class = "rate-good"
        elif rate_value <= 0.13:
            rate_class = "rate-average"
        else:
            rate_class = "rate-expensive"
        
        # Renewable energy color coding
        if renewable_value == 100:
            renewable_class = "renewable-100"
        elif renewable_value >= 50:
            renewable_class = "renewable-high"
        elif renewable_value >= 25:
            renewable_class = "renewable-medium"
        else:
            renewable_class = ""
        
        # Supplier styling
        supplier_class = "supplier-community" if "Community" in row['Supplier'] else ""
        
        html_content += "<tr>"
        for i, (col, value) in enumerate(row.items()):
            if col == 'Rate ($/kWh)':
                html_content += f'<td class="{rate_class}">{value}</td>'
            elif col == 'Renewable %':
                html_content += f'<td class="{renewable_class}">{value}%</td>'
            elif col == 'Supplier':
                html_content += f'<td class="{supplier_class}">{value}</td>'
            else:
                html_content += f'<td>{value}</td>'
        html_content += "</tr>"
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="legend">
        <div class="legend-section">
            <div class="legend-title">💰 Rate Categories</div>
            <span class="legend-item rate-excellent">Excellent (≤$0.09)</span>
            <span class="legend-item rate-good">Good ($0.09-$0.11)</span>
            <span class="legend-item rate-average">Average ($0.11-$0.13)</span>
            <span class="legend-item rate-expensive">Expensive (>$0.13)</span>
        </div>
        <div class="legend-section">
            <div class="legend-title">🌱 Renewable Energy</div>
            <span class="legend-item renewable-100">100% Renewable</span>
            <span class="legend-item renewable-high">≥50% Renewable</span>
            <span class="legend-item renewable-medium">≥25% Renewable</span>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>⚠️ Important Notes:</strong></p>
        <ul style="text-align: left; max-width: 600px; margin: 0 auto;">
            <li>Rates shown are per kilowatt-hour (kWh) and do not include delivery charges</li>
            <li>Community Power programs may have additional local benefits</li>
            <li>Variable rates may change monthly - fixed rates stay the same for the term</li>
            <li>Always verify current rates and terms directly with suppliers before enrolling</li>
            <li>Consider your usage patterns when choosing between short and long-term contracts</li>
        </ul>
        <p style="margin-top: 20px;">
            <strong>Source:</strong> <a href="https://www.energy.nh.gov/engyapps/ceps/ResidentialCompare.aspx?choice=Eversource" target="_blank">NH Department of Energy</a><br>
            Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        </p>
    </div>
        </div>
    </body>
    </html>
    """
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ Saved to {html_file}")
    
    return csv_file, excel_file, html_file

def main():
    """
    Main function to create the energy rate comparison
    """
    print("🔌 NH Energy Rate Parser - Complete Edition")
    print("=" * 60)
    
    # Parse the data
    suppliers = parse_all_energy_data()
    print(f"📊 Parsed {len(suppliers)} energy supplier plans")
    
    # Create comparison table
    df = create_comparison_table(suppliers)
    
    # Display summary of the best options
    print("\n🏆 TOP 10 LOWEST RATES")
    print("-" * 50)
    top_10 = df.head(10)
    for idx, row in top_10.iterrows():
        renewable_indicator = "🌱" if float(row['Renewable %']) == 100 else "🔋" if float(row['Renewable %']) >= 50 else ""
        print(f"{row['Rate ($/kWh)']} | {row['Plan Name'][:30]:<30} | {row['Supplier'][:25]:<25} | {row['Term (Months)']}mo {renewable_indicator}")
    
    # Save to files
    print(f"\n💾 Saving comparison files...")
    csv_file, excel_file, html_file = save_comparison_files(df)
    
    # Show summary statistics
    rates = [float(rate.replace('$', '')) for rate in df['Rate ($/kWh)']]
    print(f"\n📈 SUMMARY STATISTICS")
    print("-" * 40)
    print(f"Lowest rate:     ${min(rates):.5f} per kWh")
    print(f"Highest rate:    ${max(rates):.5f} per kWh")
    print(f"Average rate:    ${sum(rates)/len(rates):.5f} per kWh")
    print(f"Rate spread:     ${max(rates) - min(rates):.5f} per kWh")
    print(f"Total plans:     {len(rates)}")
    
    # Renewable energy analysis
    renewable_100 = sum(1 for _, row in df.iterrows() if float(row['Renewable %']) == 100)
    renewable_50_plus = sum(1 for _, row in df.iterrows() if float(row['Renewable %']) >= 50)
    print(f"100% Renewable:  {renewable_100} plans")
    print(f"50%+ Renewable:  {renewable_50_plus} plans")
    
    print(f"\n✅ Analysis complete!")
    print(f"   🌐 Open {html_file} in your browser for the best viewing experience")
    print(f"   📊 Use {excel_file} for detailed analysis in Excel")
    print(f"   📋 Use {csv_file} for importing into other tools")

if __name__ == "__main__":
    main()
