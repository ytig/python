var cur = -1;
var list = [];

function registerWindow(object) {
  if (!(object in list)) {
    list[list.length] = object;
  }
}

function unregisterWindow(object) {
  for (var i = 0; i < list.length; i++) {
    if (list[i] == object) {
      if (i == cur) {
        object.onFocusChanged(false);
        cur = -1;
      }
      list.splice(i, 1);
      break;
    }
  }
}

function requestFocus(object) {
  var _cur = cur;
  cur = -1;
  for (var i = 0; i < list.length; i++) {
    if (list[i] == object) {
      cur = i;
      break;
    }
  }
  if (_cur != cur) {
    if (_cur >= 0) {
      list[_cur].onFocusChanged(false);
    }
    if (cur >= 0) {
      list[cur].onFocusChanged(true);
    }
  }
}

$(document).keyup(function (event) {
  if (cur >= 0) {
    list[cur].onKeyboradClick(event);
  }
});

export default {
  registerWindow: registerWindow,
  unregisterWindow: unregisterWindow,
  requestFocus: requestFocus
}
