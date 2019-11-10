var cur = -1;
var list = [];

function registerWindow(object) {
  var i = list.indexOf(object);
  if (i >= 0) {
    return;
  }
  list.push(object);
}

function unregisterWindow(object) {
  var i = list.indexOf(object);
  if (i < 0) {
    return;
  }
  list.splice(i, 1);
  if (i == cur) {
    cur = -1;
    object.onFocusChanged(false);
  }
}

function requestFocus(object) {
  var old_object = cur >= 0 ? list[cur] : null;
  cur = list.indexOf(object);
  var new_object = cur >= 0 ? list[cur] : null;
  if (old_object == new_object) {
    return;
  }
  if (old_object != null) {
    old_object.onFocusChanged(false);
  }
  if (new_object != null) {
    new_object.onFocusChanged(true);
  }
}

document.addEventListener('keydown', function (event) {
  if (cur >= 0) {
    if (list[cur].onKeyDown(event)) {
      event.preventDefault();
      return;
    }
  }
  if (event.keyCode == 32) {
    if (document.fullscreenElement == null) {
      document.body.webkitRequestFullScreen();
    }
    event.preventDefault();
    return;
  }
});

export default {
  registerWindow: registerWindow,
  unregisterWindow: unregisterWindow,
  requestFocus: requestFocus
};
