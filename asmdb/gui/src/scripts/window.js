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

var canvasToken = 0;
var canvasList = {};
window.getContext = function (token, top, height) {
  if (token in canvasList) {
    var canvasItem = canvasList[token];
    if (top >= canvasItem[2] + canvasItem[3] || top + height <= canvasItem[2]) {
      return null;
    }
    var s = devicePixelRatio;
    var y = top - canvasItem[2];
    canvasItem[1].setTransform(s, 0, 0, s, 0, s * y);
    return canvasItem[1];
  }
  return null;
}
window.setContext = function (canvas, top, height) {
  var token = ++canvasToken;
  for (var key in canvasList) {
    var val = canvasList[key];
    if (val[0] == canvas) {
      delete canvasList[key];
      break;
    }
  }
  var s = devicePixelRatio;
  if (canvas.width != s * canvas.clientWidth || canvas.height != s * canvas.clientHeight) {
    canvas.width = s * canvas.clientWidth;
    canvas.height = s * canvas.clientHeight;
  }
  var context = canvas.getContext('2d');
  canvasList[token] = [canvas, context, top, height];
  return token;
}
window.delContext = function (canvas) {
  for (var key in canvasList) {
    var val = canvasList[key];
    if (val[0] == canvas) {
      delete canvasList[key];
      break;
    }
  }
}

export default {};
