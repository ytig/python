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
    if (top >= canvasItem[1] + canvasItem[2] || top + height <= canvasItem[1]) {
      return null;
    }
    var context = canvasItem[0].getContext('2d');
    var t = context.getTransform();
    var y = top - canvasItem[1];
    context.setTransform(t.a, 0, 0, t.d, 0, t.d * y);
    return context;
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
  canvasList[token] = [canvas, top, height];
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
