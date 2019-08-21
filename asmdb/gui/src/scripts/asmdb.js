function registerEvent(type, object) {
  //todo
  setTimeout(() => {
    object.onBreak(1, '00112233445566778899AABBCCDDEEFF');
  }, 1000);
  setTimeout(() => {
    object.onBreak(1, '00112233445566770099AABBCCDDEEFF');
  }, 8000);
}

function unregisterEvent(object) {
  //todo
}

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent
};
