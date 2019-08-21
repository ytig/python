function registerEvent(type, object) {
  //todo
  setTimeout(() => {
    object.onBreak(1, '');
  }, 3000);
}

function unregisterEvent(object) {
  //todo
}

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent
};
