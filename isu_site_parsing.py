from bs4 import BeautifulSoup
import requests
import json
import re
import pandas as pd

# the source for calculating scoresb: https://en.wikipedia.org/wiki/ISU_World_Standings_and_Season%27s_World_Ranking#Principles
ranking_points = dict()
ranking_points['Olympic Games'] = {1: 1200, 2: 1080, 3: 972, 4: 875, 5: 787, 6: 709, 7: 638, 8: 574, 9: 517, 10: 465, 11: 418, 12: 377, 13: 339, 14: 305, 15: 275, 16: 247, 17: 222, 18: 200, 19: 180, 20: 162, 21: 146, 22: 131, 23: 118, 24: 106}
ranking_points['World Championship'] = {1: 1200, 2: 1080, 3: 972, 4: 875, 5: 787, 6: 709, 7: 638, 8: 574, 9: 517, 10: 465, 11: 418, 12: 377, 13: 339, 14: 305, 15: 275, 16: 247, 17: 222, 18: 200, 19: 180, 20: 162, 21: 146, 22: 131, 23: 118, 24: 106}
ranking_points['European Championship'] = {1: 840, 2: 756, 3: 680, 4: 612, 5: 551, 6: 496, 7: 446, 8: 402, 9: 362, 10: 325, 11: 293, 12: 264, 13: 237, 14: 214, 15: 192, 16: 173, 17: 156, 18: 140, 19: 126, 20: 113, 21: 102, 22: 92, 23: 83, 24: 74}
ranking_points['Four Continents Championship'] = {1: 840, 2: 756, 3: 680, 4: 612, 5: 551, 6: 496, 7: 446, 8: 402, 9: 362, 10: 325, 11: 293, 12: 264, 13: 237, 14: 214, 15: 192, 16: 173, 17: 156, 18: 140, 19: 126, 20: 113, 21: 102, 22: 92, 23: 83, 24: 74}
ranking_points['World Juniors'] = {1: 500, 2: 450, 3: 405, 4: 365, 5: 328, 6: 295, 7: 266, 8: 239, 9: 215, 10: 194, 11: 174, 12: 157, 13: 141, 14: 127, 15: 114, 16: 103, 17: 93, 18: 83, 19: 75, 20: 68, 21: 61, 22: 55, 23: 49, 24: 44}
# ranking_points['Grand Prix Final'] = {1: 800, 2: 720, 3: 648, 4: 583, 5: 525, 6: 472, 7: 425, 8: 383, 9: 345, 10: 310, 11: 279, 12: 251, 13: 226, 14: 203, 15: 183, 16: 165, 17: 148, 18: 133, 19: 120, 20: 108}
# ranking_points['Grand Prix'] = {1: 400, 2: 360, 3: 324, 4: 292, 5: 262, 6: 236, 7: 213, 8: 191, 9: 172, 10: 155, 11: 139, 12: 125, 13: 113, 14: 101, 15: 91, 16: 82, 17: 74, 18: 67, 19: 60, 20: 54}
# ranking_points['Junior Grand Prix Final'] = {1: 350, 2: 315, 3: 284, 4: 255, 5: 230, 6: 207, 7: 186, 8: 167, 9: 151, 10: 135, 11: 122, 12: 109, 13: 99, 14: 89, 15: 80, 16: 72, 17: 65, 18: 59, 19: 53, 20: 48}
# ranking_points['Junior Grand Prix'] = {1: 250, 2: 225, 3: 203, 4: 182, 5: 164, 6: 148, 7: 133, 8: 120, 9: 108, 10: 97}
# ranking_points['Challenger Series'] = {1: 300, 2: 270, 3: 243, 4: 219, 5: 198, 6: 178, 7: 160, 8: 144}
# ranking_points['International Senior Competitions'] = {1: 250, 2: 225, 3: 203, 4: 182, 5: 164, 6: 148, 7: 133, 8: 120, 9: 108, 10: 97}

with open('ranking_points.json', 'w') as file:
    json.dump(ranking_points, file)

with open('ranking_points.json') as file:
    ranking_points = json.load(file)

def find_table_structure(soup):
    all_cells = soup.find_all('td')

    for i, cell in enumerate(all_cells):
        cell_text = cell.get_text(strip=True)
        if cell_text == 'Olympic Games':
            event_classes = cell.get('class', [])
            event_class = event_classes[0] if event_classes else None

            parent_row = cell.find_parent('tr')
            if parent_row:
                row_cells = parent_row.find_all('td')
                current_index = row_cells.index(cell) if cell in row_cells else -1

                if current_index >= 0 and current_index + 1 < len(row_cells):
                    next_cell = row_cells[current_index + 1]
                    placement_classes = next_cell.get('class', [])
                    placement_class = placement_classes[0] if placement_classes else None

                    return (event_class, placement_class)

    return (None, None)

def get_skaters_merits(skater_link):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    html_page = requests.get(skater_link,
                             headers=headers,
                             timeout=10)
    html_page.raise_for_status()
    soup = BeautifulSoup(html_page.text, 'html.parser')
    flx_1, flx_2 = find_table_structure(soup)
    if flx_1 == None and flx_2 == None:
        print(f'Flx types are not defined for {skater_link}')
        return None
    competition_results = {}
    rows = soup.find_all('tr')

    for row in rows:
        event_cell = row.find('td', class_=flx_1)
        if event_cell:
            event_name = event_cell.get_text(strip=True)
            placement_cells = row.find_all('td', class_=flx_2)

            placements = []
            for cell in placement_cells:
                link = cell.find('a')
                if link:
                    place_text = link.get_text(strip=True)
                    try:
                        placements.append(int(place_text))
                    except ValueError:
                        placements.append(place_text)
                else:
                    cell_text = cell.get_text(strip=True)
                    if cell_text:
                        try:
                            placements.append(int(cell_text))
                        except ValueError:
                            placements.append(cell_text)

            if placements:
                competition_results[event_name] = placements
    return competition_results

def get_rating_score(competition_results):
    score = 0
    for competition in competition_results.keys():
        if competition in ranking_points.keys():
            for place in competition_results[competition]:
                try:
                    score += ranking_points[competition][str(place)]
                except KeyError:
                    pass
        elif competition in ['Four Continents', 'European Champ.']:
            for place in competition_results[competition]:
                try:
                    score += ranking_points['Four Continents Championship'][str(place)]
                except KeyError:
                    pass
        elif competition == 'World Champ.':
            for place in competition_results[competition]:
                try:
                    score += ranking_points['World Championship'][str(place)]
                except KeyError:
                    pass
        else:
            if 'National' not in competition:
                print(competition)
    return score

df = pd.read_csv('FS_nicks_links.csv')
graph_dict = {}
additional_info = {}
for index, row in df.iterrows():
    nick = row['nickname']
    if row['yeb'] == True:
        point_score = row['sum']
    else:
        link = row['isu_link']
        competition_results = get_skaters_merits(link)
        additional_info[nick] = competition_results
        point_score = get_rating_score(competition_results)

    graph_dict[nick] = {'name': row['name'],
                        'discipline': row['type'],
                        'score': point_score}

with open('graph_attributes.json', 'w') as f:
    json.dump(graph_dict, f)

with open('additional_info.json', 'w') as f:
    json.dump(additional_info, f)
