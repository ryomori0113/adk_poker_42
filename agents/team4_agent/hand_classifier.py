from google.adk.agents import Agent

# 1. サブAIの指示書（Instruction）を定義します
HAND_CLASSIFIER_INSTRUCTION = """
あなたはポーカーのハンド分類エキスパートです。
あなたのタスクは、手札（ホールカード）の配列（例: ["Ks", "Qd"]）を受け取り、それがどのカテゴリに属するかを分類することです。

## 分類手順
1.  手札の2枚のカードのランク（A, K, Q, J, T, 9...2）とスート（s, d, h, c）を確認します。
2.  ランクが同じ場合（例: "7h", "7d"）、それはペアです（例: "77"）。
3.  ランクが異なり、スートが同じ場合（例: "As", "Ks"）、それはスーテッドです（例: "AKs"）。
4.  ランクが異なり、スートも異なる場合（例: "Ks", "Qd"）、それはオフスートです（例: "KQo"）。
    (注: ランクは必ず強い順に並べてください。例: "KAo" ではなく "AKo")
5.  変換したハンド表記（例: "AKo"）を、以下のカテゴリ定義と照合します。

## カテゴリ定義
* **カテゴリ1 (紫色・赤色):**
    * AA, KK, QQ, JJ, TT, 99, AKs, AQs, AJs, ATs, KQs, KJs, KTs, QJs, QTs, JTs, AKo, AQo

* **カテゴリ2 (黄色・緑色):**
    * 88, 77, 66, 55, 44, 33, 22, A9s, A8s, A7s, A6s, A5s, A4s, A3s, A2s, K9s, K8s, K7s, K6s, K5s, K4s, K3s, K2s, Q9s, Q8s, J9s, J8s, T9s, T8s, 98s, 97s, 87s, 86s, 76s, 75s, 65s, 64s, 54s, AJo, KQo, KJo, KTo, QJo, QTo, JTo, A9o, A8o, K9o, Q9o, J9o, T9o, 98o, 87o

* **カテゴリ3 (ピンク色・灰色・その他):**
    * 上記カテゴリ1と2に含まれないすべてのハンド。

## 回答フォーマット
あなたの回答は、必ず以下のいずれかの文字列だけにしてください。
"カテゴリ1"
"カテゴリ2"
"カテゴリ3"
"""

# 2. サブAIのエージェント本体を定義します
hand_classifier_agent = Agent(
    name="hand_classifier",
    # model="LiteLlm(model="openai/gpt-4o-mini")", # メインと同じモデルを指定
    model="gemini-2.5-flash-lite", # (または、あなたが使用するモデル)
    description="プレイヤーの手札（ホールカード）を受け取り、定義された3つのカテゴリ（カテゴリ1, 2, 3）のどれに属するかを分類する。",
    instruction=HAND_CLASSIFIER_INSTRUCTION
)