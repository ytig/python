var def = null;
var cur = -1;
var list = [];

function setDefaultWindow(object) {
  def = object;
}

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

function requestNextFocus() {
  if (list.length <= 0) {
    return;
  }
  requestFocus(list[(cur + 1) % list.length]);
}

document.addEventListener('keydown', function (event) {
  var consume = false;
  consume = cur >= 0 ? list[cur].onKeyDown(event) : false;
  if (!consume) {
    consume = def != null ? def.onKeyDown(event) : false;
  }
  if (consume) {
    event.preventDefault();
  }
});

export default {
  setDefaultWindow: setDefaultWindow,
  registerWindow: registerWindow,
  unregisterWindow: unregisterWindow,
  requestFocus: requestFocus,
  requestNextFocus: requestNextFocus
};
