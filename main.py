import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from objects import Cours, Day, EDTDate, EDTTime, Week
import os, time, dotenv, re, json, ics, pytz, pickle
from datetime import datetime
import utils as U

dotenv.load_dotenv()

EDIT_SET_COOKIES_PAGE = "https://ws-edt-cd.wigorservices.net/login.php"
EDT_PAGE = "https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?action=posEDTLMS&serverID=C"
LOGIN_PAGE = "https://cas-p.wigorservices.net/cas/login"
TIMEZONE = "Europe/Paris"
COOKIES_FILE = "output/cookies.pkl"

def save_cookies(driver, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, path):
    if not os.path.exists(path):
        return
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def getSemainesDeCours(driver: webdriver.Firefox) -> list:
    semaines = []
    masterCalendar = driver.find_element(By.ID, "I_Du_MasterCal")
    for month in masterCalendar.find_elements(By.CLASS_NAME, "I_Du_MoisCal"):
        for week in month.find_elements(By.CLASS_NAME, "I_Du_SemCal"):
            isWorkingWeek = False
            for day in week.find_elements(By.CLASS_NAME, "I_Du_CaseCal"):
                if day.value_of_css_property("background-color") == "rgb(204, 204, 204)":
                    isWorkingWeek = True
                    break
            if not isWorkingWeek:
                continue
            semaines.append(week.get_attribute('onclick'))
    return semaines

def getJoursDeLaSemaine(driver: webdriver.Firefox, _week: list[int]) -> list[Day]:
    days: list[Day] = [None, None, None, None, None]
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.Case"))
        )
        cours = driver.find_elements(By.CSS_SELECTOR, "div.Case")
        for _cours in cours:
            if "Apres" == _cours.get_attribute("id"): continue
            _day_index = U.get_day_by_left(_cours)

            if days[_day_index] is None:
                days[_day_index] = Day(U.get_day_by_index(driver, _day_index), [])

            start, end = U.get_cours_start_and_end_time(_cours)
            if start is None or end is None:
                print(f"Skipping course due to missing start or end time: {_cours}")
                print(_week)
                print(_day_index)
                continue

            name = U.get_cours_name(_cours)
            if not name:
                print(f"Skipping course due to missing name: {_cours}")
                print(_week)
                print(_day_index)
                continue

            salle = U.get_cours_salle(_cours)
            if not salle:
                print(f"Skipping course due to missing salle: {_cours}")
                print(_week)
                print(_day_index)
                continue

            prof, class_name = U.get_cours_info(_cours)

            cours_item = Cours(name, EDTDate(_week[0] + _day_index, _week[1], _week[2]), start, end, salle, prof, class_name)
            days[_day_index].cours.append(cours_item)
    except Exception as e:
        print(f"An error occurred while locating the elements: {e}")
    return days

def main():
    username = os.getenv("360_USERNAME")
    password = os.getenv("360_PASSWORD")

    geckodriver_path = "./geckodriver.exe"
    if not os.path.exists(geckodriver_path):
        print("Geckodriver not found at path: " + geckodriver_path)
        print("Please download the latest geckodriver from https://github.com/mozilla/geckodriver/releases")
        return
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    # options.add_argument("--window-size=1920,1080")
    
    service = FirefoxService(executable_path=geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    
    driver.get(EDIT_SET_COOKIES_PAGE)

    if os.path.exists(COOKIES_FILE):
        load_cookies(driver, COOKIES_FILE)

    driver.get(EDT_PAGE)

    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    
    if driver.current_url.startswith(LOGIN_PAGE):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.NAME, "submitBtn").click()

        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        save_cookies(driver, COOKIES_FILE)

    while "Runtime Error" in driver.title:
        driver.refresh()
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        save_cookies(driver, COOKIES_FILE)

    semaines = getSemainesDeCours(driver)

    days: list[Day] = []

    base_url = driver.current_url

    for semaine in semaines:
        month, day, year = re.search(r"I_Du_Click_Semaine\('(\d{2})/(\d{2})/(\d{4})'\)", semaine).groups()
        week = [int(day), int(month), int(year)]

        driver.get(base_url + "&date=" + month + "/" + day + "/" + year)

        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        while "Runtime Error" in driver.title:
            driver.refresh()
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        jours = getJoursDeLaSemaine(driver, week)
        days.extend(jours)

    days = [day for day in days if day is not None]

    with open("output/days.json", "w", encoding="UTF-8") as f:
        f.write(
            json.dumps(
                [day.json() for day in days],
                indent=4,
                ensure_ascii=False
            )
        )

    driver.quit()

    convert_to_ics()

def convert_to_ics():
    with open("output/days.json", "r", encoding="UTF-8") as f:
        days = json.loads(f.read())

    calendar = ics.Calendar()
    tz = pytz.timezone(TIMEZONE)
    for day in days:
        for cours in day["cours"]:
            uid = f"{(cours['class_name'] + '_' if cours['class_name'] else '')}{cours['date']}_{cours['start']}_{cours['end']}"
            uid = uid.lower().replace(" ", "_").replace(":", "_").replace("/", "_")
            event = ics.Event()
            event.uid = uid
            event.name = (cours["name"] + " - " + cours["room"]).title()
            event.description = (cours["teacher"] + " - " + (cours["class_name"] if cours["class_name"] else "Classe inconnue")).title()
            event.begin = tz.localize(datetime.strptime(f"{cours['date']} {cours['start']}", "%Y-%m-%d %H:%M:%S"))
            event.end = tz.localize(datetime.strptime(f"{cours['date']} {cours['end']}", "%Y-%m-%d %H:%M:%S"))
            calendar.events.add(event)

    with open("output/edt.ics", "w", encoding="utf-8") as f:
        f.writelines(calendar)

if __name__ == '__main__':
    if not os.path.exists("output"):
        os.makedirs("output")

    is_edt_loaded = os.path.exists("output/days.json")
    if is_edt_loaded:
        answer = ""
        while answer not in ["S", "C"]:
            answer = input("Emploi du temps déjà chargé. Souhaitez-vous le recharger ou le convertir ? (S/C): ")
        if answer == "S":
            main()
        if answer == "C":
            convert_to_ics()
    else:
        main()