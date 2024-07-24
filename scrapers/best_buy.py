import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import pandas as pd
import os

#-------------------------------------------------------Driver CONFIGURATION-------------------------------------------------------------------------#
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-geolocation")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-extensions")

driver = webdriver.Chrome(options=chrome_options)
stealth(driver,
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)

#-----------------------------------------------------Personalization Variables---------------------------------------------------------------------#
# Get parameters from script frontend
if len(sys.argv) != 2:
    print("Usage: python best_buy.py <keyword>")
    sys.exit(1)
    
url = "https://www.bestbuy.com/?intl=nosplash"
search_for = sys.argv[1]

#-----------------------------------------------------Do Not Modify if no changes are required------------------------------------------------------#

class_search_bar = "search-input"
class_search_button = "header-search-button"

class_items = "sku-item"
class_next_button = "sku-list-page-next"

class_show_full_specs = "c-button.c-button-outline.c-button-md.show-full-specs-btn.col-xs-6"

class_product_5_star = "ugc-c-review-average.font-weight-medium.order-1"
class_product_review_amount = "c-reviews.order-2"
class_product_price = "priceView-hero-price.priceView-customer-price"
class_product_price_btn_modal = "priceView-tap-to-view-price.priceView-tap-to-view-price-bold"
class_product_price_div_modal = 'restricted-pricing__regular-price-section'
class_product_price_innerdiv_modal = 'pricing-price'
class_product_price_btn_close_modal = "c-close-icon.c-modal-close-icon"
class_product_sku = "product-data-value.body-copy"
class_product_img="primary-image.max-w-full.max-h-full"
class_product_features_btn = "c-button-unstyled.features-drawer-btn.w-full.flex.justify-content-between.align-items-center.py-200"
class_product_features_seemore_btn = "c-button-unstyled.see-more-button.btn-link.bg-none.p-none.border-none.text-style-body-lg-500"
class_product_features_description_text = "description-text.lv.text-style-body-lg-400"
class_product_features_div_of_ul_li = "pdp-utils-product-info"


class_ul_item_specs = "zebra-stripe-list.inline.m-none.p-none"
class_li_item_specs = "zebra-list-item.mt-500"
class_div_each_spec = "zebra-row.flex.p-200.justify-content-between.body-copy-lg"
class_div_spec_type = "mr-100.inline"
class_div_spec_text = "w-full"

# Global Variables
next_page = None
links = []
products_data = []
all_headers = ["Link", "Name", "SKU", "Price", "Five Star", "Review Amount", "Image Link", 'Description']  # Use list instead of set

#----------------------------------------------------------------Functions-------------------------------------------------------------------------#
def handle_survey():
    try:
        # If survey is noticed then click the no button, else, continue
        no_thanks_button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "survey_invite_no"))
        )
        no_thanks_button.click()
        print("Survey dismissed")
    except:
        print("No survey popup")
        
def scrape_page(driver):
    global links
    global next_page
    
    handle_survey()    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("Scrolled to bottom of the page.")
    try:
        elems = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_items)))
        print(f"Found {len(elems)} elements with class {class_items}.")

        tags = [elem.find_element(By.TAG_NAME, "a") for elem in elems]
        links.extend([tag.get_attribute("href") for tag in tags])
        
        try:
            next_page = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_next_button))).get_attribute("href")
            print(f"Found next page: {next_page}")
        except:
            next_page = None
            print("No next page found.")
    except Exception as e:
        print("Error!! ", e)

def process_product(driver, link):
    global products_data, all_headers
    driver.get(link)
    driver.implicitly_wait(20)
    handle_survey()
    product_info = {'Link': link}
    
    try:
        product_name_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        product_info['Name'] = product_name_element.text
    except Exception as e:
        product_info['Name'] = "N/A"
        print("Error getting product name:", e)
    if "Package" in product_info['Name']: return

    try:
        product_sku_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_product_sku))
        )
        product_info['SKU'] = product_sku_element.text
    except Exception as e:
        product_info['SKU'] = "N/A"
        print("Error getting product SKU:", e)
        
    try:
        product_image_link = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_product_img))
        )
        product_info['Image Link'] = product_image_link.get_attribute('src')
    except Exception as e:
        product_info['Image Link'] = "N/A"
        print("Error getting product SKU:", e)    
    
    try:
        price_div = driver.find_element(By.CLASS_NAME, class_product_price)
        product_info['Price'] = price_div.find_element(By.TAG_NAME, 'span').text
    except Exception as e:
        #Some times the product has the price hidden (it needs to be added in your cart to show price, so that is what this is doing)
        try:
            driver.find_element(By.CLASS_NAME,class_product_price_btn_modal).click()
            try:
                price_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_product_price_div_modal))
                )
                price_div = price_div.find_element(By.CLASS_NAME, class_product_price_innerdiv_modal)
                price_div = price_div.find_element(By.CLASS_NAME, class_product_price)
                price = price_div.find_element(By.TAG_NAME, 'span').text
                product_info['Price'] = price
            except Exception as e_text:
                print("Couldn't get the price because ", e_text)
                product_info['Price'] = ""
                    #I was having problem to click in the button, this is an atomic bomb, I know
            try:
                #Uses Selenium to click
                close_btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, class_product_price_btn_close_modal))
                )
                close_btn.click()
            except Exception as e:
                print(f"Error clicking close button: {e}")
                try:
                    # Uses JS to click
                    driver.execute_script("arguments[0].click();", close_btn)
                except Exception as js_e:
                    print(f"Error clicking close button with JS: {js_e}")
                    try:
                        #Just refresh if everything fails
                        driver.refresh()
                    except Exception as all_e:
                        print("Error in all atempts to click in the close button: ", all_e)
        except: print("Couldn't close the modal nand/nor get the price properly")
        
    try:
        description_features = []
        try:
            # Wait for and click the product features button
            features_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_features_btn))
            )
            features_btn.click()
        except Exception as e: print("There was a problem finding the Features Button: ", e)
        
        try:
            # Wait for and click the 'See More' button if it exists
            see_more_btn = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_features_seemore_btn))
            ) 
            see_more_btn.click()
        except Exception as e:
            print("No 'See More' button found:", e)
        try:
            # Wait for and extract the main features description
            features_description = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_product_features_description_text))
            ).text

            description_features.append(features_description)
        except: print('No text description found')
        
        # Wait for the div containing the list of features
        div_of_features = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_product_features_div_of_ul_li))
        )

        # Extract the features list
        list_of_features = div_of_features.find_elements(By.TAG_NAME, "li")
        for each_element in list_of_features:
            try:
                try:
                    h4 = each_element.find_element(By.TAG_NAME, 'h4').text
                except: h4=''
                p = each_element.find_element(By.TAG_NAME, 'p').text        
                description_line = f"{h4}: {p}, "
                description_features.append(description_line)
                
            except Exception as e:
                print("Error extracting feature:", e)
                continue

        product_info['Description'] = description_features
        
    except Exception as e:
        product_info['Description'] = "N/A"
        print("Error getting Features:", e)
        
    finally:
        try:
            # Attempt to close any modal that might be open
            close_icon = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'c-close-icon'))
            )
            close_icon.click()
        except Exception as e:
            print("No close icon found, refreshing page:", e)
            driver.refresh()
            
    try:
        five_star = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_product_5_star))
        ).text
        product_info['Five Star'] = five_star
    except Exception as e:
        product_info['Five Star'] = "N/A"
        print("Error getting five star rating:", e)

    try:
        review_amount = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_product_review_amount))
        ).text
        product_info['Review Amount'] = review_amount
    except Exception as e:
        product_info['Review Amount'] = "N/A"
        print("Error getting review amount:", e)
    
    try:
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, class_show_full_specs))).click()
    except Exception as e:
        print("Couldn't click show full specs button:", e)
    
    try:
        list_of_specs_ul = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, class_ul_item_specs))
        )

        for each_item in list_of_specs_ul:
            try:
                spec_items = each_item.find_elements(By.CLASS_NAME, class_div_each_spec)
                for spec_item in spec_items:
                    header = spec_item.find_element(By.CLASS_NAME, class_div_spec_type).text
                    #I could not find a way of getting the spec text with CSS Classes
                    #Then I could fetch by XPATH on a generic mode
                    spec = spec_item.find_element(By.XPATH, ".//div[contains(@class, 'w-full') and not(contains(@class, 'mr-200'))]").text
                    product_info[header] = spec
                    if header not in all_headers:
                        all_headers.append(header)
                    
                    print(f'ADDED:\n\tSPEC: {spec}\n\tHEADER:{header}\n\tCOMPLETE SPEC ADDED:{product_info}\n')

                    if header not in all_headers:
                        all_headers.append(header)
            except Exception as e:
                print(f"Error extracting specification: {e}")
                continue
    except Exception as e:
        print(f"Error occurred while getting specifications: {e}")
    products_data.append(product_info)


def process_products(driver):
    global links
    for link in links: 
        process_product(driver, link)
    links.clear()

#---------------------------------------------------------------------------Begining---------------------------------------------------------------------#    
try:        
    driver.get(url)
    handle_survey()
    driver.implicitly_wait(20)  # Wait for it to load
    print("Page loaded.")
    search = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_search_bar)))
    search.send_keys(search_for)
    
    time.sleep(2)
    
    button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, class_search_button)))
    button.click()
    
    driver.implicitly_wait(20)  # Wait for it to load
    '''
    This section is useful for test purposes
        You need to uncomment and fix indentation, also look at the code below, might be useful
    '''
    try:
        links = pd.read_csv("statics/product_link_BB.csv")
        links = links["Product Links"].to_list()
        if links == None:
            scrape_page(driver)
        while True:
            handle_survey()
            scrape_page(driver)
            if next_page: 
                driver.get(next_page)
                print(f"Navigating to next page: {next_page}")
            else: 
                break
    except:
        scrape_page(driver)
        while True:
            handle_survey()
            scrape_page(driver)
            if next_page: 
                driver.get(next_page)
                print(f"Navigating to next page: {next_page}")
            else: 
                break
    
except Exception as e:
    print("Not able to run the code, error: ", e)

if not os.path.exists("statics/product_links_BB.csv"):
    df = pd.DataFrame(links, columns=['Product Links'])
    df.to_csv("statics/product_links_BB.csv", index=False)

process_products(driver)

# Convert the list of dictionaries into a dataframe
df = pd.DataFrame(products_data)

# Ensure all headers are included
for header in all_headers:
    if header not in df.columns:
        df[header] = "N/A"

# Reorder columns based on all_headers
columns_order = ['Link', 'Name', 'SKU', 'Price', 'Five Star', 'Review Amount', 'Image Link', 'Description'] + sorted([header for header in all_headers if header not in ['Link', 'Name', 'SKU', 'Price', 'Five Star', 'Review Amount', 'Image Link', 'Description']])
df = df.reindex(columns=columns_order)

print(df.head(20))
df.to_csv('outputs/Best_Buy/product_data.csv', index=False)

driver.quit()
