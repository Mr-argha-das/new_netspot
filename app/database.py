from pathlib import Path
import os, tempfile
import pandas as pd
from .config import DATA_DIR

SCHEMAS = {
    "users": ["id","name","email","game","game_profile_name","utr_id","phone","password_hash","role","status","created_at"],
    "teams": ["id","owner_id","game","name","logo","status","admin_note","created_at","updated_at"],
    "team_members": ["id","team_id","user_id","slot","game_id","profile_name","status","note"],
    "tournaments": ["id","name","game","map","description","rules","date","time","registration_deadline","entry_fee","first_prize","second_prize","prize_pool","max_teams","players_per_team","banner","status","room_id","room_password","match_number","created_at"],
    "applications": ["id","tournament_id","team_id","owner_id","status","admin_note","created_at","updated_at"],
    "payments": ["id","user_id","utr_id","amount","status","admin_note","created_at","updated_at"],
    "winners": ["id","tournament_id","team_id","winner_name","prize","description","logo","created_at"],
    "notifications": ["id","user_id","title","message","kind","is_read","created_at"],
    "settings": ["key","value"],
    "faq": ["id","question","answer","active","sort_order","created_at"],
    "match_results": ["id","tournament_id","team_id","rank","points","prize","created_at"],
}
def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, cols in SCHEMAS.items():
        p = DATA_DIR/f"{name}.feather"
        if not p.exists():
            pd.DataFrame(columns=cols).to_feather(p)
    if len(read("settings")) == 0:
        seed_settings({
            "registration_amount":"99",
            "payment_qr":"",
            "payment_instructions":"Scan the QR and enter the UTR ID after payment.",
            "site_name":"NETSPORTS",
            "support_email":"",
            "support_phone":"",
            "maintenance_mode":"0",
            "hero_title":"PLAY. WIN. REPEAT.",
            "hero_description":"Build your squad, enter tournaments, climb the leaderboard and become the next NETSPORTS champion."
        })
def read(name):
    p=DATA_DIR/f"{name}.feather"
    if not p.exists(): init_db()
    df=pd.read_feather(p)
    return df
def write(name, df):
    p=DATA_DIR/f"{name}.feather"
    fd,tmp=tempfile.mkstemp(prefix=p.stem+"_",suffix=".feather",dir=str(DATA_DIR))
    os.close(fd)
    try:
        df.to_feather(tmp)
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def add(name, record):
    df=read(name)
    for c in SCHEMAS[name]:
        if c not in record: record[c]=None
    df=pd.concat([df,pd.DataFrame([record],columns=SCHEMAS[name])],ignore_index=True)
    write(name,df)
    return record
def update(name, record_id, changes):
    df=read(name)
    if "id" not in df.columns: return False
    mask=df["id"].astype(str)==str(record_id)
    if not mask.any(): return False
    for k,v in changes.items():
        if k in df.columns: df.loc[mask,k]=v
    write(name,df); return True
def delete(name, record_id):
    df=read(name)
    if "id" not in df.columns: return False
    before=len(df); df=df[df["id"].astype(str)!=str(record_id)]
    write(name,df); return len(df)<before
def get(name, record_id):
    df=read(name)
    if "id" not in df.columns:return None
    x=df[df["id"].astype(str)==str(record_id)]
    return None if x.empty else x.iloc[0].to_dict()
def find_one(name, **kwargs):
    df=read(name)
    for k,v in kwargs.items():
        if k in df.columns: df=df[df[k].astype(str).str.lower()==str(v).lower()]
    return None if df.empty else df.iloc[0].to_dict()
def seed_settings(d):
    df=pd.DataFrame([{"key":k,"value":v} for k,v in d.items()])
    write("settings",df)
def settings():
    df=read("settings")
    return dict(zip(df["key"].astype(str),df["value"].astype(str))) if not df.empty else {}
def set_setting(k,v):
    df=read("settings")
    if (df["key"].astype(str)==str(k)).any():
        df.loc[df["key"].astype(str)==str(k),"value"]=str(v)
    else:
        df=pd.concat([df,pd.DataFrame([{"key":k,"value":str(v)}])],ignore_index=True)
    write("settings",df)
