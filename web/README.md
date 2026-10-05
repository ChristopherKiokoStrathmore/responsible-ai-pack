# Web demo

Next.js App Router. The write-up is the site root. The interactive review is `/demo`.

JSON in `data/` for the articles, and figures in `public/figures/`, are byte copies of the committed `reports/` and `assets/` files. `data/holdout_scores.json` is the held-out gender, SeniorCitizen, label, and pinned-model probability, written by `scripts/export_demo_scores.py`, so the cutoff control can recompute rates. It is checked against `reports/fairness.json`.

```bash
npm install
npm test
npm run build
```

Do not add a metric that is not already in those reports or in `MODEL_CARD.md`.

Optional: set `NEXT_PUBLIC_SITE_URL` to the deployment origin so Open Graph image URLs resolve. On Vercel the app falls back to `VERCEL_URL`.

Live demo: [https://responsible-ai-pack.vercel.app/demo](https://responsible-ai-pack.vercel.app/demo)
