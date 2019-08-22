function registerEvent(type, object) {
  //todo
  setTimeout(() => {
    var hex = "";
    for (var i = 0; i < 10 * 2 * 344; i++) {
      hex += "0123456789abcdef".charAt(Math.floor(16 * Math.random()));
    }
    object.cache = hex;
    object.onBreak(1, hex);
  }, 1000);
  setTimeout(() => {
    var hex = "";
    for (var i = 0; i < 10 * 2 * 344; i++) {
      if (Math.random() > 0.98) {
        hex += "0123456789abcdef".charAt(Math.floor(16 * Math.random()));
      } else {
        hex += object.cache.slice(i, i + 1);
      }
    }
    object.onBreak(1, hex);
  }, 2000);
}

function unregisterEvent(type, object) {
  //todo
}

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent
};
