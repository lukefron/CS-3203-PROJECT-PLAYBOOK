$(function() {
    $(window).on('load', function(){
        $.ajax({
			url: '/teams',
			type: 'GET',
			success: function(response){
                console.log(response[0][0])
                let tbodyEl2 = $('#teamsbody');

                tbodyEl2.html('');
                
                for (let i = 0; i < response.length; i++) {
                console.log(response[i])
                    tbodyEl2.append('\
                        <tr>\
                        <td class="teamid">' + response[i][2] + '</td>\
                        <td>"' + response[i][1] +'"</td>\
                        <td>"' + response[i][3] + "-" + response[i][4]+'"</td>\
                        </tr>\
                        ');
                }

			},
			error: function(error){
				console.log(error);
			}
            
        });
    });


});

