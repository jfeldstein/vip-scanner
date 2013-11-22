csv = require 'csv'
fs  = require 'fs'
Twit = require 'twit'
Deferred = require("promised-io/promise").Deferred
All = require("promised-io/promise").all
request = require('request')
rateLimit = require('function-rate-limit')


T = new Twit
  consumer_key:         ''
  consumer_secret:      ''
  access_token:         ''
  access_token_secret:  ''



# Get one user's twitter count
rate_limited_twitter_call = rateLimit 180, 900000, (sn, d) ->
  T.get 'users/show', {screen_name: sn}, (err, resp) ->
    if err
      console.log("TWITTER ERROR", err)
      resp = {followers_count: ''}

    d.resolve resp.followers_count

getTwitterFollowerCount = (url) ->
  if !( has_twitter = url.match(/\/([^\/]+)$/) )?
    return ''
  
  deferred = new Deferred

  screen_name = has_twitter[1]

  rate_limited_twitter_call screen_name, deferred

  deferred.promise



# Get one user's angelco count
getAngelCoFollowerCount = (url) ->
  if !( has_angelco = url.match(/\/([^\/]+)$/) )?
    return ''
  
  deferred = new Deferred

  screen_name = has_angelco[1]

  params = 
    url: "https://api.angel.co/1/users/search?slug=#{screen_name}"
    json: true

  request params, (e, r, angelcoUser) ->
    if e? 
      console.log("ANGELCO ERROR", e)
      angelcoUser = {follower_count: ''}

    deferred.resolve angelcoUser.follower_count

  deferred.promise


csv()
.from.stream(fs.createReadStream(__dirname+'/userdata.csv'))
.to.path(__dirname+'/socialuserdata.csv')
.transform( (row, index, cb) ->
  
  next = (counts) ->
    cb false, row.concat(counts)

  orCry = (error) ->
    cb error

  All(getTwitterFollowerCount(row[4]), getAngelCoFollowerCount(row[5])).then next, orCry

)
.on('record', (row,index) ->
  console.log('#'+index+' '+JSON.stringify(row));
)
.on('end', (count) ->
  console.log('Number of lines: '+count);
)
.on('error', (error) ->
  console.log(error.message);
);