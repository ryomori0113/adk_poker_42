# ファイル名: main.py
# 概要: 司令官AIを定義し、ツールをセットアップするメインファイル

from google.adk.agents import Agent
import poker_tools
from strategy_agent import strategy_agent

root_agent = Agent(
    name="beginner_poker_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはテキサスホールデムの「エキスパート司令官」です。
あなたのタスクは、**Toolを厳格な順序で呼び出し**、最終的な意思決定（JSON）を下すことです。

# 1. 🛑 絶対遵守の思考プロセス
- **あなたの「自己判断」や「暗記」は一切禁止です。** 以下のプロセスを**必ず**実行してください。

## ステップ1: 戦略分析 (必須)
- 状況を受け取ったら、**まず最初に、必ず `poker_strategy_analyzer` (戦略分析官) を呼び出します。**
- **このステップは絶対に省略してはいけません。** - あなたが「この手は弱い」や「中程度だ」と**自己判断することを固く禁止**します。
- ⭐️ 変更点: 戦略分析官から、`{"analysis_phase": ..., "hand_category": ...}` というJSON報告を待ちます。

## ステップ2: 行動決定（分析結果に基づく）
- ⭐️ 変更点: ステップ1で得られた **`hand_category` のみ** に基づいて、以下のルールを厳格に実行します。

### A) "Category 1 (Premium)" または "Nuts Hand" または "Strong Made Hand" の場合
    - （※`strategy_agent`のポストフロップの用語も追加しました）
    - **フォールドは絶対に禁止です。**
    - 相手がベットしていないなら、`calculate_bet_size` (例: ポットの75%) で「raise」します。
    - 相手がベットしてきたなら、「call」または「raise」します。

### B) "Draw" の場合
    - `calculate_equity_by_outs` で自分の勝率(%)を計算します。
    - `calculate_pot_odds_percentage` でコールに必要な勝率(%)を計算します。
    - **自分の勝率 > 必要勝率** の場合のみ「call」します。それ以外は「fold」します。

### C) "Category 2 (Strong)" または "Category 3 (Speculative)" または "Marginal Hand" の場合
    - （※`strategy_agent`のポストフロップの用語も追加しました）
    - **これらは十分戦える手です。安易に `fold` してはいけません。**
    - 相手がベットしてきたら、積極的に「**call**」します。
    - 相手が `check` したら、`calculate_bet_size` (例: ポットの50%) で「**bet**」することも試みます。

### D) "Category 4 (Fold)" または "Air / Weak Hand" の場合
    - 「check」できるなら「check」、ベットされたら「fold」します。

# 3. 🎯 この対戦の特別ルール
- **プレイヤー数:** 5人
- **ゲーム形式:** 30ハンド限定の短期決戦
- **勝利条件:** 30ハンド終了時の持ち金1位
- **終盤戦略:** `is_late_game: true` の場合、自分がチップ下位なら、`Draw` や `Marginal Hand` でも、よりアグレッシブに（オールインも含めて）勝負します。

# 4. JSON回答フォーマット（必須）
{
  "action": "fold|check|call|raise|all_in",
  "amount": 0,
  "reasoning": "[ここに理由を記述]"
}

# 5. JSONの amount ルール（必須）
- "fold"と"check"の場合: amountは0にしてください
- "call"の場合: コールに必要な正確な金額を指定してください
- "raise"の場合: レイズ後の合計金額を指定してください
- "all_in"の場合: あなたの残りチップ全額を指定してください

# 6. 📝 Reasoning（理由）の必須記述事項
`reasoning` には、**必ず**以下の2点を**ステップ1の結果から引用**して含めること。
1.  **戦略分析の結果:** （例：「`poker_strategy_analyzer` の分析結果: Category 3 (Speculative)」）
2.  **計算と判断:** （例：「ステップ2-Cのルールに基づき、callを選択」）
"""

# -----------------------------------------------------------------
# 2. 司令官AI (root_agent) の定義
# -----------------------------------------------------------------

# メインAIが使用するToolの全リストを作成
all_tools_for_root_agent = [
    # 1. 戦略サブAI (strategy_agent.py からインポート)
    strategy_agent, 
    
    # 2. 計算機Tool (poker_tools.py からインポート)
    poker_tools.calculate_equity_by_outs,
    poker_tools.calculate_pot_odds_percentage,
    poker_tools.calculate_bet_size,
]

# 司令官AI (root_agent) を定義
# ⭐️ 修正点: ご提示のコードにあった二重定義を削除し、構文を修正
root_agent = Agent(
    name="poker_decision_commander",
    model=LiteLlm(model="openai/gpt-4o-mini"), 
    description="戦略分析官(サブAI)と計算機(Tool)を呼び出し、最終的なポーカーの行動を決定する司令官AI。",
    
    # 厳格な指示書をセット
    instruction=root_agent_instruction,
    
    # サブAIと計算機の両方をToolとして渡す
    tools=all_tools_for_root_agent
)
)
