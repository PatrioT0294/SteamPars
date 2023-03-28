import time
from datetime import date, timedelta
import json

current_date = date.today()
yesterday = date.today() - timedelta(days=1)
inventory_dict = json.load(open('inventory_new.json', 'r'))

def delete_today():
    for inventory in inventory_dict.items():
        if inventory[0] != 'storage':
            for item in inventory[1]['items'].items():
                if f'{current_date}' in item[1]['price']:
                    del item[1]['price'][f'{current_date}']
                if f'{current_date}' in item[1]['total_item_price']:
                    del item[1]['total_item_price'][f'{current_date}']
                if f'{current_date}' in item[1]['market_count']:
                    del item[1]['market_count'][f'{current_date}']
                print(inventory_dict)
    json.dump(inventory_dict, open("inventory_new.json", "w+"))

def fix_selected_date_total_price():
    for inventory in inventory_dict.items():
        if inventory[0] != 'storage':
            for item in inventory[1]['items'].items():
                item[1]['total_item_price']['2023-01-19'] = item[1]['price']['2023-01-19'] * item[1]['count']['2023-01-19']
        json.dump(inventory_dict, open("inventory_fixed.json", "w+"))

def show_current_count():
    for item in inventory_dict["total"]["items"].items():
        if item[1]["type"] == "Container":
            print(f'{item[1]["name"]} - {item[1]["count"]["2023-03-23"]}')

def last_two_day_total_price():
    for item in inventory_dict["total"]["items"].items():
        if f'{current_date}' in item[1]["count"]:
            if item[1]["total_item_price"][f'{current_date}']-item[1]["total_item_price"][f"{yesterday}"] > 20 or item[1]["total_item_price"][f'{current_date}']-item[1]["total_item_price"][f"{yesterday}"] < -10:
                print(f'{item[1]["name"]}:\nCount: {item[1]["count"][f"{current_date}"]}\nPrice: {item[1]["price"][f"{yesterday}"]} -> {item[1]["price"][f"{current_date}"]}\nTotal price: {item[1]["total_item_price"][f"{yesterday}"]} -> {item[1]["total_item_price"][f"{current_date}"]}\nTotal change: {round(item[1]["total_item_price"][f"{current_date}"]-item[1]["total_item_price"][f"{yesterday}"], 2)}\n')

def percent_grow():
    for item in inventory_dict["total"]["items"].items():
        if '2023-01-19' in item[1]['price']:
            print(
                f'{item[1]["name"]}: {item[1]["price"]["2023-01-19"]} -> {item[1]["price"]["2023-03-24"]} ({round((float(item[1]["price"]["2023-03-24"]) * 100) / float(item[1]["price"]["2023-01-19"]) - 100, 2)}%)')
        else:
            print(f'{item[1]["name"]} нет данных')
            # date = '2023-01-19'
            # while date not in item[1]['price']:
            #     print(f'{date} not in {item[1]["name"]}!')
            #     date = date - timedelta(days=1)
            # print(
            #     f'{item[1]["name"]}: {item[1]["price"]["2023-01-19"]} -> {item[1]["price"]["2023-03-24"]} ({round((float(item[1]["price"]["2023-03-24"]) * 100) / float(item[1]["price"]["2023-01-19"]) - 100, 2)}%)')


# delete_today()
# show_current_count()
last_two_day_total_price()
# percent_grow()