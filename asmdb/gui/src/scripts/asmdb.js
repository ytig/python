function registerEvent(type, object) {
  //todo
  setTimeout(() => {
    object.onBreak(1, '');
  }, 1000);
}

function unregisterEvent(object) {
  //todo
}

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent
};
