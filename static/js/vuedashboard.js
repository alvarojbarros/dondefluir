Vue.config.devtools = true;

dias = {
	1:'Lunes',
	2:'Martes',
	3:'Miércoles',
	4:'Jueves',
	5:'Viernes',
	6:'Sábado',
	0:'Domingo'
}
meses = {
	0:'Enero',
	1:'Febrero',
	2:'Marzo',
	3:'Abril',
	4:'Mayo',
	5:'Junio',
	6:'Julio',
	7:'Agosto',
	8:'Septiembre',
	9:'Octubre',
	10:'Noviembre',
	11:'Diciembre'
}
date = new Date();
w = date.getDay();
m = date.getMonth();
Y = date.getYear() + 1900;
d = date.getDate();
hoy = 'Hoy es ' + dias[w] + ' ' + d + ' de ' + meses[m] + ' de ' + Y;

var vue_dashboard_date = new Vue({
  el: '#dashboard',
  data: {
    currentdate:  hoy,
  },

})

var vue_dashboard_ntf = new Vue({
  el: '#notifications',
  data: {
    news: 'No hay nuevas notificaciones',
    values: '',
    cnt: 0,
  },

})
