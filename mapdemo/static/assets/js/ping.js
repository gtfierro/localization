function make_req() {
  var d = new Date();
  $.ajax({
    url: '/dummy',
    data: {'d': d.getTime()},
    timeout: 100,
    complete: function() {
      setTimeout(make_req, 500);
    }
  });
}
$(function() {
  make_req();
});
