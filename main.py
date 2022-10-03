import requests as r
import time
from configHandler import Config
import os


def get_player_info(API_KEY, nick, platform):
    responce = r.get(
        "https://api.mozambiquehe.re/bridge?auth={0}&player={1}&platform={2}".format(API_KEY, nick, platform))
    try:
        if responce.status_code == 429:
            while responce.status_code == 429:
                responce = r.get(
                    "https://api.mozambiquehe.re/bridge?auth={0}&player={1}&platform={2}".format(API_KEY, nick,
                                                                                                 platform))
        player_json = responce.json()
        if player_json['global']['name'] == "":
            player_json['global']['name'] = nick
        return player_json
    except Exception as ex:
        print(ex)


def update_player_online_time(player_json, last_online_list):
    if player_json != None:
        if player_json['realtime']['currentState'] != 'offline':
            last_online_list.update({player_json['global']['name']: time.time()})
        else:
            last_online_list.update({player_json['global']['name']: 0})
        return last_online_list


def get_pred_cutoff(API_KEY):
    responce = r.get(
        "https://api.mozambiquehe.re/predator?auth={0}".format(API_KEY))
    try:
        if responce.status_code == 429:
            while responce.status_code == 429:
                responce = r.get(
                    "https://api.mozambiquehe.re/predator?auth={0}".format(API_KEY))
        predator_json = responce.json()
        return predator_json['RP']['PC']['val']
    except Exception as ex:
        print(ex)


def return_max_len(array):
    max_len = 0
    for i in array:
        if len(i) > max_len:
            max_len = len(i)
    return max_len


def load_player_from_json(player_json, last_online_list):
    if player_json is not None:
        player = [player_json['global']['rank']['rankScore'], player_json['global']['name']]

        # Составление раздела рангов #
        if player_json['global']['rank']['rankName'].lower() == 'master':
            player_json['global']['rank']['rankDiv'] = 0
        rank = player_json['global']['rank']['rankName'] + ' '
        if player_json['global']['rank']['rankDiv'] == 4:
            rank += 'IV'
        if player_json['global']['rank']['rankDiv'] == 3:
            rank += 'III'
        if player_json['global']['rank']['rankDiv'] == 2:
            rank += 'II'
        if player_json['global']['rank']['rankDiv'] == 1:
            rank += 'I'
        player.append(rank)
        rank = ''

        i = 0
        if player_json['global']['rank']['rankScore'] == 0:
            while rank_required_points[i] // (player_json['global']['rank']['rankScore'] + 1) < 1:
                i += 1
        else:
            if player_json['global']['rank']['rankScore'] < rank_required_points[len(rank_required_points) - 1]:
                while rank_required_points[i] / player_json['global']['rank']['rankScore'] <= 1:
                    i += 1
        current_rank_size = rank_required_points[i] - rank_required_points[i - 1]
        if player_json['global']['rank']['rankScore'] < 1000:
            current_division_size = current_rank_size
        elif player_json['global']['rank']['rankScore'] >= 15000:
            current_division_size = current_rank_size
        else:
            current_division_size = current_rank_size / 4
        progress_bar_x = round((player_json['global']['rank']['rankScore'] - rank_required_points[
            i - 1]) % current_division_size * 20 / current_division_size)
        for n in range(0, int(progress_bar_x)):
            rank += '█'
        for n in range(0, 20 - int(progress_bar_x)):
            rank += '▁'
        rank += ' ' + str(player_json['global']['rank']['rankScore']) + '/' + str(int(
            ((player_json['global']['rank']['rankScore'] - rank_required_points[i - 1]) // current_division_size) * int(
                current_division_size) + int(current_division_size) + rank_required_points[i - 1]))
        ############################################################

        player.append(rank)
        temp_status = player_json['realtime']['selectedLegend'] + ' '
        if player_json['realtime']['currentState'] != 'offline':
            temp_status += player_json['realtime']['currentStateAsText'] + ' '
        else:
            if player_json['realtime']['isOnline'] == 1:
                temp_status += 'ONLINE '
            else:
                temp_status += 'OFFLINE '
                if last_online_list.get(player_json['global']['name']) != 0:
                    temp_time_delta = time.gmtime(time.time() - last_online_list.get(player_json['global']['name']))
                    temp_status += ' (LAST ' + str(temp_time_delta.tm_hour) + 'h ' + str(
                        temp_time_delta.tm_min) + 'm AGO)'
        if player_json['realtime']['partyFull'] == 1:
            temp_status += ' FULL SQUAD'
        player.append(temp_status)
        player.append(str(500 * player_json['global']['levelPrestige'] + player_json['global']['level']))
        return player


def build_beautiful_banner(players, save_array):
    banner = ''
    delta_list = ['PO']
    nickname_list = ['NICKNAME']
    rank_list = ['RANK']
    progress_list = ['PROGRESS']
    status_list = ['STATUS']
    level_list = ['LVL']
    # Заполнение списков разделов
    for p in range(1, len(players)):
        if players[p] == None:
            continue
        if int(players[p][0]) > 0:
            delta_list.append('+' + str(players[p][0] - save_array[p][0]))
        else:
            delta_list.append(str(players[p][0] - save_array[p][0]))
        nickname_list.append(players[p][1])
        rank_list.append(players[p][2])
        progress_list.append(str(players[p][3]))
        status_list.append(players[p][4])
        level_list.append(str(players[p][5]))

    # определение самых длинных данных в разделах
    long_delta_points = return_max_len(delta_list)
    long_nickname = return_max_len(nickname_list)
    long_rank = return_max_len(rank_list)
    long_progress = return_max_len(progress_list)
    long_status = return_max_len(status_list)
    long_level = return_max_len(level_list)
    # Здесь формируется красивый вывод
    for p in range(0, len(players)):
        if players[p] == None:
            continue
        if p != 0:
            players[p][0] = str(players[p][0] - save_array[p][0])
            if int(players[p][0]) > 0:
                players[p][0] = '+' + players[p][0]
        while len(players[p][0]) < long_delta_points:
            players[p][0] += ' '
        while len(players[p][1]) < long_nickname + 1:
            players[p][1] += ' '
        while len(players[p][2]) < long_rank:
            players[p][2] += ' '
        while len(players[p][3]) < long_progress:
            players[p][3] += ' '
        while len(players[p][4]) < long_status:
            players[p][4] += ' '
        while len(players[p][5]) < long_level:
            players[p][5] += ' '
        for i in range(0, len(players[p])):
            if i != 1:
                players[p][i] = str(players[p][i]).upper()
    for p in players:
        if p != None:
            for f in p:
                banner += (f + ' | ')
            banner += '\n'
    return banner


config = Config()
API_KEY = config.get_key()
platform = 'PC'
last_online_list = {}
rank_required_points = [0, 1000, 3000, 5400, 8200, 11400, 15000, get_pred_cutoff(API_KEY), 100000]

player_list = config.get_victims()
players = [['PO', 'NICKNAME', 'RANK', 'PROGRESS', 'STATUS', 'LVL']]
save_array = [['TITLE_RESERVED']]

for pl in player_list:
    player_json = get_player_info(API_KEY, pl, platform)
    last_online_list = update_player_online_time(player_json, last_online_list)
    save_array.append([player_json['global']['rank']['rankScore'], player_json['global']['level']])

    players.append(load_player_from_json(player_json, last_online_list))
for i in players:
    with open('save.txt', 'w') as save_file:
        a = 1
players = []

while True:
    players.append(['PO', 'NICKNAME', 'RANK', 'PROGRESS', 'STATUS', 'LVL'])
    start_time = time.time()
    for pl in player_list:
        player_json = get_player_info(API_KEY, pl, platform)
        update_player_online_time(player_json, last_online_list)
        players.append(load_player_from_json(player_json, last_online_list))
    os.system('cls')
    print('\n')
    print(build_beautiful_banner(players, save_array))
    players = []
