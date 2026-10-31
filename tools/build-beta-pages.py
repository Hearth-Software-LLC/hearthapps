#!/usr/bin/env python3
"""Build the beta funnel pages from tools/app_pages_data.py.

    python3 tools/build-beta-pages.py && npm run icons

Writes:
  beta/<app>/index.html   one page per app in BETA_ORDER (hero, what testers get,
                          "What's new this week", the TestFlight button, the launch waitlist form)
  beta/thanks/index.html  where the API sends a form post without JavaScript (?status=invalid on a bad request)
  beta/confirmed/index.html  where the confirmation email's link lands (?apps=… or ?status=expired)
and refreshes the waitlist form between the <!-- waitlist-form --> markers in beta/index.html.

Copy lives in tools/app_pages_data.py (APPS, BETA_ORDER, BETA_EXTRA). The nav and footer are
copied from index.html; the form markup comes from build-app-pages.py so every form matches.
The behavior (fetch, What's new, ?via=) is in assets/js/beta.js. The API contract is in the
hearth-api repo's beta funnel notes: POST /v1/waitlist, GET /v1/beta/<app>, /go/tf/<app>.
"""
import html, importlib.util, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from app_pages_data import APPS, BETA_ORDER, BETA_EXTRA

spec = importlib.util.spec_from_file_location('build_app_pages', os.path.join(HERE, 'build-app-pages.py'))
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

ROOT = B.ROOT
e = html.escape
TF_GO = 'https://hearthapps.com/go/tf/'


def app_data(app):
    if app in APPS:
        a = dict(APPS[app]); a['strong'] = B.STRONG[app]; a['product'] = True
        return a
    a = dict(BETA_EXTRA[app]); a['product'] = False
    return a


def head(title, description, path, theme=None, noindex=False, og=True):
    meta_theme = (f'<meta name="theme-color" content="{theme}">' if theme else
                  '<meta name="theme-color" content="#FBFBFD" media="(prefers-color-scheme: light)">\n'
                  '<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">')
    robots = '\n<meta name="robots" content="noindex">' if noindex else ''
    ogs = f'''
<meta property="og:type" content="website">
<meta property="og:site_name" content="Hearth">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="https://hearthapps.com{path}">
<meta property="og:image" content="https://hearthapps.com/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">''' if og else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">{robots}
<link rel="canonical" href="https://hearthapps.com{path}">
{meta_theme}
<meta name="color-scheme" content="light dark">
<script>(function(){{var t;try{{t=localStorage.getItem('hearth-theme')}}catch(e){{}}var d=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;document.documentElement.setAttribute('data-theme',d?'dark':'light')}})();</script>{ogs}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/css/site.css">
<script src="/assets/js/site.js" defer></script>
<script src="/assets/js/beta.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''


def tf_button(app):
    return (f'<a class="store beta" href="{TF_GO}{app}" data-tf rel="noopener"><img class="store-icon" src="/assets/img/testflight-app-icon.webp" '
            'width="32" height="32" alt="" decoding="async"><span><small>Join the beta on</small>TestFlight</span></a>')


EMBER_MOCK = '''<div class="stage beta-stage">
      <div class="halo" style="background:#FFB27A"></div>
      <div class="phone">
        <div class="screen mock ember-mock" role="img" aria-label="Ember answering a spoken question about dinner and the grocery budget">
          <div class="em-orb" aria-hidden="true"><i></i><i></i><i></i></div>
          <p class="em-q">“What’s for dinner, and are we OK on groceries?”</p>
          <div class="em-a">
            <p>Tacos tonight — everyone’s eating. You have <b>$142</b> left of this month’s grocery budget.</p>
            <div class="em-src"><span style="background:#D9472B"></span>BigTable<span style="background:#1E9E6A"></span>Suffice</div>
          </div>
          <div class="em-mic"><svg data-lucide="Mic" width="24" height="24"></svg></div>
          <div class="island"></div>
        </div>
      </div>
    </div>'''


def build_app(app, header, footer):
    a = app_data(app); n = a['name']
    path = f'/beta/{app}'
    desc = f'Try {n} before it reaches the App Store. Join the free beta on TestFlight, or leave your email to hear when it launches.'
    out = [head(f'{n} beta — Hearth', desc, path, theme=a['strong']), header]
    if a['product']:
        ipad, phone, ipad_alt, phone_alt = a['hero']
        devices = f'''<div class="hero-devices">
      {B.img(ipad, "render-ipad", "(max-width: 860px) 86vw, 740px", ipad_alt, eager=True)}
      {B.img(phone, "render-phone", "(max-width: 860px) 28vw, 260px", phone_alt, eager=True)}
    </div>'''
    else:
        devices = EMBER_MOCK
    glance = ''.join(f'    <div class="gl reveal">{B.icon(ic, 24)}<strong>{e(t)}</strong><span>{e(d)}</span></div>\n' for ic, t, d in a['glance'])
    more = f'\n  <p class="beta-more"><a href="/{app}">See everything {e(n)} does</a></p>' if a['product'] else ''
    sub = (f'Rather wait for the App Store? Leave your email and we’ll tell you when {e(n)} is out.')
    form = B.waitlist_form(path, [app], 'Get notified at launch', sub)
    disclaimer = f'\n  <p class="disclaimer">{e(a["disclaimer"])}</p>' if a.get('disclaimer') else ''
    out.append(f'''
<main id="main" class="product beta-page" style="--accent:var(--{app});--accent-ink:var(--{app}-ink);--accent-strong:{a["strong"]}">

<section id="top" class="p-hero" aria-labelledby="hero-title">
  <div class="wrap">
    <img class="p-icon ic-l" src="/assets/img/{app}@2x.webp" width="96" height="96" alt="{n} app icon" fetchpriority="high"><img class="p-icon ic-d" src="/assets/img/{app}-dark@2x.webp" width="96" height="96" alt="{n} app icon">
    <p class="eyebrow">{e(n)} · Public beta</p>
    <h1 id="hero-title" class="h1">{e(a["h1"])}</h1>
    <p class="lede">{e(a["lede"])}</p>
    <div class="cta-row">
      {tf_button(app)}
      <a class="btn btn-ghost" href="#notify">Get notified at launch</a>
    </div>
    <p class="price-note">Free on TestFlight</p>
    {devices}
  </div>
</section>

<section class="wrap" aria-labelledby="get-title">
  <h2 id="get-title" class="beta-h2 reveal">What testers get</h2>
  <div class="glance">
{glance}  </div>{more}
</section>

<section class="wrap beta-sec" aria-labelledby="wn-title" data-whats-new="{app}" hidden>
  <div class="wn">
    <h2 id="wn-title">What’s new this week</h2>
    <ul></ul>
    <p class="wn-date" hidden></p>
  </div>
</section>

<section id="notify" class="wrap beta-sec" aria-labelledby="wl-title">
  {form}
</section>

<section class="wrap" aria-label="How to join">
  <p class="beta-help">New to TestFlight? It’s Apple’s free app for trying apps before they launch. Install it, then tap <strong>Join the beta</strong> on your iPhone or iPad. <a href="/beta">Step-by-step help</a></p>{disclaimer}
</section>

</main>
''')
    out.append(footer + '\n</body>\n</html>\n')
    write(f'beta/{app}/index.html', ''.join(out))


STATUS_PAGES = {
    'thanks': dict(
        title='Check your email — Hearth', path='/beta/thanks',
        desc='Confirm your email to hear when a Hearth app launches.',
        blocks=[
            # Without JavaScript only "default" shows, so it has to read right either way.
            ('default', False, 'Check your email.', 'If your address was right, we just sent you a link to confirm. Nothing there in a few minutes? Check your spam folder, or go back and try again.', ('/beta', 'Back to the betas')),
            ('ok', True, 'Check your email to confirm.', 'We just sent you a link. Tap it to confirm, and we’ll email you once more when the app launches.', ('/beta', 'Back to the betas')),
            ('invalid', True, 'That didn’t go through.', 'Something in the form wasn’t right, usually a typo in the email address.', ('/beta#notify', 'Go back and try again')),
        ]),
    'confirmed': dict(
        title='You’re on the list — Hearth', path='/beta/confirmed',
        desc='You’ll hear from us once, when the app launches.',
        blocks=[
            ('default', False, 'You’re on the list.', 'We’ll email you once, when it launches. Nothing else. If the page said your link expired, sign up again on the beta page.', ('/beta', 'Back to the betas')),
            ('ok', True, 'You’re on the list.', 'We’ll email you once, when it launches. Nothing else.', ('/beta', 'Back to the betas')),
            ('expired', True, 'That link has expired.', 'Confirmation links last 7 days. Sign up again and we’ll send you a new one.', ('/beta#notify', 'Sign up again')),
        ]),
}


def build_status(kind, header, footer):
    p = STATUS_PAGES[kind]
    out = [head(p['title'], p['desc'], p['path'], noindex=True, og=False), header, '\n<main id="main">\n']
    out.append(f'<section class="page-hero beta-status" data-beta-status="{kind}">\n  <div class="wrap">\n')
    for state, hidden, h1, body, (href, label) in p['blocks']:
        hid = ' hidden' if hidden else ''
        out.append(f'''    <div class="bs-block" data-state="{state}"{hid}>
      <p class="eyebrow">Hearth betas</p>
      <h1 class="h1">{e(h1)}</h1>
      <p class="lede" data-lede>{e(body)}</p>
      <div class="cta-row"><a class="btn btn-dark" href="{href}"{' data-back' if state == 'invalid' else ''}>{e(label)}</a></div>
    </div>
''')
    out.append('  </div>\n</section>\n</main>\n')
    out.append(footer + '\n</body>\n</html>\n')
    write(f'beta/{kind}/index.html', ''.join(out))


def refresh_beta_index():
    path = os.path.join(ROOT, 'beta/index.html')
    s = open(path).read()
    start, end = '<!-- waitlist-form -->', '<!-- /waitlist-form -->'
    if start not in s:
        sys.exit('beta/index.html is missing the <!-- waitlist-form --> markers')
    sub = 'Rather wait for the App Store? Pick the apps you’re waiting for, and we’ll tell you when each one launches.'
    form = B.waitlist_form('/beta', BETA_ORDER, 'Get notified at launch', e(sub),
                           note='We’ll email you once to confirm, and once when each app you chose launches. Nothing else.')
    s = s[:s.index(start) + len(start)] + '\n  ' + form + '\n  ' + s[s.index(end):]
    open(path, 'w').write(s)
    print('refreshed beta/index.html (waitlist form)')


def write(rel, text):
    os.makedirs(os.path.dirname(os.path.join(ROOT, rel)), exist_ok=True)
    open(os.path.join(ROOT, rel), 'w').write(text)
    print('wrote', rel)


if __name__ == '__main__':
    header, footer = B.chrome()
    header = header.replace('href="/beta">', 'href="/beta" aria-current="page">')
    for app in BETA_ORDER:
        build_app(app, header, footer)
    for kind in STATUS_PAGES:
        build_status(kind, header, footer)
    refresh_beta_index()
