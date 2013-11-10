$(document).ready(function() {
  $.get('../alarms', function(data) {
    console.log(data);
    var alarms = JSON.parse(data);
    var $alarmsList = $('#alarms-list');
    for(var i = 0; i < alarms.length; i++) {
      var listItem = document.createElement('li');
      listItem.innerHTML = alarms[i];
      listItem.className = 'noon';
      $alarmsList.append(listItem);
    }
  });
});
