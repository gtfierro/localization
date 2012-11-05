function make_req() {
  var d = new Date();
  $.ajax({
    'url': '/dummy',
    'data': {'d': d.getTime()},
    'timeout': 100,
    'complete': function() {
      console.log('complete');
      make_req();
    }
  });
}
$(function() {
  make_req();
});
