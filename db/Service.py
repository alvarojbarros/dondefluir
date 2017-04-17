#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time
from tools.dbconnect import engine,Session
from flask_login import current_user
from dondefluir.db.Company import Company
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Service(Base,Record):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    Name = Column(String(40))
    CompanyId = Column(Integer, ForeignKey(Company.id), nullable=False)

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'text','Hidde': True,'Readonly':1}
        res['Name'] = {'Type': 'text', 'Label': 'Nombre', 'Input': 'text'}
        res['CompanyId'] = {'Type': 'integer', 'Label': 'Empresa', 'Input': 'combo','Level':[0],'LinkTo':{'Table':'Company','Show':['Name']}}
        return res

    def check(self):
        if hasattr(self,"_new"):
            self.CompanyId = current_user.CompanyId
        if not self.Name: return Error("Debe Completar el Nombre")
        return True

    @classmethod
    def getRecordList(cls,TableClass):
        if current_user.UserType in (1,2,3):
            session = Session()
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId)
            session.close()
        else:
            records = Record.getRecordList(TableClass)
        return records

Base.metadata.create_all(engine)
