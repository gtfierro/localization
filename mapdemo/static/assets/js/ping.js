function make_req() {
  var d = new Date();
  $.ajax({
    'url': '/dummy',
    'data': {'d': d.getTime()},
    'timeout': 100,
    'complete': function() {
      console.log('complete');
      setTimeout("make_req();", 250);
    }
  });
}
$(function() {
  make_req();
});
