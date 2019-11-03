var cur = -1;
var list = [];

function registerWindow(object) {
  if (object in list) {
    return;
  }
  list.push(object);
}

function unregisterWindow(object) {
  if (!(object in list)) {
    return;
  }
  var i = list.indexOf(object);
  list.splice(i, 1);
  if (i == cur) {
    cur = -1;
    object.onFocusChanged(false);
  }
}

function requestFocus(object) {
  if (!(object in list)) {
    return;
  }
  var _object = cur >= 0 ? list[cur] : null;
  cur = list.indexOf(object);
  if (_object == object) {
    return;
  }
  if (_object != null) {
    _object.onFocusChanged(false);
  }
  object.onFocusChanged(true);
}

document.addEventListener('keydown', function (event) {
  if (cur >= 0) {
    if (list[cur].onKeyDown(event)) {
      event.preventDefault();
    }
  }
});

export default {
  registerWindow: registerWindow,
  unregisterWindow: unregisterWindow,
  requestFocus: requestFocus
};
