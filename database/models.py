from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, SmallInteger, Float, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship

from database.session import Base


class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum('active', 'deleted', 'blocked'), default='active')
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Items(BaseMixin, Base):
    __tablename__ = 'items'
    name = Column(String)
    content = Column(Text)

    depth = Column(SmallInteger)

    sort_group = Column(Integer, index=True)
    sort_in_group = Column(Float, index=True)

    owner_id = Column(Integer, ForeignKey('owners.id'))
    owner = relationship('Owners', back_populates='items', uselist=False)

    del_key = Column(String)


class Owners(BaseMixin, Base):
    __tablename__ = 'owners'
    name = Column(String)
    content = Column(Text)

    items = relationship('Items', back_populates='owner')
    item_groups = Column(SmallInteger, default=0)

    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship('Groups', back_populates='children', uselist=False)


members_association = Table(
    'groups_members_association',
    Base.metadata,
    Column('groups_id', ForeignKey('groups.id')),
    Column('members_id', ForeignKey('members.id'))
)


rights_association = Table(
    'members_rights_association',
    Base.metadata,
    Column('group_rights_id', ForeignKey('group_rights.id')),
    Column('members_id', ForeignKey('members.id'))
)


class Groups(BaseMixin, Base):
    __tablename__ = 'groups'
    name = Column(String)
    description = Column(String)

    children = relationship('Owners', back_populates='group')
    members = relationship('Members',
                           secondary=lambda: members_association,
                           back_populates='groups')
    rights_tables = relationship('GroupRights', back_populates='group')


class Members(BaseMixin, Base):
    __tablename__ = 'members'
    name = Column(String, index=True)

    groups = relationship('Groups',
                          secondary=lambda: members_association,
                          back_populates='members')
    rights = relationship('GroupRights',
                          secondary=lambda: rights_association,
                          back_populates='members')


class GroupRights(BaseMixin, Base):
    __tablename__ = 'group_rights'
    name = Column(String)

    first_right = Column(Boolean, default=True)
    second_right = Column(Boolean, default=False)
    third_right = Column(Boolean, default=False)

    members = relationship('Members',
                           secondary=lambda: rights_association,
                           back_populates='rights')

    group_id = Column(Integer, ForeignKey('groups.id'), index=True)
    group = relationship('Groups', back_populates='rights_tables')
