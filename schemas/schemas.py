from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from database.models import Owners, Items


class ItemBase(BaseModel):
    name: str
    content: str | None = None
    depth: int

    owner_id: int

    sort_group: int | None = None
    root_id: int | None = None
    root_sort: float | None = None

    del_key: str | None = None


class OwnerBase(BaseModel):
    name: str
    content: str | None = None


class ItemDisplay(BaseModel):
    id: int
    name: str
    content: str | None = None
    depth: int
    sort_group: int
    sort_in_group: float
    del_key: str

    class Config:
        orm_mode = True


class OwnerDisplay(BaseModel):
    name: str
    content: str | None = None

    class Config:
        orm_mode = True


def create_owner(req: OwnerBase, db: Session):
    new_owner = Owners(
        name=req.name,
        content=req.content
    )
    db.add(new_owner)
    db.commit()
    db.refresh(new_owner)
    return new_owner


def create_items(req: ItemBase, db: Session):
    """
    :param req: name, content, depth, owner_id, sort_group, root_id, root_sort, del_key
        name: item 명
        content: item 내용
        depth: 트리형 구조 에서의 깊이 (기본은 0)
        owner_id: owner 의 id
        sort_group: 트리형 구조 내에서, 정렬 그룹 (뿌리 대상이 이 없다면, 즉 depth==0이라면, 0으로 request)
        root_id: depth==0이라면, 0으로 request, 그외엔 뿌리 대상의 id
        root_sort: 뿌리 대상의 구조내 정렬 순번
        del_key: 뿌리 대상의 del_key, depth==0이라면, 0으로 request
    :param db: session 연결용
    """
    # 쿼리 1번
    row = db.execute(select(Owners.item_groups)
                     .where(Owners.id == req.owner_id)
                     .limit(1)).scalar()

    sort = row + 1

    if req.depth == 0:  # 깊이가 0이면, group 수에 따라서 결정
        sort_group = sort
        sort_in_group = 0

        del_key = str(req.owner_id)+'-'+str(sort)
    else:  # 아니면, root의 그룹 그대로
        sort_group = req.sort_group
        # 쿼리 2번, 다음꺼 + 그 이전꺼 찾아야 하기에 => 쿼리 총 2번 반복 (총 3번)
        af = db.execute(select(Items.sort_in_group)
                        .where(Items.sort_group == sort_group)
                        .where(Items.sort_in_group > req.root_sort)  # 부모 보다 순서가 뒤며,
                        .where(Items.depth < req.depth)  # 자신 보다 낮은 depth
                        .order_by(Items.sort_in_group)
                        .limit(1)).scalar()  # 중에 첫번째

        if af is None:
            af = sort_group + 1
        bf = db.execute(select(Items.sort_in_group)
                        .where(Items.sort_group == sort_group)
                        .where(Items.sort_in_group < af)  # 앞썬 거(af)보다 순서가 앞인,
                        .order_by(-Items.sort_in_group)
                        .limit(1)).scalar()  # 중에 첫번째
        sort_in_group = (af+bf)/2  # 중간 삽입을 위한 평균 값

        del_key = str(req.del_key)+'-'+str(req.root_id)

    new_item = Items(
        name=req.name,
        content=req.content,
        depth=req.depth,
        owner_id=req.owner_id,
        sort_group=sort_group,
        sort_in_group=sort_in_group,
        del_key=del_key)  # 생성

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    if new_item and req.depth == 0:
        db.execute(update(Owners)
                   .where(Owners.id == req.owner_id)
                   .values(item_groups=sort))  # 이후, 그룹 증설
        db.commit()

    return new_item


def get_items(owner_id: int, db: Session):
    items = db.execute(select(Items)  # status == active 전부 탐색
                       .where(Items.owner_id == owner_id)
                       .where(Items.status == 'active')
                       .order_by(Items.sort_group)
                       .order_by(Items.sort_in_group)).scalars().all()
    return items


def del_items(del_key: str, db: Session):
    items = db.execute(select(Items)  # 해당 하위 대상을 포함, 전부 status 변경
                       .where(Items.del_key.like(f"{del_key}%"))).scalars().all()

    for i in items:
        i.status = 'deleted'
    db.commit()

    return 'success'
