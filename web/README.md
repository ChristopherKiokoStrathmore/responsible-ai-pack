# Web demo

Next.js App Router reading of the pinned churn model. JSON in `data/` and figures in `public/figures/` are byte copies of the committed `reports/` and `assets/` files, so the app can deploy with the Vercel **Root Directory** set to `web`.

```bash
npm install
npm run build
```

Do not add a metric that is not already in those reports or in `MODEL_CARD.md`.

Optional: set `NEXT_PUBLIC_SITE_URL` to the deployment origin so Open Graph image URLs resolve. On Vercel the app falls back to `VERCEL_URL`.

Live demo: placeholder. Put the deployment URL in the repository README after the first publish.
