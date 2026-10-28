#!/usr/bin/env python3
"""Turn the device renders in each app repo's marketing/mockups into web images.

    python3 tools/export-renders.py          # from ~/Developer/hearthapps

Each render is trimmed to its visible pixels, resized to two widths and saved as
WebP with transparency in assets/img/renders/<app>/. renders.json records sizes
so the HTML can carry width/height. Edit SPEC to add or swap screens.
Light renders are skipped for now: several came out blank or identical across apps.
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV = os.path.dirname(ROOT)
REPO = {'bigtable': 'bigtable-ios', 'suffice': 'suffice', 'sated': 'sated',
        'caloma': 'caloma', 'hearken': 'hearken', 'trove': 'trove'}
# device folder -> (short key, widths)
DEVICE = {
    'iPhone-18-Pro-01': ('phone-a', (360, 720)),
    'iPhone-18-Pro-02': ('phone-b', (360, 720)),
    'iPhone-18-Pro-03': ('phone-tilt', (520, 1040)),
    'iPad-Pro-12-9-01': ('ipad-a', (600, 1200)),
    'iPad-Pro-12-9-02': ('ipad-b', (720, 1440)),
    'iPhone-Duo-01': ('duo-flat', (800, 1600)),
    'iPhone-Duo-02': ('duo', (520, 1040)),
    'Apple-Watch-Ultra-01': ('watch', (280, 560)),
}
# (app, device folder, variant folder, screen)
SPEC = [
    # Home page: one phone per app (a = copy left, b = copy right) and its watch
    ('bigtable', 'iPhone-18-Pro-01', 'dark', '01-plan'),
    ('suffice', 'iPhone-18-Pro-02', 'dark', '02-budget'),
    ('sated', 'iPhone-18-Pro-01', 'dark', '01-today'),
    ('caloma', 'iPhone-18-Pro-02', 'dark', '01-home'),
    ('hearken', 'iPhone-18-Pro-01', 'dark', '02-reader'),
    ('trove', 'iPhone-18-Pro-02', 'dark', '01-home'),
    ('trove', 'iPhone-18-Pro-02', 'dark', '03-document'),
    # Home page: every screen
    ('caloma', 'iPad-Pro-12-9-01', 'dark', '01-home'),
    ('bigtable', 'iPhone-Duo-01', 'dark-landscape', '08-cook'),
    ('hearken', 'iPad-Pro-12-9-02', 'dark', '02-reader'),
    ('suffice', 'iPad-Pro-12-9-02', 'dark', '01-overview'),
    ('trove', 'iPad-Pro-12-9-02', 'dark-landscape', '03-document'),
    ('sated', 'iPhone-Duo-02', 'dark', '01-today'),
    # BigTable product page
    ('bigtable', 'iPad-Pro-12-9-02', 'dark', '01-plan'),
    ('bigtable', 'iPhone-18-Pro-03', 'dark', '01-plan'),
    ('bigtable', 'iPhone-18-Pro-01', 'dark', '08-cook'),
    ('bigtable', 'iPhone-18-Pro-02', 'dark', '02-recipes'),
    ('bigtable', 'iPhone-18-Pro-01', 'dark', '03-recipe'),
    ('bigtable', 'iPhone-18-Pro-02', 'dark', '04-grocery'),
    ('bigtable', 'iPhone-18-Pro-01', 'dark', '07-community'),
    ('bigtable', 'iPad-Pro-12-9-01', 'dark', '02-recipes'),
    ('bigtable', 'iPhone-Duo-02', 'dark', '01-plan'),
    # App product pages: Suffice
    ('suffice', 'iPhone-18-Pro-01', 'dark', '04-activity'),
    ('suffice', 'iPhone-18-Pro-01', 'dark', '07-ask'),
    ('suffice', 'iPhone-18-Pro-02', 'dark', '06-bills'),
    ('suffice', 'iPhone-18-Pro-01', 'dark', '05-transaction'),
    ('suffice', 'iPad-Pro-12-9-01', 'dark', '06-bills'),
    # Sated
    ('sated', 'iPad-Pro-12-9-02', 'dark', '03-trends'),
    ('sated', 'iPhone-18-Pro-02', 'dark', '07-add'),
    ('sated', 'iPhone-18-Pro-01', 'dark', '06-coach'),
    ('sated', 'iPhone-18-Pro-02', 'dark', '02-meal'),
    ('sated', 'iPhone-18-Pro-01', 'dark', '03-trends'),
    ('sated', 'iPad-Pro-12-9-01', 'dark', '06-coach'),
    ('sated', 'iPhone-Duo-01', 'dark-landscape', '01-today'),
    # Caloma
    ('caloma', 'iPad-Pro-12-9-02', 'dark', '01-home'),
    ('caloma', 'iPhone-18-Pro-01', 'dark', '04-kid'),
    ('caloma', 'iPhone-18-Pro-01', 'dark', '02-chores'),
    ('caloma', 'iPhone-18-Pro-02', 'dark', '07-rewards'),
    ('caloma', 'iPhone-18-Pro-02', 'dark', '05-calendar'),
    ('caloma', 'iPhone-18-Pro-01', 'dark', '08-homecare'),
    ('caloma', 'iPad-Pro-12-9-01', 'dark', '10-kidview'),
    ('caloma', 'iPhone-Duo-01', 'dark-landscape', '02-chores'),
    # Hearken
    ('hearken', 'iPhone-18-Pro-01', 'dark', '12-plans'),
    ('hearken', 'iPhone-18-Pro-02', 'dark', '02-reader'),
    ('hearken', 'iPhone-18-Pro-01', 'dark', '06-path'),
    ('hearken', 'iPhone-18-Pro-02', 'dark', '08-quiz'),
    ('hearken', 'iPhone-18-Pro-01', 'dark', '03-listen'),
    ('hearken', 'iPad-Pro-12-9-01', 'dark', '09-mapquest'),
    # Trove
    ('trove', 'iPad-Pro-12-9-02', 'dark', '01-home'),
    ('trove', 'iPhone-18-Pro-01', 'dark', '03-document'),
    ('trove', 'iPhone-18-Pro-02', 'dark', '11-add'),
    ('trove', 'iPhone-18-Pro-01', 'dark', '04-people'),
    ('trove', 'iPhone-18-Pro-02', 'dark', '06-assets'),
    ('trove', 'iPhone-18-Pro-01', 'dark', '01-home'),
    ('trove', 'iPad-Pro-12-9-01', 'dark', '04-people'),
    ('trove', 'iPhone-Duo-01', 'dark-landscape', '03-document'),
]

def main():
    out_root = os.path.join(ROOT, 'assets', 'img', 'renders')
    manifest_path = os.path.join(out_root, 'renders.json')
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    total = 0
    for app, dev, variant, screen in SPEC:
        src = os.path.join(DEV, REPO[app], 'marketing', 'mockups', dev, variant, screen + '.png')
        key, widths = DEVICE[dev]
        name = f"{key}-{screen.split('-', 1)[1]}"
        if f'{app}/{name}' in manifest and all(os.path.exists(os.path.join(out_root, app, f'{name}-{w}.webp')) for w in widths):
            continue
        im = Image.open(src).convert('RGBA')
        box = im.getchannel('A').point(lambda p: 255 if p > 8 else 0).getbbox()
        im = im.crop(box)
        os.makedirs(os.path.join(out_root, app), exist_ok=True)
        for w in widths:
            w = min(w, im.width)
            h = round(im.height * w / im.width)
            path = os.path.join(out_root, app, f'{name}-{w}.webp')
            im.resize((w, h), Image.LANCZOS).save(path, 'WEBP', quality=82, method=6)
            total += os.path.getsize(path)
        manifest[f'{app}/{name}'] = {'w': widths[0], 'h': round(im.height * widths[0] / im.width),
                                    'widths': list(widths), 'source': f'{REPO[app]}/marketing/mockups/{dev}/{variant}/{screen}.png'}
        print(f'{app}/{name}  {widths}  {im.size}', flush=True)
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=1, sort_keys=True)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print(f'{len(SPEC)} renders, {total / 1e6:.1f} MB total')

if __name__ == '__main__':
    main()
