import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    INSTAGRAM_USERNAME, 
    INSTAGRAM_PASSWORD,
    POST_URL,
    SCROLL_PAUSE,
    LOAD_MORE_ATTEMPTS
)
from scraper import InstagramScraper

def setup_driver():
    """Setup Chrome WebDriver"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment untuk headless mode
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    return driver

def main():
    driver = None
    
    try:
        # Setup browser
        print(">>> Menyiapkan browser...")
        driver = setup_driver()
        
        # Inisialisasi scraper
        scraper = InstagramScraper(driver)
        
        # Login
        scraper.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        
        # Buka postingan
        print(f"\n>>> Membuka: {POST_URL}")
        driver.get(POST_URL)
        time.sleep(5)
        
        # Scroll & Load More
        print("\n>>> Mencoba memuat komentar lama...")
        for i in range(LOAD_MORE_ATTEMPTS):
            success = scraper.click_load_more()
            if success:
                print(f"Tombol Load More ditekan ({i+1})...")
                time.sleep(SCROLL_PAUSE)
            else:
                # Scroll untuk memicu lazy load
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(1)
        
        # Ekstraksi komentar
        hasil = scraper.extract_comments()
        
        # Simpan hasil
        if hasil:
            df = pd.DataFrame(hasil)
            df.to_csv("hasil_komentar_ig.csv", index=False, encoding='utf-8-sig')
            print(f"\n✓ SUKSES! {len(hasil)} komentar disimpan ke 'hasil_komentar_ig.csv'")
            print("\nPreview data:")
            print(df.head())
        else:
            print("\n✗ GAGAL: Tidak ada data yang terambil.")
    
    except Exception as e:
        print(f"\n✗ Error Fatal: {e}")
    
    finally:
        if driver:
            # driver.quit()  # Uncomment untuk auto close browser
            print("\n>>> Selesai.")

if __name__ == "__main__":
    main()