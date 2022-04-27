$(function() {

    $('#search-form').on('submit', function(event){
        event.preventDefault();
        var createInput2 = $('#search-input');
    
      console.log(createInput2.val())
      $.ajax({
          url: '/teamSearch',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({ teamName: createInput2.val() }),
          success: function(response) {
              console.log(response);
              $('#get-searched-teams').click();
          }
      });
    }); 
    
        //Get searched tweets
        $('#get-searched-teams').on('click', function() {
            $.ajax({
                url: '/teamSearch',
                contentType: 'application/json',
                success: function(response) {
        
                    let tbodyEl2 = $('#searchbody');

                    tbodyEl2.html('');

                    for (let i = 0; i < response.length; i++) {
                    var numId = response[i][0]
                    stringId = numId.toString();
                    console.log(response[i])
                        tbodyEl2.append('\
                            <tr>\
                            <td class="teamid">' + response[i][0] + '</td>\
                            <td>"' + response[i][1] +'"</td>\
                            <td>"' + response[i][3] + "-" + response[i][4]+'"</td>\
                            <td><a href="/teams/roster/' + response[i][0] +'"> More Details</a></td>\
                            <td><a href="addFavoriteTeam/' + response[i][0] +'"> Add To Favorite Teams</a></td>\
                            </tr>\
                            ');
                    }
                },
                error: function () {

                }
            });
        });

        $('#clear-searched-teams').on('click', function() {
            $.ajax({
                url: '/clearSearches',
                contentType: 'application/json',
                success: function(response) {
              console.log(response);
              $('#get-searched-teams').click();
                },
                error: function () {

                }
            });
        });

        
    $('#player-search-form').on('submit', function(event){
        event.preventDefault();
        var createInput2 = $('#player-search-input');
    
      console.log(createInput2.val())
      $.ajax({
          url: '/playerSearch',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({ playerName: createInput2.val() }),
          success: function(response) {
              console.log(response);
              $('#get-searched-players').click();
          }
      });
    }); 
    
        //Get searched tweets
        $('#get-searched-players').on('click', function() {
            $.ajax({
                url: '/playerSearch',
                contentType: 'application/json',
                success: function(response) {
        
                    let tbodyEl2 = $('#playersearchbody');

                    tbodyEl2.html('');
                    for (let i = 0; i < response.length; i++) {
                    var numId = response[i][0]
                    stringId = numId.toString();
                    console.log(response[i])
                        tbodyEl2.append('\
                            <tr>\
                            <td class="playerid">' + response[i][2] + '</td>\
                            </tr>\
                            ');
                    }
                },
                error: function () {

                }
            });
        });

        $('#clear-searched-players').on('click', function() {
            $.ajax({
                url: '/clearPlayerSearches',
                contentType: 'application/json',
                success: function(response) {
                    console.log(response)
                    $('#get-searched-players').click();
                    
                },
                error: function () {

                }
            });
        });





});

