import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

GITHUB_USERNAME = "SadhanaSai"
MEDIUM_FEED = "https://medium.com/feed/@sadhanasainarayanan"
STATUS_FILE = "status.json"
OUTPUT_FILE = "README.md"

TALKS = [
    {
        "event": "DEF CON 34 Cloud Village",
        "topic": "Trust Fall: How Agentic AI Inherits Your Cloud's Worst IAM Habits",
        "year": "2026"
    },
    {
        "event": "AISF Vegas",
        "topic": "How AI Agents Weaponize Compliance through Specification Gaming",
        "year": "2026"
    },
]
 
SKILLS = {
    "languages":  "Python · Bash · R · JavaScript",
    "cloud":      "AWS · Azure · GCP · Kubernetes · Docker · nginx",
    "ai / ml":    "LangGraph · MCP · PyTorch · scikit-learn · MLflow · FastAPI",
    "security":   "WAF · GuardDuty · OpenTelemetry · Splunk · Dynatrace",
}

TEMPLATE = """\
<!-- auto-generated — do not edit directly. edit generate_readme.py or status.json -->

Hi, I'm Sadhana.

I'm a Cloud Platform Engineer with 4+ years of experience across interconnected fields \
such as Cloud Platform Engineering (Security), AI Systems, MLOps, Data Science.

I like building things and understanding how they work. Lately that means AI systems, \
what they do when no one's checking, and whether we can trust what they tell us.

Interested in AI security, auditing models, mechanistic interpretability, \
behavioral versioning, and evaluation awareness. \
Just things I find worth digging into.

---

### What's Active

{status_block}

---
 
### Conference Speaking
 
{talks_block}
 
---
 
### skills
 
{skills_block}
 
---

### Repos

{repos_block}

---

### Writing

{posts_block}

---

### Elsewhere

[LinkedIn](https://linkedin.com/in/sadhanasainarayanan) · [Medium](https://medium.com/@sadhanasainarayanan)

</sub>

<sub>last updated {timestamp}</sub>
"""


def fetch_repos():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    params = {
        "sort": "pushed",
        "direction": "desc",
        "per_page": 10,
        "type": "owner"
    }
    headers = {"Accept": "application/vnd.github+json"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        repos = resp.json()
    except Exception as e:
        print(f"GitHub API error: {e}")
        return []

    results = []
    for r in repos:
        if r.get("fork") or r.get("private") or r.get("name") == GITHUB_USERNAME:
            continue
        pushed = r.get("pushed_at", "")
        pushed_fmt = pushed[:10] if pushed else "—"
        results.append({
            "name": r["name"],
            "description": r.get("description") or "—",
            "language": r.get("language") or "—",
            "stars": r.get("stargazers_count", 0),
            "pushed": pushed_fmt,
            "url": r["html_url"]
        })

    return results[:6]


def fetch_posts():
    try:
        resp = requests.get(MEDIUM_FEED, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception as e:
        print(f"Medium RSS error: {e}")
        return []

    ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    channel = root.find("channel")
    if channel is None:
        return []

    posts = []
    for item in channel.findall("item")[:3]:
        title = item.findtext("title", "—").strip()
        link = item.findtext("link", "#").strip()
        pub = item.findtext("pubDate", "")
        try:
            date = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d")
        except Exception:
            date = "—"
        posts.append({"title": title, "link": link, "date": date})

    return posts


def load_status():
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"status.json error: {e}")
        return {}


def render_status(status):
    if not status:
        return "_nothing filed yet_"
    lines = []
    labels = {
        "building": "building",
        "exploring": "exploring",
        "next": "next"
    }
    for key, label in labels.items():
        val = status.get(key)
        if val:
            lines.append(f"**{label}** — {val}")
    return "\n\n".join(lines)


def render_repos(repos):
    if not repos:
        return "_no public repos found_"

    header = "| repo | description | lang | last push |"
    divider = "|---|---|---|---|"
    rows = []
    for r in repos:
        name = f"[{r['name']}]({r['url']})"
        desc = r["description"][:60] + "…" if len(r["description"]) > 60 else r["description"]
        rows.append(f"| {name} | {desc} | {r['language']} | {r['pushed']} |")

    return "\n".join([header, divider] + rows)

def render_talks():
    lines = []
    for t in TALKS:
        lines.append(f"- **{t['event']}** ({t['year']}) — {t['topic']}")
    return "\n".join(lines)
 
 
def render_skills():
    lines = []
    for label, tools in SKILLS.items():
        lines.append(f"`{label}`&nbsp;&nbsp;{tools}")
    return "\n\n".join(lines)


def render_posts(posts):
    if not posts:
        return "_nothing published yet_"
    lines = []
    for p in posts:
        lines.append(f"- [{p['title']}]({p['link']}) <sub>{p['date']}</sub>")
    return "\n".join(lines)


def main():
    print("fetching repos...")
    repos = fetch_repos()

    print("fetching posts...")
    posts = fetch_posts()

    print("loading status...")
    status = load_status()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    readme = TEMPLATE.format(
        talks_block=render_talks(),
        skills_block=render_skills(),
        status_block=render_status(status),
        repos_block=render_repos(repos),
        posts_block=render_posts(posts),
        timestamp=timestamp
    )

    with open(OUTPUT_FILE, "w") as f:
        f.write(readme)

    print(f"wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
