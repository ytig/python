var list = [];

function registerEvent(object) {
  var i = list.indexOf(object);
  if (i >= 0) {
    return;
  }
  list.push(object);
}

function unregisterEvent(object) {
  var i = list.indexOf(object);
  if (i < 0) {
    return;
  }
  list.splice(i, 1);
}

function dispatchEvent() {
  for (var object of new Array(...list)) {
    object.onResize();
  }
}

window.addEventListener('resize', dispatchEvent);

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent,
  dispatchEvent: dispatchEvent
};
