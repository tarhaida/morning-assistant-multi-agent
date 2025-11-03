"""
Nutrition Specialist Agent
Analyzes school cafeteria menus and provides nutritional insights.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Any
from datetime import datetime, date
from llm import get_llm
from utils import load_config
from prompt_builder import build_system_prompt_message
from custom_tools import check_menu_tool, get_menu_tool


class NutritionAgent:
    """Nutrition analysis specialist agent."""
    
    def __init__(self):
        """Initialize the nutrition agent."""
        self.config = load_config()
        self.agent_config = self.config['nutrition_agent']
        
        # Initialize LLM
        self.llm = get_llm(
            model_name=self.agent_config['llm'],
            temperature=self.agent_config['temperature']
        )
        
        # Build system prompt
        self.system_prompt = build_system_prompt_message(
            self.agent_config['prompt_config']
        )
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze today's school menu using complete pipeline.
        
        Returns:
            Dictionary with nutrition analysis
        """
        print(f"\n{'='*80}")
        print(f"[NutritionAgent] 🍽️ MENU ANALYSIS PIPELINE")
        print(f"{'='*80}")
        
        try:
            from pathlib import Path
            
            today = date.today().strftime('%Y-%m-%d')
            today_weekday = datetime.today().strftime('%A')
            print(f"\n[NutritionAgent] 📅 Date: {today} ({today_weekday})")
            
            # STEP 1: Web Scraping
            print(f"\n{'─'*80}")
            print(f"[NutritionAgent] STEP 1: WEB SCRAPING")
            print(f"{'─'*80}")
            if today_weekday == "Monday":
                print("[NutritionAgent] 🗓️  Monday detected - running scraper")
                result = check_menu_tool.invoke({})
                print(f"[NutritionAgent] Result: {result[:150]}...")
            else:
                print(f"[NutritionAgent] ⏭️  Not Monday - skip scrape")
            
            # STEP 2: Check Images
            print(f"\n{'─'*80}")
            print(f"[NutritionAgent] STEP 2: IMAGE CHECK")
            print(f"{'─'*80}")
            project_root = Path(__file__).parent.parent.parent
            image_folder = project_root / "data" / "final_menu_download"
            csv_path = project_root / "data" / "divonne_menu_results" / "divonne_school_menus.csv"
            
            if image_folder.exists():
                images = list(image_folder.glob("*.jpg")) + list(image_folder.glob("*.JPG"))
                print(f"[NutritionAgent] 📁 Folder: {image_folder}")
                print(f"[NutritionAgent] 📸 Images: {len(images)}")
                for img in images[:3]:
                    print(f"[NutritionAgent]    - {img.name}")
            else:
                print(f"[NutritionAgent] ❌ No image folder")
                images = []
            
            # STEP 3: Check CSV / DOCUPIPE OCR
            print(f"\n{'─'*80}")
            print(f"[NutritionAgent] STEP 3: CSV / DOCUPIPE OCR")
            print(f"{'─'*80}")
            print(f"[NutritionAgent] 📊 CSV: {csv_path}")
            print(f"[NutritionAgent] 📊 Exists: {csv_path.exists()}")
            
            if images and not csv_path.exists():
                print(f"[NutritionAgent] 🔍 Images found, no CSV - Running DOCUPIPE OCR")
                try:
                    # Import and run DOCUPIPE extractor
                    import docupipe_extractor
                    print(f"[NutritionAgent] 🤖 Initializing DOCUPIPE Extractor...")
                    extractor = docupipe_extractor.EnhancedMenuExtractor(
                        image_folder=image_folder,
                        output_folder=csv_path.parent
                    )
                    print(f"[NutritionAgent] 🚀 Processing images with DOCUPIPE API...")
                    extractor.process_all_menus()
                    print(f"[NutritionAgent] ✅ DOCUPIPE processing completed!")
                except Exception as e:
                    print(f"[NutritionAgent] ❌ DOCUPIPE Error: {e}")
                    import traceback
                    traceback.print_exc()
            elif not images:
                print(f"[NutritionAgent] ⚠️  No images found - cannot run DOCUPIPE")
            else:
                print(f"[NutritionAgent] ✅ CSV already exists - skipping DOCUPIPE")
            
            # STEP 4: Extract Menu
            print(f"\n{'─'*80}")
            print(f"[NutritionAgent] STEP 4: EXTRACT MENU")
            print(f"{'─'*80}")
            try:
                import menu_extractor
                extractor = menu_extractor.DivonneMenuExtractor()
                print(f"[NutritionAgent] 🔎 Searching for: {today}")
                menu_df = extractor.extract_and_process_menus(target_date=today)
                
                if menu_df is not None and not menu_df.empty:
                    row = menu_df.iloc[0]
                    print(f"[NutritionAgent] ✅ Found! {row['day_of_week']}")
                    menu_text = f"""
📅 {row['date']} - {row['day_of_week']}
🥗 Entrée: {row['entree']}
🍖 Plats: {row['plats']}
🥔 Accompagnement: {row['accompagnement']}
🍰 Dessert: {row['dessert']}
"""
                else:
                    print(f"[NutritionAgent] ⚠️  No menu for {today}")
                    menu_text = f"Aucun menu trouvé pour aujourd'hui ({today})"
            except ImportError:
                print(f"[NutritionAgent] ❌ menu_extractor import failed")
                menu_text = get_menu_tool.invoke({})
            
            # STEP 5: AI Analysis
            print(f"\n{'─'*80}")
            print(f"[NutritionAgent] STEP 5: AI NUTRITION ANALYSIS")
            print(f"{'─'*80}")
            
            # Create analysis prompt
            user_prompt = f"""
Analyze the following school cafeteria menu and provide nutritional insights:

TODAY'S MENU:
{menu_text}

Provide:
1. Brief nutritional assessment
2. Suggestions for balancing the evening meal
3. Any dietary notes for parents
"""
            
            print(f"[NutritionAgent] 🤖 Sending to LLM: {self.agent_config['llm']}")
            # Get LLM analysis
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            analysis = response.content if hasattr(response, 'content') else str(response)
            
            print(f"[NutritionAgent] ✅ Analysis received ({len(analysis)} chars)")
            print(f"{'='*80}\n")
            
            return {
                "success": True,
                "menu": menu_text,
                "analysis": analysis,
                "date": today
            }
            
        except Exception as e:
            print(f"[NutritionAgent] ❌ ERROR: {e}")
            print(f"{'='*80}\n")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "date": today if 'today' in locals() else "unknown"
            }


def nutrition_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for nutrition analysis.
    
    Args:
        state: Current state dictionary
        
    Returns:
        Updated state
    """
    agent = NutritionAgent()
    result = agent.analyze()
    
    # Update state
    state["menu_data"] = result
    state["menu"] = result.get("menu", "")
    state["nutrition_analysis"] = result.get("analysis", "")
    
    if not result.get("success"):
        state.setdefault("errors", []).append(f"Nutrition: {result.get('error')}")
    
    return state
