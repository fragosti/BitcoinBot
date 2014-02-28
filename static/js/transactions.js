$('document').ready(function(){


	function loadtransactions() {
		$.get('/api/transaction_history', function(response){
			if (response == 'error'){
				return
			}
			var html = "";
			response = JSON.parse(response)
		
			for(var i = 0; i < response.length ; i++){
				var obj = response[i];
				html += 
				"<tr>"+
         			"<td>" + obj.time + "</td>" +
            		"<td>" + obj.pair + "</td>" + 
            		"<td>" + obj.amount + "</td>" +
            		"<td>" + obj.rate + "</td>" +
        		"</tr>"
			}
			$('#transactions_fill').html(html);
		});
	}
	loadtransactions()
	setInterval(loadtransactions, 10000)

});