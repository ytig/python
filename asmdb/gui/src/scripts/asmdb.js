var struct = {};

document.cookie = 'token={}; path=/'; //for test
// var ws = new WebSocket('ws://' + location.host + '/ws');
var ws = new WebSocket('ws://localhost:8080/ws');
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
      if (data.tag in callbacks) {
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
      }
      break;
  }
};

var counter = 0;
var _registers = null;

class Union {
  constructor(callable) {
    this._callable = callable;
    this._wait = 0;
    this._events = [];
  }

  wait() {
    this._wait++;
  }

  notify(event) {
    if (event != undefined) {
      this._events.push(event);
    }
    if (--this._wait == 0) {
      if (this._callable()) {
        for (var _event of this._events) {
          _event();
        }
      }
      this._events.splice(0, this._events.length);
    }
  }
}

function push(attrName, newValue, oldValue) {
  switch (attrName) {
    case 'suspend':
      counter++;
      if (newValue) {
        var _counter = counter;
        ir((registers) => {
          var union = new Union(() => {
            return _counter == counter;
          });
          union.wait();
          //bar
          union.wait();
          union.notify(() => {
            _registers = registers;
            iterObjects('bar', (object) => {
              object.onBreak();
            });
          });
          //assembly todo
          //registers
          union.wait();
          union.notify(() => {
            iterObjects('registers', (object) => {
              object.onBreak(registers);
            });
          });
          //stack
          union.wait();
          var sp = registers['sp'];
          xb([sp, sp + 400 * 10], (stack) => {
            union.notify(() => {
              iterObjects('stack', (object) => {
                object.onBreak(sp, stack);
              });
            });
          });
          //memory
          iterObjects('memory', (object) => {
            union.wait();
            var range = object.getRange();
            if (range == null) {
              union.notify(() => {
                object.onBreak(null, null);
              });
            } else {
              xb(range, (memory) => {
                union.notify(() => {
                  object.onBreak(range[0], memory);
                });
              });
            }
          });
          union.notify();
        });
      } else {
        iterObjects('*', (object) => {
          object.onContinue();
        });
      }
      break;
    case 'breakpoints':
      iterObjects('*', (object) => {
        if (object.onBreakpoints) {
          object.onBreakpoints(newValue);
        }
      });
      break;
    case 'watchpoints':
      iterObjects('*', (object) => {
        if (object.onWatchpoints) {
          object.onWatchpoints(newValue);
        }
      });
      break;
  }
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
  if (success || failure) {
    callbacks[data.tag] = {
      success: success,
      failure: failure
    };
  }
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

function rlse() {
  pull('rlse');
}

function ir(success) {
  pull('ir', [], function (ret) {
    if (success) {
      success(ret);
    }
  });
}

function xb(range, success) {
  pull('xb', [...range], function (ret) {
    if (success) {
      success(atob(ret));
    }
  });
}

var objects = {};

function iterObjects(filter, handler) {
  filter = filter.split('|');
  if (filter.indexOf('*') >= 0) {
    filter = null;
  }
  for (var type in objects) {
    if (filter && filter.indexOf(type) < 0) {
      continue;
    }
    var array = objects[type];
    for (var object of array) {
      handler(object);
    }
  }
}

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

const asmType = 'arm32';
const asmUnit = {
  'arm32': 4
} [asmType];
const asmRegs = {
  'arm32': ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'cpsr']
} [asmType];

function getAddressUsage(int) {
  //todo
  if (int % 32 == 0) {
    return '2';
  }
  if (int % 32 == 1) {
    return '3';
  }
  if (int % 32 == 2) {
    return '4';
  }
  return '1';
}

export default {
  next: next,
  step: step,
  cont: cont,
  rlse: rlse,
  xb: xb,
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent,
  asmUnit: asmUnit,
  asmRegs: asmRegs,
  getAddressUsage: getAddressUsage
};
