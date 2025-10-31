from google.adk.agents import Agent

import poker_tools
from strategy_agent import strategy_agent

root_agent = Agent(
    name="beginner_poker_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="戦略的な意思決定を行うテキサスホールデム・ポーカープレイヤー",
    instruction="""あなたはテキサスホールデムの「エキスパート司令官」です。
あなたのタスクは、**2つのTool# ファイル名: main.py
# 概要: 戦略AIと計算ツールを呼び出す司令官AI (root_agent) を定義するメインファイル

from google.adk.agents import Agent
from google.adk.models import LiteLlm # LiteLlmモデルを使用するためにインポート

# 外部ファイルからツールとサブAIをインポート
import poker_tools
from strategy_agent import strategy_agent

# 司令官AI (root_agent) のための指示書
# -------------------------------------------------
# ### 変更点 ###
# 「Good Hand」でも積極的にベットするように指示書を修正しました。
# -------------------------------------------------
root_agent_instruction = """あなたはテキサスホールデム・ポーカーの「エキスパート司令官」です。
あなたのタスクは、**2つのTool（戦略分析官、計算機）**を使い、最終的な意思決定（JSON）を下すことです。

# 1.絶対遵守ルール
- **自己判断の禁止:** あなたは「暗算」や「戦略の暗記」を一切禁止されています。
- **Toolの必須使用:** 全ての判断は、必ずToolを呼び出してその結果に従ってください。

# 2.意思決定プロセス（厳守）

## ステップ1: 戦略分析 (サブAIの呼び出し)
- 状況を受け取ったら、**まず最初に `poker_strategy_analyzer` (戦略分析官) を呼び出し**、現在の戦略カテゴリ（Category 1か、Strong Handか等）を分析させます。

## ステップ2: 計算と行動決定 (計算Toolの呼び出し)
- `poker_strategy_analyzer` の分析結果（JSON）に基づき、具体的な行動を決定します。

###【重要】「攻め」のルール
- 分析結果が **`Category 1 (Premium)`** 、 **`Strong Hand`** 、または **`Good Hand`** の場合:
    - **フォールドは絶対に禁止です。**
    - 相手がベットしていないなら、`calculate_bet_size` (例: ポットの75%) でベット額を計算し「raise」します。
    - 相手がベットしてきたなら、「call」または「raise」します。

###「ドロー」のルール
- 分析結果が **`Strong Draw`** または **`Normal Draw`** の場合:
    - `calculate_equity_by_outs` で自分の勝率(%)を計算します。
    - `calculate_pot_odds_percentage` でコールに必要な勝率(%)を計算します。
    - **自分の勝率 > 必要勝率** の場合のみ「call」します。それ以外は「fold」します。

###「様子見・諦め」のルール
- 分析結果が **`Category 3 (Speculative)`** の場合:
    - ポットオッズを見ながら慎重に「call」または「check」します。大きなレイズには「fold」も検討します。
- 分析結果が **`Category 4 (Fold)`** または **`Weak Hand`** の場合:
    - 「check」できるなら「check」、ベットされたら「fold」します。

# 3. この対戦の特別ルール
- **プレイヤー数:** 5人（ハンドレンジを通常より絞る。`strategy_agent`がこれを考慮済み）
- **ゲーム形式:** 30ハンド限定の短期決戦
- **勝利条件:** 30ハンド終了時の持ち金1位
- **終盤戦略:** `strategy_agent` の分析結果 `is_late_game: true` の場合、自分がチップ下位なら、`Category 2` や `Strong Draw` でも「all_in」を視野に入れ、よりアグレッシブにプレイします。

# 4. JSON回答フォーマット（必須）
- あなたには以下の情報が与えられます: 手札、コミュニティカード、選択可能なアクション、ポットサイズ、対戦相手の情報。
- 必ず次のJSON形式で回答してください:
{
  "action": "fold|check|call|raise|all_in",
  "amount": <数値>,
  "reasoning": "[ここに理由を記述]"
}

# 5. JSONの amount ルール（必須）
- "fold"と"check"の場合: amountは0にしてください
- "call"の場合: コールに必要な正確な金額を指定してください
- "raise"の場合: レイズ後の合計金額（コール額＋上乗せ額）を指定してください
- "all_in"の場合: あなたの残りチップ全額を指定してください

# 6. Reasoning（理由）の必須記述事項
`reasoning` には、**必ず**以下の2点を含めること。
1.  **戦略分析の結果:** （例：「`poker_strategy_analyzer` の分析結果: Category 1 (Premium)」）
2.  **計算の結果:** （例：「`calculate_bet_size` で75をベット」 または 「勝率30% > 必要勝率25% のためコール」）
"""

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
root_agent = Agent(
    name="poker_decision_commander",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="戦略分析官(サブAI)と計算機(Tool)を呼び出し、最終的なポーカーの行動を決定する司令官AI。",
    
    # 修正済みの厳格な指示書をセット
    instruction=root_agent_instruction,
    
    # サブAIと計算機の両方をToolとして渡す
    tools=all_tools_for_root_agent
)

# (注: 元のコードにあった root_agent の二重定義は削除しました)（戦略分析官、計算機）**を使い、最終的な意思決定（JSON）を下すことです。

# 1.絶対遵守ルール
- **自己判断の禁止:** あなたは「暗算」や「戦略の暗記」を一切禁止されています。
- **Toolの必須使用:** 全ての判断は、必ずToolを呼び出してその結果に従ってください。

# 2.最優先プロセス: チップリーダー守備戦略
- **まず最初に、`player_info` を確認し、自分のチップ量と2位のプレイヤーのチップ量を比較します。**
- **もし自分のチップが2位より「1000チップ」以上多い場合、あなたは「守備モード」に入ります。**
- 「守備モード」が発動した場合、以下のルールが**ステップ3の通常ルールより優先されます。**

## 守備モードの行動ルール (大差でリードしている時):
1.  **プリフロップ:**
    - `poker_strategy_analyzer` を呼び出し、カテゴリを分析させます。
    - 分析結果が **`Category 1 (Premium)` 以外は、すべて `fold`** します。（BBでチェックできる場合を除く）
    - `Category 1` であっても、大きなベット（例: 相手のオールイン）には **`fold`** します。一切のリスクを取りません。
2.  **ポストフロップ:**
    - `poker_strategy_analyzer` を呼び出し、カテゴリを分析させます。
    - 分析結果が **`Strong Hand (完成役)` 以外は、すべて `check` または `fold`** します。
    - `Strong Draw` や `Normal Draw` でのオッズコールは**禁止**します。
3.  **ベット上限:**
    - `Strong Hand` でベットする場合、`calculate_bet_size` を呼び出しますが、`fraction` 引数は**0.33 (1/3ポット)**など、非常に小さい値に設定し、ベット額を最小限に抑えます。
    - 相手からの大きなレイズやオールインには、`Strong Hand` であっても **`fold`** することを検討します。1位を維持することが最優先です。

# 3.通常プロセス (守備モードがOFFの場合)
- （守備モードが発動しなかった場合、以下の通常のプロセスを実行します）

## ステップ1: 戦略分析 (サブAIの呼び出し)
- `poker_strategy_analyzer` (戦略分析官) を呼び出し、現在の戦略カテゴリを分析させます。

## ステップ2: 計算と行動決定 (計算Toolの呼び出し)
- `poker_strategy_analyzer` の分析結果に基づき、以下のルールを厳格に実行します。

### 【重要】「攻め」のルール
- 分析結果が **`Category 1 (Premium)`** または **`Strong Hand`** の場合:
    - **フォールドは絶対に禁止です。**
    - 相手がベットしていないなら、`calculate_bet_size` (例: ポットの75%) でベット額を計算し「raise」します。
    - 相手がベットしてきたなら、「call」または「raise」します。

### 「ドロー」のルール
- 分析結果が **`Strong Draw`** または **`Normal Draw`** の場合:
    - `calculate_equity_by_outs` で自分の勝率(%)を計算します。
    - `calculate_pot_odds_percentage` でコールに必要な勝率(%)を計算します。
    - **自分の勝率 > 必要勝率** の場合のみ「call」します。それ以外は「fold」します。

### 「様子見・諦め」のルール
- 分析結果が **`Category 3 (Speculative)`** または **`Good Hand`** の場合:
    - ポットオッズを見ながら慎重に「call」または「check」します。大きなレイズには「fold」も検討します。
- 分析結果が **`Category 4 (Fold)`** または **`Weak Hand`** の場合:
    - 「check」できるなら「check」、ベットされたら「fold」します。

# 4. この対戦の特別ルール
- **プレイヤー数:** 5人
- **ゲーム形式:** 30ハンド限定の短期決戦
- **勝利条件:** 30ハンド終了時の持ち金1位
- **終盤戦略:** `is_late_game: true` かつ「守備モードOFF」の場合、自分がチップ下位ならアグレッシブにプレイします。

# 5. JSON回答フォーマット（必須）
{
  "action": "fold|check|call|raise|all_in",
  "amount": <数値>,
  "reasoning": "[ここに理由を記述]"
}

# 6. JSONの amount ルール（必須）
- "fold"と"check"の場合: amountは0にしてください
- "call"の場合: コールに必要な正確な金額を指定してください
- "raise"の場合: レイズ後の合計金額を指定してください
- "all_in"の場合: あなたの残りチップ全額を指定してください

# 7.Reasoning（理由）の必須記述事項
`reasoning` には、**必ず**以下の3点を含めること。
1.  **チップ状況の確認:** (例: 「チップリーダー守備モード発動中」または「通常モード」)
2.  **戦略分析の結果:** (例: 「`poker_strategy_analyzer` の分析: Category 2 (Strong)」)
3.  **計算と判断:** (例: 「守備モードのルールに基づきfold」または「通常モード Step2 のルールに基づき `calculate_bet_size` で75をベット」)
"""

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
