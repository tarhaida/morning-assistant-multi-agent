#!/usr/bin/env python3
"""
Enhanced Docupipe Menu Extractor with fixes
==========================================
- Replace "Non détecté" with "-"
- Add "/" between desserts
- Fix end-of-month date parsing
- Sort by date
"""

import os
import sys
import json
import time
import base64
import requests
import pandas as pd
import re
from datetime import datetime, date
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class EnhancedMenuExtractor:
    def __init__(self, image_folder=None, output_folder=None):
        """Initialize DOCUPIPE extractor with project paths"""
        self.api_key = os.getenv('API_KEY_DOCUPIPE')
        if not self.api_key:
            raise ValueError("❌ API_KEY_DOCUPIPE not found in .env file")
        
        self.base_url = "https://app.docupipe.ai"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-Key": self.api_key
        }
        
        # Use project structure paths
        project_root = Path(__file__).parent.parent
        data_dir = project_root / "data"
        
        # Image folder (where simple_menu_checker downloads images)
        if image_folder is None:
            self.image_folder = data_dir / "final_menu_download"
        else:
            self.image_folder = Path(image_folder)
        
        # Results directory (where CSV is saved)
        if output_folder is None:
            self.results_dir = data_dir / "divonne_menu_results"
        else:
            self.results_dir = Path(output_folder)
        
        self.results_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"[DOCUPIPE] Image folder: {self.image_folder}")
        print(f"[DOCUPIPE] Output folder: {self.results_dir}")
    
    def upload_document(self, image_path):
        """Upload document to Docupipe API"""
        print(f"📤 Uploading: {os.path.basename(image_path)}")
        
        # Encode image to base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Upload to Docupipe - correct API structure
        url = f"{self.base_url}/document"
        payload = {
            "document": {
                "file": {
                    "contents": image_data,
                    "filename": os.path.basename(image_path)
                }
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        result = response.json()
        return result['documentId'], result['jobId']
    
    def wait_for_processing(self, job_id, document_id, max_wait=60):
        """Wait for document processing to complete by polling jobId"""
        print("   ⏳ Processing...")
        
        url = f"{self.base_url}/job/{job_id}"
        
        wait_seconds = 2
        for i in range(max_wait // wait_seconds):
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            status = data.get('status')
            
            if status == 'completed':
                # Now get the document results
                doc_url = f"{self.base_url}/document/{document_id}"
                doc_response = requests.get(doc_url, headers=self.headers)
                doc_response.raise_for_status()
                return doc_response.json()
            elif status == 'failed':
                raise Exception(f"❌ Processing failed: {data.get('error', 'Unknown error')}")
            
            time.sleep(wait_seconds)
            # Exponential backoff
            wait_seconds = min(wait_seconds * 1.5, 10)
        
        raise Exception("⏰ Processing timeout")
    
    def parse_filename_dates(self, filename):
        """Parse date range from filename and return month info"""
        # Extract date patterns from filename
        filename_lower = filename.lower()
        
        # Handle different filename patterns
        if "29-au-03-octobre" in filename_lower:
            # Special case: spans September to October
            return {"start_month": 9, "end_month": 10, "year": 2025}
        elif "septembre" in filename_lower:
            return {"start_month": 9, "end_month": 9, "year": 2025}
        elif "octobre" in filename_lower:
            return {"start_month": 10, "end_month": 10, "year": 2025}
        
        # Default fallback
        return {"start_month": 9, "end_month": 9, "year": 2025}
    
    def fix_date_logic(self, filename, day_number):
        """Fix date logic for end-of-month spans"""
        date_info = self.parse_filename_dates(filename)
        
        # Special handling for "29-au-03-Octobre" (spans Sept-Oct)
        if "29-au-03-octobre" in filename.lower():
            if day_number <= 30:  # Days 29, 30 are September
                month = 9
            else:  # Days 2, 3 are October (offset by 30)
                month = 10
                day_number = day_number - 30
        else:
            month = date_info["start_month"]
        
        year = date_info["year"]
        
        # Create date object
        try:
            return date(year, month, day_number)
        except ValueError:
            # Handle invalid dates (like day 31 in a 30-day month)
            print(f"⚠️ Invalid date: {year}-{month:02d}-{day_number:02d}, using approximation")
            return date(year, month, min(day_number, 28))
    
    def clean_text(self, text):
        """Clean text by removing asterisks and normalizing"""
        if not text:
            return ""
        
        # Remove asterisks
        text = re.sub(r'\*+', '', text)
        
        # Clean up extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def format_dessert(self, dessert_text):
        """Format dessert text with proper separators"""
        if not dessert_text:
            return ""
        
        # Common dessert patterns to separate with "/"
        patterns = [
            r'(Sélection de notre affineur)\s+(.*)',
            r'(Yaourt)\s+(.*)',
            r'(Fromage blanc)\s+(.*)',
            r'(Fromage qui chlingue)\s+(.*)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, dessert_text, re.IGNORECASE)
            if match:
                return f"{match.group(1)} / {match.group(2)}"
        
        # For other combinations, look for multiple desserts
        desserts = []
        words = dessert_text.split()
        
        # Common dessert indicators
        dessert_indicators = ['sélection', 'yaourt', 'fromage', 'fruit', 'compote', 'mousse', 'cake', 'cookies']
        
        current_dessert = []
        for word in words:
            if word.lower() in dessert_indicators and current_dessert:
                # Start of new dessert
                desserts.append(' '.join(current_dessert))
                current_dessert = [word]
            else:
                current_dessert.append(word)
        
        if current_dessert:
            desserts.append(' '.join(current_dessert))
        
        if len(desserts) > 1:
            return ' / '.join(desserts)
        
        return dessert_text
    
    def parse_markdown_table(self, text):
        """Parse markdown table and extract menu items for each day"""
        lines = text.strip().split('\n')
        
        # Find table lines (start with |)
        table_lines = [line for line in lines if line.strip().startswith('|')]
        
        if len(table_lines) < 2:
            return []
        
        # Parse each row by splitting on |
        rows = []
        for line in table_lines:
            # Skip separator lines (:---|)
            if ':---' in line or '----' in line:
                continue
            
            # Split by | and clean
            cells = [cell.strip() for cell in line.split('|')]
            # Remove empty first/last cells
            cells = [c for c in cells if c]
            
            if cells:
                rows.append(cells)
        
        if len(rows) < 2:
            return []
        
        # Find day columns
        days_data = []
        for row in rows:
            for i, cell in enumerate(row):
                if i == 0:  # Skip label column
                    continue
                day_match = re.search(r'(Lundi|Mardi|Mercredi|Jeudi|Vendredi)\s*(\d+)', cell)
                if day_match and not any(d['column_index'] == i for d in days_data):
                    days_data.append({
                        'day_name': day_match.group(1),
                        'day_num': int(day_match.group(2)),
                        'column_index': i
                    })
        
        # Extract menu items for each day
        menus = []
        for day_info in days_data:
            col_idx = day_info['column_index']
            
            menu = {
                'day_of_week': day_info['day_name'],
                'day_number': day_info['day_num'],
                'entree': '',
                'plats': '',
                'accompagnement': '',
                'dessert': ''
            }
            
            # Extract items from each row
            for row in rows:
                if len(row) <= col_idx:
                    continue
                
                label = row[0].lower() if row else ''
                value = row[col_idx] if len(row) > col_idx else ''
                
                # Skip empty values and day headers
                if not value or re.search(r'(Lundi|Mardi|Mercredi|Jeudi|Vendredi)\s*\d+', value):
                    continue
                
                if 'entrée' in label or 'entree' in label:
                    menu['entree'] = value
                elif 'plat' in label:
                    menu['plats'] = value
                elif 'accompagnement' in label:
                    menu['accompagnement'] = value if value else '-'
                elif 'dessert' in label:
                    menu['dessert'] = value
            
            menus.append(menu)
        
        return menus
    
    def extract_table_data(self, doc_data, filename):
        """Extract menu data from Docupipe response"""
        menu_entries = []
        
        # New API structure: result.pages[].sections[] or result.text
        result = doc_data.get('result', {})
        
        # Try to get full text first
        full_text = result.get('text', '')
        
        if not full_text:
            print(f"   ⚠️ No text found in {filename}")
            return menu_entries
        
        print(f"   🎯 Found text content ({len(full_text)} chars)")
        
        # Parse markdown table
        menus = self.parse_markdown_table(full_text)
        
        if not menus:
            print(f"   ⚠️ Could not parse table from {filename}")
            return menu_entries
        
        print(f"   📅 Found {len(menus)} days")
        
        # Convert to entries with dates
        for menu in menus:
            menu_date = self.fix_date_logic(filename, menu['day_number'])
            
            # Clean and format data
            entree = self.clean_text(menu.get('entree', ''))
            plats = self.clean_text(menu.get('plats', ''))
            accompagnement = self.clean_text(menu.get('accompagnement', ''))
            if not accompagnement or accompagnement.lower() in ["non détecté", "non detecte"]:
                accompagnement = "-"
            
            dessert = self.format_dessert(self.clean_text(menu.get('dessert', '')))
            
            entry = {
                'filename': filename,
                'date': menu_date.strftime('%Y-%m-%d'),
                'day_of_week': menu['day_of_week'],
                'day_number': menu['day_number'],
                'entree': entree or "-",
                'plats': plats or "-",
                'accompagnement': accompagnement,
                'dessert': dessert or "-"
            }
            
            menu_entries.append(entry)
            print(f"   ✅ {menu['day_of_week']} {menu['day_number']}: {entree[:30]}...")
        
        return menu_entries
        
        return menu_entries
    
    def process_all_menus(self):
        """Process all menu images"""
        print("🍽️ ENHANCED DOCUPIPE MENU EXTRACTOR")
        print("📊 Fixed version with proper formatting")
        print("=" * 50)
        
        # Find all menu images - use the image_folder set in __init__
        menu_folder = self.image_folder
        image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
        menu_files = []
        
        print(f"[DOCUPIPE] Searching in: {menu_folder}")
        
        for ext in image_extensions:
            menu_files.extend(menu_folder.glob(f'*{ext}'))
        
        if not menu_files:
            print(f"❌ No menu files found in {menu_folder}!")
            return
        
        print(f"📄 Found {len(menu_files)} menu files\n")
        
        all_entries = []
        
        for i, menu_file in enumerate(menu_files, 1):
            print(f"[{i}/{len(menu_files)}] 🔍 Processing: {menu_file.name}")
            
            try:
                # Upload and process
                doc_id, job_id = self.upload_document(str(menu_file))
                doc_data = self.wait_for_processing(job_id, doc_id)
                
                # Extract data
                entries = self.extract_table_data(doc_data, menu_file.name)
                all_entries.extend(entries)
                
                # Rate limiting
                if i < len(menu_files):
                    print("   ⏱️ Waiting 3 seconds...")
                    time.sleep(3)
                
            except Exception as e:
                print(f"   ❌ Error processing {menu_file.name}: {e}")
        
        if not all_entries:
            print("❌ No menu data extracted!")
            return
        
        # 4. Sort by date
        all_entries.sort(key=lambda x: x['date'])
        
        # Save results
        self.save_results(all_entries)
        
        # Show preview
        self.show_preview(all_entries)
    
    def save_results(self, entries):
        """Save extracted data in multiple formats"""
        print(f"\n💾 SAVING ENHANCED MENU DATA")
        print(f"📊 Total records: {len(entries)}")
        
        # Convert to DataFrame
        df = pd.DataFrame(entries)
        
        # Save in different formats
        csv_path = self.results_dir / "enhanced_menu_data.csv"
        json_path = self.results_dir / "enhanced_menu_data.json"  
        excel_path = self.results_dir / "enhanced_menu_data.xlsx"
        
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV: {csv_path}")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON: {json_path}")
        
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"✅ Excel: {excel_path}")
    
    def show_preview(self, entries):
        """Show preview of extracted data"""
        print(f"\n📋 ENHANCED DATA PREVIEW:")
        
        for entry in entries[:5]:  # Show first 5 entries
            print(f"📅 {entry['date']} - {entry['day_of_week']}:")
            print(f"   🥗 Entrée: {entry['entree']}")
            print(f"   🍖 Plats: {entry['plats']}")
            print(f"   🍚 Accompagnement: {entry['accompagnement']}")
            print(f"   🍰 Dessert: {entry['dessert']}")
            print()
        
        print("🎉 ENHANCED EXTRACTION COMPLETED!")
        print(f"📊 Total menu entries: {len(entries)}")
        print(f"📁 Results saved in: {self.results_dir.absolute()}")

def main():
    try:
        extractor = EnhancedMenuExtractor()
        extractor.process_all_menus()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()