import argparse, json
from pathlib import Path
from src.pipeline import run

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args=ap.parse_args()
    candidates, failures, eligible, rejected = run(args.input)
    ranked=[]
    for i,c in enumerate(eligible,1):
        d=c.to_dict(); d["rank"]=i; ranked.append(d)
    rejected_out=[c.to_dict() for c in rejected]
    result={
      "ranked_eligible_candidates": ranked,
      "rejected_candidates": rejected_out,
      "batch_summary": {"total_resumes":len(candidates)+len(failures),"successfully_parsed":len(candidates),"eligible":len(eligible),"rejected":len(rejected),"failed_or_unreadable":len(failures)},
      "failures": failures,
    }
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result["batch_summary"],indent=2))

if __name__ == "__main__": main()
