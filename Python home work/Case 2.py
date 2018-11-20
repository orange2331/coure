import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome("/Users/alexandrteplitskiy/Documents/Python курсы/Семинар/chromedriver")
def mid_hotel_price(city,date1,date2):

    _start_date = date1
    _finish_date = date2

    start_date_element = None
    finish_date_element = None

    driver.get("https://www.booking.com")

    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "ss")))
    search_input.clear()  # не забываем очищать форму

    calendar = driver.find_element_by_xpath('//*[@id="frm"]/div[1]/div[2]/div[1]/div[2]/div/div/div/div/button')

    calendar.click()

    all_dates = driver.find_elements_by_class_name("bui-calendar__date")

    for date in all_dates:
        attr = date.get_attribute("data-date")
        if attr == _start_date:
            start_date_element = date
            continue
        if attr == _finish_date:
            finish_date_element = date

    submit = driver.find_element_by_xpath('//*[@id="frm"]/div[1]/div[4]/div[2]/button')
    search_input.send_keys(city)
    ActionChains(driver).click(start_date_element).click(finish_date_element).click(submit).perform()

    # следующая страница
    new_prices = []
    for i in range(0, 5):

        # element = WebDriverWait(driver, 10).until(
        #    EC.element_to_be_selected((By.CLASS_NAME, 'price')))
        all_prices = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "price")))  # ждем загрузки соед. страницы
        for name in all_prices:
            new_prices.append(' '.join([element.text for element in name.find_elements_by_tag_name("b")]))
        next_pg = driver.find_element_by_class_name('paging-next')
        next_pg.click()
        time.sleep(10)
    # print()
    pattern = re.compile(r'RUB ')
    valid=[]
    for i in new_prices:
        pr=re.sub(pattern, '', i)
        s=pr.replace(',','')
        s_int=int(s)
        valid.append(s_int)
    print(sum(valid)/len(valid))
mid_hotel_price("Милан","2018-12-02","2018-12-08")