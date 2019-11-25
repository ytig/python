class Debugger {
  constructor() {
    document.cookie = 'token={}; path=/'; //for test
    this.TYPE = 'arm32';
    switch (this.TYPE) {
      case 'arm32':
        this.UNIT = 4;
        this.REGS = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'cpsr'];
        this.SPNM = 'sp';
        this.LRNM = 'lr';
        this.PCNM = 'pc';
        this.WLEN = 4;
        break;
    }
    this.struct = {
      suspend: false,
      breakpoints: [],
      watchpoints: []
    };
    this.counter = 0;
    this.registers = null;
    this.tag = 0;
    this.callbacks = {};
    this.objects = {};
    this.ws = new WebSocket('ws://localhost:8080/ws');
    // this.ws = new WebSocket('ws://' + location.host + '/ws');
    this.ws.onmessage = this.onMessage.bind(this);
  }

  onMessage(event) {
    var data = JSON.parse(event.data);
    switch (data.type) {
      case 'push':
        if (data.key in this.struct) {
          var oldValue = this.struct[data.key];
          this.struct[data.key] = data.val;
          this.push(data.key, data.val, oldValue);
        } else {
          this.push(data.key, data.val);
        }
        break;
      case 'pull':
        if (data.tag in this.callbacks) {
          var callback = this.callbacks[data.tag];
          delete this.callbacks[data.tag];
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
  }

  push(attrName, newValue, oldValue) {
    switch (attrName) {
      case 'suspend':
        this.counter++;
        if (newValue) {
          var counter = this.counter;
          this.reg((registers) => {
            var union = new Union(() => {
              return counter == this.counter;
            });
            union.wait();
            //bar
            union.wait();
            union.notify(() => {
              this.registers = registers;
              this.iterObjects('bar', (object) => {
                object.onBreak();
              });
            });
            //assembly
            var pc = registers[this.PCNM];
            this.iterObjects('assembly', (object) => {
              union.wait();
              var range = object.getRange(pc);
              if (range == null) {
                union.notify(() => {
                  object.onBreak(pc, null);
                });
              } else {
                this.asm(range, (assembly) => {
                  union.notify(() => {
                    object.onBreak(pc, assembly);
                  });
                });
              }
            });
            //registers
            union.wait();
            union.notify(() => {
              this.iterObjects('registers', (object) => {
                object.onBreak(registers);
              });
            });
            //stack
            union.wait();
            var sp = registers[this.SPNM];
            this.mem([sp, sp + 400 * 10], (stack) => {
              union.notify(() => {
                this.iterObjects('stack', (object) => {
                  object.onBreak(sp, stack);
                });
              });
            });
            //memory
            this.iterObjects('memory', (object) => {
              union.wait();
              var range = object.getRange();
              if (range == null) {
                union.notify(() => {
                  object.onBreak(null, null);
                });
              } else {
                this.mem(range, (memory) => {
                  union.notify(() => {
                    object.onBreak(range[0], memory);
                  });
                });
              }
            });
            union.notify();
          });
        } else {
          this.iterObjects('bar|assembly|registers|stack|memory', (object) => {
            object.onContinue();
          });
        }
        break;
      case 'breakpoints':
        this.iterObjects('*', (object) => {
          if (object.onBreakpoints) {
            object.onBreakpoints(newValue);
          }
        });
        break;
      case 'watchpoints':
        this.iterObjects('*', (object) => {
          if (object.onWatchpoints) {
            object.onWatchpoints(newValue);
          }
        });
        break;
      case 'assigned':
        var where = newValue.split('=')[0];
        var value = newValue.split('=')[1];
        if (where.startsWith('*')) {
          this.iterObjects('stack|memory', (object) => {
            object.onAssigned(parseInt(where.slice(1)), parseInt(value));
          });
        } else {
          this.registers[where] = parseInt(value);
          this.iterObjects('registers', (object) => {
            object.onAssigned(where, parseInt(value));
          });
        }
        break;
    }
  }

  pull(method, params, success, failure) {
    var data = {
      type: 'pull',
      tag: ++this.tag,
      method: method,
      params: params || []
    };
    if (success || failure) {
      this.callbacks[data.tag] = {
        success: success,
        failure: failure
      };
    }
    this.ws.send(JSON.stringify(data));
  }

  next() {
    this.pull('next');
  }

  step() {
    this.pull('step');
  }

  cont() {
    this.pull('cont');
  }

  rlse() {
    this.pull('rlse');
  }

  asm(range, success) {
    this.pull('asm', [...range], function (ret) {
      if (success) {
        success(ret);
      }
    });
  }

  reg(success) {
    this.pull('reg', [], function (ret) {
      if (success) {
        success(ret);
      }
    });
  }

  mem(range, success) {
    this.pull('mem', [...range], function (ret) {
      if (success) {
        success(atob(ret));
      }
    });
  }

  bpt(delPoints, setPoints) {
    this.pull('bpt', [delPoints, setPoints]);
  }

  wpt(delPoints, setPoints) {
    this.pull('wpt', [delPoints, setPoints]);
  }

  asgn(express) {
    this.pull('asgn', [express]);
    this.push('assigned', express);
  }

  iterObjects(filter, handler) {
    filter = filter.split('|');
    if (filter.indexOf('*') >= 0) {
      filter = null;
    }
    for (var type in this.objects) {
      if (filter && filter.indexOf(type) < 0) {
        continue;
      }
      var array = this.objects[type];
      for (var object of array) {
        handler(object);
      }
    }
  }

  registerEvent(type, object) {
    if (!(type in this.objects)) {
      this.objects[type] = [];
    }
    var i = this.objects[type].indexOf(object);
    if (i >= 0) {
      return;
    }
    this.objects[type].push(object);
    var suspend = this.struct.suspend;
    var counter = this.counter;
    switch (type) {
      case 'bar':
        if (!suspend) {
          object.onContinue();
        } else {
          object.onBreak();
        }
        break;
      case 'assembly':
        if (!suspend) {
          object.onContinue();
        } else {
          this.reg((registers) => {
            if (counter != this.counter) {
              return;
            }
            var pc = registers[this.PCNM];
            var range = object.getRange(pc);
            if (range == null) {
              object.onBreak(pc, null);
            } else {
              this.asm(range, (assembly) => {
                if (counter != this.counter) {
                  return;
                }
                object.onBreak(pc, assembly);
              });
            }
          });
        }
        break;
      case 'registers':
        if (!suspend) {
          object.onContinue();
        } else {
          this.reg((registers) => {
            if (counter != this.counter) {
              return;
            }
            object.onBreak(registers);
          });
        }
        break;
      case 'stack':
        if (!suspend) {
          object.onContinue();
        } else {
          this.reg((registers) => {
            var sp = registers[this.SPNM];
            this.mem([sp, sp + 400 * 10], (stack) => {
              if (counter != this.counter) {
                return;
              }
              object.onBreak(sp, stack);
            });
          });
        }
        break;
      case 'memory':
        if (!suspend) {
          object.onContinue();
        } else {
          var range = object.getRange();
          if (range == null) {
            object.onBreak(null, null);
          } else {
            this.mem(range, (memory) => {
              if (counter != this.counter) {
                return;
              }
              object.onBreak(range[0], memory);
            });
          }
        }
        break;
    }
    if (object.onBreakpoints) {
      object.onBreakpoints(this.struct.breakpoints);
    }
    if (object.onWatchpoints) {
      object.onWatchpoints(this.struct.watchpoints);
    }
  }

  unregisterEvent(type, object) {
    if (!(type in this.objects)) {
      return;
    }
    var i = this.objects[type].indexOf(object);
    if (i < 0) {
      return;
    }
    this.objects[type].splice(i, 1);
  }

  isSuspend() {
    return this.struct.suspend;
  }

  getRegisters() {
    return Object.assign({}, this.registers);
  }

  getAssemblyRange() {
    return [0, Math.pow(16, 2 * this.UNIT)]; //todo
  }

  getRegistersRange() {
    var range = [];
    var _regs = [this.SPNM, this.LRNM, this.PCNM];
    for (var reg of this.REGS) {
      if (_regs.indexOf(reg) < 0) {
        range.push(reg);
      }
    }
    return range;
  }

  getMemoryRange() {
    return [0, Math.pow(16, 2 * this.UNIT)];
  }

  getAddressUsage(int) {
    var delta = int - this.registers[this.SPNM];
    if (delta >= 0 && delta < 400 * 10) {
      return '3';
    }
    //todo
    return '1';
  }

  getRegsString(int) {
    var str = '';
    switch (this.getAddressUsage(int)) {
      case '1':
        if (int >= 0x21 && int <= 0x7e) {
          if (int == 0x27) {
            str = '"\'"';
          } else {
            str = "'" + String.fromCharCode(int) + "'";
          }
        }
        break;
      case '3':
        str = this.SPNM;
        var delta = int - this.registers[this.SPNM];
        if (delta != 0) {
          str += '+' + delta;
        }
        break;
    }
    return str;
  }

  getCpsrString(int) {
    var n = (int & 0x80000000) == 0 ? '' : 'N';
    var z = (int & 0x40000000) == 0 ? '' : 'Z';
    var c = (int & 0x20000000) == 0 ? '' : 'C';
    var v = (int & 0x10000000) == 0 ? '' : 'V';
    return n + z + c + v;
  }

  getWatchpointsLength() {
    return this.struct.watchpoints.length;
  }
}

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

var instance = null;

function newInstance() {
  instance = new Debugger();
}

function getInstance() {
  return instance;
}

export default {
  newInstance: newInstance,
  getInstance: getInstance
};
