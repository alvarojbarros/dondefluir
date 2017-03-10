from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time, Index
from dbconnect import engine
from flask_login import current_user
from Service import Service
from Company import Company
from User import User
from Record import Record
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserService(Base,Record):
    __tablename__ = 'userservice'
    id = Column(Integer, primary_key=True)
    UserId = Column(String(20), ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id), nullable=False)
    ServiceId = Column(Integer, ForeignKey(Service.id), nullable=False)

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'text', 'Label':'Codigo','Hidde': True,'Readonly':1}
        res['CompanyId'] = {'Type': 'integer', 'Label': 'Empresa', 'Hidde': True}
        res['UserId'] = {'Type': 'text', 'Label': 'Usuario', 'Input': 'combo','Level':[0,1],'LinkTo':{'Table':'User','Show':['Name']}}
        res['ServiceId'] = {'Type': 'integer', 'Label': 'Servicio', 'Input': 'combo','Level':[0,1],'LinkTo':{'Table':'Service','Show':['Name']}}
        return res

    def check(self):
        if hasattr(self,"_new"):
            self.CompanyId = current_user.CompanyId
        if not self.UserId: return Error("Completar Usuario")
        if not self.ServiceId: return Error("Completar Servicio")
        return True

    @classmethod
    def getRecordList(cls,TableClass):
        if current_user.UserType==1:
            session = Session()
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId)
            session.close()
        else:
            records = Record.getRecordList(TableClass)
        return records

Index('UserService', UserService.UserId, UserService.ServiceId, unique=True)

Base.metadata.create_all(engine)
