String.prototype.zfill = function (size) {
  var str = this;
  while (str.length < size) {
    str = "0" + str;
  }
  return str;
}

export default {};
