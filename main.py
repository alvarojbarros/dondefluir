# -*- coding: utf-8 -*-

from flask import render_template, request,jsonify
from flask_login import login_required, current_user
from tools.dbconnect import Session
from sqlalchemy.orm import sessionmaker
from flask import Blueprint
from tools.Tools import *
from tools.DBTools import *
from dondefluir.db.User import User
from dondefluir.db.Company import Company
from dondefluir.db.Notification import Notification
from dondefluir.db.Service import Service
from dondefluir.db.Activity import Activity,ActivitySchedules,ActivityUsers
from dondefluir.db.Payment import Payment
from sqlalchemy import or_
import getsettings
settings = getsettings.getSettings()

blue_dondefluir = Blueprint('blue_dondefluir', __name__,template_folder='templates',static_url_path='/dondefluir/static',static_folder='static')

def getActivitiesTableName():
    if current_user.UserType==3:
        return "Mi agenda"
    else:
        return "Todas las actividades"

def getPaymentsTableName():
    if current_user.UserType==3:
        return "Mis Pagos"
    elif current_user.UserType==0:
        return "Pagos"
    else:
        return "Pagos Recibidos"

def addElementToList(Elements,Element,UserType):
    if ('Level' not in Element) or (UserType in Element['Level']):
        Elements[len(Elements)] = Element

def getModules(UserType):
    Elements = {}
    functions = "runSearchBoxOnKey()"
    Element = {'Name':'Usuarios','Level':[0,1,2],'Template':'users.html','Vars':{'Table':'User','Functions':functions} \
        ,'Image':'fa-users'}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Empresas','Level':[0,3],'Template':'company.html','Vars':{'Table':'Company','Functions':functions} \
        ,'Image':'fa-fort-awesome','Module':{0:'Empresas'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':getActivitiesTableName(),'Level':[0,1,2,3],'Template':'activity.html' \
        ,'Vars':{'Table':'Activity','Functions':functions},'Image':'fa-sun-o' \
        ,'Module':{0:'Actividades',1:'Actividades',2:'Actividades'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Mis Profesionales','Level':[0,3],'Template':'professional.html' \
        ,'Vars':{'Table':'User','Functions':functions,'favorite':'true'},'Image':'fa-heart'}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Profesionales','Level':[0,3],'Template':'professional.html'
        ,'Vars':{'Table':'User','Functions':functions,'favorite':'false'},'Image':'fa-magic' \
        ,'Module':{0:'Empresas',1:'Empresa'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Buscar Clientes','Level':[0,1,2],'Template':'customer.html'
        ,'Vars':{'Table':'User','Functions':functions,'favorite':'False'},'Image':'fa-smile-o' \
        ,'Module':{0:'Empresas',1:'Empresa'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Mis Clientes','Level':[0,1,2],'Template':'customer.html' \
        ,'Vars':{'Table':'User','Functions':functions,'favorite':'True'},'Image':'fa-smile-o'}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Servicios','Level':[0,1],'Template':'service.html' \
        ,'Vars':{'Table':'Service','Functions':functions},'Image':'fa-coffee' \
        ,'Module':{0:'Empresas',1:'Empresa'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Servicios por Profesional','Level':[0,1],'Template':'userservice.html' \
        ,'Vars':{'Table':'UserService','Functions':functions},'Image':'fa-suitcase' \
        ,'Module':{0:'Empresas',1:'Empresa'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Vista de calendario','Level':[0,1,2],'Template':'calendar.html' \
        ,'Vars':{'Functions':functions,'UserId':current_user.id,'UserName':current_user.Name},'Image':'ti-calendar p-r-10' \
        ,'Module':{0:'Agenda',1:'Agenda',2:'Agenda'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Cursos y Eventos','Template':'events.html','Vars':{'Table':'Activity'},'Image':'fa-star' \
        ,'Module':{0:'Actividades',1:'Actividades',2:'Actividades'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Notificaciones','Template':'notification.html','Vars':{'Table':'Notification'},'Image':'fa-envelope-o'}
    addElementToList(Elements,Element,UserType)
    Element = {'Name':'Vista de lista','Level':[0,1,2],'Template':'myschedule.html' \
        ,'Vars':{'Template': 'myschedule.html','profId': current_user.id},'Image':'fa-magic' \
        ,'Module':{0:'Agenda',1:'Agenda',2:'Agenda'}.get(UserType,None)}
    addElementToList(Elements,Element,UserType)
    Element = {'Name': getPaymentsTableName(),'Template':'payment.html','Vars':{'Table':'Payment'},'Image':'fa-envelope-o' \
        ,'Level':[0,1,3]}
    addElementToList(Elements,Element,UserType)


    Modules,Names = resumeModules(Elements,UserType)
    return Modules,Names

def resumeModules(Elements,UserType):
    Modules = {}
    for key in Elements:
        Element = Elements[key]
        Element['Vars']['Template'] = Element['Template']
        Element['Vars']['Name'] = Element['Name']
        if 'Module' in Element:
            ModuleName = Element['Module']
            if ModuleName:
                if ModuleName not in Modules:
                    Modules[ModuleName] = {}
                Modules[ModuleName][len(Modules[ModuleName])] = Element
            else:
                Modules[Element.get('Name',None)] = {0: Element}
        else:
            Modules[Element.get('Name',None)] = {0: Element}
    res = {}
    names = {}
    c = 0
    for ModuleName in Modules:
        res[c] = Modules[ModuleName]
        names[c] = ModuleName
        c += 1
    return res,names

def getMyFunction(function,params):
    res = eval('%s(%s)' % (function,str(params)))
    return res

def getProfessional(favorite,companyId):
    session = Session()
    if not favorite:
        records = session.query(User).filter_by(FindMe=True,Closed=0)\
            .join(Company,User.CompanyId==Company.id)
        if companyId:
            records = records.filter(User.CompanyId==companyId)
        records  = records.with_entities(User.id,User.Name,Company.Name.label("CompanyName"),User.Title,User.City)
    else:
        from dondefluir.db.UserFavorite import UserFavorite
        records = session.query(User).filter_by(Closed=0)\
            .join(UserFavorite,User.id==UserFavorite.FavoriteId)\
            .filter_by(UserId=current_user.id,Checked=True)\
            .join(Company,User.CompanyId==Company.id)
        if companyId:
            records = records.filter(User.CompanyId==companyId)
        records  = records.with_entities(User.id,User.Name,Company.Name.label("CompanyName"),User.Title,User.City)
    session.close()
    return records


def getUserNote(*args):
    custId = args[0]['custId']
    from dondefluir.db.UserNote import UserNote
    records = UserNote.getRecordList(UserNote,custId)
    return records


def getCustomer(*args):
    favorite = args[0]['favorite']
    session = Session()
    if not favorite:
        records = session.query(User).filter_by(UserType=3,Closed=0)
    else:
        from dondefluir.db.UserFavorite import UserFavorite
        records = session.query(User).filter_by(UserType=3,Closed=0).join(UserFavorite,User.id==UserFavorite.FavoriteId)\
            .filter_by(UserId=current_user.id,Checked=True)\
            .with_entities(User.id,User.Name)
    session.close()
    return records

def isUserAdmin(*args):
    if current_user.UserType in (0,1):
        return True
    return False

def getBreakCalendarDates(act,dates):
    for d in dates:
        schedule = dates[d]
        for j in range(len(schedule)):
            if act.TransDate==schedule[j]['Date']:
                if (act.StartTime>schedule[j]['StartTime'] and act.EndTime<schedule[j]['EndTime']):
                    dic = {'FechaStr':schedule[j]['FechaStr'],'StartTime': schedule[j]['StartTime'],'EndTime': act.StartTime,'Date': schedule[j]['Date']}
                    schedule.insert(j+1,dic)
                    dic = {'FechaStr': schedule[j]['FechaStr'],'StartTime': act.EndTime,'EndTime': schedule[j]['EndTime'],'Date': schedule[j]['Date']}
                    schedule.insert(j+2,dic)
                    del schedule[j]
                    return dates
                if (act.StartTime>schedule[j]['StartTime'] and act.StartTime<schedule[j]['EndTime'] and act.EndTime>=schedule[j]['EndTime']):
                    schedule[j]['EndTime'] = act.StartTime
                    return dates
                if (act.StartTime<=schedule[j]['StartTime'] and act.EndTime<schedule[j]['EndTime'] and act.EndTime>schedule[j]['StartTime']):
                    schedule[j]['StartTime'] = act.EndTime
                    return dates
    return dates

@blue_dondefluir.route('/_get_calendar_events')
def get_calendar_events():
    profId = request.args.get('prodId',None)
    companyId = request.args.get('companyId',None)
    eventId = request.args.get('eventId',None)
    res = showProfessionalEvents({'profId':profId,'eventId':eventId,'companyId': companyId})
    return jsonify(result=res)


@blue_dondefluir.route('/_get_calendar_dates')
def get_calendar_dates():
    profId = request.args.get('id')
    AddActivities = request.args.get('AddActivities',True)
    res = getCalendarDates(profId,AddActivities)
    for d in res:
        list = res[d]
        for dic in list:
            for i in dic:
                if i in ('StartTime','EndTime'):
                    dic[i] = dic[i].strftime("%H:%M")
                elif i == 'Date' and isinstance(dic[i],date):
                    dic[i] = dic[i].strftime("%Y-%m-%d")
    return jsonify(result=res)


def getCalendarDates(profId,AddActivities=False):
    session = Session()
    user = session.query(User).filter_by(id=profId,Closed=0).first()
    if not user:
        return []

    ShowFromDays = 0
    if user.ShowFromDays: ShowFromDays = user.ShowFromDays
    d = addDays(today(),ShowFromDays)
    ShowDays = user.ShowDays
    if not ShowDays: ShowDays = 15
    td = addDays(d,ShowDays)

    activities = session.query(Activity) \
        .filter(Activity.ProfId==profId,Activity.Status!=2) \
        .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
        .filter(ActivitySchedules.TransDate>=d,ActivitySchedules.TransDate<=td) \
        .outerjoin(Service,Service.id==Activity.ServiceId)\
        .outerjoin(User,Activity.CustId==User.id)\
        .with_entities(ActivitySchedules.TransDate,ActivitySchedules.StartTime,ActivitySchedules.EndTime,Service.Name.label('Name') \
            ,Activity.Comment,Activity.id,User.Name.label('Customer'))
    dates = {}

    while d<td:
        weekday = d.weekday()
        for row in user.Schedules:
            found = False
            if (weekday==0 and row.d1): found = True
            if (weekday==1 and row.d2): found = True
            if (weekday==2 and row.d3): found = True
            if (weekday==3 and row.d4): found = True
            if (weekday==4 and row.d5): found = True
            if (weekday==5 and row.d6): found = True
            if (weekday==6 and row.d7): found = True
            if found:
                datestr = WeekName[weekday] + " " + d.strftime("%d/%m/%Y")
                datekey = d.strftime("%Y-%m-%d")
                if datekey not in dates:
                    dates[datekey] = []
                dates[datekey].append({'FechaStr':datestr,'StartTime':row.StartTime,'EndTime':row.EndTime,'CompanyId':user.CompanyId,'Date':d})
        d = addDays(d,1)

    for activity in activities:
        dates = getBreakCalendarDates(activity,dates)

    if user.FixedSchedule:
        newArray = {}
        for d in sorted(dates):
            schedules = dates[d]
            for i in range(len(schedules)):
                lastTime = addMinutesToTime(schedules[i]['EndTime'],-user.MinTime)
                startTime = schedules[i]['StartTime']
                while (startTime<=lastTime):
                    datestr = schedules[i]['FechaStr']
                    if d not in newArray:
                        newArray[d] = []
                    endTime = addMinutesToTime(startTime,user.MinTime)
                    newArray[d].append({'FechaStr':datestr,'StartTime':startTime,'EndTime':endTime,'CompanyId':user.CompanyId,'Date':d})
                    startTime = addMinutesToTime(startTime,user.MinTime)
        dates = newArray
    if AddActivities:
        for activity in activities:
            d = activity.TransDate
            weekday = d.weekday()
            datestr = WeekName[weekday] + " " + d.strftime("%d/%m/%Y")
            datekey = d.strftime("%Y-%m-%d")
            dates[datekey].append({'FechaStr':datestr,'StartTime':activity.StartTime,'EndTime':activity.EndTime \
                ,'CompanyId':user.CompanyId, 'Date':d, 'Comment': activity.Comment, 'Service': activity.Name \
                , 'id': activity.id, 'Customer': activity.Customer})
    session.close()
    return dates

@blue_dondefluir.route('/_set_favorite')
def set_favorite():
    from dondefluir.db.UserFavorite import UserFavorite
    favId = request.args.get('favId')
    session = Session()
    session.expire_on_commit = False
    record = session.query(UserFavorite).filter_by(UserId=current_user.id,FavoriteId=favId).first()
    if not record:
        record = UserFavorite()
        record.UserId = current_user.id
        record.FavoriteId = favId
        record.CompanyId = current_user.CompanyId
        record.beforeInsert()
        record.Checked = True
        session.add(record)
    else:
        record.Checked = not record.Checked
    status = record.Checked
    res = record.save(session)
    if res:
        return jsonify(result={'res':True,'id':record.id,'Status': status})
    else:
        return jsonify(result={'res':False,'Error':str(res)})

def getUserService(params):
    session = Session()
    from dondefluir.db.UserService import UserService
    from dondefluir.db.Service import Service
    records = session.query(UserService)\
        .join(User,User.id==UserService.UserId)\
        .join(Service,Service.id==UserService.ServiceId)\
        .filter_by(CompanyId=current_user.CompanyId) \
        .with_entities(UserService.id,UserService.CompanyId,User.Name.label("UserName"),Service.Name.label("ServiceName"))
    session.close()
    return records

def showProfessionalEvents(*args):
    profId = args[0].get('profId',None)
    eventId = args[0].get('eventId',None)
    companyId = args[0].get('companyId',None)
    session = Session()
    records = session.query(Activity) \
        .join(Company,Activity.CompanyId==Company.id)\
        .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
        .filter(ActivitySchedules.TransDate>=today(),or_(Activity.Type==1,Activity.Type==2)) \
        .with_entities(Activity.Comment,Activity.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
        ,ActivitySchedules.EndTime,Activity.id,Activity.MaxPersons,Activity.Price,Activity.Description,Activity.OnlinePayment \
        ,Company.KeyPayco,Company.OnlinePayment.label('CompanyPayment'))
    if eventId: records = records.filter(Activity.id==eventId)
    if profId: records = records.filter(Activity.ProfId==profId)
    if companyId: records = records.filter(Activity.CompanyId==companyId)
    res = {}
    k = 0
    for r in records:

        cnt = session.query(Activity).filter_by(id=r.id)\
            .join(ActivityUsers,Activity.id==ActivityUsers.activity_id)\
            .count()
        if r.id not in res:
            res[r.id] = []
        st = Activity.StatusList[0]
        stv = 0
        paid = 0

        if k==0:
            FindCust = session.query(Activity).filter_by(id=r.id)\
                .join(ActivityUsers,Activity.id==ActivityUsers.activity_id)\
                .filter(ActivityUsers.CustId==current_user.id)\
                .count()
            if FindCust:
                st = Activity.StatusList[1]
                stv = 1
                Paid = session.query(Payment)\
                    .filter_by(UserId=current_user.id,ActivityId=r.id,ResponseCode=1) \
                    .count()
                if Paid:
                    paid = 1

        TransDate = WeekName[r.TransDate.weekday()] + " " + r.TransDate.strftime("%d/%m/%Y")
        res[r.id].append({'Comment': r.Comment,'TransDate': TransDate, 'StartTime': r.StartTime.strftime("%H:%M") \
            , 'Description': r.Description, 'Price': r.Price, 'MaxPersons': r.MaxPersons, 'OnlinePayment': r.OnlinePayment \
            , 'EndTime': r.EndTime.strftime("%H:%M"), 'Status': st, 'Persons': cnt, 'StatusValue': stv, 'Paid': paid \
            , 'KeyPayco': r.KeyPayco, 'CompanyPayment':r.CompanyPayment})
        k += 1
    return res

@blue_dondefluir.route('/_get_professional_list')
def get_professional_list():
    favorite = request.args.get('Favorite')=='true'
    companyId = request.args.get('CompanyId',None)
    records = getProfessional(favorite,companyId)
    res = fillRecordList(records,['Name','id','CompanyName','Title','City'])
    for dic in res:
        dic['Image'] = getImageLink('User',dic['id'],'ImageProfile')
    return jsonify(result=res)


@blue_dondefluir.route('/_set_cust_to_event')
def set_cust_to_event():
    eventId = request.args.get('id')
    session = Session()
    session.expire_on_commit = False
    record = session.query(Activity).filter_by(id=eventId).first()
    if record:
        found = False
        st = 1
        for row in record.Users:
            if row.CustId==current_user.id:
                found = True
                record.Users.remove(row)
                st = 0
                break
        if not found:
            row = ActivityUsers()
            row.CustId = current_user.id
            record.Users.append(row)
        res = record.save(session)
        if res:
            return jsonify(result={'res':True,'label':Activity.StatusList[st],'st': st})
        else:
            return jsonify(result={'res':False,'Error':str(res)})
    return jsonify(result={'res':False,'Error':'Registro Inexistente'})


def getCalendarData(UserId):
    records = Activity.getRecordListCalendar(Activity,ProfId=UserId)
    list = []
    for record in records:
        st = "%sT%s" %(record.TransDate.strftime('%Y-%m-%d'),record.StartTime.strftime('%H:%M:%S'))
        et = "%sT%s" %(record.TransDate.strftime('%Y-%m-%d'),record.EndTime.strftime('%H:%M:%S'))
        onclick = ''' getRecordForm('Activity','recordform.html',id='%i')''' % record.id
        id = 'activity_%i' % record.id
        #tooltip = "%s\n" % record.Comment
        #tooltip += "Fecha: %s\n" % record.TransDate.strftime('%Y-%m-%d')
        #tooltip += "Horario: %s a %s\n" % (record.StartTime.strftime('%H:%M:%S'),record.EndTime.strftime('%H:%M:%S'))

        BGColor = 'yellow'
        textColor = 'black'
        if record.Status==1:
            BGColor = 'green'
            textColor = 'white'
        elif record.Status==2:
            BGColor = 'gray'
            textColor = 'white'
        list.append({'title': record.Comment,'start':st,'end':st,'onclick':onclick,'id':id,'backgroundColor':BGColor, \
            'textColor': textColor})
    return list

@blue_dondefluir.route('/data')
def return_data():
    UserId = request.args.get('UserId', '')
    res = getCalendarData(UserId)
    return jsonify(res)
    with open("events.json", "r") as input_data:
        return input_data.read()

@blue_dondefluir.route('/_set_notification_read')
def set_notification_read():
    nftId = request.args.get('id')
    session = Session()
    session.expire_on_commit = False
    record = session.query(Notification).filter_by(id=nftId).first()
    if record:
        record.Status = 1
        res = record.save(session)
        if res:
            return jsonify(result={'res':True})
        else:
            return jsonify(result={'res':False,'Error':str(res)})
    return jsonify(result={'res':False,'Error':'Registro Inexistente'})

@blue_dondefluir.route('/_get_notifications')
def get_notifications():
    session = Session()
    session.expire_on_commit = False
    record = session.query(Notification).filter_by(UserId=current_user.id,Status=0).order_by(Notification.TransDate.desc())
    cnt = record.count()
    l = []
    k = 0
    for r in record:
        k += 1
        l.append({'Comment':r.Comment,'TransDate': "%s %s" % (WeekName[int(r.TransDate.strftime("%w"))] \
            ,r.TransDate.strftime("%d/%m/%Y")),'id':r.id})
        if k>=4:
            break
    return jsonify(result={'cnt':cnt,'values':l})


@blue_dondefluir.route('/_get_current_date')
def get_current_date():
    date = today()
    w = date.weekday()
    m = date.month
    Y = date.year
    d = date.day
    hoy = 'Hoy es %s %i de %s de %i' %(WeekName[w],d,meses[m],Y)
    return jsonify(result=hoy)


@blue_dondefluir.route('/_event_list')
def event_list():
    fields = request.args.get('Fields').split(',')
    order_by = request.args.get('OrderBy',None)
    desc = request.args.get('Desc',None)
    limit = request.args.get('Limit',None)
    records = Activity.getEventList(limit=limit,order_by=order_by,desc=desc)
    fieldsDef = Activity.fieldsDefinition()
    res = fillRecordList(records,fields,fieldsDef)
    return jsonify(result=res)

@blue_dondefluir.route('/_cancel_activity')
def cancel_activity():
    session = Session()
    session.expire_on_commit = False
    _id = request.args.get('id')
    record = session.query(Activity).filter_by(id=_id).first()
    if not record:
        return jsonify(result={'res': False,'Error':'Registro no Encontrado'})
    record.setOldFields()
    record.Status = record.CANCELLED
    res = record.check()
    if not res:
        return jsonify(result={'res': False,'Error':str(res)})
    record.syncVersion += 1
    res = record.afterUpdate()
    if not res:
        return jsonify(result={'res': False,'Error':str(res)})
    try:
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify(result={'res': False,'Error':str(e)})
    record.callAfterCommitUpdate()
    return jsonify(result={'res':True,'id': record.id,'syncVersion': record.syncVersion})

@blue_dondefluir.route('/epayco/<activity_id>')
def epayco(activity_id):
    return render_template('epayco_res.html',current_user=current_user,app_name=settings.app_name,activityId=activity_id)


@blue_dondefluir.route('/_set_payment')
def set_payment():
    from dondefluir.db.Payment import Payment
    activityId = request.args.get('activityId')
    session = Session()
    session.expire_on_commit = False
    record = Payment()
    record.UserId = current_user.id
    record.CompanyId = current_user.CompanyId
    record.ActivityId = activityId
    record.ResponseCode = request.args.get('x_cod_response')
    record.Response = request.args.get('x_response')
    record.Amount = request.args.get('x_amount')
    record.TransDate = now()
    record.Reference = request.args.get('x_id_invoice')
    record.Reason = request.args.get('x_response_reason_text')
    record.TransactionId = request.args.get('x_transaction_id')
    record.BankName = request.args.get('x_bank_name')
    record.AutorizationCode = request.args.get('x_approval_code')
    record.Currency = request.args.get('x_currency_code')
    record.beforeInsert()
    session.add(record)
    res = record.save(session)
    if res:
        return jsonify(result={'res':True,'id':record.id})
    else:
        return jsonify(result={'res':False,'Error':str(res)})
