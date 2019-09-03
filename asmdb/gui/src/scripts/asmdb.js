function for_test(bytes) {
  var str = '';
  for (var b in bytes) {
    str += String.fromCharCode(bytes[b]);
  }
  return str;
}

var stack = null;
var memory = null;

setTimeout(() => {
  if (stack) {
    var bytes = [];
    for (var i = 0; i < 10 * 256; i++) {
      bytes[bytes.length] = Math.floor(256 * Math.random());
    }
    stack.onBreak(1, for_test(bytes));
  }
  if (memory) {
    bytes = [];
    for (var i = 0; i < 4 * 512; i++) {
      bytes[bytes.length] = Math.floor(256 * Math.random());
    }
    memory.onBreak(2048, for_test(bytes));
  }
}, 1000);

function registerEvent(type, object) {
  //todo
  switch (type) {
    case 'stack':
      stack = object;
      break;
    case 'memory':
      memory = object;
      break;
  }
}

function unregisterEvent(type, object) {
  //todo
}

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent
};
