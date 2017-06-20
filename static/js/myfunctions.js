
function showProfessional(id,Name,current_user_id){
	vars = {Template: 'showprofessional.html',profId: id}
	getTemplate('container-fluid',vars,function (){
		setProffesional(id,current_user_id);
	})
}


function getProfessionalList(favorite,current_user_id){

	$.getJSON($SCRIPT_ROOT + '/_get_professional_list', {'Favorite': favorite },function(data) {
		Vue.set(vue_recordlist,'values', data.result);
		Vue.set(vue_recordlist,'user_id', current_user_id);
		Vue.set(vue_recordlist,'user_type', vue_user_menu.current_user_type);
	});
}


function setProffesional(id,current_user_id){
	getRecordBy('User',{id:id,NotFilterFields:true},function(data){
		Vue.set(vue_title,'Title', data.record.Name);
		Vue.set(vue_record,'values', data.record);

		$.getJSON($SCRIPT_ROOT + '/_get_calendar_dates', {'id':id},function(data1) {
			Vue.set(vue_schedule,'values',data1.result)
			Vue.set(vue_schedule,'profId',id)
			Vue.set(vue_schedule,'profName',data.record.Name)
			Vue.set(vue_schedule,'current_user_id',current_user_id)
		});

		$.getJSON($SCRIPT_ROOT + '/_get_calendar_events', {'id':id},function(data2) {
			Vue.set(vue_schedule,'events',data2.result)
		});

		getRecordBy('UserFavorite',{UserId: current_user_id, FavoriteId: data.record.id},function(recordFav){
			if (recordFav && recordFav.record && recordFav.record.Checked){
				Vue.set(vue_record,'favorite', 'Eliminar de Favoritos');
				Vue.set(vue_record,'classname', 'btn btn-danger btn-rounded waves-effect waves-light m-t-20');
			}
		});
		getRecordBy('Company',{id: data.record.CompanyId},function(company){
			Vue.set(vue_title,'companyName', company.record.Name);
			/*if (!data.record.Email){record_email.innerHTML = company.Email;}
			if (!data.record.Phone){record_phone.innerHTML = company.Phone;}
			if (!data.record.Address){record_address.innerHTML = company.Address;}
			if (!data.record.City){record_city.innerHTML = company.City;} */
		});
	});
}

function setFavorite(element,t){
  if (t=='0'){favId = vue_record.values.id}
  if (t=='1'){favId = vue_record.values.record.id}
  $.getJSON($SCRIPT_ROOT + '/_set_favorite',{favId: favId}, function(data) {
      if (data.result['res']==true){
		  favorite = document.getElementById('favorite');
		  if (favorite){
		 	  if (data.result['Status']==true) {
		 	  	  if (t=="1"){
					  console.log(7)
					  vue_record.values.fields.Favorite.Label = 'Eliminar de Favoritos'
					  vue_record.values.record.Favorite = 1
					  vue_record.values.fields.Favorite.Class = 'btn btn-danger btn-rounded waves-effect waves-light m-t-20'
				  }
		 	  	  if (t=="0"){
					  Vue.set(vue_record,'favorite', 'Eliminar de Favoritos');
					  Vue.set(vue_record,'classname', 'btn btn-danger btn-rounded waves-effect waves-light m-t-20');
				  }
		  	  }else{
		 	  	  if (t=="1"){
					  vue_record.values.record.Favorite = 0
					  vue_record.values.fields.Favorite.Label = 'Agregar a Favoritos'
					  vue_record.values.fields.Favorite.Class = 'btn btn-primary btn-rounded waves-effect waves-light m-t-20'
				  }
		 	  	  if (t=="0"){
					  Vue.set(vue_record,'favorite', 'Agregar a Favoritos');
					  Vue.set(vue_record,'classname', 'btn btn-primary btn-rounded waves-effect waves-light m-t-20');
				  }
			  }
		  }
	  }
  });
}

function showNotes(){
	var id = document.getElementById('id');
	var name = document.getElementById('Name');
	vars = {Template: 'usernote.html','custId':id.value,'custName': name.value}
	getTemplate('container-fluid',vars)
}

function setActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId){
	Vue.set(vue_record.values.record,'ProfId', ProfId);
	Vue.set(vue_record.values.record,'CustId', CustId);
	vue_record.values.record.CompanyId = CompanyId
	vue_record.values.record.Status = 0
	vue_record.values.record.Type = 0
	vue_record.values.record.Schedules.push({'StartTime': StartTime,'TransDate': TransDate, 'EndTime': EndTime})
	updateLinkTo()
}


function createActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId){
	vars = {Template: 'activityform.html',Table:'Activity'}
	getTemplate('container-fluid',vars,function(){
		getRecord({TableName:'Activity'},function (data){
			Vue.set(vue_record,'table', 'Activity');
			Vue.set(vue_record,'values', data);
			Vue.set(vue_buttons,'canEdit', data.canEdit);
			Vue.set(vue_buttons,'canDelete', data.canDelete);
			setCustomVue('Activity',data.record)
			vue_title.Title = 'Nuevo Actividad'
			setActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId);
		})
	})
}

function setCustomerToEvent(id){
    $.getJSON($SCRIPT_ROOT + '/_set_cust_to_event',{id: id}, function(data) {
      	res = data.result['res'];
      	if (res){
			console.log(1)
			vue_event.events[id][0].Status = data.result.label;
			if (data.result.st==1){
				vue_event.events[id][0].Persons += 1;
				vue_event.events[id][0].StatusValue = 1;
			}else{
				vue_event.events[id][0].StatusValue = 0;
				vue_event.events[id][0].Persons += -1;
			}
	  	}else{
			alert(data.result['Error']);
		};
    });

}

function newUserNote(custId){
	vars = {Template: 'recordform.html',Table:'UserNote',RecordId:''}
	getTemplate('container-fluid',vars,function(){
		getRecord({TableName:'UserNote'},function (data){
			Vue.set(vue_record,'values', data);
			Vue.set(vue_record,'table', 'UserNote');
			Vue.set(vue_buttons,'canEdit', data.canEdit);
			Vue.set(vue_buttons,'canDelete', data.canDelete);
			vue_record.values.record.UserId = custId;
			vue_title.Title = 'Ingresar Nota'
		})
	})
}

function setNotificationRead(id){
    $.getJSON($SCRIPT_ROOT + '/_set_notification_read',{id: id}, function(data) {
    	getNotifications();
    });
}


function getTemplateNotification(){
	vars = {'Name':'Notificaciones','Table':'Notification','Template':'notification.html'}
	getTemplate('container-fluid',vars,function(){
		vue_title.Title = vars.Name;
	});
}

function getNotifications(){
	div = document.getElementById('notifications-menu');
	if (div){
		$.getJSON($SCRIPT_ROOT + '/_get_notifications',{}, function(data) {
			Vue.set(vue_notifications,'values',data.result.values)
			Vue.set(vue_notifications,'cnt',data.result.cnt)
			notif_dash = document.getElementById('notifications');
			if (notif_dash){
				Vue.set(vue_dashboard_ntf,'values',data.result.values)
				Vue.set(vue_dashboard_ntf,'cnt',data.result.cnt)
			}
			if (data.result.cnt>0){
				Vue.set(vue_notifications,'news',data.result.cnt + ' notificaciones nuevas')
				if (notif_dash){
					Vue.set(vue_dashboard_ntf,'news',data.result.cnt + ' notificaciones nuevas')
				}
			}else{
				Vue.set(vue_notifications,'news','No hay nuevas notificaciones')
				if (notif_dash){
					Vue.set(vue_dashboard_ntf,'news','No hay nuevas notificaciones')
				}
			}
		});
	}
}

function getMyFunctionReady(){
	getNotifications();
}

function updateNotificationsList(){
	Vue.set(vue_dashboard_ntf,'values',vue_notifications.values)
	Vue.set(vue_dashboard_ntf,'cnt',vue_notifications.cnt)
	Vue.set(vue_dashboard_ntf,'news',vue_notifications.news)
}

function showDashboard(){
	getTemplate('container-fluid',{'Template':'mycontainer.html'},function(){
		updateNotificationsList();
	});
}

function getCurrentDate(){
	$.getJSON($SCRIPT_ROOT + '/_get_current_date',{}, function(data) {
		Vue.set(vue_dashboard_date,'currentdate',data.result);
	});

}

function getEventList(fields){

	var vars = {'Table': 'Activity','Fields': fields }
	vars['OrderBy'] = 'TransDate';
	Vue.set(vue_recordlist,'table', 'Activity');
	Vue.set(vue_recordlist,'user_type', vue_user_menu.current_user_type);
	$.getJSON($SCRIPT_ROOT + '/_event_list', vars ,function(data) {
		Vue.set(vue_recordlist,'values', data.result);
	});
}


function showEvent(id){
    var vars = {Template: 'event.html',Table: 'Activity', id: id}
	getTemplate('container-fluid',vars,function (){
		$.getJSON($SCRIPT_ROOT + '/_get_calendar_events', {'eventId':id},function(data) {
			Vue.set(vue_event,'events', data.result);
		});
	});
}

function cancelActivity() {
    var fields = {}
	_id = vue_record.values.record.id;
	messages.error_msg = '';
	if (vue_record.values.record.Status==2){
		messages.error_msg = 'Actividad ya cancelada';
		return;
	}
    if (_id){
		fields['id'] = _id;
		$.getJSON($SCRIPT_ROOT + '/_cancel_activity', fields, function(data) {
		  if (data.result['res']){
			  setMessageTimeout('Actividad Cancelada')
			  vue_record.values.record.syncVersion = data.result['syncVersion'];
			  vue_record.values._state = 1
			  vue_record.values.record.Status = 2
			  Vue.set(vue_buttons,'id', data.result.id);
			  Vue.set(vue_buttons,'Status', 2);
		  }else{
			  messages.error_msg = data.result['Error'];
		  }
		});
	}else{
	  messages.error_msg = 'No se puede cancelar';
	}
};

function setCustomVue(Table,record){
	if (Table=='Activity'){
		Vue.set(vue_buttons,'id', record.id);
		Vue.set(vue_buttons,'Status', record.Status);
	}
}