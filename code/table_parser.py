#!/usr/bin/env python3
"""
Improved table parser for DOCUPIPE markdown tables
Extracts individual day menus from the table structure
"""

import re

def parse_markdown_table(text):
    """
    Parse a markdown table and extract menu items for each day.
    
    Expected structure:
    | Day | Lundi 1 | Mardi 2 | Mercredi 3 | ...
    | Entrée | item1 | item2 | item3 | ...
    | Plats | item1 | item2 | item3 | ...
    | Accompagnement | item1 | item2 | item3 | ...
    | Dessert | item1 | item2 | item3 | ...
    """
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
        # Remove empty first/last cells from split
        cells = [c for c in cells if c]
        
        if cells:
            rows.append(cells)
    
    if len(rows) < 2:
        return []
    
    # First row should have days
    day_row = rows[0]
    
    # Extract days with regex
    days_data = []
    for i, cell in enumerate(day_row):
        if i == 0:  # Skip first column (labels)
            continue
        day_match = re.search(r'(Lundi|Mardi|Mercredi|Jeudi|Vendredi)\s*(\d+)', cell)
        if day_match:
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
        for row in rows[1:]:  # Skip header row
            if len(row) <= col_idx:
                continue
            
            label = row[0].lower() if row else ''
            value = row[col_idx] if len(row) > col_idx else ''
            
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


# Test with sample data
if __name__ == "__main__":
    sample_text = """
|:---------------|:-------------------------------|:-------------------------------|:-----------------------------|:-----------------------------|
| Entrée | Betterave rouge | Carottes râpées | Salade de tomate séchées et mozzarella | Feuilleté au fromage |
| Plats | Steak haché Steak végétarien | Ravioli farci épinards crème de ciboulette | Supions à la provençale | Minute de bœuf au caramel de soja |
| Accompagnement | Penne sauce tomate | - | Riz complet | Haricots verts |
| Dessert | Sélection de notre affineur / Fruit du jour | Yaourt / Fruit du jour | Sélection de notre affineur / Mousse au chocolat | Yaourt / Fruit du jour |
"""
    
    # Note: This sample doesn't have the day header row, but shows the structure
    print("Testing parser...")
    menus = parse_markdown_table(sample_text)
    for menu in menus:
        print(menu)
