function registerEvent(type, object) {
  //todo
  console.log('todo')
  setInterval(() => {
    object.onBreak(1, '');
  }, 2000);
}

function unregisterEvent(object) {
  //todo
}

export default {
  registerEvent: registerEvent,
  unregisterEvent: unregisterEvent
};
