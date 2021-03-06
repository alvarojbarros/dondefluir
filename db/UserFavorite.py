# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, Boolean, String, ForeignKey, Index
from tools.dbconnect import engine
from dondefluir.db.User import User
from dondefluir.db.Company import Company
import tools.DBTools
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserFavorite(Base,Record):
    __tablename__ = 'userfavorite'
    id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey(User.id), nullable=False)
    FavoriteId = Column(Integer, ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id), nullable=False)
    Checked = Column(Boolean)

    def beforeInsert(self):
        Record.beforeInsert(self)
        user = User.getRecordById(self.FavoriteId)
        if user and user.CompanyId:
            self.CompanyId = user.CompanyId

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'text', 'Hidde': True}
        res['UserId'] = {'Type': 'integer'}
        res['FavoriteId'] = {'Type': 'integer'}
        res['Checked'] = {'Type': 'boolean'}
        return res

Index('UserFavorite', UserFavorite.UserId, UserFavorite.FavoriteId, unique=True)

Base.metadata.create_all(engine)
