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
ALL_GAMES = yaml.safe_load(open(ROOT / "data/games.yaml"))["games"]
# Only games the owner has approved for public promotion appear anywhere on the site (promote: true).
GAMES = [g for g in ALL_GAMES if g.get("promote")]
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
@media (max-width:820px){.nav{gap:4px 16px;padding:8px 16px}.nav .brand{flex:1 1 100%}.nav .brand img{width:36px;height:36px}.nav{overflow-x:auto;flex-wrap:wrap}.nav a.l{font-size:.92rem;padding:4px 0;white-space:nowrap}.hero{grid-template-columns:1fr;text-align:center;padding-top:30px}.hero p{margin:0 auto}.btns{justify-content:center}.hero .logo{max-width:320px;order:-1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
"""

DISCORD_SVG = ('<svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true"><path fill="currentColor" d="M19.6 5.3A17 17 0 0 0 15.4 4l-.5 1.1a15.6 15.6 0 0 0-5.8 0L8.6 4a17 17 0 0 0-4.2 1.3C1.7 9.3 1 13.2 1.3 17.1A17 17 0 0 0 6.5 19.7l1.1-1.8a11 11 0 0 1-1.7-.8l.4-.3a12.2 12.2 0 0 0 11.4 0l.4.3c-.5.3-1.1.6-1.7.8l1.1 1.8a17 17 0 0 0 5.2-2.6c.4-4.5-.7-8.4-3.1-11.8zM8.5 14.7c-1 0-1.9-1-1.9-2.1s.8-2.1 1.9-2.1 1.9 1 1.9 2.1-.8 2.1-1.9 2.1zm7 0c-1 0-1.9-1-1.9-2.1s.8-2.1 1.9-2.1 1.9 1 1.9 2.1-.8 2.1-1.9 2.1z"/></svg>')

HOME_CSS = """
.navdc{margin-left:auto;background:#5865f2;color:#fff!important;font-weight:900;padding:9px 16px;border-radius:999px;text-decoration:none;white-space:nowrap}
.navdc:hover{background:#4752c4}
.dbar{position:fixed;left:12px;right:12px;bottom:max(12px,env(safe-area-inset-bottom));z-index:60;display:none;align-items:center;justify-content:center;gap:10px;
background:#5865f2;color:#fff;font-weight:900;font-size:1.08rem;letter-spacing:.02em;padding:15px 18px;border-radius:16px;text-decoration:none;box-shadow:0 10px 30px rgba(0,0,0,.5)}
@media (max-width:760px){.dbar{display:flex}body{padding-bottom:84px}.navdc{display:none}}
.h-launch{display:grid;grid-template-columns:1.2fr 1fr;gap:0;border-radius:28px;overflow:hidden;border:2px solid #fc72b7;background:#1a0f2e;margin-top:8px;box-shadow:0 30px 80px rgba(252,114,183,.18)}
.h-launch picture,.h-launch img{display:block;width:100%;height:100%;object-fit:cover}
.h-launch .art{aspect-ratio:auto;height:100%;min-height:260px;margin:0;border:0;border-radius:0;padding:28px;box-sizing:border-box}
.h-launch .art img{width:80%;max-width:440px;height:auto;object-fit:contain;margin:0 auto}
.art img{height:auto;object-fit:contain}
.h-launch .txt{padding:30px;display:flex;flex-direction:column;justify-content:center}
.h-launch h2{font-size:clamp(1.9rem,4vw,2.8rem);line-height:1.02;margin:10px 0}
.h-launch .date{display:inline-block;background:#ffd84d;color:#1a0f2e;font-weight:900;padding:6px 12px;border-radius:10px;margin:6px 0 14px}
.btn.dc{background:#5865f2;color:#fff;border-color:#5865f2}
@media (max-width:860px){.h-launch{grid-template-columns:1fr}.h-launch .txt{padding:22px}}
/* ---- Homepage (h-*) ---- */
.h-wrap{max-width:1180px;margin:0 auto;padding:0 20px}
main.home{max-width:none;padding:0;overflow-x:clip}
.h-hero{margin:0;position:relative;overflow:hidden;isolation:isolate;border-bottom:1px solid var(--line)}
.h-hero::before{content:"";position:absolute;inset:0;z-index:-2;background:
 radial-gradient(700px 420px at 78% 38%,rgba(120,18,230,.55),transparent 65%),
 radial-gradient(520px 360px at 12% 20%,rgba(17,249,253,.16),transparent 70%),
 radial-gradient(600px 400px at 40% 110%,rgba(252,114,183,.22),transparent 70%)}
.h-hero::after{content:"";position:absolute;inset:0;z-index:-1;opacity:.35;background-image:linear-gradient(rgba(120,100,255,.18) 1px,transparent 1px),linear-gradient(90deg,rgba(120,100,255,.18) 1px,transparent 1px);background-size:44px 44px;-webkit-mask-image:radial-gradient(ellipse 80% 70% at 50% 40%,#000 30%,transparent 75%);mask-image:radial-gradient(ellipse 80% 70% at 50% 40%,#000 30%,transparent 75%)}
.h-hero .h-wrap{display:grid;grid-template-columns:1.2fr .8fr;gap:28px;align-items:center;padding-top:64px;padding-bottom:56px}
.h-eyebrow{display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:.85rem;letter-spacing:.08em;text-transform:uppercase;color:#e9e4ff;background:rgba(120,18,230,.28);border:1px solid rgba(160,110,255,.45);padding:6px 14px;border-radius:999px}
.h-eyebrow i{width:8px;height:8px;border-radius:50%;background:#2ef08a;box-shadow:0 0 10px #2ef08a}
.h-hero h1{font-size:clamp(2.3rem,4.6vw,3.9rem);line-height:.98;letter-spacing:-.02em;font-weight:900;margin:18px 0 14px}
.h-hero h1 .nw{white-space:nowrap}.h-hero h1 em{font-style:normal;display:block;white-space:nowrap;background:linear-gradient(90deg,var(--cyan),#a98bff 45%,var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 4px 24px rgba(252,114,183,.25))}
.h-hero p.h-sub{color:var(--mute);font-size:1.18rem;max-width:34rem;margin:0}
.h-hero .btns{margin-top:26px}
.btn.big{padding:15px 26px;font-size:1.05rem}
.btn.primary{box-shadow:0 8px 30px rgba(140,40,240,.45)}
.h-logo{position:relative;justify-self:center;width:100%;max-width:560px}
.h-logo img{width:100%;height:auto;display:block;filter:drop-shadow(0 18px 50px rgba(120,18,230,.6));animation:float 6s ease-in-out infinite}
.h-logo::before{content:"";position:absolute;inset:8% 10%;border-radius:50%;background:conic-gradient(from 0deg,rgba(17,249,253,.35),rgba(252,114,183,.35),rgba(120,18,230,.35),rgba(17,249,253,.35));filter:blur(50px);z-index:-1;animation:spin 14s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.h-follow{display:flex;align-items:center;gap:10px;margin-top:28px;flex-wrap:wrap}
.h-follow span{color:var(--mute);font-weight:700;font-size:.9rem;margin-right:4px}
.h-ico{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;color:#fff;background:#221a55;border:1px solid var(--line);transition:transform .15s,background .15s}
.h-ico svg{width:22px;height:22px}
.h-ico:hover{transform:translateY(-3px);color:#fff}
.h-ico.yt:hover{background:#e3001b}.h-ico.tt:hover{background:#111;box-shadow:-3px 0 0 #25f4ee,3px 0 0 #fe2c55}.h-ico.ig:hover{background:linear-gradient(45deg,#f9a825,#e1306c,#833ab4)}.h-ico.dc:hover{background:#5865f2}
.h-ticker{overflow:hidden;background:linear-gradient(90deg,var(--purple),#c0349b);color:#fff;font-weight:900;letter-spacing:.06em;text-transform:uppercase;font-size:.95rem;white-space:nowrap;transform:rotate(-1.2deg);margin:-14px -10px 0;box-shadow:0 10px 30px rgba(0,0,0,.35);position:relative;z-index:2}
.h-ticker div{display:inline-block;padding:12px 0;animation:tick 40s linear infinite}
.h-ticker b{margin:0 18px;color:var(--cyan)}
@keyframes tick{to{transform:translateX(-50%)}}
.h-sec{padding:76px 0 10px}
.h-kicker{color:var(--pink);font-weight:900;letter-spacing:.12em;text-transform:uppercase;font-size:.85rem;margin:0 0 6px}
.h-sec h2{font-size:clamp(1.9rem,4.4vw,3rem);line-height:1.05;letter-spacing:-.01em;font-weight:900;margin:0 0 12px}
.h-sec .lead{font-size:1.1rem}
.h-pillars{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:28px}
.h-pillar{position:relative;border-radius:24px;padding:30px;overflow:hidden;border:1px solid var(--line);background:linear-gradient(160deg,#211a52,#141033)}
.h-pillar::after{content:"";position:absolute;width:260px;height:260px;right:-80px;top:-90px;border-radius:50%;background:var(--glow);filter:blur(60px);opacity:.45}
.h-pillar h3{font-size:1.6rem;margin:10px 0 8px;font-weight:900}.h-pillar p{color:var(--mute);margin:0 0 16px;position:relative;z-index:1}
.h-pillar .tag{display:inline-block;font-weight:900;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;color:var(--glowtxt)}
.h-pillar a{position:relative;z-index:1;font-weight:800}
.h-feature{display:grid;grid-template-columns:1.35fr 1fr;border-radius:28px;overflow:hidden;border:1px solid #2b6c8a;background:#0b1430;margin-top:26px;box-shadow:0 30px 80px rgba(0,0,0,.45),0 0 0 1px rgba(17,249,253,.08)}
.h-feature>a,.h-feature picture{display:block;height:100%}
.h-feature img{width:100%;height:100%;object-fit:cover;display:block}
.h-feature .txt{padding:34px;display:flex;flex-direction:column;justify-content:center;background:linear-gradient(160deg,#0f1b40,#0b1430)}
.h-feature h3{font-size:clamp(1.7rem,3vw,2.3rem);line-height:1.05;margin:12px 0 10px;font-weight:900}
.h-feature p{color:#c9d6ff;margin:0 0 12px}
.h-games{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:26px}
.h-game{display:flex;flex-direction:column;border-radius:22px;overflow:hidden;text-decoration:none;color:var(--ink);background:var(--card);border:1px solid var(--line);transition:transform .2s,box-shadow .2s,border-color .2s}
.h-game:hover{transform:translateY(-6px);border-color:var(--accent);box-shadow:0 18px 50px color-mix(in srgb,var(--accent) 30%,transparent);color:var(--ink)}
.h-game .pic{position:relative;aspect-ratio:16/9;overflow:hidden;background:#120e30}
.h-game .pic img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s}
.h-game:hover .pic img{transform:scale(1.05)}
.h-game .pic .lbl{position:absolute;left:10px;bottom:10px;font-size:.72rem;font-weight:800;padding:3px 9px;border-radius:999px;background:rgba(8,6,24,.78);color:#e8e4ff}
.h-ph{position:absolute;inset:0;display:grid;place-items:center;text-align:center;background:
 repeating-linear-gradient(135deg,color-mix(in srgb,var(--accent) 10%,transparent) 0 14px,transparent 14px 28px),
 radial-gradient(circle at 50% 45%,color-mix(in srgb,var(--accent) 45%,transparent),transparent 65%),#130f34}
.h-ph strong{display:block;font-size:1.25rem;margin-bottom:22px;font-weight:900;line-height:1.05;padding:0 18px;text-shadow:0 3px 18px rgba(0,0,0,.6)}
.h-ph img.m{width:58px!important;height:58px!important;filter:drop-shadow(0 4px 12px rgba(0,0,0,.5));object-fit:contain!important;margin:0 auto 8px}
.h-game .body{padding:18px 20px 22px;display:flex;flex-direction:column;gap:6px;flex:1}
.h-game h3{margin:4px 0 0;font-size:1.3rem;font-weight:900;line-height:1.15}
.h-game p{margin:0;color:var(--mute)}
.h-game .go{margin-top:auto;padding-top:10px;font-weight:800;color:var(--accent)}
.h-game.next{grid-column:1/-1;flex-direction:row;border:2px dashed #5b4bb5;background:linear-gradient(160deg,#1a1442,#100c2a)}
.h-game.next .pic{flex:0 0 34%;aspect-ratio:auto;min-height:170px;display:grid;place-items:center;background:radial-gradient(circle at 50% 50%,rgba(120,18,230,.45),transparent 65%),#100c2a}
.h-game.next .inf{font-size:5.2rem;font-weight:900;line-height:1;background:linear-gradient(90deg,var(--cyan),var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent}
.h-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px;counter-reset:s}
.h-step{border-radius:20px;padding:24px;background:var(--card);border:1px solid var(--line);position:relative}
.h-step::before{counter-increment:s;content:counter(s);display:grid;place-items:center;width:44px;height:44px;border-radius:14px;font-weight:900;font-size:1.25rem;color:#0d0b24;background:linear-gradient(135deg,var(--cyan),var(--pink));margin-bottom:12px}
.h-step h3{margin:0 0 6px;font-size:1.2rem}.h-step p{margin:0;color:var(--mute)}
.h-creator-cta{margin-top:22px;display:flex;gap:12px;flex-wrap:wrap}
.h-socials{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:26px}
.h-soc{display:flex;flex-direction:column;gap:14px;padding:22px;border-radius:22px;text-decoration:none;color:#fff;min-height:170px;position:relative;overflow:hidden;transition:transform .2s,box-shadow .2s}
.h-soc:hover{transform:translateY(-5px);color:#fff;box-shadow:0 18px 40px rgba(0,0,0,.4)}
.h-soc svg{width:38px;height:38px}
.h-soc b{font-size:1.3rem;font-weight:900}.h-soc small{opacity:.9;font-size:.95rem;overflow-wrap:anywhere}
.h-soc .arr{margin-top:auto;font-weight:800}
.h-soc.yt{background:linear-gradient(150deg,#ff2d3d,#a0001a)}
.h-soc.tt{background:linear-gradient(150deg,#1b1b1f,#050507);box-shadow:inset 4px 0 0 #25f4ee,inset -4px 0 0 #fe2c55}
.h-soc.ig{background:linear-gradient(45deg,#f9a825,#e1306c 50%,#833ab4)}
.h-soc.dc{background:linear-gradient(150deg,#6d78ff,#3c45c9)}
.h-discord{margin:80px 0 70px;border-radius:30px;padding:40px;display:grid;grid-template-columns:auto 1fr;gap:30px;align-items:center;background:radial-gradient(500px 300px at 85% 0%,rgba(252,114,183,.35),transparent 70%),linear-gradient(120deg,#2b1f6e,#4a1d86);border:1px solid #6b4fe0;box-shadow:0 30px 80px rgba(60,20,140,.45)}
.h-discord img{width:160px;height:auto;filter:drop-shadow(0 10px 30px rgba(17,249,253,.35));animation:float 6s ease-in-out infinite}
.h-discord h2{margin:0 0 8px;font-size:clamp(1.7rem,3.6vw,2.5rem);font-weight:900;line-height:1.05}
.h-discord p{color:#e2dcff;margin:0 0 18px;font-size:1.08rem}
.btn.white{background:#fff;color:#3b2a9a}.btn.white:hover{color:#3b2a9a}
@media (max-width:980px){.h-games{grid-template-columns:1fr 1fr}.h-socials{grid-template-columns:1fr 1fr}.h-feature{grid-template-columns:1fr}.h-steps{grid-template-columns:1fr}}
@media (max-width:820px){
 .h-hero .h-wrap{grid-template-columns:1fr;text-align:center;padding-top:28px;padding-bottom:44px;gap:6px}
 .h-logo{max-width:330px;order:-1}.h-hero p.h-sub{margin:0 auto}.h-hero .btns,.h-follow{justify-content:center}
 .h-pillars{grid-template-columns:1fr}.h-sec{padding-top:58px}
 .h-discord{grid-template-columns:1fr;text-align:center;padding:30px 22px}.h-discord img{width:120px;margin:0 auto}
}
@media (max-width:600px){.h-games{grid-template-columns:1fr}.h-game.next{flex-direction:column}.h-game.next .pic{min-height:130px}}
@media (max-width:520px){.h-hero .btns .btn{flex:1 1 100%;justify-content:center}.h-socials{gap:12px}.h-soc{min-height:150px;padding:18px}.h-soc b{font-size:1.15rem}.h-soc small{font-size:.7rem;letter-spacing:-.01em}.h-eyebrow{font-size:.64rem;letter-spacing:.04em;white-space:nowrap;padding:6px 11px}.h-feature .txt{padding:24px}}
"""

ICONS = {  # simple inline SVG glyphs (no third-party scripts or fonts)
    "YouTube": ("yt", '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.75 15.1V8.9L15.5 12l-5.75 3.1z"/></svg>'),
    "TikTok": ("tt", '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.6 2h-3.4v13.4a2.9 2.9 0 1 1-2.9-2.9c.3 0 .6 0 .9.1V9.1a6.4 6.4 0 1 0 5.4 6.3V8.6a8 8 0 0 0 4.6 1.5V6.7a4.7 4.7 0 0 1-4.6-4.7z"/></svg>'),
    "Instagram": ("ig", '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="12" cy="12" r="4.4" fill="none" stroke="currentColor" stroke-width="2.2"/><circle cx="17.6" cy="6.4" r="1.4" fill="currentColor"/></svg>'),
    "Discord": ("dc", '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.6 5.3A17 17 0 0 0 15.4 4l-.5 1.1a15.6 15.6 0 0 0-5.8 0L8.6 4a17 17 0 0 0-4.2 1.3C1.7 9.3 1 13.2 1.3 17.1A17 17 0 0 0 6.5 19.7l1.1-1.8a11 11 0 0 1-1.7-.8l.4-.3a12.2 12.2 0 0 0 11.4 0l.4.3c-.5.3-1.1.6-1.7.8l1.1 1.8a17 17 0 0 0 5.2-2.6c.4-4.5-.7-8.4-3.1-11.8zM8.5 14.7c-1 0-1.9-1-1.9-2.1s.8-2.1 1.9-2.1 1.9 1 1.9 2.1-.8 2.1-1.9 2.1zm7 0c-1 0-1.9-1-1.9-2.1s.8-2.1 1.9-2.1 1.9 1 1.9 2.1-.8 2.1-1.9 2.1z"/></svg>'),
}


def handle(l):
    u = l["url"].rstrip("/")
    return "Join the server" if l["label"] == "Discord" else "@" + u.rsplit("/", 1)[-1].lstrip("@")


def art_picture(g, sizes, eager=False):
    a = g.get("art")
    if not a:  # no approved art yet (e.g. visuals being redesigned): branded placeholder, never an old screenshot
        return ('<div class="art" style="margin:0"><img src="/assets/logo-v3-480.png" alt="Mindless Obsessions logo" width="480" height="386">'
                '<small>New look coming soon</small></div>')
    f = f"/assets/games/{a['file']}"
    return (f'<picture><source type="image/webp" srcset="{f}-800.webp 800w, {f}-1600.webp 1600w" sizes="{sizes}">'
            f'<img src="{f}-800.webp" alt="{E(a["alt"])}" width="800" height="{450 if a["kind"] == "screenshot" else 450}"'
            f'{"" if eager else " loading=" + chr(34) + "lazy" + chr(34)} decoding="async"></picture>')


def home_game_card(g):
    st = g["status"]
    if g.get("art"):
        lbl = "Official key art" if g["art"]["kind"] == "key-art" else "In-game screenshot · in development"
        pic = art_picture(g, "(max-width:600px) 100vw, 380px") + f'<span class="lbl">{lbl}</span>'
    else:
        pic = (f'<div class="h-ph"><div><img class="m" src="/assets/logo-v3-480.png" alt="" width="80" height="64">'
               f'<strong>{E(g["name"])}</strong></div></div><span class="lbl">Artwork coming soon</span>')
    return f"""<a class="h-game" style="--accent:{g['accent']}" href="/games/{g['slug']}/">
<div class="pic">{pic}</div><div class="body"><div><span class="pill {'live' if st == 'released' else 'dev'}">{STATUS[st]}</span><span class="pill">{E(g['genre'])}</span></div>
<h3>{E(g['name'])}</h3><p>{E(g['summary'])}</p><span class="go">View game →</span></div></a>"""


def join_page():
    """One-tap Discord landing page (TikTok bio destination). Focused: no nav, one big button."""
    inv = SITE["discord_invite"]
    g = next((x for x in GAMES if x["slug"] == "spit-on-them-tycoon"), {})
    title = "Join our Discord · Spit On Them Tycoon"
    desc = "Join the Mindless Obsessions Discord for Spit On Them Tycoon launch updates, sneak peeks and the community."
    perks = [("🚀", "Launch-day ping", f"Be first to know when Spit On Them Tycoon goes live on Roblox ({E(g.get('launch_note', 'coming soon'))})."),
             ("👀", "Sneak peeks", "New characters, updates and clips in #spit-updates before anywhere else."),
             ("😂", "Hang out", "Chat Roblox, share your funniest clips and fan art with other players."),
             ("💡", "Shape the game", "Drop ideas in #suggestions. The devs read them.")]
    cards = "".join(f'<li><span class="e" aria-hidden="true">{e}</span><div><b>{t}</b><p>{d}</p></div></li>' for e, t, d in perks)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{D}/join/">
<link rel="icon" href="/assets/favicon-64.png"><link rel="apple-touch-icon" href="/assets/favicon-180.png"><meta name="theme-color" content="#0d0b24">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{D}/join/"><meta property="og:image" content="{D}/assets/og-v3-1200x630.png"><meta name="twitter:card" content="summary_large_image">
<style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#fff;text-align:center;
background:radial-gradient(120% 70% at 50% 0%,#3b1466 0%,#160c33 55%,#0d0b24 100%);padding:28px 16px calc(32px + env(safe-area-inset-bottom))}}
.w{{max-width:520px;margin:0 auto}}
.m{{width:min(56vw,230px);height:auto;filter:drop-shadow(0 12px 30px rgba(252,114,183,.45));animation:b 2.6s ease-in-out infinite}}
@keyframes b{{50%{{transform:translateY(-8px) rotate(-2deg)}}}}
@media (prefers-reduced-motion:reduce){{.m{{animation:none}}}}
.k{{display:inline-block;margin:14px 0 6px;font-weight:800;font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;color:#11f9fd}}
h1{{margin:0;font-size:clamp(2.3rem,11vw,3.4rem);line-height:.95;font-weight:950;letter-spacing:-.02em;
background:linear-gradient(90deg,#fc72b7,#ffd84d);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{color:#d8d2ff;font-size:1.08rem;margin:12px 0 4px}}
.date{{display:inline-block;background:#ffd84d;color:#1a0f2e;font-weight:900;padding:6px 12px;border-radius:10px;margin:10px 0 18px}}
.cta{{display:flex;align-items:center;justify-content:center;gap:12px;width:100%;min-height:72px;border-radius:20px;background:#5865f2;color:#fff;
text-decoration:none;font-weight:950;font-size:1.45rem;letter-spacing:.02em;box-shadow:0 14px 40px rgba(88,101,242,.55);animation:p 1.8s ease-in-out infinite}}
@keyframes p{{50%{{box-shadow:0 14px 56px rgba(88,101,242,.9)}}}}
.cta:active{{transform:scale(.98)}}
.inv{{margin:10px 0 0;color:#a9a3d9;font-size:.92rem}}.inv a{{color:#a9b2ff}}
ul{{list-style:none;padding:0;margin:26px 0 22px;text-align:left;display:grid;gap:12px}}
li{{display:flex;gap:14px;align-items:flex-start;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:14px}}
li .e{{font-size:1.7rem;line-height:1}}li b{{font-size:1.05rem}}li p{{margin:3px 0 0;color:#cfc9f5;font-size:.95rem}}
.cta.two{{min-height:62px;font-size:1.2rem;animation:none}}
.f{{margin-top:22px;font-size:.85rem;color:#8f89c0}}.f a{{color:#c9c3ff}}
</style></head>
<body><main class="w">
<img class="m" src="/assets/logo-v3-480.png" alt="Mindless Obsessions logo" width="230" height="185">
<span class="k">Mindless Obsessions presents</span>
<h1>SPIT ON THEM TYCOON</h1>
<p class="sub">Our hilarious Roblox tycoon is almost here. Join the Discord and be there for launch.</p>
{f'<span class="date">{E(g["launch_note"])} · not released yet</span>' if g.get("launch_note") else ""}
<a class="cta" href="{inv}" rel="noopener">{DISCORD_SVG}<span>JOIN OUR DISCORD</span></a>
<p class="inv">Official invite: <a href="{inv}" rel="noopener">{E(inv.replace("https://", ""))}</a> · free · 13+</p>
<ul>{cards}</ul>
<a class="cta two" href="{inv}" rel="noopener">{DISCORD_SVG}<span>JOIN THE DISCORD</span></a>
<p class="f">Follow us: <a href="https://www.tiktok.com/@mindlessobsessions">TikTok</a> · <a href="https://www.youtube.com/@mindlessobsessions">YouTube</a> · <a href="https://www.instagram.com/mindlessobsessions.gg/">Instagram</a> · <a href="/?stay=1">Visit the website</a><br>
Roblox is a trademark of Roblox Corporation; we are not affiliated with or endorsed by Roblox.</p>
</main></body></html>"""


def launch_section():
    g = next((x for x in GAMES if x["slug"] == "spit-on-them-tycoon"), None)
    if not g:
        return ""
    return f"""<section class="h-sec" id="spit" aria-labelledby="lt"><p class="h-kicker">Coming to Roblox</p>
<div class="h-launch"><a href="/games/{g['slug']}/" tabindex="-1" aria-hidden="true">{art_picture(g, "(max-width:860px) 100vw, 640px", eager=True)}</a>
<div class="txt"><div><span class="pill dev">Not released yet</span><span class="pill">{E(g['genre'])}</span></div>
<h2 id="lt">{E(g['name'])}</h2><p>{E(g.get('pitch') or g['summary'])}</p>
{f'<span class="date">{E(g["launch_note"])}</span>' if g.get("launch_note") else ""}
<div class="btns"><a class="btn dc big" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join the Discord for launch day</a><a class="btn ghost" href="/games/{g['slug']}/">About the game</a></div></div></div></section>"""


def home_body():
    by = {g["slug"]: g for g in GAMES}
    feat = by.get("spit-on-them-tycoon")
    icons = "".join(f'<a class="h-ico {ICONS[l["label"]][0]}" href="{E(l["url"])}" rel="me noopener" target="_blank" aria-label="{E(l["label"])}">{ICONS[l["label"]][1]}</a>'
                    for l in SITE["links"] if l["label"] in ICONS)
    socials = "".join(f'<a class="h-soc {ICONS[l["label"]][0]}" href="{E(l["url"])}" rel="me noopener" target="_blank">{ICONS[l["label"]][1]}'
                      f'<div><b>{E(l["label"])}</b><br><small>{E(handle(l))}</small></div><span class="arr">{"Join" if l["label"] == "Discord" else "Follow"} →</span></a>'
                      for l in SITE["links"] if l["label"] in ICONS)
    words = ["Original Roblox games", "Creator highlights", "Funny moments", "Epic clips", "New games always in the lab",
             "Permission-first", "Tycoon", "Multiplayer chaos"]
    tick = "".join(f"{E(w)}<b>✦</b>" for w in words)
    feature = ""
    if feat and feat.get("art") and feat["slug"] != "spit-on-them-tycoon":
        feature = f"""<div class="h-feature"><a href="/games/{feat['slug']}/" tabindex="-1" aria-hidden="true">{art_picture(feat, "(max-width:980px) 100vw, 700px", eager=True)}</a>
<div class="txt"><div><span class="pill dev">{STATUS[feat['status']]}</span><span class="pill">{E(feat['genre'])}</span></div>
<h3>{E(feat['name'])}</h3><p>{E(feat['summary'])}</p>{f"<p>{E(feat['details'])}</p>" if feat.get('details') else ""}
<div class="btns"><a class="btn primary" href="/games/{feat['slug']}/">See the game</a></div></div></div>"""
    cards = "".join(home_game_card(g) for g in GAMES if not (feature and g is feat))
    nxt = f"""<a class="h-game next" style="--accent:#a98bff" href="{SITE['discord_invite']}" rel="noopener" target="_blank">
<div class="pic"><span class="inf" aria-hidden="true">∞</span></div><div class="body"><div><span class="pill">Game #{len(GAMES) + 1} and beyond</span></div>
<h3>The next obsession is in the lab</h3><p>New genres, new chaos, new games. Follow along on Discord.</p>
<span class="go">Get updates on Discord →</span></div></a>"""
    return f"""
<section class="h-hero"><div class="h-wrap"><div>
<span class="h-eyebrow"><i></i>Roblox game studio + entertainment network</span>
<h1><span class="nw">Your daily dose of</span> <em>Roblox insanity</em></h1>
<p class="h-sub">We build original Roblox games, and we share the funniest, most epic moments from Roblox creators, with their permission. New games. New creators. Endless obsessions.</p>
<div class="btns"><a class="btn dc big" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join our Discord</a><a class="btn ghost big" href="#spit">Spit On Them Tycoon</a></div>
<div class="h-follow"><span>Follow us</span>{icons}</div></div>
<div class="h-logo"><img src="/assets/logo-v3-720.png" alt="Mindless Obsessions logo: a grinning pink brain wearing headphones, holding a game controller" width="722" height="580" fetchpriority="high"></div>
</div></section>
<div class="h-ticker" aria-hidden="true"><div>{tick}{tick}</div></div>

<div class="h-wrap">
{launch_section()}
<section class="h-sec" aria-labelledby="two"><p class="h-kicker">What we do</p><h2 id="two">Two things. One obsession.</h2>
<div class="h-pillars">
<div class="h-pillar" style="--glow:#11f9fd;--glowtxt:#7ffcff"><span class="tag">The studio</span><h3>We make Roblox games</h3>
<p>Original Roblox games. Our first, Spit On Them Tycoon, is in development right now, and more ideas are in the lab.</p><a href="#games">See our games →</a></div>
<div class="h-pillar" style="--glow:#fc72b7;--glowtxt:#ffb0d8"><span class="tag">The network</span><h3>We share Roblox's best moments</h3>
<p>Funny moments, wins, fails and wild challenges from Roblox creators and streamers, posted only with their permission and always credited.</p><a href="#creators">How highlights work →</a></div>
</div></section>

<section class="h-sec" id="games" aria-labelledby="gt"><p class="h-kicker">Our games</p><h2 id="gt">Built by Mindless Obsessions</h2>
<p class="lead">Every game here is an original Mindless Obsessions project. Each status is accurate, and we'll add a "Play on Roblox" link when a game goes public.</p>
{feature}
<div class="h-games">{cards}{nxt}</div></section>

<section class="h-sec" id="creators" aria-labelledby="ct"><p class="h-kicker">Creator highlights</p><h2 id="ct">The best of Roblox, credited properly</h2>
<p class="lead">We feature short highlights from Roblox creators and streamers on TikTok, Instagram Reels, YouTube Shorts and Facebook. Our rules are simple:</p>
<div class="h-steps"><div class="h-step"><h3>Permission first</h3><p>We only post a creator's footage after they give us written permission, for each platform.</p></div>
<div class="h-step"><h3>Always credited</h3><p>Every clip names the creator on screen and links to their channel. No watermark removal, no misleading edits.</p></div>
<div class="h-step"><h3>Down on request</h3><p>Creators can ask us to take a clip down at any time, and we remove it promptly.</p></div></div>
<div class="h-creator-cta"><a class="btn primary" href="mailto:{SITE['contact_email']}?subject=Creator%20highlights">I'm a creator: feature me</a><a class="btn ghost" href="/creators/">How it works</a></div></section>

<section class="h-sec" aria-labelledby="ft"><p class="h-kicker">Follow the obsession</p><h2 id="ft">Find us everywhere</h2>
<div class="h-socials">{socials}</div></section>

<section class="h-discord" aria-labelledby="dt"><img src="/assets/logo-v3-480.png" alt="The Mindless Obsessions brain mascot" width="150" height="150" loading="lazy">
<div><h2 id="dt">Join the community on Discord</h2><p>Chat Roblox, share clips and fan art, get game updates first, and help test what we build.</p>
<a class="btn white big" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join our Discord</a></div></section>
</div>"""


NAV = [("/", "Home"), ("/games/", "Games"), ("/creators/", "Creator Highlights"), ("/community/", "Community"),
       ("/about/", "About"), ("/contact/", "Contact")]


def page(path, title, desc, body, active=None, main_class=""):
    canonical = f"{D}{path}"
    nav = "".join(f'<a class="l" href="{h}"{" aria-current=page" if h == active else ""}>{E(t)}</a>' for h, t in NAV)
    links = "".join(f'<a href="{E(l["url"])}" rel="me noopener" target="_blank">{E(l["label"])}</a>' for l in SITE["links"])
    full_title = title if title.startswith(SITE["name"]) else f"{title} · {SITE['name']}"
    ld = json.dumps({"@context": "https://schema.org", "@type": "Organization", "name": SITE["name"], "url": D,
                     "logo": f"{D}/assets/logo-circle-v3-512.png", "sameAs": [l["url"] for l in SITE["links"]]})
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full_title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}"><link rel="icon" href="/assets/favicon-64.png"><link rel="apple-touch-icon" href="/assets/favicon-180.png">
<meta name="theme-color" content="#0d0b24">
<meta property="og:type" content="website"><meta property="og:site_name" content="{E(SITE['name'])}"><meta property="og:title" content="{E(full_title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{D}/assets/og-v3-1200x630.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{D}/assets/og-v3-1200x630.png">
<link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{ld}</script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><nav class="nav" aria-label="Main"><a class="brand" href="/"><img src="/assets/logo-circle-v3-96.png" alt="" width="42" height="42">Mindless Obsessions</a>{nav}<a class="navdc" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join Discord</a></nav></header>
<main id="main"{f' class="{main_class}"' if main_class else ""}>{body}</main>
<a class="dbar" href="{SITE['discord_invite']}" rel="noopener" target="_blank">{DISCORD_SVG}<span>JOIN OUR DISCORD</span></a>
<footer class="bottom"><div class="in"><div>© {dt.date.today().year} {E(SITE['name'])}. Roblox is a trademark of Roblox Corporation; we are not affiliated with or endorsed by Roblox.</div>
<nav aria-label="Social">{links}</nav>
<nav aria-label="Legal"><a href="/legal/privacy/">Privacy</a><a href="/legal/terms/">Terms</a><a href="/legal/copyright/">Copyright</a><a href="/legal/data-deletion/">Data deletion</a><a href="/legal/cookies/">Cookies</a></nav></div></footer>
</body></html>"""


def game_card(g):
    st = g["status"]
    return f"""<a class="card game" style="--accent:{g['accent']}" href="/games/{g['slug']}/">
<div class="art"><img src="/assets/logo-v3-480.png" alt="Mindless Obsessions logo" loading="lazy"><small>Artwork coming soon</small></div>
<span class="pill {'live' if st == 'released' else 'dev'}">{STATUS[st]}</span><span class="pill">{E(g['genre'])}</span>
<h3>{E(g['name'])}</h3><p>{E(g['summary'])}</p></a>"""


def social_links():
    return '<div class="social">' + "".join(
        f'<a href="{E(l["url"])}" rel="me noopener" target="_blank">{l["icon"]} {E(l["label"])}</a>' for l in SITE["links"]) + "</div>"


def discord_block():
    return f"""<div class="discord"><img src="/assets/logo-circle-v3-192.png" alt="Mindless Obsessions logo">
<div><h2 style="margin:0">Join the community on Discord</h2><p class="lead">Chat Roblox, share your clips and fan art, get game updates, and help test what we build.</p>
<a class="btn primary" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join our Discord</a></div></div>"""


def build():
    out = {}
    cards = "".join(game_card(g) for g in GAMES)
    out["index.html"] = page("/", f"{SITE['name']}: Roblox entertainment network & game studio", SITE["description"], home_body(), "/", "home")
    out["index.html"] = out["index.html"].replace("<head>", """<head><script>(function(){try{var q=location.search,r=document.referrer||"",u=navigator.userAgent||"";
if(q.indexOf("stay=1")<0&&(/tiktok\\.com/i.test(r)||/musical_ly|BytedanceWebview|TikTok/i.test(u))){location.replace("/join/?from=tiktok")}}catch(e){}})();</script>""", 1)
    out["games/index.html"] = page("/games/", "Our games", "Original Roblox games from the Mindless Obsessions studio.", f"""
<section><h1>Our games</h1><p class="lead">Every game below is an original Mindless Obsessions project. Status reflects where it really is; we will add Roblox links when a game is publicly available.</p>
<div class="grid">{cards}</div></section><section>{discord_block()}</section>""", "/games/")
    for g in GAMES:
        roblox = (f'<a class="btn primary" href="{E(g["roblox_url"])}" rel="noopener" target="_blank">Play on Roblox</a>'
                  if g.get("roblox_url") else '<span class="pill dev">Not yet available to play</span>')
        details = f"<p>{E(g['details'])}</p>" if g.get("details") else ""
        out[f"games/{g['slug']}/index.html"] = page(f"/games/{g['slug']}/", g["name"], g["summary"], f"""
<section class="prose" style="--accent:{g['accent']}"><p><a href="/games/">← All games</a></p>
{('<div style="max-width:720px;border-radius:18px;overflow:hidden">' + art_picture(g, "(max-width:760px) 100vw, 720px", eager=True) + '</div><p><small>In-game screenshot · in development</small></p>') if g.get('art') else '<div class="art" style="max-width:640px"><img src="/assets/logo-v3-480.png" alt="Mindless Obsessions logo" width="480" height="386"><small>Official artwork and screenshots coming soon</small></div>'}
<span class="pill dev">{STATUS[g['status']]}</span><span class="pill">{E(g['genre'])}</span>
<h1>{E(g['name'])}</h1><p class="lead">{E(g['summary'])}</p>{details}
{f'<p><strong>{E(g["launch_note"])}</strong></p>' if g.get("launch_note") else ""}<div class="btns">{roblox}<a class="btn dc" href="{SITE['discord_invite']}" rel="noopener" target="_blank">Join our Discord</a></div>
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
<li>Game updates, testing and bug reports</li></ul>
<p>Please read the server rules when you join. Discord requires members to be at least 13.</p>
<h2>Follow us</h2>{social_links()}
<h2>Creator collaborations</h2><p>Roblox creators can reach us about highlights and collaborations: <a href="/contact/">contact us</a>.</p></section>""", "/community/")
    out["about/index.html"] = page("/about/", "About", "About Mindless Obsessions: a Roblox entertainment network and an independent game studio.", f"""
<section class="prose"><h1>About Mindless Obsessions</h1>
<p class="lead">We're two things at once: a Roblox entertainment network and an independent Roblox game studio.</p>
<h2>The network</h2><p>We share the funniest, craziest and most epic Roblox moments across YouTube, TikTok and Instagram, featuring creators and streamers who've given us permission, always with credit.</p>
<h2>The studio</h2><p>We build original Roblox games. Our first, Spit On Them Tycoon, is in development. See <a href="/games/">our games</a>.</p>
<h2>Our community</h2><p>Our <a href="{SITE['discord_invite']}">Discord</a> is home base: game updates, testing, clips and fan art.</p></section>""", "/about/")
    out["contact/index.html"] = page("/contact/", "Contact", "Contact Mindless Obsessions for business, creator collaborations and permission requests.", f"""
<section class="prose"><h1>Contact</h1>
<div class="grid"><div class="card"><h3>Business inquiries</h3><p><a href="mailto:{SITE['contact_email']}?subject=Business%20inquiry">{SITE['contact_email']}</a></p></div>
<div class="card"><h3>Creator collaborations</h3><p>Email us with your channel link (subject: Creator highlights) or message us on <a href="{SITE['discord_invite']}">Discord</a>.</p></div>
<div class="card"><h3>Takedowns &amp; permissions</h3><p>Want a clip removed or a permission changed? Email us with the link; we act promptly. See <a href="/legal/copyright/">Copyright</a>.</p></div>
<div class="card"><h3>Privacy &amp; data deletion</h3><p>See <a href="/legal/data-deletion/">how to request deletion</a>.</p></div></div></section>""", "/contact/")
    legal(out)
    out["404.html"] = page("/404.html", "Page not found", "This page does not exist.", f"""
<section class="prose" style="text-align:center;padding:60px 0"><img src="/assets/logo-v3-480.png" alt="Confused Mindless Obsessions mascot" width="180" height="180">
<h1>404: our brain lost this page</h1><p class="lead">It may have moved. Try the <a href="/">home page</a> or <a href="/games/">our games</a>.</p></section>""")
    out["join/index.html"] = join_page()
    # Keep old URLs used by the TikTok developer app working.
    for old, new in (("terms.html", "/legal/terms/"), ("privacy.html", "/legal/privacy/")):
        out[old] = (f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{D}{new}">'
                    f'<meta http-equiv="refresh" content="0; url={new}"><p>Moved to <a href="{new}">{new}</a>.</p>')
    urls = ["/", "/join/", "/games/", *[f"/games/{g['slug']}/" for g in GAMES], "/creators/", "/community/", "/about/", "/contact/",
            "/legal/privacy/", "/legal/terms/", "/legal/copyright/", "/legal/data-deletion/", "/legal/cookies/"]
    out["sitemap.xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
        f"<url><loc>{D}{u}</loc><lastmod>{dt.date.today()}</lastmod></url>" for u in urls) + "</urlset>\n"
    out["robots.txt"] = f"User-agent: *\nAllow: /\nDisallow: /tiktok/\nSitemap: {D}/sitemap.xml\n"
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets/site.css").write_text(CSS.strip() + "\n" + HOME_CSS.strip() + "\n")
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
