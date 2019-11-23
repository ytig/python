class Sloth {
  constructor(delay) {
    this.bool_t = false;
    this.bool_f = false;
    this.delay = delay;
    this.counter = 0;
  }

  set(bool) {
    if (this.bool_t == bool) {
      return;
    }
    this.bool_t = bool;
    this.counter++;
    if (this.bool_t) {
      this.bool_f = true;
    } else {
      var counter = this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.bool_f = false;
      }, this.delay);
    }
  }
}

export default Sloth;
