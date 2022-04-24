/**
 * Necessary imports for reading JSON files and using the Express framework
 */
const { json, application } = require('express');
const express = require('express');
const app = express();
let PORT = 3000;

/**
 * Other requirements for reading JSON files
 */
 const fs = require('fs');
 const path = require('path');
 app.use(express.json());

/**
 * This sets the local Node server to the predefined port (3000)
 */
 app.listen(PORT, function(err){
    if (err) console.log(err);
    console.log("Server listening on PORT", PORT);
});

/**
 * The following methods are to demo grabbing a forecast for a specific point
 * The goal of this would be to allow for the importation of forecasts to derive weather-based analytics
 */

/**
 * Making sure node/express is set up correctly in this file
 */
 app.get('/home', (req,res) => {
    res.send("This worked");
});

/**
 * These variables needed to make the request to the NWS API
 * 
 * https because of the protocol
 * Agent because the NWS API requires a user-agent to gain access to their API
 */
const https = require('https');
const { hasUncaughtExceptionCaptureCallback } = require('process');
const { Agent } = require('http');
const { url } = require('inspector');
/**
 * This method is to grab and parse the data from the NWS API
 * 
 * For demonstration purposes, I the same coordinates and the NWS API demo on their website:
 * https://weather-gov.github.io/api/general-faqs#how-to-get-forecast
 * Lat: 38.8894
 * Lon: -77.0352
 * 
 * NOTE: First two runs will throw errors (one for each request), but after this the files will be written
 *      I'm not sure why this error keeps occuring
 */
app.get('/hourforecast/:lat/:lon/:hour', (req,res) => {
    let latitude = parseFloat(req.params["lat"]);
    let longitude = parseFloat(req.params["lon"]);
    let hour = String(req.params["hour"]);

    /**
     * This calls the method to pull the NWS API request
     */
    let forecast = getForecast(latitude,longitude, res);
    //res.send(forecast);
    /**
     * On the second JSON file, the 'periods' field refers to the forecast hour,
     *  with the 'number field representing the hour of the forecast
     */
    res.send(forecast.properties.periods[hour]);
});
/**
 * This method is the helper method that makes the desired API requests
 * @param {*} lat Latitude of the point desired, pulled from URL request
 * @param {*} lon longitude of point desired, pulled from URL request
 * @param {*} response given from the app.get method, used to call the website
 * @returns The JSON file of the second request made
 */
function getForecast(lat,lon, response) {
    /**
     * Options used in the https request
     */
    const options = {
        hostname : 'api.weather.gov' ,
        //port : 443,
        path: '/points/' + String(lat) + ',' + String(lon) ,
        method : 'GET' ,
        headers: {'User-Agent' : 'Project API , alexander.j.nozka-1@ou.edu'}
    };
    /**
     * This section reads in the data and files it in their respective JSON files
     * On the NWS API website, it is required to make two requests to get the proper data needed for each location
     */
    var file = fs.createWriteStream("Request1.json");
    var request = https.get(options, function(response) {
      response.on("finish",function(){
        console.log( fs.readFileSync("Request1.json",{encoding:"utf8"}));
      }).pipe(file);
    });
    //Parses the data in the first file
    let rawdata = fs.readFileSync(path.resolve(__dirname, 'Request1.json'));
    let request1 = JSON.parse(rawdata);
    //Making the second request
    const url = new URL(request1.properties.forecastHourly);
    let options2 = {
        hostname : url.hostname,
        path : url.pathname , 
        method : 'GET' ,
        headers: {'User-Agent' : 'Project API , alexander.j.nozka-1@ou.edu'}
    };
    var file2 = fs.createWriteStream("Request2.json");
    request = https.get(options2, function(response) {
      response.on("finish",function(){
        console.log( fs.readFileSync("Request2.json",{encoding:"utf8"}));
      }).pipe(file2);
    });
    //Parsing the data from the second request
    let rawdata2 = fs.readFileSync(path.resolve(__dirname, 'Request2.json'));
    let request2 = JSON.parse(rawdata2);
    return request2; 
}
/**
 * This api request prints the full JSON for the specified lat/lon
 */
app.get('/fullJSON/:lat/:lon', (req,res) => {
  let latitude = parseFloat(req.params["lat"]);
  let longitude = parseFloat(req.params["lon"]);

  let forecast = getForecast(latitude,longitude, res);
  res.send(forecast);
});
/**
 * This api request is supposed to grant the forecast between the given hours
 * 
 * NOTE:This includes the first hour and excludes the last hour
 * 
 * ind_forecast is the object created to store all of the values of a forecast of a given hour
 * forecastArray is an array to hold all of these different values
 * forecastString is the String submitted to the website as the final output
 */
app.get('/forecastrange/:lat/:lon/:first/:second', (req,res) => {
  /**
   * Pulling in all the initial conditions
   */
  let parameters = req.params;
  let latitude = parseFloat(req.params["lat"]);
  let longitude = parseFloat(req.params["lon"]);
  let initialhour = String(req.params["first"]);
  let finalhour = String(req.params["second"]);

  let forecast = getForecast(latitude,longitude, res);

  /**
   * This is pulling the forecast from the requested hours into the array
   * each individual forecast is an object with the specified properties below
   */
  let ind_forecast;
  let forecastArray = new Array();
  let index = 0;
  for(let x = parseInt(initialhour); x < parseInt(finalhour); x++)
  {
    ind_forecast = {
      hour: String(x),
      temp: String(forecast.properties.periods[x].temperature) + String(forecast.properties.periods[x].temperatureUnit),
      wind: String(forecast.properties.periods[x].windSpeed) + String(forecast.properties.periods[x].windDirection),
      conditions: forecast.properties.periods[x].shortForecast
    };
    forecastArray[index] = ind_forecast;
    index++;
    ind_forecast = null;
  }
  /**
   * This is now hopefully just for formatting purposes
   */
   let forecastString = "";
  for(let y = 0; y < forecastArray.length; y++)
  {
    forecastString+= "Hour: " + forecastArray[y].hour + "\n";
    forecastString+= "Temperature: " + forecastArray[y].temp + "\t";
    forecastString+= "Wind: " + forecastArray[y].wind + "\t";
    forecastString+= "Conditions: " + forecastArray[y].conditions + "\n\n";
  }
  res.send(forecastString);
});
