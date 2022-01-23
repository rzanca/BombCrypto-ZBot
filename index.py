# -*- coding: utf-8 -*-    
from src.logger import logger, loggerMapClicked
from cv2 import cv2
from os import listdir
from random import randint
from random import random
from pyclick import HumanClicker
from datetime import datetime

import numpy as np
import mss
import pyautogui
import time
import sys
import yaml
import telegram
import os

if __name__ == '__main__':
    with open('./config.yaml', 'r', encoding='utf-8') as open_yml:
        c = yaml.safe_load(open_yml)
    with open('./telegram.yaml', 'r', encoding='utf-8') as teleg:
        t = yaml.safe_load(teleg)

ct = c['threshold']
ch = c['home']
tl = t['telegram_log']
pyautogui.PAUSE = c['time_intervals']['interval_between_moviments']
pyautogui.FAILSAFE = False
hc = HumanClicker()
pyautogui.MINIMUM_DURATION = 0.1
pyautogui.MINIMUM_SLEEP = 0.1
pyautogui.PAUSE = 2
TELEGRAM_BOT_TOKEN = tl['token']
TELEGRAM_CHAT_ID  = tl['chatid']
CONTA = tl['conta']

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def telsendtext(bot_message, num_try=0):
    global bot
    try:
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=bot_message)
    except:
        if num_try == 1:
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            return telsendtext(bot_message, 1)
        return 0

def telsendphoto(photo_path, num_try=0):
    global bot
    try:
        return bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open(photo_path, 'rb'))
    except:
        if num_try == 1:
            bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
            return telsendphoto(photo_path, 1)
        return 0

test = telsendtext('🔌 Bot inicializado na ' + CONTA + '. \n\n 💰 É hora de faturar alguns BCoins!!!')

saldo_atual = 0.0


cat = '''
>>---> BombCrypto ZBot - v 0.1.0 

>>---> https://github.com/rzanca/bombcrypto-zbot/

>>---> Curtiu? Faça sua doação... Wallet BEP20
>>---> 0xc11ed49D4c8cAe4EBdE49091c90543b17079d894

>>---> Pressione ctrl + c ou feche o prompt para parar o BOT.

>>---> As configurações variáveis estão em config.yaml'''

def addrandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)

def movetowithrandomness(x, y, t):
    hc.move((int(x), int(y)), t)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

images = load_images()

def loadheroestosendhome():
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d Herois que devem ser mandados para casa carregados.' % len(heroes))
    return heroes

def show(rectangles, img = None):
    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))
    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickbtn(img, name=None, timeout=3, threshold=ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
    start = time.time()
    clicked = False
    while not clicked:
        matches = positions(img, threshold=threshold)
        if len(matches) == 0:
            hast_timed_out = time.time() - start > timeout
            if hast_timed_out:
                if not name is None:
                    pass
                return False
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2
        movetowithrandomness(pos_click_x, pos_click_y, 1)
        pyautogui.click()
        return True

def printscreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printscreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def scroll():
    hero_item_list = positions(images['hero-item'], threshold=ct['common'])
    if len(hero_item_list) == 0:
        return
    x, y, w, h = hero_item_list[len(hero_item_list) - 1]
    movetowithrandomness(x, y, 1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0, -c['click_and_drag_amount'], duration=1, button='left')

def sendall():
    buttons = positions(images['send-all'], threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        movetowithrandomness(x + (w / 2), y + (h / 2), 1)
        pyautogui.click()
    return len(buttons)

def restall():
    logger('🏢 Colocando heróis para descansar')
    gotoheroes()
    time.sleep(1)
    buttons = positions(images['rest-all'], threshold=ct['go_to_work_btn'])
    for (x, y, w, h) in buttons:
        movetowithrandomness(x + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        time.sleep(2)
    return len(buttons)

def ishome(hero, buttons):
    y = hero[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def isworking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickgreenbarbuttons():
    offset = 140

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d Barras verdes detectadas' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d Botoes detectados' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        if not isworking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d Botoes com barra verde detectados' % len(not_working_green_bars))
        logger('👆 Clicando em %d herois' % len(not_working_green_bars))

    hero_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger('⚠️ Houve muitos cliques em herois, tente aumentar o go_to_work_btn threshold')
            return        
    return len(not_working_green_bars)

def clickfullbarbuttons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isworking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicando em %d herois' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        movetowithrandomness(x + offset + (w / 2), y + (h / 2), 1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)

def gotoheroes():
    if clickbtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    time.sleep(1)
    clickbtn(images['hero-icon'])
    time.sleep(randint(1,3))

def gotogame():
    clickbtn(images['x'])

    clickbtn(images['treasure-hunt-icon'])

def refreshheroespositions():

    logger('🔃 Atualizando posicao dos herois')
    clickbtn(images['go-back-arrow'])
    clickbtn(images['treasure-hunt-icon'])

def login():
    global login_attempts
    logger('😿 Checando se o jogo se desconectou')
    if clickbtn(images['connect-wallet'], timeout=10):
        logger('🎉 Botão de conexão da carteira encontrado, logando!')
        login_attempts = login_attempts + 1
        if clickbtn(images['select-wallet-2'], timeout=8):
            time.sleep(10)
            refreshheroes()
            login_attempts = 0
            return

    if login_attempts > 3:
        logger('🔃 Muitas tentativas de login, atualizando')
        login_attempts = 0
        pyautogui.hotkey('ctrl', 'f5')
        return

    else:
        pass
    if clickbtn(images['ok'], timeout=5):
        time.sleep(10)
        login()
        pass

def sendheroestowork():
    if c['select_heroes_mode'] == 'full':
        return clickfullbarbuttons()
    elif c['select_heroes_mode'] == 'green':
        return clickgreenbarbuttons()
    else:
        return sendall()

def sendheroeshome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len (hero_positions) == 0:
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('Nenhum heroi que deveria ser enviado para casa encontrado.')
        return
    print(' %d Herois que devem ser enviados para casa encontrados.' % n)
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not ishome(position, go_home_buttons):
            print(isworking(position, go_work_buttons))
            if(not isworking(position, go_work_buttons)):
                print ('Heroi não está trabalhando, enviando para casa.')
                movetowithrandomness(go_home_buttons[0][0] + go_home_buttons[0][2] / 2, position[1] + position[3] / 2, 1)
                pyautogui.click()
            else:
                print ('Heroi está trabalhando, não será enviado para casa.')
        else:
            print('Heroi já está na casa, ou a casa está cheia.')

def refreshheroes():
    logger('🏢 Procurando heróis para trabalhar')

    gotoheroes()

    if c['select_heroes_mode'] == 'full':
        logger('⚒️ Enviando heróis com a energia cheia para o trabalho', color='green')
    elif c['select_heroes_mode'] == 'green':
        logger('⚒️ Enviando heróis com a energia verde para o trabalho', color='green')
    else:
        logger('⚒️ Enviando todos heróis para o trabalho', color='green')

    empty_scrolls_attempts = c['scroll_attempts']
    send_all_work = False
    if not ch['enable'] and c['select_heroes_mode'] == 'all':
        time.sleep(1)
        send_all_work = sendall()
        if send_all_work:
            logger('💪 ALL heroes sent to work')
        time.sleep(2)

    if not send_all_work:
        while empty_scrolls_attempts > 0:
            sendheroestowork()
            sendheroeshome()
            empty_scrolls_attempts = empty_scrolls_attempts - 1
            scroll()
            time.sleep(2)
        logger('💪 {} Heróis enviados para o trabalho'.format(hero_clicks))
    gotogame()


def gobalance():
    logger('Consultando seu saldo')
    time.sleep(2)
    global saldo_atual
    clickbtn(images['consultar-saldo'])
    i = 10
    coins_pos = positions(images['coin-icon'], threshold=ct['default'])
    while len(coins_pos) == 0:
        if i <= 0:
            break
        i = i - 1
        coins_pos = positions(images['coin-icon'], threshold=ct['default'])
        time.sleep(5)

    if len(coins_pos) == 0:
        logger('Saldo não encontrado.')
        clickbtn(images['x'])
        return

    left, top, width, height = coins_pos[0]
    left = left - 44
    top = top + 130
    width = 200
    height = 50

    myscreen = pyautogui.screenshot(region=(left, top, width, height))
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\targets\saldo1.png'
    myscreen.save(img_dir)
    time.sleep(2)
    enviar = ('🚨 Seu saldo Bcoins 🚀🚀🚀 na ' + CONTA)
    telsendtext(enviar)
    telsendphoto(img_dir)

    clickbtn(images['x'])



def getdifference(then, now=datetime.now(), interval='horas'):

    duration = now - then
    duration_in_s = duration.total_seconds()

    yr_ct = 365 * 24 * 60 * 60  
    day_ct = 24 * 60 * 60  
    hour_ct = 60 * 60  
    minute_ct = 60

    def yrs():
        return divmod(duration_in_s, yr_ct)[0]

    def days():
        return divmod(duration_in_s, day_ct)[0]

    def hrs():
        return divmod(duration_in_s, hour_ct)[0]

    def mins():
        return divmod(duration_in_s, minute_ct)[0]

    def secs():
        return duration_in_s

    return {
        'anos': int(yrs()),
        'dias': int(days()),
        'horas': int(hrs()),
        'minutos': int(mins()),
        'segundos': int(secs()),
    }[interval]

def timespendtomap():
    try:
        data_inicio_mapa = None
        caminho = (
            os.path.dirname(os.path.realpath(__file__)) + r'\savedvars\tempo_mapa.txt'
        )
        with open(caminho, 'r') as text_file:
            data_inicio_mapa = text_file.readline()
            if data_inicio_mapa == '':
                data_inicio_mapa = datetime.now()

            if not isinstance(data_inicio_mapa, datetime):
                data_inicio_mapa = datetime.strptime(
                    data_inicio_mapa, '%Y-%m-%d %H:%M:%S.%f'
                )
            intervalo = 'horas'
            horas_gastas = getdifference(
                data_inicio_mapa, now=datetime.now(), interval=intervalo
            )
            if horas_gastas == 0:
                intervalo = 'minutos'
                horas_gastas = getdifference(
                    data_inicio_mapa, now=datetime.now(), interval=intervalo
                )
            if horas_gastas == 0:
                intervalo = 'segundos'
                horas_gastas = getdifference(
                    data_inicio_mapa, now=datetime.now(), interval=intervalo
                )

            telsendtext(
                f'Demoramos {horas_gastas} {intervalo} para concluir o mapa na ' + CONTA + '.'
            )
        with open(caminho, 'w') as text_file_write:
            data_inicio_mapa = datetime.now()
            text_file_write.write(str(data_inicio_mapa))

    except:
        logger('Não conseguiu obter informações do tempo de conclusão do mapa.')
    
def main():
    global hero_clicks
    global login_attempts
    global last_log_is_progress
    hero_clicks = 0
    login_attempts = 0
    last_log_is_progress = False

    global images
    images = load_images()

    if ch['enable']:
        global home_heroes
        home_heroes = loadheroestosendhome()
    else:
        print('>>---> Modo Casa não habilitado')
    print('\n')

    print(cat)
    time.sleep(5)
    t = c['time_intervals']

    last = {
    'login' : 0,
    'heroes' : 0,
    'new_map' : 0,
    'refresh_heroes' : 0,
    'balance' :0,
    'refresh_page': time.time()
    }


    while True:
        now = time.time()

        if now - last['refresh_page'] > addrandomness(t['check_for_refresh_page'] * 60):
            logger('🔃 Atualizando o jogo')
            last['refresh_page'] = now
            restall()
            pyautogui.hotkey('ctrl', 'f5')
            
        if now - last['heroes'] > addrandomness(t['send_heroes_for_work'] * 60):
            last['heroes'] = now
            refreshheroes()
           
        if now - last['login'] > addrandomness(t['check_for_login'] * 60):
            sys.stdout.flush()
            last['login'] = now
            login()

        if now - last['new_map'] > t['check_for_new_map_button']:
            last['new_map'] = now

            if clickbtn(images['new-map']):
                telsendtext(f'Completamos mais um mapa!')
                timespendtomap()
                loggerMapClicked()
                time.sleep(3)
                num_jaulas = len(positions(images['jail'], threshold=0.8))
                if num_jaulas > 0:
                    telsendtext(
                        f'Parabéns temos {num_jaulas} nova(s) jaula(s) no novo mapa 🎉🎉🎉.'
                        )

        if now - last['refresh_heroes'] > addrandomness(t['refresh_heroes_positions'] * 60):
            last['refresh_heroes'] = now
            refreshheroespositions()
            
        if now - last['balance'] > addrandomness(t['get_saldo'] * 60):
            last['balance'] = now
            gobalance()

        logger(None, progress_indicator=True)

        sys.stdout.flush()

        time.sleep(1)

main()
