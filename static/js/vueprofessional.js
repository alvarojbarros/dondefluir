Vue.config.devtools = true;

var vue_title = new Vue({
  el: '#vue_title',
  data: {
    Title: '',
    companyName: '',
  },

})

var vue_record = new Vue({
  el: '#recordFields',
  data: {
    values: '',
    favorite: 'Agregar a Favoritos',
  },

})
