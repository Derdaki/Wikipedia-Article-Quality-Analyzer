import requests
import re

# ---------------- CONFIG ---------------- #

BIASED_WORDS = [
    "best", "greatest", "most famous", "amazing", "unique",
    "الأفضل", "الأعظم", "الأشهر", "الرائع",
    "le meilleur", "le plus célèbre", "incroyable"
]

DEFAULT_LANGUAGE = "en"

HEADERS = {
    "User-Agent": "WikiQualityAnalyzer/1.0 (personal project)"
}

# ---------------------------------------- #

def fetch_article_text(title, lang):
    api_url = f"https://{lang}.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "prop": "revisions",
        "rvslots": "main",
        "rvprop": "content",
        "format": "json",
        "formatversion": "2",
        "titles": title
    }

    response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)

    if response.status_code != 200:
        print("❌ HTTP Error:", response.status_code)
        return None

    try:
        data = response.json()
    except ValueError:
        print("❌ Failed to parse JSON response")
        return None

    pages = data.get("query", {}).get("pages", [])

    if not pages or "missing" in pages[0]:
        return None

    return pages[0]["revisions"][0]["slots"]["main"]["content"]


def analyze_article(title, lang=DEFAULT_LANGUAGE):
    text = fetch_article_text(title, lang)

    if not text:
        print("❌ Article not found or could not be retrieved.")
        return

    score = 0
    strengths = []
    weaknesses = []

    # 1️⃣ Article length
    word_count = len(text.split())
    if word_count >= 3000:
        score += 20
        strengths.append("Sufficient article length")
    else:
        weaknesses.append("Article is relatively short")

    # 2️⃣ Structure
    section_count = text.count("==")
    if section_count >= 10:
        score += 20
        strengths.append("Well-structured with multiple sections")
    else:
        weaknesses.append("Insufficient number of sections")

    # 3️⃣ References
    references = text.count("<ref")
    if references >= 20:
        score += 25
        strengths.append("Well-referenced with reliable sources")
    else:
        weaknesses.append("Not enough references")

    # 4️⃣ Media
    if any(tag in text for tag in ["[[File:", "[[Image:", "[[ملف:"]):
        score += 10
        strengths.append("Includes illustrative media")
    else:
        weaknesses.append("No images or media found")

    # 5️⃣ Neutrality
    biased_found = [w for w in BIASED_WORDS if w.lower() in text.lower()]
    if not biased_found:
        score += 15
        strengths.append("Neutral and encyclopedic tone")
    else:
        weaknesses.append(
            "Potential promotional language: " + ", ".join(biased_found)
        )

    # ---------------- OUTPUT ---------------- #

    print("=" * 60)
    print(f"📄 Article Title : {title}")
    print(f"🌐 Language      : {lang}")
    print(f"📊 Final Score   : {score} / 100")

    if score >= 80:
        print("⭐ Recommendation: Strong candidate for Featured Article")
    elif score >= 60:
        print("🟡 Recommendation: Good article, needs improvements")
    else:
        print("🔴 Recommendation: Not ready for Featured status")

    print("\n✅ Strengths:")
    for s in strengths:
        print(f"  • {s}")

    print("\n❌ Weaknesses:")
    for w in weaknesses:
        print(f"  • {w}")

    print("=" * 60)


# ---------------- CLI ---------------- #

if __name__ == "__main__":
    print("Wikipedia Article Quality Analyzer")
    print("----------------------------------")

    article_title = input("Enter article title: ").strip()
    language = input("Enter Wikipedia language code (en, ar, fr): ").strip()

    if not language:
        language = DEFAULT_LANGUAGE

    analyze_article(article_title, language)