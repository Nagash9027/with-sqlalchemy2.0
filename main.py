from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import schemas.schemas as schemas
from database import models
from database.session import engine, get_db
from schemas.schemas import OwnerBase, ItemBase, OwnerDisplay, ItemDisplay

app = FastAPI()


@app.get('/')
async def main():
    return {'msg': 'Empty Page'}


@app.post('/', response_model=OwnerDisplay)
async def create_owner(req: OwnerBase, db: Session = Depends(get_db)):
    return schemas.create_owner(req, db)


@app.post('/items', response_model=ItemDisplay)
async def create_items(req: ItemBase, db: Session = Depends(get_db)):
    return schemas.create_items(req, db)


@app.get('/items/{owner_id}', response_model=list[ItemDisplay])
async def get_items(owner_id: int, db: Session = Depends(get_db)):
    return schemas.get_items(owner_id, db)


@app.post('/items/del/{del_key}')
async def del_items(del_key: str, db: Session = Depends(get_db)):
    return schemas.del_items(del_key, db)

models.Base.metadata.create_all(engine)
