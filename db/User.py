#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time, DateTime
from tools.dbconnect import engine,MediumText,Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_login import current_user
from dondefluir.db.Company import Company
import tools.DBTools
from tools.Record import Record,DetailRecord
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *

Base = declarative_base()

class User(Base,Record,UserMixin):
    __tablename__ = 'user'
    id = Column(String(50), primary_key=True)
    Password = Column(String(20))
    Active = Column(Integer)
    UserType = Column(Integer)
    CompanyId = Column(Integer, ForeignKey(Company.id))
    Name = Column(String(40))
    Title = Column(String(40))
    FindMe = Column(Integer)
    EditSchedule = Column(Integer)
    FixedSchedule = Column(Integer)
    MinTime = Column(Integer)
    MaxTime = Column(Integer)
    ShowDays = Column(Integer)
    Phone = Column(String(40))
    Comment = Column(MediumText())
    City = Column(String(100))
    Address = Column(String(100))
    ImageProfile = Column(String(100))
    NtfActivityCancel = Column(Integer)
    NtfActivityNew = Column(Integer)
    NtfActivityChange = Column(Integer)
    NtfActivityReminder = Column(Integer)
    NtfReminderDays = Column(Integer)
    NtfReminderHours = Column(Integer)
    ShowFromDays = Column(Integer)

    Schedules = relationship('UserSchedule', cascade="all, delete-orphan")

    #def __repr__(self):
    #    return "<User(Active='%s', AcessGroup='%s', Password='%s')>" % (self.Active, self.AcessGroup, self.Password)

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'text', 'Label': 'Email','Input':'text','Readonly':1}
        res['Password'] = {'Type': 'text', 'Label': 'Password','Input':'password'}
        res['Active'] = {'Type': 'integer', 'Label': 'Activo', 'Input': 'checkbox','Level':[0]}
        res['UserType'] = {'Type': 'integer', 'Label': 'Tipo de Usuario', 'Input': 'combo', \
            'Values': {0: 'Super',1: 'Administrador',2: 'Profesional',3: 'Cliente'},'Level':[0,1],\
            'ValuesLevel':{0:[0,1,2,3],1:[1,2,3],2:[3],3:[]}}
        res['CompanyId'] = {'Type': 'integer', 'Label': 'Empresa', 'Input': 'combo','Level':[0],'LinkTo':{'Table':'Company','Show':['Name']}}
        res['Name'] = {'Type': 'text', 'Label': 'Nombre', 'Input': 'text'}
        res['Title'] = {'Type': 'text', 'Label': 'Profesión', 'Input': 'text','Level':[0,1,2]}
        res['FindMe'] = {'Type': 'integer', 'Label': 'Aparecer en Buscador', 'Input': 'checkbox','Level':[0,1,2]}
        res['FixedSchedule'] = {'Type': 'integer', 'Label': 'Horarios Fijos', 'Input': 'checkbox','Level':[0,1,2]}
        res['MinTime'] = {'Type': 'integer', 'Label': 'Tiempo Mínimo', 'Input': 'integer','Level':[0,1,2]}
        res['MaxTime'] = {'Type': 'integer', 'Label': 'Timpo Máximo', 'Input': 'integer','Level':[0,1,2]}
        res['ShowDays'] = {'Type': 'integer', 'Label': 'Disponibilidad Hasta', 'Input': 'integer','Level':[0,1,2]}
        res['ShowFromDays'] = {'Type': 'integer', 'Label': 'Disponibilidad Desde', 'Input': 'integer','Level':[0,1,2]}
        res['Phone'] = {'Type': 'text', 'Label': 'Teléfono', 'Input': 'text'}
        res['Comment'] = {'Type': 'text', 'Label': 'Descripción','Input':'textarea','rows':'4','Level':[0,1,2]}
        res['Address'] = {'Type': 'text', 'Label': 'Dirección', 'Input': 'text'}
        res['City'] = {'Type': 'text', 'Label': 'Ciudad', 'Input': 'text'}
        res['EditSchedule'] = {'Type': 'integer', 'Label': 'Editar Agenda', 'Input': 'combo', \
            'Values': {0: 'SI',1: 'NO'},'Level':[0,1]}
        res['Schedules'] = {'Type':[],'Label':'Horarios','Class':'UserSchedule',\
            'fieldsDefinition': UserSchedule.fieldsDefinition(),'Level':[0,1,2]}
        res['Favorite'] = {'Type': 'integer', 'Label': 'Agregar a Favoritos', 'Input': 'checkbox','Level':[0,1,2],'Persistent':False, \
            'Method':'getFavorite()','onClick': 'setFavorite(this)' }
        res['ImageProfile'] = {'Type': 'text', 'Label': 'Imagen de Perfil', 'Input': 'fileinput'}
        res['NtfActivityNew'] = {'Type': 'integer', 'Label': 'Nueva Actividad', 'Input': 'checkbox'}
        res['NtfActivityCancel'] = {'Type': 'integer', 'Label': 'Actividad Cancelada', 'Input': 'checkbox'}
        res['NtfActivityChange'] = {'Type': 'integer', 'Label': 'Actividad Modificada', 'Input': 'checkbox'}
        res['NtfActivityReminder'] = {'Type': 'integer', 'Label': 'Recordatorio de Actividad ', 'Input': 'checkbox'}
        res['NtfReminderDays'] = {'Type': 'integer', 'Label': 'Días de Antelación para Recordatorio', 'Input': 'integer'}
        res['NtfReminderHours'] = {'Type': 'integer', 'Label': 'Horas de Antelación para Recordatorio', 'Input': 'integer'}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {"Name":"Información del Usuario", "Fields": [[0,["Name","Phone"]],[3,["Address","City"]] \
            ,[6,["Comment"]],[7,["Title","ImageProfile"]]]}
        Tabs[1] = {"Name":"Configuración del Usuario", "Fields": [[0,["id","Password"]],[2,["UserType","Active"]] \
            ,[4,["CompanyId","EditSchedule"]],[6,["FindMe"]],[7,["Favorite"]]]}
        Tabs[2] = {"Name":"Agenda","Fields": [[0,["ShowFromDays","ShowDays"]],[1,["FixedSchedule"]],[2,["MaxTime","MinTime"]],[3,["Schedules"]]]}
        Tabs[3] = {"Name":"Notificaciones", "Fields": [[0,["NtfActivityNew","NtfActivityCancel"]] \
            ,[2,["NtfActivityChange","NtfActivityReminder"]]]}
        return Tabs

    def filterFields(self,fields):
        #filtro de campo por tipo de usuario
        filters = {3:['Title','FindMe','FixedSchedule','MinTime','MaxTime','EditSchedule','Schedules','ShowDays','ShowFromDays','Comment']}
        if self.UserType in filters:
            filters = filters[self.UserType]
            for fn in filters:
                if fn in fields:
                    del fields[fn]
        if (current_user.id==self.id) and (self.EditSchedule):
            del fields['Schedules']
        if self.id:
            del fields['Password']

    @classmethod
    def getUserFromDataBase(cls,username,all=False):
        user = cls.getRecordById(username)
        if user:
            if all:
                return User(user.id,user.Password,user.Active,user.UserType)
            else:
                return user

    @classmethod
    def addNewUser(cls,username,password,name):
        from sqlalchemy.orm import sessionmaker
        session = Session()
        new_user = User(username,password,0,None)
        new_user.syncVersion = 0
        new_user.UserType = 3
        new_user.Name = name
        session.add(new_user)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            session.close()
            return Error(str(e))
        user = session.query(User).filter_by(id=username).first()
        session.close()
        if user:
            return User(user.id,user.Password,user.Active,user.UserType,user.CompanyId)

    @classmethod
    def get(cls,username):
        user_data = cls.getUserFromDataBase(username)
        return user_data

    def __init__(self, id=None, Password=None, Active=None, UserType=None, CompanyId=None, EditSchedule=None):
        self.id = id
        self.Password = Password
        self.Active = Active
        self.UserType = UserType
        self.CompanyId = CompanyId
        self.EditSchedule = EditSchedule

    def check(self):
        if hasattr(self,"_new") and not self.id: return Error("Completar Código")
        if self.UserType==3:
            self.CompanyId = None
        if current_user.UserType in (1,2) and self.UserType in (1,2,3):
            self.CompanyId = current_user.CompanyId
        if current_user.UserType in (1,2) and not self.CompanyId: return Error("Completar Empresa")
        return True

    @classmethod
    def getRecordList(cls,TableClass,limit=None,order_by=None,desc=None):
        if current_user.UserType==1:
            session = Session()
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId)
            session.close()
        elif current_user.UserType==2:
            session = Session()
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId,UserType=3)
            session.close()
        else:
            records = Record.getRecordList(TableClass)
        return records

    @classmethod
    def canUserCreate(self):
        if current_user.UserType in (0,1):
            return True

    @classmethod
    def canUserDelete(self):
        if current_user.UserType == 0:
            return True

    @classmethod
    def canUserEdit(self,recordId):
        if current_user.UserType in (0,1) or current_user.id==recordId:
            return True

    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if current_user.UserType==1:
            if record and record.UserType==3:
                return 1 #solo insertar nuevos
        if current_user.UserType==2:
            return 2 #nunca

    def getFavorite(self):
        from dondefluir.db.UserFavorite import UserFavorite
        session = Session()
        record = session.query(UserFavorite).filter_by(UserId=current_user.id,FavoriteId=self.id).first()
        if record and record.Checked:
            return 1
        return 0

    def getField(self,fieldname):
        if getattr(self,fieldname): return getattr(self,fieldname)
        elif self.CompanyId:
            compay = Company.getRecordById(self.CompanyId)
            if company and getattr(company,fieldname):
                return getattr(company,fieldname)

    @classmethod
    def getRecordTitle(self):
        return ['Name']


class UserSchedule(Base,DetailRecord):
    __tablename__ = 'userschedule'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(20), ForeignKey('user.id'), nullable=False)
    StartTime = Column(Time)
    EndTime = Column(Time)
    d1 = Column(Integer)
    d2 = Column(Integer)
    d3 = Column(Integer)
    d4 = Column(Integer)
    d5 = Column(Integer)
    d6 = Column(Integer)
    d7 = Column(Integer)

    @classmethod
    def fieldsDefinition(cls):
        res = DetailRecord.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['StartTime'] = {'Type': 'time', 'Label': 'Desde','Input':'time'}
        res['EndTime'] = {'Type': 'time', 'Label': 'Hasta','Input':'time'}
        res['d1'] = {'Type': 'integer', 'Label': 'Lu', 'Input': 'checkbox'}
        res['d2'] = {'Type': 'integer', 'Label': 'Ma', 'Input': 'checkbox'}
        res['d3'] = {'Type': 'integer', 'Label': 'Mi', 'Input': 'checkbox'}
        res['d4'] = {'Type': 'integer', 'Label': 'Ju', 'Input': 'checkbox'}
        res['d5'] = {'Type': 'integer', 'Label': 'Vi', 'Input': 'checkbox'}
        res['d6'] = {'Type': 'integer', 'Label': 'Sa', 'Input': 'checkbox'}
        res['d7'] = {'Type': 'integer', 'Label': 'Do', 'Input': 'checkbox'}
        res['__order__'] = cls.fieldsOrder()
        res['__lenght__'] = "1"
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs['0'] = ['StartTime','EndTime']
        Tabs['1'] = ['d1','d2','d3','d4','d5','d6','d7']
        return Tabs

    @classmethod
    def fieldsOrder(cls):
        return ['id','StartTime','EndTime','d1','d2','d3','d4','d5','d6','d7']

    def fieldsDetail(self):
        return []

#Index('Email', User.Email, unique=True)

Base.metadata.create_all(engine)
