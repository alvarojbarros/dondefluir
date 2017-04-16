
function showProfessional(id,Name,current_user_id){
	console.log(current_user_id)
	vars = {Template: 'showprofessional.html',profId: id}
	getTemplate('container-fluid',vars,function (){
		setProffesional(id,current_user_id);
	})
}


function getProfessionalList(favorite,current_user_id){

	console.log(current_user_id)
	$.getJSON($SCRIPT_ROOT + '/_get_professional_list', {'Favorite': favorite },function(data) {
		Vue.set(vue_recordlist,'values', data.result);
		Vue.set(vue_recordlist,'user_id', current_user_id);
	});
}


function setProffesional(id,current_user_id){
	console.log(current_user_id)
	getRecordBy('User',{id:id,NotFilterFields:true},function(data){
		Vue.set(vue_title,'Title', data.record.Name);
		Vue.set(vue_record,'values', data.record);
		/*prof_Name = document.getElementById('prof_Name');
		prof_Name.innerHTML = data.record.Name;
		prof_Name2 = document.getElementById('prof_Name2');
		prof_Name2.innerHTML = record.Name;
		prof_id = document.getElementById('id');
		prof_id.value = record.id;
		prof_Name3 = document.getElementById('prof_Name3');
		prof_Name3.innerHTML = record.Name;
		user_title = document.getElementById('user_title');
		user_title.innerHTML = record.Title;

		record_email = document.getElementById('record_email');
		record_email.innerHTML = record.Email
		record_phone = document.getElementById('record_phone');
		record_phone.innerHTML = record.Phone
		record_address = document.getElementById('record_address');
		record_address.innerHTML = record.Address
		record_city = document.getElementById('record_city');
		record_city.innerHTML = record.City
		record_comment = document.getElementById('record_comment');
		record_comment.innerHTML = record.Comment */

		getRecordBy('UserFavorite',{UserId: current_user_id, FavoriteId: data.record.id},function(recordFav){
			if (recordFav && recordFav.Checked){
				Vue.set(vue_record,'favorite', 'Eliminar de Favoritos');
			}
		});
		/*getRecordBy('Company',{id: data.record.CompanyId},function(company){
			company_name = document.getElementById('company_name');
			company_name.innerHTML = company.Name
			if (!data.record.Email){record_email.innerHTML = company.Email;}
			if (!data.record.Phone){record_phone.innerHTML = company.Phone;}
			if (!data.record.Address){record_address.innerHTML = company.Address;}
			if (!data.record.City){record_city.innerHTML = company.City;}
		});*/
	});
}

function setFavorite(element){
  favId = document.getElementById('id');
  $.getJSON($SCRIPT_ROOT + '/_set_favorite',{favId: favId.value}, function(data) {
      if (data.result['res']==true){
		  favorite = document.getElementById('favorite');
		  if (favorite){
		 	  if (data.result['Status']==true) {
		 	  	favorite.innerHTML = 'Eliminar de Favoritos';
		  	  }else{
		 	  	favorite.innerHTML = 'Agregar de Favoritos';
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
	console.log(1);
	var p1 = document.getElementById('ProfId');
	p1.value = ProfId;
	var p2 = document.getElementById('StartTime');
	p2.value = StartTime;
	var p3 = document.getElementById('EndTime');
	p3.value = EndTime;
	var p4 = document.getElementById('TransDate');
	p4.value = TransDate;
	var p5 = document.getElementById('CompanyId');
	p5.value = CompanyId;
	var p6 = document.getElementById('CustId');
	p6.value = CustId;
	var p7 = document.getElementById('Schedules');
	p7.setAttribute("has_rows",true);

}


function createActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId){
	vars = {Template: 'recordform.html',Table:'Activity'}
	getTemplate('container-fluid',vars,function(){
		getRecord('Activity',{},function (data){
			Vue.set(vue_record,'values', data);
			vue_title.recordName = 'Nuevo Actividad'
			setActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId);
		})

		/*createRecordForm(null,'Activity',null,'recordFields',function(){
			setActivity(TransDate,StartTime,EndTime,ProfId,CompanyId,CustId);
		});*/
	})
}

function setCustomerToEvent(id){
    $.getJSON($SCRIPT_ROOT + '/_set_cust_to_event',{id: id}, function(data) {
      	res = data.result['res'];
      	if (res){
			e = document.getElementById(id);
			e.innerHTML = data.result.label;
	  	}else{
			alert(data.result['Error']);
		};
    });

}

function newUserNote(custId){
	vars = {Template: 'recordform.html',Table:'UserNote'}
	getTemplate('container-fluid',vars,function(){
		/*createRecordForm(null,'UserNote',null,'recordFields',function(){
			var userId = document.getElementById('UserId');
			userId.value = custId;
		});*/
	})
}