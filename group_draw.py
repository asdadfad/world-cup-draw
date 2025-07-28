team_continent = {
    "Qatar": ["As"], "Belgium": ["Eu"], "Brazil": ["SA"], "France": ["Eu"],
    "Argentina": ["SA"], "England": ["Eu"], "Portugal": ["Eu"], "Spain": ["Eu"],  # pot1
    "Denmark": ["Eu"], "Netherlands": ["Eu"], "Germany": ["Eu"], "Switzerland": ["Eu"],
    "Croatia": ["Eu"], "Mexico": ["NA"], "USA": ["NA"], "Uruguay": ["SA"],        # pot2
    "Iran": ["As"], "Serbia": ["Eu"], "Japan": ["As"], "Senegal": ["Af"],
    "Tunisia": ["Af"], "Poland": ["Eu"], "KoreaRep": ["As"], "Morocco": ["Af"],    # pot3
    "Wales/Scot/Ukr": ["Eu"],
    "Peru/UAE/Au": ["SA", "As"],
    "CostaRica/NZ": ["NA"],
    "Saudi Arabia": ["As"],
    "Cameroon": ["Af"], "Ecuador": ["SA"], "Canada": ["NA"], "Ghana": ["Af"]     # pot4
}
from collections import Counter

def is_group_valid(continents):
    tab = Counter(continents)
    if 'Eu' not in tab:
        return False
    if tab['Eu'] > 2:
        return False
    for cont, count in tab.items():
        if cont != 'Eu' and count > 1:
            return False
    return True

def is_group_valid2(continents):
    tab = Counter(continents)
    if tab.get('Eu', 0) > 2:
        return False
    for cont, count in tab.items():
        if cont != 'Eu' and count > 1:
            return False
    return True
from itertools import product

def check_all_groups(group):
    for row in group:
        # 提取该组的所有已填球队
        teams = [team for team in row if team is not None]
        continents_list = []
        for team in teams:
            if team not in team_continent:
                return False  # 未知球队
            continents_list.append(team_continent[team])
        # 如果所有球队只有一个大陆选项，直接检查
        if all(len(opts) == 1 for opts in continents_list):
            continents = [opts[0] for opts in continents_list]
            if not is_group_valid(continents):
                return False
        else:
            # 存在多选洲的球队，枚举所有可能组合
            for combo in product(*continents_list):
                if not is_group_valid(combo):
                    return False
    return True
def is_group_possible(team_names):
    if not team_names:
        return True
    options_list = []
    for team in team_names:
        if team not in team_continent:
            raise ValueError(f"unknown team: {team}")
        options_list.append(team_continent[team])
    if all(len(opts) == 1 for opts in options_list):
        continents = [opts[0] for opts in options_list]
        return is_group_valid2(continents)
    for combo in product(*options_list):
        if not is_group_valid2(combo):
            return False
    return True
import random

def sample_assignment(group, available):
    m = [row[:] for row in group]
    npots = len(available)
    ngroups = len(m)
    for pot in range(npots):
        avail_teams = [team for team in available[pot] if team is not None]
        empty_pos = [i for i in range(ngroups) if m[i][pot] is None or m[i][pot] == ""]
        if len(avail_teams) != len(empty_pos):
            raise Exception(f"Pot {pot+1}: 可用队伍数 {len(avail_teams)} ≠ 空位数 {len(empty_pos)}")
        perm = random.sample(avail_teams, k=len(avail_teams))
        for j, group_idx in enumerate(empty_pos):
            m[group_idx][pot] = perm[j]
    return m

def sample_valid_assignments(group, available, n):
    results = []
    count_valid = 0
    while count_valid < n:
        cand = sample_assignment(group, available)
        if check_all_groups(cand):
            count_valid += 1
            results.append([row[:] for row in cand])  # 深拷贝
    return results

import math

group = [[None]*4 for _ in range(8)]
available_all = [
    ["Qatar", "Belgium", "Brazil", "France", "Argentina", "England", "Portugal", "Spain"],
    ["Denmark", "Netherlands", "Germany", "Switzerland", "Croatia", "Mexico", "USA", "Uruguay"],
    ["Iran", "Serbia", "Japan", "Senegal", "Tunisia", "Poland", "KoreaRep", "Morocco"],
    ["Wales/Scot/Ukr", "Peru/UAE/Au", "CostaRica/NZ", "Saudi Arabia", "Cameroon", "Ecuador", "Canada", "Ghana"]
]

available = [row[:] for row in available_all]

group[0][0] = "Qatar"
available[0][0] = None

remaining_pot1 = [t for t in available[0] if t is not None]
random.shuffle(remaining_pot1)
for idx in range(1, 8):
    group[idx][0] = remaining_pot1[idx-1]
available[0] = [None] * len(available[0])

for pot in range(1, 4):
    teams = available[pot]
    non_none_indices = [i for i, t in enumerate(teams) if t is not None]
    for grp_idx in range(8):
        counts = {}
        for idx in non_none_indices:
            team = teams[idx]
            samples = sample_valid_assignments(group, available, 50)  # 采样次数适当
            count = sum(1 for s in samples if s[grp_idx][pot] == team)
            counts[idx] = count
        non0 = {idx: cnt for idx, cnt in counts.items() if cnt > 0}
        if not non0:
            continue
        max_count = max(non0.values())
        normalized = {idx: cnt/max_count for idx, cnt in non0.items()}

        N = {}
        for idx, prob in normalized.items():
            if prob <= 0:
                N[idx] = math.inf
            else:
                k = 1
                while random.random() > prob:
                    k += 1
                N[idx] = k

        NN = {idx: 0 for idx in N}
        while True:
            choice = random.choice(list(N.keys()))
            NN[choice] += 1
            if NN[choice] >= N[choice]:
                winner = choice
                break

        group[grp_idx][pot] = teams[winner]
        available[pot][winner] = None

for i, grp in enumerate(group):
    print(f"Group {chr(65+i)}: {grp}")
