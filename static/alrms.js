$(document).ready(function() {
  $.get('../alarms', function(data) {
    console.log(data);
    var alarms = JSON.parse(data);
    var $alarmsList = $('#alarms-list');
    for(var i = 0; i < alarms.length; i++) {
      var date = new Date(alarms[i] * 1000);
      var listItem = document.createElement('li');
      listItem.innerHTML = date.toLocaleTimeString('en-US');
      if (date.getHours() < 6) {
        listItem.className = 'night';
      } else if (date.getHours() < 7) {
        listItem.className = 'sunrise';
      } else if (date.getHours() < 12) {
        listItem.className = 'morning';
      } else if (date.getHours() < 13) {
        listItem.className = 'noon';
      } else if (date.getHours() < 14) {
        listItem.className = 'early-afternoon';
      } else if (date.getHours() < 16) {
        listItem.className = 'mid-afternoon';
      } else if (date.getHours() < 18) {
        listItem.className = 'late-afternoon';
      } else if (date.getHours() < 19) {
        listItem.className = 'dusk';
      } else if (date.getHours() < 20) {
        listItem.className = 'early-night';
      } else {
        listItem.className = 'night';
      }
      $alarmsList.append(listItem);
    }
  });
});
