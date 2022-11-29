from selenium import webdriver
import logging

def setup_driver():
    """
     Creates a selenium driver. Remember to close driver in end of script
     """
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--incognito")
        options.add_argument("--headless")
        options.add_argument("--window-size=258,258")
        driver = webdriver.Chrome(chrome_options=options)
        #driver.maximize_window()
        return driver
    except:
        logging.info("Could not load Driver!")
