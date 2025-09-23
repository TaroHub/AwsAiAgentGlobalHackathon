"""
条例生成モジュール
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class OrdinanceStructure:
    """条例構造"""
    title: str
    purpose: str
    definitions: Dict[str, str]
    chapters: List[str]
    articles: List[str]

class OrdinanceGenerator:
    """条例生成クラス"""

    def __init__(self):
        self.templates = {
            "子育て支援": {
                "title_template": "○○市子育て世帯支援条例",
                "purpose_template": "子育て世帯が安心して子どもを育てることができる社会の実現を図るため、必要な施策を総合的かつ計画的に推進することを目的とする。",
                "key_definitions": {
                    "子育て世帯": "市内に住所を有し、18歳に満たない子どもを養育する世帯",
                    "子育て支援": "子どもの健全な育成及び子育て世帯の負担軽減に資する支援"
                }
            },
            "高齢者支援": {
                "title_template": "○○市高齢者支援推進条例",
                "purpose_template": "高齢者が住み慣れた地域で安心して暮らし続けられる社会の実現を図るため、必要な施策を総合的かつ計画的に推進することを目的とする。",
                "key_definitions": {
                    "高齢者": "65歳以上の者",
                    "高齢者支援": "高齢者の健康保持、社会参加及び生活支援に資する支援"
                }
            },
            "環境政策": {
                "title_template": "○○市持続可能な環境都市推進条例",
                "purpose_template": "持続可能な社会の実現に向けて、環境の保全及び創造に関する施策を総合的かつ計画的に推進することを目的とする。",
                "key_definitions": {
                    "環境": "大気、水、土壌、生物その他の環境の構成要素",
                    "持続可能な発展": "環境を保全しつつ、将来の世代の需要を満たす能力を損なわない発展"
                }
            }
        }

    def generate_ordinance_draft(self, policy_context: Dict[str, Any]) -> OrdinanceStructure:
        """条例草案の生成"""

        domain = policy_context.get("policy_domain", "総合政策")
        title = policy_context.get("policy_title", "○○市政策推進条例")

        if domain in ["子ども・子育て支援", "子育て支援"]:
            template_key = "子育て支援"
        elif domain in ["高齢者福祉", "高齢者支援"]:
            template_key = "高齢者支援"
        elif domain in ["環境政策"]:
            template_key = "環境政策"
        else:
            template_key = "子育て支援"  # デフォルト

        template = self.templates[template_key]

        return OrdinanceStructure(
            title=title,
            purpose=template["purpose_template"],
            definitions=template["key_definitions"],
            chapters=self.generate_chapters(template_key),
            articles=self.generate_articles(template_key, policy_context)
        )

    def generate_chapters(self, template_key: str) -> List[str]:
        """章立ての生成"""
        return [
            "第1章 総則",
            "第2章 基本理念及び基本方針",
            "第3章 市の責務",
            "第4章 市民及び事業者の役割",
            "第5章 支援施策",
            "第6章 推進体制",
            "第7章 財政上の措置",
            "第8章 雑則",
            "附則"
        ]

    def generate_articles(self, template_key: str, policy_context: Dict[str, Any]) -> List[str]:
        """条文の生成"""

        if template_key == "子育て支援":
            return self.generate_childcare_articles(policy_context)
        elif template_key == "高齢者支援":
            return self.generate_elderly_articles(policy_context)
        elif template_key == "環境政策":
            return self.generate_environment_articles(policy_context)
        else:
            return self.generate_general_articles(policy_context)

    def generate_childcare_articles(self, policy_context: Dict[str, Any]) -> List[str]:
        """子育て支援条例の条文生成"""
        title = policy_context.get("policy_title", "子育て世帯支援条例")

        articles = [
            # 第1章 総則
            f"（目的）\n第1条　この条例は、子育て世帯が安心して子どもを育てることができる社会の実現を図るため、必要な施策を総合的かつ計画的に推進することを目的とする。",

            f"（定義）\n第2条　この条例において、次の各号に掲げる用語の意義は、当該各号に定めるところによる。\n(1) 子育て世帯　市内に住所を有し、18歳に満たない子どもを養育する世帯をいう。\n(2) 子育て支援　子どもの健全な育成及び子育て世帯の負担軽減に資する支援をいう。",

            # 第2章 基本理念
            f"（基本理念）\n第3条　子育て支援は、次に掲げる事項を基本理念として行うものとする。\n(1) 子どもの最善の利益が最優先に考慮されること\n(2) 保護者が子育てについての第一義的責任を有することを前提とし、地域社会全体で支援すること\n(3) 子どもの発達段階に応じた切れ目のない支援が提供されること",

            # 第3章 市の責務
            f"（市の責務）\n第4条　市は、前条の基本理念にのっとり、子育て支援に関する施策を総合的に企画し、実施する責務を有する。\n2　市は、子育て支援の推進に当たっては、国、県、関係機関及び民間団体等との連携を図るものとする。",

            # 第4章 市民・事業者の責務
            f"（市民の責務）\n第5条　市民は、子どもが健やかに成長できる環境づくりに努めなければならない。\n2　市民は、市が実施する子育て支援施策に協力するよう努めなければならない。",

            f"（事業者の責務）\n第6条　事業者は、従業員の仕事と子育ての両立を支援するよう努めなければならない。\n2　事業者は、その事業活動において、子育てしやすい環境の整備に配慮するよう努めなければならない。",

            # 第5章 支援施策
            f"（子育て支援施策）\n第7条　市は、子育て支援を推進するため、次に掲げる施策を講ずる。\n(1) 保育所、認定こども園、放課後児童クラブ等の整備及び運営の充実\n(2) 子育て世帯への経済的支援\n(3) 子育て相談、親子交流の場の提供\n(4) 地域による見守り活動の推進\n(5) 医療費助成制度の充実\n(6) その他市長が必要と認める施策",

            f"（経済的支援）\n第8条　市は、子育て世帯の経済的負担を軽減するため、18歳以下の子ども1人につき月額5,000円の支援金を支給する。\n2　前項の支援金の支給に関し必要な事項は、規則で定める。",

            # 第6章 推進体制
            f"（推進会議の設置）\n第9条　市は、子育て支援施策を総合的に推進するため、子育て支援推進会議（以下「推進会議」という。）を設置する。\n2　推進会議は、学識経験者、子育て当事者、関係団体の代表者その他市長が必要と認める者をもって組織する。",

            # 第7章 財政措置
            f"（財政上の措置）\n第10条　市は、子育て支援施策を推進するため、必要な財政上の措置を講ずるよう努めるものとする。",

            # 第8章 雑則
            f"（委任）\n第11条　この条例の施行に関し必要な事項は、市長が別に定める。",

            # 附則
            f"（施行期日）\n1　この条例は、公布の日から起算して6月を超えない範囲内において市長が規則で定める日から施行する。"
        ]

        return articles

    def generate_elderly_articles(self, policy_context: Dict[str, Any]) -> List[str]:
        """高齢者支援条例の条文生成"""
        title = policy_context.get("policy_title", "高齢者支援推進条例")

        articles = [
            f"（目的）\n第1条　この条例は、高齢者が住み慣れた地域で安心して暮らし続けられる社会の実現を図るため、必要な施策を総合的かつ計画的に推進することを目的とする。",

            f"（定義）\n第2条　この条例において「高齢者」とは、65歳以上の者をいう。",

            f"（基本理念）\n第3条　高齢者支援は、高齢者の尊厳が保持され、住み慣れた地域で自立した生活を営むことができるよう、医療、介護、予防、住まい及び生活支援が包括的に確保されることを基本理念とする。",

            f"（市の責務）\n第4条　市は、前条の基本理念にのっとり、高齢者支援に関する施策を総合的に企画し、実施する責務を有する。",

            f"（高齢者支援施策）\n第5条　市は、高齢者支援を推進するため、次に掲げる施策を講ずる。\n(1) 地域包括ケアシステムの構築\n(2) 介護予防及び健康づくりの推進\n(3) 生活支援サービスの充実\n(4) 社会参加の促進\n(5) デジタル格差の解消\n(6) その他市長が必要と認める施策"
        ]

        return articles

    def generate_environment_articles(self, policy_context: Dict[str, Any]) -> List[str]:
        """環境政策条例の条文生成"""
        title = policy_context.get("policy_title", "持続可能な環境都市推進条例")

        articles = [
            f"（目的）\n第1条　この条例は、持続可能な社会の実現に向けて、環境の保全及び創造に関する施策を総合的かつ計画的に推進することを目的とする。",

            f"（定義）\n第2条　この条例において「環境」とは、大気、水、土壌、生物その他の環境の構成要素をいう。",

            f"（基本理念）\n第3条　環境の保全及び創造は、現在及び将来の市民が健康で文化的な生活を営む上で必要な環境を確保することを旨として行わなければならない。",

            f"（環境施策）\n第4条　市は、環境の保全及び創造を推進するため、次に掲げる施策を講ずる。\n(1) 温室効果ガスの削減\n(2) 再生可能エネルギーの導入促進\n(3) 廃棄物の削減及びリサイクルの推進\n(4) 生物多様性の保全\n(5) 環境教育の推進"
        ]

        return articles

    def generate_general_articles(self, policy_context: Dict[str, Any]) -> List[str]:
        """一般的な条例の条文生成"""
        return [
            f"（目的）\n第1条　この条例は、市民の福祉向上を図るため、必要な施策を総合的かつ計画的に推進することを目的とする。",
            f"（市の責務）\n第2条　市は、前条の目的を達成するため、必要な施策を実施する責務を有する。"
        ]

    def format_ordinance_text(self, structure: OrdinanceStructure) -> str:
        """条例文書の整形"""
        formatted_text = f"""
{structure.title}

{structure.purpose}

【定義】
"""
        for key, value in structure.definitions.items():
            formatted_text += f"・{key}：{value}\n"

        formatted_text += "\n【条文】\n"
        for i, article in enumerate(structure.articles, 1):
            formatted_text += f"{article}\n\n"

        return formatted_text