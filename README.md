# NH Energy Rates Comparison

Automated tool for comparing electricity rates in New Hampshire's Eversource territory.

## 🚀 Quick Start

### One-Time Setup

1. **Create GitHub Repository**
   ```bash
   # Create a new repository on GitHub (e.g., "nh-energy-rates")
   # Then connect your local folder:
   git remote add origin https://github.com/yourusername/nh-energy-rates.git
   ```

2. **Run Initial Setup**
   ```bash
   python auto_update_github.py
   ```

3. **Enable GitHub Pages**
   - Go to your repository Settings → Pages
   - Set Source to "Deploy from branch" 
   - Select `develop` branch
   - Your site will be available at: `https://yourusername.github.io/nh-energy-rates`

### Monthly Updates

**Option 1: Double-click the batch file (Windows)**
```
monthly_update.bat
```

**Option 2: Run Python script directly**
```bash
python auto_update_github.py
```

**Option 3: Manual generation**
```bash
python complete_energy_parser.py
```

## 📁 Generated Files

The script creates organized output files:

```
outputs/
├── csv/energy_rates.csv          # Spreadsheet data
├── excel/energy_rates.xlsx       # Excel workbook  
├── html/energy_rates.html        # Web page (main display)
└── json/energy_rates.json        # API-ready data
```

## 🔧 Features

- **Live Data**: Scrapes current rates from NH Department of Energy
- **Real Links**: Actual signup URLs for each energy supplier
- **Sortable Table**: Click column headers to sort by any field
- **Mobile Friendly**: Responsive design works on all devices
- **Multiple Formats**: CSV, Excel, HTML, and JSON outputs
- **Auto-Git**: Automatically commits and pushes updates to GitHub

## 🏆 Rate Categories

- **🟢 Excellent**: ≤ $0.09/kWh
- **🔵 Good**: $0.09 - $0.11/kWh  
- **🟡 Average**: $0.11 - $0.13/kWh
- **🔴 Expensive**: > $0.13/kWh

## 🌱 Renewable Energy

- **🌿 100% Renewable**: Fully clean energy
- **⚡ 50%+ Renewable**: Majority clean energy
- **🔋 25%+ Renewable**: Partial clean energy

## 📊 Data Sources

- Primary: [NH Department of Energy](https://www.energy.nh.gov/engyapps/ceps/ResidentialCompare.aspx?choice=Eversource)
- Backup: Curated database with real supplier links

## 🤖 Automation Options

### GitHub Actions (Recommended for Hands-off Updates)

Create `.github/workflows/monthly-update.yml`:

```yaml
name: Monthly Energy Rate Update

on:
  schedule:
    - cron: '0 9 1 * *'  # Run at 9 AM on the 1st of every month
  workflow_dispatch:      # Allow manual triggers

jobs:
  update-rates:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install pandas openpyxl requests beautifulsoup4
    - name: Generate updated data
      run: python complete_energy_parser.py
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add .
        git commit -m "Auto-update energy rates - $(date)" || exit 0
        git push
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Monthly, 1st of month
4. Set action: Start program `monthly_update.bat`

## 📱 Mobile Access

The generated site is fully responsive and works great on phones/tablets for checking rates on the go.

## 🔍 Advanced Usage

### Custom Data Processing

```python
from complete_energy_parser import parse_all_energy_data
import pandas as pd

# Get raw data
suppliers = parse_all_energy_data()
df = pd.DataFrame(suppliers)

# Custom analysis
renewable_only = df[df['renewable_energy_pct'].astype(float) >= 100]
print(f"Found {len(renewable_only)} 100% renewable plans")
```

### API Integration

Use the JSON output for building apps:

```javascript
fetch('outputs/json/energy_rates.json')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total_plans} energy plans`);
    console.log(`Last updated: ${data.last_updated}`);
  });
```

## 🛠️ Dependencies

- Python 3.7+
- pandas
- openpyxl  
- requests
- beautifulsoup4

## 📞 Support

This tool is for informational purposes only. Always verify rates and terms directly with energy suppliers before enrolling.

---

⚡ **Save money, save the planet!** Compare rates regularly to find the best deal for your home.
