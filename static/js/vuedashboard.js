Vue.config.devtools = true;

var vue_dashboard_date = new Vue({
  el: '#dashboard',
  data: {
    currentdate:  '',
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
