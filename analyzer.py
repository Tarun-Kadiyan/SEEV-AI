"""Explainable skill coverage plus optional sentence-embedding semantic similarity."""
from writing_review import review_writing
import re
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = ['python','java','c++','c','sql','mysql','postgresql','mongodb','excel','power bi','tableau','machine learning','deep learning','artificial intelligence','nlp','natural language processing','data analysis','data visualization','statistics','pandas','numpy','scikit-learn','tensorflow','pytorch','streamlit','flask','django','fastapi','html','css','javascript','react','node.js','git','github','docker','aws','azure','linux','communication','leadership','teamwork','problem solving','project management','agile','rest api','reinforcement learning','spark','etl','data cleaning','data modeling','dashboards','business intelligence','reporting','data engineering','cloud computing','kubernetes','figma','customer service','recruitment','hr analytics']
ALIASES = {'power bi':['powerbi'], 'javascript':['js'], 'scikit-learn':['sklearn'], 'postgresql':['postgres'], 'machine learning':['ml'], 'natural language processing':['nlp'], 'artificial intelligence':['ai'], 'rest api':['restful api'], 'excel':['ms excel','microsoft excel']}

def clean(text):
    return re.sub(r'\s+', ' ', (text or '').lower()).strip()

def extract_skills(text):
    t=clean(text)
    found=[]
    for skill in SKILLS:
        names=[skill]+ALIASES.get(skill,[])
        if any(re.search(r'(?<![a-z0-9+#])'+re.escape(s)+r'(?![a-z0-9+#])',t) for s in names):
            found.append(skill)
    return sorted(set(found))

@lru_cache(maxsize=1)
def _embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def text_similarity(resume_text,jd_text,semantic=True):
    if semantic:
        try:
            embeddings=_embedding_model().encode([resume_text[:12000],jd_text[:12000]],normalize_embeddings=True)
            value=float(embeddings[0] @ embeddings[1])
            return round(max(0,min(100,value*100)),1),'Semantic embeddings (MiniLM)'
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            # Remain operational offline / without the optional model package.
            pass
    try:
        matrix=TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=8000).fit_transform([resume_text,jd_text])
        return round(float(cosine_similarity(matrix[0:1],matrix[1:2])[0][0])*100,1),'TF-IDF fallback'
    except ValueError:
        return 0.0,'TF-IDF fallback'

def analyze_resume(resume_text,jd_text,semantic=True):
    have=set(extract_skills(resume_text)); need=set(extract_skills(jd_text))
    matched=sorted(have & need); missing=sorted(need-have)
    skill_score=100*len(matched)/len(need) if need else 0.0
    semantic_score, method=text_similarity(resume_text,jd_text,semantic)
    score=round(.55*skill_score+.45*semantic_score if need else semantic_score,1)
    tier='Strong alignment' if score>=75 else 'Moderate alignment' if score>=50 else 'Limited alignment'
    tips=[]
    if missing: tips.append('If you have these skills, demonstrate them with concrete evidence: '+', '.join(missing[:8])+'.')
    if not re.search(r'\bprojects?\b',clean(resume_text)): tips.append('Add a relevant project with tools, responsibilities and measurable results.')
    if not re.search(r'\b(internship|experience|employment|worked)\b',clean(resume_text)): tips.append('Highlight relevant practical work, internships or volunteer experience where applicable.')
    tips.append('Tailor your achievements to the role using accurate, specific examples; never claim skills you do not have.')
    return {'writing_review':review_writing(resume_text),'score':score,'skill_score':round(skill_score,1),'text_score':semantic_score,'semantic_score':semantic_score,'matching_method':method,'matched_skills':matched,'missing_skills':missing,'jd_skills':sorted(need),'resume_skills':sorted(have),'recommendation':tier,'recommendations':tips}

def analyze_batch(resumes,jd_text,semantic=True):
    return [(name,analyze_resume(text,jd_text,semantic)) for name,text in resumes]
