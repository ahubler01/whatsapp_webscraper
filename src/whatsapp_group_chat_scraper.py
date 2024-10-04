import base64
import hashlib
import json
import os
import random
import string
import time
import logging
from datetime import datetime
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
logging.getLogger('WDM').setLevel(logging.WARNING)

#######################################################
# PLEASE READ THE README FILE BEFORE RUNNING THE SCRIPT
#######################################################

def main():
    
    CHROME_PROFILE = os.getenv('CHROME_PROFILE')
    GROUP_CHAT_NAME = os.getenv('GROUP_CHAT_NAME')
    OLDEST_MESSAGE = os.getenv('OLDEST_MESSAGE')
        
    # Set up folder to store images
    folder_path = os.path.join(os.getcwd(), 'data')
    create_folder(folder_path)

    # Setup the Chrome WebDriver with the desired profile
    driver = setup_driver(CHROME_PROFILE)

    # Open WhatsApp Web
    driver.get('https://web.whatsapp.com/')

    # Reuse WebDriverWait throughout the script
    wait = WebDriverWait(driver, 20)

    # Custom function to open the group chat
    locate_chat(wait, GROUP_CHAT_NAME)

    # Locate the parent element containing the messages
    parent_element = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "x3psx0u xwib8y2 xkhd6sd xrmvbpv")]'))
    )

    # Initialize the reference for the previous message's date
    previous = parse_datetime_from_str(OLDEST_MESSAGE)

    # Scroll and load older messages
    index = scroll_and_load_older_messages(previous, driver, parent_element)

    # Data extraction: Initialize an empty list to store the conversation data
    conversation_data = []

    # Consolidate XPath queries for message components to minimize search
    message_elements = parent_element.find_elements(By.XPATH, './/div[contains(@class, "_akbu")]')
    date_elements = parent_element.find_elements(By.XPATH, './/div[contains(@class, "copyable-text")]')
    sender_elements = parent_element.find_elements(By.XPATH, './/span[contains(@class, "_ahx_")]')
    image_xpath = '//img[@class="x15kfjtz x1c4vz4f x2lah0s xdl72j9 x127lhb5 x4afe7t xa3vuyk x10e4vud"]'
    image_elements = parent_element.find_elements(By.XPATH, image_xpath)
    
    # Create a folder to store the images
    if image_elements:
        path = os.path.join(os.getcwd(), 'data', 'images')
        create_folder(path)

    # Extract the data from the elements
    for i in range(index):
        message_text = message_elements[i].text
        date_text = date_elements[i].get_attribute('data-pre-plain-text') if i < len(date_elements) else 'N/A'
        date_time_text = parse_datetime_from_str(date_text[:19]).isoformat()
        sender_text = sender_elements[i].text if i < len(sender_elements) else 'N/A'
        
        image_data = None
        if i < len(image_elements):
            try:
                image_element = image_elements[i]
                image_url = driver.execute_script("""
                    var imageElement = arguments[0];
                    var canvas = document.createElement('canvas');
                    var ctx = canvas.getContext('2d');
                    var img = new Image();
                    img.src = imageElement.src;
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    return canvas.toDataURL('image/png').substring(22);  // Remove base64 prefix
                """, image_element)

                image_bytes = base64.b64decode(image_url)
                img = Image.open(BytesIO(image_bytes))
                
                # Generate a random hash for the image
                random_number = ''.join(random.choices(string.digits, k=4))
                hash_object = hashlib.sha256(random_number.encode())
                hash_hex = hash_object.hexdigest()          
                path = os.path.join('data', 'images', f'{hash_hex}.png')
                img.save(path)  
                image_data = f'{hash_hex}.png'
                
            except Exception as e:
                logger.error(f"Error processing image {i}: {e}")

        
        # Append the data to the conversation_data list
        conversation_data.append({
            'sender': sender_text,  
            'message': message_text,
            'date_time': date_time_text,
            'image': image_data
        })

    json_path = os.path.join(os.getcwd(), 'data', 'conversation_data.json')
    
    # Save the conversation data to a JSON file
    with open(json_path, 'w') as f:
        json.dump(conversation_data, f, indent=4)

    for data in conversation_data:
        logger.info(data)
        
    logger.info(f"Conversation data saved to {json_path}")

    # Close the browser
    driver.quit()


def create_folder(path:os.path.join) -> None:
    """Creates a folder with the given os.path.join if it does not exist."""    
    if not os.path.exists(path):
        os.makedirs(path)
        
def parse_datetime_from_str(datetime_str:str) -> datetime:
    """Parse the date-time string in the format '[%H:%M, %d/%m/%Y]' to a datetime object.

    Args:
        datetime_str (str): String of type [%H:%M, %d/%m/%Y].

    Returns:
        datetime: datetime str in the format %H:%M, %d/%m/%Y.
    """    
    return datetime.strptime(datetime_str, '[%H:%M, %d/%m/%Y]')

def scroll_and_load_older_messages(previous: datetime, driver: webdriver, parent_element: webdriver.remote.webelement.WebElement) -> int:
    """Scroll the chat window to load older messages until the reference message is reached.

    Returns:
        index (int): Index of the first message that is older than the reference message.
    """    
    while True:
        time_date_elements = parent_element.find_elements(By.XPATH, './/div[contains(@class, "copyable-text")]')
        
        if not time_date_elements:
            logger.debug("No more messages found.")
            break

        time_date = time_date_elements[0].get_attribute('data-pre-plain-text')
        current = parse_datetime_from_str(time_date[:19])  
        
        if current < previous:
            for index, time_date_element in enumerate(reversed(time_date_elements)):
                time_date = time_date_element.get_attribute('data-pre-plain-text')
                current = parse_datetime_from_str(time_date[:19])  
                if current < previous:
                    logger.debug(f"Found older message at position {index}: {time_date}")
                    return index  
                else:
                    driver.execute_script("arguments[0].scrollIntoView(true);", time_date_element)
                    time.sleep(1)  
        else:
            driver.execute_script("arguments[0].scrollIntoView(true);", time_date_elements[0])
            time.sleep(1) 
            
        logger.info("Loading older messages...")
        time.sleep(1)
        
        
def setup_driver(CHROME_PROFILE: str) -> webdriver.Chrome:
    """Setup the Chrome WebDriver with the necessary options and return the driver instance.

    Returns:
        driver (webdriver.Chrome): Chrome WebDriver instance.
    """    
    chrome_options = Options()
    chrome_options.add_argument('--disable-search-engine-choice-screen') 
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_script_timeout(900)

    return driver

                   
def locate_chat(wait:WebDriverWait, name:str, retries:int =3 , delay:int =2 ) -> bool:
    """Find the chat with a given name in WhatsApp web and click on that chat, with a retry mechanism.

    Args:
        wait (WebDriverWait): The WebDriverWait instance used to wait for the chat element to be present.
        name (str): The name of the chat to locate.
        retries (int, optional): The number of retry attempts to locate the chat. Defaults to 3.
        delay (int, optional): The delay in seconds between retry attempts. Defaults to 2.

    Returns:
        bool: True if the chat was successfully located and clicked, False otherwise.
    """ 
    attempt = 0
    x_arg = f'//span[contains(@title, "{name}")]'

    # Retry mechanism to locate the chat
    while attempt < retries:
        try:
            logger.debug(f"Attempt {attempt + 1}: Locating chat using XPath: {x_arg}")
            
            # Locate the chat element
            person_title = wait.until(EC.presence_of_element_located((By.XPATH, x_arg)))
            logger.debug(f"Chat located: {person_title.text}")
            
            person_title.click()
            return True
        
        except Exception as e:
            attempt += 1
            logger.error(f"Error locating chat on attempt {attempt}: {e}")
            
            if attempt == retries:
                logger.error(f"Failed to locate chat after {retries} attempts.")
                return False
            
            time.sleep(delay)  

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO,  
                format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    main()