import re
import time
import requests
import json
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver

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

# Получение предметов и их количество из инвентарей

def get_inventory_info(inventory_url, headers, inv_path, inventory):
    temp_dict = {}
    # get_inventory = requests.get(inventory_url, headers=headers).json()
    get_inventory = json.load(open(inv_path, 'r'))
    for item_type in get_inventory['descriptions']:
        type = item_type['tags'][0]["localized_tag_name"]
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
        if assets['classid'] in temp_dict:
            temp_dict[assets['classid']] += int(assets['amount'])
    print(temp_dict)
    for item in temp_dict.items():
        inventory_dict[inventory]['items'][item[0]]['count'][f'{current_date}'] = item[1]
    return inventory_dict

def get_data_with_selenium(url, url2):
    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    market = {'price': '', 'count': ''}
    try:
        driver = webdriver.Firefox(executable_path="D:\Python\SteamPars\geckodriver.exe",
                                   options=options)
        driver.get(url=url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        if len(soup.text) > 500:
            soup_find_commodity = soup.find(id='market_commodity_forsale')
            if soup_find_commodity != None:
                find_price = soup_find_commodity.find_all(class_='market_commodity_orders_header_promote')
                for span in find_price:
                    if re.search('\$', span.text):
                        market['price'] = float(span.text.replace('$', ''))
                    else:
                        market['count'] = span.text
            else:
                market_count = soup.find(id='searchResultsTable').find(id='searchResults_total').text
                market['count'] = market_count.encode("ascii", "ignore").decode()
                get_price = requests.get(url2, headers=headers, cookies=cookies).json()
                if get_price != None:
                    market['price'] = float(re.search(regex_price, get_price['lowest_price'])[0])
                else:
                    print('Цена не получена')

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
    return market

def get_total_count(inventory_dict):
    temp_dict = {}
    for inventory in inventory_dict.items():
        if inventory[0] == 'total':
            continue
        else:
            for item in inventory[1]['items'].items():
                if item[0] not in temp_dict:
                    temp_dict[item[0]] = item[1]['count'][f'{current_date}']
                else:
                    temp_dict[item[0]] += item[1]['count'][f'{current_date}']
    return temp_dict


regex_price = re.compile(r'\d+\.\d+')
# url1 = 'https://steamcommunity.com/market/listings/730/StatTrak%E2%84%A2%20M4A4%20%7C%20Zirka%20%28Minimal%20Wear%29'
# url2 = 'https://steamcommunity.com/market/priceoverview/?country=RU&currency=1&appid=730&market_hash_name=StatTrak%E2%84%A2%20M4A4%20|%20Zirka%20(Minimal%20Wear)'
# get_data_with_selenium(url1, url2)

# url = "https://steamcommunity.com/market/listings/730/Falchion%20Case"
# get_data_with_selenium(url)

for item in inventory_dict['storage']['items'].items():
    if f'{current_date}' not in item[1]['count']:
        item[1]['count'][f'{current_date}'] = item[1]['count'][f'{yesterday}']
print(inventory_dict['storage'])

temp_dict = get_total_count(inventory_dict)
for item in inventory_dict['total']['items'].items():
    print(temp_dict[item[0]])
    inventory_dict['total']['items'][item[0]]['count'][f'{current_date}'] = temp_dict[item[0]]
json.dump(inventory_dict, open("inventory_new.json","w+"))

inventory_url = ""

for inv in inventory_dict.items():
    if inv[0] == 'total' or inv[0] == 'storage':
        continue
    else:
        print(f'Текущий инвентарь {inv[0]}')
        inv_path = inv[1]['local']
        inventory = inv[0]
        inventory_dict = get_inventory_info(inventory_url, headers, inv_path, inventory)
json.dump(inventory_dict, open("inventory_new.json","w+"))

for inventory_id in inventory_dict.items():
    if inventory_id[0] != 'storage':
        for item in inventory_id[1]['items'].items():
            url = f'https://steamcommunity.com/market/listings/730/{item[1]["name"]}'.replace('в„ў ', '%E2%84%A2%20').replace(' ', '%20').replace('|', '%7C')
            url2 = f'https://steamcommunity.com/market/priceoverview/?country=RU&currency=1&appid=730&market_hash_name={item[1]["name"]}'.replace('в„ў ', '%E2%84%A2%20').replace(' ', '%20').replace('|', '%7C')
            print(f' {inventory_id[0]}, {item[1]["name"]}')
            # time.sleep(random.randint(5,10))
            if f'{current_date}' in item[1]['price'] and f'{current_date}' in item[1]['market_count'] and f'{current_date}' in item[1]['total_item_price']:
                print('Информация уже собрана')
                continue
            else:
                if item[0] in inventory_dict['main']['items']:
                    if f'{current_date}' in inventory_dict['main']['items'][item[0]]['price'] and f'{current_date}' in inventory_dict['main']['items'][item[0]]['market_count']:
                        print('Информация уже собрана для первого инвентаря')
                        print(inventory_dict)
                        print(item[1])
                        print(inventory_dict['main']['items'][item[0]]['price'][f'{current_date}'])
                        item[1]['price'][f'{current_date}'] = inventory_dict['main']['items'][item[0]]['price'][f'{current_date}']
                        item[1]['market_count'][f'{current_date}'] = inventory_dict['main']['items'][item[0]]['market_count'][f'{current_date}']
                        item[1]['total_item_price'][f'{current_date}'] = round(item[1]['price'][f'{current_date}'] * item[1]['count'][f'{current_date}'], 2)
                        json.dump(inventory_dict, open("inventory_new.json", "w+"))
                elif item[0] in inventory_dict['secondary']['items']:
                    if f'{current_date}' in inventory_dict['secondary']['items'][item[0]]['price'] and f'{current_date}' in inventory_dict['secondary']['items'][item[0]]['market_count']:
                        print('Информация уже собрана для второго инвентаря')
                        item[1]['price'][f'{current_date}'] = inventory_dict['secondary']['items'][item[0]]['price'][f'{current_date}']
                        item[1]['market_count'][f'{current_date}'] = inventory_dict['secondary']['items'][item[0]]['market_count'][f'{current_date}']
                        item[1]['total_item_price'][f'{current_date}'] = round(item[1]['price'][f'{current_date}'] * item[1]['count'][f'{current_date}'], 2)
                        json.dump(inventory_dict, open("inventory_new.json", "w+"))
                else:
                    market = get_data_with_selenium(url, url2)
                    item[1]['price'][f'{current_date}'] = market['price']
                    item[1]['market_count'][f'{current_date}'] = market['count']
                    item[1]['total_item_price'][f'{current_date}'] = round(market['price'] * item[1]['count'][f'{current_date}'], 2)
                    print(f"Цена: {market['price']}\nКоличество в инвентаре: {item[1]['count'][f'{current_date}']}\nКоличество на ТП: {market['count']}\nОбщая стоимость: {item[1]['total_item_price'][f'{current_date}']}")
                    print(inventory_dict)
                    print('----------------')
                    json.dump(inventory_dict, open("inventory_new.json", "w+"))
print('Все цены получены')

usd = float(re.search(regex_price, requests.get('https://steamcommunity.com/market/priceoverview/?country=RU&currency=1&appid=730&market_hash_name=StatTrak%E2%84%A2%20M4A4%20|%20Zirka%20(Minimal%20Wear)', headers=headers).json()['lowest_price'])[0])
rub = float(re.search(r'\d+,\d+', requests.get('https://steamcommunity.com/market/priceoverview/?country=RU&currency=5&appid=730&market_hash_name=StatTrak%E2%84%A2%20M4A4%20|%20Zirka%20(Minimal%20Wear)', headers=headers).json()['lowest_price'])[0].replace(',', '.'))
rub_usd = round(rub/usd, 2)
inventory_dict['total']['rub_usd'][f'{current_date}'] = rub_usd

summ = float(0)
for item in inventory_dict['total']['items'].items():
    summ += item[1]['total_item_price'][f'{current_date}']
inventory_dict['total']['total_price'][f'{current_date}'] = summ
json.dump(inventory_dict, open("inventory_new.json", "w+"))
print(f'Итоговая стоимость: ${summ} / {round(summ*rub_usd, 2)} р.')


