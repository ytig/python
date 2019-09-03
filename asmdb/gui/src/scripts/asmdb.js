function for_test(bytes) {
  var str = '';
  for (var b in bytes) {
    str += String.fromCharCode(bytes[b]);
  }
  return str;
}

function registerEvent(type, object) {
  //todo
  switch (type) {
    case 'stack':
      setTimeout(() => {
        var bytes = [];
        for (var i = 0; i < 10 * 256; i++) {
          bytes[bytes.length] = Math.floor(256 * Math.random());
        }
        object.cache = bytes;
        object.onBreak(1, for_test(bytes));
      }, 1000);
      setTimeout(() => {
        var bytes = [];
        for (var i = 0; i < 10 * 256; i++) {
          if (Math.random() > 0.98) {
            bytes[bytes.length] = Math.floor(256 * Math.random());
          } else {
            bytes[bytes.length] = object.cache[bytes.length];
          }
        }
        object.onBreak(1, for_test(bytes));
      }, 2000);
      break;
    case 'memory':
      setTimeout(() => {
        var bytes = [];
        for (var i = 0; i < 4 * 512; i++) {
          bytes[bytes.length] = Math.floor(256 * Math.random());
        }
        object.cache = bytes;
        object.onBreak(2048, for_test(bytes));
      }, 1000);
      setTimeout(() => {
        var bytes = [];
        for (var i = 0; i < 4 * 512; i++) {
          if (Math.random() > 0.98) {
            bytes[bytes.length] = Math.floor(256 * Math.random());
          } else {
            bytes[bytes.length] = object.cache[bytes.length];
          }
        }
        object.onBreak(2048, for_test(bytes));
      }, 2000);
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
