from tkinter import *
from tkinter.ttk import Combobox
from tkinter import ttk
from tkinter import filedialog
import json
# from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import numpy as np

inventory = json.load(open('inventory_new.json', 'r'))
item_list = []
type_list = []
total_price = []
current_chk = 0
x_all = []
y_all = []

# for i in inventory['total']['total_price'].items():
#     print(f'{i[0]}: {i[1] * inventory["total"]["rub_usd"][i[0]]}')
def update_type_list(type, item):
    if type.get() == 0 and item in type_list:
        type_list.remove(item)
    elif type.get() == 1 and item not in type_list:
        type_list.append(item)
    updated_type_list = []
    for item in inventory['total']['items'].items():
        if item[1]['type'] in type_list:
            updated_type_list.append(item[1]['name'])
    combo['values'] = (sorted(updated_type_list))
    combo.current(0)

def clicked():
    """ Вывести график цены выбранного предмета """
    x = []
    y = []
    selected_item = combo.get()
    for item in inventory['total']['items'].items():
        if item[1]['name'] == selected_item:
            for i in item[1]['price'].items():
                x.append(i[0])
                y.append(i[1])
    plt.plot(x, y)
    plt.show()

def clicked_all():
    """ Вывести график цены всего инвентаря """
    plt.plot(x_all, y_all)
    # fig, ax = plt.subplots()
    plt.show()

def show_market_count():
    """ Вывести график количества выбранных предметов на ТП """
    x = []
    y = []
    selected_item = combo.get()
    for item in inventory['total']['items'].items():
        if item[1]['name'] == selected_item:
            for i in item[1]['market_count'].items():
                x.append(i[0])
                y.append(int(i[1]))
    plt.plot(x, y)
    plt.show()

for price in inventory['total']['total_price'].items():
    x_all.append(price[0])
    y_all.append(price[1])

for item in inventory['total']['items'].items():
    if item[1]['type'] not in type_list:
        type_list.append(item[1]['type'])

for item in inventory['total']['items'].items():
    if item[1]['type'] in type_list:
        item_list.append(item[1]['name'])

window = Tk()
window.title("Steam Inventory")
window.geometry('430x250')

btn = Button(window, text="График цены", command=clicked)
btn.grid(column=1, row=0)

show_total_price_btn = Button(window, text="Общий график", command=clicked_all)
show_total_price_btn.grid(column=1, row=1)

show_market_count_btn = Button(window, text="График количества", command=show_market_count)
show_market_count_btn.grid(column=1, row=2)

container = IntVar()
container.set(1)
container_checkbutton = ttk.Checkbutton(text="Container", state=ACTIVE, variable=container, command=lambda: update_type_list(container, 'Container'))
container_checkbutton.grid(column=3, row=0)

pistol = IntVar()
pistol.set(1)
pistol_checkbutton = ttk.Checkbutton(text="Pistol", variable=pistol, command=lambda: update_type_list(pistol, 'Pistol'))
pistol_checkbutton.grid(column=3, row=1)

sticker = IntVar()
sticker.set(1)
sticker_checkbutton = ttk.Checkbutton(text="Sticker", variable=sticker, command=lambda: update_type_list(sticker, 'Sticker'))
sticker_checkbutton.grid(column=3, row=2)

shotgun = IntVar()
shotgun.set(1)
shotgun_checkbutton = ttk.Checkbutton(text="Shotgun", variable=shotgun, command=lambda: update_type_list(shotgun, 'Shotgun'))
shotgun_checkbutton.grid(column=3, row=3)

smg = IntVar()
smg.set(1)
smg_checkbutton = ttk.Checkbutton(text="SMG", variable=smg, command=lambda: update_type_list(smg, 'SMG'))
smg_checkbutton.grid(column=3, row=4)

machinegun = IntVar()
machinegun.set(1)
machinegun_checkbutton = ttk.Checkbutton(text="Machinegun", variable=machinegun, command=lambda: update_type_list(machinegun, 'Machinegun'))
machinegun_checkbutton.grid(column=3, row=5)

sniper = IntVar()
sniper.set(1)
sniper_checkbutton = ttk.Checkbutton(text="Sniper Rifle", variable=sniper, command=lambda: update_type_list(sniper, 'Sniper Rifle'))
sniper_checkbutton.grid(column=3, row=6)

rifle = IntVar()
rifle.set(1)
rifle_checkbutton = ttk.Checkbutton(text="Rifle", variable=rifle, command=lambda: update_type_list(rifle, 'Rifle'))
rifle_checkbutton.grid(column=3, row=7)

combo = Combobox(window, state="readonly", width=30)
combo['values'] = (sorted(item_list))
combo.current(0)
combo.grid(column=0, row=0)

window.mainloop()

# Примеры

# pistol = IntVar()
# pistol_checkbutton = ttk.Checkbutton(text="Pistol", variable=pistol, command= lambda: update_type_list(pistol, 'Pistol'))
# pistol_checkbutton.grid(column=3, row=1)
