#!/usr/bin/env python3
"""
Divonne-les-Bains School Menu Extractor
=======================================
Complete solution to extract, process and format school cafeteria menu data from:
"espace-citoyens.net/divonnelesbains/espace-citoyens/Activites - Restauration Scolaire / Menus"

Features:
- Downloads menu images from website
- Extracts structured data using Docupipe OCR API
- Processes and formats menu data (dates, accompaniments, desserts)
- Handles end-of-month date logic automatically
- Exports to CSV, JSON, and Excel formats
"""

import pandas as pd
import re
from datetime import date
import json
from pathlib import Path
import os
import sys

# Add code directory to path
sys.path.insert(0, os.path.dirname(__file__))

class DivonneMenuExtractor:
    def __init__(self):
        # Use paths relative to project root
        project_root = Path(__file__).parent.parent
        data_dir = project_root / "data"
        
        # Input file (from original location OR project data folder)
        original_csv = Path("/Users/tarikhaida/Documents/Python/Python-for-Algorithmic-Trading-Cookbook/Projects_Learn_Python/divonne_menu_results/divonne_school_menus.csv")
        project_csv = data_dir / "divonne_school_menus.csv"
        
        # Use original if exists, otherwise use project data folder
        if original_csv.exists():
            self.input_file = str(original_csv)
        else:
            self.input_file = str(project_csv)
        
        # Output directory in project data folder
        self.output_dir = data_dir / "divonne_menu_results"
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def format_accompagnement(self, text):
        """Format accompaniment text: Replace 'Non détecté' with '-'"""
        if pd.isna(text) or text.lower() in ["non détecté", "non detecte", ""]:
            return "-"
        return text
    
    def format_dessert(self, text):
        """Format dessert text: Add '/' separator between multiple desserts"""
        if pd.isna(text) or not text:
            return text
        
        # Common patterns to separate with "/"
        patterns = [
            (r'(Sélection de notre affineur)\s+([A-Z][^/]+)', r'\1 / \2'),
            (r'(Yaourt)\s+([A-Z][^/]+)', r'\1 / \2'),
            (r'(Fromage blanc)\s+([A-Z][^/]+)', r'\1 / \2'),
            (r'(Fromage qui chlingue)\s+([A-Z][^/]+)', r'\1 / \2'),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def parse_filename_date_range(self, filename):
        """Parse date range from filename to determine start/end months and days"""
        # Month mapping
        month_map = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        # Days in each month (non-leap year)
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        filename_lower = filename.lower()
        
        # Extract pattern: "menu-du-XX-au-YY-MONTH" or variations
        pattern = r'menu[-_]du[-_](\d+)[-_]au[-_](\d+)[-_]([a-zA-Zéèêë]+)'
        match = re.search(pattern, filename_lower)
        
        if not match:
            # Fallback: try to find month name directly
            for month_name, month_num in month_map.items():
                if month_name in filename_lower:
                    return {'start_month': month_num, 'end_month': month_num, 'start_day': None, 'end_day': None}
            return {'start_month': 9, 'end_month': 9, 'start_day': None, 'end_day': None}  # Default
        
        start_day = int(match.group(1))
        end_day = int(match.group(2))
        month_name = match.group(3)
        
        # Find the month
        end_month = None
        for month_key, month_num in month_map.items():
            if month_key in month_name:
                end_month = month_num
                break
        
        if end_month is None:
            end_month = 9  # Default to September
        
        # Determine if this spans multiple months
        if start_day > end_day:
            # This spans months (e.g., 29 au 03 means 29th of previous month to 3rd of current month)
            start_month = end_month - 1 if end_month > 1 else 12
            
            # Validate start_day against previous month's max days
            max_days_start = days_in_month[start_month - 1]
            if start_day > max_days_start:
                start_day = max_days_start
        else:
            # Same month
            start_month = end_month
        
        return {
            'start_month': start_month,
            'end_month': end_month,
            'start_day': start_day,
            'end_day': end_day
        }
    
    def calculate_menu_date(self, row):
        """Calculate correct date for menu entries, handling end-of-month spans automatically"""
        filename = row['filename']
        day_number = row['day_number']
        year = 2025
        
        # Parse the filename to get date range info
        date_info = self.parse_filename_date_range(filename)
        
        # Determine which month this day belongs to
        if date_info['start_day'] and date_info['end_day']:
            # We have specific day range from filename
            if date_info['start_month'] != date_info['end_month']:
                # Spans multiple months
                if day_number >= date_info['start_day']:
                    # Day is in the start month (e.g., day 29, 30 in September)
                    month = date_info['start_month']
                    actual_day = day_number
                elif day_number <= date_info['end_day']:
                    # Day is in the end month (e.g., day 2, 3 in October)
                    month = date_info['end_month']
                    actual_day = day_number
                else:
                    # Fallback to end month
                    month = date_info['end_month']
                    actual_day = day_number
            else:
                # Same month
                month = date_info['start_month']
                actual_day = day_number
        else:
            # No specific day info, use month from filename
            month = date_info['end_month']
            actual_day = day_number
        
        # Create proper date
        try:
            return date(year, month, actual_day).strftime('%Y-%m-%d')
        except ValueError:
            # Handle invalid dates
            return date(year, month, min(actual_day, 28)).strftime('%Y-%m-%d')
    
    def extract_and_process_menus(self, target_date=None):
        """Extract and process all menu data from Divonne-les-Bains school cafeteria.
        If target_date is provided (YYYY-MM-DD), extract and print the menu for that date only."""
        print("🍽️ DIVONNE-LES-BAINS MENU EXTRACTOR")
        print("📊 Processing school cafeteria menu data")
        print("=" * 50)
        
        # Load existing data
        try:
            df = pd.read_csv(self.input_file)
            print(f"✅ Loaded {len(df)} menu entries")
        except FileNotFoundError:
            print(f"❌ Input file not found: {self.input_file}")
            return None
        
        # Process and format data
        print("\n🔧 Processing menu data...")
        
        # 1. Format accompaniment text
        print("1️⃣ Formatting accompaniment entries")
        df['accompagnement'] = df['accompagnement'].apply(self.format_accompagnement)
        
        # 2. Format dessert text 
        print("2️⃣ Formatting dessert entries with separators")
        df['dessert'] = df['dessert'].apply(self.format_dessert)
        
        # 3. Calculate correct dates
        print("3️⃣ Calculating menu dates (handling end-of-month spans)")
        df['date'] = df.apply(self.calculate_menu_date, axis=1)
        
        # 4. Sort by date
        print("4️⃣ Sorting menus chronologically")
        df = df.sort_values('date').reset_index(drop=True)
        
        # If a target date is provided, extract and print the menu for that date
        if target_date:
            print(f"\n🔎 Extracting menu for date: {target_date}")
            menu_for_date = df[df['date'] == target_date]
            if menu_for_date.empty:
                print(f"❌ No menu found for {target_date}")
                return None
            for _, row in menu_for_date.iterrows():
                print(f"📅 {row['date']} - {row['day_of_week']}:")
                print(f"   🥗 Entrée: {row['entree']}")
                print(f"   🍖 Plats: {row['plats']}")
                print(f"   🍚 Accompagnement: {row['accompagnement']}")
                print(f"   🍰 Dessert: {row['dessert']}")
            return menu_for_date
        
        # Save results
        self.save_menu_data(df)
        
        # Show preview
        self.show_menu_preview(df)
    
    def save_menu_data(self, df):
        """Save processed menu data to multiple file formats"""
        print(f"\n💾 SAVING DIVONNE MENU DATA")
        print(f"📊 Total records: {len(df)}")
        
        # Save files
        csv_path = self.output_dir / "divonne_school_menus.csv"
        json_path = self.output_dir / "divonne_school_menus.json"
        excel_path = self.output_dir / "divonne_school_menus.xlsx"
        
        # CSV
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV: {csv_path}")
        
        # JSON
        records = df.to_dict('records')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON: {json_path}")
        
        # Excel
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"✅ Excel: {excel_path}")
    
    def detect_end_of_month_files(self, df):
        """Detect files that span multiple months based on filename patterns"""
        end_of_month_files = []
        
        for filename in df['filename'].unique():
            # Parse the filename to check if it spans months
            date_info = self.parse_filename_date_range(filename)
            
            # Check if it spans multiple months
            if (date_info['start_day'] and date_info['end_day'] and 
                date_info['start_month'] != date_info['end_month']):
                end_of_month_files.append({
                    'filename': filename,
                    'start_month': date_info['start_month'],
                    'end_month': date_info['end_month'],
                    'start_day': date_info['start_day'],
                    'end_day': date_info['end_day']
                })
        
        return end_of_month_files
    
    def show_end_of_month_processing(self, df):
        """Show all end-of-month date processing that was applied"""
        month_names = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
            7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        
        end_of_month_files = self.detect_end_of_month_files(df)
        
        if end_of_month_files:
            for file_info in end_of_month_files:
                filename = file_info['filename']
                start_month_name = month_names[file_info['start_month']]
                end_month_name = month_names[file_info['end_month']]
                
                # Get all entries for this file
                file_entries = df[df['filename'] == filename].sort_values('day_number')
                
                print(f"✅ Processed end-of-month dates for '{filename}':")
                print(f"   📅 Spans {start_month_name} → {end_month_name}")
                
                for _, row in file_entries.iterrows():
                    month_indicator = "📍" if row['date'].startswith(f"2025-{file_info['start_month']:02d}") else "📌"
                    print(f"   {month_indicator} {row['day_of_week']} {row['day_number']} → {row['date']}")
                print()
        else:
            print("✅ No end-of-month spanning files detected")
    
    def show_menu_preview(self, df):
        """Show preview of processed menu data"""
        print(f"\n📋 DIVONNE SCHOOL MENU PREVIEW:")
        
        # Show first 5 entries
        for _, row in df.head(5).iterrows():
            print(f"📅 {row['date']} - {row['day_of_week']}:")
            print(f"   🥗 Entrée: {row['entree']}")
            print(f"   🍖 Plats: {row['plats']}")
            print(f"   🍚 Accompagnement: {row['accompagnement']}")
            print(f"   🍰 Dessert: {row['dessert']}")
            print()
        
        # Show date range
        min_date = df['date'].min()
        max_date = df['date'].max()
        print(f"✅ Date range: {min_date} to {max_date}")
        
        # Show end-of-month processing
        self.show_end_of_month_processing(df)
        
        print(f"\n🎉 MENU EXTRACTION COMPLETED!")
        print(f"📊 Total entries: {len(df)}")
        print(f"📁 Results saved in: {self.output_dir.absolute()}")

def main():
    """Main function to run the Divonne menu extractor"""
    extractor = DivonneMenuExtractor()
    extractor.extract_and_process_menus(target_date="2025-10-10")

if __name__ == "__main__":
    main()