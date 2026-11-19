"""Transparent editorial checks, not an AI authorship detector."""
import re
from collections import Counter

PHRASES = ('results-driven','detail-oriented','highly motivated','dynamic professional','proven track record','passionate about','excellent communication skills','team player','fast-paced environment','leveraging cutting-edge','go above and beyond','self-starter')

def review_writing(text):
    normalized=' '.join(text.casefold().split())
    chunks=[x.strip() for x in re.split(r'\n+|(?<=[.!?])\s+',text) if len(x.split())>=5]
    hits={p:len(re.findall(r'(?<!\w)'+re.escape(p)+r'(?!\w)',normalized)) for p in PHRASES}
    hits={p:n for p,n in hits.items() if n}
    flagged=sum(any(p in x.casefold() for p in hits) for x in chunks)
    repeated=sum(n-1 for n in Counter(' '.join(x.casefold().split()) for x in chunks).values() if n>1)
    tips=[]
    if hits: tips.append('Replace broad claims with specific responsibilities, tools and examples you can verify.')
    if repeated: tips.append('Remove repeated statements and use the space for distinct achievements.')
    tips.append('For each achievement, describe what you did, how you did it, and the outcome if known. Never invent metrics or experience.')
    return {'generic_line_pct':round(100*flagged/len(chunks),1) if chunks else None,'lines_reviewed':len(chunks),'phrases':hits,'repeated_lines':repeated,'tips':tips,'method':'Editorial phrase checklist v1; AI authorship unknown'}

def writing_pct(result):
    return result.get('writing_review',{}).get('generic_line_pct')
