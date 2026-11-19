"""Job-specific, actionable learning recommendations; no hiring guarantees."""
COURSES={
'python':('Python fundamentals and practical scripting','functions, lists, dictionaries, files and error handling','Automate cleaning a CSV dataset and export a summary.'),
'sql':('SQL for data analysis','joins, grouping, subqueries and window functions','Build a sales database and answer five business questions using SQL.'),
'excel':('Excel for business analysis','pivot tables, lookup functions and charts','Create a monthly sales report with pivot tables.'),
'power bi':('Microsoft Learn: Power BI fundamentals','Power Query, DAX and dashboard creation','Build a sales dashboard with revenue, profit and monthly trends.'),
'tableau':('Tableau fundamentals','calculated fields, filters and dashboards','Create an interactive customer analytics dashboard.'),
'pandas':('Pandas for data analysis','missing values, merges, groupby and aggregation','Clean and summarize an online retail dataset.'),
'numpy':('NumPy fundamentals','arrays, indexing and vectorized calculations','Analyze numerical sensor data and calculate summary statistics.'),
'statistics':('Applied statistics','distributions, hypothesis testing and correlation','Analyze a survey and explain its limitations.'),
'data cleaning':('Data cleaning and preprocessing','missing values, duplicates and validation','Clean a messy dataset and document every transformation.'),
'data visualization':('Data visualization fundamentals','chart selection, labeling and interpretation','Create a report with five clear charts.'),
'flask':('Flask web development','routes, validation and database integration','Build a CRUD application with a REST API.'),
'django':('Django fundamentals','models, views, authentication','Build a task management web application.'),
'fastapi':('FastAPI fundamentals','routing, schemas and API testing','Build a documented inventory REST API.'),
'react':('React fundamentals','components, state and API calls','Create an interactive dashboard using a public API.'),
'machine learning':('Applied machine learning','train/test splits, baselines and evaluation','Build and evaluate a classification model.'),
'git':('Git and GitHub fundamentals','commits, branches and pull requests','Publish a documented project with version history.'),
'docker':('Docker fundamentals','images, containers and compose','Containerize a small web application.'),
}
def improvement_plan(result):
    gaps=list(dict.fromkeys(result.get('missing_skills') or []))
    courses=[]
    for skill in gaps:
        title,topics,project=COURSES.get(skill.lower(),(f'{skill.title()} fundamentals',f'core concepts and hands-on exercises in {skill}',f'Complete a small job-relevant exercise demonstrating {skill}.'))
        courses.append(dict(skill=skill,title=title,topics=topics,project=project))
    return courses
