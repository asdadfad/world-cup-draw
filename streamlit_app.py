import streamlit as st
import numpy as np
import pandas as pd
import random
from itertools import permutations
from group_draw import *


st.title('World Cup Group Draw Simulator')

if st.button('Start Draw'):
    group = [[None] * 4 for _ in range(8)]
    available_all = [
        ["Qatar", "Belgium", "Brazil", "France", "Argentina", "England", "Portugal", "Spain"],
        ["Denmark", "Netherlands", "Germany", "Switzerland", "Croatia", "Mexico", "USA", "Uruguay"],
        ["Iran", "Serbia", "Japan", "Senegal", "Tunisia", "Poland", "KoreaRep", "Morocco"],
        ["Wales/Scot/Ukr", "Peru/UAE/Au", "CostaRica/NZ", "Saudi Arabia", "Cameroon", "Ecuador", "Canada", "Ghana"]
    ]

    table_placeholder = st.empty()

    available = [row[:] for row in available_all]

    group[0][0] = "Qatar"
    available[0][0] = None

    remaining_pot1 = [t for t in available[0] if t is not None]
    random.shuffle(remaining_pot1)
    for idx in range(1, 8):
        group[idx][0] = remaining_pot1[idx - 1]
    available[0] = [None] * len(available[0])

    group_df = pd.DataFrame(group, columns=["Pot1", "Pot2", "Pot3", "Pot4"],
                            index=["Group A", "Group B", "Group C", "Group D",
                                   "Group E", "Group F", "Group G", "Group H"])
    table_placeholder.dataframe(group_df)

    for pot in range(1, 4):
        teams = available[pot]
        non_none_indices = [i for i, t in enumerate(teams) if t is not None]
        for grp_idx in range(8):

            counts = {}
            for idx in non_none_indices:
                team = teams[idx]
                samples = sample_valid_assignments(group, available, 50)
                count = sum(1 for s in samples if s[grp_idx][pot] == team)
                counts[idx] = count

            non_zero = {idx: cnt for idx, cnt in counts.items() if cnt > 0}
            if not non_zero:
                continue
            max_count = max(non_zero.values())
            normalized = {idx: cnt / max_count for idx, cnt in non_zero.items()}

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

            group_df = pd.DataFrame(group, columns=["Pot1", "Pot2", "Pot3", "Pot4"],
                                    index=["Group A", "Group B", "Group C", "Group D",
                                           "Group E", "Group F", "Group G", "Group H"])
            table_placeholder.dataframe(group_df)

    st.success('Draw completed!')


