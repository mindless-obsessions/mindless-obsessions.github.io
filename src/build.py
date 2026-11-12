#!/usr/bin/env python3
"""Build the Mindless Obsessions static site from data/*.yaml into the repo root (GitHub Pages serves main:/).

Truthfulness rules (enforced by data, not code): only verified game facts; no invented screenshots, dates,
reviews, testimonials, addresses or compliance claims. Add a game by adding an entry to data/games.yaml.
Run:  python3 src/build.py
"""
import datetime as dt
import html
import json
import pathlib
import shutil

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = yaml.safe_load(open(ROOT / "data/site.yaml"))
GAMES = yaml.safe_load(open(ROOT / "data/games.yaml"))["games"]
D = SITE["domain"].rstrip("/")
E = html.escape
STATUS = {"in-development": "In development", "testing": "Testing", "released": "Out now on Roblox"}

CSS = """
:root{--bg:#0d0b24;--bg2:#171236;--card:#1d1745;--line:#332a73;--ink:#f4f2ff;--mute:#c4bfe6;--pink:#fc72b7;--cyan:#11f9fd;--purple:#7812e6;--focus:#ffd84d}
*{box-sizing:border-box}html{scroll-behavior:smooth}
html{background:#0d0b24}
body{margin:0;min-height:100vh;background-color:#0d0b24;background-image:radial-gradient(1200px 600px at 50% -10%,#3a2380 0%,transparent 60%),linear-gradient(#171236,#0d0b24 900px);background-repeat:no-repeat;color:var(--ink);font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Ubuntu,sans-serif}
a{color:var(--cyan)}a:hover{color:#8ffcff}
:focus-visible{outline:3px solid var(--focus);outline-offset:3px;border-radius:6px}
.skip{position:absolute;left:-999px;top:8px;background:var(--focus);color:#000;padding:8px 14px;border-radius:8px;z-index:10}.skip:focus{left:8px}
header.top{position:sticky;top:0;z-index:5;background:rgba(13,11,36,.88);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.nav{max-width:1120px;margin:0 auto;display:flex;align-items:center;gap:18px;padding:10px 20px;flex-wrap:wrap}
.nav .brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:800;letter-spacing:.3px;margin-right:auto}
.nav .brand img{width:42px;height:42px;border-radius:50%}
.nav a.l{color:var(--mute);text-decoration:none;font-weight:600;padding:6px 2px}.nav a.l:hover,.nav a.l[aria-current]{color:#fff;border-bottom:2px solid var(--pink)}
main{max-width:1120px;margin:0 auto;padding:0 20px 60px}
.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:30px;align-items:center;padding:56px 0 30px}
.hero h1{font-size:clamp(2.1rem,5vw,3.6rem);line-height:1.05;margin:.2em 0}
.hero h1 span{background:linear-gradient(90deg,var(--cyan),var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--mute);font-size:1.15rem;max-width:36rem}
.hero .logo{width:100%;max-width:520px;justify-self:center;filter:drop-shadow(0 12px 40px rgba(120,18,230,.55));animation:float 6s ease-in-out infinite}
@keyframes float{50%{transform:translateY(-10px) rotate(-1deg)}}
.btns{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:12px 20px;border-radius:999px;font-weight:800;text-decoration:none;border:2px solid transparent}
.btn.primary{background:linear-gradient(90deg,var(--purple),#b13cf0);color:#fff}.btn.ghost{border-color:var(--cyan);color:var(--cyan)}
.btn:hover{transform:translateY(-2px);transition:transform .15s}
section{margin:46px 0}h2{font-size:clamp(1.5rem,3vw,2.1rem);margin:.2em 0 .5em}
.lead{color:var(--mute);max-width:46rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:20px;position:relative;overflow:hidden}
.card h3{margin:.1em 0 .3em;font-size:1.25rem}.card p{color:var(--mute);margin:.3em 0}
.card.game{border-top:4px solid var(--accent,var(--cyan));text-decoration:none;color:var(--ink);display:block;transition:transform .15s,border-color .15s}
.card.game:hover{transform:translateY(-4px);border-color:var(--accent)}
.pill{display:inline-block;font-size:.8rem;font-weight:700;padding:3px 10px;border-radius:999px;background:#2a2265;color:#e6e1ff;margin-right:6px}
.pill.dev{background:#3b2a12;color:#ffd38a}.pill.live{background:#123b26;color:#8ff0b8}
.art{aspect-ratio:16/9;border-radius:12px;background:radial-gradient(circle at 50% 40%,color-mix(in srgb,var(--accent) 35%,transparent),transparent 60%),#120e30;display:grid;place-items:center;margin-bottom:12px;border:1px solid var(--line)}
.art img{width:42%;max-width:160px;opacity:.95}.art small{color:var(--mute)}
.social{display:flex;flex-wrap:wrap;gap:10px}.social a{display:inline-flex;gap:8px;align-items:center;padding:10px 16px;border-radius:999px;background:#241c5a;color:#fff;text-decoration:none;font-weight:700}
.social a:hover{background:#30257a}
.discord{background:linear-gradient(120deg,#2b1f6e,#3d1d7a);border:1px solid #5b3fd0;border-radius:22px;padding:26px;display:flex;gap:20px;align-items:center;flex-wrap:wrap}
.discord img{width:96px;height:96px;border-radius:50%}
.mute{color:var(--mute)}.prose{max-width:50rem}.prose h2{margin-top:1.4em}.prose li{margin:.3em 0}
.note{border-left:4px solid var(--pink);background:#1d1745;padding:12px 16px;border-radius:8px;color:var(--mute)}
footer.bottom{border-top:1px solid var(--line);margin-top:40px}
footer .in{max-width:1120px;margin:0 auto;padding:26px 20px;display:flex;flex-wrap:wrap;gap:16px 30px;color:var(--mute);font-size:.95rem}
footer a{color:var(--mute)}footer nav{display:flex;flex-wrap:wrap;gap:6px 16px}
@media (max-width:820px){.hero{grid-template-columns:1fr;text-align:center;padding-top:30px}.hero p{margin:0 auto}.btns{justify-content:center}.hero .logo{max-width:320px;order:-1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""

NAV = [("/", "Home"), ("/games/", "Games"), ("/creators/", "Creator Highlights"), ("/community/", "Community"),
       ("/about/", "About"), ("/contact/", "Contact")]


def page(path, title, desc, body, active=None):
    canonical = f"{D}{path}"
    nav = "".join(f'<a class="l" href="{h}"{" aria-current=page" if h == active else ""}>{E(t)}</a>' for h, t in NAV)
    links = "".join(f'<a href="{E(l["url"])}" rel="me noopener" target="_blank">{E(l["label"])}</a>' for l in SITE["links"])
    full_title = title if title.startswith(SITE["name"]) else f"{title} · {SITE['name']}"
    ld = json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": SITE["name"], "url": D,
                     "logo": f"{D}/assets/mascot-512.png", "sameAs": [l["url"] for l in SITE["links"]]})
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full_title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}"><link rel="icon" href="/assets/favicon-64.png"><link rel="apple-touch-icon" href="/assets/favicon-180.png">
<meta name="theme-color" content="#0d0b24">
<meta property="og:type" content="website"><meta property="og:site_name" content="{E(SITE['name'])}"><meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{D}/assets/og-1200x630.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{D}/assets/og-1200x630.png">
<link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{ld}</script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><nav class="nav" aria-label="Main"><a class="brand" href="/"><img src="/assets/mascot-96.png" alt="" width="42" height="42">Mindless Obsessions</a>{nav}</nav></header>
<main id="main">{body}</main>
<footer class="bottom"><div class="in"><div>© {dt.date.today().year} {E(SITE['name'])}. Roblox is a trademark of Roblox Corporation; we are not affiliated with or endorsed by Roblox.</div>
<nav aria-label="Social">{links}</nav>
<nav aria-label="Legal"><a href="/legal/privacy/">Privacy</a><a href="/legal/terms/">Terms</a><a href="/legal/copyright/">Copyright</a><a href="/legal/data-deletion/">Data deletion</a><a href="/legal/cookies/">Cookies</a></nav></div></footer>
</body></html>"""


def game_card(g):
    st = g["status"]
    return f"""<a class="card game" style="--accent:{g['accent']}" href="/games/{g['slug']}/">
<div class="art"><img src="/assets/mascot-256.png" alt="" loading="lazy"><small>Artwork coming soon</small></div>
<span class="pill {'live' if st == 'released' else 'dev'}">{STATUS[st]}</span><span class="pill">{E(g['genre'])}</span>
<h3>{E(g['name'])}</h3><p>{E(g['summary'])}</p></a>"""


def social_links():
    return '<div class="social">' + "".join(
        f'<a href="{E(l["url"])}" rel="me noopener" target="_blank">{l["icon"]} {E(l["label"])}</a>' for l in SITE["links"]) + "</div>"


def discord_block():
    return f"""<div class="discord"><img src="/assets/mascot-256.png" alt="Mindless Obsessions mascot">
<div><h2 style="margin:0">Join the community on Discord</h2><p class="lead">Chat Roblox, share your clips and fan art, get game updates, and help test what we build.</p>
<a class="btn primary" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join our Discord</a></div></div>"""


def build():
    out = {}
    cards = "".join(game_card(g) for g in GAMES)
    out["index.html"] = page("/", f"{SITE['name']}: Roblox entertainment network & game studio", SITE["description"], f"""
<section class="hero"><div><p class="pill">Roblox entertainment network + indie game studio</p>
<h1>Your daily dose of <span>Roblox insanity</span></h1>
<p>Creator highlights, funny moments and epic clips from across Roblox, plus original games from our own studio. New games. New creators. Endless obsessions.</p>
<div class="btns"><a class="btn primary" href="/games/">Explore our games</a><a class="btn ghost" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join the Discord</a></div></div>
<img class="logo" src="/assets/logo-640.png" alt="Mindless Obsessions logo: a grinning pink brain wearing headphones, holding a game controller" width="640" height="495"></section>
<section aria-labelledby="g"><h2 id="g">Our games</h2><p class="lead">Original Roblox games across genres, with more on the way.</p><div class="grid">{cards}</div></section>
<section aria-labelledby="c"><h2 id="c">Creator highlights</h2><p class="lead">We feature the funniest and most epic moments from Roblox creators and streamers, only with their written permission, always credited and linked.</p>
<a class="btn ghost" href="/creators/">How creator highlights work</a></section>
<section aria-labelledby="f"><h2 id="f">Follow the obsession</h2>{social_links()}</section>
<section>{discord_block()}</section>""", "/")
    out["games/index.html"] = page("/games/", "Our games", "Original Roblox games from the Mindless Obsessions studio.", f"""
<section><h1>Our games</h1><p class="lead">Every game below is an original Mindless Obsessions project. Status reflects where it really is; we will add Roblox links when a game is publicly available.</p>
<div class="grid">{cards}</div></section><section>{discord_block()}</section>""", "/games/")
    for g in GAMES:
        roblox = (f'<a class="btn primary" href="{E(g["roblox_url"])}" rel="noopener" target="_blank">Play on Roblox</a>'
                  if g.get("roblox_url") else '<span class="pill dev">Not yet available to play</span>')
        details = f"<p>{E(g['details'])}</p>" if g.get("details") else ""
        out[f"games/{g['slug']}/index.html"] = page(f"/games/{g['slug']}/", g["name"], g["summary"], f"""
<section class="prose" style="--accent:{g['accent']}"><p><a href="/games/">← All games</a></p>
<div class="art" style="max-width:640px"><img src="/assets/mascot-256.png" alt=""><small>Official artwork and screenshots coming soon</small></div>
<span class="pill dev">{STATUS[g['status']]}</span><span class="pill">{E(g['genre'])}</span>
<h1>{E(g['name'])}</h1><p class="lead">{E(g['summary'])}</p>{details}
<div class="btns">{roblox}</div>
<h2>Updates</h2><p>Development updates are posted first in our <a href="{SITE['discord_invite']}">Discord</a> and on our social channels.</p></section>""", "/games/")
    out["creators/index.html"] = page("/creators/", "Creator highlights", "How Mindless Obsessions features Roblox creators: permission first, always credited.", f"""
<section class="prose"><h1>Creator highlights</h1>
<p class="lead">Mindless Obsessions shares short highlights from Roblox creators and streamers: funny moments, wins, fails, boss fights and wild challenges.</p>
<h2>Permission first</h2><ul>
<li>We only post a creator's footage after they give us <b>written permission</b> for each platform.</li>
<li>Every clip credits the creator on screen and links to their channel.</li>
<li>We never remove watermarks, change the meaning of a clip, or claim ownership of creators' footage.</li>
<li>Creators can ask us to take any clip down at any time, and we remove it promptly.</li></ul>
<h2>Featured creators</h2><p>Our first permitted highlights are coming soon.</p>
<h2>Are you a Roblox creator?</h2><p>Want your best moments featured? Email <a href="mailto:{SITE['contact_email']}?subject=Creator%20highlights">{SITE['contact_email']}</a> with your channel link, or reach us on <a href="{SITE['discord_invite']}">Discord</a>.</p></section>""", "/creators/")
    out["community/index.html"] = page("/community/", "Community", "Join the Mindless Obsessions community on Discord and social media.", f"""
<section>{discord_block()}</section>
<section class="prose"><h2>What's on the server</h2><ul><li>General chat, Roblox chat, clips &amp; memes, fan art and suggestions</li>
<li>A dedicated space for each of our games, with update channels and bug reports</li><li>Optional ping roles for the games you care about</li></ul>
<p>Please read the server rules when you join. Discord requires members to be at least 13.</p>
<h2>Follow us</h2>{social_links()}
<h2>Creator collaborations</h2><p>Roblox creators can reach us about highlights and collaborations: <a href="/contact/">contact us</a>.</p></section>""", "/community/")
    out["about/index.html"] = page("/about/", "About", "About Mindless Obsessions: a Roblox entertainment network and an independent game studio.", f"""
<section class="prose"><h1>About Mindless Obsessions</h1>
<p class="lead">We're two things at once: a Roblox entertainment network and an independent Roblox game studio.</p>
<h2>The network</h2><p>We share the funniest, craziest and most epic Roblox moments across YouTube, TikTok and Instagram, featuring creators and streamers who've given us permission, always with credit.</p>
<h2>The studio</h2><p>We build original Roblox games across genres, from castle defense and sports to tycoons and adventures, and we're not stopping at four. See <a href="/games/">our games</a>.</p>
<h2>Our community</h2><p>Our <a href="{SITE['discord_invite']}">Discord</a> is home base: game updates, testing, clips and fan art.</p></section>""", "/about/")
    out["contact/index.html"] = page("/contact/", "Contact", "Contact Mindless Obsessions for business, creator collaborations and permission requests.", f"""
<section class="prose"><h1>Contact</h1>
<div class="grid"><div class="card"><h3>Business inquiries</h3><p><a href="mailto:{SITE['contact_email']}?subject=Business%20inquiry">{SITE['contact_email']}</a></p></div>
<div class="card"><h3>Creator collaborations</h3><p>Email us with your channel link (subject: Creator highlights) or message us on <a href="{SITE['discord_invite']}">Discord</a>.</p></div>
<div class="card"><h3>Takedowns &amp; permissions</h3><p>Want a clip removed or a permission changed? Email us with the link; we act promptly. See <a href="/legal/copyright/">Copyright</a>.</p></div>
<div class="card"><h3>Privacy &amp; data deletion</h3><p>See <a href="/legal/data-deletion/">how to request deletion</a>.</p></div></div></section>""", "/contact/")
    legal(out)
    out["404.html"] = page("/404.html", "Page not found", "This page does not exist.", f"""
<section class="prose" style="text-align:center;padding:60px 0"><img src="/assets/mascot-256.png" alt="Confused Mindless Obsessions mascot" width="180" height="180">
<h1>404: our brain lost this page</h1><p class="lead">It may have moved. Try the <a href="/">home page</a> or <a href="/games/">our games</a>.</p></section>""")
    # Keep old URLs used by the TikTok developer app working.
    for old, new in (("terms.html", "/legal/terms/"), ("privacy.html", "/legal/privacy/")):
        out[old] = (f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{D}{new}">'
                    f'<meta http-equiv="refresh" content="0; url={new}"><p>Moved to <a href="{new}">{new}</a>.</p>')
    urls = ["/", "/games/", *[f"/games/{g['slug']}/" for g in GAMES], "/creators/", "/community/", "/about/", "/contact/",
            "/legal/privacy/", "/legal/terms/", "/legal/copyright/", "/legal/data-deletion/", "/legal/cookies/"]
    out["sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
        f"<url><loc>{D}{u}</loc><lastmod>{dt.date.today()}</lastmod></url>" for u in urls) + "</urlset>\n"
    out["robots.txt"] = f"User-agent: *\nAllow: /\nDisallow: /tiktok/\nSitemap: {D}/sitemap.xml\n"
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets/site.css").write_text(CSS.strip() + "\n")
    for rel, content in out.items():
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return sorted(out)


def legal(out):
    u, email = SITE["policies_updated"], SITE["contact_email"]
    def doc(path, title, desc, body):
        out[path.strip("/") + "/index.html"] = page(path, title, desc, f'<section class="prose"><h1>{title}</h1><p class="mute">Last updated {u}</p>{body}</section>')
    doc("/legal/privacy/", "Privacy Policy", "How Mindless Obsessions handles personal information.", f"""
<p>This policy explains what information Mindless Obsessions ("we", "us") handles, why, and your choices. It covers this website, our official social accounts, our Discord server, and the internal tools we use to publish videos to our own accounts.</p>
<h2>This website</h2><p>The site is hosted on GitHub Pages. We use <b>no cookies, analytics, ads, trackers or forms</b>. GitHub, as our host, may process technical data such as IP addresses in server logs to deliver and secure the site; see GitHub's privacy statement.</p>
<h2>When you contact us</h2><p>If you email us, we receive your email address and message and use them only to reply and handle your request. We keep correspondence only as long as needed for that purpose, including records of creator permissions.</p>
<h2>Roblox creators we research or contact</h2><p>To find creators whose clips we might feature with permission, we keep a private list of public creator channel information: channel name, links, public statistics, recent public video titles, and any business contact the creator publishes. We use it only to request permission, keep permission records, and credit creators. We do not sell it. Creators can ask us to delete their information or not to contact them; see Data deletion.</p>
<h2>Social media and Discord</h2><p>When you interact with our TikTok, Instagram, YouTube or Discord, those platforms' own privacy policies apply. We may see your public username and public interactions, and we use aggregate statistics about our own posts to understand what works.</p>
<h2>Our publishing tools</h2><p>Our internal tool "Mindless Obsessions Publisher" connects to our own accounts through official platform APIs (TikTok, YouTube, Meta) only to upload our videos and read statistics for our own posts. Access tokens are stored on our own computer in the operating system's encrypted keyring and are never published or shared.</p>
<h2>Sharing</h2><p>We do not sell or rent personal information and do not share it for advertising. We share information only with the platforms needed to publish our content, or where the law requires.</p>
<h2>Children</h2><p>This website is a general-audience site about Roblox games and entertainment. It collects no personal information through forms or tracking. We do not knowingly collect personal information from children under 13; if you believe a child has emailed us, contact us and we will delete it. Our Roblox games run on Roblox and are subject to Roblox's own privacy policy and parental controls.</p>
<h2>Your choices and rights</h2><p>You can ask us what information we have about you, to correct it, or to delete it. See <a href="/legal/data-deletion/">Data deletion</a>. Depending on where you live, you may have additional rights under local law.</p>
<h2>Changes</h2><p>We will update this page when our practices change and change the date above.</p>
<h2>Contact</h2><p><a href="mailto:{email}">{email}</a> · <a href="{SITE['discord_invite']}">Discord</a></p>""")
    doc("/legal/terms/", "Terms of Service", "Terms for using the Mindless Obsessions website and community.", f"""
<h2>1. Who we are</h2><p>Mindless Obsessions is a Roblox entertainment network and an independent Roblox game studio. "We" and "us" mean the Mindless Obsessions team.</p>
<h2>2. Using this site</h2><p>You may browse and share links to this site. Don't attempt to disrupt it or misuse its content.</p>
<h2>3. Our content</h2><p>Our logo, mascot, game names, artwork and original videos belong to Mindless Obsessions. Please don't reuse them commercially without permission.</p>
<h2>4. Creator content</h2><p>Creator clips we feature belong to their creators and are shared with their written permission, with credit. Creators may revoke permission at any time.</p>
<h2>5. Our games</h2><p>Our games run on Roblox. Playing them is subject to Roblox's Terms of Use and Community Standards. Any in-game purchases are processed by Roblox under Roblox's terms.</p>
<h2>6. Community</h2><p>Our Discord and social spaces have their own rules; Discord's and each platform's terms also apply.</p>
<h2>7. Our publishing tool</h2><p>"Mindless Obsessions Publisher" is an internal tool used only by our team to post to our own official accounts. It is not offered to the public.</p>
<h2>8. Links</h2><p>We link to other sites and platforms we don't control and aren't responsible for their content.</p>
<h2>9. No warranty</h2><p>This site is provided "as is", without warranties of any kind, to the extent permitted by law.</p>
<h2>10. Changes and contact</h2><p>We may update these terms and will change the date above. Questions: <a href="mailto:{email}">{email}</a>.</p>""")
    doc("/legal/copyright/", "Copyright & takedowns", "Copyright, credits and how to request removal of content.", f"""
<h2>Our content</h2><p>© Mindless Obsessions. The Mindless Obsessions name, logo, brain mascot, game names and original content are ours.</p>
<h2>Creator content</h2><p>Creator clips we post are owned by their creators, used with written permission, and credited. We do not claim ownership of creators' footage.</p>
<h2>Trademarks</h2><p>Roblox and related marks are trademarks of Roblox Corporation. Mindless Obsessions is an independent developer and is not affiliated with, sponsored by, or endorsed by Roblox Corporation.</p>
<h2>Request a removal</h2><p>If you believe content we posted uses your work without permission, email <a href="mailto:{email}?subject=Takedown%20request">{email}</a> with: a link to the content, a description of your work, your contact details, and a statement that you are the owner or authorized to act for the owner. We review requests promptly and remove content where appropriate. Platform-level copyright reporting tools on YouTube, TikTok and Instagram are also available.</p>""")
    doc("/legal/data-deletion/", "Data deletion requests", "How to ask Mindless Obsessions to delete your information.", f"""
<p>You can ask us to delete information we hold about you, including creator research records, permission records, or emails.</p>
<h2>How to request</h2><ol><li>Email <a href="mailto:{email}?subject=Data%20deletion%20request">{email}</a> with the subject "Data deletion request".</li>
<li>Tell us what to delete (for example your channel link or the email address you contacted us from).</li>
<li>We may ask a question to confirm the request comes from you.</li></ol>
<h2>What happens</h2><p>We delete the information from our records, generally within 30 days, and confirm by email. If we must keep a minimal record (for example that a creator asked us never to feature their content or contact them again), we keep only what's needed to honor that request.</p>
<h2>Platform data</h2><p>Information you shared on TikTok, Instagram, YouTube or Discord is controlled by those platforms; use their settings to delete it. Data in our Roblox games is handled through Roblox's systems and policies.</p>""")
    doc("/legal/cookies/", "Cookies", "Mindless Obsessions does not use cookies on this website.", f"""
<p>This website does <b>not</b> set cookies and does not use analytics, advertising or tracking scripts, so there is no cookie banner. If that ever changes, we will update this page and ask for consent where required before setting non-essential cookies.</p>
<p>Embedded content or links to TikTok, YouTube, Instagram or Discord take you to those services, which have their own cookie policies.</p>""")


if __name__ == "__main__":
    for f in build():
        print(f)
