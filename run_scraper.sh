#!/bin/bash
# ============================================================================
# Healthcare Market Rate Scraper - Quick Run Script
# ============================================================================
# 
# SCHEDULE: Run this on the 1st and 15th of each month
# 
# To set up Mac reminders, run:
#   ./setup_reminders.sh
#
# To run the scraper manually:
#   ./run_scraper.sh
#
# ============================================================================

echo "======================================================================"
echo "🏥 CareRev Healthcare Market Rate Scraper"
echo "======================================================================"
echo ""
echo "📅 SCHEDULE REMINDER:"
echo "   • Run on the 1ST of each month (100 credits)"
echo "   • Run on the 15TH of each month (100 credits)"
echo "   • Total: 200 credits = FREE tier"
echo ""

# Check if it's the 1st or 15th
DAY=$(date +%d)
if [ "$DAY" == "01" ] || [ "$DAY" == "15" ]; then
    echo "✅ Today is a scheduled run day!"
else
    echo "ℹ️  Today is the ${DAY}th. Next run dates:"
    echo "   • 1st of next month"
    echo "   • 15th of this/next month"
    echo ""
    read -p "Run anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""
echo "Starting scraper..."
echo ""

# Run the scraper
cd "$(dirname "$0")"
python3 run_healthcare_scraper.py

echo ""
echo "======================================================================"
echo "Done! Check the output/ folder for your Excel file."
echo "Copy it to your dashboard's data/ folder to update visualizations."
echo "======================================================================"
