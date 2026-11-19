"""Persistent, account-scoped recruitment campaigns."""
from writing_review import writing_pct
import hashlib
import json
from database import connect

def init_campaigns():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS campaigns (
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
          jd TEXT NOT NULL, method TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS campaign_candidates (
          campaign_id INTEGER NOT NULL, digest TEXT NOT NULL, analysis_id INTEGER NOT NULL,
          PRIMARY KEY(campaign_id,digest), UNIQUE(analysis_id),
          FOREIGN KEY(campaign_id) REFERENCES campaigns(id),
          FOREIGN KEY(analysis_id) REFERENCES analyses(id))""")

def create_campaign(uid,title,jd,method):
    if not title.strip() or len(jd.strip())<40 or method not in ('Semantic embeddings (MiniLM)','TF-IDF fallback'):
        raise ValueError('Invalid campaign settings')
    with connect() as c:
        return c.execute('INSERT INTO campaigns(user_id,title,jd,method) VALUES(?,?,?,?)',
                         (uid,title.strip(),jd.strip(),method)).lastrowid

def campaigns(uid):
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT * FROM campaigns WHERE user_id=? ORDER BY id DESC',(uid,))]

def digest(text):
    return hashlib.sha256(' '.join(text.casefold().split()).encode()).hexdigest()

def existing_digests(uid,cid):
    with connect() as c:
        return {r[0] for r in c.execute('SELECT cc.digest FROM campaign_candidates cc JOIN campaigns p ON p.id=cc.campaign_id WHERE p.id=? AND p.user_id=?',(cid,uid))}

def add_results(uid,cid,results):
    """Atomically save new analyses and campaign memberships; reject mixed methods."""
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        p=c.execute('SELECT * FROM campaigns WHERE id=? AND user_id=?',(cid,uid)).fetchone()
        if not p: raise ValueError('Campaign unavailable')
        if any(r['matching_method']!=p['method'] for _,_,r in results):
            raise ValueError('Matching method changed. No candidates saved; restore the campaign model or create a new campaign.')
        added=0
        for name,h,r in results:
            if c.execute('SELECT 1 FROM campaign_candidates WHERE campaign_id=? AND digest=?',(cid,h)).fetchone(): continue
            aid=c.execute("""INSERT INTO analyses(user_id,mode,filename,job_title,score,jd_text,result_json,created_at)
              VALUES(?,'Company',?,?,?,?,?,datetime('now'))""",
              (uid,name,p['title'],r['score'],p['jd'],json.dumps(r))).lastrowid
            c.execute('INSERT INTO campaign_candidates VALUES(?,?,?)',(cid,h,aid))
            added+=1
        return added

def ranking(uid,cid):
    with connect() as c:
        rows=c.execute("""SELECT a.* FROM analyses a JOIN campaign_candidates cc ON cc.analysis_id=a.id
             JOIN campaigns p ON p.id=cc.campaign_id WHERE p.id=? AND p.user_id=? AND a.user_id=?
             ORDER BY a.score DESC,a.id ASC""",(cid,uid,uid)).fetchall()
    out=[]
    for i,a in enumerate(rows,1):
        r=json.loads(a['result_json'])
        out.append({'Rank':i,'Analysis ID':a['id'],'Candidate':a['filename'],'Role':a['job_title'],
                    'Fit score':a['score'],'Generic wording %':writing_pct(r),'Skill coverage':r['skill_score'],'Text alignment':r['semantic_score'],
                    'Missing skills':', '.join(r['missing_skills'])})
    return out
