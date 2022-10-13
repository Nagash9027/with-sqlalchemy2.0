from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Members, Groups, GroupRights


class MemberBase(BaseModel):
    name: str


class GroupBase(BaseModel):
    name: str
    description: str | None = None

    creator_id: int


class GroupRightsBase(BaseModel):
    name: str
    first_right: bool
    second_right: bool
    third_right: bool

    group_id: int


class GroupAdd(BaseModel):
    self_id: int
    tar_id: int

    group_id: int


class GrantRights(BaseModel):
    self_id: int
    tar_id: int

    group_id: int
    rights_id: int


def create_member(req: MemberBase, db: Session):
    new_member = Members(
        name=req.name
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


def create_group(req: GroupBase, db: Session):
    new_group = Groups(
        name=req.name,
        description=req.description
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    # default 권한 추가, 생성자(req.creator_id) -> 모든 권한 ok -> cr
    # default 권한: { cr, mg, cu } -> 3개

    return new_group


def create_group_rights(req: GroupRightsBase, db: Session):
    new_rights = GroupRights(
        name=req.name,
        group_id=req.group_id,
        first_right=req.first_right,
        second_right=req.second_right,
        third_right=req.third_right
    )
    db.add(new_rights)
    db.commit()
    db.refresh(new_rights)

    return new_rights


def adj_rights():  # 나중에 처리.
    pass


def group_add_member(req: GroupAdd, db: Session):
    # self_id validate, skip for now
    # tar_id validate, skip for now
    # then :

    tar = db.execute(select(Members)
                     .where(Members.id == req.tar_id)
                     .limit(1))

    group = db.execute(select(Groups)
                       .where(Groups.id == req.group_id)
                       .limit(1))

    group.members.add(tar)
    db.commit()

    return {'msg': 'success'}


def group_del_member():  # not for now
    pass


def set_rights_member(req: GrantRights, db: Session):
    # self_id validate, skip for now
    # tar_id validate, skip for now
    # then :

    tar = db.execute(select(Members)
                     .where(Members.id == req.tar_id)
                     .limit(1))

    tar.rights.add(db.execute(select(GroupRights)
                              .where(GroupRights.id == req.rights_id)
                              .limit(1)))
    db.commit()

    return {'msg': 'success'}
