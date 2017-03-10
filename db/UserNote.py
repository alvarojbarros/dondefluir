from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime
from dbconnect import engine,MediumText,Session
from Record import Record
from sqlalchemy.ext.declarative import declarative_base
from Tools import *
from User import User
from Company import Company
from flask_login import current_user

Base = declarative_base()

class UserNote(Base,Record):

    __tablename__ = 'usernote'
    id = Column(Integer, primary_key=True)
    UserId = Column(String(20), ForeignKey(User.id), nullable=False)
    ProfId = Column(String(20), ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id))
    TransDate = Column(DateTime)
    Note = Column(MediumText())

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['UserId'] = {'Type': 'text','Hidde': True}
        #res['ProfId'] = {'Type': 'text', 'Label': 'Usuario', 'Input': 'combo','LinkTo':{'Table':'User','Show':['Name']}}
        #res['CompanyId'] = {'Type': 'text', 'Label': 'Empresa', 'Input': 'combo','LinkTo':{'Table':'Company','Show':['Name']}}
        #res['TransDate'] = {'Type': 'datetime', 'Label': 'Fecha','Input':'datetime'}
        res['ProfId'] = {'Type': 'text', 'Hidde': True}
        res['CompanyId'] = {'Type': 'text', 'Hidde': True}
        res['TransDate'] = {'Type': 'datetime', 'Hidde': True}
        res['Note'] = {'Type': 'text', 'Label': 'Nota','Input':'textarea','rows':'4','cols':'50'}
        return res

    @classmethod
    def getRecordList(cls,TableClass,custId=None):
        session = Session()
        if current_user.UserType==3:
            records = session.query(cls).filter_by(UserId=current_user.id)
        elif current_user.UserType in (0,1):
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId,UserId=custId)
        elif current_user.UserType==2:
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId,UserId=custId,ProfId=current_user.id)
        session.close()
        return records

    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if current_user.UserType in (1,2):
            if fieldname in ('ProfId','TransDate','CompanyId'):
                return 2 #solo insertar nuevos

    def defaults(self):
        self.TransDate = now()
        self.ProfId = current_user.id
        self.CompanyId = current_user.CompanyId

    @classmethod
    def canUserDelete(self):
        return False

Base.metadata.create_all(engine)
