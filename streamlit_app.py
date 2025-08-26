import streamlit as st
import pandas as pd
import random
import math
import time
from group_draw import sample_valid_assignments  # 你的采样函数

st.title('World Cup Group Draw Simulator')

# 高亮函数
def highlight_row(row, current_team, winner_team):
    color = ''
    if row['Team'] == current_team:
        color = 'background-color: lightcoral;'  # 红色
    if row['Team'] == winner_team:
        color = 'background-color: lightgreen;'  # 绿色
    return [color] * len(row)


# 初始化状态
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "group" not in st.session_state:
    st.session_state.group = None
if "available" not in st.session_state:
    st.session_state.available = None
if "pot" not in st.session_state:
    st.session_state.pot = 1
if "grp_idx" not in st.session_state:
    st.session_state.grp_idx = 0
if "winner_team" not in st.session_state:
    st.session_state.winner_team = None

# Start 按钮
if st.button("Start"):
    st.session_state.group = [[None] * 4 for _ in range(8)]
    available_all = [
        ["Qatar", "Belgium", "Brazil", "France", "Argentina", "England", "Portugal", "Spain"],
        ["Denmark", "Netherlands", "Germany", "Switzerland", "Croatia", "Mexico", "USA", "Uruguay"],
        ["Iran", "Serbia", "Japan", "Senegal", "Tunisia", "Poland", "KoreaRep", "Morocco"],
        ["Wales/Scot/Ukr", "Peru/UAE/Au", "CostaRica/NZ", "Saudi Arabia", "Cameroon", "Ecuador", "Canada", "Ghana"]
    ]
    st.session_state.available = [row[:] for row in available_all]

    # Pot1 分配
    st.session_state.group[0][0] = "Qatar"
    st.session_state.available[0][0] = None
    remaining_pot1 = [t for t in st.session_state.available[0] if t is not None]
    random.shuffle(remaining_pot1)
    for idx in range(1, 8):
        st.session_state.group[idx][0] = remaining_pot1[idx - 1]
    st.session_state.available[0] = [None] * len(st.session_state.available[0])

    st.session_state.pot = 1
    st.session_state.grp_idx = 0
    st.session_state.initialized = True
    st.session_state.winner_team = None


# 单步执行函数（带动画）
def do_one_draw_step():
    pot = st.session_state.pot
    grp_idx = st.session_state.grp_idx
    group = st.session_state.group
    available = st.session_state.available

    teams = available[pot]
    non_none_indices = [i for i, t in enumerate(teams) if t is not None]
    if not non_none_indices:
        st.session_state.pot += 1
        st.session_state.grp_idx = 0
        return

    counts = {}
    samples = sample_valid_assignments(group, available, 50)
    for idx in non_none_indices:
        team = teams[idx]
        count = sum(1 for s in samples if s[grp_idx][pot] == team)
        counts[idx] = count

    non_zero = {idx: cnt for idx, cnt in counts.items() if cnt > 0}
    if not non_zero:
        return
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

    # 动画模拟抽签过程
    anim_placeholder = st.empty()
    current_team = None
    while True:
        choice = random.choice(list(N.keys()))
        current_team = teams[choice]
        NN[choice] += 1

        anim_df = pd.DataFrame({
            "Team": [teams[i] for i in N.keys()],
            "Target N": [N[i] for i in N.keys()],
            "Draw Count": [NN[i] for i in N.keys()]
        })

        styled_df = anim_df.style.apply(
            highlight_row,
            current_team=current_team,
            winner_team=None,
            axis=1
        )
        anim_placeholder.write(styled_df)

        time.sleep(0.5)

        if NN[choice] >= N[choice]:
            winner = choice
            break

    # 最终结果
    final_df = pd.DataFrame({
        "Team": [teams[i] for i in N.keys()],
        "Target N": [N[i] for i in N.keys()],
        "Draw Count": [NN[i] for i in N.keys()]
    })
    styled_final = final_df.style.apply(
        highlight_row,
        current_team=None,
        winner_team=teams[winner],
        axis=1
    )
    anim_placeholder.write(styled_final)

    # 更新状态
    group[grp_idx][pot] = teams[winner]
    st.session_state.winner_team = teams[winner]
    available[pot][winner] = None

    st.session_state.grp_idx += 1
    if st.session_state.grp_idx >= 8:
        st.session_state.pot += 1
        st.session_state.grp_idx = 0


# 快速完成抽签（无动画）
def finish_draw_fast():
    while st.session_state.pot <= 3:
        pot = st.session_state.pot
        grp_idx = st.session_state.grp_idx
        group = st.session_state.group
        available = st.session_state.available

        teams = available[pot]
        non_none_indices = [i for i, t in enumerate(teams) if t is not None]
        if not non_none_indices:
            st.session_state.pot += 1
            st.session_state.grp_idx = 0
            continue

        counts = {}
        samples = sample_valid_assignments(group, available, 50)
        for idx in non_none_indices:
            team = teams[idx]
            count = sum(1 for s in samples if s[grp_idx][pot] == team)
            counts[idx] = count

        non_zero = {idx: cnt for idx, cnt in counts.items() if cnt > 0}
        if not non_zero:
            winner = random.choice(non_none_indices)
        else:
            max_count = max(non_zero.values())
            normalized = {idx: cnt / max_count for idx, cnt in non_zero.items()}
            probs = list(normalized.values())
            winner = random.choice(list(normalized.keys()))

        group[grp_idx][pot] = teams[winner]
        available[pot][winner] = None

        st.session_state.grp_idx += 1
        if st.session_state.grp_idx >= 8:
            st.session_state.pot += 1
            st.session_state.grp_idx = 0


# 控制按钮显示
if st.session_state.initialized:
    if st.session_state.pot <= 3:
        if st.button("Next"):
            do_one_draw_step()
        if st.button("Finish Draw"):
            finish_draw_fast()

# 显示总表
if st.session_state.initialized:
    group_df = pd.DataFrame(st.session_state.group, columns=["Pot1", "Pot2", "Pot3", "Pot4"],
                            index=["Group A", "Group B", "Group C", "Group D",
                                   "Group E", "Group F", "Group G", "Group H"])
    st.subheader("Current Groups")
    st.dataframe(group_df)

    if st.session_state.pot > 3:
        st.success("Draw completed!")
