"""
政策分析モジュール
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class PolicyContext:
    """政策コンテキスト"""
    domain: str
    priority: int
    complexity: str
    stakeholders: List[str]
    legal_basis: List[str]

class PolicyAnalyzer:
    """政策分析クラス"""

    def __init__(self):
        self.policy_keywords = {
            "子育て支援": {
                "keywords": ["子育て", "保育", "育児", "子ども", "乳幼児", "学童"],
                "legal_basis": ["児童福祉法", "子ども・子育て支援法"],
                "stakeholders": ["保護者", "保育園", "学校", "子育て支援センター"]
            },
            "高齢者支援": {
                "keywords": ["高齢者", "介護", "年金", "シニア", "老人", "敬老"],
                "legal_basis": ["介護保険法", "高齢者医療確保法"],
                "stakeholders": ["高齢者", "介護事業者", "医療機関", "家族"]
            },
            "環境政策": {
                "keywords": ["環境", "エコ", "温暖化", "リサイクル", "再生可能", "CO2"],
                "legal_basis": ["環境基本法", "地球温暖化対策推進法"],
                "stakeholders": ["市民", "環境団体", "企業", "研究機関"]
            },
            "教育政策": {
                "keywords": ["教育", "学校", "学習", "教師", "生徒", "学力"],
                "legal_basis": ["教育基本法", "学校教育法"],
                "stakeholders": ["児童生徒", "教職員", "保護者", "教育委員会"]
            },
            "防災政策": {
                "keywords": ["防災", "災害", "地震", "避難", "緊急", "安全"],
                "legal_basis": ["災害対策基本法", "消防法"],
                "stakeholders": ["市民", "消防署", "自主防災組織", "医療機関"]
            }
        }

    def analyze_policy_domain(self, text: str) -> PolicyContext:
        """政策領域の分析"""

        domain_scores = {}

        for domain, config in self.policy_keywords.items():
            score = 0
            for keyword in config["keywords"]:
                score += text.lower().count(keyword.lower())
            domain_scores[domain] = score

        # 最高スコアの領域を選択
        primary_domain = max(domain_scores, key=domain_scores.get) if max(domain_scores.values()) > 0 else "総合政策"

        # コンテキスト情報を構築
        if primary_domain in self.policy_keywords:
            config = self.policy_keywords[primary_domain]
            return PolicyContext(
                domain=primary_domain,
                priority=self._assess_priority(text),
                complexity=self._assess_complexity(text),
                stakeholders=config["stakeholders"],
                legal_basis=config["legal_basis"]
            )
        else:
            return PolicyContext(
                domain="総合政策",
                priority=2,
                complexity="中程度",
                stakeholders=["市民", "行政"],
                legal_basis=["地方自治法"]
            )

    def _assess_priority(self, text: str) -> int:
        """優先度評価（1:高 2:中 3:低）"""
        high_priority_words = ["緊急", "早急", "重要", "深刻", "危機"]
        medium_priority_words = ["必要", "改善", "検討", "推進"]

        high_count = sum(1 for word in high_priority_words if word in text)
        medium_count = sum(1 for word in medium_priority_words if word in text)

        if high_count > 0:
            return 1
        elif medium_count > 0:
            return 2
        else:
            return 3

    def _assess_complexity(self, text: str) -> str:
        """複雑度評価"""
        complexity_indicators = {
            "高": ["制度", "システム", "法律", "条例", "組織", "予算"],
            "中": ["施策", "事業", "サービス", "支援", "活動"],
            "低": ["情報", "案内", "相談", "窓口"]
        }

        scores = {}
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            scores[level] = score

        return max(scores, key=scores.get) if max(scores.values()) > 0 else "中"

    def extract_key_phrases(self, text: str) -> List[str]:
        """キーフレーズの抽出"""
        # 簡易的な名詞句抽出
        patterns = [
            r'[ぁ-んァ-ン一-龯]+(?:支援|制度|政策|対策|事業|施策)',
            r'[ぁ-んァ-ン一-龯]+(?:の|に関する)[ぁ-んァ-ン一-龯]+',
            r'[ぁ-んァ-ン一-龯]{3,}'
        ]

        key_phrases = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            key_phrases.extend(matches)

        # 重複除去と長さでフィルタリング
        key_phrases = list(set([phrase for phrase in key_phrases if len(phrase) >= 3]))

        return key_phrases[:10]  # 上位10個を返す

    def identify_target_groups(self, text: str) -> List[str]:
        """対象グループの特定"""
        target_groups = {
            "子育て世帯": ["子育て", "保育", "育児", "子ども"],
            "高齢者": ["高齢者", "シニア", "老人", "介護"],
            "学生": ["学生", "生徒", "児童", "学校"],
            "働く世代": ["働く", "就労", "労働", "サラリーマン"],
            "女性": ["女性", "母親", "ママ"],
            "障害者": ["障害", "バリアフリー", "アクセシビリティ"],
            "外国人": ["外国人", "国際", "多文化"],
            "起業家": ["起業", "創業", "ベンチャー", "中小企業"]
        }

        identified_groups = []
        for group, keywords in target_groups.items():
            if any(keyword in text for keyword in keywords):
                identified_groups.append(group)

        return identified_groups if identified_groups else ["市民全般"]

    def suggest_related_policies(self, domain: str) -> List[str]:
        """関連政策の提案"""
        related_policies = {
            "子育て支援": [
                "保育所整備事業",
                "放課後児童クラブ運営",
                "子育て支援センター事業",
                "医療費助成制度",
                "児童手当制度"
            ],
            "高齢者支援": [
                "地域包括ケアシステム",
                "介護予防事業",
                "高齢者見守りサービス",
                "シルバー人材センター",
                "デジタル格差解消事業"
            ],
            "環境政策": [
                "再生可能エネルギー導入促進",
                "省エネルギー推進事業",
                "廃棄物削減・リサイクル",
                "緑化推進事業",
                "環境教育プログラム"
            ],
            "教育政策": [
                "ICT教育推進",
                "特別支援教育",
                "生涯学習推進",
                "図書館機能充実",
                "国際理解教育"
            ],
            "防災政策": [
                "地域防災計画",
                "避難所整備",
                "防災教育",
                "情報伝達システム",
                "自主防災組織支援"
            ]
        }

        return related_policies.get(domain, ["総合計画事業", "市民サービス向上事業"])