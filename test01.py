import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def create_webdriver():
    return webdriver.Chrome()

def get_detail(url,driver):
    data = dict()    
    driver.get(url)

    # 抓 電話/電子信箱/網站/社群介紹 等網頁資料
    telephone_element = driver.find_element(By.CLASS_NAME, 'info-tel')
    data['telephone'] = telephone_element.text
    email_element = driver.find_element(By.CLASS_NAME, 'info-mail')
    data['email'] = email_element.text
    website_element = driver.find_elements(By.CLASS_NAME, 'border-icon')
    for web in website_element:
        href = web.get_attribute('href')
        if href:
            for sns in ['facebook','twitter','linkedin','instagram']:
                if sns in href:
                    data[sns] = href
        else:
            data['Website'] = href
    desc_element = driver.find_element(By.CLASS_NAME, 'ex-foreword')
    if desc_element: # 確定有東西
        print("Description: ", desc_element.text)
    else:
        print("Description not found.")
    
    return data

if __name__ == '__main__':
    driver = create_webdriver()
    get_url = 'https://cybersec.ithome.com.tw/2024/exhibition-page/2109'
    data = get_detail(get_url,driver)
    time.sleep(0.5)
    print(data)
    driver.close()