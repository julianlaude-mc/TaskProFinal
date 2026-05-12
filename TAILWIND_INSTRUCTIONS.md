Tailwind setup and build instructions

This project uses Tailwind CSS via a compiled CSS file (recommended for production) with a CDN fallback for prototyping.

Files created by the setup
- assets/css/input.css         # Tailwind entry file (@tailwind base; @tailwind components; @tailwind utilities)
- tailwind.config.js          # Tailwind config (content globs)
- postcss.config.js           # PostCSS config (tailwindcss + autoprefixer)
- package.json                # npm scripts: build:css and watch:css
- static/css/custom.css       # Project custom styles extracted from inline <style>

How to build locally (macOS / zsh)
1. Install node and npm if not already installed (recommended Node 18+).
   https://nodejs.org/

2. From project root, install dependencies:

```bash
npm install
```

3. Build the compiled Tailwind CSS (one-time before production):

```bash
npm run build:css
```

This produces `static/css/tailwind.css` (minified). The template attempts to load this file first and falls back to the CDN if it's not present.

4. During development, keep Tailwind watching for changes:

```bash
npm run watch:css
```

This watches your templates and JS (per `tailwind.config.js` content globs) and rebuilds `static/css/tailwind.css` on change.

How templates reference Tailwind
- The base template (`templates/proponent/base.html`) dynamically inserts a `<link>` to `{% static 'css/tailwind.css' %}`. If the link fails to load (e.g., not built yet), the page will automatically load the Tailwind CDN script as a fallback.
- The project's custom CSS (`static/css/custom.css`) is loaded after Tailwind so it can override styles.

Notes
- For production, ensure you run `npm run build:css` as part of your build/deploy pipeline (CI or release script). The CDN fallback is intended for local prototyping only.
- If you add more template folders or JS that contains Tailwind classes, update `tailwind.config.js` content globs so unused classes are purged properly.
- Do not commit `node_modules` to source control; add to `.gitignore` if needed.

If you want, I can also:
- Move other inline CSS into `static/css/custom.css` (already done for the base template's large style block).
- Hook the build step into your CI pipeline or add a Makefile target to run the build.
