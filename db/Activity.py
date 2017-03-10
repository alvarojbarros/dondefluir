from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, Time, Float
from tools.dbconnect import engine,MediumText,Session
from tools.Record import Record,DetailRecord
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
from dondefluir.db.User import User
from dondefluir.db.Company import Company
from dondefluir.db.Service import Service
from flask_login import current_user
from sqlalchemy.orm import relationship

Base = declarative_base()

class Activity(Base,Record):

    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    CustId = Column(String(20), ForeignKey(User.id))
    ProfId = Column(String(20), ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id))
    ServiceId = Column(Integer, ForeignKey(Service.id))
    Type = Column(Integer)
    Comment = Column(String(100))
    Image = Column(String(100))
    MaxPersons = Column(Integer)
    Price = Column(Float)
    Description = Column(MediumText())
    Users = relationship('ActivityUsers', cascade="all, delete-orphan")
    Schedules = relationship('ActivitySchedules', cascade="all, delete-orphan")
    Status = Column(Integer)

    def __init__(self):
        super(self.__class__,self).__init__()
        #super().__init__()

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['CustId'] = {'Type': 'text', 'Label': 'Cliente', 'Input': 'combo','LinkTo':{'Table':'User','Show':['Name'],'Method':'getCustomer'}}
        res['ProfId'] = {'Type': 'text', 'Label': 'Profesional', 'Input': 'combo','LinkTo':{'Table':'User','Show':['Name']}}
        res['CompanyId'] = {'Type': 'text', 'Label': 'Empresa', 'Input': 'combo','LinkTo':{'Table':'Company','Show':['Name']}}
        res['ServiceId'] = {'Type': 'text', 'Label': 'Servicio', 'Input': 'combo','LinkTo':{'Table':'Service','Show':['Name']}}
        res['Comment'] = {'Type': 'text', 'Label': 'Comment', 'Input':'text'}
        res['Type'] = {'Type': 'integer', 'Label': 'Tipo', 'Input': 'combo','Values': {0: 'Cita',1: 'Curso'},'Level':[0,1,2]}
        res['Users'] = {'Type':[],'Label':'Usuarios','Class':'ActivityUsers', 'fieldsDefinition': ActivityUsers.fieldsDefinition(),'Level':[0,1,2]}
        res['Schedules'] = {'Type':[],'Label':'Horarios','Class':'ActivitySchedules', 'fieldsDefinition': ActivitySchedules.fieldsDefinition(),'Level':[0,1,2,3]}
        res['Image'] = {'Type': 'text', 'Label': 'Imagen', 'Input': 'fileinput','Level':[0,1,2]}
        res['MaxPersons'] = {'Type': 'integer', 'Label': 'Cupos', 'Input': 'integer','Level':[0,1,2]}
        res['Price'] = {'Type': 'float', 'Label': 'Valor', 'Input': 'number','Level':[0,1,2]}
        res['Description'] = {'Type': 'text', 'Label': 'Descripcion','Input':'textarea','rows':'4','Level':[0,1,2]}
        res['Status'] = {'Type': 'integer', 'Label': 'Estado', 'Input': 'combo','Values': {0: 'Solicitada',1: 'Confirmada',2:'Cancelada'},'Level':[0,1,2]}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {"Name":"Informacion", "Fields": [(0,["CompanyId","ProfId"]),(2,["CustId","ServiceId","Status"]),(4,["Comment","Type"])]}
        Tabs[1] = {"Name":"Horarios","Fields": [(0,["Schedules"])]}
        Tabs[2] = {"Name":"Curso","Fields": [(0,["MaxPersons","Price","Image"]),(1,["Description"])]}
        Tabs[3] = {"Name":"Clientes","Fields": [(0,["Users"])]}
        return Tabs


    @classmethod
    def getRecordList(cls,TableClass,custId=None):
        if current_user.UserType==3:
            session = Session()
            records = session.query(cls) \
                .filter_by(CustId=current_user.id) \
                .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                .with_entities(cls.Comment,cls.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                ,ActivitySchedules.EndTime,cls.id,cls.Status)
            session.close()
        elif current_user.UserType in (1,2):
            session = Session()
            if not custId:
                records = session.query(cls) \
                    .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                    .with_entities(cls.Comment,cls.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                    ,ActivitySchedules.EndTime,cls.id,cls.Status)\
                    .filter(Activity.CompanyId==current_user.CompanyId)
            else:
                records = session.query(cls) \
                    .filter_by(CompanyId=current_user.CompanyId,CustId=custId) \
                    .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                    .with_entities(cls.Comment,cls.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                    ,ActivitySchedules.EndTime,cls.id)
            session.close()
        else:
            session = Session()
            records = session.query(cls).join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
                .with_entities(cls.Comment,cls.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                ,ActivitySchedules.EndTime,cls.id,cls.Status)
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
        self.ProfId = current_user.id
        self.CompanyId = current_user.CompanyId

    def check(self):
        if not len(self.Schedules):
            return Error("Debe ingresar horarios")
        if self.Type==1 and not self.Comment:
            return Error("Debe ingresar Comentario")
        return True

    @classmethod
    def canUserCreate(self):
        if current_user.UserType in (0,1,2):
            return True

    '''@classmethod
    def getfieldsDefinition(cls,record):
        res = Record.getfieldsDefinition(record)
        print(res)
        if record.id and not record.Type:
            del res['Users']
        return res '''

    def afterCommitUpdate(self):
        if current_user.id!=self.ProfId:
            user = User.getRecordById(self.ProfId)
            if user and user.NtfActivityNew and user.Email:
                msj = "\n"
                msj += "Fecha: %s\n" % self.TransDate.strftime('%d/%m/%Y')
                msj += "Horario: %s a %s\n" % (self.StartTime.strftime('%M:%H'),self.EndTime.strftime('%M:%H'))
                msj += "\n"
                if self.CustId:
                    customer = User.getRecordById(self.CustId)
                    if customer:
                        if customer.Name:
                            msj += "Cliente: %s\n" % customer.Name
                        else:
                            msj += "Cliente: %s\n" % customer.id
                        if customer.Phone:
                            msj += "Telefono: %s\n" % customer.Phone
                        if customer.Email:
                            msj += "Email: %s\n" % customer.Email
                msj += "\n"
                return mail.sendMail(user.Email,'Tiene una nueva Actividad',msj)
        if not self.Type and self.current_user.id==self.CustId:
            if current_user.NtfActivityNew and current_user.Email:
                if self.ProfId:
                    prof = User.getRecordById(self.ProfId)
                    if prof:
                        self.sendCustomerMailNewActivity(prof,user.Email)
        if self.Type and self.ProfId:
            prof = User.getRecordById(self.ProfId)
            if prof:
                for row in self.Users:
                    customer = User.getRecordById(row.CustId)
                    if customer and customer.NtfActivityNew and customer.Email:
                        self.sendCustomerMailNewActivity(prof,customer.Email)


    def afterCommitInsert(self):
        return True
        if current_user.id!=self.ProfId:
            user = User.getRecordById(self.ProfId)
            if user and user.NtfActivityNew and user.Email:
                msj = "\n"
                msj += "Fecha: %s\n" % self.TransDate.strftime('%d/%m/%Y')
                msj += "Horario: %s a %s\n" % (self.StartTime.strftime('%M:%H'),self.EndTime.strftime('%M:%H'))
                msj += "\n"
                if self.CustId:
                    customer = User.getRecordById(self.CustId)
                    if customer:
                        if customer.Name:
                            msj += "Cliente: %s\n" % customer.Name
                        else:
                            msj += "Cliente: %s\n" % customer.id
                        if customer.Phone:
                            msj += "Telefono: %s\n" % customer.Phone
                        if customer.Email:
                            msj += "Email: %s\n" % customer.Email
                msj += "\n"
                return mail.sendMail(user.Email,'Tiene una nueva Actividad',msj)
        if not self.Type and self.current_user.id==self.CustId:
            if current_user.NtfActivityNew and current_user.Email:
                if self.ProfId:
                    prof = User.getRecordById(self.ProfId)
                    if prof:
                        self.sendCustomerMailUpdateActivity(prof,user.Email)
        ''' if self.Type and self.ProfId:
            prof = User.getRecordById(self.ProfId)
            if prof:
                for row in self.Users:
                    customer = User.getRecordById(row.CustId)
                    if customer and customer.NtfActivityNew and customer.Email:
                        self.sendCustomerMailNewActivity(prof,customer.Email) '''

    def sendCustomerMailUpdateActivity(self,prof,CustEmail):
        self.sendCustomerMailActivity(CustEmail,'Actividad Modificada',msj)

    def sendCustomerMailNewActivity(self,prof,CustEmail):
        self.sendCustomerMailActivity(CustEmail,'Tiene una nueva Actividad',msj)

    def sendCustomerMailActivity(self,prof,CustEmail,Subject):
        msj = "\n"
        msj += "Descripcion: %s\n" % self.Comment
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
        if address: msj += "Direccion: %s\n" % address
        city = prof.getField('City')
        if city: msj += "Ciudad: %s\n" % city
        msj += "\n"
        return mail.sendMail(CustEmail,Subject,msj)


    def afterCommitUpdate(self):
        pass


class ActivityUsers(Base,DetailRecord):
    __tablename__ = 'activityusers'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)
    CustId = Column(String(20), ForeignKey(User.id), nullable=False)

    @classmethod
    def fieldsDefinition(cls):
        res = DetailRecord.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['CustId'] = {'Type': 'text', 'Label': 'Cliente', 'Input': 'combo','LinkTo':{'Table':'User','Show':['Name']}}
        res['__order__'] = cls.fieldsOrder()
        return res

    @classmethod
    def fieldsOrder(cls):
        return ['id','CustId']

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
        res['TransDate'] = {'Type': 'date', 'Label': 'Fecha','Input':'date'}
        res['StartTime'] = {'Type': 'time','Label': 'Desde','Input':'time'}
        res['EndTime'] = {'Type': 'time', 'Label': 'Hasta','Input':'time'}
        res['__order__'] = cls.fieldsOrder()
        return res

    @classmethod
    def fieldsOrder(cls):
        return ['id','TransDate','StartTime','EndTime']

    @classmethod
    def getUserFieldsReadOnly(cls,fieldname):
        if current_user.UserType == 3:
            if fieldname in ('TransDate','StartTime','EndTime'):
                return 2 # nunca
        return 0 # siempre


Base.metadata.create_all(engine)
