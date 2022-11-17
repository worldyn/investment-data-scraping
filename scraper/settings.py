from selenium import webdriver

def setup_driver():
     """
     Creates a selenium driver. Remember to close driver in end of script
     """
     options = webdriver.ChromeOptions()
     options.add_argument('--ignore-certificate-errors')
     options.add_argument('--incognito')
     options.add_argument('--headless')
     options.add_argument("--window-size=1258,1258")
     driver = webdriver.Chrome("./chromedriver", chrome_options=options)
     driver.maximize_window()
     return driver
