import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import datetime
import validators
from icecream import ic
from selenium_stealth import stealth
import time
ic.configureOutput(includeContext=True)
def time_format():
    return f'{datetime.datetime.now()}|> '

ic.configureOutput(prefix=time_format)


def sleep(seconds):
    for i in range(seconds):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            continue


def exists_by_text2(driver, text):
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH,"//*[contains(text(), '"+str(text)+"')]")))
    except Exception:
        return False
    return True


def exists_by_xpath(driver, thex, howlong):
    try:
        WebDriverWait(driver, howlong).until(ec.visibility_of_element_located((By.XPATH, thex)))
    except:
        return False


def exists_by_text(driver, text):
    driver.implicitly_wait(2)
    try:
        driver.find_element_by_xpath("//*[contains(text(), '"+str(text)+"')]")
    except NoSuchElementException:
        driver.implicitly_wait(5)
        return False
    driver.implicitly_wait(5)
    return True


def user_logged_in(driver):
    try:
        driver.find_element_by_xpath('//*[@id="file-type"]')
    except NoSuchElementException:
        driver.implicitly_wait(5)
        return False
    driver.implicitly_wait(5)
    return True


def wait_for_xpath(driver, x):
    while True:
        try:
            driver.find_element_by_xpath(x)
            return True
        except:
            time.sleep(0.1)
            pass


def scroll_to_bottom(driver):
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def file_to_list(filename):
    colabs = []
    for line in open(filename):
        if validators.url(line):
            colabs.append(line)
    return colabs


def switch_to_tab(driver, tab_index):
    print("Switching to tab " + str(tab_index))
    try:
        driver.switch_to.window(driver.window_handles[tab_index])
    except:
        print("Error switching tabs.")
        return False


def new_tab(driver, url, tab_index):
    print("Opening new tab to " + str(url))
    try:
        driver.execute_script("window.open('" + str(url) + "')")
    except:
        print("Error opening new tab.")
        return False
    switch_to_tab(driver, tab_index)
    return True
    

fork = sys.argv[1]
timeout = int(sys.argv[2])
colab_urls = file_to_list('notebooks.csv')

if len(colab_urls) > 0 and validators.url(colab_urls[0]):
    colab_1 = colab_urls[0]
else:
    raise Exception('No notebooks')

chrome_options = Options()
# chrome_options.add_argument('--headless') # uncomment for headless mode
chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument("user-data-dir=profile") # left for debugging
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--enable-javascript")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

wd = webdriver.Chrome('chromedriver', options=chrome_options)

wd.get(colab_1)
try:
    for cookie in pickle.load(open("gCookies.pkl", "rb")):
        wd.add_cookie(cookie)
except Exception:
    pass
wd.get(colab_1)



if exists_by_text(wd, "Sign in"):
    print("No auth cookie detected. Please login to Google.")
    wd.close()
    wd.quit()
    chrome_options_gui = Options()
    chrome_options_gui.add_argument('--no-sandbox')
    #chrome_options.add_argument("user-data-dir=profile") # left for debugging
    chrome_options_gui.add_argument('--disable-infobars')
    wd = webdriver.Chrome('chromedriver', options=chrome_options_gui)
    wd.get("https://accounts.google.com/signin")
    wait_for_xpath(wd, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/c-wiz/div/div[4]/div/div/header/div[2]')
    print("Login detected. Saving cookie & restarting connection.")
    pickle.dump(wd.get_cookies(), open("gCookies.pkl", "wb"))
    wd.close()
    wd.quit()
    wd = webdriver.Chrome('chromedriver', options=chrome_options)
while True:
    for colab_url in colab_urls:
        complete = False
        wd.get(colab_url)
        print("Logged in.") # for debugging
        running = False
        wait_for_xpath(wd, '//*[@id="file-menu-button"]')
        print('Notebook loaded.')
        sleep(10)
        
        ic('before...')
        i = 0
        while True:
            ic('...')
            if exists_by_text(wd, "Runtime disconnected"):
                ic("runtime disconnected")
                try:
                    wd.find_element_by_xpath('//*[@id="ok"]').click()
                    pass
                except NoSuchElementException:
                    pass
            if exists_by_text2(wd, "Notebook loading error"):
                wd.get(colab_url)
                ic("loading error")
            try:
                ic()
                time.sleep(20)
                wd.find_element_by_xpath('//*[@id="file-menu-button"]/div/div/div[1]')
                wd.find_element_by_xpath("//body").click()
                if not running:
                    ic()
                    
                    actions = ActionChains(wd)
                    actions.key_down(Keys.CONTROL)
                    actions.key_down(Keys.SHIFT)
                    actions.send_keys("q")

                    actions.key_up(Keys.CONTROL)
                    actions.key_up(Keys.SHIFT)
                    actions.perform()

                    # exists_by_xpath(wd, '//*[@id="ok"]', 10)
                    # wd.find_element_by_xpath('//*[@id="ok"]').click()
                    sleep(3)
                    actions = ActionChains(wd)
                    # actions.click(body)
                    actions.key_down(Keys.CONTROL)
                    actions.key_down(Keys.SHIFT)
                    actions.send_keys("r")
                    
                    actions.key_up(Keys.CONTROL)
                    actions.key_up(Keys.SHIFT)

                    actions.perform()

                    sleep(10)
                    element = wd.find_element_by_xpath("//body")
                    element.send_keys(Keys.CONTROL,Keys.SHIFT, 'r')

                   
                    
                    # wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.SHIFT + "Q")
                    # wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.SHIFT + "R")
                    ic()
                    # exists_by_xpath(wd, '//*[@id="ok"]', 10)
                    ic()
                    # wd.find_element_by_xpath('//*[@id="ok"]').click()
                    sleep(10)
                    ic()
                    # wd.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.F9)
                    running = True
                    ic('####RUNNING1')

            except Exception as e:
                ic(e)
                pass
            if running:
                ic('####RUNNING2')
                try:
                    wd.find_element_by_css_selector('.notebook-content-background').click()
                    #actions = ActionChains(wd)
                    #actions.send_keys(Keys.SPACE).perform()
                    scroll_to_bottom(wd)
                    print("performed scroll")
                except:
                    ic("scroll performed error")
                    pass
                for frame in wd.find_elements_by_css_selector('.output_text'):
                    ic('iframe')
                    # actions = ActionChains(wd)
                    # actions.move_to_element(frame)
                    # actions.perform()

                    # wd.switch_to.frame(frame)
                    '''
                    links = browser.find_elements_by_partial_link_text('oauth2/auth')
                    for link in links:
                        new_tab(wd, link.get_attribute("href"), 1)
                        wd.find_element_by_css_selector('li.M8HEDc:nth-child(1)>div:nth-child(1)').click()
                        wd.find_element_by_css_selector('#submit_approve_access>content:nth-child(3)>span:nth-child(1)').click()
                        auth_code = wd.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div/div/form/content/section/div/content/div/div/div/textarea').text
                    '''
                    for output in wd.find_elements_by_css_selector('.output_text'):
                        ic()
                        ic(output.text)
                        if fork.strip() in output.text.strip():
                            
                            
                            running = False
                            complete = True
                            print("Completion string found. Waiting for next cycle.")
                            break
                    
                        time.sleep(10)
                    time.sleep(10)
                    
                    wd.switch_to.default_content()
                    if complete:
                        break
                if complete:
                    
                    ic('complete')
                    break
            
            if i > 10:
                break
            i += 1        

    sleep(timeout)
