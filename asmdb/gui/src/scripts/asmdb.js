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
    var _regs = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'cpsr'];
    var regs = {};
    for (var i = 0; i < _regs.length; i++) {
      var max = Math.random() < 0.5 ? 0xffffffff : 0xff;
      regs[_regs[i]] = Math.floor(max * Math.random());
    }
    registers.onBreak(regs);
    registers.testRegs = regs;
    setTimeout(() => {
      for (var i = 0; i < _regs.length; i++) {
        if (Math.random() < 0.8) {
          continue;
        }
        var max = Math.random() < 0.5 ? 0xffffffff : 0xff;
        regs[_regs[i]] = Math.floor(max * Math.random());
      }
      registers.onBreak(registers.testRegs);
    }, 2500);
  }
  if (stack) {
    var bytes = [];
    for (var i = 0; i < 10 * 256; i++) {
      bytes[bytes.length] = Math.floor(256 * Math.random());
    }
    stack.onBreak(1, for_test(bytes));
    stack.testBytes = bytes;
    setTimeout(() => {
      stack.testBytes[0] = 147;
      stack.testBytes[1] = 147;
      stack.testBytes[2] = 147;
      stack.testBytes[3] = 147;
      stack.onBreak(1, for_test(stack.testBytes));
    }, 2500);
  }
  if (memory) {
    var range = memory.getRange();
    if (range == null) {
      memory.onBreak();
    } else {
      var bytes = [];
      for (var i = 0; i < range[1] - range[0]; i++) {
        bytes[bytes.length] = Math.floor(256 * Math.random());
      }
      memory.onBreak(range[0], for_test(bytes));
    }
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

function xb(range, callback) {
  //todo
  setTimeout(() => {
    var bytes = [];
    for (var i = 0; i < range[1] - range[0]; i++) {
      bytes[bytes.length] = Math.floor(256 * Math.random());
    }
    callback(range[0], for_test(bytes));
  }, 20);
}

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent,
  xb: xb
};
