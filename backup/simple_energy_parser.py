import re
import pandas as pd
from datetime import datetime

def parse_energy_data():
    """
    Parse the energy rate data from the fetched content
    """
    # The raw data from the website
    raw_data = """
    Winter Break 24 Per KWh: $0.18800 Last Update: 8/1/2025 Ambit Energy Pricing: Fixed Monthly Charge: No 1-877-282-6248 Intro Price: No Rate Good for: 24 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: As temperatures drop, your savings will rise. Get 50% off your energy charges on bill cycles beginning November 1st through the end of February. Only available to new Ambit customers!
    
    Ultimate Perks 12 Per KWh: $0.14250 Last Update: 8/1/2025 Ambit Energy Pricing: Fixed Monthly Charge: No 1-877-282-6248 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Only available to new Ambit customers!
    
    Winter Break 12 Per KWh: $0.18500 Last Update: 8/1/2025 Ambit Energy Pricing: Fixed Monthly Charge: No 1-877-282-6248 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: As temperatures drop, your savings will rise. Get 50% off your energy charges on bill cycles beginning November 1st through the end of February. Only available to new Ambit customers!
    
    White Mountain Select 12 Month Term Per KWh: $0.13500 Last Update: 8/1/2025 Ambit Energy Pricing: Fixed Monthly Charge: No 1-877-282-6248 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Only available to new Ambit customers!
    
    Amherst BASIC Per KWh: $0.08840 Last Update: 7/21/2025 Amherst Community Power Pricing: Fixed Monthly Charge: No 866-968-8065 Intro Price: No Rate Good for: 6 months Compare Cancellation Fee: No Rate End: October, 2025 *Last meter read* Renewable Energy: 25.20 % Comments: Stable rate program offered by Standard Power open to customers in Amherst.
    
    Amherst GREEN Default Per KWh: $0.08880 Last Update: 7/21/2025 Amherst Community Power Pricing: Fixed Monthly Charge: No 866-968-8065 Intro Price: No Rate Good for: 6 months Compare Cancellation Fee: No Rate End: October, 2025 *Last meter read* Renewable Energy: 26.20 % Comments: Stable rate program offered by Standard Power open to customers in Amherst.
    
    Amherst GREEN 50% Per KWh: $0.10300 Last Update: 7/21/2025 Amherst Community Power Pricing: Fixed Monthly Charge: No 866-968-8065 Intro Price: No Rate Good for: 6 months Compare Cancellation Fee: No Rate End: October, 2025 *Last meter read* Renewable Energy: 50.00 % Comments: Stable rate program offered by Standard Power open to customers in Amherst.
    
    Amherst GREEN 100% Per KWh: $0.11950 Last Update: 7/21/2025 Amherst Community Power Pricing: Fixed Monthly Charge: No 866-968-8065 Intro Price: No Rate Good for: 6 months Compare Cancellation Fee: No Rate End: October, 2025 *Last meter read* Renewable Energy: 100.00 % Comments: Stable rate program offered by Standard Power open to customers in Amherst.
    
    Embrace Green 6 Per KWh: $0.13490 Last Update: 8/1/2025 CleanSky Energy Pricing: Fixed Monthly Charge: No 1-888-355-6205 Intro Price: No Rate Good for: 6 months Compare Cancellation Fee: $50.00 Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Have a question about a plan or need help placing an order? Call us: 1-888-355-6205
    
    Ultra Clean Solar 24 Per KWh: $0.12790 Last Update: 8/1/2025 CleanSky Energy Pricing: Fixed Monthly Charge: No 1-888-355-6205 Intro Price: No Rate Good for: 24 months Compare Cancellation Fee: $150.00 Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Have a question about a plan or need help placing an order? Call us: 1-888-355-6205
    
    Embrace Green 12 Per KWh: $0.12990 Last Update: 8/1/2025 CleanSky Energy Pricing: Fixed Monthly Charge: No 1-888-355-6205 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: $75.00 Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Have a question about a plan or need help placing an order? Call us: 1-888-355-6205
    
    Embrace Green 24 Per KWh: $0.12490 Last Update: 8/1/2025 CleanSky Energy Pricing: Fixed Monthly Charge: No 1-888-355-6205 Intro Price: No Rate Good for: 24 months Compare Cancellation Fee: $150.00 Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Have a question about a plan or need help placing an order? Call us: 1-888-355-6205
    
    Affordable Wind 12 Per KWh: $0.13190 Last Update: 8/1/2025 CleanSky Energy Pricing: Fixed Monthly Charge: No 1-888-355-6205 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: $75.00 Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Have a question about a plan or need help placing an order? Call us: 1-888-355-6205
    
    Live Brighter AE 15 Per KWh: $0.11790 Last Update: 8/4/2025 Direct Energy Services, LLC Pricing: Fixed Monthly Charge: No 888-836-6141 Intro Price: No Rate Good for: 15 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Rate plan is available for new customers only.
    
    Live Brighter SS 12 Per KWh: $0.12090 Last Update: 8/4/2025 Direct Energy Services, LLC Pricing: Fixed Monthly Charge: No 888-836-6141 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Rate plan is available for new customers only.
    
    Go Green Lights 24 Per KWh: $0.13390 Last Update: 8/4/2025 Direct Energy Services, LLC Pricing: Fixed Monthly Charge: No 888-836-6141 Intro Price: No Rate Good for: 24 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Green Energy. Rate plan is available for new customers only.
    
    Live Brighter 15 Per KWh: $0.12290 Last Update: 8/4/2025 Direct Energy Services, LLC Pricing: Fixed Monthly Charge: No 888-836-6141 Intro Price: No Rate Good for: 15 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Rate plan is available for new customers only.
    
    Live Brighter AE 12 Per KWh: $0.12690 Last Update: 8/4/2025 Direct Energy Services, LLC Pricing: Fixed Monthly Charge: No 888-836-6141 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Rate plan is available for new customers only.
    
    Live Brighter TO 15 Per KWh: $0.11690 Last Update: 8/4/2025 Direct Energy Services, LLC Pricing: Fixed Monthly Charge: No 888-836-6141 Intro Price: No Rate Good for: 15 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Rate plan is available for new customers only.
    
    Live Brighter 24 Per KWh: $0.12890 Last Update: 8/4/2025 Direct Energy Services, LLC Pricing: Fixed Monthly Charge: No 888-836-6141 Intro Price: No Rate Good for: 24 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Rate plan is available for new customers only.
    
    Easy Choice 3 - Residential Per KWh: $0.08890 Last Update: 8/5/2025 ENH Power Pricing: Fixed Monthly Charge: No 1-833-488-3147 Intro Price: No Rate Good for: 3 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Are you looking for a fixed rate energy plan? This plan is for you. Enjoy 3 months of a fixed rate with no monthly service fee and no early termination fee.
    
    Simple Power 12 - Residential Per KWh: $0.11790 Last Update: 8/5/2025 ENH Power Pricing: Fixed Monthly Charge: No 1-833-488-3147 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: $100.00 Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: Are you looking for a fixed rate energy plan? This plan is for you. Enjoy 12 months of a fixed rate with no monthly service fee and a $100 early termination fee.
    
    SmartEnergy - Web Only Rate Per KWh: $0.10890 Last Update: 8/5/2025 SmartEnergy Pricing: Fixed Monthly Charge: No 1-800-760-1207 Intro Price: No Rate Good for: 4 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Enjoy our fixed rate for 4 months!
    
    Think Clean 12 Per KWh: $0.11900 Last Update: 7/31/2025 Think Energy Pricing: Fixed Monthly Charge: No 1-833-669-3080 Intro Price: No Rate Good for: 12 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Think Clean 12 Sign up and receive a $100 gift card. New customers only.
    
    Think Clean 36 Per KWh: $0.12500 Last Update: 8/1/2025 Think Energy Pricing: Fixed Monthly Charge: No 1-833-669-3080 Intro Price: No Rate Good for: 36 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 100.00 % Comments: Think Clean 36 Sign up and receive a $100 gift card. New customers only.
    
    Think Basic 4 Per KWh: $0.09900 Last Update: 7/31/2025 Think Energy Pricing: Fixed Monthly Charge: No 1-833-669-3080 Intro Price: No Rate Good for: 4 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments:
    
    Power Your Tomorrow Fixed - 18 Per KWh: $0.11870 Last Update: 7/31/2025 Town Square Energy Pricing: Fixed Monthly Charge: No 1-877-430-0093 Intro Price: No Rate Good for: 18 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: 18 monthly bill cycles fixed at 11.87 cents/kWh.
    
    Power Your Tomorrow Variable - 1 Per KWh: $0.08890 Last Update: 7/25/2025 Town Square Energy Pricing: Variable Monthly Charge: No 1-877-430-0093 Intro Price: No Rate Good for: 1 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: You will be given the opportunity to earn a rebate equal to 10% of what you paid toward the electricity supply charges during your first ten full billing cycles.
    
    Power Your Today Fixed - 4 Per KWh: $0.09770 Last Update: 7/31/2025 Town Square Energy Pricing: Fixed Monthly Charge: No 1-877-430-0093 Intro Price: No Rate Good for: 4 months Compare Cancellation Fee: No Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: 4 monthly bill cycles fixed at 9.77 cents/kWh.
    
    Power Your Tomorrow Fixed - 4 Per KWh: $0.12000 Last Update: 7/31/2025 Town Square Energy Pricing: Fixed Monthly Charge: No 1-877-430-0093 Intro Price: No Rate Good for: 4 months Compare Cancellation Fee: $50.00 Rate End: *Last meter read* Renewable Energy: 0.00 % Comments: 4 monthly bill cycles fixed at 12.00 cents/kWh.
    """
    
    suppliers = []
    
    # Split into individual entries
    entries = [entry.strip() for entry in raw_data.split('\n\n') if entry.strip()]
    
    for entry in entries:
        # Extract plan name and rate
        rate_match = re.search(r'(.+?)\s+Per KWh:\s*\$(\d+\.\d+)', entry)
        if not rate_match:
            continue
            
        plan_name = rate_match.group(1).strip()
        rate = float(rate_match.group(2))
        
        # Extract supplier name
        supplier_match = re.search(r'Last Update:.*?\d+/\d+/\d+\s+([^P]+?)(?:Pricing:|$)', entry)
        supplier = supplier_match.group(1).strip() if supplier_match else ""
        
        # Extract term
        term_match = re.search(r'Rate Good for:\s*(\d+)\s*months?', entry)
        term = term_match.group(1) if term_match else ""
        
        # Extract renewable percentage
        renewable_match = re.search(r'Renewable Energy:\s*(\d+\.?\d*)\s*%', entry)
        renewable = renewable_match.group(1) if renewable_match else "0"
        
        # Extract cancellation fee
        cancel_match = re.search(r'Cancellation Fee:\s*([^R]+?)(?:Rate|$)', entry)
        cancel_fee = cancel_match.group(1).strip() if cancel_match else "No"
        
        # Extract phone
        phone_match = re.search(r'(\d{1}-?\d{3}-?\d{3}-?\d{4})', entry)
        phone = phone_match.group(1) if phone_match else ""
        
        # Extract pricing type
        pricing_match = re.search(r'Pricing:\s*(\w+)', entry)
        pricing_type = pricing_match.group(1) if pricing_match else ""
        
        suppliers.append({
            'plan_name': plan_name,
            'supplier': supplier,
            'rate_per_kwh': rate,
            'term_months': term,
            'renewable_energy_pct': renewable,
            'cancellation_fee': cancel_fee,
            'phone': phone,
            'pricing_type': pricing_type
        })
    
    return suppliers

def create_comparison_table(suppliers):
    """
    Create a clean comparison table
    """
    df = pd.DataFrame(suppliers)
    
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
    df.to_excel(excel_file, index=False, sheet_name="Energy Rates Comparison")
    print(f"✓ Saved to {excel_file}")
    
    # Create an enhanced HTML file
    html_file = f"nh_energy_rates_comparison_{timestamp}.html"
    
    # Calculate some statistics
    rates = [float(rate.replace('$', '')) for rate in df['Rate ($/kWh)']]
    min_rate = min(rates)
    max_rate = max(rates)
    avg_rate = sum(rates) / len(rates)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NH Energy Rate Comparison - Eversource Territory</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 20px;
                background-color: #f8f9fa;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            .stats {{
                background: #e8f4f8;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
            }}
            .stat-item {{
                text-align: center;
                margin: 5px;
            }}
            .stat-value {{
                font-size: 1.5em;
                font-weight: bold;
                color: #2c3e50;
            }}
            .stat-label {{
                color: #7f8c8d;
                font-size: 0.9em;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                font-size: 14px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px 8px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
                position: sticky;
                top: 0;
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            tr:hover {{
                background-color: #e3f2fd;
                cursor: pointer;
            }}
            .rate-excellent {{
                background-color: #d4edda !important;
                color: #155724;
                font-weight: bold;
            }}
            .rate-good {{
                background-color: #d1ecf1 !important;
                color: #0c5460;
            }}
            .rate-average {{
                background-color: #fff3cd !important;
                color: #856404;
            }}
            .rate-expensive {{
                background-color: #f8d7da !important;
                color: #721c24;
            }}
            .renewable-100 {{
                background-color: #28a745 !important;
                color: white;
                font-weight: bold;
            }}
            .renewable-high {{
                background-color: #6f42c1 !important;
                color: white;
            }}
            .renewable-medium {{
                background-color: #fd7e14 !important;
                color: white;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #6c757d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔌 New Hampshire Energy Rate Comparison</h1>
            <p style="text-align: center; color: #6c757d; font-style: italic;">
                Eversource Territory • Data extracted from NH Department of Energy
            </p>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">${min_rate:.5f}</div>
                    <div class="stat-label">Lowest Rate</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${max_rate:.5f}</div>
                    <div class="stat-label">Highest Rate</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${avg_rate:.5f}</div>
                    <div class="stat-label">Average Rate</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(rates)}</div>
                    <div class="stat-label">Total Plans</div>
                </div>
            </div>
    """
    
    # Generate table HTML with color coding
    html_content += "\n<table>\n"
    html_content += "<tr>" + "".join([f"<th>{col}</th>" for col in df.columns]) + "</tr>\n"
    
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
        
        html_content += "<tr>"
        for i, (col, value) in enumerate(row.items()):
            if col == 'Rate ($/kWh)':
                html_content += f'<td class="{rate_class}">{value}</td>'
            elif col == 'Renewable %':
                html_content += f'<td class="{renewable_class}">{value}%</td>'
            else:
                html_content += f'<td>{value}</td>'
        html_content += "</tr>\n"
    
    html_content += """
        </table>
        
        <div class="footer">
            <p><strong>Rate Color Guide:</strong></p>
            <p>
                <span style="background-color: #d4edda; padding: 3px 8px; border-radius: 3px; margin: 0 5px;">Excellent (≤$0.09)</span>
                <span style="background-color: #d1ecf1; padding: 3px 8px; border-radius: 3px; margin: 0 5px;">Good ($0.09-$0.11)</span>
                <span style="background-color: #fff3cd; padding: 3px 8px; border-radius: 3px; margin: 0 5px;">Average ($0.11-$0.13)</span>
                <span style="background-color: #f8d7da; padding: 3px 8px; border-radius: 3px; margin: 0 5px;">Expensive (>$0.13)</span>
            </p>
            <p><strong>Renewable Energy Guide:</strong></p>
            <p>
                <span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; margin: 0 5px;">100% Renewable</span>
                <span style="background-color: #6f42c1; color: white; padding: 3px 8px; border-radius: 3px; margin: 0 5px;">≥50% Renewable</span>
                <span style="background-color: #fd7e14; color: white; padding: 3px 8px; border-radius: 3px; margin: 0 5px;">≥25% Renewable</span>
            </p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Source:</strong> <a href="https://www.energy.nh.gov/engyapps/ceps/ResidentialCompare.aspx?choice=Eversource">NH Department of Energy</a></p>
            <p><em>Always verify rates and terms directly with suppliers before enrolling.</em></p>
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
    print("🔌 NH Energy Rate Parser")
    print("=" * 50)
    
    # Parse the data
    suppliers = parse_energy_data()
    print(f"📊 Parsed {len(suppliers)} energy supplier plans")
    
    # Create comparison table
    df = create_comparison_table(suppliers)
    
    # Display the table
    print("\n📋 NEW HAMPSHIRE ENERGY RATE COMPARISON")
    print("=" * 80)
    print(df.to_string(index=False))
    
    # Save to files
    print(f"\n💾 Saving files...")
    csv_file, excel_file, html_file = save_comparison_files(df)
    
    # Show summary statistics
    rates = [float(rate.replace('$', '')) for rate in df['Rate ($/kWh)']]
    print(f"\n📈 SUMMARY STATISTICS")
    print("-" * 30)
    print(f"Lowest rate:  ${min(rates):.5f} per kWh")
    print(f"Highest rate: ${max(rates):.5f} per kWh")
    print(f"Average rate: ${sum(rates)/len(rates):.5f} per kWh")
    print(f"Rate spread:  ${max(rates) - min(rates):.5f} per kWh")
    print(f"Total plans:  {len(rates)}")
    
    # Find best deals
    renewable_plans = df[df['Renewable %'].astype(float) == 100]
    if not renewable_plans.empty:
        best_renewable = renewable_plans.iloc[0]
        print(f"\n🌱 Best 100% Renewable: {best_renewable['Plan Name']} at {best_renewable['Rate ($/kWh)']}")
    
    short_term = df[df['Term (Months)'].astype(str).isin(['3', '4', '6'])]
    if not short_term.empty:
        best_short = short_term.iloc[0]
        print(f"⚡ Best Short-term: {best_short['Plan Name']} at {best_short['Rate ($/kWh)']} ({best_short['Term (Months)']} months)")
    
    print(f"\n✅ Files created successfully!")
    print(f"   📄 Open {html_file} in your browser for the best viewing experience")

if __name__ == "__main__":
    main()
