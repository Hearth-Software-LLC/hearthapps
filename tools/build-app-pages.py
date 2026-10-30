#!/usr/bin/env python3
"""Build one product page per app from tools/app_pages_data.py.

    python3 tools/build-app-pages.py && npm run icons

Writes <app>/index.html for every app in APPS. The nav and footer are copied from
index.html, so edit those there first. Icons are written as empty
<svg data-lucide="Name"> tags; `npm run icons` renders them.
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app_pages_data import APPS, HEARTH_PLUS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, 'assets/img/renders/renders.json')))
ORDER = ['bigtable', 'suffice', 'sated', 'caloma', 'hearken', 'trove', 'ember']
NAMES = {'bigtable': 'BigTable', 'suffice': 'Suffice', 'sated': 'Sated', 'caloma': 'Caloma', 'hearken': 'Hearken', 'trove': 'Trove', 'ember': 'Ember'}
# A darker shade for filled buttons and the hero, so white text stays readable.
STRONG = {'bigtable': '#D9472B', 'suffice': '#167A52', 'sated': '#C2540A', 'caloma': '#D02148', 'hearken': '#0A6CF0', 'trove': '#0F7A9C'}
e = html.escape

def page_url(app):
    return f'/{app}' if app in APPS else f'/#{app}'

def img(key, cls, sizes, alt, eager=False):
    m = M[key]; app, name = key.split('/')
    srcset = ', '.join(f'/assets/img/renders/{app}/{name}-{w}.webp {w}w' for w in m['widths'])
    load = ' fetchpriority="high"' if eager else ' loading="lazy"'
    c = f'render {cls}'.strip()
    return (f'<img class="{c}" src="/assets/img/renders/{app}/{name}-{m["widths"][0]}.webp" srcset="{srcset}" '
            f'sizes="{sizes}" width="{m["w"]}" height="{m["h"]}" alt="{e(alt)}"{load} decoding="async">')

def icon(name, size=20):
    return f'<svg data-lucide="{name}" width="{size}" height="{size}"></svg>'

def appicon(app, size, alt=''):
    return (f'<img class="ic-l" src="/assets/img/{app}@2x.webp" width="{size}" height="{size}" alt="{alt}" loading="lazy">'
            f'<img class="ic-d" src="/assets/img/{app}-dark@2x.webp" width="{size}" height="{size}" alt="{alt}" loading="lazy">')

def ticks(items):
    return ''.join(f'<li>{icon("Check")}<span>{e(t)}</span></li>' for t in items)

def get_button(a, cls='store', label=True):
    if a['store']:
        return f'<a class="{cls}" href="{a["store"]}" rel="noopener"><span><small>Download on the</small>App Store</span></a>'
    return f'<a class="{cls} beta" href="{a["beta"]}" rel="noopener"><img class="store-icon" src="/assets/img/testflight-app-icon.webp" width="32" height="32" alt="" decoding="async"><span><small>Join the beta on</small>TestFlight</span></a>'

def chrome():
    home = open(os.path.join(ROOT, 'index.html')).read()
    header = home[home.index('<header class="nav">'):home.index('</header>') + 9]
    footer = home[home.index('<footer class="foot">'):home.index('</footer>') + 9]
    header = re.sub(r'href="/?#(ember|beta)"', r'href="/#\1"', header)
    header = re.sub(r'href="/?#(bigtable|suffice|sated|caloma|hearken|trove)"', r'href="/\1"', header)
    return header, footer

def build(app, a, header, footer):
    n = a['name']; strong = STRONG[app]
    head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(a["title"])} · Hearth</title>
<meta name="description" content="{e(a["description"])}">
<link rel="canonical" href="https://hearthapps.com/{app}">
<meta name="theme-color" content="{strong}">
<meta name="color-scheme" content="light dark">
<script>(function(){{var t;try{{t=localStorage.getItem('hearth-theme')}}catch(e){{}}var d=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;document.documentElement.setAttribute('data-theme',d?'dark':'light')}})();</script>
<meta property="og:type" content="website">
<meta property="og:site_name" content="Hearth">
<meta property="og:title" content="{e(n)} — {e(a["h1"])}">
<meta property="og:description" content="{e(a["description"])}">
<meta property="og:url" content="https://hearthapps.com/{app}">
<meta property="og:image" content="https://hearthapps.com/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/css/site.css">
<script src="/assets/js/site.js" defer></script>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "SoftwareApplication", "name": n, "operatingSystem": "iOS 26, iPadOS 26", "applicationCategory": "LifestyleApplication", "description": a["description"], "url": f"https://hearthapps.com/{app}", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@type": "Organization", "name": "Hearth Software LLC", "url": "https://hearthapps.com/"}}, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''
    hdr = header.replace(f'href="/{app}">', f'href="/{app}" aria-current="page">', 1)
    cta_href = a['store'] or a['beta']; cta_label = 'Download' if a['store'] else 'Join the beta'
    has_plans = bool(a.get('plans'))
    links = '<a href="#features">Features</a><a href="#screens">Every screen</a><a href="#together">With Hearth</a>'
    links += '<a href="#plans">Plans</a>' + '<a href="#faq">FAQ</a>'
    ipad, phone, ipad_alt, phone_alt = a['hero']
    out = [head, hdr, f'''
<main id="main" class="product" style="--accent:var(--{app});--accent-ink:var(--{app}-ink);--accent-strong:{strong}">

<div class="pnav">
  <div class="wrap pnav-in">
    <a class="pnav-name" href="#top">{appicon(app, 28)}{n}</a>
    <nav class="pnav-links" aria-label="{n}">{links}<a class="pnav-cta" href="{cta_href}" rel="noopener">{cta_label}</a></nav>
  </div>
</div>

<section id="top" class="p-hero" aria-labelledby="hero-title">
  <div class="wrap">
    <img class="p-icon ic-l" src="/assets/img/{app}@2x.webp" width="96" height="96" alt="{n} app icon" fetchpriority="high"><img class="p-icon ic-d" src="/assets/img/{app}-dark@2x.webp" width="96" height="96" alt="{n} app icon">
    <p class="eyebrow">{e(n)} · {e(a["kind"])}</p>
    <h1 id="hero-title" class="h1">{e(a["h1"])}</h1>
    <p class="lede">{e(a["lede"])}</p>
    <div class="cta-row">
      {get_button(a)}
      <span class="price-note">{e(a["price_note"])}</span>
    </div>
    <div class="hero-devices">
      {img(ipad, "render-ipad", "(max-width: 860px) 86vw, 740px", ipad_alt, eager=True)}
      {img(phone, "render-phone", "(max-width: 860px) 28vw, 260px", phone_alt, eager=True)}
    </div>
  </div>
</section>

<section class="wrap" aria-label="At a glance">
  <div class="glance">
''']
    for ic, t, d in a['glance']:
        out.append(f'    <div class="gl reveal">{icon(ic, 24)}<strong>{e(t)}</strong><span>{e(d)}</span></div>\n')
    out.append('  </div>\n</section>\n')
    for i, f in enumerate(a['features']):
        sid = ' id="features"' if i == 0 else ''
        flip = ' flip' if i % 2 else ''
        halo = a['halo']
        out.append(f'''
<section{sid} class="feature" aria-labelledby="f{i+1}">
  <div class="wrap feature-grid{flip}">
    <div class="feature-copy reveal">
      <p class="kick">{e(f["kick"])}</p>
      <h2 id="f{i+1}" class="h2">{e(f["h2"])}</h2>
      <p class="sub">{e(f["sub"])}</p>
      <ul class="ticks">{ticks(f["ticks"])}</ul>
    </div>
    <div class="feature-media reveal-zoom"><div class="halo" style="background:{halo}"></div>{img(f["img"][0], "render-phone", "(max-width: 560px) 74vw, 330px", f["img"][1])}</div>
  </div>
</section>
''')
    out.append('\n<section class="wrap" aria-label="More features">\n  <div class="pair">\n')
    for c in a['pair']:
        out.append(f'''    <article class="bt reveal" style="--tint:{c["tint"]}">
      <div class="bt-copy"><p class="kick">{e(c["kick"])}</p><h3>{e(c["h3"])}</h3><p>{e(c["p"])}</p></div>
      <div class="bt-media">{img(c["img"][0], "render-phone", "(max-width: 860px) 260px, 300px", c["img"][1])}</div>
    </article>
''')
    out.append('  </div>\n</section>\n')
    s = a['screens']
    out.append(f'''
<section id="screens" class="p-dark" aria-labelledby="sc-title">
  <div class="wrap">
    <h2 id="sc-title" class="h2 reveal">{e(s["h2"])} <span class="soft">{e(s["soft"])}</span></h2>
    <p class="sub reveal">{e(s["sub"])}</p>
    <div class="dev-tabs" role="tablist" aria-label="Devices" data-tabs hidden>
''' if len(s['tabs']) > 1 else '')
    for i, t in enumerate(s['tabs'] if len(s['tabs']) > 1 else []):
        sel = 'true' if i == 0 else 'false'
        out.append(f'      <button class="dev-tab" type="button" role="tab" id="tab-{i}" aria-controls="panel-{i}" aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">{e(t[0])}</button>\n')
    if len(s['tabs']) > 1:
        out.append('    </div>\n')
    for i, t in enumerate(s['tabs']):
        label, kicker, h3, body, key, alt = t
        kind = 'watch' if '/watch-' in key else ('wide' if '/duo-flat' in key else 'tall')
        out.append(f'''    <div class="dev-panel dev-{kind}"{' role="tabpanel" id="panel-%d" aria-labelledby="tab-%d"' % (i, i) if len(s['tabs']) > 1 else ''}>
      <div class="dev-copy"><p class="bt-kicker">{e(kicker)}</p><h3>{e(h3)}</h3><p>{e(body)}</p></div>
      <div class="dev-media">{img(key, "", "(max-width: 860px) 86vw, 560px", alt)}</div>
    </div>
''')
    out.append('  </div>\n</section>\n')
    out.append(f'''
<section id="together" class="sec" aria-labelledby="tg-title">
  <div class="wrap">
    <h2 id="tg-title" class="h2 reveal">Better with <span class="soft">the rest of Hearth.</span></h2>
    <p class="sub reveal">{e(n)} shares one household with every Hearth app, so the people in your life only have to be set up once.</p>
    <div class="together">
''')
    for title, body, tag, partner in a['together']:
        icons = appicon(app, 40) + (icon('Plus', 12) + appicon(partner, 40) if partner else '')
        out.append(f'      <div class="tg reveal"><div class="tg-icons">{icons}</div><h3>{e(title)}</h3><p>{e(body)}</p><span class="plus-tag">{e(tag)}</span></div>\n')
    out.append('    </div>\n  </div>\n</section>\n')
    hp = HEARTH_PLUS
    if has_plans:
        p = a['plans']
        out.append(f'''
<section id="plans" class="sec" style="padding-top:0" aria-labelledby="pl-title">
  <div class="wrap">
    <!-- DRAFT: confirm features and prices against MONETIZATION.md before launch. -->
    <div class="plans-head">
      <h2 id="pl-title" class="h2 reveal">Free to start. <span class="soft">Plus when you want more.</span></h2>
      <div class="billing" role="group" aria-label="Billing period" data-billing hidden><button type="button" aria-pressed="true" data-period="monthly">Monthly</button><button type="button" aria-pressed="false" data-period="yearly">Yearly</button></div>
    </div>
    <div class="plans">
      <div class="plan reveal"><h3>{e(n)}</h3><p class="price">Free</p><p class="per">Forever, for the whole household</p><ul>{ticks(p["free"])}</ul></div>
      <div class="plan hi reveal"><span class="plan-badge">Most popular</span><h3>{e(n)} Plus</h3>
        <p class="price"><span data-monthly>{p["plus_monthly"]} <small>/ month</small></span><span data-yearly hidden>{p["plus_yearly"]} <small>/ year</small></span></p>
        <p class="per"><span data-monthly>or {p["plus_yearly"]} a year</span><span data-yearly hidden>Billed once a year</span></p><ul>{ticks(p["plus"])}</ul></div>
      <div class="plan reveal"><h3>Hearth+</h3>
        <p class="price"><span data-monthly>{hp["monthly"]} <small>/ month</small></span><span data-yearly hidden>{hp["yearly"]} <small>/ year</small></span></p>
        <p class="per"><span data-monthly>or {hp["yearly"]} a year</span><span data-yearly hidden>Billed once a year</span></p><ul>{ticks(["Plus in every Hearth app", "The cross-app features above", f"Lifetime option, {hp['lifetime']} once"])}</ul></div>
    </div>
    <p class="plans-note">Your own data is never behind a paywall. Subscriptions renew until canceled in Settings.</p>
  </div>
</section>
''')
    else:
        out.append(f'''
<section id="plans" class="sec" style="padding-top:0" aria-labelledby="pl-title">
  <div class="wrap">
    <!-- DRAFT: confirm prices against MONETIZATION.md before launch. -->
    <div class="hplus reveal">
      <div><h2 id="pl-title">{e(n)} Plus, or Hearth+ for every app.</h2>
        <p>{e(n)} Plus adds more to {e(n)} on its own. Hearth+ unlocks Plus in every Hearth app, plus the features that connect them, for your whole household.</p>
        <p class="fine">Your own data is never behind a paywall.</p></div>
      <div class="hplus-price"><p class="price">{hp["monthly"]} <small>/ month</small></p><p class="per">Hearth+ · or {hp["yearly"]} a year, or {hp["lifetime"]} once</p></div>
    </div>
  </div>
</section>
''')
    title, body, items = a['privacy']
    lis = ''.join(f'<li>{icon(ic, 24)}<span>{e(t)}</span></li>' for ic, t in items)
    out.append(f'''
<section class="wrap" aria-labelledby="pv-title">
  <div class="privacy-band reveal">
    <div><h2 id="pv-title">{e(title)}</h2><p>{e(body)}</p></div>
    <ul>{lis}</ul>
  </div>
</section>

<section id="faq" class="faq-sec" aria-labelledby="faq-title">
  <div class="wrap">
    <h2 id="faq-title" class="faq-title">Questions</h2>
    <div class="faq">
''')
    faqs = a['faq'] + [('Where can I get help?', 'Visit Support or write to support@hearthapps.com. A real person reads every message.')]
    for q, ans in faqs:
        ans_html = e(ans).replace('Support', '<a href="/support">Support</a>', 1).replace('support@hearthapps.com', '<a href="mailto:support@hearthapps.com">support@hearthapps.com</a>')
        out.append(f'      <details><summary>{e(q)}<span class="plus">{icon("Plus", 12)}</span></summary><div class="answer">{ans_html}</div></details>\n')
    out.append('    </div>\n')
    if a.get('disclaimer'):
        out.append(f'    <p class="disclaimer">{e(a["disclaimer"])}</p>\n')
    out.append('  </div>\n</section>\n')
    c1, c2 = a['close']
    more = ''.join(f'<a href="{page_url(o)}">{appicon(o, 64)}{NAMES[o]}</a>' for o in ORDER if o != app)
    out.append(f'''
<section class="close" aria-labelledby="cl-title">
  <div class="wrap">
    <h2 id="cl-title" class="h2 reveal">{e(c1)}<br><span class="grad">{e(c2)}</span></h2>
    <div class="cta-row">{get_button(a)}</div>
    <p class="more-label">More from Hearth</p>
    <nav class="more-apps" aria-label="More Hearth apps">{more}</nav>
  </div>
</section>

</main>
''')
    out.append(footer + '\n</body>\n</html>\n')
    os.makedirs(os.path.join(ROOT, app), exist_ok=True)
    open(os.path.join(ROOT, app, 'index.html'), 'w').write(''.join(out))

if __name__ == '__main__':
    header, footer = chrome()
    for app, a in APPS.items():
        build(app, a, header, footer)
        print('wrote', f'{app}/index.html')
