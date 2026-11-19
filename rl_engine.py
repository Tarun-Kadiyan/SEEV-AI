"""Actual online epsilon-greedy contextual multi-armed bandit for resume-improvement advice.

Each account learns from its own explicit feedback. No hiring ranking is modified.
"""
import random
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name('seev.db')
ACTIONS = ('technical_skills', 'projects', 'experience', 'resume_tailoring')
COMPANY_ACTIONS = ('review_skill_evidence', 'technical_interview', 'request_work_samples', 'manual_profile_review')
LABELS = {
    'technical_skills': 'Develop evidence of relevant technical skills through a small, verifiable project.',
    'projects': 'Describe a role-relevant project: the problem, your tools, your contribution, and a measurable result.',
    'experience': 'Highlight relevant internships, practical work, coursework, or volunteering with concrete achievements.',
    'resume_tailoring': 'Prioritize accurate role-relevant accomplishments and use clear language that matches the job requirements.'
}
COMPANY_LABELS = {
 'review_skill_evidence': 'Review evidence of role-relevant skills in the candidate’s work history.',
 'technical_interview': 'Consider a structured, role-relevant technical assessment with human oversight.',
 'request_work_samples': 'Request a relevant portfolio or work sample for human review.',
 'manual_profile_review': 'Perform a structured manual review against the documented job requirements.'
}
EPSILON = 0.15


def context_for(result, mode='Individual'):
    """Coarse, explainable context for learning, without sensitive attributes."""
    missing = len(result.get('missing_skills') or [])
    fit = float(result.get('score') or 0)
    base = ('gaps' if missing else 'no_gaps') + ':' + ('low_fit' if fit < 60 else 'high_fit')
    return mode.lower() + ':' + base


def eligible_actions(result, mode='Individual'):
    if mode == 'Company': return COMPANY_ACTIONS
    return ACTIONS if result.get('missing_skills') else ACTIONS[1:]


def _connect():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def init_rl_db():
    with _connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS rl_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            analysis_id INTEGER NOT NULL,
            context TEXT NOT NULL,
            action TEXT NOT NULL,
            strategy TEXT NOT NULL,
            propensity REAL NOT NULL,
            reward REAL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            rewarded_at TEXT,
            UNIQUE(user_id, analysis_id)
        )""")
        con.execute('CREATE INDEX IF NOT EXISTS idx_rl_user_context ON rl_decisions(user_id,context,action)')


def action_stats(user_id, context, actions=ACTIONS):
    """Mean reward per action, from only this user's rated recommendations."""
    init_rl_db()
    with _connect() as con:
        rows=con.execute("""SELECT action, COUNT(*) AS n, AVG(reward) AS mean_reward
                            FROM rl_decisions WHERE user_id=? AND context=? AND reward IS NOT NULL
                            GROUP BY action""",(user_id,context)).fetchall()
    result={a:{'count':0,'mean_reward':0.0} for a in actions}
    for r in rows:
        if r['action'] in result: result[r['action']]={'count':int(r['n']),'mean_reward':float(r['mean_reward'])}
    return result


def _choose(stats, available, epsilon, rng):
    """Explore untried actions first; then epsilon-greedy exploitation/exploration."""
    untried=[a for a in available if stats[a]['count']==0]
    if untried:
        return rng.choice(untried),'cold_start',1/len(untried)
    if rng.random() < epsilon:
        return rng.choice(available),'explore',epsilon/len(available)
    best=max(stats[a]['mean_reward'] for a in available)
    ties=[a for a in available if stats[a]['mean_reward']==best]
    return rng.choice(ties),'exploit',(1-epsilon)/len(ties)+epsilon/len(available)


def get_or_create_recommendation(user_id, analysis_id, result, rng=None, epsilon=EPSILON, mode='Individual'):
    """Persist one action per analysis so Streamlit reruns do not resample it."""
    init_rl_db()
    with _connect() as con:
        existing=con.execute('SELECT * FROM rl_decisions WHERE user_id=? AND analysis_id=?',
                             (user_id,analysis_id)).fetchone()
    if existing:return dict(existing)
    with _connect() as con:
        analysis=con.execute('SELECT mode FROM analyses WHERE id=? AND user_id=?',(analysis_id,user_id)).fetchone()
    if analysis is None or analysis['mode'] != mode:
        raise ValueError('Analysis does not belong to this account and mode')
    context=context_for(result,mode)
    available=eligible_actions(result,mode)
    stats=action_stats(user_id,context,available)
    action,strategy,propensity=_choose(stats,available,epsilon,rng or random.Random())
    with _connect() as con:
        con.execute("""INSERT OR IGNORE INTO rl_decisions
            (user_id,analysis_id,context,action,strategy,propensity)
            VALUES (?,?,?,?,?,?)""",(user_id,analysis_id,context,action,strategy,propensity))
        row=con.execute('SELECT * FROM rl_decisions WHERE user_id=? AND analysis_id=?',
                        (user_id,analysis_id)).fetchone()
    return dict(row)


def record_reward(user_id, decision_id, rating):
    """One explicit reward per decision; feedback cannot be overwritten or double-counted."""
    mapping={'Yes':1.0,'Partly':0.5,'No':0.0}
    if rating not in mapping:raise ValueError('Feedback must be Yes, Partly, or No')
    init_rl_db()
    with _connect() as con:
        cursor=con.execute("""UPDATE rl_decisions SET reward=?, rewarded_at=datetime('now')
                              WHERE id=? AND user_id=? AND reward IS NULL""",
                           (mapping[rating],decision_id,user_id))
    return cursor.rowcount==1


def learning_summary(user_id, mode='Individual'):
    init_rl_db()
    with _connect() as con:
        rows=con.execute("""SELECT action,COUNT(*) AS rated,AVG(reward) AS avg_reward
                            FROM rl_decisions WHERE user_id=? AND context LIKE ? AND reward IS NOT NULL
                            GROUP BY action""",(user_id,mode.lower()+':%')).fetchall()
        total=con.execute('SELECT COUNT(*) FROM rl_decisions WHERE user_id=? AND context LIKE ? AND reward IS NOT NULL',(user_id,mode.lower()+':%')).fetchone()[0]
    return {'rated':total,'actions':{r['action']:{'rated':r['rated'],'average_reward':round(r['avg_reward'],3)} for r in rows}}


def recommend_learning_actions(missing_skills):
    """Legacy compatibility; static labels, not a learned RL decision."""
    actions=ACTIONS if missing_skills else ACTIONS[1:]
    return [LABELS[a] for a in actions]
