import requests
import json
import re
import time

link_pattern = r'(http:\/\/store.steampowered.com\/search\/\?list_of_subs=+\d+[,]*\d*)'
name_pattern = r"market_name\S{2}\s\S(\d{2}%(\s\w*[&!@#$%^*(\[)<>\].:;'{}+_\\\-=\w]*)*)"
last_assetid_pattern = r'last_assetid[": "]+(\d+)'
game_price_on_sale = r'\<strike\>(\d+[,]\d+)€'
game_price_not_on_sale = r'\s+(\d+[,]\d+)€'
game_name_owned = r"name\":\"(\w+[&!@#$%^*(\[)<>\].:;'\s{}+\\\-=\w]*)"

headers = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 "
                  " Safari/537.36",
}


# FIRST
def owned_games(ids):
    url = f'https://steamcommunity.com/profiles/' + ids + '/games/?tab=all'
    games = requests.get(url=url, headers=headers)
    # games = json.dumps(games.json())
    games = games.content.decode('UTF-8')
    names = re.findall(game_name_owned, games)
    # print(names)
    return names


# SECOND
def fetch_info(ids, game_filter, price):
    num = 0
    start = time.time()
    coupons = dict()
    games_gone_through = 0
    try:
        url = f"https://steamcommunity.com/inventory/" + ids + "/753/3?l=english&count=1"
        inventory = requests.get(url=url, headers=headers)
        inventory = json.dumps(inventory.json())
        links = re.findall(link_pattern, inventory)
        names = re.findall(name_pattern, inventory)
        start_assetid = re.findall(last_assetid_pattern, inventory)

        while len(start_assetid) != 0:
            try:
                time.sleep(2)
                print(f'\r Time : {time.time() - start:.3f} | Games : {len(names)} ', end='\r')
                url = f"https://steamcommunity.com/inventory/" + ids + \
                      "/753/3?l=english&count=80&start_assetid=" + start_assetid[0]
                inventory = requests.get(url=f'{url}')
                inventory = json.dumps(inventory.json())
                links += re.findall(link_pattern, inventory)
                names += re.findall(name_pattern, inventory)
                start_assetid = re.findall(last_assetid_pattern, inventory)

            except NameError:
                print('Timeout')
                time.sleep(5)
                fetch_info(ids, game_filter, price)

        print(f' Founded {len(names)} coupons. Time {time.time() - start:.5f}\n')
        #     f'  №  |  Time  |  Games  |  OFF%  |  Links')
        dict_sorter(names, links, num, start, games_gone_through, coupons, game_filter, price)

        print(f'\r \nFounded : {len(names)} coupons from witch {len(coupons)} usable')
        coupons = dict((sorted(coupons.items(), key=lambda item: (item[1], item[0]), reverse=True)))

        f = open(f"{ids}.txt", "w")
        for items, value in coupons.items():
            f.write(f'{items} - > {value} \n')
        f.close()
        # end = time.time()
        # total_time = end - start
        # print("\n" + str(total_time))
    except NameError:
        print('timeout')
        fetch_info(ids, game_filter, price)


# THIRD
def dict_sorter(game_name, game_links, num, start, games_gone_through, coupons, game_filter, price):
    print(f' №   | Time   | Games   | OFF%   | Links')
    estimated_time, estimated = 0, 0

    for name, link in zip(game_name, game_links):
        name = name[0]
        games_gone_through += 1
        off, game = name.split('% OFF ')
        timer = f'{time.time() - start:.2f}'
        estimated_time_start = time.time()

        if game not in game_filter and int(off) >= 66:
            if game not in coupons.keys():
                game_price = price_scraper(link)

                if float(game_price) < float(price):
                    coupons[game] = [int(off), game_price, link]
                    num += 1
                    print(f' {games_gone_through}   | {timer}   '
                          f'| {num}   | {off}   | {link}')

            elif game in coupons.keys():
                if int(off) > int(coupons[game][0]):
                    coupons[game][0] = int(off)

        estimated_time += float(f'{time.time() - estimated_time_start}')

        estimated = (estimated_time / int(games_gone_through)) * (len(game_name) - int(games_gone_through))

        progress = 100 * (games_gone_through / len(game_name))
        progress_bar = '{' + (int(progress // 2.5) * '#') + (int(40-progress // 2.5) * '-') + '}'

        print(f'\r ETC: {estimated:.2f} sec'
              f' | Games : {len(game_name)}/{games_gone_through} | {progress_bar} {progress:.2f} % ',
              end='\r')
    print(f'\r')


# FORTH
def price_scraper(urls):
    urls = urls + f'&category2=29'  # You can remove the [+ f'&category2=29'] filter to show games without trading cards
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


# #####################- EXAMPLE COUPON BOTS -############################
# 76561198305632439
# 76561198305632439, 76561198018370992, 76561198044411569


def _main():
    own_steam_id = '76561198145230280'  # Put your own SteamID
    steam_id = []
    print(f'Enter Steam id: ', end='')
    steam_ids = str(input())
    print(f'Max price: ', end='')
    max_price = float(input())

    if '' == steam_ids:
        print(f'Enter steam id')
        _main()

    if 'exit' in steam_ids:
        exit()

    if ',' in steam_ids:
        steam_id = steam_ids.split(', ')
    else:
        steam_id.append(steam_ids)

    if '' == max_price:
        print(f'Max price is set to 5')
        max_price = 5

    for user_id in steam_id:
        print(f'\nFor user : {own_steam_id}\nScraping inventory for coupons from user : {user_id}')
        owned_games_list = owned_games(own_steam_id)
        fetch_info(user_id, owned_games_list, max_price)

    print(f'\nIf you want to run more users enter steam id and press enter')
    _main()


if __name__ == '__main__':
    _main()
