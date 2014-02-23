$('document').ready(function(){


	
	$.get('/api/transaction_history', function(response){
		console.log(response)
	});



})