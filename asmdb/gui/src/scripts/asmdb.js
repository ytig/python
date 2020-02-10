class Debugger {
  constructor(kernel) {
    switch (kernel) {
      case 'arm32':
        this.UNIT = 4;
        this.WLEN = 4;
        this.BEND = false;
        this.REGS = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'sp', 'lr', 'pc', 'cpsr'];
        this.SPNM = 'sp';
        this.LRNM = 'lr';
        this.PCNM = 'pc';
        break;
      default:
        this.UNIT = 4;
        this.WLEN = 0;
        this.BEND = false;
        this.REGS = [];
        this.SPNM = '';
        this.LRNM = '';
        this.PCNM = '';
        break;
    }
    this.struct = {
      suspend: false,
      breakpoints: [],
      watchpoints: [],
      maps: []
    };
    this.lenb = 0;
    this.utf8 = '';
    this.counter = 0;
    this.registers = null;
    this.unique = 0;
    this.callbacks = {};
    this.objects = {};
    this.ws = new WebSocket('ws://' + location.host + '/ws');
    this.state = 0;
    this.ws.onopen = this.onOpen.bind(this);
    this.ws.onmessage = this.onMessage.bind(this);
    this.ws.onclose = this.onClose.bind(this);
  }

  finish() {
    this.ws.close();
  }

  onOpen() {
    this.state = 1;
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
        if (data.xid in this.callbacks) {
          var callback = this.callbacks[data.xid];
          delete this.callbacks[data.xid];
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

  onClose() {
    if (this.state == 0) {
      this.iterObjects('world', (object) => {
        object.onNew('WebSocket connection to \'' + this.ws.url + '\' failed');
        object.onCtrl(false);
      });
    }
    this.state = -1;
  }

  push(attrName, newValue, oldValue) {
    switch (attrName) {
      case 'anew':
        this.iterObjects('world', (object) => {
          object.onNew(newValue);
        });
        break;
      case 'ctrl':
        this.iterObjects('world', (object) => {
          object.onCtrl(newValue);
        });
        break;
      case 'quit':
        if (newValue) {
          this.iterObjects('world', (object) => {
            object.onQuit();
          });
        }
        break;
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
        if (where.startsWith('$')) {
          where = where.substring(1);
          value = parseInt(value);
          this.registers[where] = value;
          this.iterObjects('registers', (object) => {
            object.onAssigned(where, value);
          });
        } else if (where.startsWith('*')) {
          where = parseInt(where.substring(1));
          value = parseInt(value);
          this.iterObjects('stack|memory', (object) => {
            object.onAssigned(where, value);
          });
        }
        break;
      case 'lenb':
        var lenb = this.lenb;
        var lenu = this.utf8.length;
        this.readu(lenb, (u, l) => {
          l -= (this.lenb - lenb);
          u = u.substring(this.utf8.length - lenu);
          if (l > 0) {
            this.lenb += l;
            this.utf8 += u;
            this.iterObjects('python3', (object) => {
              object.onRead(this.utf8);
            });
          }
        });
        break;
    }
  }

  pull(method, params, success, failure) {
    var data = {
      type: 'pull',
      xid: ++this.unique,
      method: method,
      params: params || []
    };
    if (success || failure) {
      this.callbacks[data.xid] = {
        success: success,
        failure: failure
      };
    }
    if (this.state != 0) {
      if (this.state == 1) {
        this.ws.send(JSON.stringify(data));
      }
    } else {
      var runnable = () => {
        if (this.state != 0) {
          if (this.state == 1) {
            this.ws.send(JSON.stringify(data));
          }
        } else {
          setTimeout(runnable);
        }
      }
      setTimeout(runnable);
    }
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

  setwinsize(rows, cols) {
    this.pull('setwinsize', [rows, cols]);
  }

  readu(offset, success) {
    this.pull('readb', [offset], function (ret) {
      if (success) {
        var b = atob(ret);
        success(decodeURIComponent(escape(b)), b.length);
      }
    });
  }

  writeu(u) {
    var b = unescape(encodeURIComponent(u));
    this.pull('writeb', [btoa(b)]);
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
      case 'python3':
        object.onRead(this.utf8);
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

  getAddressInfo(address) {
    var index = binarySearch(this.struct.maps, function (info) {
      if (address < info.start) {
        return -1;
      }
      if (address >= info.end) {
        return 1;
      }
      return 0;
    });
    if (index >= 0) {
      return this.struct.maps[index];
    } else {
      return null;
    }
  }

  getAddressLabel(address) {
    var info = this.getAddressInfo(address);
    if (info) {
      return info.section + '|' + getSimpleTarget(info.target);
    }
    return null;
  }

  getAddressBase() {
    if (this.registers != null) {
      var info = this.getAddressInfo(this.registers[this.PCNM]);
      if (info) {
        return info.start - info.offset;
      }
    }
    return null;
  }

  getRegisters() {
    return Object.assign({}, this.registers);
  }

  getAssemblyRange() {
    return [0, Math.pow(256, this.UNIT)];
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
    return [0, Math.pow(256, this.UNIT)];
  }

  getAddressUsage(int) {
    var usage = '1';
    var delta = int - this.registers[this.SPNM];
    if (delta >= 0 && delta < 400 * 10) {
      usage = '3';
    } else {
      var info = this.getAddressInfo(int);
      var target = this.getAddressInfo(this.registers[this.PCNM]);
      target = target != null ? target.target : null;
      if (info) {
        if (/^\/data\/app\/.*\.so$/.test(info.target) || info.target == target) {
          if (/^\.init$|^\.plt$|^\.text$|^\.fini$/.test(info.section)) {
            usage = '2';
          } else if (/^\.rodata$|^\.data$|^\.bss$/.test(info.section)) {
            if (int % (1 * this.UNIT) == 0) {
              usage = '4';
            }
          }
        } else if (/libc_malloc/.test(info.target)) {
          if (int % (2 * this.UNIT) == 0) {
            usage = '4';
          }
        }
      }
    }
    return usage;
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
      case '2':
        var info = this.getAddressInfo(int);
        var target = this.getAddressInfo(this.registers[this.PCNM]);
        target = target != null ? target.target : null;
        if (info) {
          if (info.target == target) {
            var delta = int - info.start + info.offset;
            str = '/0x' + delta.toString(16);
          } else {
            str = getSimpleTarget(info.target);
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
    var t = (int & 0x20) == 0 ? '' : 'T';
    return n + z + c + v + t;
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

function getSimpleTarget(target) {
  return target.substring(Math.max(target.lastIndexOf('/'), target.lastIndexOf('@')) + 1);
}

var instance = null;

function newInstance(kernel) {
  instance = new Debugger(kernel);
}

function getInstance() {
  return instance;
}

function oldInstance() {
  instance.finish();
  instance = null;
}

function getToken(obj, key) {
  var token = obj.get('token');
  if (!token || typeof token != 'object') {
    token = {};
  }
  var val = token[key];
  if (typeof val != 'string') {
    val = '';
  }
  return val;
}

function setToken(obj, key, val) {
  var token = obj.get('token');
  if (!token || typeof token != 'object') {
    token = {};
  }
  token[key] = val;
  obj.set('token', token);
}

function delToken(obj, key) {
  var token = obj.get('token');
  if (!token || typeof token != 'object') {
    token = {};
  }
  delete token[key];
  obj.set('token', token);
}

export default {
  newInstance: newInstance,
  getInstance: getInstance,
  oldInstance: oldInstance,
  getToken: getToken,
  setToken: setToken,
  delToken: delToken
};
