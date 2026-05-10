#!/usr/bin/env python3
"""
ed-source.html (教育委員会向け指針) を ハイブリッドサイトに統合する

実行:
    python integrate_ed.py --src ed-source.html --dst /tmp/dist-hybrid

機能:
1. ed.htmlのプレースホルダーを削除し、本文をそのまま流し込む
2. ed専用CSSを css/ed.css として外部化
3. 左サイドバー + 上部ナビ の混在は避ける(ed.htmlだけ特殊レイアウト)
4. 末尾ボタンを「← トップに戻る」「監査アプリへ進む →」の2ボタンに変更
5. .card の枠線・影を削減して開放感を出す(リスクボックスの色は維持)
"""

import argparse
from pathlib import Path
from html import escape

from bs4 import BeautifulSoup

BASE_URL = "https://ptaorg.github.io/1/"


def integrate_ed(src_path, dst_dir):
    """ed-source.html を ed.html として dst_dir に統合"""
    with open(src_path, encoding="utf-8") as f:
        ed_soup = BeautifulSoup(f.read(), "html.parser")

    # 1. 本文(main-wrapper)とサイドバー(aside)を取り出す
    aside = ed_soup.find("aside")
    main_wrapper = ed_soup.find(class_="main-wrapper")
    inner_script = None
    for s in ed_soup.find_all("script"):
        if s.string and "setActive" in s.string:
            inner_script = s
            break

    if not main_wrapper:
        print("error: main-wrapper not found in ed-source")
        return

    # 2. main-wrapperの中の <main> 要素 (実際のコンテンツ)
    inner_main = main_wrapper.find("main")
    if not inner_main:
        body_html = main_wrapper.decode_contents()
    else:
        body_html = inner_main.decode_contents()

    body_soup = BeautifulSoup(body_html, "html.parser")

    # ===== 改良点 2: サイドバーtitleを「目次」に変えて重複感を解消 =====
    if aside:
        site_title = aside.find("div", class_="site-title")
        if site_title:
            # 既存の "教育委員会向け / PTA運営適正化指針" を残しつつ、上に「目次」見出しを足す
            new_title = ed_soup.new_tag("div", **{"class": "site-title"})
            heading = ed_soup.new_tag("div", style="font-size:.78rem;letter-spacing:.18em;color:#94a3b8;font-weight:900;margin-bottom:6px")
            heading.string = "TABLE OF CONTENTS"
            new_title.append(heading)
            # 元のtitleテキストを保持
            for child in list(site_title.children):
                new_title.append(child)
            site_title.replace_with(new_title)

    # ===== 改良点 3: 章番号の続きとして "8. お問い合わせ・関連リンク" を新設 =====
    # 末尾のCTAをこの章の中に意味的に組み込む
    last_section = body_soup.find_all("section")[-1] if body_soup.find_all("section") else None
    cta = body_soup.find("div", class_="cta-wrapper")

    # ===== 改良点 5: Q&A検索ボックスを追加 =====
    faq_section = body_soup.find("section", id="faq")
    if faq_section:
        h2 = faq_section.find("h2")
        if h2:
            search_box = body_soup.new_tag("div", **{"class": "faq-search-wrap"})
            inp = body_soup.new_tag("input", **{
                "type": "text",
                "id": "faqSearch",
                "class": "faq-search",
                "placeholder": "Q&Aを検索（例: 名簿、会費、職員）"
            })
            note = body_soup.new_tag("p", **{"class": "faq-search-note"})
            faq_count = len(faq_section.find_all("div", class_="faq-item"))
            note.string = f"全 {faq_count} 問。キーワードで絞り込めます。"
            search_box.append(inp)
            search_box.append(note)
            h2.insert_after(search_box)

    # ===== 改良点 4: e-Govリンクの整理（一次資料章を「重要 / 参考」に二段化） =====
    sources_section = body_soup.find("section", id="sources")
    if sources_section:
        ol = sources_section.find("ol")
        if ol:
            lis = ol.find_all("li", recursive=False)
            # 重要(教委が必ず確認すべき): 最初の6本(社会教育法・学校教育法・地教行法・個人情報保護法・PPCガイドライン・地公法)
            important_count = 6
            if len(lis) > important_count:
                # 重要LIをまとめる新しい ol
                important_ol = body_soup.new_tag("ol", **{"class": "source-important"})
                for li in lis[:important_count]:
                    important_ol.append(li.extract())

                heading_imp = body_soup.new_tag("h3", **{"class": "source-heading"})
                heading_imp.string = "教育委員会が必ず確認すべき一次資料"
                ol.insert_before(heading_imp)
                ol.insert_before(important_ol)

                # 残りは <details> で折り畳み
                heading_ref = body_soup.new_tag("h3", **{"class": "source-heading"})
                heading_ref.string = "参考一次資料・行政資料(展開してご覧ください)"

                details = body_soup.new_tag("details", **{"class": "source-details"})
                summary = body_soup.new_tag("summary")
                summary.string = f"参考資料 {len(lis) - important_count} 件を表示"
                details.append(summary)

                ref_ol = body_soup.new_tag("ol", **{"class": "source-reference", "start": str(important_count + 1)})
                # 残りのliをref_olに
                remaining = ol.find_all("li", recursive=False)
                for li in remaining:
                    ref_ol.append(li.extract())
                details.append(ref_ol)

                ol.insert_before(heading_ref)
                ol.insert_before(details)
                ol.decompose()

    # ===== 改良点 3 続き: CTAを最終章の中に取り込む =====
    if cta:
        # 文末ボタン置換 + 章タイトル化
        new_cta_section = body_soup.new_tag("section", id="contact")
        new_h2 = body_soup.new_tag("h2")
        new_h2.string = "8. お問い合わせ・関連リンク"
        new_cta_section.append(new_h2)

        intro_p = body_soup.new_tag("p")
        intro_p.string = (
            "この指針に関するお問い合わせ、各自治体での運用相談、本文の引用許諾等は、"
            "PTA適正化推進委員会までご連絡ください。"
        )
        new_cta_section.append(intro_p)

        contact_p = body_soup.new_tag("p", style="margin-top:1rem")
        contact_p.append(BeautifulSoup(
            'メール: <a href="mailto:info@ptaorg.com">info@ptaorg.com</a><br>'
            '電話: 070-9012-7772<br>'
            '所在地: 〒235-0021 神奈川県横浜市磯子区岡村',
            "html.parser"
        ))
        new_cta_section.append(contact_p)

        # 関連ページの導線
        related_h3 = body_soup.new_tag("h3", style="margin-top:1.8rem")
        related_h3.string = "本サイト内の関連ページ"
        new_cta_section.append(related_h3)

        related_ul = body_soup.new_tag("ul")
        for url, label, desc in [
            ("audit.html", "監査アプリ・立場別しおり", "学校管理職・教育委員会向けのセルフチェックと確認点リスト"),
            ("responses.html", "教育委員会回答DB", "全国76自治体・111回答本文を比較できるデータベース"),
            ("evidence.html", "資料の強み", "回答・開示資料・実物文書・法制度の5層構造"),
            ("journal/index.html", "論考・研究アーカイブ", "個別論考の全文(校務分掌・職務専念義務・代理徴収など)"),
        ]:
            li = body_soup.new_tag("li")
            a = body_soup.new_tag("a", href=url)
            a.string = label
            li.append(a)
            li.append(f" — {desc}")
            related_ul.append(li)
        new_cta_section.append(related_ul)

        # CTAボタン群(中身置換)
        new_cta = body_soup.new_tag("div", **{"class": "cta-wrapper"})
        back_btn = body_soup.new_tag("a", href="index.html", **{"class": "btn-back"})
        back_btn.string = "← トップに戻る"
        forward_btn = body_soup.new_tag("a", href="audit.html", **{"class": "btn-orange"})
        forward_btn.string = "監査アプリで点検する →"
        new_cta.append(back_btn)
        new_cta.append(" ")
        new_cta.append(forward_btn)
        new_cta_section.append(new_cta)

        # 既存CTAを新セクションで置換
        cta.replace_with(new_cta_section)

        # サイドバーにも 8章を追加
        if aside:
            nav_menu = aside.find("ul", class_="nav-menu")
            if nav_menu:
                new_li = ed_soup.new_tag("li")
                new_a = ed_soup.new_tag("a", href="#contact", **{"class": "nav-link"})
                new_a.string = "8. お問い合わせ"
                new_li.append(new_a)
                nav_menu.append(new_li)

    # 4. asideの中身を取得 (左サイドバー)
    aside_html = aside.decode_contents() if aside else ""

    # 5. ed専用CSSをファイル化
    style_tag = ed_soup.find("style")
    css_text = style_tag.string if style_tag else ""

    additional_css = """

/* === ハイブリッド統合追加: ed.htmlの体裁調整 === */

/* strength版の上部ナビとの干渉を避ける */
body.ed-page { display: block; }
body.ed-page > aside.ed-sidebar {
  position: fixed; left: 0; top: 60px; width: 280px; height: calc(100vh - 60px);
  background: var(--nav-bg); border-right: 1px solid var(--border-color);
  padding: 2rem 1.25rem; overflow-y: auto;
  box-shadow: 2px 0 16px rgba(15, 23, 42, 0.04); z-index: 10;
}
body.ed-page .main-wrapper {
  margin-left: 280px; padding: 2.5rem; max-width: none;
}
@media (max-width: 980px) {
  body.ed-page > aside.ed-sidebar {
    position: static; width: 100%; height: auto;
    border-right: 0; border-bottom: 1px solid var(--border-color);
    box-shadow: none;
  }
  body.ed-page .main-wrapper { margin-left: 0; padding: 1.25rem; }
}

/* カード装飾の解放: 枠線・影を控えめに、開放的に */
body.ed-page .card {
  background: transparent;
  border: 0;
  box-shadow: none;
  padding: 0;
  margin: 1.2rem 0 1.8rem;
  border-left: 3px solid var(--border-color);
  padding-left: 1.2rem;
}
body.ed-page .card h3, body.ed-page .card h4 {
  color: var(--main-color);
}

/* リスクボックスは色分け機能として維持(影だけ控えめに) */
body.ed-page .risk-box,
body.ed-page .warn-box,
body.ed-page .ok-box,
body.ed-page .info-box {
  box-shadow: none;
}

/* === 改良点 5: Q&A検索 === */
body.ed-page .faq-search-wrap {
  margin: 1.4rem 0 2rem;
}
body.ed-page .faq-search {
  width: 100%;
  padding: 12px 16px;
  border: 1.5px solid var(--border-color);
  border-radius: 999px;
  font: inherit;
  font-size: 1rem;
  outline: none;
  transition: .2s;
}
body.ed-page .faq-search:focus {
  border-color: var(--main-color);
  box-shadow: 0 0 0 3px rgba(23, 52, 92, .1);
}
body.ed-page .faq-search-note {
  margin: .5rem 0 0;
  color: var(--muted-color);
  font-size: .85rem;
}
body.ed-page .faq-item.is-hidden { display: none; }
body.ed-page .faq-empty {
  padding: 1.2rem; background: #f8fafc; border-radius: 12px;
  color: var(--muted-color); text-align: center;
}

/* === 改良点 4: 一次資料の二段化 === */
body.ed-page .source-heading {
  margin: 2rem 0 .8rem;
  color: var(--main-color);
  font-size: 1.1rem;
  font-weight: 800;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: .5rem;
}
body.ed-page .source-important {
  background: var(--info-bg);
  border: 1px solid var(--info-border);
  border-radius: 12px;
  padding: 1rem 1rem 1rem 2.5rem;
  margin: 0;
}
body.ed-page .source-details {
  margin: 0;
}
body.ed-page .source-details summary {
  cursor: pointer;
  padding: 12px 16px;
  background: #fff;
  border: 1px dashed var(--border-color);
  border-radius: 12px;
  font-weight: 700;
  color: var(--main-color);
  list-style: none;
}
body.ed-page .source-details summary::after {
  content: " ▼"; float: right; color: var(--muted-color);
}
body.ed-page .source-details[open] summary::after { content: " ▲"; }
body.ed-page .source-reference {
  background: #fafbff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem 1rem 1rem 2.5rem;
  margin-top: .5rem;
}

/* === 改良点 3: 末尾CTAの整理 === */
body.ed-page .cta-wrapper {
  display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;
  margin: 2.5rem 0 1rem;
}
body.ed-page .btn-back {
  display: inline-block;
  padding: 14px 28px;
  background: #fff;
  color: var(--main-color);
  border: 2px solid var(--main-color);
  border-radius: 999px;
  text-decoration: none;
  font-weight: 700;
  transition: .2s;
}
body.ed-page .btn-back:hover {
  background: var(--main-color);
  color: #fff;
}

/* 印刷時はサイドバー・ナビ・フッターを隠してフラット化 */
@media print {
  body.ed-page > aside.ed-sidebar,
  body.ed-page .topbar,
  body.ed-page .footer { display: none !important; }
  body.ed-page .main-wrapper { margin-left: 0; padding: 0; }
  body.ed-page .source-details { /* 印刷時は強制展開 */ }
  body.ed-page .source-details > summary { display: none; }
}
"""

    full_css = css_text + additional_css
    css_dir = dst_dir / "css"
    css_dir.mkdir(exist_ok=True)
    (css_dir / "ed.css").write_text(full_css, encoding="utf-8")

    # 6. JSをファイル化(既存のスクロール連動 + Q&A検索)
    js_dir = dst_dir / "js"
    js_dir.mkdir(exist_ok=True)
    js_text = inner_script.string if inner_script else ""

    # === 改良点 5: Q&A検索のJS追加 ===
    faq_search_js = """

// Q&A検索
(function(){
  const input = document.getElementById('faqSearch');
  if (!input) return;
  const items = document.querySelectorAll('.faq-item');
  const note = document.querySelector('.faq-search-note');
  const total = items.length;
  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    let visible = 0;
    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      const match = !q || text.includes(q);
      item.classList.toggle('is-hidden', !match);
      if (match) visible++;
    });
    if (note) {
      note.textContent = q
        ? `「${input.value}」の検索結果: ${visible} 問 / 全 ${total} 問`
        : `全 ${total} 問。キーワードで絞り込めます。`;
    }
  });
})();
"""
    (js_dir / "ed.js").write_text(js_text + faq_search_js, encoding="utf-8")

    # 7. ed.html を組み立て
    title = "教育委員会向け PTA運営適正化指針"
    description = "公立学校におけるPTA運営について、公私分離、地方公務員法第35条、働き方改革、個人情報、会費徴収、加入意思確認を整理する教育委員会向け実務指針。"

    body_final = str(body_soup)

    # strength版の共通ヘッダー・フッター
    nav_html = ""
    for url, label in [
        ("index.html", "全体"),
        ("map.html", "調査地図"),
        ("responses.html", "回答DB"),
        ("evidence.html", "資料の強み"),
        ("audit.html", "監査・しおり"),
        ("journal/index.html", "論考"),
        ("ed.html", "教委向け指針"),
    ]:
        attrs = ' aria-current="page"' if url == "ed.html" else ""
        nav_html += f'<a href="{url}"{attrs}>{label}</a>'

    header = f'''<header class="topbar"><div class="nav">
<a class="brand" href="index.html"><span class="brand-mark">PTA</span><span>PTA適正化推進委員会</span></a>
<button class="nav-toggle" aria-label="メニュー" aria-expanded="false">☰</button>
<nav class="links" aria-label="主要ナビゲーション">{nav_html}</nav>
</div></header>'''

    footer = f'''<footer class="footer"><div class="wrap footer-grid">
<div><strong>PTA適正化推進委員会</strong>
<p>教育委員会回答・公文書開示資料・実物文書・法制度整理を接続して、PTA運営の適正化を検証する研究サイトです。</p>
<p class="small" style="color:#9ca3af;margin-top:8px">〒235-0021 神奈川県横浜市磯子区岡村<br>
<a href="mailto:info@ptaorg.com" style="color:#cbd5e1">info@ptaorg.com</a></p>
</div>
<div>
<a href="map.html">調査地図</a>
<a href="responses.html">回答DB</a>
<a href="audit.html">監査アプリ</a>
<a href="journal/index.html">論考アーカイブ</a>
<a href="ed.html">教委向け指針</a>
<a href="donate.html">ご支援</a>
<a href="sitemap.html">サイトマップ</a>
</div>
</div></footer>'''

    html = f'''<!doctype html>
<html lang="ja"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}｜PTA適正化推進委員会</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{BASE_URL}ed.html">
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(title)}｜PTA適正化推進委員会">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{BASE_URL}ed.html">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/style.css">
<link rel="stylesheet" href="css/ed.css">
</head>
<body class="ed-page">
{header}
<aside class="ed-sidebar">
{aside_html}
</aside>
<div class="main-wrapper">
{body_final}
</div>
{footer}
<script src="js/site.js"></script>
<script src="js/ed.js"></script>
</body></html>
'''

    (dst_dir / "ed.html").write_text(html, encoding="utf-8")
    print(f"ed.html generated: {len(html)} bytes")
    print(f"css/ed.css generated: {len(full_css)} bytes")
    print(f"js/ed.js generated: {len(js_text + faq_search_js)} bytes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="ed-source.html")
    parser.add_argument("--dst", required=True, help="dist-hybridディレクトリ")
    args = parser.parse_args()

    src_path = Path(args.src).resolve()
    dst_dir = Path(args.dst).resolve()

    integrate_ed(src_path, dst_dir)


if __name__ == "__main__":
    main()
