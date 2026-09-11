from ..database import add
from ..auth import now
from ..utils import uid
def notify(user_id,title,message,kind="info"):
    add("notifications",{"id":uid(),"user_id":str(user_id),"title":title,"message":message,"kind":kind,"is_read":False,"created_at":now()})
