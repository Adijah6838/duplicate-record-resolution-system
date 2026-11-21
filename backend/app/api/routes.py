import csv, io
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db, engine, Base
from app.models.customer import Customer, DuplicateCandidate, MergeHistory
from app.services.matcher import compare
from datetime import datetime

router = APIRouter()
Base.metadata.create_all(bind=engine)

def to_dict(c):
    return {"id": c.id, "full_name": c.full_name, "email": c.email, "phone": c.phone, "address": c.address, "date_of_birth": str(c.date_of_birth) if c.date_of_birth else None, "status": c.status}

@router.post("/upload")
def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    text = file.file.read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    count = 0
    for r in rows:
        dob = None
        if r.get("date_of_birth"):
            try: dob = datetime.strptime(r["date_of_birth"].strip(), "%Y-%m-%d").date()
            except: pass
        db.add(Customer(full_name=r.get("full_name","").strip(), email=r.get("email","").strip(), phone=r.get("phone","").strip(), address=r.get("address","").strip(), date_of_birth=dob))
        count += 1
    db.commit()
    return {"imported": count}

@router.get("/customers")
def list_customers(db: Session = Depends(get_db)):
    return [to_dict(c) for c in db.query(Customer).filter(Customer.status=="active").all()]

@router.post("/detect")
def detect(threshold: float = 50, db: Session = Depends(get_db)):
    db.query(DuplicateCandidate).filter(DuplicateCandidate.decision=="pending").delete()
    db.commit()
    customers = db.query(Customer).filter(Customer.status=="active").all()
    found = 0
    for i in range(len(customers)):
        for j in range(i+1, len(customers)):
            a, b = customers[i], customers[j]
            res = compare({"full_name":a.full_name,"email":a.email,"phone":a.phone,"address":a.address,"date_of_birth":str(a.date_of_birth) if a.date_of_birth else None},
                          {"full_name":b.full_name,"email":b.email,"phone":b.phone,"address":b.address,"date_of_birth":str(b.date_of_birth) if b.date_of_birth else None})
            if res["score"] >= threshold:
                db.add(DuplicateCandidate(customer_a_id=a.id, customer_b_id=b.id, **res))
                found += 1
    db.commit()
    return {"candidates": found}

@router.get("/duplicates")
def list_dups(db: Session = Depends(get_db)):
    out=[]
    for d in db.query(DuplicateCandidate).filter(DuplicateCandidate.decision=="pending").all():
        a=db.get(Customer,d.customer_a_id); b=db.get(Customer,d.customer_b_id)
        out.append({"id":d.id,"score":d.score,"breakdown":{"name":d.name_score,"email":d.email_score,"phone":d.phone_score,"address":d.address_score,"dob":d.dob_score},"a":to_dict(a),"b":to_dict(b)})
    return out

@router.post("/duplicates/{dup_id}/decision")
def decide(dup_id: int, action: str, db: Session = Depends(get_db)):
    d=db.get(DuplicateCandidate,dup_id)
    if not d: return {"error":"not found"}
    a=db.get(Customer,d.customer_a_id); b=db.get(Customer,d.customer_b_id)
    if action=="approve":
        b.status="merged"; b.merged_into_id=a.id; d.decision="approved"
        db.add(MergeHistory(survivor_id=a.id, merged_id=b.id, score=d.score, action="merged"))
    else:
        d.decision="rejected"
        db.add(MergeHistory(survivor_id=a.id, merged_id=b.id, score=d.score, action="rejected"))
    db.commit()
    return {"ok": True, "action": action}

@router.get("/history")
def history(db: Session = Depends(get_db)):
    return [{"id":h.id,"survivor_id":h.survivor_id,"merged_id":h.merged_id,"score":h.score,"action":h.action,"at":str(h.created_at)} for h in db.query(MergeHistory).all()]

@router.get("/quality")
def quality(db: Session = Depends(get_db)):
    total=db.query(Customer).count()
    active=db.query(Customer).filter(Customer.status=="active").count()
    merged=db.query(Customer).filter(Customer.status=="merged").count()
    missing_email=db.query(Customer).filter((Customer.email=="")|(Customer.email.is_(None))).count()
    return {"total":total,"active":active,"merged":merged,"missing_email":missing_email}