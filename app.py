"""SEEV AI | Resume-to-role fit review for individuals and recruitment teams."""
from writing_review import review_writing, writing_pct
import io
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from analyzer import analyze_resume, analyze_batch
from database import (init_db,create_user,authenticate_user,save_analysis,
                      get_history_details,get_analysis_details,save_feedback)
from utils import extract_text
from rl_engine import (init_rl_db, get_or_create_recommendation, record_reward,
                       learning_summary, LABELS, COMPANY_LABELS, EPSILON)

load_dotenv()
st.set_page_config(page_title='SEEV | Resume Intelligence',page_icon='◈',layout='wide',initial_sidebar_state='expanded')
init_db()
init_rl_db()

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{color-scheme:dark}
html,body,.stApp{font-family:'DM Sans',sans-serif!important;color:#f2f2f4!important}
.stApp{background:radial-gradient(ellipse at 95% 2%,#371c18 0%,transparent 34%),radial-gradient(ellipse at 20% 85%,#23171e 0%,transparent 36%),#0d0e13!important}
[data-testid="stHeader"]{background:#0d0e13e8!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#15151d 0%,#1c151b 60%,#28191b 100%)!important;border-right:1px solid #3b2a30!important}
[data-testid="stSidebar"] *{color:#f3e9e9!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:7px 0}
.block-container{max-width:1480px;padding-top:1.7rem;padding-bottom:4rem}
h1,h2,h3{font-family:Manrope,sans-serif!important;color:#fff3ee!important;letter-spacing:-.035em}
p,li,span,label{line-height:1.5}
[data-testid="stMarkdownContainer"] p{color:#e0d9db!important}
[data-testid="stMetric"]{background:linear-gradient(145deg,#22212b,#302126)!important;padding:18px 21px;border:1px solid #49343a;border-radius:16px;box-shadow:0 8px 22px #00000033}
[data-testid="stMetricLabel"]{color:#d0bfc3!important;font-weight:600}
[data-testid="stMetricValue"]{color:#ff9b51!important;font-family:Manrope,sans-serif}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(110deg,#ed6a25,#d74737)!important;color:#fff!important;border:1px solid #f0824c!important}
div.stButton>button,div.stFormSubmitButton>button,div.stDownloadButton>button{border-radius:11px;min-height:2.65rem;font-weight:650}
div.stButton>button:hover,div.stDownloadButton>button:hover{border-color:#ff934b!important;color:#ffb174!important}
[data-testid="stFileUploader"]{border:1px dashed #8d534a!important;background:#231e26!important;border-radius:13px;padding:9px}
[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input{background:#211f29!important;color:#fff0e8!important;border:1px solid #50414a!important}
.hero{padding:31px 36px;background:linear-gradient(110deg,#211c26 0%,#402225 60%,#9c3c24 100%);border:1px solid #7e4038;border-radius:20px;margin-bottom:22px;box-shadow:0 13px 28px #0000004a}
.hero h1{color:#fff5ee!important;font-size:2.25rem;margin:4px 0 10px}
.hero p{color:#f1d7d2!important;max-width:800px;font-size:1rem}
.eyebrow{color:#ffb56d!important;font-size:.78rem;letter-spacing:.14em;font-weight:800}
.panel{background:linear-gradient(130deg,#23212c,#302126)!important;border:1px solid #49343a;border-radius:16px;padding:21px 23px;margin-bottom:14px}
.panel h3{margin:0 0 8px;color:#ffe8da!important}
.panel p{margin:0;color:#d8c5c8!important}
.note{padding:12px 16px;border-left:4px solid #f47734;background:#35231f;border-radius:8px;color:#ffe1cb;margin:13px 0}
[data-testid="stDataFrame"]{border-radius:13px;overflow:hidden}
[data-testid="stAlert"]{border-radius:12px}
[data-testid="stExpander"]{background:#24202a!important;border:1px solid #49353c!important;border-radius:12px}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#49343a!important}
div[data-testid="stPlotlyChart"]{background:linear-gradient(145deg,#211e29,#2c2027)!important;border:1px solid #49343a;border-radius:16px;padding:10px}
[data-testid="stSidebar"] button{color:#fff1e7!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"]>div,
[data-testid="stAppViewContainer"] [data-baseweb="input"]>div{background:#211f29!important;color:#fff2eb!important;border-color:#514047!important}
[data-testid="stAppViewContainer"] [data-baseweb="select"] *{color:#f7e9e4!important}
[data-testid="stAppViewContainer"] [data-testid="stCheckbox"] label p{color:#e8d7d5!important}
[data-testid="stTabs"] button{color:#dfc3c2!important}
[data-testid="stTabs"] button[aria-selected="true"]{color:#ffab6a!important}
hr{border-color:#46333a!important}

/* High contrast controls, including light-theme fallback */
.stApp [data-testid="stExpander"] summary {background:#302630!important;color:#fff2eb!important;border-radius:10px;}
.stApp [data-testid="stExpander"] summary * {color:#fff2eb!important;}
.stApp button[data-testid^="stBaseButton"], .stApp div.stButton>button,
.stApp div.stFormSubmitButton>button,.stApp div.stDownloadButton>button {
background:#38262b!important;color:#fff2eb!important;border:1px solid #a96648!important;}
.stApp button[data-testid^="stBaseButton"] *, .stApp div.stButton>button *,
.stApp div.stFormSubmitButton>button *, .stApp div.stDownloadButton>button * {color:inherit!important;}
.stApp button[data-testid*="Primary"], .stApp button[kind="primary"], .stApp button[kind="primaryFormSubmit"] {
background:#a83d19!important;color:#ffffff!important;}
.stApp button:disabled {opacity:.65!important;}
.stApp [data-baseweb="select"] > div {background:#25212b!important;color:#fff2eb!important;}
.stApp [data-baseweb="select"] * {color:#fff2eb!important;}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"] {background:#29232d!important;color:#fff2eb!important;}
[role="option"] * {color:#fff2eb!important;}
[role="option"]:hover, [role="option"][aria-selected="true"] {background:#63392d!important;}
.stApp [data-testid="stAlert"], .stApp [data-testid="stAlertContainer"], .stApp [data-baseweb="notification"] {
background:#302630!important;color:#fff2eb!important;border-radius:10px;}
.stApp [data-testid="stAlert"] *, .stApp [data-testid="stAlertContainer"] * {color:#fff2eb!important;}
.stApp [data-testid="stFileUploaderDropzone"] {background:#29232d!important;color:#fff2eb!important;}
.stApp [data-testid="stFileUploaderDropzone"] * {color:#fff2eb!important;}
.stApp input::placeholder,.stApp textarea::placeholder {color:#bfb0b8!important;opacity:1;}

</style>
''',unsafe_allow_html=True)


# Consistent, readable circular charts for all score and evaluation views.
DONUT_COLORS=['#ff8a3d','#ef4c50','#e6b65c','#ba70db','#ff6f61','#f4a261','#b85b81']

def circular_comparison(items):
    """Independent percentage rings on a shared 0–100 scale."""
    fig=go.Figure()
    n=len(items)
    for i,(label,value,color) in enumerate(items):
        value=max(0.,min(100.,float(value)))
        radius=1-i*0.23
        inner=radius-0.17
        inset=(1-radius)/2
        fig.add_trace(go.Pie(
            values=[value,100-value],labels=[str(label),'Remaining'],
            hole=inner/radius,sort=False,direction='clockwise',rotation=0,
            domain=dict(x=[inset,1-inset],y=[inset,1-inset]),
            marker=dict(colors=[color,'#342b32'],line=dict(width=0)),
            textinfo='none',showlegend=False,
            hovertemplate=f'{label}: {value:.1f}%<extra></extra>'))
    fig.add_annotation(x=.5,y=.5,text='<b>0–100%</b>',showarrow=False,
        font=dict(size=18,color='#fff2e8'))
    fig.update_layout(height=310,margin=dict(l=12,r=12,t=12,b=12),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans',color='#f5e8e5'))
    return fig

def circular_group(items, columns=3):
    """One compact chart and an aligned legend, never one chart per record."""
    items=list(items)[:3]
    if not items: return
    counter=st.session_state.get('_seev_chart_counter',0)+1
    st.session_state['_seev_chart_counter']=counter
    chart,legend=st.columns([1,1])
    with chart:
        st.plotly_chart(circular_comparison(items),use_container_width=True,
            key=f'seev_comparison_{counter}',config={'displayModeBar':False})
    with legend:
        st.caption('Independent scores · each ring is out of 100%')
        for label,value,color in items:
            import html
            safe=html.escape(str(label))
            st.markdown(f'<div style="padding:12px 0;border-bottom:1px solid #40353d;display:flex;align-items:center;gap:10px"><span style="color:{color};font-size:20px">●</span><span style="flex:1;color:#f5e8e5">{safe}</span><strong style="color:{color};font-size:21px">{float(value):.1f}%</strong></div>',unsafe_allow_html=True)

NOTICE='Scores estimate resume-to-job-description alignment, not hiring probability or a decision to hire. Human review is essential.'

def header(kicker,title,subtitle):
    st.markdown(f'<div class="hero"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)

def signin():
    header('WELCOME TO SEEV','Better insight. Clearer decisions.','Review role alignment, find skill gaps, and track screening results in one place.')
    a,b=st.tabs(['Sign in','Create an account'])
    with a:
        with st.form('login'):
            email=st.text_input('Email',key='login_email'); password=st.text_input('Password',type='password',key='login_password')
            submit=st.form_submit_button('Sign in',type='primary')
        if submit:
            user=authenticate_user(email,password)
            if user: st.session_state.user=user; st.rerun()
            else: st.error('Incorrect email or password.')
    with b:
        with st.form('register'):
            name=st.text_input('Full name'); email=st.text_input('Email',key='reg_email')
            role=st.selectbox('Account type',['Individual','Company']); company=st.text_input('Company / team name (optional)')
            pw=st.text_input('Create password',type='password'); confirm=st.text_input('Confirm password',type='password')
            submit=st.form_submit_button('Create account',type='primary')
        if submit:
            if not name.strip() or '@' not in email or len(pw)<6: st.error('Enter a name, valid email and password with at least 6 characters.')
            elif pw!=confirm: st.error('Passwords do not match.')
            else:
                ok,msg=create_user(name,email,pw,role,company if role=='Company' else '')
                (st.success if ok else st.error)(msg)

def show_writing(review):
    st.subheader('Resume writing review')
    if not review:
        st.info('Not analyzed in this saved review. Upload the resume again for a writing check.')
        return
    value=review.get('generic_line_pct')
    st.metric('Generic wording frequency', 'Not enough text' if value is None else f'{value:.1f}%')
    st.caption('Percentage of reviewed text segments containing checklist phrases. This is not an AI-generated content probability or evidence of authorship. It does not affect fit scores.')
    st.write('Segments reviewed:',review['lines_reviewed'], '· Repeated segments:',review['repeated_lines'])
    st.write('Phrases to review: '+(', '.join(review['phrases']) or 'None flagged by this checklist'))
    for tip in review['tips']: st.write('• '+tip)

def writing_page():
    header('INDIVIDUAL WORKSPACE','Resume writing check','Improve clarity and specificity without inventing experience. No job description required.')
    file=st.file_uploader('Resume',type=['pdf','docx','txt'],key='writing_file')
    if file and st.button('Check writing'):
        try:
            content=extract_text(file.getvalue(),file.name)
            if len(content.strip())<30: st.warning('Not enough readable text.')
            else: show_writing(review_writing(content))
        except Exception as exc: st.error(str(exc))

def show_breakdown(result):
    a,b,c,d=st.columns(4)
    a.metric('Estimated fit',f"{result.get('score',0):.1f}%")
    b.metric('Skill coverage',f"{result.get('skill_score',0):.1f}%")
    c.metric('Text alignment',f"{result.get('semantic_score',result.get('text_score',0)):.1f}%")
    d.metric('Skills to review',len(result.get('missing_skills',[])))
    circular_group([('Estimated fit',result.get('score',0),'#ff8a3d'),('Skill coverage',result.get('skill_score',0),'#ef4c50'),('Text alignment',result.get('semantic_score',result.get('text_score',0)),'#e6b65c')],3)
    st.caption(NOTICE)
    st.caption('Similarity method: '+result.get('matching_method','Legacy TF-IDF / unknown'))
    left,right=st.columns(2)
    with left:
        st.subheader('Matched skills')
        st.write(', '.join(result.get('matched_skills',[])) or 'No tracked skills found in both documents.')
    with right:
        st.subheader('Skills not detected in resume')
        st.write(', '.join(result.get('missing_skills',[])) or 'No gaps detected in the tracked skill vocabulary.')
    show_writing(result.get('writing_review'))
    st.subheader('Suggested next steps')
    for tip in result.get('recommendations',[]): st.markdown('- '+tip)

def export_csv(rows):
    return pd.DataFrame(rows).to_csv(index=False).encode('utf-8-sig')

def semantic_control(key):
    enabled=st.toggle('Use semantic embeddings when available',value=True,key=key,help='Install sentence-transformers for MiniLM contextual matching. Otherwise the app clearly falls back to TF-IDF.')
    return enabled

def individual_review(user):
    header('INDIVIDUAL WORKSPACE','Check your resume fit','Compare your resume with a role, understand the score, and keep a private review history.')
    with st.form('individual_form'):
        role=st.text_input('Target job title',placeholder='e.g. Junior Data Analyst')
        resume=st.file_uploader('Your resume (PDF, DOCX or TXT)',type=['pdf','docx','txt'])
        jd=st.text_area('Paste job description',height=190,placeholder='Paste the full job description here...')
        semantic=st.checkbox('Use semantic embeddings when available',value=True)
        submit=st.form_submit_button('Analyze resume',type='primary')
    if submit:
        if not resume or len(jd.strip())<40: st.error('Upload a resume and enter a job description of at least 40 characters.')
        else:
            content=extract_text(resume.getvalue(),resume.name)
            if len(content.strip())<30: st.error('Unable to extract enough text. For scanned PDFs, use a text-based resume.')
            else:
                with st.spinner('Analyzing your resume...'):
                    result=analyze_resume(content,jd,semantic)
                    analysis_id=save_analysis(user['id'],'Individual',resume.name,result['score'],jd,result,role)
                st.session_state.latest_individual_id=analysis_id
                st.success('Review saved to your history.')
    if st.session_state.get('latest_individual_id'):
        record=get_analysis_details(user['id'],st.session_state.latest_individual_id)
        if record:
            from roadmap import improvement_plan
            result=record['result']
            st.divider()
            st.subheader('1. Resume match results')
            a,b,c=st.columns(3)
            a.metric('Estimated fit',f"{result.get('score',0):.1f}%")
            b.metric('Skill coverage',f"{result.get('skill_score',0):.1f}%")
            c.metric('Text alignment',f"{result.get('semantic_score',0):.1f}%")
            left,right=st.columns(2)
            with left:
                st.markdown('### Matched skills')
                for skill in result.get('matched_skills',[]): st.markdown('✓ '+skill.title())
                if not result.get('matched_skills'): st.write('No tracked matches detected.')
            with right:
                st.markdown('### Missing skills')
                for skill in result.get('missing_skills',[]): st.markdown('• '+skill.title())
                if not result.get('missing_skills'): st.write('No tracked gaps detected.')
            st.subheader('2. How to improve your resume')
            plan=improvement_plan(result)
            decision=get_or_create_recommendation(user['id'],record['id'],result)
            if plan:
                for item in plan:
                    st.markdown('**'+item['skill'].title()+' — skill gap**')
                    st.write('Learn: '+item['title']+' ('+item['topics']+').')
                    st.write('Practice: '+item['project'])
                    st.write('Resume change: once completed, describe the project, your contribution and actual outcome in the Projects section.')
            else:
                st.write('No tracked missing skills. Strengthen evidence of the skills already listed and review the full job description.')
            st.markdown('### Improve your existing resume')
            matched=result.get('matched_skills',[])
            if matched:
                st.write('Highlight relevant existing skills: '+', '.join(matched)+'. Support them with real examples.')
            for tip in result.get('recommendations',[]):
                if not tip.startswith('If you have these skills'): st.markdown('• '+tip)
            st.write('Use a project bullet such as: Built [actual project] using [tools you used] to achieve [verified result]. Replace the placeholders with your own work.')
            st.caption('These steps improve documented job alignment, not a guaranteed selection probability. Never add skills or achievements you cannot demonstrate.')
            with st.expander('Optional: improve future advice'):
                st.write('Preferred guidance: '+LABELS[decision['action']])
                if decision['reward'] is None:
                    feedback=st.radio('Was this guidance helpful?', ['Yes','Partly','No'],horizontal=True,key=f"rl_rating_{decision['id']}")
                    if st.button('Save preference',key=f"rl_save_{decision['id']}"):
                        if record_reward(user['id'],decision['id'],feedback): st.rerun()
                else: st.caption('Preference saved.')
            st.subheader('3. Score breakdown')
            circular_group([('Estimated fit',result.get('score',0),'#ff8a3d'),('Skill coverage',result.get('skill_score',0),'#ef4c50'),('Text alignment',result.get('semantic_score',0),'#e6b65c')],3)
            st.caption('Similarity method: '+result.get('matching_method','Unknown'))
            show_writing(result.get('writing_review'))
            st.download_button('Download analysis (JSON)',json.dumps(result,indent=2).encode(),file_name='seev_resume_review.json',mime='application/json')

from bulk_dataset import dataset_file_inputs

from campaigns import init_campaigns, campaigns, create_campaign, existing_digests, digest, add_results, ranking

def company_review(user):
    init_campaigns()
    header('COMPANY WORKSPACE','Candidate Screening','Continue a saved vacancy or create a new one. Rankings include all accepted batches for that campaign.')
    uid=user['id']
    with st.expander('Create a new recruitment campaign'):
        with st.form('new_campaign'):
            title=st.text_input('Job title')
            jd=st.text_area('Job description',height=180)
            method=st.selectbox('Fixed matching method',['Semantic embeddings (MiniLM)','TF-IDF fallback'])
            create=st.form_submit_button('Create campaign')
        if create:
            try:
                cid=create_campaign(uid,title,jd,method)
                st.session_state['active_campaign']=cid
                st.rerun()
            except ValueError as exc: st.error(str(exc))
    choices={c['id']:c for c in campaigns(uid)}
    if not choices:
        st.info('Create your first campaign to begin.')
        return
    ids=list(choices)
    active=st.session_state.get('active_campaign')
    cid=st.selectbox('Recruitment campaign',ids,index=ids.index(active) if active in ids else 0,
                     format_func=lambda x:f"{choices[x]['title']} · #{x}",key='campaign_picker_'+str(active))
    c=choices[cid]
    jd=c['jd']; role=c['title']; semantic=c['method']=='Semantic embeddings (MiniLM)'
    st.caption('Fixed matching method: '+c['method'])
    with st.expander('Campaign job description'): st.write(jd)
    uploads=st.file_uploader('Upload candidates',type=['pdf','docx','txt','csv','xlsx'],accept_multiple_files=True,key='unified_upload',help='Mix individual resumes and candidate datasets in one batch.')
    files=[]; dataset_rows=[]; ready=True
    for i,file in enumerate(uploads):
        if file.name.lower().endswith(('.csv','.xlsx')):
            with st.expander('Dataset settings: '+file.name,expanded=True):
                rows=dataset_file_inputs(st,file,key=f'unified_{i}_{digest(file.name+str(file.size))}')
                if rows is None: ready=False
                else: dataset_rows.extend((f'{file.name} · {name}',text) for name,text in rows)
        else: files.append(file)
    st.caption(f'{len(files)} resume files and {len(dataset_rows)} readable dataset rows ready for screening.')
    submit=st.button('Analyze All Candidates',type='primary',disabled=not ready or not (files or dataset_rows))
    if submit:
        parsed=list(dataset_rows)
        for file in files:
            try:
                content=extract_text(file.getvalue(),file.name)
                if len(content.strip())>=30: parsed.append((file.name,content))
                else: st.warning('Unreadable: '+file.name)
            except Exception: st.warning('Unreadable: '+file.name)
        seen=existing_digests(uid,cid)
        pending=[]
        for name,content in parsed:
            h=digest(content)
            if h not in seen:
                pending.append((name,content,h)); seen.add(h)
        st.info(f'{len(parsed)-len(pending)} duplicate text records skipped.')
        if pending:
            progress=st.progress(0)
            try:
                results=[]
                for i,(name,content,h) in enumerate(pending):
                    r=analyze_resume(content,jd,semantic)
                    if r['matching_method']!=c['method']:
                        raise ValueError('Campaign model unavailable. Install or restore MiniLM before continuing; no results saved.')
                    results.append((name,h,r))
                    progress.progress((i+1)/len(pending))
                count=add_results(uid,cid,results)
                st.success(f'{count} new candidates saved in {role}.')
            except Exception as exc: st.error(str(exc))
            finally: progress.empty()
        elif not parsed: st.warning('Upload readable candidate data first.')
    batch=ranking(uid,cid)
    st.metric('Total unique campaign candidates',len(batch))
    if batch:
        st.divider(); st.subheader('Cumulative candidate ranking')
        df=pd.DataFrame(batch)
        limit=st.selectbox('Show candidates',['All',5,10,50,100],key='campaign_limit')
        visible=df if limit=='All' else df.head(limit)
        st.dataframe(visible.drop(columns=['Analysis ID']),use_container_width=True,hide_index=True)
        st.caption('Ranking is for human review; scores are not hiring probabilities.')
        st.subheader('Top 3 candidates · fit comparison')
        circular_group([(str(r['Candidate']).replace('.pdf','')[:24],r['Fit score'],DONUT_COLORS[i%len(DONUT_COLORS)]) for i,r in df.head(3).iterrows()],4)
        st.download_button('Download full campaign ranking CSV',export_csv(batch),'seev_candidate_ranking.csv','text/csv')
        options={f"{row['Candidate']} · {row['Fit score']:.1f}% · #{row['Analysis ID']}":row['Analysis ID'] for row in batch}
        selected=st.selectbox('Inspect a candidate',list(options))
        record=get_analysis_details(user['id'],options[selected])
        if record:
            show_breakdown(record['result'])
            st.subheader('Adaptive HR review guidance — reinforcement learning')
            st.caption('The bandit learns which review guidance HR finds useful. It never changes candidate scores, rankings, or hiring decisions.')
            decision=get_or_create_recommendation(user['id'],record['id'],record['result'],mode='Company')
            st.markdown('**Suggested human review action:** '+COMPANY_LABELS[decision['action']])
            st.caption('Contextual epsilon-greedy bandit · '+decision['strategy'].replace('_',' ')+' · exploration '+str(int(EPSILON*100))+'%')
            if decision['reward'] is None:
                feedback=st.radio('Was this HR review suggestion useful?', ['Yes','Partly','No'],horizontal=True,key=f"company_rl_rating_{decision['id']}")
                if st.button('Train company RL from feedback',key=f"company_rl_save_{decision['id']}"):
                    if record_reward(user['id'],decision['id'],feedback):
                        st.success('Company RL reward saved. Future HR review suggestions can adapt.')
                        st.rerun()
                    else: st.warning('Feedback already recorded.')
            else:
                st.success(f"Company feedback recorded · reward {decision['reward']:.1f} / 1.0")

def dashboard(user):
    mode=user['role']; history=get_history_details(user['id'],mode)
    header('YOUR DASHBOARD',f"{mode} overview",'All metrics are based on reviews saved under your own account.')
    if not history:
        st.info('No analyses saved yet. Open the screening workspace to create your first review.'); return
    df=pd.DataFrame(history)
    df['Generic wording %']=df['result_json'].map(lambda raw:writing_pct(json.loads(raw or '{}')))
    df['score']=pd.to_numeric(df['score'],errors='coerce').fillna(0)
    a,b,c,d=st.columns(4)
    a.metric('Total reviews',len(df)); b.metric('Average fit',f"{df['score'].mean():.1f}%")
    c.metric('Highest fit',f"{df['score'].max():.1f}%")
    d.metric('Reviews ≥ 75%',int((df['score']>=75).sum()))
    if mode in ('Individual','Company'):
        st.subheader('RL learning progress — '+mode)
        learning=learning_summary(user['id'],mode=mode)
        st.caption('Real feedback-based online learning. Ratings are per recommended action; no automatic hiring decisions.')
        st.metric('Recommendations rated',learning['rated'])
        if learning['actions']:
            st.dataframe(pd.DataFrame([{'Action':(COMPANY_LABELS if mode=='Company' else LABELS).get(action,action), 'Ratings':stats['rated'],
                        'Average reward (0–1)':stats['average_reward']}
                        for action,stats in learning['actions'].items()]),hide_index=True,use_container_width=True)
        else:
            st.info('Rate adaptive suggestions in your screening workspace, then return here to view learning progress.')
    st.subheader('Score overview')
    circular_group([('Average fit',df['score'].mean(),'#ff8a3d'),('Highest fit',df['score'].max(),'#ef4c50'),
                    ('Strong alignment share',100*(df['score']>=75).mean(),'#e6b65c')],3)
    st.subheader('Top 3 review scores')
    recent=df.sort_values('score',ascending=False).head(3)
    circular_group([(str(row['filename'])[:22],row['score'],DONUT_COLORS[i%len(DONUT_COLORS)])
                    for i,(_,row) in enumerate(recent.iterrows())],4)
    if mode=='Company':
        st.subheader('Candidate rankings')
        display=df[['id','filename','job_title','score','created_at','Generic wording %']].rename(columns={'id':'Review ID','filename':'Candidate','job_title':'Role','score':'Fit score','created_at':'Date'})
        st.dataframe(display.sort_values('Fit score',ascending=False),hide_index=True,use_container_width=True)
    else:
        st.subheader('Your recent reviews')
        st.dataframe(df[['id','job_title','filename','score','created_at','Generic wording %']].rename(columns={'id':'Review ID','job_title':'Role','filename':'Resume','score':'Fit score','created_at':'Date'}),hide_index=True,use_container_width=True)
    st.download_button('Export full history (CSV)',export_csv(df.drop(columns=['result_json','jd_text'],errors='ignore')),'seev_history.csv','text/csv')

def history_page(user):
    header('REVIEW ARCHIVE','Your saved history','Open any prior analysis to revisit skill gaps and recommendations.')
    records=get_history_details(user['id'],user['role'])
    if not records: st.info('No saved analyses yet.'); return
    options={f"#{r['id']} · {r['job_title'] or 'Untitled role'} · {r['filename']} · {r['score']:.1f}% · {r['created_at']}":r['id'] for r in records}
    selected=st.selectbox('Select an analysis',list(options))
    record=get_analysis_details(user['id'],options[selected])
    if record:
        st.caption(f"Saved {record['created_at']} · {record['mode']} · {record['filename']}")
        show_breakdown(record['result'])
        st.download_button('Download selected review (JSON)',json.dumps(record['result'],indent=2).encode(),'seev_saved_review.json','application/json')



def dataset_evaluation_page():
    header('MODEL EVALUATION','Dataset & ranking evaluation','Test 15 fictional candidates against 6 sample job descriptions (90 labeled pairs).')
    st.info('All examples and relevance labels are synthetic and illustrative, not expert-annotated hiring ground truth. Scores are ranking metrics, NOT model accuracy or probability of selection.')
    from evaluation import evaluate, read_csv
    resumes=read_csv('resumes.csv')
    jobs=read_csv('job_descriptions.csv')
    a,b,c=st.columns(3)
    a.metric('Sample resumes',len(resumes))
    b.metric('Job descriptions',len(jobs))
    c.metric('Labeled pairs',len(resumes)*len(jobs))
    with st.expander('View dataset samples'):
        st.dataframe(pd.DataFrame([{'Candidate':r['candidate_name'],'Role':r['candidate_role'],'Resume ID':r['resume_id']} for r in resumes]),hide_index=True,use_container_width=True)
        st.dataframe(pd.DataFrame(jobs)[['jd_id','job_title']],hide_index=True,use_container_width=True)
    semantic=st.checkbox('Evaluate with MiniLM embeddings (if installed)',value=False,help='Unchecked: TF-IDF baseline. Checked: MiniLM if available; otherwise labeled TF-IDF fallback.')
    if st.button('Run dataset evaluation',type='primary'):
        with st.spinner('Ranking all 90 resume–job pairs...'):
            result=evaluate(semantic=semantic)
        st.session_state['dataset_eval_result']=result
    result=st.session_state.get('dataset_eval_result')
    if result:
        st.caption('Actual matching method: '+', '.join(sorted({r['matching_method'] for r in result['jobs']})))
        a,b=st.columns(2)
        a.metric('Mean NDCG@5',f"{result['mean_ndcg_at_5']:.3f}")
        b.metric('Mean Precision@5',f"{result['mean_precision_at_5']:.3f}")
        st.caption('NDCG@5 measures ranking agreement with the synthetic relevance labels. Precision@5 is the fraction of top-five resumes with label 2 or 3.')
        summary=pd.DataFrame([{'Job':r['job_title'],'NDCG@5':r['ndcg_at_5'],'Precision@5':r['precision_at_5']} for r in result['jobs']])
        st.dataframe(summary,hide_index=True,use_container_width=True)
        st.subheader('Evaluation comparison')
        job=st.selectbox('Inspect ranking for a job',list(range(len(result['jobs']))),format_func=lambda x:result['jobs'][x]['job_title'])
        row=summary.iloc[job]
        circular_group([('NDCG@5',row['NDCG@5']*100,'#ff8a3d'),
                        ('Precision@5',row['Precision@5']*100,'#ef4c50')],2)
        ranking=pd.DataFrame(result['jobs'][job]['ranking'])
        ranking.insert(0,'Rank',range(1,len(ranking)+1))
        st.dataframe(ranking[['Rank','candidate','role','score','relevance','method']],hide_index=True,use_container_width=True)
        st.download_button('Download evaluation results (CSV)',summary.to_csv(index=False).encode('utf-8'),'seev_evaluation_results.csv','text/csv')

def about():
    header('HOW IT WORKS','Clear and explainable matching','A practical decision-support tool, not an automated hiring authority.')
    for title,body in [('01 · Upload','Upload a text-readable resume and provide a job description.'),('02 · Compare','Detect skills, calculate coverage, and compare overall wording or optional semantic embeddings.'),('03 · Review','Inspect estimated fit, missing skills and concrete improvement suggestions.'),('04 · Track','Return to your private dashboard for historical comparisons and downloadable reports.'),('05 · Learn','Individuals can rate a recommended improvement; an epsilon-greedy contextual bandit learns from category-specific rewards over time.')]:
        st.markdown(f'<div class="panel"><h3>{title}</h3><p>{body}</p></div>',unsafe_allow_html=True)
    st.info('To enable actual semantic embeddings, run: pip install sentence-transformers. The first use downloads the MiniLM model; without it, the app uses TF-IDF fallback and labels that method clearly.')
    st.warning('Avoid using fit scores as the sole basis for employment decisions. The app does not infer protected attributes or predict a calibrated hiring likelihood.')

if 'user' not in st.session_state: signin(); st.stop()
user=st.session_state.user
with st.sidebar:
    st.markdown('## ◈ SEEV')
    st.caption('Resume intelligence workspace')
    st.divider()
    st.markdown(f"**{user['name']}**")
    st.caption(user['role']+' account')
    st.divider()
    page=st.radio('Navigation',(['Dashboard','Candidate Screening','History','Dataset Evaluation','About SEEV'] if user['role']=='Company' else ['Dashboard','Analyze resume','Resume Writing Check','History','Dataset Evaluation','About SEEV']),label_visibility='collapsed')
    st.divider()
    if st.button('Sign out',use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
if page=='Dashboard': dashboard(user)
elif page in ('Candidate Screening','Analyze resume'):
    (company_review if user['role']=='Company' else individual_review)(user)
elif page=='Resume Writing Check' and user['role']=='Individual': writing_page()
elif page=='History': history_page(user)
elif page=='Dataset Evaluation': dataset_evaluation_page()
else: about()
