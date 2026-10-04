import json,csv,glob,os,re
from collections import Counter
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'sources'); OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'fellowship-data')
os.makedirs(OUT,exist_ok=True)
base={r['slug']:r for r in json.load(open(f'{D}/base_programs.json'))}
res={}
for f in sorted(glob.glob(f'{D}/results/r*.json')):
    for r in json.load(open(f)): res[r['slug']]=r
keys=["Specialty","Subspecialty","Department","State or region","Training type","Duration","Start","Deadline","Eligibility","International applicants","Accreditation","Application method","Positions","Funding","Visa support","Licence requirement","Last verified"]
rows=[];log=[]
for s,b in base.items():
    if 'error' in b: continue
    r=res.get(s)
    f=dict(r['fields']) if r else {k:b[k] for k in keys if k in b}
    if r and r.get('changes'): f['Last verified']='3 October 2026'
    rows.append({"slug":s,"url":"https://thefellowshipportal.com"+s,"title":b['title'],"institution":b.get('inst',''),
                 **{k:f.get(k,"Not stated on official page") for k in keys},
                 "official_urls":" | ".join(r['official_urls'] if r else b.get('official_urls',[])),
                 "research_status":r['status'] if r else "not_researched","notes":(r or {}).get('notes','')})
    for k,c in ((r or {}).get('changes') or {}).items():
        log.append({"slug":s,"title":b['title'],"institution":b.get('inst',''),"field":k,"old":c.get('old'),"new":c.get('new'),"source":c.get('source')})
json.dump(rows,open(f'{OUT}/programs.json','w'),indent=1,ensure_ascii=False)
for name,data in (('programs.csv',rows),('changes.csv',log)):
    if data:
        with open(f'{OUT}/{name}','w',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
weak=re.compile(r'not stated|check with|confirm|contact the programme|not specified|unknown',re.I)
print("programs",len(rows),"researched",sum(r['research_status']!='not_researched' for r in rows),"changes",len(log),"real fills",sum(1 for l in log if not re.match(r"not stated",str(l["new"]),re.I)))
print(Counter(r['research_status'] for r in rows))
for k in keys:
    before=sum(1 for b in base.values() if 'error' not in b and (k not in b or weak.search(b[k])))
    after=sum(1 for r in rows if weak.search(r[k]))
    print(f"{k:25} kosong/samar: {before:3} -> {after:3}")

# --- new anaesthesia & radiology programmes ---
new=[]
seen=set(base)|{r['slug'] for r in rows}
seen_key={(r['title'].lower(),r['institution'].lower()) for r in rows}
for f in sorted(glob.glob(f'{D}/new/*_*.json')):
    if 'existing' in f: continue
    try: data=json.load(open(f))
    except Exception as e: print("skip",f,e); continue
    for p in data:
        k=(p.get('title','').lower(),p.get('inst','').lower())
        if p.get('slug') in seen or k in seen_key or not p.get('official_urls'): continue
        seen.add(p['slug']); seen_key.add(k)
        p=dict(p); p['official_urls']=" | ".join(p['official_urls']); new.append(p)
if new:
    cols=list(dict.fromkeys(c for p in new for c in p))
    json.dump(new,open(f'{OUT}/new_programs.json','w'),indent=1,ensure_ascii=False)
    with open(f'{OUT}/new_programs.csv','w',newline='',encoding='utf-8') as fh:
        w=csv.DictWriter(fh,fieldnames=cols,restval=''); w.writeheader(); w.writerows(new)
print("new programmes",len(new),Counter((p['Specialty'],p.get('Country')) for p in new))

# --- apply profile gap-fill patches (only to missing/vague fields) ---
PD=f'{D}/patches'
VAGUE=re.compile(r'^(not stated|check with|confirm current|not specified|contact programme|see official|unknown|$)',re.I)
ALLOWED={"International applicants","Visa support","Funding","Positions","Deadline","Start","Licence requirement","Eligibility","Accreditation","Application method","Duration"}
patches=[]
for f in sorted(glob.glob(f'{PD}/*.json')):
    try: patches+=json.load(open(f)).get('patches',[])
    except Exception as e: print("skip patch",f,e)
if patches:
    P=json.load(open(f'{OUT}/programs.json')); Nw=json.load(open(f'{OUT}/new_programs.json'))
    idx={r['slug']:r for r in P+Nw}; plog=[]; applied=0
    for p in patches:
        r=idx.get(p.get('slug')); k=p.get('field'); v=(p.get('value') or '').strip()
        if not r or k not in ALLOWED or not v or not VAGUE.match(str(r.get(k,'')).strip()): continue
        plog.append({"slug":r['slug'],"title":r['title'],"institution":r.get('institution') or r.get('inst'),"field":k,"old":r.get(k,''),"new":v,"source":p.get('source','')})
        r[k]=v; applied+=1
        if p.get('source') and p['source'] not in r['official_urls']: r['official_urls']+=' | '+p['source']
    json.dump(P,open(f'{OUT}/programs.json','w'),indent=1,ensure_ascii=False)
    json.dump(Nw,open(f'{OUT}/new_programs.json','w'),indent=1,ensure_ascii=False)
    for name,data in (('programs.csv',P),('new_programs.csv',Nw)):
        cols=list(dict.fromkeys(c for x in data for c in x))
        with open(f'{OUT}/{name}','w',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=cols,restval=''); w.writeheader(); w.writerows(data)
    if plog:
        with open(f'{OUT}/changes.csv','a',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=list(plog[0])); w.writerows(plog)
    print("patches applied",applied,"of",len(patches))
