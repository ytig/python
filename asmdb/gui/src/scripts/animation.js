var Animation = function (speed, display, initial) {
  if (!initial) initial = 0;
  var self = this;
  self.value = initial;
  self.target = initial;
  if (typeof speed == "number") self.speed = function () {
    return speed;
  };
  else if (typeof speed == "function") self.speed = speed;
  else self.speed = function () {
    return 0;
  };
  if (typeof display == "function") self.display = display;
  else self.display = function () {};
  var time, loop;
  self.post = function () {
    if (time == undefined) {
      time = new Date().getTime();
      if (requestAnimationFrame) requestAnimationFrame(loop);
      else setTimeout(loop);
    }
  };
  loop = function () {
    if (time != undefined) {
      if (self.value == self.target) time = undefined;
      else {
        var delta = new Date().getTime() - time;
        time += delta;
        while (delta-- > 0) {
          if (self.value < self.target) self.value = Math.min(self.value + self.speed(self.value, self.target), self.target);
          else self.value = Math.max(self.value - self.speed(self.value, self.target), self.target);
          if (self.value == self.target) break;
        }
        self.display(self.value, self.target);
        if (requestAnimationFrame) requestAnimationFrame(loop);
        else setTimeout(loop, 16.7);
      }
    }
  }
};
Animation.prototype.$ = function () {
  this.display(this.value, this.target);
}
Animation.prototype.$value = function (val) {
  if (val == undefined) return this.value;
  else {
    this.value = val;
    this.target = val;
    this.display(this.value, this.target);
  }
};
Animation.prototype.$target = function (val) {
  if (val == undefined) return this.target;
  else {
    this.target = val;
    if (this.value != this.target) this.post();
  }
};

var Bessel = function (x1, y1, x2, y2) {
  this.ax = 1 - 3 * x1 - 3 * x2;
  this.bx = 3 * x2;
  this.cx = 3 * x1;
  this.ay = 1 - 3 * y1 - 3 * y2;
  this.by = 3 * y2;
  this.cy = 3 * y1;
};
Bessel.prototype.speed = function (value) {
  var ts = this.tartaglia(this.ay, this.by, this.cy, -value);
  for (var i in ts) {
    var t = ts[i];
    if (t < 0 || t > 1) continue;
    return (this.ay * 3 * t * t + this.by * 2 * t + this.cy) / (this.ax * 3 * t * t + this.bx * 2 * t + this.cx);
  }
  return NaN;
}
Bessel.prototype.egypt = function (a, b) {
  if (!a) return [];
  return [-b / a];
}
Bessel.prototype.babylon = function (a, b, c) {
  if (!a) return Bessel.prototype.egypt(b, c);
  var val1 = b * b - 4 * a * c;
  var x1 = 0;
  var x2 = 0;
  if (val1 >= 0) {
    x1 = (-1 * b + Math.sqrt(val1)) / (2 * a);
    x2 = (-1 * b - Math.sqrt(val1)) / (2 * a);
    return [x1, x2];
  }
  return [];
}
Bessel.prototype.tartaglia = function (a, b, c, d) {
  if (!a) return Bessel.prototype.babylon(b, c, d);
  b /= a;
  c /= a;
  d /= a;
  var disc, q, r, dum1, s, t, term1, r13;
  q = (3.0 * c - (b * b)) / 9.0;
  r = -(27.0 * d) + b * (9.0 * c - 2.0 * (b * b));
  r /= 54.0;
  disc = q * q * q + r * r;
  term1 = (b / 3.0);
  if (disc > 0) {
    s = r + Math.sqrt(disc);
    s = ((s < 0) ? -Math.pow(-s, (1.0 / 3.0)) : Math.pow(s, (1.0 / 3.0)));
    t = r - Math.sqrt(disc);
    t = ((t < 0) ? -Math.pow(-t, (1.0 / 3.0)) : Math.pow(t, (1.0 / 3.0)));
    return [-term1 + s + t];
  }
  if (disc == 0) {
    r13 = ((r < 0) ? -Math.pow(-r, (1.0 / 3.0)) : Math.pow(r, (1.0 / 3.0)));
    return [-term1 + 2.0 * r13, -(r13 + term1)];
  }
  q = -q;
  dum1 = q * q * q;
  dum1 = Math.acos(r / Math.sqrt(dum1));
  r13 = 2.0 * Math.sqrt(q);
  return [-term1 + r13 * Math.cos(dum1 / 3.0), -term1 + r13 * Math.cos((dum1 + 2.0 * Math.PI) / 3.0), -term1 + r13 * Math.cos((dum1 + 4.0 * Math.PI) / 3.0)];
}
Animation.bessel = function (duration, x1, y1, x2, y2) {
  var bessel = new Bessel(x1, y1, x2, y2);
  var k = 10;
  return function (value, target) {
    var speed = bessel.speed((value < target || duration > 0) ? (1 - Math.abs(target - value)) : Math.abs(target - value));
    if (isNaN(speed)) speed = k;
    return Math.max(1 / k, Math.min(k, speed)) / Math.abs(duration);
  }
}
Animation.linear = function (duration) {
  return Animation.bessel(duration, 0, 0, 1, 1);
}
Animation.ease = function (duration) {
  return Animation.bessel(duration, 0.25, 0.1, 0.25, 1);
}
Animation.ease_in = function (duration) {
  return Animation.bessel(duration, 0.42, 0, 1, 1);
}
Animation.ease_out = function (duration) {
  return Animation.bessel(duration, 0, 0, 0.58, 1);
}
Animation.ease_in_out = function (duration) {
  return Animation.bessel(duration, 0.42, 0, 0.58, 1);
}

export default Animation;
