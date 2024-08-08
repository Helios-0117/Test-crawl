import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

browser = webdriver.Chrome()
browser.get('http://www.yahoo.com')
assert 'Yahoo' in browser.title # report if there's no "Apple" in title

elem = browser.find_element(By.NAME, 'p')  # try finding something in search box p
elem.clear()
elem.send_keys('iphone 15' + Keys.RETURN) # press Enter key
assert "No results found." not in browser.page_source

time.sleep(5)
browser.quit() # close browser
browser.close() # close current page