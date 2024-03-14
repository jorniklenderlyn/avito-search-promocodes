from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from bs4 import BeautifulSoup
from itertools import permutations
from random import choice, randint
from threading import Thread
import json
import time
import string
import sys
import datetime


g_note_for_promocode = None
g_prev_promocode = None
g_quantity_promocode_checked = 0


class Note:
    def __init__(self, path='note.txt', mode='w', encoding='utf-8'):
        self.file = open(path, mode=mode, encoding=encoding)

    def AddLine(self, data, delimiter):
        if type(list()) == type(data):
            out_data = delimiter.join(list(map(str, data)))
        else:
            out_data = str(data)
        self.file.write(out_data + '\n')
        self.file.flush()


def check_promocode(browser: WebDriver, promocode: str) -> tuple:
    # getting json response
    browser.get(f'https://www.avito.ru/web/1/delivery/point/info?items%5B0%5D%5BitemId%5D=3729514611&items%5B0%5D%5Bquantity%5D=1&services%5B0%5D=636720%3Apochta&promocode={promocode}')
    # parsing json in html response
    page_html = BeautifulSoup(browser.page_source, 'html.parser')
    # parsing status in json
    status = json.loads(page_html.find(id='json').text)['result']['services'][0]['promocode']['status']
    # looking status of promocode
    message = json.loads(page_html.find(id='json').text)['result']['services'][0]['promocode']['message']
    if status == 'success':
        return message, True
    return message, False


def solution(login: str, password: str, browser: WebDriver, stratage: int, is_save_prev_promocode: bool, template: str):
    global g_quantity_promocode_checked, g_note_for_promocode, g_prev_promocode
    browser.get('https://avito.ru')
    browser.find_element(By.XPATH, '//*[contains(text(), "Вход и регистрация")]').click()
    while browser.page_source.find('name="login"') == -1:
        time.sleep(1)
    input_login = browser.find_element(By.XPATH, '//input[@name="login"]')
    input_login.clear()
    input_login.send_keys(login)
    input_password = browser.find_element(By.XPATH, '//input[@name="password"]')
    input_password.clear()
    input_password.send_keys(password)
    browser.find_element(By.XPATH, '//*[contains(text(), "Войти")]').click()
    time.sleep(10)

    note_for_good_promocode = g_note_for_promocode
    # key is message, value is ref to file maybe

    if stratage == 0:
        letters = string.ascii_uppercase + string.digits
        for length in range(6, 9):
            for p in permutations(letters, length):
                promocode = template.format(''.join(list(p)))
                is_checked = False
                n_attempt = 0
                while not is_checked:
                    if n_attempt == 5:
                        raise RuntimeError("bad browser")
                    try:
                        message, status = check_promocode(browser, promocode)
                        is_checked = True
                    except:
                        time.sleep(randint(1, 5))
                        n_attempt += 1
                        browser.refresh()
                print(promocode, status) if status else None
                if status:
                    note_for_good_promocode.AddLine([promocode, message], ';')
                g_quantity_promocode_checked = g_quantity_promocode_checked + 1
    elif stratage == 1:
        letters = list(string.ascii_uppercase + string.digits)
        i = 0
        prev_promocode = g_prev_promocode
        while True:
            changeable_part = ''
            for length in range(randint(6, 8)):
                changeable_part += choice(letters)
            if is_save_prev_promocode and changeable_part in prev_promocode:
                continue
            elif is_save_prev_promocode:
                prev_promocode.add(changeable_part)
            promocode = template.format(changeable_part)
            is_checked = False
            n_attempt = 0
            while not is_checked:
                if n_attempt == 5:
                    raise RuntimeError("bad browser")
                try:
                    message, status = check_promocode(browser, promocode)
                    is_checked = True
                except:
                    time.sleep(randint(1, 5))
                    n_attempt += 1
                    browser.refresh()
                    # with open('out.html', 'w') as f:
                    #     f.write(str(browser.page_source))
            print(promocode, status) if status else None
            if status:
                note_for_good_promocode.AddLine([promocode, message], ';')
            g_quantity_promocode_checked = g_quantity_promocode_checked + 1

            # browser.refresh()
            # time.sleep(1)
    elif stratage == 2:
        promocode = input('Promocode for checking: ')
        message, status = check_promocode(browser, promocode)
        if status:
            print('good', message)
        else:
            print('bad')
    else:
        print('No stratages with number:', stratage)
    sys.exit(0)


def start_solution(login: str, password:str, stratage: int, is_save_prev_promocode: bool, template: str) -> None:
    while True:
        try:
            browser = webdriver.Firefox()
            print('start')
        except Exception as err:
            print(err)
            continue
        try:
            solution(login, password, browser, stratage, is_save_prev_promocode, template=template)
        except Exception as err:
            print(err)
            try:
                browser.close()
            except:
                print('bad close, browser already closed')
                pass
        print('reopen browser')


def print_quantity_of_checked_promocode():
    i = 0
    while True:
        if g_quantity_promocode_checked // 100 > i:
            i = g_quantity_promocode_checked // 100
            print('quantity_promocode_checked', g_quantity_promocode_checked, datetime.datetime.now().time())
        time.sleep(5)


if __name__ == '__main__':
    stratage = 0
    is_save_prev_promocode = False
    quantity_browsers = 1
    template_of_promocode = 'AVT{}GUARD'

    i_stratage_flag = None
    if '-s' in sys.argv:
        i_stratage_flag = sys.argv.index('-s')
    elif '--stratage' in sys.argv:
        i_stratage_flag = sys.argv.index('--stratage')

    if i_stratage_flag:
        if len(sys.argv) > i_stratage_flag + 1 and sys.argv[i_stratage_flag + 1].isdigit:
            stratage = int(sys.argv[i_stratage_flag + 1])
            print('stratage', sys.argv[i_stratage_flag + 1])
    
    i_quantity_browsers_flag = None
    if '-q' in sys.argv:
        i_quantity_browsers_flag = sys.argv.index('-q')
    elif '--quantity' in sys.argv:
        i_quantity_browsers_flag = sys.argv.index('--quantity')
    
    if i_quantity_browsers_flag:
        if len(sys.argv) > i_quantity_browsers_flag + 1 and sys.argv[i_quantity_browsers_flag + 1].isdigit:
            quantity_browsers = int(sys.argv[i_quantity_browsers_flag + 1])
            print('quantity', sys.argv[i_quantity_browsers_flag + 1])
    
    i_template_flag = None
    if '-t' in sys.argv:
        i_template_flag = sys.argv.index('-t')
    elif '--template' in sys.argv:
        i_template_flag = sys.argv.index('--template')
    
    if i_template_flag:
        if len(sys.argv) > i_template_flag + 1:
            if '{}' in sys.argv[i_template_flag + 1]:
                template_of_promocode = sys.argv[i_template_flag + 1]
                print('template', sys.argv[i_template_flag + 1])

    if '--with-set' in sys.argv:
        is_save_prev_promocode = True
        print('set activated')

    login = input('login: ')
    password = input('password: ')

    note_name = input('output file name: ')
    g_note_for_promocode = Note(path=note_name, mode='a', encoding='utf-8')
    g_note_for_promocode.AddLine(['promocode', 'status'], ';')
    g_prev_promocode = set()
    g_quantity_promocode_checked = 0
    
    if stratage == 0:
        quantity_browsers = 1

    n_threading = quantity_browsers
    threadings = []
    
    for i_threading in range(n_threading):
        threadings.append(Thread(target=start_solution, args=(login, password, stratage, is_save_prev_promocode, template_of_promocode)))
    
    threadings.append(Thread(target=print_quantity_of_checked_promocode))
    
    for t in threadings:
        t.start()

