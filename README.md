# hearthapps.com

The marketing site for **Hearth** — BigTable, Suffice, Sated, Caloma and Hearken.

Plain HTML, one stylesheet and one small script. No framework and no build step:
what's in this folder is exactly what gets served.

```
index.html            Home: hero, the five apps, principles
support/index.html    Support + FAQ
privacy/index.html    Privacy Policy (one policy for all five apps)
terms/index.html      Terms of Use (one set of terms for all five apps)
404.html              Not-found page
assets/css/site.css   All styles (Apple-style type, layout, animations, breakpoints)
assets/js/site.js     Mobile menu, scroll-reveal fallback, legal-page TOC highlight
assets/img/           App icons (256 px and @2x 512 px WebP) and the social image (og.png)
assets/brand/         The Hearth mark as SVG
favicon.svg, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png, site.webmanifest
robots.txt, sitemap.xml, vercel.json
```

## Preview locally

```sh
cd ~/Developer/hearthapps
npm run dev
# open http://localhost:3000   (another port: PORT=8080 npm run dev)
```

`npm run dev` runs `tools/dev-server.mjs`, a tiny Node server with no dependencies (nothing to
install) that serves the folder the way Vercel does: clean URLs like `/privacy`, and the custom
404 page. `package.json` and `tools/` are listed in `.vercelignore`, so they never deploy.

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

## Before launch

- **App Store and TestFlight links.** BigTable links to the App Store. Suffice, Sated and Hearken
  show a blue "Join the beta on TestFlight" button plus a "How to join" link to `/beta`, the
  page with TestFlight instructions. Caloma shows "Coming soon". When an app's link changes,
  update it everywhere it appears: search the HTML files for its `testflight.apple.com/join/` link.
- **Legal review.** The Privacy Policy and Terms were drafted from the apps' code. Have them
  checked, confirm BigTable's AI provider and Sated's Apple Health behaviour, and replace
  `[STATE]` in `terms/index.html` with your governing-law state.
- **Search.** After the domain is live, add it to Google Search Console and Bing Webmaster
  Tools and submit `https://hearthapps.com/sitemap.xml`.

## Editing notes

- Brand colors live at the top of `assets/css/site.css` (`--bigtable`, `--suffice`, …).
- The nav and footer are repeated in each page — change all five HTML files when you edit them.
- Each page has its own `<title>`, description, canonical URL and Open Graph tags in `<head>`.
  The home page also carries Organization, WebSite and SoftwareApplication structured data;
  the support page carries FAQPage structured data that mirrors its FAQ — update both together.
- **Light and dark.** The sun/moon button in the nav switches appearance and remembers the choice;
  until someone picks, the site follows their device setting. Dark colors are the `:root[data-theme="dark"]`
  block at the top of `site.css`, and each app icon has a `-dark` WebP from `~/Developer/app-icons`.
- Animations respect **Reduce Motion**. Scroll reveals use CSS scroll-driven animations where
  the browser supports them and an IntersectionObserver fallback elsewhere; with JavaScript off,
  everything is simply visible.
