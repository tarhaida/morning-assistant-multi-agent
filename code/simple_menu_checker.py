#!/usr/bin/env python3
"""
Smart Menu Checker and Downloader
Downloads school menu images from Divonne-les-Bains website
Only downloads new menus that haven't been downloaded before
"""

import os
import sys
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from urllib.parse import urljoin, urlparse
import hashlib
from pathlib import Path

class SmartMenuChecker:
    def __init__(self, download_folder=None):
        """Initialize the smart menu checker"""
        self.base_url = "https://www.espace-citoyens.net"
        self.menu_url = "https://www.espace-citoyens.net/divonnelesbains/espace-citoyens/Activites/IndexActivitesPubliques#"
        
        # Use project data folder if no custom folder specified
        if download_folder is None:
            project_root = Path(__file__).parent.parent
            download_folder = str(project_root / "data" / "final_menu_download")
        
        self.download_folder = download_folder
        self.downloaded_files = set()
        
        # Create download folder if it doesn't exist
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            print(f"📁 Created download folder: {self.download_folder}")
        
        # Load existing files
        self.load_existing_files()
    
    def load_existing_files(self):
        """Load list of already downloaded files"""
        if os.path.exists(self.download_folder):
            existing_files = [f for f in os.listdir(self.download_folder) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf'))]
            self.downloaded_files = set(existing_files)
            print(f"📋 Found {len(self.downloaded_files)} existing menu files")
            for file in sorted(self.downloaded_files):
                print(f"   📄 {file}")
        else:
            print("📁 No existing download folder found")
    
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome WebDriver initialized successfully")
            return driver
        except Exception as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("💡 Make sure ChromeDriver is installed: brew install chromedriver")
            return None
    
    def navigate_to_menus(self, driver):
        """Navigate to the school menus page"""
        try:
            print(f"🌐 Navigating to: {self.menu_url}")
            driver.get(self.menu_url)
            
            # Wait for page to load
            print("⏳ Waiting for page to load...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait extra time for dynamic content to load (JavaScript heavy page)
            print("⏳ Waiting for dynamic content...")
            time.sleep(8)
            
            # Scroll down to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            print("✅ Page loaded successfully")
            print(f"📍 Current URL: {driver.current_url}")
            
            # Try to find and click on menu-related elements
            print("🔍 Looking for menu content...")
            
            # Check if we need to navigate further
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"   Found {len(links)} links on page")
            
            # Look for menu-related links
            menu_keywords = ["menu", "cantine", "restaurant", "scolaire"]
            menu_links_found = []
            for link in links:
                try:
                    link_text = link.text.lower().strip()
                    href = link.get_attribute("href") or ""
                    
                    if any(keyword in link_text for keyword in menu_keywords):
                        menu_links_found.append(link.text.strip())
                        print(f"   📎 Found menu-related link: '{link.text.strip()}'")
                except:
                    continue
            
            if menu_links_found:
                print(f"✅ Found {len(menu_links_found)} menu-related links")
            
            # Look for and click on "RESTAURATION SCOLAIRE" link
            print("🔍 Looking for 'RESTAURATION SCOLAIRE' link to click...")
            restauration_clicked = False
            for link in links:
                try:
                    link_text = link.text.strip()
                    if link_text == "RESTAURATION SCOLAIRE":
                        print(f"🖱️ Clicking on '{link_text}'...")
                        try:
                            link.click()
                        except:
                            driver.execute_script("arguments[0].click();", link)
                        
                        restauration_clicked = True
                        time.sleep(5)  # Wait for new content to load
                        
                        # Scroll again after clicking
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(1)
                        
                        print(f"✅ Clicked successfully, new URL: {driver.current_url}")
                        
                        # After clicking 'RESTAURATION SCOLAIRE'
                        time.sleep(2)  # Wait for the new content to load
                        
                        # Find and click 'Menus restaurant scolaire'
                        menu_links = driver.find_elements(By.TAG_NAME, "a")
                        menu_link = None
                        for link in menu_links:
                            link_text = link.text.lower().strip()
                            if "menus restaurant scolaire" in link_text or "menu restaurant scolaire" in link_text or "menus scolaires" in link_text:
                                menu_link = link
                                print(f"✅ Found 'Menus restaurant scolaire' link: '{link.text.strip()}'")
                                break

                        if menu_link:
                            driver.execute_script("arguments[0].click();", menu_link)
                            print("🖱️ Clicked on 'Menus restaurant scolaire' link")
                            time.sleep(2)  # Wait for menu page to load
                        else:
                            print("❌ Could not find 'Menus restaurant scolaire' link")
                            return False
                        
                        break
                except:
                    continue
            
            if not restauration_clicked:
                print("⚠️ Could not click on RESTAURATION SCOLAIRE link")
            
            return True
            
        except TimeoutException:
            print("❌ Timeout waiting for page elements")
            return False
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def find_menu_images(self, driver):
        """Find all menu images on the page"""
        try:
            print("🔍 Searching for menu images and PDFs...")
            
            menu_items = []
            
            # Find all images
            images = driver.find_elements(By.TAG_NAME, "img")
            print(f"   Found {len(images)} total images on page")
            
            for img in images:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt") or ""
                title = img.get_attribute("title") or ""
                
                # Check if this looks like a menu image
                if src and self.is_menu_item(src, alt, title):
                    # Make URL absolute
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = urljoin(self.base_url, src)
                    elif not src.startswith("http"):
                        src = urljoin(driver.current_url, src)
                    
                    menu_items.append({
                        'url': src,
                        'alt': alt,
                        'title': title,
                        'type': 'image'
                    })
                    print(f"   📸 Found menu image: {os.path.basename(src)}")
            
            # Find all links (for PDFs and other documents)
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"   Found {len(links)} total links on page")
            
            for link in links:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                if href and self.is_menu_item(href, text, ""):
                    # Make URL absolute
                    if href.startswith("//"):
                        href = "https:" + href
                    elif href.startswith("/"):
                        href = urljoin(self.base_url, href)
                    elif not href.startswith("http"):
                        href = urljoin(driver.current_url, href)
                    
                    menu_items.append({
                        'url': href,
                        'alt': text,
                        'title': text,
                        'type': 'document'
                    })
                    print(f"   📄 Found menu document: {os.path.basename(href)}")
            
            print(f"✅ Found {len(menu_items)} menu items total")
            return menu_items
            
        except Exception as e:
            print(f"❌ Error finding images: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def is_menu_item(self, url, alt, title):
        """Check if an item is likely a menu"""
        # Accept items where the filename in url, alt, or title starts with "menu-du-"
        url = url.lower()
        alt = alt.lower()
        title = title.lower()
        
        from urllib.parse import urlparse
        filename = os.path.basename(urlparse(url).path)
        starts_with_menu_du = (
            filename.startswith("menu-du-") or
            alt.startswith("menu-du-") or
            title.startswith("menu-du-")
        )
        
        # Exclude common non-menu items
        exclude_indicators = [
            "logo", "icon", "button", "background", "banner", "header", "footer",
            "picto", "trois_barres", "trois-barres", "pictomenu"
        ]
        text_to_check = f"{url} {alt} {title}"
        has_exclude_indicator = any(indicator in text_to_check for indicator in exclude_indicators)
        
        # Exclude anchor-only links
        if url.endswith("#") or url.endswith("indexactivitespubliques#"):
            has_exclude_indicator = True
        
        return starts_with_menu_du and not has_exclude_indicator
    
    def generate_filename(self, url, alt_text=""):
        """Generate a filename for the menu item"""
        # Extract filename from URL
        parsed_url = urlparse(url)
        original_filename = os.path.basename(parsed_url.path)
        
        # Remove URL parameters
        if "?" in original_filename:
            original_filename = original_filename.split("?")[0]
        
        if original_filename and "." in original_filename:
            return original_filename
        
        # Generate filename from alt text
        if alt_text:
            # Clean alt text for filename
            clean_alt = alt_text.lower().replace(" ", "_")
            clean_alt = "".join(c for c in clean_alt if c.isalnum() or c in "_-")
            # Determine extension from URL
            if ".pdf" in url.lower():
                return f"{clean_alt}.pdf"
            else:
                return f"{clean_alt}.jpg"
        
        # Generate from URL hash as fallback
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        if ".pdf" in url.lower():
            return f"menu_{url_hash}.pdf"
        return f"menu_{url_hash}.jpg"
    
    def is_already_downloaded(self, filename):
        """Check if a file has already been downloaded"""
        return filename in self.downloaded_files
    
    def download_item(self, item_info):
        """Download a single menu item (image or PDF)"""
        url = item_info['url']
        alt = item_info.get('alt', '')
        
        # Generate filename
        filename = self.generate_filename(url, alt)
        filepath = os.path.join(self.download_folder, filename)
        
        # Check if already downloaded
        if self.is_already_downloaded(filename):
            print(f"   ⏭️ Skipping {filename} (already downloaded)")
            return False
        
        try:
            print(f"   📥 Downloading: {filename}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if not (content_type.startswith('image/') or content_type.startswith('application/pdf')):
                print(f"   ⚠️ Warning: Content type is {content_type}")
            
            # Save the file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Add to downloaded files set
            self.downloaded_files.add(filename)
            
            file_size = len(response.content)
            print(f"   ✅ Downloaded {filename} ({file_size:,} bytes)")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Download failed for {filename}: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error downloading {filename}: {e}")
            return False
    
    def check_and_download_menus(self):
        """Main method to check for new menus and download them"""
        print("🍽️ SMART MENU CHECKER")
        print("📊 Checking for new menu images to download")
        print("=" * 60)
        
        # Setup WebDriver
        driver = self.setup_driver()
        if not driver:
            return False
        
        try:
            # Navigate to menus page
            if not self.navigate_to_menus(driver):
                print("\n💡 TIP: Unable to load the menu page.")
                print(f"   Try visiting: {self.menu_url}")
                return False
            
            # Find menu items
            menu_items = self.find_menu_images(driver)
            
            if not menu_items:
                print("❌ No menu items found")
                print("\n💡 Current page URL:", driver.current_url)
                print("💡 The page may require login or the structure has changed")
                return False
            
            # Download new items
            print(f"\n📥 DOWNLOADING NEW MENUS")
            new_downloads = 0
            
            for i, item_info in enumerate(menu_items):
                print(f"[{i+1}/{len(menu_items)}] Processing item...")
                if self.download_item(item_info):
                    new_downloads += 1
                time.sleep(1)  # Be polite to the server
            
            print(f"\n📊 DOWNLOAD SUMMARY:")
            print(f"   📄 Total items found: {len(menu_items)}")
            print(f"   📥 New downloads: {new_downloads}")
            print(f"   📋 Total files in folder: {len(self.downloaded_files)}")
            print(f"   📁 Download folder: {os.path.abspath(self.download_folder)}")
            
            if new_downloads > 0:
                print("🎉 New menus downloaded successfully!")
            else:
                print("✅ All menus are up to date!")
            
            return True
            
        finally:
            driver.quit()
            print("🔒 WebDriver closed")

def main():
    """Main function"""
    checker = SmartMenuChecker()
    success = checker.check_and_download_menus()
    
    if success:
        print("\n✅ Menu check completed successfully!")
    else:
        print("\n❌ Menu check failed!")
    
    return success

if __name__ == "__main__":
    main()