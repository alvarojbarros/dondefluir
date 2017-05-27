Vue.config.devtools = true;

var vue_record = new Vue({
  el: '#recordFields',
  data: {
 	loading: false,
    values: '',
    favorite: 'Agregar a Favoritos',
    classname: 'btn btn-primary btn-rounded waves-effect waves-light m-t-20',
  },
  ready: function() {
    this.loading = true;
  }

})

var vue_tabs = new Vue({
  el: '#vue_tabs',
  data: {
    user_type: 0,
  },

})
