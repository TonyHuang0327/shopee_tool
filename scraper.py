import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_price_safely(driver):
    """從 'product_price' 容器中提取所有 'NT$' 開頭的價格，避免重複抓取隱藏價格"""
    prices = []  # 確保每次調用函數時清空價格列表
    try:
        price_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product_price'))
        )
        
        # 抓取所有包含價格的子標籤，且只加入顯示中的價格
        price_elements = price_container.find_elements(By.XPATH, './/*')
        for price_element in price_elements:
            price_text = price_element.text.strip()
            if price_text.startswith("NT$") and price_element.is_displayed():
                prices.append(price_text)
                
        # 移除重複的價格值
        prices = list(dict.fromkeys(prices))
        
    except NoSuchElementException:
        print("警告: 無法找到價格資訊")
    
    # 如果沒有找到價格，則加入預設值
    if not prices:
        prices = ["價格未提供"]
    
    return prices

def get_element_text_safely(driver, selector_type, selector_value, default_value=""):
    try:
        element = driver.find_element(selector_type, selector_value)
        return element.text
    except NoSuchElementException:
        print(f"警告: 無法找到元素 {selector_value}")
        return default_value

# 初始化 CSV 檔案並寫入標題
csv_filename = 'happylife_products.csv'
with open(csv_filename, mode='w', encoding='utf-8', newline='') as file:
    fieldnames = ['name', 'description', 'price', 'introduction', 'item_spec']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

# 使用 webdriver_manager 自動管理 EdgeDriver
service = EdgeService(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service)

try:
    driver.maximize_window()
    driver.get('https://www.happylifepro.com.tw/collections/all')
    time.sleep(1)

    while True:
        item_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-v-8ca3f62a].productClick.overlay.qk-show_on_hover.qk-hidden--phone.qk-pos--abs.qk-w--100.qk-h--100.qk-display--flex.qk-justify--center.qk-align--center')

        for index in range(len(item_links)):
            try:
                item_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-v-8ca3f62a].productClick.overlay.qk-show_on_hover.qk-hidden--phone.qk-pos--abs.qk-w--100.qk-h--100.qk-display--flex.qk-justify--center.qk-align--center')
                item_links[index].click()
                time.sleep(1)

                item_title = get_element_text_safely(driver, By.CLASS_NAME, 'qk-text--heading.qk-fs--hd1.qk-fw--bold.qk-mg--0')
                item_description = get_element_text_safely(driver, By.CLASS_NAME, 'product_brief.qk-text--text.qk-fs--body')
                item_spec_labels = driver.find_elements(By.CSS_SELECTOR, 'div.advance label.option')
                item_spec_texts = [get_element_text_safely(spec, By.TAG_NAME, 'span') for spec in item_spec_labels]
                
                try:
                    container = driver.find_element(By.CSS_SELECTOR, 'div.ckeditor.qk-mg_t--1')
                    item_introduction_texts = []
                    
                    for p in container.find_elements(By.TAG_NAME, 'p'):
                        item_introduction_texts.append(p.text)
                        
                        # 檢查 p 標籤內是否有 img 標籤，有的話提取 src
                        imgs = p.find_elements(By.TAG_NAME, 'img')
                        for img in imgs:
                            img_src = img.get_attribute('src')
                            item_introduction_texts.append(f"[圖片] {img_src}")

                except NoSuchElementException:
                    print("警告: 無法找到商品介紹")
                    item_introduction_texts = []

                item_price = get_price_safely(driver)

                item_data = {
                    'name': item_title,
                    'description': item_description,
                    'price': item_price,
                    'introduction': item_introduction_texts,
                    'item_spec': item_spec_texts
                }

                # 寫入每筆商品資料到 CSV
                with open(csv_filename, mode='a', encoding='utf-8', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writerow(item_data)
                print(f"成功抓取商品: {item_title}")

            except Exception as e:
                print(f"處理商品時發生錯誤: {str(e)}")
                continue
            finally:
                driver.back()
                time.sleep(1)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'div.qk-mg_l--1.qk-arrow.qk-arrow_r--md.qk-cursor--pointer')
            next_button.click()
            time.sleep(1)
        except NoSuchElementException:
            print("已達到最後一頁，停止抓取。")
            break

finally:
    driver.quit()