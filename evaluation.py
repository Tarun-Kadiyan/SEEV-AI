"""Synthetic resume ranking evaluation. Scores are NOT hiring accuracy."""
import csv
from pathlib import Path
import math
from analyzer import analyze_resume

DATA = Path(__file__).resolve().parent / "data"

def read_csv(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

def dcg(values, k=5):
    return sum((2**v-1)/math.log2(i+2) for i,v in enumerate(values[:k]))

def evaluate(semantic=False, k=5):
    resumes=read_csv("resumes.csv")
    jobs=read_csv("job_descriptions.csv")
    labels={(r["jd_id"],r["resume_id"]):int(r["relevance"]) for r in read_csv("relevance_labels.csv")}
    results=[]
    for jd in jobs:
        ranked=[]
        for resume in resumes:
            result=analyze_resume(resume["resume_text"],jd["jd_text"],semantic=semantic)
            ranked.append({"candidate":resume["candidate_name"],"role":resume["candidate_role"],
                           "resume_id":resume["resume_id"],"score":result["score"],
                           "relevance":labels[(jd["jd_id"],resume["resume_id"])],
                           "method":result["matching_method"]})
        ranked.sort(key=lambda r:(-r["score"],r["resume_id"]))
        actual=[r["relevance"] for r in ranked]
        ideal=sorted(actual,reverse=True)
        denominator=dcg(ideal,k)
        ndcg=dcg(actual,k)/denominator if denominator else 0.0
        precision=sum(r["relevance"]>=2 for r in ranked[:k])/k
        results.append({"job_id":jd["jd_id"],"job_title":jd["job_title"],
                        "ndcg_at_5":round(ndcg,3),"precision_at_5":round(precision,3),
                        "matching_method":ranked[0]["method"],"ranking":ranked})
    return {"jobs":results,"mean_ndcg_at_5":round(sum(x["ndcg_at_5"] for x in results)/len(results),3),
            "mean_precision_at_5":round(sum(x["precision_at_5"] for x in results)/len(results),3),
            "dataset_size":len(resumes)*len(jobs),"resume_count":len(resumes),"jd_count":len(jobs)}

if __name__=="__main__":
    import argparse, json
    parser=argparse.ArgumentParser()
    parser.add_argument("--semantic",action="store_true",help="Try MiniLM; may fall back to TF-IDF")
    args=parser.parse_args()
    result=evaluate(semantic=args.semantic)
    print(json.dumps({k:v for k,v in result.items() if k!="jobs"},indent=2))
    for item in result["jobs"]:
        print(item["job_title"],"NDCG@5:",item["ndcg_at_5"],"P@5:",item["precision_at_5"],"Method:",item["matching_method"])
