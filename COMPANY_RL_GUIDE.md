# RL in both SEEV AI portals

**Individual:** Learns from feedback on skill/project/experience/resume-tailoring suggestions.

**Company:** Learns from feedback on four human review guidance actions: verify skill evidence, structured technical interview, request work samples, and manual profile review. HR selects a candidate from the ranked list, rates the guidance (Yes=1, Partly=0.5, No=0). Ratings are stored per company account and coarse fit/skill-gap context in `rl_decisions`.

Both use online epsilon-greedy multi-armed bandits with 15% exploration. They do **not** train a candidate selection policy, change fit scores, automatically shortlist/reject applicants, or infer actual hiring outcomes. The labels measure perceived suggestion usefulness only. Results require larger real feedback evaluations.

Existing `seev.db` is preserved; the table is created additively. Individual and Company contexts are separate.
