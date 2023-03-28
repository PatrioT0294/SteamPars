import re
import time
import requests
import json
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# url1 = 'https://steamcommunity.com/market/listings/730/StatTrak%E2%84%A2%20M4A4%20%7C%20Zirka%20%28Minimal%20Wear%29'
# url2 = 'https://steamcommunity.com/market/priceoverview/?country=RU&currency=1&appid=730&market_hash_name=StatTrak%E2%84%A2%20M4A4%20|%20Zirka%20(Minimal%20Wear)'
# get_data_with_selenium(url1, url2)

fault = False
# regex_price = re.compile(r'\d+\.\d+|\d+')
regex_price = re.compile(r'(\d+\.\d+|\d+|\d+,\d+\.\d+|\d+|\d+,\d+) USD')
inventory_dict = json.load(open('inventory_new.json', 'r'))
not_interested = ["Graffiti", "Pass", "Tool", "Collectible"]
current_date = date.today()
yesterday = date.today() - timedelta(days=1)
headers = {"Host": "steamcommunity.com",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
           "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
           "Accept-Encoding": "gzip, deflate, br",
           "Connection": "keep-alive",
           "Upgrade-Insecure-Requests": "1",
           "Sec-Fetch-Dest": "document",
           "Sec-Fetch-Mode": "navigate",
           "Sec-Fetch-Site": "cross-site",
           "Cache-Control": "max-age=0"}
cookies = {'ActListPageSize': '10',
           'timezoneOffset': '10800,0',
           '_ga': 'GA1.2.1611490937.1668268330',
           'browserid': '2668973627388810656',
           'steamCurrencyId': '5',
           'recentlyVisitedAppHubs': '493520,1272080,865360',
           'strInventoryLastContext': '730_2',
           'extproviders_730': 'steam',
           'steamLoginSecure': '76561197999431019||eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MENDRV8yMURCMUYwMF8wNDg3QiIsICJzdWIiOiAiNzY1NjExOTc5OTk0MzEwMTkiLCAiYXVkIjogWyAid2ViIiBdLCAiZXhwIjogMTY3NDAzMDU5MSwgIm5iZiI6IDE2NjUzMDI1MzgsICJpYXQiOiAxNjczOTQyNTM4LCAianRpIjogIjE3QTBfMjFFQkIyRUNfMURGN0YiLCAib2F0IjogMTY3Mjg1NzgxOCwgInJ0X2V4cCI6IDE2OTEyNDQ0ODAsICJwZXIiOiAwLCAiaXBfc3ViamVjdCI6ICIxNzYuOTkuMTU4LjE1NSIsICJpcF9jb25maXJtZXIiOiAiOTEuMTkzLjE3Ny4xNTIiIH0.uN1DRNNSTjFwpiMmXvv1OwjKQTvRH63064GiipXSRndDSK5py6vFaLxDPEfqpwKJiTzUExKolsQrqdeq4uyrDw',
           '_gid': 'GA1.2.839068405.1673942540',
           'sessionid': 'c29c1829e1c23c3a53e9507f'}
""" Заблокированные сначала """
trade_blocked_items = {"5192729257": "2727227113", "5192734839": "991959905", "5192728547": "3946324730", "5192729790": "3761545285", "5192733381": "1293508920", "5236486478": "1544067968"}

def update_storage_items(yesterday):
    """ Обновление информации о предметах в хранилищах (перенос информации за предыдущий день) """
    for item in inventory_dict['storage']['items'].items():
        if f'{current_date}' not in item[1]['count']:
            while f'{yesterday}' not in item[1]['count']:
                print(f'{yesterday} not in {item[1]["count"]}!')
                yesterday = yesterday - timedelta(days=1)
                print(f'yesterday: {yesterday}')
                time.sleep(2)
            item[1]['count'][f'{current_date}'] = item[1]['count'][f'{yesterday}']
    return inventory_dict

def update_inventory_info(inventory_dict):
    """ Получение URL инвентарей для последующего получения актулальной информации о них """
    for inv in inventory_dict.items():
        if inv[0] == 'total' or inv[0] == 'storage': # смотрим только словари main и secondary
            continue
        else:
            print(f'Текущий инвентарь {inv[0]}')
            inventory_url = inv[1]['url']
            inventory = inv[0]
            inventory_dict = get_inventory_info(inventory_url, headers, inventory)
            # print(f'INV DICT {inventory_dict}')
    json.dump(inventory_dict, open("inventory_new.json", "w+"))
    return inventory_dict

def get_inventory_info(inventory_url, headers, inventory):
    """ Получение актуальной информации об инвентаре """
    temp_dict = {}
    request = requests.get(inventory_url, headers=headers)
    get_inventory = request.json()
    # get_inventory = json.load(open("main_inventory.json", 'r'))
    # if get_inventory == None:
    #     print('Информация об инвентаре не получена')
    # else:
    for item_type in get_inventory['descriptions']:
        type = item_type['tags'][0]["localized_tag_name"]
        if item_type['classid'] in trade_blocked_items:
            print(f'blocked item {item_type["classid"]}, replace with {trade_blocked_items[item_type["classid"]]}')
            classid = trade_blocked_items[item_type['classid']]
        else:
            classid = item_type['classid']
        if classid not in inventory_dict[inventory]['items'] and type not in not_interested:
            inventory_dict[inventory]['items'][classid] = {'name': item_type['market_hash_name'],
                                                           'type': item_type['tags'][0]["localized_tag_name"], 'price': {}, 'count': {},
                                                           'market_count': {}, 'total_item_price': {}}
        if classid not in inventory_dict['total']['items'] and type not in not_interested:
            inventory_dict['total']['items'][classid] = {'name': item_type['market_hash_name'],
                                                         'type': item_type['tags'][0]["localized_tag_name"], 'price': {}, 'count': {},
                                                         'market_count': {}, 'total_item_price': {}}
        if classid not in temp_dict and type not in not_interested:
            temp_dict[classid] = 0
    for assets in get_inventory['assets']:
        if assets['classid'] in trade_blocked_items:
            current_asset = trade_blocked_items[assets['classid']]
        else:
            current_asset = assets['classid']
        if current_asset in temp_dict:
            temp_dict[current_asset] += int(assets['amount'])
    for item in temp_dict.items():
        inventory_dict[inventory]['items'][item[0]]['count'][f'{current_date}'] = item[1]
    return inventory_dict

def get_data_with_selenium(url, url2):
    """ Получение информации (цены, количество на ТП) по предметам с сайта Steam """
    global fault
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    options.headless = True
    market = {'price': '', 'count': ''}
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url=url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if len(soup.text) > 500:
            print('len > 500')
            soup_find_commodity = soup.find(id='market_commodity_forsale')
            if soup_find_commodity != None:
                print("soup_find_commodity != None")
                find_price = soup_find_commodity.find_all(class_='market_commodity_orders_header_promote')
                print(f'find_price: {find_price}')
                if find_price != []:
                    for span in find_price:
                        print('span', span.text)
                        if re.search('\$', span.text):
                            market['price'] = float(span.text.replace('$', ''))
                        else:
                            market['count'] = span.text
                else:
                    market['price'] = None
                    print(f'market_commodity_orders_header_promote отсутствует')
            else:
                print('not find soup_find_commodity')
                market_count = soup.find(id='searchResultsTable').find(id='searchResults_total').text
                market['count'] = market_count.encode("ascii", "ignore").decode()
                get_price = requests.get(url2, headers=headers, cookies=cookies).json()
                print(url2)
                if get_price != None:
                    print('get_price', get_price)
                    if 'lowest_price' in get_price:
                        print(f'get_price[lowest_price] {get_price["lowest_price"]}')
                        market['price'] = float(re.search(regex_price, get_price['lowest_price'])[1].replace(",", "")) # В некоторых встречается median_price вместо lowest_price
                    else:
                        print('lowest_price отсутствует')
                        market['price'] = None
                        fault = True
                else:
                    print('Цена не получена')
        else:
            print(f'Не удалось получить данные по предмету')
            market['price'] = None
            inventory_dict['total']['fault'][f'{current_date}'] = True
    except Exception as ex:
        print(f"Ошибка: {ex}")
        print(soup)
        inventory_dict['total']['fault'][f'{current_date}'] = True
    finally:
        driver.close()
        driver.quit()
    return market
    return fault

def get_total_count(inventory_dict):
    """ Подсчёт общего количества предметов """
    temp_dict = {}
    for inventory in inventory_dict.items():
        if inventory[0] == 'total':
            continue
        else:
            for item in inventory[1]['items'].items():
                if item[0] not in temp_dict:
                    if f'{current_date}' in item[1]['count']:
                        print(temp_dict)
                        print(f'{item[0]} из {inventory[0]}')
                        temp_dict[item[0]] = item[1]['count'][f'{current_date}']
                else:
                    if f'{current_date}' in item[1]['count']:
                        print(f'{item[0]} из {inventory[0]}')
                        temp_dict[item[0]] += item[1]['count'][f'{current_date}']
    return temp_dict

def update_dictionary():
    """ Занесение информации по ценам, количеству в инвентаре и на ТП в словарь """
    for inventory_id in inventory_dict.items():
        if inventory_id[0] != 'storage':
            for item in inventory_id[1]['items'].items():
                url = f'https://steamcommunity.com/market/listings/730/{item[1]["name"]}'.replace('в„ў ', '%E2%84%A2%20').replace(' ', '%20').replace('|', '%7C')
                url2 = f'https://steamcommunity.com/market/priceoverview/?country=RU&currency=1&appid=730&market_hash_name={item[1]["name"]}'.replace('в„ў ', '%E2%84%A2%20').replace(' ', '%20').replace('|', '%7C')
                print(f' {inventory_id[0]}, {item[1]["name"]}')
                if f'{current_date}' in item[1]['price'] and f'{current_date}' in item[1]['market_count'] and f'{current_date}' in item[1]['total_item_price']:
                    print('Информация уже собрана')
                    continue
                else:
                    if item[0] in inventory_dict['main']['items'] and f'{current_date}' in inventory_dict['main']['items'][item[0]]['price'] and f'{current_date}' in inventory_dict['main']['items'][item[0]]['market_count']:
                        if f'{current_date}' in item[1]['count']:
                            print('Информация уже собрана для первого инвентаря')
                            print(item[1])
                            print(inventory_dict['main']['items'][item[0]]['price'][f'{current_date}'])
                            item[1]['price'][f'{current_date}'] = inventory_dict['main']['items'][item[0]]['price'][f'{current_date}']
                            item[1]['market_count'][f'{current_date}'] = inventory_dict['main']['items'][item[0]]['market_count'][f'{current_date}']
                            item[1]['total_item_price'][f'{current_date}'] = round(item[1]['price'][f'{current_date}'] * item[1]['count'][f'{current_date}'], 2)
                            json.dump(inventory_dict, open("inventory_new.json", "w+"))
                    elif item[0] in inventory_dict['secondary']['items'] and f'{current_date}' in inventory_dict['secondary']['items'][item[0]]['price'] and f'{current_date}' in inventory_dict['secondary']['items'][item[0]]['market_count']:
                        if f'{current_date}' in item[1]['count']:
                            print('Информация уже собрана для второго инвентаря')
                            item[1]['price'][f'{current_date}'] = inventory_dict['secondary']['items'][item[0]]['price'][f'{current_date}']
                            item[1]['market_count'][f'{current_date}'] = inventory_dict['secondary']['items'][item[0]]['market_count'][f'{current_date}']
                            item[1]['total_item_price'][f'{current_date}'] = round(item[1]['price'][f'{current_date}'] * item[1]['count'][f'{current_date}'], 2)
                            json.dump(inventory_dict, open("inventory_new.json", "w+"))
                    else:
                        time.sleep(10)
                        print('Получение цены')
                        market = get_data_with_selenium(url, url2)
                        if market['price'] == None or market['price'] == '':
                            inventory_dict['total']['fault'][f'{current_date}'] = True
                            print('Цена не получена (нет поля lowest_price)')
                            time.sleep(60)
                            continue
                        else:
                            if f'{current_date}' in item[1]['count']:
                                print(market)
                                print(market['price'])
                                print(type(market['price']))
                                item[1]['price'][f'{current_date}'] = float(market['price'])
                                item[1]['market_count'][f'{current_date}'] = market['count']
                                item[1]['total_item_price'][f'{current_date}'] = round(market['price'] * item[1]['count'][f'{current_date}'], 2)
                                print(f"Цена: {market['price']}\nКоличество в инвентаре: {item[1]['count'][f'{current_date}']}\nКоличество на ТП: {market['count']}\nОбщая стоимость: {item[1]['total_item_price'][f'{current_date}']}")
                                print('----------------')
                                json.dump(inventory_dict, open("inventory_new.json", "w+"))
                            elif inventory_id[0] == 'total' and f'{current_date}' not in item[1]['count']:
                                item[1]['count'][f'{current_date}'] = 0
                                item[1]['price'][f'{current_date}'] = float(market['price'])
                                item[1]['market_count'][f'{current_date}'] = market['count']
                                item[1]['total_item_price'][f'{current_date}'] = round(
                                    market['price'] * item[1]['count'][f'{current_date}'], 2)
                                json.dump(inventory_dict, open("inventory_new.json", "w+"))

def get_usd_rub_course():
    """ Получение курса рубля в Steam на сегодняшний день """
    global rub_usd
    usd = float(re.search(regex_price, requests.get(
        'https://steamcommunity.com/market/priceoverview/?country=RU&currency=1&appid=730&market_hash_name=StatTrak%E2%84%A2%20M4A4%20|%20Zirka%20(Minimal%20Wear)',
        headers=headers).json()['median_price'])[1])
    # print(requests.get(
    #     'https://steamcommunity.com/market/priceoverview/?country=RU&currency=5&appid=730&market_hash_name=StatTrak%E2%84%A2%20M4A4%20|%20Zirka%20(Minimal%20Wear)',
    #     headers=headers))
    rub = float(re.search(r'\d+,\d+|\d+', requests.get(
        'https://steamcommunity.com/market/priceoverview/?country=RU&currency=5&appid=730&market_hash_name=StatTrak%E2%84%A2%20M4A4%20|%20Zirka%20(Minimal%20Wear)',
        headers=headers).json()['median_price'])[0].replace(',', '.'))
    rub_usd = round(rub / usd, 2)
    inventory_dict['total']['rub_usd'][f'{current_date}'] = rub_usd

def get_total_price():
    """ Подсчёт общей стоимости инвентаря """
    summ = float(0)
    for item in inventory_dict['total']['items'].items():
        if f'{current_date}' in item[1]['total_item_price']:
            summ += item[1]['total_item_price'][f'{current_date}']
    inventory_dict['total']['total_price'][f'{current_date}'] = round(summ, 2)
    inventory_dict['total']['fault'][f'{current_date}'] = fault
    json.dump(inventory_dict, open("inventory_new.json", "w+"))
    print(f'Итоговая стоимость: ${round(summ, 2)} / {round(summ * rub_usd, 2)} р.')

if __name__ == '__main__':
    # if f'{current_date}' in inventory_dict['total']['fault'] and inventory_dict['total']['fault'][f'{current_date}'] == False:
    #     print('Вся информация уже собрана')
    # else:
    inventory_dict['total']['fault'][f'{current_date}'] = False
    update_storage_items(yesterday)
    update_inventory_info(inventory_dict)

    """ Что делает код? """
    """ Считает общее количество предметов и заносит это в словарь total """
    temp_dict = get_total_count(inventory_dict)
    print(f'TEMP: {temp_dict}')
    for item in temp_dict.items():
        inventory_dict['total']['items'][item[0]]['count'][f'{current_date}'] = temp_dict[item[0]]
        print(item[0])

    update_dictionary()

    print(inventory_dict['total']['fault'][f'{current_date}'])
    if inventory_dict['total']['fault'][f'{current_date}'] == False:
        print('Все цены получены')
    else:
        print('Всю информацию собрать не удалось. Повторная попытка')
        time.sleep(360)
        update_dictionary()
        if inventory_dict['total']['fault'][f'{current_date}'] == False:
            print('Все цены получены')
        else:
            print('Всю информацию собрать не удалось. Нужен повторный запуск')

    get_usd_rub_course()
    get_total_price()

