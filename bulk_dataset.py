import pandas as pd
from io import BytesIO

def read_dataset(data, name, sheet=0):
    if name.lower().endswith('.xlsx'):
        return pd.read_excel(BytesIO(data), sheet_name=sheet, dtype=str)
    for encoding in ('utf-8-sig','cp1252'):
        try:
            return pd.read_csv(BytesIO(data), encoding=encoding, dtype=str)
        except UnicodeDecodeError:
            continue
    raise ValueError('Unsupported CSV encoding')

def prepare_rows(df, columns, id_column=None):
    rows=[]
    skipped=0
    for i, row in enumerate(df.fillna('').itertuples(index=False,name=None)):
        values=dict(zip(df.columns,row))
        text='\\n'.join(str(values[c]).strip() for c in columns if str(values[c]).strip())
        if len(text.strip())<30:
            skipped+=1
            continue
        identifier=str(values.get(id_column,'')).strip()
        rows.append((f'{identifier or "Candidate"} [row {i+1}]',text))
    return rows,skipped

def dataset_inputs(st):
    file=st.file_uploader('Upload candidate dataset',type=['csv','xlsx'],key='bulk_file')
    if file is None: return []
    return dataset_file_inputs(st,file,'bulk') or []

def dataset_file_inputs(st,file,key):
    try:
        sheet=0
        if file.name.lower().endswith('.xlsx'):
            sheet=st.selectbox('Excel sheet',pd.ExcelFile(BytesIO(file.getvalue())).sheet_names,key=key+'_sheet')
        df=read_dataset(file.getvalue(),file.name,sheet)
    except Exception as exc:
        st.error(f'Cannot read dataset: {exc}')
        return None
    st.metric('Dataset rows',len(df))
    cols=list(df.columns)
    defaults=[c for c in cols if c.lower().replace(' ','_') in ('resume','resume_text','resume_str','resume_content','skills','experience','work_experience','projects','education','summary')]
    selected=st.multiselect('Job-related text columns (exclude contact and personal details)',cols,default=defaults,key=key+'_cols')
    identifier=st.selectbox('Candidate ID column (optional)',[None]+cols,index=next((i+1 for i,c in enumerate(cols) if c.lower() in ('name','candidate_name','candidate_id')),0),format_func=lambda x:x or 'Row number',key=key+'_id')
    if not selected:
        st.warning("Select at least one resume text column.")
        return None
    if identifier in selected: 
        st.warning('Remove the ID column from job-related text columns.')
        return None
    rows,skipped=prepare_rows(df,selected,identifier)
    st.caption(f'{len(rows)} readable candidate rows; {skipped} empty or too short. One row = one candidate.')
    return rows
