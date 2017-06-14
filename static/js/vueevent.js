Vue.config.devtools = true;

var vue_event = new Vue({
  el: '#event_record',
  data: {
    events: '',
  },
  methods: {
    getScript: function(params) {
			return $(
				'<script src="https://s3-us-west-2.amazonaws.com/epayco/v1.0/checkoutEpayco.js" ' +
				'    class="epayco-button" ' +
				'    data-epayco-key=' + params.KeyPayco +
				'    data-epayco-amount=' + params.Price +
				'    data-epayco-name=' + params.Comment +
				'    data-epayco-description=' + params.Description +
				'    data-epayco-currency="cop" ' +
				'    data-epayco-country="co" ' +
				'    data-epayco-test="true" ' +
				'    data-epayco-response="'+ window.location.href.replace('#','') + 'epayco/' + params.id + '"' +
				'    data-epayco-confirmation="https://ejemplo.com/confirmacion" > <' + '/script>')
		}
	},
	mounted: function () {
		for (k in this.events){
			$(this.$refs['form' + k]).html(this.getScript(this.events[k][0]))
		}
	},
	updated: function () {
		for (k in this.events){
			$(this.$refs['form' + k]).html(this.getScript(this.events[k][0]))
		}
}


})
