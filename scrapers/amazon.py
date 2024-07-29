import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import pandas as pd
from routines.Amazon.Amazon_Laundry import cleanup_BR, cleanup_US

# Receive values from script frontend
if len(sys.argv) != 4:
    print("Usage: python amazon.py <keyword> <country> <need_change_location>")
    sys.exit(1)

keyword = sys.argv[1]
country = sys.argv[2]
need_change_location = sys.argv[3].lower() == 'true'



# -------------------------------------------------------------------------------------------------------------------#
# Driver Configuration - prioratazing safety and discretion (trying at least)
# -------------------------------------------------------------------------------------------------------------------#
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-geolocation")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-extensions")
driver = webdriver.Chrome(options=chrome_options)
# -------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------------------------------------------------------------------------#
# configure Selenium Stealth
# -------------------------------------------------------------------------------------------------------------------#
stealth(driver,
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)
# -------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------------------------------------------------------------------------#
# -----------------------------------------Customizable Variables---------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------#

#Links
url_USA = "https://www.amazon.com" 
url_MXC = "https://www.amazon.com.mx" 
url_India = "https://www.amazon.in" 
url_BR = "https://www.amazon.com.br" 

#Zip codes
zip_code_USA = "19947" 
zip_code_MXC = "01000"
zip_code_India = "400001"
zip_code_BR = "13500600"

#What to scrape
# keywords_USA = "Washer Machines and Dryers"
# keywords_MXC = "lavadoras y secadoras"
# keywords_India = "Washer Machines and Dryers"
# keywords_BR = "Lavadoras e Secadoras de Roupas"


#Small Data treatment
txt_th_5star_USA = "Customer Reviews" 
txt_th_ignore_USA = "Best Sellers Rank" 

txt_th_5star_MXC = "Opinión media de los clientes" 
txt_th_ignore_MXC = "Clasificación en los más vendidos de Amazon" 

txt_th_5star_India = "Customer Reviews"
txt_th_ignore_India = "Best Sellers Rank"

txt_th_5star_BR = "Avaliações de Clientes"
txt_th_ignore_BR = "Ranking dos mais vendidos"
   
keywords = sys.argv[1]

zip_code = None
url = None
txt_th_5star = None
txt_th_ignore = None

target_country = sys.argv[2]
match target_country:
    
    case "USA":
        zip_code = zip_code_USA
        url = url_USA
        txt_th_5star = txt_th_5star_USA
        txt_th_ignore = txt_th_ignore_USA
        
    case "MXC":
        zip_code = zip_code_MXC
        url = url_MXC
        txt_th_5star = txt_th_5star_MXC
        txt_th_ignore = txt_th_ignore_MXC
        
    case "India":
        zip_code = zip_code_India
        url = url_India
        txt_th_5star = txt_th_5star_India
        txt_th_ignore = txt_th_ignore_India
        
    case "BR":
        zip_code = zip_code_BR
        url = url_BR
        txt_th_5star = txt_th_5star_BR
        txt_th_ignore = txt_th_ignore_BR        

you_need_to_change_location = sys.argv[3].lower() == 'true'


# -------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------------------------------------------------------------------------#
#JUST TO CHANGE IF THERE IS A CHANGE IN THE AMAZON WEBSITE  
# -------------------------------------------------------------------------------------------------------------------#
# Navigation classes
class_search_bar = 'nav-input.nav-progressive-attribute'
class_submit_btn = 'nav-search-submit-button'
class_next_btn = 's-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator'

# For each item
class_itens = 's-result-item.s-asin'

# URLs of each item
class_link = 'a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal'

# Item classes DEPRECATED OR TO BE USED LATER   
att_img = 'data-image-source-density'
class_image_li = 'a-spacing-small item imageThumbnail a-declarative'
class_local_currency = "a-price-symbol"

# What to get from each object
class_name = 'a-size-large.product-title-word-break'
class_price = "a-price-whole"
id_description = 'productDescription'
id_img = 'imgTagWrapperId'
class_th = "a-color-secondary.a-size-base.prodDetSectionEntry"
class_td = 'a-size-base.prodDetAttrValue'
class_5_Star = 'reviewCountTextLinkedHistogram.noUnderline'
id_review_counts = 'acrCustomerReviewText'
# -------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------#
# Global Variables
next_page = None
product_link = []
products_data = []
# -------------------------------------------------------------------------------------------------------------------#


# -------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------FUNCTIONS-------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------#

def location_changer():
    # Wait for the location icon to be present and click it
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "nav-packard-glow-loc-icon"))
    )
    driver.find_element(By.ID, "nav-packard-glow-loc-icon").click()

    # Wait for the ZIP input field to be present and send ZIP code
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
    )
    zip_input = driver.find_element(By.ID, "GLUXZipUpdateInput")
    zip_input.send_keys(zip_code, Keys.ENTER)  # Replace with your target ZIP code

    # Send Enter key using send_keys method
    zip_input.send_keys(Keys.ENTER)

    # Optional: Use JavaScript to trigger Enter key event
    driver.execute_script(
        "arguments[0].dispatchEvent(new KeyboardEvent('keydown', {'key': 'Enter'}));", zip_input
    )

    # Optional: Use ActionChains to send Enter key
    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER).perform()

    # Adding a sleep to ensure actions are completed (optional, use WebDriverWait for better handling)
    time.sleep(5)
                        

def scrape_page(driver:webdriver):
    '''
    This function gets the link of each object of each page in the 'keywords' pages.
    It will change variables such as 'product_link' and 'next_page',
    putting all the links inside product_link and going to the next page if there is one 
    
    Parameters:
        -driver: webdriver
    '''
    global product_link
    global next_page

    # wait until elements are found
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_itens)))

    # get elements links
    elements = driver.find_elements(By.CLASS_NAME, class_itens)
    for element in elements:
        item = element.find_element(By.CLASS_NAME, class_link)
        product_link.append(item.get_attribute('href'))

    # Uncomment after testing // Comment for testing (time and processment):
    try:
        next_page = driver.find_element(By.CLASS_NAME, class_next_btn).get_attribute("href")
    except:
        next_page = None

def process_product(driver:webdriver, link:str):
    '''
    For each object whose link was copied in the product_link:
    →it will fetch some informations
    →process a dictionary if this informations
    →append in the list of the dictionaries that contains all machines
    
    For all of them, we are trying to get, if not found, leave it blank, because there are lots of differences between each object
    
    Parameters:
        -driver: webdriver
        -link: str
    '''
    global products_data
    driver.get(link) #Go to the object's page
    driver.implicitly_wait(20) #Wait the page to load

    product_info = {'Link': link} #append it's link in the dictionary

    try:
        name = driver.find_element(By.CLASS_NAME, class_name).text 
        product_info['Name'] = name #append it's name in the dictionary      
    except: product_info['Name'] = ""

    try:
        price = driver.find_element(By.CLASS_NAME, class_price).text
        product_info['Price'] = price #append it's price in the dictionary (integer only)    
    except: product_info['Price'] = ""
        
    #For this one, there is a table, so I am gathering all elements, the Table Headers (th) and the Table Data (td)
    #I'm storing them in two lists
    #There are two exceptions in the tables, the 5-Star Review Avg., that we want and the Website's Selling Rank, which is not interesting
    try:
        th_elements = driver.find_elements(By.CLASS_NAME, class_th)
        td_elements = driver.find_elements(By.CLASS_NAME, class_td)
        th_texts = [elem.text for elem in th_elements]
        td_texts = [elem.text for elem in td_elements]
        
        #The review avg.
        try: five_stars = driver.find_element(By.CLASS_NAME, class_5_Star).get_attribute('title') 
        except: five_stars = None
            
        for th_text, td_text in zip(th_texts, td_texts): #Now we want to envelop that in a structure like: "th_text":"td_text", treating the exceptions
            if th_text == txt_th_5star: product_info[th_text] = five_stars
            elif th_text == txt_th_ignore: product_info[th_text] = ""
            else: product_info[th_text] = td_text
                
    except Exception as e: print("Error: ", e)
    
    try: review_counts = driver.find_element(By.ID, id_review_counts).text
    except: review_counts = None
    finally: product_info['Review Count'] = review_counts
        
   #Get the item's description if there is one   
    try: description = driver.find_element(By.ID, id_description).find_element(By.TAG_NAME,'span').text
    except: description = None
    finally: product_info["Description"] = description
    
    #Get the item's img if there is one
    try: img = driver.find_element(By.ID, id_img).find_element(By.TAG_NAME,'img').get_attribute('src')
    except: img = None
    finally: product_info["Image Link"] = img
    
    products_data.append(product_info)#Add item in the list of items

def process_products(driver:webdriver):
    '''
        Iterates for each link, in the end let go of the list of links
    '''
    global product_link
    for link in product_link: process_product(driver, link)

    product_link.clear()
    
# -------------------------------------------------------------------------------------------------------------------#
# ------------------------------------------------------Start!-------------------------------------------------------#
# -------------------------------------------------------------------------------------------------------------------#

try:
    driver.get(url) #Go to the website
    driver.implicitly_wait(20)#Wait for it to load
    if you_need_to_change_location:
        location_changer()
    search = driver.find_element(By.CLASS_NAME, class_search_bar)#go to the search bar
    search.send_keys(keywords)#type the keywords
    time.sleep(1)#take a breath
    search_btn = driver.find_element(By.ID, class_submit_btn)#go to the button
    search_btn.click()#click in the search button
    driver.implicitly_wait(5)#wait for the page to load
    
    while True:
        '''
        For each page, scrape the links until you find no more pages
        '''
        scrape_page(driver)
        if next_page: driver.get(next_page)
            
        else: break
            
    #Now for each link gotten, find the infos we need        
    process_products(driver)
    
except Exception as e:
    print("Failed to run the code, exited with error: ", e)
    
finally:
    #Close google
    driver.quit()

#-----------------------------------------------------------Storing in a CSV -----------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------#

# Convert the list of dictionaries into a dataframe, printing top 5 items for checking
df = pd.DataFrame(products_data)
print(df.head(20))
df.to_csv('outputs/Amazon/product_data.csv', index=False)
if 'washer' in keyword or 'dryer' in keyword:
    match target_country:
        case 'USA': df = cleanup_US(df)
        case 'BR': df = cleanup_BR(df)
        case 'MX': print('not implemented yet')
        case 'India': print('not implemented yet')
df.to_csv('../outputs/Amazon/product_data_cleaned.csv', index=False)