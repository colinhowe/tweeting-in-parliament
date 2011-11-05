last_y_used = 0;
tweet_height = 150;

place_tweet_element = function(minute, times, el) {
  // Find the closest time value
  //
  if (minute < times[0]) {
    $('#predebate_tweets').append(el);
  } else if (minute < times[times.length - 1]) {
    // Find the two time slots that contain this tweet
    var start_index = -1;
    var stop_index = -1;
    $.each(times, function(index, time) {
      if (time > minute) {
        start_index = index - 1;
        stop_index = index;
        return false;
      }
    });

    var start_y = $('#time_' + times[start_index]).position().top;
    var stop_y = $('#time_' + times[stop_index]).position().top;
    
    // Calculate the percentage of time through the period that this tweet is
    var period_length = times[stop_index] - times[start_index];
    var percentage = (minute - times[start_index]) / period_length; 
    
    // The desired position is offset from the start of the period by the
    // percentage through the period that the tweet is in time.
    var desired_y = start_y + (stop_y - start_y) *  percentage;
    if (desired_y < last_y_used) {
      desired_y = last_y_used;
    }
    last_y_used = desired_y + tweet_height;

    el.css('position', 'absolute');
    el.css('top', desired_y + 'px');
    el.css('left', ($('#hansard_body').position().left + 600) + 'px');
    $('#hansard_body').append(el);
  } else {
    $('#postdebate_tweets').append(el);
    // Time will be somewhere in between
  }
};

display_tweet = function(times, tweet) {
  // Find the number of minutes since midnight and display as close as possible
  // to that time
  time_components = tweet.time.split(':');
  minute = parseInt(time_components[0]) * 60 + parseInt(time_components[1]);

  el = $('<div class="tweet"></div>')
    .append($('<img src="' + tweet.profile_pic + '"/>'))
    .append($('<a href="http://twitter.com/' + tweet.screenname + '" class="screenname">@' + tweet.screenname + '</span>'))
    .append($('<span class="body"> ' + tweet.body + '</span>'))
    .append($('<br/><span class="time"> ' + tweet.time + '</span>'))
  ;
  place_tweet_element(minute, times, el);
};

display_tweets = function(times, tweets) {
  // Sort the times
  times.sort(function(a, b) { return a - b; });
  
  // Display each tweet
  $.each(tweets, function(index, tweet) {
    display_tweet(times, tweet);
  });
};
