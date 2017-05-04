#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, Time, Float
from tools.dbconnect import engine,MediumText,Session
from tools.Record import Record,DetailRecord
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
from dondefluir.db.User import User
from dondefluir.db.Company import Company
from dondefluir.db.Service import Service
from dondefluir.db.UserService import UserService
from dondefluir.db.Notification import Notification
from flask_login import current_user
from sqlalchemy.orm import relationship,aliased
from sqlalchemy import or_

Base = declarative_base()

class Activity(Base,Record):

    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    CustId = Column(String(20), ForeignKey(User.id), nullable=True)
    ProfId = Column(String(20), ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id))
    ServiceId = Column(Integer, ForeignKey(Service.id), nullable=True)
    Type = Column(Integer)
    Comment = Column(String(100))
    Image = Column(String(100))
    MaxPersons = Column(Integer)
    Price = Column(Float)
    Description = Column(MediumText())
    Users = relationship('ActivityUsers', cascade="all, delete-orphan")
    Schedules = relationship('ActivitySchedules', cascade="all, delete-orphan")
    Status = Column(Integer)

    StatusList = ['Tomar este curso','Anular Inscripción']

    def __init__(self):
        super(self.__class__,self).__init__()
        #super().__init__()

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['CustId'] = {'Type': 'text', 'Label': 'Cliente', 'Input': 'combo','LinkTo':{'Table':'User','Show':['Name'],'Method':'getCustomer','Params':"{'favorite':False}"}}
        res['ProfId'] = {'Type': 'text', 'Label': 'Profesional', 'Input': 'combo','LinkTo':{'Table':'User','Show':['Name']}}
        res['CompanyId'] = {'Type': 'text', 'Label': 'Empresa', 'Input': 'combo','LinkTo':{'Table':'Company','Show':['Name']}}
        res['ServiceId'] = {'Type': 'text', 'Label': 'Servicio', 'Input': 'combo','LinkTo':{'Table':'Service','Show':['Name']}}
        res['Comment'] = {'Type': 'text', 'Label': 'Comentario', 'Input':'text'}
        res['Type'] = {'Type': 'integer', 'Label': 'Tipo', 'Input': 'combo','Values': {0: 'Cita',1: 'Curso',2:'Evento'},'Level':[0,1,2]}
        res['Users'] = {'Type':[],'Class':'ActivityUsers', 'fieldsDefinition': ActivityUsers.fieldsDefinition(),'Level':[0,1,2],'htmlView':ActivityUsers.htmlView()}
        res['Schedules'] = {'Type':[],'Label':'Horarios','Class':'ActivitySchedules', 'fieldsDefinition': ActivitySchedules.fieldsDefinition(),'Level':[0,1,2,3],'htmlView':ActivitySchedules.htmlView()}
        res['Image'] = {'Type': 'text', 'Label': 'Imagen', 'Input': 'fileinput','Level':[0,1,2]}
        res['MaxPersons'] = {'Type': 'integer', 'Label': 'Cupos', 'Input': 'integer','Level':[0,1,2]}
        res['Price'] = {'Type': 'float', 'Label': 'Valor', 'Input': 'number','Level':[0,1,2]}
        res['Description'] = {'Type': 'text', 'Label': 'Descripción','Input':'textarea','rows':'4','Level':[0,1,2]}
        res['Status'] = {'Type': 'integer', 'Label': 'Estado', 'Input': 'combo','Values': {0: 'Solicitada',1: 'Confirmada',2:'Cancelada'},'Level':[0,1,2]}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {"Name":"Información", "Fields": [[0,["CompanyId","ProfId"]],[2,["CustId","ServiceId","Status"]],[4,["Comment","Type"]]]}
        Tabs[1] = {"Name":"Horarios","Fields": [[0,["Schedules"]]]}
        Tabs[2] = {"Name":"Curso/Evento",'Level':[0,1,2],"Fields": [[0,["MaxPersons","Price","Image"]],[1,["Description"]]]}
        Tabs[3] = {"Name":"Clientes",'Level':[0,1,2],"Fields": [[0,["Users"]]]}
        return Tabs

    @classmethod
    def getEventList(cls,limit=None,order_by=None,desc=None):
        UserProf = aliased(User)
        session = Session()
        records = session.query(cls) \
            .filter(or_(cls.Type==1,cls.Type==2)) \
            .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
            .filter(ActivitySchedules.TransDate>=today()) \
            .join(Company,cls.CompanyId==Company.id)\
            .join(UserProf,cls.ProfId==UserProf.id)\
            .outerjoin(Service,cls.ServiceId==Service.id)\
            .with_entities(cls.Comment,UserProf.Name.label('ProfId'),ActivitySchedules.TransDate,ActivitySchedules.StartTime \
            ,ActivitySchedules.EndTime,cls.id,cls.Status,Company.Name.label('CompanyId')\
            ,Service.Name.label('ServiceId'))
        if order_by and desc: records = records.order_by(ActivitySchedules.TransDate.desc())
        elif order_by: records = records.order_by(ActivitySchedules.TransDate)
        if limit: records = records.limit(limit)
        session.close()
        return records



    @classmethod
    def getRecordList(cls,TableClass,custId=None,limit=None,order_by=None,desc=None):
        UserProf = aliased(User)
        UserCust = aliased(User)
        if current_user.UserType==3:
            session = Session()
            records = session.query(cls) \
                .filter_by(CustId=current_user.id) \
                .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                .filter(ActivitySchedules.TransDate>=today()) \
                .join(Company,cls.CompanyId==Company.id)\
                .join(UserProf,cls.ProfId==UserProf.id)\
                .outerjoin(UserCust,cls.CustId==UserCust.id)\
                .outerjoin(Service,cls.ServiceId==Service.id)\
                .with_entities(cls.Comment,UserProf.Name.label('ProfId'),ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                ,ActivitySchedules.EndTime,cls.id,cls.Status,UserCust.Name.label('CustId'),Company.Name.label('CompanyId')\
                ,Service.Name.label('ServiceId'))
            if order_by and desc: records = records.order_by(ActivitySchedules.TransDate.desc())
            elif order_by: records = records.order_by(ActivitySchedules.TransDate)
            if limit: records = records.limit(limit)
            session.close()
        elif current_user.UserType in (1,2):
            session = Session()
            if not custId:
                records = session.query(cls) \
                    .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                    .filter(ActivitySchedules.TransDate>=today()) \
                    .join(Company,cls.CompanyId==Company.id)\
                    .join(UserProf,cls.ProfId==UserProf.id)\
                    .outerjoin(UserCust,cls.CustId==UserCust.id)\
                    .outerjoin(Service,cls.ServiceId==Service.id)\
                    .with_entities(cls.Comment,UserProf.Name.label('ProfId'),ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                    ,ActivitySchedules.EndTime,cls.id,cls.Status,UserCust.Name.label('CustId'),Company.Name.label('CompanyId')\
                    ,Service.Name.label('ServiceId'))\
                    .filter(Activity.CompanyId==current_user.CompanyId)
                if order_by and desc: records = records.order_by(ActivitySchedules.TransDate.desc())
                elif order_by: records = records.order_by(ActivitySchedules.TransDate)
                if limit: records = records.limit(limit)
            else:
                records = session.query(cls) \
                    .filter_by(CompanyId=current_user.CompanyId,CustId=custId) \
                    .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                    .filter(ActivitySchedules.TransDate>=today()) \
                    .join(Company,cls.CompanyId==Company.id)\
                    .join(UserProf,cls.ProfId==UserProf.id)\
                    .outerjoin(UserCust,cls.CustId==UserCust.id)\
                    .outerjoin(Service,cls.ServiceId==Service.id)\
                    .with_entities(cls.Comment,UserProf.Name.label('ProfId'),ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                    ,ActivitySchedules.EndTime,cls.id,cls.Status,UserCust.Name.label('CustId'),Company.Name.label('CompanyId')\
                    ,Service.Name.label('ServiceId'))
                if order_by and desc: records = records.order_by(ActivitySchedules.TransDate.desc())
                elif order_by: records = records.order_by(ActivitySchedules.TransDate)
                if limit: records = records.limit(limit)
            session.close()
        else:
            session = Session()
            records = session.query(cls).join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                .filter(ActivitySchedules.TransDate>=today()) \
                .join(Company,cls.CompanyId==Company.id)\
                .join(UserProf,cls.ProfId==UserProf.id)\
                .outerjoin(UserCust,cls.CustId==UserCust.id)\
                .outerjoin(Service,cls.ServiceId==Service.id)\
                .with_entities(cls.Comment,UserProf.Name.label('ProfId'),ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                ,ActivitySchedules.EndTime,cls.id,cls.Status,UserCust.Name.label('CustId'),Company.Name.label('CompanyId')\
                ,Service.Name.label('ServiceId'))
            if order_by and desc: records = records.order_by(ActivitySchedules.TransDate.desc())
            elif order_by: records = records.order_by(ActivitySchedules.TransDate)
            if limit: records = records.limit(limit)
            session.close()
        return records

    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if current_user.UserType == 1:
            if fieldname in ['Type']:
                return 1 #solo insertar nuevos
            elif fieldname in ['CompanyId']:
                return 2 # nunca
        if current_user.UserType == 2:
            if fieldname in ['Type']:
                return 1 #solo insertar nuevos
            elif fieldname in ('CustId','ProfId','CompanyId'):
                return 2 # nunca
        if current_user.UserType == 3:
            if fieldname in ['Comment']:
                return 1 #solo insertar nuevos
            elif fieldname in ('ProfId','CompanyId','TransDate','StartTime','EndTime','CustId'):
                return 2 # nunca
        return 0 # siempre

    def defaults(self):
        #self.ProfId = current_user.id
        self.Status = 0
        self.CompanyId = current_user.CompanyId

    def check(self):
        #if not self.ServiceId:
        #    return Error("Debe Elegir un Servicio")
        if not len(self.Schedules):
            return Error("Debe ingresar horarios")
        if self.Type in (1,2) and not self.Comment:
            return Error("Debe ingresar Nombre del Curso o Evento")
        return True

    @classmethod
    def canUserCreate(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def canUserAddRow(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def canUserDeleteRow(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def customGetFieldsDefinition(cls,record,res):
        if current_user.UserType!=3:
            res['Comment']['Label'] = 'Nombre de Curso/Evento'
        return res


    '''@classmethod
    def getfieldsDefinition(cls,record):
        res = Record.getfieldsDefinition(record)
        print(res)
        if record.id and not record.Type:
            del res['Users']
        return res '''

    def afterCommitUpdate(self):
        True
        '''if current_user.id!=self.ProfId:
            user = User.getRecordById(self.ProfId)
            if user and user.NtfActivityNew:
                msj = "\n"
                msj += "Fecha: %s\n" % self.TransDate.strftime('%d/%m/%Y')
                msj += "Horario: %s a %s\n" % (self.StartTime.strftime('%M:%H'),self.EndTime.strftime('%M:%H'))
                msj += "\n"
                if self.CustId:
                    customer = User.getRecordById(self.CustId)
                    if customer:
                        if customer.Name:
                            msj += "Cliente: %s\n" % customer.Name
                        if customer.Phone:
                            msj += "Telefono: %s\n" % customer.Phone
                        msj += "Email: %s\n" % customer.id
                msj += "\n"
                return mail.sendMail(user.id,'Tiene una nueva Actividad',msj)
        if not self.Type and self.current_user.id==self.CustId:
            if current_user.NtfActivityNew:
                if self.ProfId:
                    prof = User.getRecordById(self.ProfId)
                    if prof:
                        self.sendCustomerMailNewActivity(prof,user.id)
        if self.Type and self.ProfId:
            prof = User.getRecordById(self.ProfId)
            if prof:
                for row in self.Users:
                    customer = User.getRecordById(row.CustId)
                    if customer and customer.NtfActivityNew:
                        self.sendCustomerMailNewActivity(prof,customer.id) '''


    def setNotification(self,comment,user_id):
        ntf = Notification()
        ntf.defaults()
        ntf.UserId = user_id
        ntf.Comment = "%s: %s" %(comment,self.Comment)
        ntf.Action = ""
        session = Session()
        res = ntf.save(session)
        if not res: return res
        return True

    def afterUpdate(self):
        if self.ProfId and current_user.id!=self.ProfId:
            if len(self.Users)==len(self.OldFields['Users']):
                res = self.setNotification("Actvididad Modificada",self.ProfId)
                if not res: return res
            else:
                res = self.setNotification("Actvididad Modificada. Nuevos Clientes",self.ProfId)
                if not res: return res
        if self.CustId and current_user.id!=self.CustId:
            res = self.setNotification("Actvididad Modificada",self.CustId)
            if not res: return res
        if len(self.Users)==len(self.OldFields['Users']):
            for row in self.Users:
                if row.CustId:
                    res = self.setNotification("Actvididad Modificada",row.CustId)
                    if not res: return res
        return True

    def afterInsert(self):
        if self.ProfId and current_user.id!=self.ProfId: self.setNotification("Nueva Actvididad",self.ProfId)
        if self.CustId and current_user.id!=self.CustId: self.setNotification("Nueva Actvididad",self.CustId)
        for row in self.Users:
            if row.CustId: self.setNotification("Nueva Actvididad",row.CustId)
        return True
        #user = User.getRecordById(self.ProfId)
        #if user and user.NtfActivityNew:

        '''if current_user.id!=self.ProfId:
            user = User.getRecordById(self.ProfId)
            if user and user.NtfActivityNew:
                msj = "\n"
                msj += "Fecha: %s\n" % self.TransDate.strftime('%d/%m/%Y')
                msj += "Horario: %s a %s\n" % (self.StartTime.strftime('%M:%H'),self.EndTime.strftime('%M:%H'))
                msj += "\n"
                if self.CustId:
                    customer = User.getRecordById(self.CustId)
                    if customer:
                        if customer.Name:
                            msj += "Cliente: %s\n" % customer.Name
                        if customer.Phone:
                            msj += "Telefono: %s\n" % customer.Phone
                        msj += "Email: %s\n" % customer.id
                msj += "\n"
                return mail.sendMail(user.id,'Tiene una nueva Actividad',msj)
        if not self.Type and self.current_user.id==self.CustId:
            if current_user.NtfActivityNew:
                if self.ProfId:
                    prof = User.getRecordById(self.ProfId)
                    if prof:
                        self.sendCustomerMailUpdateActivity(prof,user.id)'''
        ''' if self.Type and self.ProfId:
            prof = User.getRecordById(self.ProfId)
            if prof:
                for row in self.Users:
                    customer = User.getRecordById(row.CustId)
                    if customer and customer.NtfActivityNew:
                        self.sendCustomerMailNewActivity(prof,customer.id) '''

    def sendCustomerMailUpdateActivity(self,prof,CustEmail):
        self.sendCustomerMailActivity(CustEmail,'Actividad Modificada',msj)

    def sendCustomerMailNewActivity(self,prof,CustEmail):
        self.sendCustomerMailActivity(CustEmail,'Tiene una nueva Actividad',msj)

    def sendCustomerMailActivity(self,prof,CustEmail,Subject):
        msj = "\n"
        msj += "Descripción: %s\n" % self.Comment
        msj += "Fecha: %s\n" % self.TransDate.strftime('%d/%m/%Y')
        msj += "Horario: %s a %s\n" % (self.StartTime.strftime('%M:%H'),self.EndTime.strftime('%M:%H'))
        if prof.Name:
            msj += "Profesional: %s\n" % prof.Name
        else:
            msj += "Profesional: %s\n" % prof.id
        phone = prof.getField('Phone')
        if phone: msj += "Telefono: %s\n" % phone
        email = prof.getField('Email')
        if email: msj += "Email: %s\n" % email
        adddress = prof.getField('Address')
        if address: msj += "Dirección: %s\n" % address
        city = prof.getField('City')
        if city: msj += "Ciudad: %s\n" % city
        msj += "\n"
        return mail.sendMail(CustEmail,Subject,msj)


    def getLinkToFromRecord(self,TableClass):
        if TableClass==Service:
            session = Session()
            if self.ProfId:
                records = session.query(UserService)\
                    .filter_by(UserId=self.ProfId)\
                    .join(Service,UserService.ServiceId==Service.id)\
                    .with_entities(Service.id,Service.Name)
            else:
                records = session.query(UserService).join(Service,UserService.ServiceId==Service.id)\
                    .filter_by(CompanyId=self.CompanyId)\
                    .with_entities(Service.id,Service.Name)

            session.close()
            return records
        else:
            return TableClass.getRecordList(TableClass)

    @classmethod
    def getRecordTitle(self):
        return ['ProfId','CustId','ServiceId']


class ActivityUsers(Base,DetailRecord):
    __tablename__ = 'activityusers'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)
    CustId = Column(String(20), ForeignKey(User.id), nullable=False)

    @classmethod
    def fieldsDefinition(cls):
        res = DetailRecord.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['CustId'] = {'Type': 'text', 'Label': 'Cliente', 'Input': 'combo','LinkTo':{'Table':'User','Show':['Name']},'Class':'col-xs-12 p-b-20'}
        res['__order__'] = cls.fieldsOrder()
        return res

    @classmethod
    def fieldsOrder(cls):
        return ['id','CustId']

    @classmethod
    def htmlView(cls):
        return {0: ['id','CustId']}

class ActivitySchedules(Base,DetailRecord):
    __tablename__ = 'activityschedules'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)
    TransDate = Column(Date)
    StartTime = Column(Time)
    EndTime = Column(Time)

    @classmethod
    def fieldsDefinition(cls):
        res = DetailRecord.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['TransDate'] = {'Type': 'date', 'Label': 'Fecha','Input':'date','Class':'col-xs-12 col-sm-3 p-b-20'}
        res['StartTime'] = {'Type': 'time','Label': 'Desde','Input':'time','Class':'col-xs-6 col-sm-3 p-b-20'}
        res['EndTime'] = {'Type': 'time', 'Label': 'Hasta','Input':'time','Class':'col-xs-6 col-sm-3 p-b-20'}
        res['__order__'] = cls.fieldsOrder()
        res['__lenght__'] = "3"
        return res

    @classmethod
    def fieldsOrder(cls):
        return ['id','TransDate','StartTime','EndTime']

    @classmethod
    def htmlView(cls):
        return {0: ['id','TransDate','StartTime','EndTime']}


    @classmethod
    def getUserFieldsReadOnly(cls,fieldname):
        if current_user.UserType == 3:
            if fieldname in ('TransDate','StartTime','EndTime'):
                return 2 # nunca
        return 0 # siempre


Base.metadata.create_all(engine)
