from sqlalchemy import Table, Column, Integer, Boolean, String, ForeignKey, Index
from dbconnect import engine
from User import User
from Company import Company
import DBTools
from Record import Record
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserFavorite(Base,Record):
    __tablename__ = 'userfavorite'
    id = Column(Integer, primary_key=True)
    UserId = Column(String(20), ForeignKey(User.id), nullable=False)
    FavoriteId = Column(String(20), ForeignKey(User.id), nullable=False)
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
        res['UserId'] = {'Type': 'text'}
        res['FavoriteId'] = {'Type': 'text'}
        res['Checked'] = {'Type': 'boolean'}
        return res

Index('UserFavorite', UserFavorite.UserId, UserFavorite.FavoriteId, unique=True)

Base.metadata.create_all(engine)
