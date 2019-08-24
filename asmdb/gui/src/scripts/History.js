export default class History extends Array {
  has() {
    return this.length > 0;
  }

  set(value) {
    this.splice(this.length, 0, value);
  }

  get() {
    if (this.length > 0) {
      return this.splice(this.length - 1, 1)[0];
    }
  }

  del() {
    this.splice(0, this.length);
  }
}
