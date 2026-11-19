# SEEV AI — real online reinforcement learning module

## Algorithm
Contextual **epsilon-greedy multi-armed bandit**, not Q-Learning, DQN, PPO, or a supervised hiring predictor. Each user and coarse context has separate empirical action reward estimates.

- Context: (skill gaps vs no gaps) × (fit below 60 vs at least 60).
- Actions: technical skills, projects, experience, resume tailoring (technical skills excluded if no skill gaps).
- Cold start: sample uniformly among actions not yet rated in that context.
- Thereafter: explore with epsilon=0.15, otherwise exploit the highest observed average reward (random tie-breaking).
- Reward: Yes=1.0, Partly=0.5, No=0.0. Each analysis generates at most one persistent decision, and each decision can receive at most one reward.
- Data: new SQLite `rl_decisions` table, created additively; existing accounts/history are not deleted.
- Learning: per account and per context; updates after feedback, affecting **future** recommendations.
- Scope: recommendation selection only. The system does not learn a candidate-ranking or hiring policy. User feedback is a subjective usefulness reward, not evidence of job success.

## How to demonstrate learning
1. Sign in to an Individual account and analyze a resume against a JD.
2. Observe the recommended improvement action and its exploration/exploitation mode.
3. Rate that specific action Yes/Partly/No; click **Train from my feedback**.
4. Analyze again with a similar JD and resume, and repeat. The bandit explores untested actions first, then increasingly favors those with better average feedback rewards, while occasionally exploring.
5. Open Dashboard → RL learning progress to see rated action counts and mean rewards.

## Running tests
`python -m unittest discover -s tests -v`

## Limitations
Small per-user feedback datasets can be noisy; the simple context buckets are coarse. Epsilon-greedy is a genuine online bandit algorithm, but it does not solve a multi-step MDP or prove recommendation effectiveness. For a defensible study, run controlled simulations and a real user study with informed consent.
