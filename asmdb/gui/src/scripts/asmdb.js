var struct = {};

document.cookie = "token={}; path=/"; //for test
var ws = new WebSocket("ws://" + location.host + "/ws");
ws.onmessage = function (event) {
  var data = JSON.parse(event.data);
  switch (data.type) {
    case 'push':
      if (!(data.key in struct)) {
        struct[data.key] = data.val;
        push(data.key, data.val);
      } else {
        var oldValue = struct[data.key];
        struct[data.key] = data.val;
        push(data.key, data.val, oldValue);
      }
      break;
    case 'pull':
      var callback = callbacks[data.tag];
      delete callbacks[data.tag];
      if (data.e == null) {
        if (callback.success) {
          callback.success(data.r);
        }
      } else {
        if (callback.failure) {
          callback.failure(data.e);
        }
      }
      break;
  }
};

function push(attrName, newValue, oldValue) {
  //todo
  console.log(attrName, newValue);
}

var tag = 0;
var callbacks = {};

function pull(method, params, success, failure) {
  var data = {
    type: 'pull',
    tag: ++tag,
    method: method,
    params: params || []
  };
  callbacks[data.tag] = {
    success: success,
    failure: failure
  };
  ws.send(JSON.stringify(data));
}

function next() {
  pull('next');
}

function step() {
  pull('step');
}

function cont() {
  pull('cont');
}

function xb(range, success) {
  pull('xb', [...range], function (ret) {
    if (success) {
      success(atob(ret));
    }
  });
}

var objects = {};

function registerEvent(type, object) {
  if (!(type in objects)) {
    objects[type] = [];
  }
  var i = objects[type].indexOf(object);
  if (i >= 0) {
    return;
  }
  objects[type].push(object);
  //todo
}

function unregisterEvent(type, object) {
  if (!(type in objects)) {
    return;
  }
  var i = objects[type].indexOf(object);
  if (i < 0) {
    return;
  }
  objects[type].splice(i, 1);
}

export default {
  next: next,
  step: step,
  cont: cont,
  xb: xb,
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent
};
