import re
import pandas as pd
from datetime import datetime
import os
import json

def parse_all_energy_data():
    """
    Parse all the energy rate data from the complete fetched content including actual signup links
    """
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
    import time
    
    try:
        # Fetch the live data from NH.gov
        print("🌐 Fetching live data from NH Department of Energy using Playwright...")
        url = "https://www.energy.nh.gov/engyapps/ceps/ResidentialCompare.aspx?choice=Eversource"
        
        with sync_playwright() as p:
            # Launch browser - try Firefox as it often bypasses better
            print("🚀 Launching Firefox browser...")
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            
            print(f"📄 Navigating to {url}...")
            page.goto(url, wait_until="networkidle")
            
            # Wait for any potential challenges or loading
            time.sleep(5)
            
            content = page.content()
            browser.close()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the main data table - try specific class first
        # In the new format, there are multiple tables with this class, so finding one doesn't mean it's the "old big table"
        # The old format had a single large table containing all rows
        # The new format has many small tables, one per plan
        
        main_table = None
        data_table = None # Initialize for compatibility
        
        # Check if it's the old single-table format
        potential_table = soup.find('table', class_='tblcomparelist')
        if potential_table:
             # If it has many rows as direct children, it might be the old format
             # In new format, each table has ~5-6 rows
             rows = potential_table.find_all('tr')
             if len(rows) > 10: 
                 main_table = potential_table
        
        if not main_table:
            # Fallback: Search all tables for a large data table
            tables = soup.find_all('table')
            
            for table in tables:
                # Look for the table with energy rate data
                headers = table.find_all('th')
                if len(headers) > 5:  # Energy rate tables typically have many columns
                    header_text = ' '.join([th.get_text().strip() for th in headers]).lower()
                    if any(keyword in header_text for keyword in ['plan', 'supplier', 'rate', 'term', 'renewable']):
                        main_table = table
                        break
        
        suppliers = []
        
        if main_table:
            print("✓ Found energy rate table (Old Format), parsing data...")
            data_table = main_table
        else:
            # New Format Parsing
            print("✓ Checking for new card-based format...")
            # Each plan seems to be in its own table or tbody within a list
            # We'll look for the plan name spans to identify entries
            plan_name_elements = soup.find_all('span', class_='PlanName')
            
            if plan_name_elements:
                print(f"✓ Found {len(plan_name_elements)} plans in new format")
                
                for plan_span in plan_name_elements:
                    try:
                        # logical parent container for this plan (tbody)
                        # The span is inside a td, inside a tr, inside a tbody
                        plan_tbody = plan_span.find_parent('tbody')
                        if not plan_tbody:
                            continue
                            
                        # Extract textual data using the structure provided
                        
                        # Plan Name
                        plan_name = plan_span.get_text().strip()
                        
                        # Supplier Name (in the next row, class CompanyName)
                        supplier_elem = plan_tbody.find('td', class_='CompanyName')
                        supplier = supplier_elem.get_text().strip() if supplier_elem else "Unknown Supplier"
                        if not supplier: # Fallback if text is inside b tag
                             b_tag = supplier_elem.find('b') if supplier_elem else None
                             supplier = b_tag.get_text().strip() if b_tag else "Unknown Supplier"
                        # Clean up supplier name if it has "Pricing:" attached
                        if "Pricing:" in supplier:
                            supplier = supplier.split("Pricing:")[0].strip()

                        # Rate (Per KWh: $0.18590) - look for span with id containing lblKWh
                        rate_elem = plan_tbody.find('span', id=lambda x: x and 'lblKWh' in x)
                        rate_text = rate_elem.get_text().strip() if rate_elem else "0"
                        rate_value = float(re.sub(r'[^\d.]', '', rate_text)) if rate_text else 0.0

                        # Term Length (Rate Good for: 24 months)
                        term_elem = plan_tbody.find('td', class_='RateGoodFor')
                        term_text = term_elem.get_text().strip() if term_elem else "0"
                        # Extract the number of months
                        term_match = re.search(r'(\d+)', term_text)
                        term_months = term_match.group(1) if term_match else "0"

                        # Renewable (Renewable Energy: 0.00 %)
                        renewable_elem = plan_tbody.find('td', class_='RenewableEnergy')
                        renewable_text = renewable_elem.get_text().strip() if renewable_elem else "0"
                        # Extract the percentage number which might have decimals
                        renewable_pct = re.search(r'(\d+(?:\.\d+)?)', renewable_text)
                        renewable_pct = renewable_pct.group(1) if renewable_pct else "0"

                        # Cancellation Fee (Cancellation Fee: No)
                        cancel_elem = plan_tbody.find('td', class_='CancellationFee')
                        cancel_text = cancel_elem.get_text().strip() if cancel_elem else "No"
                        # Clean up "Cancellation Fee:" text label
                        cancel_fee = cancel_text.replace('Cancellation Fee:', '').strip()

                        # Phone
                        phone_elem = plan_tbody.find('td', class_='PhoneNumber')
                        phone = phone_elem.get_text().strip() if phone_elem else ""

                        # Links
                        signup_link = ""
                        learn_more_link = ""
                        
                        links = plan_tbody.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            link_text = link.get_text().strip().lower()
                            
                            if 'sign' in link_text:
                                signup_link = href
                            elif 'learn' in link_text:
                                learn_more_link = href
                        
                        # Fallback links
                        if not signup_link:
                             signup_link = "https://www.energy.nh.gov/consumers/choosing-energy-supplier"
                        if not learn_more_link:
                             learn_more_link = signup_link

                        suppliers.append({
                            'plan_name': plan_name,
                            'supplier': supplier,
                            'rate_per_kwh': rate_value,
                            'term_months': term_months,
                            'renewable_energy_pct': renewable_pct,
                            'cancellation_fee': cancel_fee,
                            'phone': phone,
                            'signup_link': f'<a href="{signup_link}" target="_blank">Sign up</a>',
                            'learn_more_link': f'<a href="{learn_more_link}" target="_blank">Learn more</a>'
                        })

                    except Exception as e:
                        print(f"⚠️Error parsing plan in new format: {e}")
                        continue

        if not suppliers and not data_table:
             print("⚠️  Could not find energy plans in either format.")
        
        if data_table and not suppliers: # If we found the old table but haven't parsed it yet (the old logic)
            print("✓ Found energy rate table, parsing data...")
            rows = data_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 6:  # Skip rows with insufficient data
                    continue
                
                try:
                    # Extract basic plan information
                    plan_name = cells[0].get_text().strip()
                    supplier = cells[1].get_text().strip()
                    
                    # Parse rate - handle different formats
                    rate_text = cells[2].get_text().strip()
                    rate_value = float(re.sub(r'[^\d.]', '', rate_text)) if rate_text else 0.0
                    
                    # Parse term
                    term_text = cells[3].get_text().strip()
                    term_months = re.sub(r'[^\d]', '', term_text) if term_text else "0"
                    
                    # Parse renewable percentage
                    renewable_text = cells[4].get_text().strip() if len(cells) > 4 else "0"
                    renewable_pct = re.sub(r'[^\d.]', '', renewable_text) if renewable_text else "0"
                    
                    # Parse cancellation fee
                    cancel_fee = cells[5].get_text().strip() if len(cells) > 5 else "No"
                    
                    # Parse phone number
                    phone = cells[6].get_text().strip() if len(cells) > 6 else ""
                    
                    # Extract actual signup links from the website
                    signup_link = ""
                    learn_more_link = ""
                    
                    # Look for links in the row
                    links = row.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        link_text = link.get_text().strip().lower()
                        
                        if href.startswith('http'):
                            if 'sign' in link_text or 'enroll' in link_text or 'join' in link_text:
                                signup_link = href
                            elif 'learn' in link_text or 'more' in link_text or 'info' in link_text:
                                learn_more_link = href
                            elif not signup_link:  # Use first link as signup if no specific signup link found
                                signup_link = href
                    
                    # If no links found in the row, look for supplier-specific patterns
                    if not signup_link:
                        # Use hardcoded links for known suppliers as fallback
                        supplier_lower = supplier.lower()
                        if "hillsborough" in supplier_lower:
                            signup_link = "http://www.standardpower.com/Communities/Hillsborough/"
                        elif "amherst" in supplier_lower:
                            signup_link = "http://www.standardpower.com/Communities/Amherst/"
                        elif "bennington" in supplier_lower:
                            signup_link = "http://www.standardpower.com/Communities/Bennington/"
                        elif "rollinsford" in supplier_lower:
                            signup_link = "http://www.standardpower.com/Communities/Rollinsford/"
                        elif "keene" in supplier_lower:
                            signup_link = "https://www.keenecommunitypower.org/"
                        elif "marlborough" in supplier_lower:
                            signup_link = "https://www.marlboroughnh.org/community-power"
                        elif "swanzey" in supplier_lower:
                            signup_link = "https://www.town.swanzey.nh.us/community-power"
                        elif "wilton" in supplier_lower:
                            signup_link = "https://www.wiltonnh.gov/community-power"
                        elif "jaffrey" in supplier_lower or "milford" in supplier_lower or "new boston" in supplier_lower:
                            signup_link = "https://www.cpcnh.org/"
                        elif "hampton" in supplier_lower:
                            signup_link = "https://www.hamptonnh.gov/community-power"
                        elif "ambit" in supplier_lower:
                            signup_link = "https://www.ambitenergy.com/"
                        elif "cleansky" in supplier_lower:
                            signup_link = "https://www.cleanskyenergy.com/"
                        elif "direct energy" in supplier_lower:
                            signup_link = "https://www.directenergy.com/"
                        elif "enh power" in supplier_lower:
                            signup_link = "https://enhpower.com/"
                        elif "xoom" in supplier_lower:
                            signup_link = "https://www.xoomenergy.com/"
                        elif "town square" in supplier_lower:
                            signup_link = "https://www.townsquareenergy.com/"
                        elif "think energy" in supplier_lower:
                            signup_link = "https://www.thinkenergy.com/"
                        elif "north american" in supplier_lower:
                            signup_link = "https://www.napower.com/"
                        elif "smartenergy" in supplier_lower:
                            signup_link = "https://www.smartenergy.com/"
                        elif "community power coalition" in supplier_lower:
                            signup_link = "https://www.cpcnh.org/"
                        elif "eversource" in supplier_lower:
                            signup_link = "https://www.eversource.com/"
                        else:
                            signup_link = "https://www.energy.nh.gov/consumers/choosing-energy-supplier"
                    
                    # Use signup link as learn more if no separate learn more link found
                    if not learn_more_link:
                        learn_more_link = signup_link
                    
                    suppliers.append({
                        'plan_name': plan_name,
                        'supplier': supplier,
                        'rate_per_kwh': rate_value,
                        'term_months': term_months,
                        'renewable_energy_pct': renewable_pct,
                        'cancellation_fee': cancel_fee,
                        'phone': phone,
                        'signup_link': f'<a href="{signup_link}" target="_blank">Sign up</a>',
                        'learn_more_link': f'<a href="{learn_more_link}" target="_blank">Learn more</a>'
                    })
                    
                except (ValueError, IndexError) as e:
                    print(f"⚠️  Skipping malformed row: {e}")
                    continue
            
            print(f"✓ Successfully parsed {len(suppliers)} energy plans from live data")
            
        elif not suppliers:
            print("⚠️  Could not find energy rate table, using fallback data...")
            # Fallback to hardcoded data with corrected links
            suppliers = get_fallback_data_with_real_links()
            
    except Exception as e:
        print(f"❌ Error fetching live data: {e}")
        print("⚠️  Using fallback data with real links...")
        suppliers = get_fallback_data_with_real_links()
    
    return suppliers

def get_fallback_data_with_real_links():
    """
    Fallback data with real signup links extracted from the original website
    """
    # Data with actual links from NH.gov website
    raw_entries = [
        ("Winter Break 24", "Ambit Energy", 0.18800, "24", "0.00", "No", "1-877-282-6248", "https://www.ambitenergy.com/"),
        ("Ultimate Perks 12", "Ambit Energy", 0.14250, "12", "0.00", "No", "1-877-282-6248", "https://www.ambitenergy.com/"),
        ("Winter Break 12", "Ambit Energy", 0.18500, "12", "0.00", "No", "1-877-282-6248", "https://www.ambitenergy.com/"),
        ("White Mountain Select 12 Month Term", "Ambit Energy", 0.13500, "12", "0.00", "No", "1-877-282-6248", "https://www.ambitenergy.com/"),
        ("Amherst BASIC", "Amherst Community Power", 0.08840, "6", "25.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Amherst/"),
        ("Amherst GREEN Default", "Amherst Community Power", 0.08880, "6", "26.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Amherst/"),
        ("Amherst GREEN 50%", "Amherst Community Power", 0.10300, "6", "50.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Amherst/"),
        ("Amherst GREEN 100%", "Amherst Community Power", 0.11950, "6", "100.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Amherst/"),
        ("Bennington GREEN Default", "Bennington Community Power", 0.08860, "6", "26.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Bennington/"),
        ("Bennington GREEN 50%", "Bennington Community Power", 0.10280, "6", "50.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Bennington/"),
        ("Bennington GREEN 100%", "Bennington Community Power", 0.11930, "6", "100.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Bennington/"),
        ("Bennington BASIC", "Bennington Community Power", 0.08820, "6", "25.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Bennington/"),
        ("Embrace Green 6", "CleanSky Energy", 0.13490, "6", "100.00", "$50.00", "1-888-355-6205", "https://www.cleanskyenergy.com/"),
        ("Ultra Clean Solar 24", "CleanSky Energy", 0.12790, "24", "100.00", "$150.00", "1-888-355-6205", "https://www.cleanskyenergy.com/"),
        ("Embrace Green 12", "CleanSky Energy", 0.12990, "12", "100.00", "$75.00", "1-888-355-6205", "https://www.cleanskyenergy.com/"),
        ("Embrace Green 24", "CleanSky Energy", 0.12490, "24", "100.00", "$150.00", "1-888-355-6205", "https://www.cleanskyenergy.com/"),
        ("Affordable Wind 12", "CleanSky Energy", 0.13190, "12", "100.00", "$75.00", "1-888-355-6205", "https://www.cleanskyenergy.com/"),
        ("Clean 100 - Residential", "Community Power Coalition of NH", 0.16819, "6", "100.00", "No", "1-866-603-7697", "https://www.cpcnh.org/"),
        ("Granite Basic - Residential", "Community Power Coalition of NH", 0.13419, "6", "25.20", "No", "1-866-603-7697", "https://www.cpcnh.org/"),
        ("Canterbury Basic - Residential", "Community Power Coalition of NH", 0.13619, "6", "25.20", "No", "1-866-603-7697", "https://www.cpcnh.org/"),
        ("Enfield Local - Residential", "Community Power Coalition of NH", 0.13619, "6", "25.20", "No", "1-866-603-7697", "https://www.cpcnh.org/"),
        ("Peterborough Local - Residential", "Community Power Coalition of NH", 0.13995, "6", "25.20", "No", "1-866-603-7697", "https://www.cpcnh.org/"),
        ("Granite Plus - Residential", "Community Power Coalition of NH", 0.14119, "6", "33.00", "No", "1-866-603-7697", "https://www.cpcnh.org/"),
        ("Clean 50 - Residential", "Community Power Coalition of NH", 0.14819, "6", "50.00", "No", "1-866-603-7697", "https://www.cpcnh.org/"),
        ("Live Brighter AE 15", "Direct Energy Services, LLC", 0.11790, "15", "0.00", "No", "888-836-6141", "https://www.directenergy.com/"),
        ("Live Brighter SS 12", "Direct Energy Services, LLC", 0.12090, "12", "0.00", "No", "888-836-6141", "https://www.directenergy.com/"),
        ("Go Green Lights 24", "Direct Energy Services, LLC", 0.13390, "24", "100.00", "No", "888-836-6141", "https://www.directenergy.com/"),
        ("Live Brighter 15", "Direct Energy Services, LLC", 0.12290, "15", "0.00", "No", "888-836-6141", "https://www.directenergy.com/"),
        ("Live Brighter AE 12", "Direct Energy Services, LLC", 0.12690, "12", "0.00", "No", "888-836-6141", "https://www.directenergy.com/"),
        ("Live Brighter TO 15", "Direct Energy Services, LLC", 0.11690, "15", "0.00", "No", "888-836-6141", "https://www.directenergy.com/"),
        ("Live Brighter 24", "Direct Energy Services, LLC", 0.12890, "24", "0.00", "No", "888-836-6141", "https://www.directenergy.com/"),
        ("Easy Choice 3 - Residential", "ENH Power", 0.08890, "3", "0.00", "No", "1-833-488-3147", "https://enhpower.com/"),
        ("Simple Power 12 - Residential", "ENH Power", 0.11790, "12", "0.00", "$100.00", "1-833-488-3147", "https://enhpower.com/"),
        ("Optional Green 100", "Hampton Community Power Aggregation", 0.12918, "4", "100.00", "No", "1-866-485-5858", "https://www.hamptonnh.gov/community-power"),
        ("Optional Green 33", "Hampton Community Power Aggregation", 0.10798, "4", "57.30", "No", "1-866-485-5858", "https://www.hamptonnh.gov/community-power"),
        ("Standard", "Hampton Community Power Aggregation", 0.09425, "4", "24.30", "No", "1-866-485-5858", "https://www.hamptonnh.gov/community-power"),
        ("Hillsborough GREEN Default", "Hillsborough Community Power", 0.08850, "7", "26.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Hillsborough/"),
        ("Hillsborough GREEN 50%", "Hillsborough Community Power", 0.10270, "7", "50.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Hillsborough/"),
        ("Hillsborough GREEN 100%", "Hillsborough Community Power", 0.11920, "7", "100.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Hillsborough/"),
        ("Hillsborough BASIC", "Hillsborough Community Power", 0.08810, "7", "25.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Hillsborough/"),
        ("Jaffrey BASIC", "Jaffrey Community Power", 0.10568, "20", "24.30", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("Jaffrey GREEN 50%", "Jaffrey Community Power", 0.11648, "20", "50.00", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("Jaffrey GREEN Default", "Jaffrey Community Power", 0.10968, "20", "34.30", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("Jaffrey GREEN 100%", "Jaffrey Community Power", 0.13648, "20", "100.00", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("Keene 100% Local Green", "Keene Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065", "https://www.keenecommunitypower.org/"),
        ("Keene Basic", "Keene Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065", "https://www.keenecommunitypower.org/"),
        ("Keene 50% Local Green", "Keene Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065", "https://www.keenecommunitypower.org/"),
        ("Keene Local Green", "Keene Community Power", 0.11470, "30", "33.40", "No", "1-866-968-8065", "https://www.keenecommunitypower.org/"),
        ("Marlborough Basic", "Marlborough Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065", "https://www.marlboroughnh.org/community-power"),
        ("Marlborough 50", "Marlborough Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065", "https://www.marlboroughnh.org/community-power"),
        ("Marlborough Standard", "Marlborough Community Power", 0.11471, "30", "33.40", "No", "1-866-968-8065", "https://www.marlboroughnh.org/community-power"),
        ("Marlborough 100", "Marlborough Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065", "https://www.marlboroughnh.org/community-power"),
        ("Milford PLUS 10%", "Milford Community Power", 0.10968, "20", "34.30", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("Milford GREEN 100%", "Milford Community Power", 0.13648, "20", "100.00", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("Milford GREEN 50%", "Milford Community Power", 0.11648, "20", "50.00", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("Milford DEFAULT", "Milford Community Power", 0.10568, "20", "24.30", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("New Boston GREEN Default", "New Boston Community Power", 0.10968, "20", "34.30", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("New Boston GREEN 50%", "New Boston Community Power", 0.11648, "20", "50.00", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("New Boston BASIC", "New Boston Community Power", 0.10568, "20", "24.30", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("New Boston GREEN 100%", "New Boston Community Power", 0.13648, "20", "100.00", "No", "1-888-875-1711", "https://www.cpcnh.org/"),
        ("14 Month Renewable Fixed", "North American Power & Gas, LLC", 0.13940, "14", "100.00", "$10.00", "877-572-9965", "https://www.napower.com/"),
        ("14 Month Standard Fixed", "North American Power & Gas, LLC", 0.12990, "14", "0.00", "$10.00", "877-572-9965", "https://www.napower.com/"),
        ("12 Month Standard Fixed", "North American Power & Gas, LLC", 0.12790, "12", "0.00", "$10.00", "877-572-9965", "https://www.napower.com/"),
        ("Rollinsford BASIC", "Rollinsford Community Power", 0.08840, "7", "25.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Rollinsford/"),
        ("Rollinsford GREEN 100%", "Rollinsford Community Power", 0.11950, "7", "100.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Rollinsford/"),
        ("Rollinsford GREEN 50%", "Rollinsford Community Power", 0.10300, "7", "50.00", "No", "866-968-8065", "http://www.standardpower.com/Communities/Rollinsford/"),
        ("Rollinsford GREEN Default", "Rollinsford Community Power", 0.08880, "7", "26.20", "No", "866-968-8065", "http://www.standardpower.com/Communities/Rollinsford/"),
        ("SmartEnergy - Web Only Rate", "SmartEnergy", 0.10890, "4", "100.00", "No", "1-800-760-1207", "https://www.smartenergy.com/"),
        ("Swanzey 100", "Swanzey Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065", "https://www.town.swanzey.nh.us/community-power"),
        ("Swanzey Basic", "Swanzey Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065", "https://www.town.swanzey.nh.us/community-power"),
        ("Swanzey Standard", "Swanzey Community Power", 0.11471, "30", "33.40", "No", "1-866-968-8065", "https://www.town.swanzey.nh.us/community-power"),
        ("Swanzey 50", "Swanzey Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065", "https://www.town.swanzey.nh.us/community-power"),
        ("Think Clean 12", "Think Energy", 0.11900, "12", "100.00", "No", "1-833-669-3080", "https://www.thinkenergy.com/"),
        ("Think Clean 36", "Think Energy", 0.12500, "36", "100.00", "No", "1-833-669-3080", "https://www.thinkenergy.com/"),
        ("Think Basic 4", "Think Energy", 0.09900, "4", "0.00", "No", "1-833-669-3080", "https://www.thinkenergy.com/"),
        ("Power Your Tomorrow Fixed - 18", "Town Square Energy", 0.11870, "18", "0.00", "No", "1-877-430-0093", "https://www.townsquareenergy.com/"),
        ("Power Your Tomorrow Variable - 1", "Town Square Energy", 0.08890, "1", "0.00", "No", "1-877-430-0093", "https://www.townsquareenergy.com/"),
        ("Power Your Today Fixed - 4", "Town Square Energy", 0.09770, "4", "0.00", "No", "1-877-430-0093", "https://www.townsquareenergy.com/"),
        ("Power Your Tomorrow Fixed - 4", "Town Square Energy", 0.12000, "4", "0.00", "$50.00", "1-877-430-0093", "https://www.townsquareenergy.com/"),
        ("Power Your Tomorrow - 4 Green", "Town Square Energy", 0.14740, "4", "100.00", "$50.00", "1-877-430-0093", "https://www.townsquareenergy.com/"),
        ("Power Your Tomorrow Variable - 1 Green", "Town Square Energy", 0.09890, "1", "100.00", "No", "1-877-430-0093", "https://www.townsquareenergy.com/"),
        ("Power Your Tomorrow Fixed - 12", "Town Square Energy", 0.11770, "12", "0.00", "No", "1-877-430-0093", "https://www.townsquareenergy.com/"),
        ("Wilton 100", "Wilton Community Power", 0.13900, "30", "100.00", "No", "1-866-968-8065", "https://www.wiltonnh.gov/community-power"),
        ("Wilton Basic", "Wilton Community Power", 0.11100, "30", "23.40", "No", "1-866-968-8065", "https://www.wiltonnh.gov/community-power"),
        ("Wilton 50", "Wilton Community Power", 0.12050, "30", "50.00", "No", "1-866-968-8065", "https://www.wiltonnh.gov/community-power"),
        ("Wilton Standard", "Wilton Community Power", 0.11471, "30", "33.40", "No", "1-866-968-8065", "https://www.wiltonnh.gov/community-power"),
        ("SureLock 12 - Residential", "XOOM Energy New Hampshire, LLC", 0.13090, "12", "0.00", "$110.00", "1-888-997-8979", "https://www.xoomenergy.com/"),
        ("SimpleClean12 - Residential", "XOOM Energy New Hampshire, LLC", 0.13290, "12", "50.00", "$110.00", "1-888-997-8979", "https://www.xoomenergy.com/"),
        ("RescueLock 12", "XOOM Energy New Hampshire, LLC", 0.13790, "12", "0.00", "$110.00", "1-888-997-8979", "https://www.xoomenergy.com/"),
        ("SimpleClean", "XOOM Energy New Hampshire, LLC", 0.16490, "1", "50.00", "No", "1-888-997-8979", "https://www.xoomenergy.com/"),
        ("SureLock 24", "XOOM Energy New Hampshire, LLC", 0.13190, "24", "0.00", "$200.00", "1-888-997-8979", "https://www.xoomenergy.com/"),
        ("Eversource Default", "Eversource", 0.11196, "6", "23.40", "No", "1-800-662-7764", "https://www.eversource.com/")
    ]
    
    suppliers = []
    for entry in raw_entries:
        signup_link = entry[7] if len(entry) > 7 else "https://www.energy.nh.gov/consumers/choosing-energy-supplier"
        
        suppliers.append({
            'plan_name': entry[0],
            'supplier': entry[1],
            'rate_per_kwh': entry[2],
            'term_months': entry[3],
            'renewable_energy_pct': entry[4],
            'cancellation_fee': entry[5],
            'phone': entry[6],
            'signup_link': f'<a href="{signup_link}" target="_blank">Sign up</a>',
            'learn_more_link': f'<a href="{signup_link}" target="_blank">Learn more</a>'
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
                     'renewable_energy_pct', 'cancellation_fee', 'phone', 'signup_link', 'learn_more_link']].copy()
    
    # Rename columns
    display_df.columns = ['Plan Name', 'Supplier', 'Rate ($/kWh)', 'Term (Months)', 
                          'Renewable %', 'Cancel Fee', 'Phone', 'Signup Link', 'Learn More Link']
    
    # Format the rate column
    display_df['Rate ($/kWh)'] = display_df['Rate ($/kWh)'].apply(lambda x: f"${x:.5f}")
    
    return display_df

def save_comparison_files(df):
    """
    Save the comparison to multiple file formats with simple, static names for client-side consumption
    """
    # Use simple, static filenames that client-side code can reliably access
    
    # Create output directories
    base_output_dir = "outputs"
    csv_dir = os.path.join(base_output_dir, "csv")
    excel_dir = os.path.join(base_output_dir, "excel")
    html_dir = os.path.join(base_output_dir, "html")
    json_dir = os.path.join(base_output_dir, "json")
    
    # Create directories if they don't exist
    for directory in [base_output_dir, csv_dir, excel_dir, html_dir, json_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Save to CSV with simple name
    csv_file = os.path.join(csv_dir, "energy_rates.csv")
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved to {csv_file}")
    
    # Save to Excel with simple name
    excel_file = os.path.join(excel_dir, "energy_rates.xlsx")
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
    
    # Save to JSON for easy JavaScript/PyScript consumption
    json_file = os.path.join(json_dir, "energy_rates.json")
    
    # Create enhanced JSON structure with both formatted links and raw URLs
    json_records = []
    for _, row in df.iterrows():
        # Extract raw URLs from the HTML links
        signup_html = row['Signup Link']
        learn_more_html = row['Learn More Link']
        
        # Extract URLs using regex
        signup_url_match = re.search(r'href="([^"]*)"', signup_html)
        learn_more_url_match = re.search(r'href="([^"]*)"', learn_more_html)
        
        signup_url = signup_url_match.group(1) if signup_url_match else ""
        learn_more_url = learn_more_url_match.group(1) if learn_more_url_match else ""
        
        record = {
            "Plan Name": row['Plan Name'],
            "Supplier": row['Supplier'],
            "Rate ($/kWh)": row['Rate ($/kWh)'],
            "Term (Months)": row['Term (Months)'],
            "Renewable %": row['Renewable %'],
            "Cancel Fee": row['Cancel Fee'],
            "Phone": row['Phone'],
            "Signup Link": signup_html,  # Formatted HTML for display
            "Learn More Link": learn_more_html,  # Formatted HTML for display
            "Signup URL": signup_url,  # Raw URL for programmatic access
            "Learn More URL": learn_more_url  # Raw URL for programmatic access
        }
        json_records.append(record)
    
    json_data = {
        "last_updated": datetime.now().isoformat(),
        "total_plans": len(df),
        "data": json_records
    }
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to {json_file}")
    
    # Create an enhanced HTML file with simple name
    html_file = os.path.join(html_dir, "energy_rates.html")
    
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
                text-align: center;
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
                cursor: pointer;
                user-select: none;
                transition: background-color 0.3s;
            }}
            th:hover {{
                background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
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
                center-align: center;
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
        html_content += """
        <div class="legend">
                <div class="legend-section">
                    <div class="highlight-title">💰 Rate Categories</div>
                    <span class="legend-item rate-excellent">Excellent (≤$0.09)</span>
                    <span class="legend-item rate-good">Good ($0.09-$0.11)</span>
                    <span class="legend-item rate-average">Average ($0.11-$0.13)</span>
                    <span class="legend-item rate-expensive">Expensive (>$0.13)</span>
                </div>
                <div class="legend-section">
                    <div class="highlight-title">🌱 Renewable Energy</div>
                    <span class="legend-item renewable-100">100% Renewable</span>
                    <span class="legend-item renewable-high">≥50% Renewable</span>
                    <span class="legend-item renewable-medium">≥25% Renewable</span>
                </div>
            </div>"""
    
    # Generate table HTML with enhanced color coding and sortable functionality
    html_content += '''
    <div class="table-container">
        <table id="energyTable">
            <thead>
                <tr>'''
    
    for idx, col in enumerate(df.columns):
        html_content += f'<th class="sortable" onclick="sortTable({idx})">{col}<span> ↕️</span></th>'
    
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
    
    html_content += f"""
            </tbody>
        </table>
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
        
        <script>
        let sortDirections = {{}};
        
        function sortTable(columnIndex) {{
            const table = document.getElementById('energyTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Determine sort direction
            const currentDirection = sortDirections[columnIndex] || 'asc';
            const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
            sortDirections[columnIndex] = newDirection;
            
            // Update header indicators
            table.querySelectorAll('th').forEach((th, index) => {{
                const span = th.querySelector('span');
                if (span) {{
                    if (index === columnIndex) {{
                        span.textContent = newDirection === 'asc' ? ' ↑' : ' ↓';
                    }} else {{
                        span.textContent = ' ↕️';
                    }}
                }}
            }});
            
            // Sort rows
            rows.sort((a, b) => {{
                const aText = a.cells[columnIndex].textContent.trim();
                const bText = b.cells[columnIndex].textContent.trim();
                
                // Handle different data types based on column
                let aValue, bValue;
                
                if (columnIndex === 2) {{ // Rate ($/kWh) column
                    // Extract numeric value from rate (remove $ and convert)
                    aValue = parseFloat(aText.replace(/[$,]/g, '')) || 0;
                    bValue = parseFloat(bText.replace(/[$,]/g, '')) || 0;
                }} else if (columnIndex === 3) {{ // Term (Months) column
                    // Convert to number
                    aValue = parseInt(aText) || 0;
                    bValue = parseInt(bText) || 0;
                }} else if (columnIndex === 4) {{ // Renewable % column
                    // Extract percentage value
                    aValue = parseFloat(aText.replace(/%/g, '')) || 0;
                    bValue = parseFloat(bText.replace(/%/g, '')) || 0;
                }} else {{ // Text columns (Plan Name, Supplier, Cancel Fee, Phone, links)
                    aValue = aText.toLowerCase();
                    bValue = bText.toLowerCase();
                }}
                
                if (typeof aValue === 'number') {{
                    return newDirection === 'asc' ? aValue - bValue : bValue - aValue;
                }} else {{
                    if (newDirection === 'asc') {{
                        return aValue.localeCompare(bValue);
                    }} else {{
                        return bValue.localeCompare(aValue);
                    }}
                }}
            }});
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        }}
        </script>
        </script>
    </body>
    </html>
    """
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ Saved to {html_file}")
    
    return csv_file, excel_file, html_file, json_file

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
    csv_file, excel_file, html_file, json_file = save_comparison_files(df)
    
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
    print(f"   🔌 Use {json_file} for client-side JavaScript/PyScript consumption")

def get_live_energy_data():
    """
    PyScript-callable function that fetches live energy data and returns JSON
    """
    try:
        print("📡 Fetching live energy data from NH.gov...")
        
        # Get all the data
        df = parse_all_energy_data()
        
        if df.empty:
            print("❌ No data found")
            return {"error": "No data found", "data": []}
        
        # Convert to JSON format
        data_dict = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_plans": len(df),
            "data": df.to_dict('records')
        }
        
        print(f"✅ Successfully fetched {len(df)} energy plans")
        return data_dict
        
    except Exception as e:
        print(f"❌ Error fetching live data: {str(e)}")
        return {"error": str(e), "data": []}

if __name__ == "__main__":
    main()
