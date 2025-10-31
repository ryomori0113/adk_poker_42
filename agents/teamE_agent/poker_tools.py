# ファイル名: poker_tools.py
# 概要: ポーカーの計算を専門に行うツールのコレクション

import math

def calculate_equity_by_outs(outs: int, street: str) -> float:
    """
    アウツ(outs)の数と現在のストリート(street)に基づき、
    次のカードで役が完成する確率（勝率）を簡易計算します。
    
    :param outs: 役が完成するために必要なカードの枚数 (例: フラッシュドローなら9枚)
    :param street: "flop" (フロップ) または "turn" (ターン)
    :return: 勝率のパーセンテージ (例: 34.1)
    """
    if street == "flop":
        # フロップ -> リバー (2枚のカードが来る)
        # (アウツ / 47) + (アウツ / 46) * ( (47-アウツ) / 47 )
        # 簡易計算 (アウツ * 4) を使うことが多いが、ここではもう少し正確に計算
        prob = 1 - ((47 - outs) / 47) * ((46 - outs) / 46)
        return round(prob * 100, 1)
    elif street == "turn":
        # ターン -> リバー (1枚のカードが来る)
        # (アウツ / 46)
        prob = (outs / 46)
        return round(prob * 100, 1)
    else:
        return 0.0

def calculate_pot_odds_percentage(pot_size: float, amount_to_call: float) -> float:
    """
    ポットオッズ（コールするために必要な勝率）を計算します。
    
    :param pot_size: 現在のポットの総額
    :param amount_to_call: コールするために必要な金額
    :return: 必要勝率のパーセンテージ (例: 25.0)
    """
    if pot_size + amount_to_call == 0:
        return 0.0
        
    # (コール額) / (コール後のポット総額)
    required_percentage = (amount_to_call / (pot_size + amount_to_call)) * 100
    return round(required_percentage, 1)

def calculate_bet_size(pot_size: float, fraction: float) -> float:
    """
    ポットサイズに対する指定された割合（フラクション）のベット額を計算します。
    (例: ポットの75%ベット)
    
    :param pot_size: 現在のポットの総額
    :param fraction: ベットする割合 (例: 0.5 for 50%, 0.75 for 75%)
    :return: 計算されたベット額
    """
    bet_amount = pot_size * fraction
    return round(bet_amount)