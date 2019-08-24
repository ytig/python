function registerEvent(type, object) {
  //todo
  switch (type) {
    case 'stack':
      setTimeout(() => {
        var bytes = [];
        for (var i = 0; i < 10 * 256; i++) {
          bytes[bytes.length] = Math.floor(256 * Math.random())
        }
        object.cache = bytes;
        object.onBreak(1, bytes);
      }, 1000);
      setTimeout(() => {
        var bytes = [];
        for (var i = 0; i < 10 * 256; i++) {
          if (Math.random() > 0.98) {
            bytes[bytes.length] = Math.floor(256 * Math.random())
          } else {
            bytes[bytes.length] = object.cache[bytes.length];
          }
        }
        object.onBreak(1, bytes);
      }, 2000);
      break;
    case 'memory':
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
