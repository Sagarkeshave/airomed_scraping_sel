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

    def scrape_data(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(20)

        names = self.driver.find_elements(By.CLASS_NAME, "HospitalCard_name__UZRIa")
        hospital_names = [name.text for name in names]
        print(f"Total {len(hospital_names)} hospitals scraped ")

        df = pd.DataFrame(columns=['Hospital_Name', 'Doctor', 'Department', "Dr_image"])

        for i in range(1, len(hospital_names) + 1):
            try:
                hos_name = self.driver.find_element(By.XPATH, f'//*[@id="hospitalsCards"]/div[{i}]/div[1]/div[3]/div[1]/div/a/h2')
                self.driver.execute_script("arguments[0].scrollIntoView();", hos_name)
                self.driver.execute_script("arguments[0].click();", hos_name)
            except NoSuchElementException as e:
                print(f"Show Hospital button not found. Skipping {i}th iteration. and thrown error ---- {e}")
                continue

            self.driver.implicitly_wait(3)

            hos_title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//h1[@class="MainInfo_titleName__rhrVM"]')))
            print(f"Accessed hospital {hos_title.text} hospital no. {i}")

            if hos_title.text == "M1 Private Clinic Munich": # this html page lackes required tags
                self.driver.back()
                continue

            self.driver.implicitly_wait(3)

            try:
                button_selector = "button.Button_button__8B4nB.Button_custom__SdTYs.outlined.DepartmentsSection_showMoreButton__F7Cgv"
                show_more = self.driver.find_element(By.CSS_SELECTOR, button_selector)
                self.driver.execute_script("arguments[0].scrollIntoView();", show_more)
                self.driver.execute_script("arguments[0].click();", show_more)
                time.sleep(1)
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Show More button not found in {hos_title.text} at {i}th. Skipping this hospital. at ")
                self.driver.back()
                continue


            self.driver.implicitly_wait(2)

            dep = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'DescriptionList_header__bdeSz DepartmentsSection_header__1jGQI')]")
            dep_len = len(dep)

            self.driver.implicitly_wait(5)

            try:
                for j in range(1, dep_len - 4):
                    self.driver.implicitly_wait(3)

                    try:
                        # Clicking on each iteration of doctor profile
                        click = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="modalRoot"]/div/div/div/div[3]/div/div/div[{j}]/div[1]/div')))
                    except (NoSuchElementException, WebDriverException) as e:
                        print(f"Click + element not present at {j} iteration in {hos_title.text}, thrown erroe == {e}")
                        self.driver.back()
                        continue

                    self.driver.execute_script("arguments[0].scrollIntoView();", click)
                    self.driver.execute_script("arguments[0].click();", click)

                    self.driver.implicitly_wait(3)
                    hos_title = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//h1[@class="MainInfo_titleName__rhrVM"]')))
                    self.driver.implicitly_wait(2)
                    dr_name = self.driver.find_element(By.XPATH, f'//*[@id="modalRoot"]/div/div/div/div[3]/div/div/div[{j}]/div[2]/div/div/div/div/div[1]/a').text
                    self.driver.implicitly_wait(2)
                    dep_name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="modalRoot"]/div/div/div/div[3]/div/div/div[{j}]/div[1]/div/div/div/div'))).text
                    self.driver.implicitly_wait(2)
                    image = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".DepartmentDoctorItem_avatar__BVier")))
                    img_url = image.get_attribute("src")
                    self.driver.implicitly_wait(2)
                    df = df._append({"Hospital_Name": self.driver.title, "Doctor": dr_name, "Department": dep_name, "Dr_image": img_url}, ignore_index=True)
            except (TimeoutException, NoSuchElementException, WebDriverException) as e:
                print(f"Internet down slow loading of website thrown error === {e}")
                continue

            self.driver.back()
            time.sleep(1)

        self.driver.quit()
        # print(df)
        df.to_csv("all_url_prod.csv", index=False, header=True)

if __name__ == "__main__":

    start = time.time()
    url = "https://airomedical.com/hospitals"
    scraper = Scraper(url)
    scraper.scrape_data()
    end = time.time()
    print(f"Took {end-start} time to execute")

