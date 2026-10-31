# hearthapps.com

The marketing site for **Hearth** — BigTable, Suffice, Sated, Caloma, Hearken, Trove and Ember.

Plain HTML, one stylesheet and one small script. No framework and no build step:
what's in this folder is exactly what gets served.

```
index.html            Home: hero, the seven apps, principles
support/index.html    Support + FAQ
privacy/index.html    Privacy Policy (one policy for all five apps)
terms/index.html      Terms of Use (one set of terms for all five apps)
404.html              Not-found page
assets/css/site.css   All styles (Apple-style type, layout, animations, breakpoints)
assets/js/site.js     Mobile menu, scroll-reveal fallback, legal-page TOC highlight
assets/js/beta.js     Beta pages: waitlist form, What's new, ?via= on TestFlight links
assets/img/           App icons (256 px and @2x 512 px WebP) and the social image (og.png)
assets/brand/         The Hearth mark as SVG
favicon.svg, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png, site.webmanifest
robots.txt, sitemap.xml, vercel.json
```

## App pages

Each app has a product page at `/<app>` (BigTable, Suffice, Sated, Caloma, Hearken, Trove), built
from one template so they stay consistent:

```sh
python3 tools/export-renders.py      # device renders from each app repo's marketing/mockups → assets/img/renders
python3 tools/build-app-pages.py     # writes <app>/index.html from tools/app_pages_data.py
python3 tools/build-beta-pages.py    # writes beta/<app>, beta/thanks, beta/confirmed and the /beta form
npm run icons && npm test
```

Edit copy and screens in `tools/app_pages_data.py`, never the generated HTML. The nav and footer
are copied from `index.html`, so change them there first. Plan prices are marked DRAFT until
they're confirmed against MONETIZATION.md.

## Beta pages and the launch waitlist

`/beta/<app>` (Suffice, Sated, Caloma, Hearken, Trove, Ember) are built by `tools/build-beta-pages.py`
from the same data (`BETA_ORDER` and `BETA_EXTRA` for Ember). They talk to hearth-api:

- "What's new this week" loads from `GET https://api.hearthapps.com/v1/beta/<app>` and stays hidden
  when it's empty or the request fails.
- "Join the beta on TestFlight" links to `https://hearthapps.com/go/tf/<app>` (plus `?via=` when the page
  was opened with one), which counts the tap and redirects. `vercel.json` rewrites `/go/*` to the API.
- The "Get notified at launch" form (on `/beta`, each beta page and each beta app's product page) posts
  to `https://api.hearthapps.com/v1/waitlist`: as JSON from `assets/js/beta.js`, or as a normal form post
  without JavaScript, which redirects to `/beta/thanks`. The confirmation email links to `/beta/confirmed`.

## Preview locally

```sh
cd ~/Developer/hearthapps
npm run dev
# open http://localhost:3000   (another port: PORT=8080 npm run dev)
```

`npm run dev` runs `tools/dev-server.mjs`, a tiny Node server with no dependencies (nothing to
install) that serves the folder the way Vercel does: clean URLs like `/privacy`, and the custom
404 page. `/go/*` redirects to api.hearthapps.com (on Vercel it's a rewrite). Development tools, package manifests and `node_modules/` are excluded from deployment.

## UI icons and tests

UI icons come from `lucide-react`, rendered into the checked-in HTML with React's static
renderer. React and Lucide are development-only dependencies: no runtime bundle, CDN, or
deployment build is needed, and icons remain visible without JavaScript.

```sh
npm ci
npm run icons        # regenerate SVGs after changing a data-lucide icon name
npm test            # theme behavior and static-icon consistency
```

Use the PascalCase Lucide component name in an SVG's `data-lucide` attribute, for example
`data-lucide="Sun"`. The renderer preserves its width, height and custom CSS classes.
The Hearth mark and app artwork are brand assets, not Lucide UI icons.

## Deploy (Vercel)

1. `npx vercel` in this folder (or push it to GitHub and import the repo in Vercel).
   Framework preset: **Other**. No build command. Output directory: `.`
2. In the project's **Domains**, add `hearthapps.com` and `www.hearthapps.com`
   (redirect `www` to the apex), then point your registrar's DNS where Vercel says.
3. `vercel.json` turns on clean URLs, security headers and image caching.

## Links for App Store Connect

| App | Support URL | Privacy Policy URL | Marketing URL |
|---|---|---|---|
| BigTable | https://hearthapps.com/support | https://hearthapps.com/privacy#bigtable | https://hearthapps.com/#bigtable |
| Suffice | https://hearthapps.com/support | https://hearthapps.com/privacy#suffice | https://hearthapps.com/#suffice |
| Sated | https://hearthapps.com/support | https://hearthapps.com/privacy#sated | https://hearthapps.com/#sated |
| Caloma | https://hearthapps.com/support | https://hearthapps.com/privacy#caloma | https://hearthapps.com/#caloma |
| Hearken | https://hearthapps.com/support | https://hearthapps.com/privacy#hearken | https://hearthapps.com/#hearken |
| Trove | https://hearthapps.com/support | https://hearthapps.com/privacy (no Trove section yet) | https://hearthapps.com/#trove |
| Ember | https://hearthapps.com/support | https://hearthapps.com/privacy (no Ember section yet) | https://hearthapps.com/#ember |

## Before launch

- **App Store and TestFlight links.** BigTable links to the App Store. Suffice, Sated, Caloma,
  Hearken, Trove and Ember show a blue "Join the beta on TestFlight" button (most with a "How to
  join" link to `/beta`, the page with TestFlight instructions).
- **Trove and Ember screens.** Their phones show HTML mocks (`.trove-mock`, `.ember-mock` in
  site.css) until they have screenshot scripts; then add them to `tools/capture-screenshots.sh`
  and swap in `<img class="shot">` like the others. When an app's link changes,
  update it everywhere it appears: search the HTML files for its `testflight.apple.com/join/` link.
- **Legal review.** The Privacy Policy, Terms and Support FAQ were checked against every app's
  code, hearth-api and HearthKit on October 19, 2026 (provider Hearth Software LLC, Utah law).
  Have a lawyer review them, and re-check them whenever an app adds a server feature, a third
  party or a permission.
- **Search.** After the domain is live, add it to Google Search Console and Bing Webmaster
  Tools and submit `https://hearthapps.com/sitemap.xml`.

## Editing notes

- Brand colors live at the top of `assets/css/site.css` (`--bigtable`, `--suffice`, …).
- The nav and footer are repeated in each page — change all six HTML files when you edit them.
- Each page has its own `<title>`, description, canonical URL and Open Graph tags in `<head>`.
  The home page also carries Organization, WebSite and SoftwareApplication structured data;
  the support page carries FAQPage structured data that mirrors its FAQ — update both together.
- **Light and dark.** The sun/moon switch in the nav changes appearance and remembers the choice;
  until someone picks, the site follows their device setting. Dark colors are the `:root[data-theme="dark"]`
  block at the top of `site.css`, and each app icon has a `-dark` WebP from `~/Developer/app-icons`.
  The new appearance reveals in a circle from the switch over 650 ms. With Reduce Motion
  enabled, or without View Transition API support, appearance changes immediately.
- Animations respect **Reduce Motion**. Scroll reveals use CSS scroll-driven animations where
  the browser supports them and an IntersectionObserver fallback elsewhere; with JavaScript off,
  everything is simply visible.
