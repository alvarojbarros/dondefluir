﻿# -*- coding: utf-8 -*-

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
from dondefluir.db.Activity import Activity,ActivitySchedules,ActivityUsers
from sqlalchemy import or_

blue_dondefluir = Blueprint('blue_dondefluir', __name__,template_folder='templates',static_url_path='/dondefluir/static',static_folder='static')

def getActivitiesModuleName():
    if current_user.UserType==3:
        return "Mi Agenda"
    else:
        return "Actividades"

def addElementToList(Tables,Table,UserType):
    if ('Level' not in Table) or (UserType in Table['Level']):
        Tables[len(Tables)] = Table

def getModules(UserType):
    Tables = {}
    functions = "runSearchBoxOnKey()"
    Table = {'Name':'Usuários','Level':[0,1,2],'Template':'users.html','Vars':{'Table':'User','Functions':functions},'Image':'fa-users'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Empresas','Level':[0],'Template':'company.html','Vars':{'Table':'Company','Functions':functions},'Image':'fa-fort-awesome'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':getActivitiesModuleName(),'Level':[0,1,2,3],'Template':'activity.html','Vars':{'Table':'Activity','Functions':functions},'Image':'fa-sun-o'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Mis Profesionales','Level':[0,3],'Template':'professional.html','Vars':{'Table':'User','Functions':functions,'favorite':'true'},'Image':'fa-heart'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Profesionales','Level':[0,3],'Template':'professional.html','Vars':{'Table':'User','Functions':functions,'favorite':'false'},'Image':'fa-magic'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Buscar Clientes','Level':[0,1,2],'Template':'customer.html','Vars':{'Table':'User','Functions':functions,'favorite':'False'},'Image':'fa-smile-o'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Mis Clientes','Level':[0,1,2],'Template':'customer.html','Vars':{'Table':'User','Functions':functions,'favorite':'True'},'Image':'fa-smile-o'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Servicios','Level':[0,1],'Template':'service.html','Vars':{'Table':'Service','Functions':functions},'Image':'fa-coffee'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Servicios por Profesional','Level':[0,1],'Template':'userservice.html','Vars':{'Table':'UserService','Functions':functions},'Image':'fa-suitcase'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Agenda','Level':[0,1,2],'Template':'calendar.html','Vars':{'Functions':functions},'Image':'ti-calendar p-r-10'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Cursos y Eventos','Template':'events.html','Vars':{'Table':'Activity'},'Image':'fa-star'}
    addElementToList(Tables,Table,UserType)
    Table = {'Name':'Notificaciones','Template':'notification.html','Vars':{'Table':'Notification'},'Image':'fa-envelope-o'}
    addElementToList(Tables,Table,UserType)
    return Tables

def getMyFunction(function,params):
    res = eval('%s(%s)' % (function,str(params)))
    return res

def getProfessional(favorite):
    session = Session()
    if not favorite:
        records = session.query(User).filter_by(FindMe=True)\
            .join(Company,User.CompanyId==Company.id)\
            .with_entities(User.id,User.Name,Company.Name.label("CompanyName"))
    else:
        from dondefluir.db.UserFavorite import UserFavorite
        records = session.query(User).join(UserFavorite,User.id==UserFavorite.FavoriteId)\
            .filter_by(UserId=current_user.id,Checked=True)\
            .join(Company,User.CompanyId==Company.id)\
            .with_entities(User.id,User.Name,Company.Name.label("CompanyName"))
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
        records = session.query(User).filter_by(UserType=3)
    else:
        from dondefluir.db.UserFavorite import UserFavorite
        records = session.query(User).filter_by(UserType=3).join(UserFavorite,User.id==UserFavorite.FavoriteId)\
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
    profId = request.args.get('id',None)
    eventId = request.args.get('eventId',None)
    res = showProfessionalEvents({'profId':profId,'eventId':eventId})
    return jsonify(result=res)


@blue_dondefluir.route('/_get_calendar_dates')
def get_calendar_dates():
    profId = request.args.get('id')
    res = getCalendarDates(profId)
    for d in res:
        list = res[d]
        for dic in list:
            for i in dic:
                if i in ('StartTime','EndTime'):
                    dic[i] = dic[i].strftime("%H:%M")
                elif i == 'Date' and isinstance(dic[i],datetime):
                    dic[i] = dic[i].strftime("%d/%m/%Y")
    return jsonify(result=res)


def getCalendarDates(profId):
    session = Session()
    user = session.query(User).filter_by(id=profId).first()
    if not user:
        return []

    ShowFromDays = 0
    if user.ShowFromDays: ShowFromDays = user.ShowFromDays
    d = addDays(today(),ShowFromDays)
    ShowDays = user.ShowDays
    if not ShowDays: ShowDays = 15
    td = addDays(d,ShowDays)

    activities = session.query(Activity) \
        .filter(Activity.ProfId==profId) \
        .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
        .filter(ActivitySchedules.TransDate>=d,ActivitySchedules.TransDate<=td) \
        .with_entities(ActivitySchedules.TransDate,ActivitySchedules.StartTime,ActivitySchedules.EndTime)
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
    session = Session()
    records = session.query(Activity) \
        .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
        .filter(ActivitySchedules.TransDate>=today(),or_(Activity.Type==1,Activity.Type==2)) \
        .with_entities(Activity.Comment,Activity.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
        ,ActivitySchedules.EndTime,Activity.id,Activity.MaxPersons,Activity.Price,Activity.Description)
    if eventId: records = records.filter(Activity.id==eventId)
    if profId: records = records.filter(Activity.ProfId==profId)
    res = {}
    k = 0
    for r in records:

        cnt = session.query(Activity).filter_by(id=r.id)\
            .join(ActivityUsers,Activity.id==ActivityUsers.activity_id)\
            .count()
        if r.id not in res:
            res[r.id] = []
        st = Activity.StatusList[0]

        if k==0:
            FindCust = session.query(Activity).filter_by(id=r.id)\
                .join(ActivityUsers,Activity.id==ActivityUsers.activity_id)\
                .filter(ActivityUsers.CustId==current_user.id)\
                .count()
            if FindCust:
                st = Activity.StatusList[1]

        TransDate = WeekName[r.TransDate.weekday()] + " " + r.TransDate.strftime("%d/%m/%Y")
        res[r.id].append({'Comment': r.Comment,'TransDate': TransDate, 'StartTime': r.StartTime.strftime("%H:%M") \
            , 'Description': r.Description, 'Price': r.Price, 'MaxPersons': r.MaxPersons \
            , 'EndTime': r.EndTime.strftime("%H:%M"), 'Status': st, 'Persons': cnt })
        k += 1
    return res

@blue_dondefluir.route('/_get_professional_list')
def get_professional_list():
    favorite = request.args.get('Favorite')=='true'
    records = getProfessional(favorite)
    res = fillRecordList(records,['Name','id','CompanyName'])
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


def getCalendarData():
    records = Activity.getRecordList(Activity)
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
            'textColor':textColor})
    return list

@blue_dondefluir.route('/data')
def return_data():
    res = getCalendarData()
    if res: return jsonify(res)
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
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
        l.append({'Comment':r.Comment,'TransDate':r.TransDate,'id':r.id})
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
