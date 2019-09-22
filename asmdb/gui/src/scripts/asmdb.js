function for_test(bytes) {
  var str = '';
  for (var b in bytes) {
    str += String.fromCharCode(bytes[b]);
  }
  return str;
}

var registers = null;
var stack = null;
var memory = null;

setTimeout(() => {
  if (registers) {
    registers.onBreak({
      'r0': 1234
    })
  }
  if (stack) {
    var bytes = [];
    for (var i = 0; i < 10 * 256; i++) {
      bytes[bytes.length] = Math.floor(256 * Math.random());
    }
    stack.onBreak(1, for_test(bytes));
  }
  if (memory) {
    bytes = [];
    var range = memory.getRange();
    for (var i = 0; i < range[1] - range[0]; i++) {
      bytes[bytes.length] = Math.floor(256 * Math.random());
    }
    memory.onBreak(range[0], for_test(bytes));
  }
}, 1000);

function registerEvent(type, object) {
  //todo
  switch (type) {
    case 'registers':
      registers = object;
      break;
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
