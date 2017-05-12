# -*- coding: utf-8 -*-

from mail import sendMail
from flask import render_template
from dondefluir.db.Service import Service
from dondefluir.db.Company import Company
from dondefluir.db.User import User
from datetime import date,time
import getsettings
settings = getsettings.getSettings()
from tools.Tools import *

def strToDate(d):
    return date(int(d[:4]),int(d[5:7]),int(d[8:10]))

def strToTime(d):
    return time(int(d[:2]),int(d[3:5]),0)


def getVars(user,activity):
    var = {}
    var['UserName'] = user.Name
    var['ActivityTitle'] = 'Cita'
    if activity.Type==0 and activity.ServiceId:
        service = Service.getRecordById(activity.ServiceId)
        if service and service.Name:
            var['ActivityTitle'] = service.Name
    elif activity.Type in (1,2) and activity.Comment:
        var['ActivityTitle'] = activity.Comment
    elif activity.Type in (1,2) and activity.ServiceId:
        service = Service.getRecordById(activity.ServiceId)
        if service and service.Name:
            var['ActivityTitle'] = service.Name
    var['ProfId'] = activity.ProfId
    prof = User.getRecordById(activity.ProfId)
    if prof and prof.Name:
        var['ProfId'] = prof.Name
    var['UserAddress'] = ''
    if prof and prof.Address:
        var['UserAddress'] = prof.Address
        if prof and prof.City:
            var['UserAddress'] += " %s" % prof.City
    var['UserPhone'] = ''
    if prof and prof.Phone:
        var['UserPhone'] = prof.Phone
    if len(activity.Schedules)>0:
        row = activity.Schedules[0]
        transdate = strToDate(row.TransDate)
        datestr = "%s %i de %s de %i" % (WeekName[transdate.weekday()],transdate.day,meses[transdate.month],transdate.year)
        var['TransDateStr'] = datestr
        var['TransDate'] = transdate.strftime("%d.%m.%Y")
        var['StartTime'] = strToTime(row.StartTime).strftime("%H:%M")
        var['EndTime'] = strToTime(row.EndTime).strftime("%H:%M")
    company = Company.getRecordById(activity.CompanyId)
    if company and company.Name:
        var['CompanyName'] = company.Name
    if company and company.WebSite:
        var['WebSite'] = company.WebSite
    if company and company.Address and not var['UserAddress']:
        var['UserAddress'] = company.Address
        if company.City:
            var['UserAddress'] += " %s" % company.City
    if company and company.Phone and not var['UserPhone']:
        var['UserPhone'] = company.Phone
    return var

def sendMailUpdateActivity(user,activity):
    var = getVars(user,activity)
    msj = render_template('notificacionesModificacionCita.html',var=var)
    subject = ' Actividad modificada: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.id,subject,msj)

def sendMailCancelActivity(user,activity):
    var = getVars(user,activity)
    msj = render_template('notificacionesCancelacionCita.html',var=var)
    subject = ' Actividad cancelada: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.id,subject,msj)

def sendMailConfirmActivity(user,activity):
    var = getVars(user,activity)
    msj = render_template('notificacionesConfirmacionCita.html',var=var)
    subject = ' Actividad confirmada: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.id,subject,msj)

def sendMailNewActivity(user,activity):
    var = getVars(user,activity)
    msj = render_template('notificacionesCreacionCita.html',var=var)
    subject = ' Nueva actividad: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.id,subject,msj)

def sendNewUserMail(user,name,password):
    msj = render_template('notificacionesCreacionUsuario.html',user=user,name=name,password=password)
    subject = 'Te damos la bienvenida a Donde Fluir!'
    return sendMail(user,subject,msj)

def sendMailNewCustActivity(user,activity):
    var = getVars(user,activity)
    msj = render_template('notificacionesNuevosClientesActividad.html',var=var)
    subject = ' Hay nuevos clientes en el %s: %s - %s con %s' % (['la Actividad','el Curso','el Evento'][activity.Type] \
        ,var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.id,subject,msj)
