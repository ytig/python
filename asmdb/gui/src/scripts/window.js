String.prototype.zfill = function (size) {
  var str = this;
  while (str.length < size) {
    str = '0' + str;
  }
  return str;
}

window.measureText = function (text, font) {
  var canvas = document.getElementById('__canvas__');
  if (!canvas) {
    canvas = document.createElement('canvas');
    canvas.id = '__canvas__';
    canvas.style.display = 'none';
    document.body.appendChild(canvas);
  }
  var context = canvas.getContext('2d');
  context.font = font;
  return context.measureText(text).width;
}

export default {};
