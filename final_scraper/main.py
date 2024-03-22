import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

class Scraper:
    def __init__(self, url):
        self.url = url
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def show_more_button(self):
        button_selector = "button.Button_button__8B4nB.Button_custom__SdTYs.outlined.DepartmentsSection_showMoreButton__F7Cgv"
        show_more = self.driver.find_element(By.CSS_SELECTOR, button_selector)
        return self.driver.execute_script("arguments[0].click();", show_more)

    def departments(self):
        self.show_more_button()
        dep = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'DescriptionList_header__bdeSz DepartmentsSection_header__1jGQI')]")
        dep_len = len(dep)
        return dep_len

    def hospital_available(self, i):
        hos_name = self.driver.find_element(By.XPATH, f'''//*[@id="hospitalsCards"]/div[{i}]/div[1]/div[3]/div[1]/div/a/h2''')

        self.driver.execute_script("arguments[0].scrollIntoView();", hos_name)
        return self.driver.execute_script("arguments[0].click();", hos_name)

    def hospital_title(self):
        hos_title = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '''//h1[@class="MainInfo_titleName__rhrVM"]'''))
        ).text
        return hos_title

    def scrape_data(self):

        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(20)

        names = self.driver.find_elements(By.CLASS_NAME, "HospitalCard_name__UZRIa")
        hospital_names = [name.text for name in names]
        print(f"Total {len(hospital_names)} hospitals scraped ")

        # Object with column names only
        df = pd.DataFrame(columns=['Hospital_Name', 'Department', 'Doctor', "Dr_image", "About_dr"])
        print(df)

        for i in range(1, 10):
            try:
                self.hospital_available(i=i)
                time.sleep(2)

            except NoSuchElementException as e:
                # If the button is not found, skip to the next hospital iteration
                print(f"Show Hospital button not found at {i}th iteration. ")
                continue
            self.driver.implicitly_wait(10)

            hos_title = self.hospital_title()
            print(f"Entered into hospital {hos_title} ")
            self.driver.implicitly_wait(3)

            try:
                self.show_more_button()
                time.sleep(1)

            except (NoSuchElementException, TimeoutException) as e:
                # If the button is not found, skip to the next hospital iteration
                print(f"Show More button not found for {hos_title}. Skipping this hospital at {i}th  error = {e}")
                time.sleep(1)
                self.driver.back()
                time.sleep(1)
                continue

            print("Accessed all the DR's profile")
            time.sleep(1)
            self.driver.implicitly_wait(2)

            dep_len = self.departments()
            print(f"Found {dep_len} department in {self.driver.title} at {i}th iteration ")

            self.driver.back()
            time.sleep(1)
            self.driver.implicitly_wait(3)

            self.hospital_available(i=i)
            time.sleep(2)
            self.driver.implicitly_wait(2)

            hos_title = self.hospital_title()

            try:
                for j in range(1, dep_len - 4):

                    time.sleep(1)
                    self.driver.implicitly_wait(5)

                    if hos_title == "University Hospital Rechts der Isar Munich" and j == 12:
                        continue

                    self.show_more_button()
                    time.sleep(1)
                    self.driver.implicitly_wait(3)

                    # Clicking on each iteration of doctor profile
                    click = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, f'''//*[@id="modalRoot"]/div/div/div/div[3]/div/div/div[{j}]/div[1]/div''')))
                    self.driver.execute_script("arguments[0].scrollIntoView();", click)
                    self.driver.execute_script("arguments[0].click();", click)
                    print("Clicked on + icon")
                    time.sleep(1)

                    # Doctor name
                    dr_name = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'''//*[@id="modalRoot"]/div/div/div/div[3]/div/div/div[{j}]/div[2]/div/div/div/div/div[1]/a'''))).text
                    print(f"Doctor name {dr_name} got ")

                    self.driver.implicitly_wait(2)
                    time.sleep(1)
                    # Relative department
                    dep_name = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'''//*[@id="modalRoot"]/div/div/div/div[3]/div/div/div[{j}]/div[1]/div/div/div/div'''))).text
                    print(f"Dep name {dep_name} got ")

                    self.driver.implicitly_wait(2)

                    image = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".DepartmentDoctorItem_avatar__BVier")))
                    img_url = image.get_attribute("src")
                    print(f"Image got ")

                    self.driver.implicitly_wait(2)
                    # time.sleep(1)

                    click_dr = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH,f'''//*[@id="modalRoot"]/div/div/div/div[3]/div/div/div[{j}]/div[2]/div/div/div/div/div[1]/a/span''')))
                    self.driver.execute_script("arguments[0].scrollIntoView();", click_dr)
                    self.driver.execute_script("arguments[0].click();", click_dr)
                    print(f"Clicked about anchor tag")
                    time.sleep(2)
                    self.driver.implicitly_wait(5)
                    time.sleep(2)

                    try:
                        self.driver.implicitly_wait(5)
                        about = WebDriverWait(self.driver, 10).until( EC.presence_of_element_located((By.XPATH, '''//div[@class="AboutBlock_message__oiMr8"]'''))).text
                        time.sleep(2)

                    except NoSuchElementException as e:
                        print(f" This is ABOUT block  Errorrrr T ----------------///////------------  {e}")
                        time.sleep(3)
                        self.driver.execute_script("window.history.go(-1)")
                        time.sleep(3)
                        about = "Doctor's Information not available"
                        print(f"Except hit for --ABOUT NOT FOUND-- for hospital {hos_title} for doctor {dr_name} iteration ")
                        time.sleep(1)
                        df = df._append(
                            {"Hospital_Name": hos_title, "Department": dep_name, "Doctor": dr_name, "Dr_image": img_url, "About_dr": about},
                            ignore_index=True)
                        continue  # we can use pass

                    self.driver.implicitly_wait(2)

                    print(f"Got about {about.split()[:5]}")
                    # time.sleep(1)

                    # time.sleep(1)
                    df = df._append(
                        {"Hospital_Name": hos_title, "Department": dep_name, "Doctor": dr_name,
                         "Dr_image": img_url,
                         "About_dr": about},
                        ignore_index=True)

                    print(f"Got the entire row in {j} th iteration in {i}th hospital {hos_title}, dep {dep_name}")
                    time.sleep(1)
                    self.driver.execute_script("window.history.go(-1)")
                    self.driver.implicitly_wait(5)
                    time.sleep(2)

                time.sleep(2)
                self.driver.back()
                time.sleep(1)

            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                print("Errrrorrrrrr  last except block ======//=== ", e)
                time.sleep(3)
                self.driver.back()
                time.sleep(3)
                continue

        self.driver.quit()
        # print(df)
        df.to_csv("main_data_2.csv", index=False, header=True)



if __name__ == "__main__":
    start = time.time()
    url = "https://airomedical.com/hospitals"
    scraper = Scraper(url)
    scraper.scrape_data()
    end = time.time()
    print(f"Took {end - start} time to execute")








