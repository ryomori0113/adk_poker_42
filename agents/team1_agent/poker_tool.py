# ファイル名: poker_tools.py
# 概要: ポーカーの計算を専門に行うツールのコレクション
#
# これらの関数は、メインのAIエージェント（司令官）から
# 「Tool」として呼び出されることを想定しています。

import math

# --- 1. 期待値（EV）の判断材料となる「勝率」を計算する ---

def calculate_equity_by_outs(outs: int, street: str) -> float:
    """
    アウツ(outs)の数と現在のストリート(street)に基づき、
    役が完成する確率（勝率）を簡易計算します。
    
    これは「自分の勝率」を計算するためのもので、
    この後「コールに必要な勝率 (ポットオッズ)」と比較するために使います。

    :param outs: 役が完成するために必要なカードの枚数 (例: フラッシュドローなら9枚)
    :param street: "flop" (フロップ) または "turn" (ターン)
    :return: 勝率のパーセンテージ (例: 34.1)
    """
    if street == "flop":
        # フロップ -> リバー (2枚のカードが来る)
        # (アウツ / 47) + (アウツ / 46) * ( (47-アウツ) / 47 )
        # 簡易計算 (アウツ * 4) よりも正確な計算式
        prob = 1 - ((47 - outs) / 47) * ((46 - outs) / 46)
        return round(prob * 100, 1)
        
    elif street == "turn":
        # ターン -> リバー (1枚のカードが来る)
        # (アウツ / 46)
        prob = (outs / 46)
        return round(prob * 100, 1)
        
    else:
        # プリフロップやリバーではこの計算は使わない
        return 0.0

# --- 2. 期待値（EV）の判断材料となる「必要勝率」を計算する ---

def calculate_pot_odds_percentage(pot_size: float, amount_to_call: float) -> float:
    """
    ポットオッズ（コールするために必要な勝率）を計算します。
    
    「自分の勝率」がこの「必要勝率」を上回っていれば、
    期待値（EV）がプラスであると判断できます。

    :param pot_size: 現在のポットの総額
    :param amount_to_call: コールするために必要な金額
    :return: 必要勝率のパーセンテージ (例: 25.0)
    """
    # ゼロ割エラーを防ぐ
    if pot_size + amount_to_call == 0:
        return 0.0
        
    # 計算式: (コール額) / (コール後のポット総額)
    # 例: ポット100, コール額50 -> 50 / (100 + 50) = 33.3%
    required_percentage = (amount_to_call / (pot_size + amount_to_call)) * 100
    return round(required_percentage, 1)

# --- 3. ベット額やレイズ額を計算する ---

def calculate_bet_size(pot_size: float, fraction: float) -> float:
    """
    ポットサイズに対する指定された割合（フラクション）のベット額を計算します。
    (例: ポットの75%ベット)
    
    これは、AIが「ポットの7割をベットしよう」と判断したときに、
    正確な金額を計算するために使います。

    :param pot_size: 現在のポットの総額
    :param fraction: ベットする割合 (例: 0.5 for 50%, 0.75 for 75%)
    :return: 計算されたベット額
    """
    if pot_size <= 0 or fraction <= 0:
        return 0.0
        
    bet_amount = pot_size * fraction
    # チップは通常整数なので、四捨五入して整数にする
    return round(bet_amount)

