# ファイル名: poker_tools.py
# 概要: ポーカーの計算ロジック（Tool）を定義するファイル

import math
from google.adk.agents import tool

### 1.  勝率の計算 (自分は勝てるか？)
@tool
def calculate_equity_by_outs(outs: int, street: str) -> float:
    """
    アウツ(outs)の数と現在のストリート(street)に基づき、役が完成する確率(エクイティ)を概算します。
    'street'引数には "flop" (フロップ) または "turn" (ターン) を指定してください。
    
    例: フロップでアウツが9枚の場合、(outs=9, street="flop") と呼び出すと、約36% (9 x 4) が返されます。
    
    Args:
        outs: 役を完成させるカードの枚数（アウツ）。
        street: 現在のゲームの進行状況。"flop" または "turn" を指定します。

    Returns:
        役が完成する確率（%）。
    """
    if street.lower() == "flop":
        # フロップ → ターン・リバー (カード2枚分): アウツ x 4
        return float(outs * 4)
    elif street.lower() == "turn":
        # ターン → リバー (カード1枚分): アウツ x 2
        return float(outs * 2)
    else:
        return 0.0

### 2. オッズの計算 (この勝負は見合うか？)
@tool
def calculate_pot_odds_percentage(pot_before_bet: int, amount_to_call: int) -> float:
    """
    相手のベットに対し、コールするために数学的に必要な勝率（ポットオッズ%）を計算します。
    
    例: ポット1000点に相手が500点ベットした場合、(pot_before_bet=1000, amount_to_call=500) と呼び出します。
    必要な勝率は 500 / (1000 + 500 + 500) = 25% と計算されます。
    
    Args:
        pot_before_bet: 相手がベットする「前」のポットサイズ。
        amount_to_call: コールするために必要な額（＝相手のベット額）。

    Returns:
        コールが正当化されるために必要な最低勝率（%）。
    """
    if amount_to_call <= 0:
        return 0.0
    final_pot = pot_before_bet + amount_to_call + amount_to_call
    if final_pot == 0:
        return 0.0
    required_equity = (amount_to_call / final_pot) * 100.0
    return round(required_equity, 2)

### 3. ベット額の計算 (いくら賭けるか？)
@tool
def calculate_bet_size_by_fraction(current_pot: int, fraction: float) -> int:
    """
    現在のポット額に対し、指定された割合（分数）のベット額を計算します。
    
    例: ポットが1000点の時、(current_pot=1000, fraction=0.66) と呼び出すと、
    約660点 (2/3ポットベット) が計算されます。
    
    Args:
        current_pot: 現在のポット額。
        fraction: ポットに対する割合（例: 0.5 (1/2ポット), 0.66 (2/3ポット), 1.0 (ポットベット)）。

    Returns:
        計算されたベット額（整数）。
    """
    bet_amount = current_pot * fraction
    return int(round(bet_amount))

@tool
def calculate_raise_size_by_multiplier(base_amount: int, multiplier: float) -> int:
    """
    プリフロップのオープンレイズやリレイズ（3ベット）の額を、基準額の倍率で計算します。
    
    例: BBが20点で3倍レイズする場合、(base_amount=20, multiplier=3.0) と呼び出します (結果: 60)。
    
    Args:
        base_amount: 基準となる額（例: BBの額、または相手のレイズ額）。
        multiplier: 倍率（例: 3.0 (3倍レイズ)）。

    Returns:
        計算されたレイズ後の合計ベット額（整数）。
    """
    raise_amount = base_amount * multiplier
    return int(round(raise_amount))

### 4. 総合的な計算
@tool
def calculate_spr(current_pot: int, effective_stack: int) -> float:
    """
    SPR (Stack to Pot Ratio) を計算します。これはポット額に対する残りチップ量の比率です。
    数値が低いほど、オールインになりやすい（コミットしている）ことを示します。
    
    Args:
        current_pot: 現在のポット額。
        effective_stack: 有効スタックサイズ（自分と相手のうち、少ない方のチップ量）。

    Returns:
        SPRの値。
    """
    if current_pot <= 0:
        return float('inf')
    
    spr_value = effective_stack / current_pot
    return round(spr_value, 2)