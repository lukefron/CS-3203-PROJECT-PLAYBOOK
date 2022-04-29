$(function() {

    $('#search-form').on('submit', function(event){
    
        event.preventDefault();
        var createInput2 = $('#search-input');
    
      console.log(createInput2.val())
      console.log("runn ing")
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
    event.stopImmediatePropagation();
    return false;
    }); 
    
        //Get searched tweets
        $('#get-searched-teams').on('click', function() {
            $.ajax({
                url: '/teamSearch',
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
                             <td><a href="/teams/roster/' + response[i][0] +'" style="color: white; background-color: darkcyan;"> View Team Roster </a></td>\
                            <td><a href="addFavoriteTeam/' + response[i][0] +'" style="color: white; background-color: darkcyan;"> Add To Favorite Teams</a></td>\
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
         console.log("runn ing")
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
       event.stopImmediatePropagation();
       return false;
       }); 
    
    
        //Get searched tweets
        $('#get-searched-players').on('click', function() {
            $.ajax({
                url: '/playerSearch',
                success: function(response) {
        
                    let tbodyEl2 = $('#playersearchbody');

                    tbodyEl2.html('');

                    for (let i = 0; i < response.length; i++) {
                    var numId = response[i][0]
                    stringId = numId.toString();
                    console.log(response[i])
                        tbodyEl2.append('\
                     <tr>\
                     <td class="playerid">' + response[i][0] + '</td>\
                     <td>"' + response[i][1] +'"</td>\
                     <td>"' + response[i][2] + " " + response[i][3] + '"</td>\
                     <td><a href="/teams/roster/' + response[i][1] +'" style="color: white; background-color: darkcyan;"> View Team Roster </a></td>\
                     <td><a href="addFavoritePlayer/' + response[i][0] +'" style="color: white; background-color: darkcyan;"> Add To Favorite Players</a></td>\
                     </tr>\
                            ');
                    }
                },
                error: function () {

                }
                
            });
                   event.stopImmediatePropagation();
                   return false;
        });


        $('#clear-searched-players').on('click', function() {
            $.ajax({
                url: '/clearPlayerSearches',
                success: function(response) {
              console.log(response);
              $('#get-searched-players').click();
                },
                error: function () {
                
                }
            });
        });
        
        



});

