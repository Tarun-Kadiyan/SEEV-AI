# SEEV AI — upgraded Streamlit application

## What is included
- Separate **Individual** and **Company** workspaces, dashboards, review history, interactive Plotly charts, ranking and CSV/JSON exports.
- Skill coverage and contextual semantic matching **when the optional `sentence-transformers` package and MiniLM model are installed**.
- Automatic clearly labeled TF-IDF fallback if the semantic model is unavailable. This is **not** semantic matching; check the method label in each review.
- SQLite history saved per authenticated user in `seev.db`.
- Feedback-based suggestion prioritizer demo (`rl_engine.py`), **not** a validated reinforcement-learning hiring system.
- Fit scores are heuristic alignment estimates, **not** selection probabilities or hiring decisions.

## Install and run
1. Extract the ZIP to a new folder and open that folder in VS Code.
2. Install: `python -m pip install -r requirements.txt`
3. For real semantic embeddings, additionally install: `python -m pip install sentence-transformers`
4. Start: `python -m streamlit run app.py`
5. Sign in with an existing account if you migrated your `seev.db`, or create a new account.

First semantic-model use downloads `all-MiniLM-L6-v2` from Hugging Face; internet access and disk space are required. Without it, analysis continues in TF-IDF fallback mode. No API key is needed.

## IMPORTANT: Preserve existing accounts and history
This ZIP deliberately **does not include** `seev.db` to avoid overwriting existing accounts/history. Before replacing your current app, back up your existing project. Copy your **existing** `seev.db` into the extracted project folder (alongside `app.py`). Existing `users`, `analyses` and `feedback` tables are preserved; the code only adds read helpers to the old database module. Never overwrite your original DB with a blank one.

## Notes
- PDF extraction is text-based; scanned PDFs without selectable text require OCR separately.
- Company screening saves one analysis per resume. Dashboard rankings are based on these saved candidate reviews.
- Existing saved analyses display their legacy fields and may not contain semantic-method metadata; new analyses include that metadata.
- Human review is required for employment decisions. Scores are not calibrated against real hiring outcomes.

## New: Synthetic evaluation dataset (no API key required)
- `data/resumes.csv`: 15 completely fictional, distinct resumes (full extracted text).
- `data/job_descriptions.csv`: 6 distinct technical job descriptions.
- `data/relevance_labels.csv`: 90 illustrative, hand-authored role-based relevance labels (0=unrelated, 1=adjacent, 2=relevant, 3=strongly relevant).
- `evaluation.py`: NDCG@5 and Precision@5 evaluation using the existing analyzer.
- **Dataset Evaluation** sidebar page: run a TF-IDF baseline or optional MiniLM, view all rankings and download results.

The relevance labels are synthetic assumptions, not expert-annotated ground truth. Do not report these scores as verified model accuracy or hiring success rates. This evaluation is for educational demonstrations only and is not suitable for real hiring validation.

To run evaluation in VS Code:
`python evaluation.py`
For MiniLM (requires installation and initial model download):
`python -m pip install sentence-transformers`
`python evaluation.py --semantic`

Your existing `seev.db` is NOT included or modified. Copy your existing `seev.db` into the extracted project folder to keep your login and history.
\n\n## UI update — circular score charts and refined color system\nAll app charts have been converted to circular score indicators, including dataset evaluation (separate NDCG@5 and Precision@5), company rankings, individual review breakdown, and dashboard history. The interface uses layered blue/teal surfaces instead of flat white cards. Preserve your original `seev.db` when switching folders.\n
## Dark Orange / Black edition
Uses charcoal black surfaces, burnt orange primary accents, red secondary accents, and gold highlights. All circular graphs retain their labels and 0–100% scale. Streamlit theme configured in `.streamlit/config.toml`. To keep history, copy your old `seev.db` to the extracted folder. Restart Streamlit after replacing the project.

## Real RL implementation
An online epsilon-greedy contextual multi-armed bandit now learns which individual resume-improvement advice categories receive positive feedback. It uses new `rl_decisions` SQLite rows and per-account rewards; it does not change hiring scores. See `RL_IMPLEMENTATION.md`.
