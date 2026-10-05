"""
Builds README.md for the GitHub profile in the LoreCraftian theme.

All copy lives in the data blocks below; badges are encoded here so labels
with dots, dashes, pluses or spaces never break. Banners come from
scripts/generate.py (run that first if you change them). Year counts are
calculated, and .github/workflows/refresh.yml re-runs both scripts every
1 January.

    python scripts/generate.py && python scripts/readme.py
"""

from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
USER = "MrNewaz"
SITE = "https://engineersaif.com"
EMAIL = "info@engineersaif.com"
MAIL = f"mailto:{EMAIL}?subject=From%20GitHub&body=Hi%20Saif%2C%20found%20you%20on%20GitHub."
HIRE_MAIL = f"mailto:{EMAIL}?subject=Hiring%3A%20Senior%20Software%20Engineer"

SINCE = 2019
YEARS = date.today().year - SINCE

NIGHT, GOLD, GOLD_HI, VIOLET = "160F26", "D6AC5C", "F6D68C", "221642"

# --------------------------------------------------------------- content ---

ABOUT_LEAD = "I don't just write code; I build products. Business logic first, then the architecture, then every pixel, with AI making each step faster and safer."
ABOUT = [
    f"I'm a **Senior Software Engineer** who turns business problems into finished products, end to end. {YEARS} years in, I've gone from automating marketing workflows at a jute manufacturer, through SaaS at Ferntech and cross-platform mobile at Supertal, to leading the Next.js migration of a **100k+ user platform at Powerley**.",
    "I'm **not bound to any stack**. I've shipped with React, Next.js and React Native, Node.js, Python and FastAPI, PostgreSQL and MongoDB, and I pick whatever fits the product and the team that has to live with it. What stays constant is how I work: I start with the customer and the business rules, then use **AI across the whole cycle** to scaffold and refactor faster, generate and harden tests, catch security issues early and review every change twice. The time it saves goes into the details that make software trustworthy.",
]

PRINCIPLES = [
    ("Business first", "I learn the customer, the rules and the numbers that matter before I touch the code, so every feature earns its place."),
    ("AI in the loop", "Scaffolding, refactors, tests and reviews move faster with AI beside me, which buys time for edge cases and polish."),
    ("Secure by default", "Auth, validation, secrets and dependencies get checked on every change, with AI as a tireless second pair of eyes."),
    ("End to end", "Schema, API, interface, deployment and the follow-up after launch. One owner from the first brief to the finished product."),
]

SERVICES = [
    ("Product engineering", "From a business problem to a finished product.", ["Discovery with stakeholders and users", "Scope, roadmap and architecture", "Full-stack build, launch and iteration"]),
    ("AI features & agents", "AI that does real work inside your product.", ["LLM features with Claude, OpenAI and Gemini", "RAG over your own data, agents and MCP tools", "Evals, guardrails and cost control"]),
    ("Web platforms", "Fast, accessible web apps that scale.", ["Next.js and React at 100k+ users", "SEO, Core Web Vitals and caching", "Design systems and motion"]),
    ("Mobile & cross-platform", "One product on every screen.", ["React Native and Expo apps", "Flutter when it fits", "Store releases, push and offline"]),
    ("Backend & APIs", "Clean services and data that hold up.", ["Node.js, Python and Go services", "REST, GraphQL, tRPC and realtime", "PostgreSQL, MongoDB and Redis"]),
    ("Modernize & secure", "Make what you have faster and safer.", ["Migrations and legacy rescues", "Performance audits and refactors", "Auth, security reviews and CI/CD"]),
]

PROCESS = [
    ("Understand", "Customers, business rules and the numbers that define success."),
    ("Shape", "Scope, architecture and the right stack for this product and team."),
    ("Build with AI", "Small, reviewed increments. AI drafts and tests beside me; I own every line."),
    ("Secure & verify", "Tests, security checks and AI-assisted review on every change."),
    ("Launch", "CI/CD, monitoring and a calm release, web, mobile or both."),
    ("Measure & iterate", "Real usage, real fixes. The product keeps improving after launch."),
]

WORK = [
    ("Saturdays", "saturdays.webp", "https://saturdays.com/", "Largest eyewear shop in India.", "Next.js · Tailwind · TypeScript"),
    ("Powerley", "powerley.webp", "https://www.dteenergy.com/", "Home energy management system.", "Next.js · Tailwind · TypeScript"),
    ("DTE Insight", "dte-insight.webp", "https://play.google.com/store/apps/details?id=com.dteenergy.insight&hl=en", "Powerley home energy management mobile app.", "React Native · Redux · NativeWind"),
    ("Saturdays Lifestyle", "saturdays-lifestyle.webp", "https://play.google.com/store/apps/details?id=com.saturdays", "E-commerce and eyewear tech mobile app.", "React Native · Redux · NativeBase"),
    ("Prospect Gaze", "prospect-gaze.webp", "https://prospectgaze.com/", "Company portfolio for Prospect Gaze Ltd.", "React · Material UI"),
    ("RGB Jute", "rgb-jute.webp", "https://rgbjute.co/", "Product portfolio with custom design and theming.", "React · Material UI · Airtable"),
]

# (label, simple-icons slug or "" when shields has no icon for it)
STACK = {
    "Daily drivers": [("AI-assisted development", ""), ("TypeScript", "typescript"), ("Next.js", "nextdotjs"), ("React", "react"),
                      ("Node.js", "nodedotjs"), ("Python", "python")],
    "AI & LLM engineering": [("Claude API", "claude"), ("OpenAI API", ""), ("Gemini", "googlegemini"), ("Vercel AI SDK", "vercel"),
                             ("LangChain", "langchain"), ("LangGraph", "langchain"), ("LlamaIndex", ""), ("Model Context Protocol", "modelcontextprotocol"),
                             ("RAG pipelines", ""), ("pgvector", "postgresql"), ("Pinecone", ""), ("Hugging Face", "huggingface"), ("Ollama", "ollama")],
    "AI-powered workflow": [("Claude Code", "claude"), ("Cursor", "cursor"), ("GitHub Copilot", "githubcopilot"), ("AI code review", ""),
                            ("AI test generation", ""), ("Prompt engineering", ""), ("Evals", "")],
    "Web": [("React 19", "react"), ("React Router 7", "reactrouter"), ("Astro", "astro"), ("Vue / Nuxt", "nuxt"), ("SvelteKit", "svelte"),
            ("Vite", "vite"), ("Tailwind CSS", "tailwindcss"), ("shadcn/ui", "shadcnui"), ("TanStack Query", "reactquery"),
            ("Zustand", ""), ("Motion", "framer"), ("Three.js / R3F", "threedotjs")],
    "Mobile & everywhere": [("React Native", "react"), ("Expo", "expo"), ("Flutter", "flutter"), ("PWA", "pwa"), ("Capacitor", "capacitor"),
                            ("Electron", "electron"), ("Tauri", "tauri")],
    "Backend & APIs": [("Bun", "bun"), ("Express", "express"), ("NestJS", "nestjs"), ("Hono", "hono"), ("FastAPI", "fastapi"),
                       ("Django", "django"), ("Go", "go"), ("tRPC", "trpc"), ("GraphQL", "graphql"), ("WebSockets", "socketdotio"),
                       ("Stripe", "stripe")],
    "Data": [("PostgreSQL", "postgresql"), ("MongoDB", "mongodb"), ("Redis", "redis"), ("Prisma", "prisma"), ("Drizzle ORM", "drizzle"),
             ("Supabase", "supabase"), ("Firebase", "firebase"), ("Neon", "neon"), ("Elasticsearch", "elasticsearch")],
    "Cloud & DevOps": [("AWS", ""), ("Google Cloud", "googlecloud"), ("Vercel", "vercel"), ("Cloudflare Workers", "cloudflareworkers"),
                       ("Docker", "docker"), ("Kubernetes", "kubernetes"), ("Terraform", "terraform"), ("GitHub Actions", "githubactions"),
                       ("Nginx", "nginx")],
    "Quality & security": [("Vitest", "vitest"), ("Jest", "jest"), ("Playwright", ""), ("Testing Library", "testinglibrary"), ("Zod", "zod"),
                           ("OAuth / JWT", "jsonwebtokens"), ("Auth.js", ""), ("OWASP practices", "owasp"), ("Sentry", "sentry"), ("ESLint", "eslint")],
    "Languages": [("TypeScript", "typescript"), ("JavaScript", "javascript"), ("Python", "python"), ("Go", "go"), ("Dart", "dart"),
                  ("SQL", "postgresql"), ("Solidity", "solidity"), ("Java", "openjdk"), ("C / C++", "cplusplus")],
    "Design & motion": [("Figma", "figma"), ("After Effects", ""), ("Premiere Pro", ""), ("Photoshop", ""), ("Illustrator", "")],
}

HIRE_PROOF = [
    ("30%", "faster platform", "Powerley"),
    ("20%", "SEO uplift", "Powerley"),
    ("35%", "fewer network calls", "Supertal"),
    ("100+", "restaurants onboarded", "Raaga, Ferntech"),
    ("25%", "lift in online sales", "RGB Jute"),
]
HIRE_WAYS = [
    ("Full-time", "Senior or lead engineer on your team. Remote-first, owning features and products from brief to launch."),
    ("Contract", "Embedded with your team for a sprint or a season: a migration, an AI feature, a performance push."),
    ("Project", "A clear scope delivered end to end: discovery, architecture, build, launch and support after it."),
]

# ---------------------------------------------------------------- helpers ---


def shield_text(s: str) -> str:
    # shields.io path escaping: - becomes --, _ becomes __, then URL-encode
    return quote(s.replace("-", "--").replace("_", "__"), safe="")


def badge(label: str, logo: str, gold: bool = False) -> str:
    bg = GOLD if gold else NIGHT
    logo_col = NIGHT if gold else GOLD_HI
    logo_q = f"&logo={logo}&logoColor={logo_col}" if logo else ""
    url = f"https://img.shields.io/badge/{shield_text(label)}-{bg}?style=for-the-badge{logo_q}"
    return f'<img src="{url}" alt="{label}" />'


def link_badge(href: str, label: str, message: str, logo: str) -> str:
    url = (f"https://img.shields.io/badge/{shield_text(label)}-{shield_text(message)}-{GOLD}"
           f"?style=for-the-badge&logo={logo}&logoColor={GOLD_HI}&labelColor={VIOLET}")
    return f'<a href="{href}"><img src="{url}" alt="{label}: {message}" /></a>'


def themed(name: str, alt: str, width: str = "100%") -> str:
    return (
        "<picture>"
        f'<source media="(prefers-color-scheme: dark)" srcset="img/lorecraft/{name}-dark.svg">'
        f'<source media="(prefers-color-scheme: light)" srcset="img/lorecraft/{name}-light.svg">'
        f'<img src="img/lorecraft/{name}-dark.svg" alt="{alt}" width="{width}">'
        "</picture>"
    )


def themed_remote(dark_url: str, light_url: str, alt: str, width: str) -> str:
    return (
        "<picture>"
        f'<source media="(prefers-color-scheme: dark)" srcset="{dark_url}">'
        f'<source media="(prefers-color-scheme: light)" srcset="{light_url}">'
        f'<img src="{dark_url}" alt="{alt}" width="{width}">'
        "</picture>"
    )


def table(cells: list[str], cols: int) -> str:
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    width = f"{100 // cols}%"
    out = ['<table align="center">']
    for row in rows:
        out.append("<tr>")
        out.extend(f'<td width="{width}" valign="top">{c}</td>' for c in row)
        out.append("</tr>")
    out.append("</table>")
    return "\n".join(out)


# ------------------------------------------------------------------ build ---


def build() -> str:
    out: list[str] = []
    w = out.append

    w("<!-- Generated by scripts/readme.py. Edit the data there, then run: python scripts/generate.py && python scripts/readme.py -->")
    w('<div align="center">\n')
    w(f'<a href="{SITE}">{themed("hero", "Saif Rahman, AI-augmented Senior Software Engineer: I architect intelligent web ecosystems")}</a>\n')
    w("<br/>\n")
    w(" ".join([
        link_badge(HIRE_MAIL, "Status", "Available for hire", "rocket"),
        link_badge(SITE, "Portfolio", "engineersaif.com", "googlechrome"),
        link_badge("https://www.linkedin.com/in/srman/", "LinkedIn", "Connect", "linkedin"),
    ]))
    w("\n")
    w(" ".join([
        link_badge(MAIL, "Mail", "Send a brief", "gmail"),
        link_badge("https://facebook.com/saif.newaz", "Facebook", "saif.newaz", "facebook"),
        link_badge("https://instagram.com/saif.newaz", "Instagram", "saif.newaz", "instagram"),
        f'<a href="https://github.com/{USER}?tab=repositories&sort=stargazers"><img alt="Total stars" '
        f'src="https://custom-icon-badges.demolab.com/github/stars/{USER}?style=for-the-badge&logo=star&logoColor={GOLD_HI}&color={GOLD}&labelColor={VIOLET}"/></a>',
        f'<img alt="Profile views" src="https://komarev.com/ghpvc/?username={USER.lower()}&label=Profile%20views&color={GOLD.lower()}&style=for-the-badge" />',
    ]))
    w("\n</div>\n")

    w('\n<h3 align="center"><i>An AI-augmented, stack-agnostic senior engineer who turns business problems into finished products.</i></h3>\n')

    # Notice
    w(f'\n{themed("h-notice", "00 · Notice: a note on private work")}\n')
    w('<p align="center">\n'
      "For client confidentiality and security, most of my featured work lives in <b>private repositories</b>.<br/>\n"
      f'Live demos are on my <a href="{SITE}">portfolio</a>. For anything else, <a href="{MAIL}">send me an email</a>.\n'
      "</p>\n")

    # About
    w(f'\n{themed("h-about", "01 · About: business problems into finished products")}\n')
    w(f"\n> ### *{ABOUT_LEAD}*\n")
    for p in ABOUT:
        w(f"\n{p}\n")
    w('\n<p align="right"><i>— Saif</i></p>\n')
    w('\n<h3 align="center">✦ How I work ✦</h3>\n')
    w(table([f"<b>{t}</b><br/><sub>{b}</sub>" for t, b in PRINCIPLES], 4))
    w(f'\n\n{themed("stats", f"{YEARS}+ years, 30+ projects, 100k+ users at peak, 30% average performance uplift")}\n')

    # Services
    w(f'\n{themed("h-services", "02 · Services: what I build, end to end")}\n')
    cells = []
    for title, lead, points in SERVICES:
        pts = "<br/>".join(f"✦ {p}" for p in points)
        cells.append(f"<h4>{title}</h4><i>{lead}</i><br/><br/><sub>{pts}</sub>")
    w(table(cells, 3))

    # Work
    w(f'\n\n{themed("h-work", "03 · Selected work: things I am proud of")}\n')
    cells = []
    for title, img, href, desc, stack in WORK:
        cells.append(
            f'<a href="{href}"><img src="img/work/{img}" alt="{title}" width="100%"/></a>'
            f'<h4 align="center"><a href="{href}">{title}</a></h4>'
            f'<p align="center"><sub>{desc}</sub><br/><sub><b>{stack}</b></sub></p>'
        )
    w(table(cells, 3))
    w(f'\n<p align="center">{link_badge(SITE, "The full archive", "22 projects", "googlechrome")}</p>\n')

    # Process
    w(f'\n{themed("h-process", "04 · Process: from problem to product")}\n')
    w(table([f"<b>0{i + 1} · {s}</b><br/><sub>{b}</sub>" for i, (s, b) in enumerate(PROCESS)], 3))

    # Stack
    w(f'\n\n{themed("h-stack", "05 · Stack: not bound to any stack, fluent in the right one")}\n')
    w('\n<p align="center"><i>I choose tools for the product and the team that has to live with the code, not out of habit.<br/>'
      "AI sits in every step: drafting, testing, reviewing and securing.</i></p>\n")
    for i, (group, items) in enumerate(STACK.items()):
        w(f'\n<p align="center"><sub><b>✦ {group.upper()} ✦</b></sub><br/>\n')
        w("\n".join(badge(label, logo, gold=(i == 0)) for label, logo in items))
        w("\n</p>\n")

    # Experience
    w(f'\n{themed("h-experience", f"06 · Experience: {YEARS} years, four kinds of teams")}\n')
    w(f'\n{themed("timeline", "Powerley 2023 to now, Senior Software Engineer. Supertal 2021 to 2023, Software Engineer. Ferntech Solutions 2020 to 2021, Software Engineer. RGB Jute 2019, Web Developer.")}\n')

    # Signals
    w(f'\n{themed("h-stats", "07 · Signals: the archive, by the numbers")}\n')
    # Our own card, drawn from scripts/signals.json (refreshed weekly by the Action).
    w(f'\n<a href="https://github.com/{USER}?tab=repositories">{themed("signals", "GitHub signals: stars, contributions, streaks and languages")}</a>\n')

    # Hire
    w(f'\n{themed("h-hire", "08 · Hire: hire an engineer who finishes")}\n')
    w(f'\n<p align="center"><b>{YEARS}+ years, 30+ shipped products and platforms serving 100k+ users.</b><br/>'
      "You get one senior owner who understands the business, builds with AI to move faster,<br/>"
      "and hands over code your team can keep building on.</p>\n")
    w(table([f'<h3 align="center">{v}</h3><p align="center">{l}<br/><sub>{where}</sub></p>' for v, l, where in HIRE_PROOF], 5))
    w("\n")
    w(table([f"<b>{t}</b><br/><sub>{b}</sub>" for t, b in HIRE_WAYS], 3))
    w(f'\n<p align="center">{link_badge(HIRE_MAIL, "Hire me", "Book a call", "googlecalendar")} '
      f'{link_badge(SITE + "/#contact", "Start a project", "Send a brief", "googlechrome")}</p>\n')

    # Contact / sign-off
    w(f'\n<a href="{MAIL}">{themed("footer", "09 · Contact: architecting intelligent web ecosystems. info@engineersaif.com")}</a>\n')
    w(f'\n{themed("divider", "")}\n')
    w(f'\n{themed("closing", "Since you came this far, this one is for you. Thank you for reading.")}\n')
    return "\n".join(out)


if __name__ == "__main__":
    (ROOT / "README.md").write_text(build(), encoding="utf-8")
    print("README.md written")
