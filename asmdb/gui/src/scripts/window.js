String.prototype.zfill = function (size) {
  var str = this;
  while (str.length < size) {
    str = '0' + str;
  }
  return str;
}

window.binarySearch = function (items, comparator) {
  var low = 0;
  var high = items.length - 1;
  while (low <= high) {
    var mid = (low + high) >>> 1;
    var delta = comparator(items[mid]);
    if (delta == 0) {
      return mid;
    }
    if (delta > 0) {
      low = mid + 1;
    } else {
      high = mid - 1;
    }
  }
  return -(low + 1);
}

window.parseSignedInt = function (float) {
  if (float >= 0) {
    return parseInt(float);
  } else {
    var floor = Math.floor(float);
    return parseInt(float - floor) + floor;
  }
}

window.requestAnimationFrames = function (callback) {
  var i = 0;
  var _callback = function () {
    if (!callback(i++)) {
      requestAnimationFrame(_callback);
    }
  }
  requestAnimationFrame(_callback);
}

window.isChildOrMe = function (parent, child) {
  while (child) {
    if (parent == child) {
      return true;
    }
    child = child.parentNode;
  }
  return false;
}

window.getBackgroundColor = function (el) {
  var defaultBackgroundColor = 'rgba(0, 0, 0, 0)';
  while (el && el != document) {
    var style = getComputedStyle(el);
    if (style.backgroundColor != defaultBackgroundColor) {
      return style.backgroundColor;
    }
    el = el.parentNode;
  }
  return defaultBackgroundColor;
}

window.emptySelection = function () {
  var selection = getSelection();
  if (selection.type == 'Range') {
    selection.empty();
  }
}

window.copyText = function (text) {
  var textarea = document.getElementById('__textarea__');
  if (!textarea) {
    textarea = document.createElement('textarea');
    textarea.id = '__textarea__';
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    textarea.style.pointerEvents = 'none';
    document.body.appendChild(textarea);
  }
  textarea.value = text;
  textarea.select();
  document.execCommand('copy');
}

window.measureText = function (text, font) {
  if (!text || text.length <= 0) {
    return 0;
  }
  font = font || '12px Menlo';
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

window.measureLength = function (length, font) {
  var width;
  if (!font || font == '12px Menlo') {
    width = 7.224609375;
  } else {
    width = window.measureText(' ', font);
  }
  return Math.max(length, 0) * width;
}

window.resetContext = function (canvas) {
  var context = canvas.getContext('2d');
  context.resetTransform();
  context.clearRect(0, 0, canvas.width, canvas.height);
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
    canvasItem[1].clearRect(0, 0, canvasItem[0].width / s, height);
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

window.saveStorage = function (key, value) {
  localStorage[key] = JSON.stringify(value);
}
window.loadStorage = function (key, defaultValue) {
  if (key in localStorage) {
    try {
      var value = JSON.parse(localStorage[key]);
      if (defaultValue == undefined || typeof value == typeof defaultValue) {
        return value;
      }
    } catch (error) {}
  }
  return defaultValue;
}

window.addEventListener('dragstart', function (event) {
  event.preventDefault();
});

window.playSound = function (src) {
  var audio = document.getElementById('__audio__');
  if (!audio) {
    audio = document.createElement('audio');
    audio.id = '__audio__';
    document.body.appendChild(audio);
  }
  audio.src = src;
  audio.play();
}

export default {};
