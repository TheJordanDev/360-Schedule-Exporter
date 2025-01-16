import re
from objects import EDTTime
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

def get_cours_hour(cours: WebElement) -> int:
    slope = 10.5555
    intercept = 15.1505

    percentage = cours.value_of_css_property('top')
    if percentage:
        return round((float(percentage.split('.')[0]) - intercept) / slope)
    return 0

def get_cours_duration(cours: WebElement) -> int:
    slope = 10.55555
    intercept = -0.8

    style = cours.get_attribute('style')
    if style:
        match = re.search(r'height:\s*([\d.]+)%', style)
        if match:
            height = float(match.group(1))
            return round((height + intercept) / slope)
    return 0

def get_day_by_left(cours: WebElement) -> int:
    style = cours.get_attribute('style')
    if style:
        match = re.search(r'left:\s*([\d.]+)%', style)
        if match:
            left = float(match.group(1))
            if 103 <= left < 122:
                return 0
            elif 122 <= left < 141:
                return 1
            elif 141 <= left < 161:
                return 2
            elif 161 <= left < 180:
                return 3
            elif 180 <= left < 200:
                return 4
    print(f"Error: Could not find day by left: {style}")
    return 0

def get_day_by_index(driver: Firefox, index: int) -> str:
    todays_index = index + 5
    day = driver.find_elements(By.CSS_SELECTOR, "div.Jour")[todays_index]
    if day:
        tc_jour = day.find_element(By.CSS_SELECTOR, "td.TCJour")
        return tc_jour.text
    return ""

def get_cours_salle(cours: WebElement) -> str:
    try:
        salle = cours.find_element(By.CSS_SELECTOR, "td.TCSalle")
        salle_text = salle.text.split(":")[1]
        if salle_text == "Aucune":
            return "Aucune"
        else:
            num_salle = salle_text.split("-")[0].strip()
            return num_salle
    except Exception as e:
        print(f"An error occurred while locating the salle element: {e}")
    return ""

def get_cours_info(cours: WebElement) -> tuple:
    try:
        prof = cours.find_element(By.CSS_SELECTOR, "td.TCProf")
        inner_html = prof.get_attribute('innerHTML')
        inner_html = re.sub(r'<img[^>]*>', '', inner_html)
        inner_html = re.sub(r'<span[^>]*>.*?<\/span>', '', inner_html)
        profs = inner_html.split("<br>")
        prof_name = profs[0].strip() if len(profs) > 0 else ""
        promo = profs[1].strip() if len(profs) > 1 else ""
        return prof_name, promo
    except Exception as e:
        print(f"An error occurred while locating the prof element: {e}")
    return "", ""

def get_cours_start_and_end_time(cours: WebElement) -> tuple:
    try:
        time_element = cours.find_element(By.CSS_SELECTOR, "td.TChdeb")
        times = time_element.text.split(" - ")
        start_hour, start_minute = times[0].strip().split(":")
        end_hour, end_minute = times[1].strip().split(":")
        return EDTTime(int(start_hour), int(start_minute)), EDTTime(int(end_hour), int(end_minute))
    except Exception as e:
        print(f"An error occurred while locating the time element: {e}")
        return None, None

def get_cours_name(cours: WebElement) -> str:
    try:
        t_case = cours.find_element(By.CSS_SELECTOR, "td.TCase")
        if t_case:
            return t_case.text
    except Exception as e:
        print(f"An error occurred while locating the name element: {e}")
    return ""