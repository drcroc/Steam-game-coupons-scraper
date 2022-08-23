import requests
import json
import re
import time


link_pattern = r'(http:\/\/store.steampowered.com\/search\/\?list_of_subs=+\d+[,]*\d*)'
name_pattern = r"market_name\S{2}\s\S(\d{2}%(\s\w*[&!@#$%^*(\[)<>\].:;'{}+_\\\-=\w]*)*)"
last_assetid_pattern = r'last_assetid[": "]+(\d+)'
game_price_on_sale = r'\<strike\>(\d+[,]\d+)€'
game_price_not_on_sale = r'\s+(\d+[,]\d+)€'


def price_scraper(urls):
    ###########################################
    urls = urls + f'&category2=29'  # You can remove the + f'&category2=29' filter for games only with trading cards
    price = requests.get(url=urls)
    price = price.content.decode('UTF-8')
    price_sale = re.findall(game_price_on_sale, price)
    price = re.findall(game_price_not_on_sale, price)
    price = price + price_sale
    # print(price)
    if len(price) > 0:
        if ',' in price[0]:
            price = price[0].replace(',', '.')
            price = float(price)
        else:
            price = float(price[0])
        time.sleep(0.5)
    else:
        price = 9999999999
    return price


def dict_sorter(game_name, game_links, num, start, games_gone_through, coupons):
    for name, link in zip(game_name, game_links):
        name = name[0]
        games_gone_through += 1
        off, game = name.split('% OFF ')
        if int(off) >= 66:
            if game not in coupons.keys():
                game_price = price_scraper(link)
                #######################################################################################
                if game_price < 1 and int(off) >= 66:   # You can change the price range and the discount here
                    coupons[game] = [int(off), game_price, link]
                    num += 1
                    game_time = time.time()
                    print(f' {games_gone_through}  | {game_time - start:.2f}  |   {num}    |  {off}   | {link}')

            elif game in coupons.keys():
                if int(off) > int(coupons[game][0]):
                    coupons[game][0] = int(off)


def fetch_info(ids):
    num = 0
    start = time.time()
    coupons = dict()
    games_gone_through = 0

    url = f"https://steamcommunity.com/inventory/" + ids + "/753/3?l=english&count=1"
    inventory = requests.get(url=url)
    inventory = json.dumps(inventory.json())
    links = re.findall(link_pattern, inventory)
    names = re.findall(name_pattern, inventory)
    start_assetid = re.findall(last_assetid_pattern, inventory)
    while len(start_assetid) != 0:
        url = f"https://steamcommunity.com/inventory/" + ids + \
              "/753/3?l=english&count=108&start_assetid=" + start_assetid[0]

        inventory = requests.get(url=f'{url}')

        inventory = json.dumps(inventory.json())
        links += re.findall(link_pattern, inventory)
        names += re.findall(name_pattern, inventory)
        start_assetid = re.findall(last_assetid_pattern, inventory)

    dict_sorter(names, links, num, start, games_gone_through, coupons)

    print(f'Founded : {len(names)} coupons from witch {len(coupons)} different')
    coupons = dict((sorted(coupons.items(), key=lambda item: (item[1], item[0]), reverse=True)))

    f = open(f"{ids}.txt", "w")
    for items, value in coupons.items():
        f.write(f'{items} - > {value} \n')
    f.close()
    end = time.time()
    total_time = end - start
    print("\n" + str(total_time))


def _main():
    steam_id = []
    print(f'Enter Steam id: ', end='')
    steam_ids = str(input())
    if 'exit' in steam_ids:
        exit()
    if ',' in steam_ids:
        steam_id = steam_ids.split(', ')
    else:
        steam_id.append(steam_ids)

    for user_id in steam_id:
        print(f'\nFor user : {user_id}\nScraping inventory for coupons\n  №  |  Time  |  Games  |  OFF%  |  Links')
        fetch_info(user_id)
    print(f'\nTo close the program type exit and press Enter\nIf you want to run more user press enter')
    exit_quest = input()
    if exit_quest.lower() == 'exit':
        exit()
    _main()


if __name__ == '__main__':
    _main()

###################- EXAMPLE -############################
# 76561198305632439
# 76561198305632439, 76561198018370992, 76561198044411569
