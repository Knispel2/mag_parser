from selenium import webdriver, common
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import pandas
import numpy

def timesleep(sleeptime=1.7):
    time.sleep(sleeptime)

def give_chrome_option(folder_path):
    chromeOptions = webdriver.ChromeOptions() #setup chrome option
    prefs = {"download.default_directory" : folder_path,
           "download.prompt_for_download": False,
           "download.directory_upgrade": True}  #set path
    chromeOptions.add_experimental_option("prefs", prefs) #set option
    chromeOptions.add_argument("--headless")
    return chromeOptions

def get_csv(folder_path):
  try:
      return pandas.read_csv(folder_path + 'base_mags.csv')
  except:
      return pandas.DataFrame(columns = ['ID', 'ФИО', 'Номер', 'Факультет'])

mag_adress='''https://cpk.msu.ru/daily/dep_01_m
https://cpk.msu.ru/daily/dep_02_m
https://cpk.msu.ru/daily/dep_03_m
https://cpk.msu.ru/daily/dep_04_m
https://cpk.msu.ru/daily/dep_05_m
https://cpk.msu.ru/daily/dep_22_m
https://cpk.msu.ru/daily/dep_38_m
https://cpk.msu.ru/daily/dep_31_m
https://cpk.msu.ru/daily/dep_09_m'''.split('\n')

facks='''Мехмат
ВМК
Физфак
Химфак
Биофак
ФФФХИ
Биотех
ГУ
Наука о материалах'''.split('\n')



def get_mags():    
    folder_path = r'C:\FSR_Data' + '\\'    
    for index in range(len(mag_adress)):
        driver= webdriver.Chrome(ChromeDriverManager().install(), chrome_options = give_chrome_option(folder_path))
        result_list = []
        driver.get(mag_adress[index])
        timesleep()
        base = driver.find_elements(By.TAG_NAME, 'td')
        for element in base:
            if not element.text[0].isdigit():
                print(element.text)
                result_list.append(element.text)
        get_mag_info(result_list, facks[index])

def get_mag_info(data, fac):
    folder_path = r'C:\FSR_Data' + '\\'
    driver= webdriver.Chrome(ChromeDriverManager().install(), chrome_options = give_chrome_option(folder_path))
    url='https://webanketa.msu.ru/index.php#panel-login-internal'
    driver.get(url)
    try:
        #503 Service Temporarily Unavailable
        lnk=driver.find_element_by_link_text('вход для сотрудников')
        lnk.click()
        timesleep()
        login=driver.find_element_by_id('login_0_0_phone_phone')
        login.send_keys('9057377023')    
        pas=driver.find_element_by_name('login_password')
        pas.send_keys('5265922106')
        timesleep()
        vds=driver.find_element_by_class_name('login')
        timesleep()
        vds.click()
        timesleep()
        counter_aut = 0
        while (driver.find_element_by_tag_name("h1").text == "503 Service Temporarily Unavailable"):
            counter_aut += 1
            driver.get('https://webanketa.msu.ru/index.php')
            if counter_aut == 30:
                return 1
    except common.exceptions.NoSuchElementException:
        print('Какая-то проблема при авторизации')
        return 1
    driver.get('https://webanketa.msu.ru/index.php?page=searchabi')
    timesleep(2)
    folder_path = r'C:\\FSR_Data' + '\\' + 'base' + '\\'
    for name_mag in data:        
        main_base =  get_csv(folder_path)
        while True:
            try:
                search_butt = driver.find_element_by_name('searchName')
                search_butt.send_keys(name_mag)
                search_butt = driver.find_element_by_name('search')
                search_butt.click()
                timesleep()
                tbd=driver.find_element_by_tag_name('tbody')
                trs=tbd.find_elements_by_tag_name('tr') #множество строк
                for i in trs: #здесь надо сделать поиск по строкам
                    string_data = i.find_elements_by_tag_name('td') #отдельно взятая строка
                    ID = string_data[0].text
                    phone = string_data[1].text
                    name = string_data[2].text
                    if name in main_base['ФИО'].unique():
                        if not phone in str(main_base.loc[main_base['ФИО'] == name, 'Номер']):
                            main_base.loc[main_base['ФИО'] == name, 'Номер'] += r'\n' + phone
                            main_base.to_csv(folder_path + 'base_mags.csv', index=False, encoding="utf-8")
                        continue                    
                    else:
                        new_row = {'ID':ID, 'ФИО':name, 'Номер': phone, 'Факультет' : fac} 
                        main_base = main_base.append(new_row, ignore_index=True)
                        main_base.sort_values('Факультет', inplace=True)
                        main_base.to_csv(folder_path + 'base_mags.csv', index=False, encoding="utf-8")
                break
            except Exception as err:
                print('*',err,'* - ')
                continue       

#get_mag_list()