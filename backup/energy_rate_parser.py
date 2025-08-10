import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_and_parse_energy_rates(url):
    """
    Fetch and parse the energy rates from the NH energy comparison website
    """
    try:
        # Headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all text content
        text_content = soup.get_text()
        
        # Parse the energy supplier data
        suppliers = parse_supplier_data(text_content)
        
        return suppliers
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def parse_supplier_data(text_content):
    """
    Parse the supplier data from the raw text content
    """
    suppliers = []
    
    # Split text into lines and process
    lines = text_content.split('\n')
    
    # Look for patterns that indicate supplier information
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for rate information - pattern: "Plan Name Per KWh: $X.XXXXX"
        rate_match = re.search(r'(.+?)\s+Per KWh:\s*\$(\d+\.\d+)', line)
        if rate_match:
            plan_name = rate_match.group(1).strip()
            rate = float(rate_match.group(2))
            
            # Look for additional information in subsequent lines
            supplier_info = {
                'plan_name': plan_name,
                'rate_per_kwh': rate,
                'supplier': '',
                'term_months': '',
                'renewable_energy_pct': '',
                'cancellation_fee': '',
                'monthly_charge': '',
                'phone': '',
                'last_update': '',
                'comments': ''
            }
            
            # Look ahead for more details
            j = i + 1
            while j < min(i + 10, len(lines)):  # Look at next 10 lines max
                next_line = lines[j].strip()
                
                # Extract supplier name (usually appears after rate)
                if not supplier_info['supplier'] and len(next_line) > 5 and 'Per KWh' not in next_line and '$' not in next_line:
                    # Check if this looks like a company name
                    if any(word in next_line.lower() for word in ['energy', 'power', 'electric', 'community', 'coalition']):
                        supplier_info['supplier'] = next_line
                
                # Extract term information
                term_match = re.search(r'Rate Good for:\s*(\d+)\s*months?', next_line)
                if term_match:
                    supplier_info['term_months'] = term_match.group(1)
                
                # Extract renewable energy percentage
                renewable_match = re.search(r'Renewable Energy:\s*(\d+\.?\d*)\s*%', next_line)
                if renewable_match:
                    supplier_info['renewable_energy_pct'] = renewable_match.group(1)
                
                # Extract cancellation fee
                cancel_match = re.search(r'Cancellation Fee:\s*\$?([^\s]+)', next_line)
                if cancel_match:
                    supplier_info['cancellation_fee'] = cancel_match.group(1)
                
                # Extract monthly charge
                monthly_match = re.search(r'Monthly Charge:\s*([^\s]+)', next_line)
                if monthly_match:
                    supplier_info['monthly_charge'] = monthly_match.group(1)
                
                # Extract phone number
                phone_match = re.search(r'(\d{1}-?\d{3}-?\d{3}-?\d{4})', next_line)
                if phone_match:
                    supplier_info['phone'] = phone_match.group(1)
                
                # Extract last update
                update_match = re.search(r'Last Update:\s*(\d+/\d+/\d+)', next_line)
                if update_match:
                    supplier_info['last_update'] = update_match.group(1)
                
                # Stop if we hit another rate entry
                if 'Per KWh:' in next_line and j > i + 1:
                    break
                
                j += 1
            
            suppliers.append(supplier_info)
        
        i += 1
    
    return suppliers

def create_rate_comparison_table(suppliers):
    """
    Create a clean comparison table of energy rates
    """
    if not suppliers:
        print("No supplier data found")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(suppliers)
    
    # Clean up the data
    df = df[df['rate_per_kwh'] > 0]  # Remove invalid rates
    
    # Sort by rate (lowest to highest)
    df = df.sort_values('rate_per_kwh')
    
    # Select and rename columns for display
    display_columns = [
        'plan_name', 'supplier', 'rate_per_kwh', 'term_months', 
        'renewable_energy_pct', 'cancellation_fee', 'monthly_charge', 'phone'
    ]
    
    df_display = df[display_columns].copy()
    df_display.columns = [
        'Plan Name', 'Supplier', 'Rate ($/kWh)', 'Term (Months)', 
        'Renewable %', 'Cancel Fee', 'Monthly Fee', 'Phone'
    ]
    
    # Format the rate column
    df_display['Rate ($/kWh)'] = df_display['Rate ($/kWh)'].apply(lambda x: f"${x:.5f}")
    
    return df_display

def save_to_files(df, filename_base="nh_energy_rates"):
    """
    Save the data to multiple formats
    """
    # Save to CSV
    csv_file = f"{filename_base}.csv"
    df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")
    
    # Save to Excel
    excel_file = f"{filename_base}.xlsx"
    df.to_excel(excel_file, index=False, sheet_name="Energy Rates")
    print(f"Data saved to {excel_file}")
    
    # Save to HTML for easy viewing
    html_file = f"{filename_base}.html"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NH Energy Rate Comparison</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            tr:hover {{ background-color: #e8f4fd; }}
            .rate-low {{ background-color: #d4edda; }}
            .rate-medium {{ background-color: #fff3cd; }}
            .rate-high {{ background-color: #f8d7da; }}
        </style>
    </head>
    <body>
        <h1>New Hampshire Energy Rate Comparison (Eversource Territory)</h1>
        <p>Data extracted and formatted from: <a href="https://www.energy.nh.gov/engyapps/ceps/ResidentialCompare.aspx?choice=Eversource">NH Energy Comparison Site</a></p>
        <p>Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        {df.to_html(escape=False, classes="table table-striped")}
    </body>
    </html>
    """
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Data saved to {html_file}")

def main():
    """
    Main function to run the energy rate parser
    """
    url = "https://www.energy.nh.gov/engyapps/ceps/ResidentialCompare.aspx?choice=Eversource"
    
    print("Fetching energy rate data from NH Energy website...")
    suppliers = fetch_and_parse_energy_rates(url)
    
    if suppliers:
        print(f"Found {len(suppliers)} supplier plans")
        
        # Create comparison table
        df = create_rate_comparison_table(suppliers)
        
        if df is not None and not df.empty:
            print("\n" + "="*100)
            print("NEW HAMPSHIRE ENERGY RATE COMPARISON (EVERSOURCE TERRITORY)")
            print("="*100)
            print(df.to_string(index=False))
            
            # Save to files
            print("\n" + "="*50)
            save_to_files(df)
            
            # Summary statistics
            rates = [float(rate.replace('$', '')) for rate in df['Rate ($/kWh)']]
            print(f"\nSUMMARY STATISTICS:")
            print(f"Lowest rate: ${min(rates):.5f} per kWh")
            print(f"Highest rate: ${max(rates):.5f} per kWh")
            print(f"Average rate: ${sum(rates)/len(rates):.5f} per kWh")
            print(f"Total plans available: {len(rates)}")
        else:
            print("No valid data found to display")
    else:
        print("Failed to extract supplier data")

if __name__ == "__main__":
    main()
