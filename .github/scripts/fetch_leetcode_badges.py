import requests
import re
import os

LEETCODE_USERNAME = "INSIGHT_CODER"

GRAPHQL_URL = "https://leetcode.com/graphql"

QUERY = """
query getUserBadges($username: String!) {
  matchedUser(username: $username) {
    badges {
      id
      name
      shortName
      displayName
      icon
      hoverText
      medal {
        slug
        config {
          iconGif
          iconGifBackground
        }
      }
      creationDate
      category
    }
    upcomingBadges {
      name
      icon
      progress
    }
  }
}
"""

def fetch_badges(username):
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/{username}/",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "query": QUERY,
        "variables": {"username": username}
    }
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data.get("data", {}).get("matchedUser", {})

def build_badge_table(badges):
    if not badges:
        return "_No badges earned yet — keep grinding! 💪_\n"

    # Sort by creationDate descending (newest first)
    sorted_badges = sorted(badges, key=lambda b: b.get("creationDate", ""), reverse=True)

    rows = []
    cells = []

    for i, badge in enumerate(sorted_badges):
        name = badge.get("displayName") or badge.get("name", "Badge")
        icon = badge.get("icon", "")
        date = badge.get("creationDate", "")

        # Build icon URL
        if icon.startswith("http"):
            icon_url = icon
        else:
            icon_url = f"https://leetcode.com{icon}"

        cell = (
            f'<td align="center" width="110">\n'
            f'  <img src="{icon_url}" width="60" height="60" alt="{name}"/>\n'
            f'  <br/>\n'
            f'  <sub><b>{name}</b></sub>\n'
            f'  <br/>\n'
            f'  <sub>{date}</sub>\n'
            f'</td>'
        )
        cells.append(cell)

        # 5 badges per row
        if (i + 1) % 5 == 0:
            rows.append("<tr>\n" + "\n".join(cells) + "\n</tr>")
            cells = []

    if cells:
        rows.append("<tr>\n" + "\n".join(cells) + "\n</tr>")

    table = (
        '<table align="center">\n'
        + "\n".join(rows)
        + "\n</table>"
    )
    return table

def build_upcoming_section(upcoming):
    if not upcoming:
        return ""

    lines = ["### 🔜 Upcoming Badges\n"]
    for badge in upcoming:
        name = badge.get("name", "")
        progress = badge.get("progress", 0)
        icon = badge.get("icon", "")
        if icon and not icon.startswith("http"):
            icon = f"https://leetcode.com{icon}"

        bar_filled = int(progress / 10)
        bar_empty = 10 - bar_filled
        bar = "█" * bar_filled + "░" * bar_empty

        if icon:
            lines.append(f'<img src="{icon}" width="24" height="24"/> **{name}** — `{bar}` {progress}%  ')
        else:
            lines.append(f'**{name}** — `{bar}` {progress}%  ')

    return "\n".join(lines) + "\n"

def update_readme(badge_table, upcoming_section, badge_count):
    readme_path = "README.md"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    badge_section = (
        "<!-- LEETCODE-BADGES:START -->\n"
        f"<div align=\"center\">\n\n"
        f"**🏅 Total Badges Earned: {badge_count}**\n\n"
        f"{badge_table}\n\n"
        f"{upcoming_section}"
        f"</div>\n"
        "<!-- LEETCODE-BADGES:END -->"
    )

    # Replace between markers
    pattern = r"<!-- LEETCODE-BADGES:START -->.*?<!-- LEETCODE-BADGES:END -->"
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, badge_section, content, flags=re.DOTALL)
    else:
        print("⚠️  Markers not found in README. Appending section.")
        new_content = content + "\n\n" + badge_section

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ README updated with {badge_count} badges!")

def main():
    print(f"🔍 Fetching badges for {LEETCODE_USERNAME}...")
    user_data = fetch_badges(LEETCODE_USERNAME)

    badges = user_data.get("badges", [])
    upcoming = user_data.get("upcomingBadges", [])

    print(f"🏅 Found {len(badges)} badge(s)")
    print(f"🔜 Found {len(upcoming)} upcoming badge(s)")

    badge_table = build_badge_table(badges)
    upcoming_section = build_upcoming_section(upcoming)

    update_readme(badge_table, upcoming_section, len(badges))

if __name__ == "__main__":
    main()
