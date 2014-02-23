$('document').ready(function(){


	
	$.get('/api/transaction_history', function(response){
		var html = "";
		response = JSON.parse(response)
		
		for(var i = 0; i < response.length ; i++){
			obj = response[i];
			console.log(obj)
			html += 
			"<tr>"+
         		"<td>" + obj.time+ "</td>" +
            	"<td>" + obj.pair + "</td>" + 
            	"<td>" + obj.amount + "</td>" +
            	"<td>" + obj.rate + "</td>" +
        	"</tr>"
		}
		$('#transactions_fill').html(html);
	});



});