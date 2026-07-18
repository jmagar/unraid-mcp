/**
* @vue/shared v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
// @__NO_SIDE_EFFECTS__
function or(e) {
  const t = /* @__PURE__ */ Object.create(null);
  for (const s of e.split(",")) t[s] = 1;
  return (s) => s in t;
}
const ke = {}, Ss = [], Rt = () => {
}, Ll = () => !1, ro = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && // uppercase letter
(e.charCodeAt(2) > 122 || e.charCodeAt(2) < 97), lo = (e) => e.startsWith("onUpdate:"), Le = Object.assign, rr = (e, t) => {
  const s = e.indexOf(t);
  s > -1 && e.splice(s, 1);
}, qa = Object.prototype.hasOwnProperty, ge = (e, t) => qa.call(e, t), G = Array.isArray, Cs = (e) => kn(e) === "[object Map]", Vs = (e) => kn(e) === "[object Set]", Gr = (e) => kn(e) === "[object Date]", X = (e) => typeof e == "function", Ve = (e) => typeof e == "string", pt = (e) => typeof e == "symbol", ye = (e) => e !== null && typeof e == "object", Ul = (e) => (ye(e) || X(e)) && X(e.then) && X(e.catch), Dl = Object.prototype.toString, kn = (e) => Dl.call(e), Ga = (e) => kn(e).slice(8, -1), io = (e) => kn(e) === "[object Object]", ao = (e) => Ve(e) && e !== "NaN" && e[0] !== "-" && "" + parseInt(e, 10) === e, dn = /* @__PURE__ */ or(
  // the leading comma is intentional so empty string "" is also included
  ",key,ref,ref_for,ref_key,onVnodeBeforeMount,onVnodeMounted,onVnodeBeforeUpdate,onVnodeUpdated,onVnodeBeforeUnmount,onVnodeUnmounted"
), uo = (e) => {
  const t = /* @__PURE__ */ Object.create(null);
  return ((s) => t[s] || (t[s] = e(s)));
}, Ja = /-\w/g, et = uo(
  (e) => e.replace(Ja, (t) => t.slice(1).toUpperCase())
), Ya = /\B([A-Z])/g, dt = uo(
  (e) => e.replace(Ya, "-$1").toLowerCase()
), Bl = uo((e) => e.charAt(0).toUpperCase() + e.slice(1)), Kn = uo(
  (e) => e ? `on${Bl(e)}` : ""
), Pt = (e, t) => !Object.is(e, t), qn = (e, ...t) => {
  for (let s = 0; s < e.length; s++)
    e[s](...t);
}, Fl = (e, t, s, n = !1) => {
  Object.defineProperty(e, t, {
    configurable: !0,
    enumerable: !1,
    writable: n,
    value: s
  });
}, co = (e) => {
  const t = parseFloat(e);
  return isNaN(t) ? e : t;
}, Jr = (e) => {
  const t = Ve(e) ? Number(e) : NaN;
  return isNaN(t) ? e : t;
};
let Yr;
const fo = () => Yr || (Yr = typeof globalThis < "u" ? globalThis : typeof self < "u" ? self : typeof window < "u" ? window : typeof global < "u" ? global : {});
function bn(e) {
  if (G(e)) {
    const t = {};
    for (let s = 0; s < e.length; s++) {
      const n = e[s], o = Ve(n) ? eu(n) : bn(n);
      if (o)
        for (const l in o)
          t[l] = o[l];
    }
    return t;
  } else if (Ve(e) || ye(e))
    return e;
}
const Qa = /;(?![^(]*\))/g, Za = /:([^]+)/, Xa = /\/\*[^]*?\*\//g;
function eu(e) {
  const t = {};
  return e.replace(Xa, "").split(Qa).forEach((s) => {
    if (s) {
      const n = s.split(Za);
      n.length > 1 && (t[n[0].trim()] = n[1].trim());
    }
  }), t;
}
function ot(e) {
  let t = "";
  if (Ve(e))
    t = e;
  else if (G(e))
    for (let s = 0; s < e.length; s++) {
      const n = ot(e[s]);
      n && (t += n + " ");
    }
  else if (ye(e))
    for (const s in e)
      e[s] && (t += s + " ");
  return t.trim();
}
const tu = "itemscope,allowfullscreen,formnovalidate,ismap,nomodule,novalidate,readonly", su = /* @__PURE__ */ or(tu);
function Hl(e) {
  return !!e || e === "";
}
function nu(e, t) {
  if (e.length !== t.length) return !1;
  let s = !0;
  for (let n = 0; s && n < e.length; n++)
    s = Xt(e[n], t[n]);
  return s;
}
function Xt(e, t) {
  if (e === t) return !0;
  let s = Gr(e), n = Gr(t);
  if (s || n)
    return s && n ? e.getTime() === t.getTime() : !1;
  if (s = pt(e), n = pt(t), s || n)
    return e === t;
  if (s = G(e), n = G(t), s || n)
    return s && n ? nu(e, t) : !1;
  if (s = ye(e), n = ye(t), s || n) {
    if (!s || !n)
      return !1;
    const o = Object.keys(e).length, l = Object.keys(t).length;
    if (o !== l)
      return !1;
    for (const i in e) {
      const a = e.hasOwnProperty(i), d = t.hasOwnProperty(i);
      if (a && !d || !a && d || !Xt(e[i], t[i]))
        return !1;
    }
  }
  return String(e) === String(t);
}
function lr(e, t) {
  return e.findIndex((s) => Xt(s, t));
}
const zl = (e) => !!(e && e.__v_isRef === !0), V = (e) => Ve(e) ? e : e == null ? "" : G(e) || ye(e) && (e.toString === Dl || !X(e.toString)) ? zl(e) ? V(e.value) : JSON.stringify(e, Wl, 2) : String(e), Wl = (e, t) => zl(t) ? Wl(e, t.value) : Cs(t) ? {
  [`Map(${t.size})`]: [...t.entries()].reduce(
    (s, [n, o], l) => (s[Vo(n, l) + " =>"] = o, s),
    {}
  )
} : Vs(t) ? {
  [`Set(${t.size})`]: [...t.values()].map((s) => Vo(s))
} : pt(t) ? Vo(t) : ye(t) && !G(t) && !io(t) ? String(t) : t, Vo = (e, t = "") => {
  var s;
  return (
    // Symbol.description in es2019+ so we need to cast here to pass
    // the lib: es2016 check
    pt(e) ? `Symbol(${(s = e.description) != null ? s : t})` : e
  );
};
/**
* @vue/reactivity v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
let Ke;
class ou {
  // TODO isolatedDeclarations "__v_skip"
  constructor(t = !1) {
    this.detached = t, this._active = !0, this._on = 0, this.effects = [], this.cleanups = [], this._isPaused = !1, this._warnOnRun = !0, this.__v_skip = !0, !t && Ke && (Ke.active ? (this.parent = Ke, this.index = (Ke.scopes || (Ke.scopes = [])).push(
      this
    ) - 1) : (this._active = !1, this._warnOnRun = !1));
  }
  get active() {
    return this._active;
  }
  pause() {
    if (this._active) {
      this._isPaused = !0;
      let t, s;
      if (this.scopes)
        for (t = 0, s = this.scopes.length; t < s; t++)
          this.scopes[t].pause();
      for (t = 0, s = this.effects.length; t < s; t++)
        this.effects[t].pause();
    }
  }
  /**
   * Resumes the effect scope, including all child scopes and effects.
   */
  resume() {
    if (this._active && this._isPaused) {
      this._isPaused = !1;
      let t, s;
      if (this.scopes)
        for (t = 0, s = this.scopes.length; t < s; t++)
          this.scopes[t].resume();
      for (t = 0, s = this.effects.length; t < s; t++)
        this.effects[t].resume();
    }
  }
  run(t) {
    if (this._active) {
      const s = Ke;
      try {
        return Ke = this, t();
      } finally {
        Ke = s;
      }
    }
  }
  /**
   * This should only be called on non-detached scopes
   * @internal
   */
  on() {
    ++this._on === 1 && (this.prevScope = Ke, Ke = this);
  }
  /**
   * This should only be called on non-detached scopes
   * @internal
   */
  off() {
    if (this._on > 0 && --this._on === 0) {
      if (Ke === this)
        Ke = this.prevScope;
      else {
        let t = Ke;
        for (; t; ) {
          if (t.prevScope === this) {
            t.prevScope = this.prevScope;
            break;
          }
          t = t.prevScope;
        }
      }
      this.prevScope = void 0;
    }
  }
  stop(t) {
    if (this._active) {
      this._active = !1;
      let s, n;
      for (s = 0, n = this.effects.length; s < n; s++)
        this.effects[s].stop();
      for (this.effects.length = 0, s = 0, n = this.cleanups.length; s < n; s++)
        this.cleanups[s]();
      if (this.cleanups.length = 0, this.scopes) {
        for (s = 0, n = this.scopes.length; s < n; s++)
          this.scopes[s].stop(!0);
        this.scopes.length = 0;
      }
      if (!this.detached && this.parent && !t) {
        const o = this.parent.scopes.pop();
        o && o !== this && (this.parent.scopes[this.index] = o, o.index = this.index);
      }
      this.parent = void 0;
    }
  }
}
function ru() {
  return Ke;
}
let Ce;
const $o = /* @__PURE__ */ new WeakSet();
class Kl {
  constructor(t) {
    this.fn = t, this.deps = void 0, this.depsTail = void 0, this.flags = 5, this.next = void 0, this.cleanup = void 0, this.scheduler = void 0, Ke && (Ke.active ? Ke.effects.push(this) : this.flags &= -2);
  }
  pause() {
    this.flags |= 64;
  }
  resume() {
    this.flags & 64 && (this.flags &= -65, $o.has(this) && ($o.delete(this), this.trigger()));
  }
  /**
   * @internal
   */
  notify() {
    this.flags & 2 && !(this.flags & 32) || this.flags & 8 || Gl(this);
  }
  run() {
    if (!(this.flags & 1))
      return this.fn();
    this.flags |= 2, Qr(this), Jl(this);
    const t = Ce, s = vt;
    Ce = this, vt = !0;
    try {
      return this.fn();
    } finally {
      Yl(this), Ce = t, vt = s, this.flags &= -3;
    }
  }
  stop() {
    if (this.flags & 1) {
      for (let t = this.deps; t; t = t.nextDep)
        ur(t);
      this.deps = this.depsTail = void 0, Qr(this), this.onStop && this.onStop(), this.flags &= -2;
    }
  }
  trigger() {
    this.flags & 64 ? $o.add(this) : this.scheduler ? this.scheduler() : this.runIfDirty();
  }
  /**
   * @internal
   */
  runIfDirty() {
    Ko(this) && this.run();
  }
  get dirty() {
    return Ko(this);
  }
}
let ql = 0, cn, fn;
function Gl(e, t = !1) {
  if (e.flags |= 8, t) {
    e.next = fn, fn = e;
    return;
  }
  e.next = cn, cn = e;
}
function ir() {
  ql++;
}
function ar() {
  if (--ql > 0)
    return;
  if (fn) {
    let t = fn;
    for (fn = void 0; t; ) {
      const s = t.next;
      t.next = void 0, t.flags &= -9, t = s;
    }
  }
  let e;
  for (; cn; ) {
    let t = cn;
    for (cn = void 0; t; ) {
      const s = t.next;
      if (t.next = void 0, t.flags &= -9, t.flags & 1)
        try {
          t.trigger();
        } catch (n) {
          e || (e = n);
        }
      t = s;
    }
  }
  if (e) throw e;
}
function Jl(e) {
  for (let t = e.deps; t; t = t.nextDep)
    t.version = -1, t.prevActiveLink = t.dep.activeLink, t.dep.activeLink = t;
}
function Yl(e) {
  let t, s = e.depsTail, n = s;
  for (; n; ) {
    const o = n.prevDep;
    n.version === -1 ? (n === s && (s = o), ur(n), lu(n)) : t = n, n.dep.activeLink = n.prevActiveLink, n.prevActiveLink = void 0, n = o;
  }
  e.deps = t, e.depsTail = s;
}
function Ko(e) {
  for (let t = e.deps; t; t = t.nextDep)
    if (t.dep.version !== t.version || t.dep.computed && (Ql(t.dep.computed) || t.dep.version !== t.version))
      return !0;
  return !!e._dirty;
}
function Ql(e) {
  if (e.flags & 4 && !(e.flags & 16) || (e.flags &= -17, e.globalVersion === vn) || (e.globalVersion = vn, !e.isSSR && e.flags & 128 && (!e.deps && !e._dirty || !Ko(e))))
    return;
  e.flags |= 2;
  const t = e.dep, s = Ce, n = vt;
  Ce = e, vt = !0;
  try {
    Jl(e);
    const o = e.fn(e._value);
    (t.version === 0 || Pt(o, e._value)) && (e.flags |= 128, e._value = o, t.version++);
  } catch (o) {
    throw t.version++, o;
  } finally {
    Ce = s, vt = n, Yl(e), e.flags &= -3;
  }
}
function ur(e, t = !1) {
  const { dep: s, prevSub: n, nextSub: o } = e;
  if (n && (n.nextSub = o, e.prevSub = void 0), o && (o.prevSub = n, e.nextSub = void 0), s.subs === e && (s.subs = n, !n && s.computed)) {
    s.computed.flags &= -5;
    for (let l = s.computed.deps; l; l = l.nextDep)
      ur(l, !0);
  }
  !t && !--s.sc && s.map && s.map.delete(s.key);
}
function lu(e) {
  const { prevDep: t, nextDep: s } = e;
  t && (t.nextDep = s, e.prevDep = void 0), s && (s.prevDep = t, e.nextDep = void 0);
}
let vt = !0;
const Zl = [];
function Mt() {
  Zl.push(vt), vt = !1;
}
function Vt() {
  const e = Zl.pop();
  vt = e === void 0 ? !0 : e;
}
function Qr(e) {
  const { cleanup: t } = e;
  if (e.cleanup = void 0, t) {
    const s = Ce;
    Ce = void 0;
    try {
      t();
    } finally {
      Ce = s;
    }
  }
}
let vn = 0;
class iu {
  constructor(t, s) {
    this.sub = t, this.dep = s, this.version = s.version, this.nextDep = this.prevDep = this.nextSub = this.prevSub = this.prevActiveLink = void 0;
  }
}
class dr {
  // TODO isolatedDeclarations "__v_skip"
  constructor(t) {
    this.computed = t, this.version = 0, this.activeLink = void 0, this.subs = void 0, this.map = void 0, this.key = void 0, this.sc = 0, this.__v_skip = !0;
  }
  track(t) {
    if (!Ce || !vt || Ce === this.computed)
      return;
    let s = this.activeLink;
    if (s === void 0 || s.sub !== Ce)
      s = this.activeLink = new iu(Ce, this), Ce.deps ? (s.prevDep = Ce.depsTail, Ce.depsTail.nextDep = s, Ce.depsTail = s) : Ce.deps = Ce.depsTail = s, Xl(s);
    else if (s.version === -1 && (s.version = this.version, s.nextDep)) {
      const n = s.nextDep;
      n.prevDep = s.prevDep, s.prevDep && (s.prevDep.nextDep = n), s.prevDep = Ce.depsTail, s.nextDep = void 0, Ce.depsTail.nextDep = s, Ce.depsTail = s, Ce.deps === s && (Ce.deps = n);
    }
    return s;
  }
  trigger(t) {
    this.version++, vn++, this.notify(t);
  }
  notify(t) {
    ir();
    try {
      for (let s = this.subs; s; s = s.prevSub)
        s.sub.notify() && s.sub.dep.notify();
    } finally {
      ar();
    }
  }
}
function Xl(e) {
  if (e.dep.sc++, e.sub.flags & 4) {
    const t = e.dep.computed;
    if (t && !e.dep.subs) {
      t.flags |= 20;
      for (let n = t.deps; n; n = n.nextDep)
        Xl(n);
    }
    const s = e.dep.subs;
    s !== e && (e.prevSub = s, s && (s.nextSub = e)), e.dep.subs = e;
  }
}
const Yn = /* @__PURE__ */ new WeakMap(), ds = /* @__PURE__ */ Symbol(
  ""
), qo = /* @__PURE__ */ Symbol(
  ""
), yn = /* @__PURE__ */ Symbol(
  ""
);
function Qe(e, t, s) {
  if (vt && Ce) {
    let n = Yn.get(e);
    n || Yn.set(e, n = /* @__PURE__ */ new Map());
    let o = n.get(s);
    o || (n.set(s, o = new dr()), o.map = n, o.key = s), o.track();
  }
}
function Bt(e, t, s, n, o, l) {
  const i = Yn.get(e);
  if (!i) {
    vn++;
    return;
  }
  const a = (d) => {
    d && d.trigger();
  };
  if (ir(), t === "clear")
    i.forEach(a);
  else {
    const d = G(e), m = d && ao(s);
    if (d && s === "length") {
      const g = Number(n);
      i.forEach((x, C) => {
        (C === "length" || C === yn || !pt(C) && C >= g) && a(x);
      });
    } else
      switch ((s !== void 0 || i.has(void 0)) && a(i.get(s)), m && a(i.get(yn)), t) {
        case "add":
          d ? m && a(i.get("length")) : (a(i.get(ds)), Cs(e) && a(i.get(qo)));
          break;
        case "delete":
          d || (a(i.get(ds)), Cs(e) && a(i.get(qo)));
          break;
        case "set":
          Cs(e) && a(i.get(ds));
          break;
      }
  }
  ar();
}
function au(e, t) {
  const s = Yn.get(e);
  return s && s.get(t);
}
function _s(e) {
  const t = /* @__PURE__ */ me(e);
  return t === e ? t : (Qe(t, "iterate", yn), /* @__PURE__ */ ft(e) ? t : t.map(yt));
}
function po(e) {
  return Qe(e = /* @__PURE__ */ me(e), "iterate", yn), e;
}
function It(e, t) {
  return /* @__PURE__ */ Wt(e) ? Ps(/* @__PURE__ */ cs(e) ? yt(t) : t) : yt(t);
}
const uu = {
  __proto__: null,
  [Symbol.iterator]() {
    return Oo(this, Symbol.iterator, (e) => It(this, e));
  },
  concat(...e) {
    return _s(this).concat(
      ...e.map((t) => G(t) ? _s(t) : t)
    );
  },
  entries() {
    return Oo(this, "entries", (e) => (e[1] = It(this, e[1]), e));
  },
  every(e, t) {
    return jt(this, "every", e, t, void 0, arguments);
  },
  filter(e, t) {
    return jt(
      this,
      "filter",
      e,
      t,
      (s) => s.map((n) => It(this, n)),
      arguments
    );
  },
  find(e, t) {
    return jt(
      this,
      "find",
      e,
      t,
      (s) => It(this, s),
      arguments
    );
  },
  findIndex(e, t) {
    return jt(this, "findIndex", e, t, void 0, arguments);
  },
  findLast(e, t) {
    return jt(
      this,
      "findLast",
      e,
      t,
      (s) => It(this, s),
      arguments
    );
  },
  findLastIndex(e, t) {
    return jt(this, "findLastIndex", e, t, void 0, arguments);
  },
  // flat, flatMap could benefit from ARRAY_ITERATE but are not straight-forward to implement
  forEach(e, t) {
    return jt(this, "forEach", e, t, void 0, arguments);
  },
  includes(...e) {
    return jo(this, "includes", e);
  },
  indexOf(...e) {
    return jo(this, "indexOf", e);
  },
  join(e) {
    return _s(this).join(e);
  },
  // keys() iterator only reads `length`, no optimization required
  lastIndexOf(...e) {
    return jo(this, "lastIndexOf", e);
  },
  map(e, t) {
    return jt(this, "map", e, t, void 0, arguments);
  },
  pop() {
    return en(this, "pop");
  },
  push(...e) {
    return en(this, "push", e);
  },
  reduce(e, ...t) {
    return Zr(this, "reduce", e, t);
  },
  reduceRight(e, ...t) {
    return Zr(this, "reduceRight", e, t);
  },
  shift() {
    return en(this, "shift");
  },
  // slice could use ARRAY_ITERATE but also seems to beg for range tracking
  some(e, t) {
    return jt(this, "some", e, t, void 0, arguments);
  },
  splice(...e) {
    return en(this, "splice", e);
  },
  toReversed() {
    return _s(this).toReversed();
  },
  toSorted(e) {
    return _s(this).toSorted(e);
  },
  toSpliced(...e) {
    return _s(this).toSpliced(...e);
  },
  unshift(...e) {
    return en(this, "unshift", e);
  },
  values() {
    return Oo(this, "values", (e) => It(this, e));
  }
};
function Oo(e, t, s) {
  const n = po(e), o = n[t]();
  return n !== e && !/* @__PURE__ */ ft(e) && (o._next = o.next, o.next = () => {
    const l = o._next();
    return l.done || (l.value = s(l.value)), l;
  }), o;
}
const du = Array.prototype;
function jt(e, t, s, n, o, l) {
  const i = po(e), a = i !== e && !/* @__PURE__ */ ft(e), d = i[t];
  if (d !== du[t]) {
    const x = d.apply(e, l);
    return a ? yt(x) : x;
  }
  let m = s;
  i !== e && (a ? m = function(x, C) {
    return s.call(this, It(e, x), C, e);
  } : s.length > 2 && (m = function(x, C) {
    return s.call(this, x, C, e);
  }));
  const g = d.call(i, m, n);
  return a && o ? o(g) : g;
}
function Zr(e, t, s, n) {
  const o = po(e), l = o !== e && !/* @__PURE__ */ ft(e);
  let i = s, a = !1;
  o !== e && (l ? (a = n.length === 0, i = function(m, g, x) {
    return a && (a = !1, m = It(e, m)), s.call(this, m, It(e, g), x, e);
  }) : s.length > 3 && (i = function(m, g, x) {
    return s.call(this, m, g, x, e);
  }));
  const d = o[t](i, ...n);
  return a ? It(e, d) : d;
}
function jo(e, t, s) {
  const n = /* @__PURE__ */ me(e);
  Qe(n, "iterate", yn);
  const o = n[t](...s);
  return (o === -1 || o === !1) && /* @__PURE__ */ mo(s[0]) ? (s[0] = /* @__PURE__ */ me(s[0]), n[t](...s)) : o;
}
function en(e, t, s = []) {
  Mt(), ir();
  const n = (/* @__PURE__ */ me(e))[t].apply(e, s);
  return ar(), Vt(), n;
}
const cu = /* @__PURE__ */ or("__proto__,__v_isRef,__isVue"), ei = new Set(
  /* @__PURE__ */ Object.getOwnPropertyNames(Symbol).filter((e) => e !== "arguments" && e !== "caller").map((e) => Symbol[e]).filter(pt)
);
function fu(e) {
  pt(e) || (e = String(e));
  const t = /* @__PURE__ */ me(this);
  return Qe(t, "has", e), t.hasOwnProperty(e);
}
class ti {
  constructor(t = !1, s = !1) {
    this._isReadonly = t, this._isShallow = s;
  }
  get(t, s, n) {
    if (s === "__v_skip") return t.__v_skip;
    const o = this._isReadonly, l = this._isShallow;
    if (s === "__v_isReactive")
      return !o;
    if (s === "__v_isReadonly")
      return o;
    if (s === "__v_isShallow")
      return l;
    if (s === "__v_raw")
      return n === (o ? l ? wu : ri : l ? oi : ni).get(t) || // receiver is not the reactive proxy, but has the same prototype
      // this means the receiver is a user proxy of the reactive proxy
      Object.getPrototypeOf(t) === Object.getPrototypeOf(n) ? t : void 0;
    const i = G(t);
    if (!o) {
      let d;
      if (i && (d = uu[s]))
        return d;
      if (s === "hasOwnProperty")
        return fu;
    }
    const a = Reflect.get(
      t,
      s,
      // if this is a proxy wrapping a ref, return methods using the raw ref
      // as receiver so that we don't have to call `toRaw` on the ref in all
      // its class methods
      /* @__PURE__ */ Ue(t) ? t : n
    );
    if ((pt(s) ? ei.has(s) : cu(s)) || (o || Qe(t, "get", s), l))
      return a;
    if (/* @__PURE__ */ Ue(a)) {
      const d = i && ao(s) ? a : a.value;
      return o && ye(d) ? /* @__PURE__ */ Jo(d) : d;
    }
    return ye(a) ? o ? /* @__PURE__ */ Jo(a) : /* @__PURE__ */ zt(a) : a;
  }
}
class si extends ti {
  constructor(t = !1) {
    super(!1, t);
  }
  set(t, s, n, o) {
    let l = t[s];
    const i = G(t) && ao(s);
    if (!this._isShallow) {
      const m = /* @__PURE__ */ Wt(l);
      if (!/* @__PURE__ */ ft(n) && !/* @__PURE__ */ Wt(n) && (l = /* @__PURE__ */ me(l), n = /* @__PURE__ */ me(n)), !i && /* @__PURE__ */ Ue(l) && !/* @__PURE__ */ Ue(n))
        return m || (l.value = n), !0;
    }
    const a = i ? Number(s) < t.length : ge(t, s), d = Reflect.set(
      t,
      s,
      n,
      /* @__PURE__ */ Ue(t) ? t : o
    );
    return t === /* @__PURE__ */ me(o) && d && (a ? Pt(n, l) && Bt(t, "set", s, n) : Bt(t, "add", s, n)), d;
  }
  deleteProperty(t, s) {
    const n = ge(t, s);
    t[s];
    const o = Reflect.deleteProperty(t, s);
    return o && n && Bt(t, "delete", s, void 0), o;
  }
  has(t, s) {
    const n = Reflect.has(t, s);
    return (!pt(s) || !ei.has(s)) && Qe(t, "has", s), n;
  }
  ownKeys(t) {
    return Qe(
      t,
      "iterate",
      G(t) ? "length" : ds
    ), Reflect.ownKeys(t);
  }
}
class pu extends ti {
  constructor(t = !1) {
    super(!0, t);
  }
  set(t, s) {
    return !0;
  }
  deleteProperty(t, s) {
    return !0;
  }
}
const mu = /* @__PURE__ */ new si(), gu = /* @__PURE__ */ new pu(), hu = /* @__PURE__ */ new si(!0);
const Go = (e) => e, Dn = (e) => Reflect.getPrototypeOf(e);
function bu(e, t, s) {
  return function(...n) {
    const o = this.__v_raw, l = /* @__PURE__ */ me(o), i = Cs(l), a = e === "entries" || e === Symbol.iterator && i, d = e === "keys" && i, m = o[e](...n), g = s ? Go : t ? Ps : yt;
    return !t && Qe(
      l,
      "iterate",
      d ? qo : ds
    ), Le(
      // inheriting all iterator properties
      Object.create(m),
      {
        // iterator protocol
        next() {
          const { value: x, done: C } = m.next();
          return C ? { value: x, done: C } : {
            value: a ? [g(x[0]), g(x[1])] : g(x),
            done: C
          };
        }
      }
    );
  };
}
function Bn(e) {
  return function(...t) {
    return e === "delete" ? !1 : e === "clear" ? void 0 : this;
  };
}
function vu(e, t) {
  const s = {
    get(o) {
      const l = this.__v_raw, i = /* @__PURE__ */ me(l), a = /* @__PURE__ */ me(o);
      e || (Pt(o, a) && Qe(i, "get", o), Qe(i, "get", a));
      const { has: d } = Dn(i), m = t ? Go : e ? Ps : yt;
      if (d.call(i, o))
        return m(l.get(o));
      if (d.call(i, a))
        return m(l.get(a));
      l !== i && l.get(o);
    },
    get size() {
      const o = this.__v_raw;
      return !e && Qe(/* @__PURE__ */ me(o), "iterate", ds), o.size;
    },
    has(o) {
      const l = this.__v_raw, i = /* @__PURE__ */ me(l), a = /* @__PURE__ */ me(o);
      return e || (Pt(o, a) && Qe(i, "has", o), Qe(i, "has", a)), o === a ? l.has(o) : l.has(o) || l.has(a);
    },
    forEach(o, l) {
      const i = this, a = i.__v_raw, d = /* @__PURE__ */ me(a), m = t ? Go : e ? Ps : yt;
      return !e && Qe(d, "iterate", ds), a.forEach((g, x) => o.call(l, m(g), m(x), i));
    }
  };
  return Le(
    s,
    e ? {
      add: Bn("add"),
      set: Bn("set"),
      delete: Bn("delete"),
      clear: Bn("clear")
    } : {
      add(o) {
        const l = /* @__PURE__ */ me(this), i = Dn(l), a = /* @__PURE__ */ me(o), d = !t && !/* @__PURE__ */ ft(o) && !/* @__PURE__ */ Wt(o) ? a : o;
        return i.has.call(l, d) || Pt(o, d) && i.has.call(l, o) || Pt(a, d) && i.has.call(l, a) || (l.add(d), Bt(l, "add", d, d)), this;
      },
      set(o, l) {
        !t && !/* @__PURE__ */ ft(l) && !/* @__PURE__ */ Wt(l) && (l = /* @__PURE__ */ me(l));
        const i = /* @__PURE__ */ me(this), { has: a, get: d } = Dn(i);
        let m = a.call(i, o);
        m || (o = /* @__PURE__ */ me(o), m = a.call(i, o));
        const g = d.call(i, o);
        return i.set(o, l), m ? Pt(l, g) && Bt(i, "set", o, l) : Bt(i, "add", o, l), this;
      },
      delete(o) {
        const l = /* @__PURE__ */ me(this), { has: i, get: a } = Dn(l);
        let d = i.call(l, o);
        d || (o = /* @__PURE__ */ me(o), d = i.call(l, o)), a && a.call(l, o);
        const m = l.delete(o);
        return d && Bt(l, "delete", o, void 0), m;
      },
      clear() {
        const o = /* @__PURE__ */ me(this), l = o.size !== 0, i = o.clear();
        return l && Bt(
          o,
          "clear",
          void 0,
          void 0
        ), i;
      }
    }
  ), [
    "keys",
    "values",
    "entries",
    Symbol.iterator
  ].forEach((o) => {
    s[o] = bu(o, e, t);
  }), s;
}
function cr(e, t) {
  const s = vu(e, t);
  return (n, o, l) => o === "__v_isReactive" ? !e : o === "__v_isReadonly" ? e : o === "__v_raw" ? n : Reflect.get(
    ge(s, o) && o in n ? s : n,
    o,
    l
  );
}
const yu = {
  get: /* @__PURE__ */ cr(!1, !1)
}, xu = {
  get: /* @__PURE__ */ cr(!1, !0)
}, _u = {
  get: /* @__PURE__ */ cr(!0, !1)
};
const ni = /* @__PURE__ */ new WeakMap(), oi = /* @__PURE__ */ new WeakMap(), ri = /* @__PURE__ */ new WeakMap(), wu = /* @__PURE__ */ new WeakMap();
function ku(e) {
  switch (e) {
    case "Object":
    case "Array":
      return 1;
    case "Map":
    case "Set":
    case "WeakMap":
    case "WeakSet":
      return 2;
    default:
      return 0;
  }
}
// @__NO_SIDE_EFFECTS__
function zt(e) {
  return /* @__PURE__ */ Wt(e) ? e : fr(
    e,
    !1,
    mu,
    yu,
    ni
  );
}
// @__NO_SIDE_EFFECTS__
function Su(e) {
  return fr(
    e,
    !1,
    hu,
    xu,
    oi
  );
}
// @__NO_SIDE_EFFECTS__
function Jo(e) {
  return fr(
    e,
    !0,
    gu,
    _u,
    ri
  );
}
function fr(e, t, s, n, o) {
  if (!ye(e) || e.__v_raw && !(t && e.__v_isReactive) || e.__v_skip || !Object.isExtensible(e))
    return e;
  const l = o.get(e);
  if (l)
    return l;
  const i = ku(Ga(e));
  if (i === 0)
    return e;
  const a = new Proxy(
    e,
    i === 2 ? n : s
  );
  return o.set(e, a), a;
}
// @__NO_SIDE_EFFECTS__
function cs(e) {
  return /* @__PURE__ */ Wt(e) ? /* @__PURE__ */ cs(e.__v_raw) : !!(e && e.__v_isReactive);
}
// @__NO_SIDE_EFFECTS__
function Wt(e) {
  return !!(e && e.__v_isReadonly);
}
// @__NO_SIDE_EFFECTS__
function ft(e) {
  return !!(e && e.__v_isShallow);
}
// @__NO_SIDE_EFFECTS__
function mo(e) {
  return e ? !!e.__v_raw : !1;
}
// @__NO_SIDE_EFFECTS__
function me(e) {
  const t = e && e.__v_raw;
  return t ? /* @__PURE__ */ me(t) : e;
}
function Cu(e) {
  return !ge(e, "__v_skip") && Object.isExtensible(e) && Fl(e, "__v_skip", !0), e;
}
const yt = (e) => ye(e) ? /* @__PURE__ */ zt(e) : e, Ps = (e) => ye(e) ? /* @__PURE__ */ Jo(e) : e;
// @__NO_SIDE_EFFECTS__
function Ue(e) {
  return e ? e.__v_isRef === !0 : !1;
}
// @__NO_SIDE_EFFECTS__
function L(e) {
  return Au(e, !1);
}
function Au(e, t) {
  return /* @__PURE__ */ Ue(e) ? e : new Eu(e, t);
}
class Eu {
  constructor(t, s) {
    this.dep = new dr(), this.__v_isRef = !0, this.__v_isShallow = !1, this._rawValue = s ? t : /* @__PURE__ */ me(t), this._value = s ? t : yt(t), this.__v_isShallow = s;
  }
  get value() {
    return this.dep.track(), this._value;
  }
  set value(t) {
    const s = this._rawValue, n = this.__v_isShallow || /* @__PURE__ */ ft(t) || /* @__PURE__ */ Wt(t);
    t = n ? t : /* @__PURE__ */ me(t), Pt(t, s) && (this._rawValue = t, this._value = n ? t : yt(t), this.dep.trigger());
  }
}
function Iu(e) {
  e.dep && e.dep.trigger();
}
function h(e) {
  return /* @__PURE__ */ Ue(e) ? e.value : e;
}
function li(e) {
  return X(e) ? e() : h(e);
}
const Tu = {
  get: (e, t, s) => t === "__v_raw" ? e : h(Reflect.get(e, t, s)),
  set: (e, t, s, n) => {
    const o = e[t];
    return /* @__PURE__ */ Ue(o) && !/* @__PURE__ */ Ue(s) ? (o.value = s, !0) : Reflect.set(e, t, s, n);
  }
};
function ii(e) {
  return /* @__PURE__ */ cs(e) ? e : new Proxy(e, Tu);
}
// @__NO_SIDE_EFFECTS__
function Pu(e) {
  const t = G(e) ? new Array(e.length) : {};
  for (const s in e)
    t[s] = ai(e, s);
  return t;
}
class Ru {
  constructor(t, s, n) {
    this._object = t, this._defaultValue = n, this.__v_isRef = !0, this._value = void 0, this._key = pt(s) ? s : String(s), this._raw = /* @__PURE__ */ me(t);
    let o = !0, l = t;
    if (!G(t) || pt(this._key) || !ao(this._key))
      do
        o = !/* @__PURE__ */ mo(l) || /* @__PURE__ */ ft(l);
      while (o && (l = l.__v_raw));
    this._shallow = o;
  }
  get value() {
    let t = this._object[this._key];
    return this._shallow && (t = h(t)), this._value = t === void 0 ? this._defaultValue : t;
  }
  set value(t) {
    if (this._shallow && /* @__PURE__ */ Ue(this._raw[this._key])) {
      const s = this._object[this._key];
      if (/* @__PURE__ */ Ue(s)) {
        s.value = t;
        return;
      }
    }
    this._object[this._key] = t;
  }
  get dep() {
    return au(this._raw, this._key);
  }
}
class Mu {
  constructor(t) {
    this._getter = t, this.__v_isRef = !0, this.__v_isReadonly = !0, this._value = void 0;
  }
  get value() {
    return this._value = this._getter();
  }
}
// @__NO_SIDE_EFFECTS__
function Vu(e, t, s) {
  return /* @__PURE__ */ Ue(e) ? e : X(e) ? new Mu(e) : ye(e) && arguments.length > 1 ? ai(e, t, s) : /* @__PURE__ */ L(e);
}
function ai(e, t, s) {
  return new Ru(e, t, s);
}
class $u {
  constructor(t, s, n) {
    this.fn = t, this.setter = s, this._value = void 0, this.dep = new dr(this), this.__v_isRef = !0, this.deps = void 0, this.depsTail = void 0, this.flags = 16, this.globalVersion = vn - 1, this.next = void 0, this.effect = this, this.__v_isReadonly = !s, this.isSSR = n;
  }
  /**
   * @internal
   */
  notify() {
    if (this.flags |= 16, !(this.flags & 8) && // avoid infinite self recursion
    Ce !== this)
      return Gl(this, !0), !0;
  }
  get value() {
    const t = this.dep.track();
    return Ql(this), t && (t.version = this.dep.version), this._value;
  }
  set value(t) {
    this.setter && this.setter(t);
  }
}
// @__NO_SIDE_EFFECTS__
function Ou(e, t, s = !1) {
  let n, o;
  return X(e) ? n = e : (n = e.get, o = e.set), new $u(n, o, s);
}
const Fn = {}, Qn = /* @__PURE__ */ new WeakMap();
let us;
function ju(e, t = !1, s = us) {
  if (s) {
    let n = Qn.get(s);
    n || Qn.set(s, n = []), n.push(e);
  }
}
function Nu(e, t, s = ke) {
  const { immediate: n, deep: o, once: l, scheduler: i, augmentJob: a, call: d } = s, m = (B) => o ? B : /* @__PURE__ */ ft(B) || o === !1 || o === 0 ? Ft(B, 1) : Ft(B);
  let g, x, C, E, U = !1, A = !1;
  if (/* @__PURE__ */ Ue(e) ? (x = () => e.value, U = /* @__PURE__ */ ft(e)) : /* @__PURE__ */ cs(e) ? (x = () => m(e), U = !0) : G(e) ? (A = !0, U = e.some((B) => /* @__PURE__ */ cs(B) || /* @__PURE__ */ ft(B)), x = () => e.map((B) => {
    if (/* @__PURE__ */ Ue(B))
      return B.value;
    if (/* @__PURE__ */ cs(B))
      return m(B);
    if (X(B))
      return d ? d(B, 2) : B();
  })) : X(e) ? t ? x = d ? () => d(e, 2) : e : x = () => {
    if (C) {
      Mt();
      try {
        C();
      } finally {
        Vt();
      }
    }
    const B = us;
    us = g;
    try {
      return d ? d(e, 3, [E]) : e(E);
    } finally {
      us = B;
    }
  } : x = Rt, t && o) {
    const B = x, Q = o === !0 ? 1 / 0 : o;
    x = () => Ft(B(), Q);
  }
  const w = ru(), H = () => {
    g.stop(), w && w.active && rr(w.effects, g);
  };
  if (l && t) {
    const B = t;
    t = (...Q) => {
      const je = B(...Q);
      return H(), je;
    };
  }
  let D = A ? new Array(e.length).fill(Fn) : Fn;
  const K = (B) => {
    if (!(!(g.flags & 1) || !g.dirty && !B))
      if (t) {
        const Q = g.run();
        if (B || o || U || (A ? Q.some((je, W) => Pt(je, D[W])) : Pt(Q, D))) {
          C && C();
          const je = us;
          us = g;
          try {
            const W = [
              Q,
              // pass undefined as the old value when it's changed for the first time
              D === Fn ? void 0 : A && D[0] === Fn ? [] : D,
              E
            ];
            D = Q, d ? d(t, 3, W) : (
              // @ts-expect-error
              t(...W)
            );
          } finally {
            us = je;
          }
        }
      } else
        g.run();
  };
  return a && a(K), g = new Kl(x), g.scheduler = i ? () => i(K, !1) : K, E = (B) => ju(B, !1, g), C = g.onStop = () => {
    const B = Qn.get(g);
    if (B) {
      if (d)
        d(B, 4);
      else
        for (const Q of B) Q();
      Qn.delete(g);
    }
  }, t ? n ? K(!0) : D = g.run() : i ? i(K.bind(null, !0), !0) : g.run(), H.pause = g.pause.bind(g), H.resume = g.resume.bind(g), H.stop = H, H;
}
function Ft(e, t = 1 / 0, s) {
  if (t <= 0 || !ye(e) || e.__v_skip || (s = s || /* @__PURE__ */ new Map(), (s.get(e) || 0) >= t))
    return e;
  if (s.set(e, t), t--, /* @__PURE__ */ Ue(e))
    Ft(e.value, t, s);
  else if (G(e))
    for (let n = 0; n < e.length; n++)
      Ft(e[n], t, s);
  else if (Vs(e) || Cs(e))
    e.forEach((n) => {
      Ft(n, t, s);
    });
  else if (io(e)) {
    for (const n in e)
      Ft(e[n], t, s);
    for (const n of Object.getOwnPropertySymbols(e))
      Object.prototype.propertyIsEnumerable.call(e, n) && Ft(e[n], t, s);
  }
  return e;
}
/**
* @vue/runtime-core v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
function Sn(e, t, s, n) {
  try {
    return n ? e(...n) : e();
  } catch (o) {
    Cn(o, t, s);
  }
}
function xt(e, t, s, n) {
  if (X(e)) {
    const o = Sn(e, t, s, n);
    return o && Ul(o) && o.catch((l) => {
      Cn(l, t, s);
    }), o;
  }
  if (G(e)) {
    const o = [];
    for (let l = 0; l < e.length; l++)
      o.push(xt(e[l], t, s, n));
    return o;
  }
}
function Cn(e, t, s, n = !0) {
  const o = t ? t.vnode : null, { errorHandler: l, throwUnhandledErrorInProduction: i } = t && t.appContext.config || ke;
  if (t) {
    let a = t.parent;
    const d = t.proxy, m = `https://vuejs.org/error-reference/#runtime-${s}`;
    for (; a; ) {
      const g = a.ec;
      if (g) {
        for (let x = 0; x < g.length; x++)
          if (g[x](e, d, m) === !1)
            return;
      }
      a = a.parent;
    }
    if (l) {
      Mt(), Sn(l, null, 10, [
        e,
        d,
        m
      ]), Vt();
      return;
    }
  }
  Lu(e, s, o, n, i);
}
function Lu(e, t, s, n = !0, o = !1) {
  if (o)
    throw e;
  console.error(e);
}
const rt = [];
let Et = -1;
const As = [];
let Zt = null, ks = 0;
const ui = /* @__PURE__ */ Promise.resolve();
let Zn = null;
function An(e) {
  const t = Zn || ui;
  return e ? t.then(this ? e.bind(this) : e) : t;
}
function Uu(e) {
  let t = Et + 1, s = rt.length;
  for (; t < s; ) {
    const n = t + s >>> 1, o = rt[n], l = xn(o);
    l < e || l === e && o.flags & 2 ? t = n + 1 : s = n;
  }
  return t;
}
function pr(e) {
  if (!(e.flags & 1)) {
    const t = xn(e), s = rt[rt.length - 1];
    !s || // fast path when the job id is larger than the tail
    !(e.flags & 2) && t >= xn(s) ? rt.push(e) : rt.splice(Uu(t), 0, e), e.flags |= 1, di();
  }
}
function di() {
  Zn || (Zn = ui.then(fi));
}
function Du(e) {
  G(e) ? As.push(...e) : Zt && e.id === -1 ? Zt.splice(ks + 1, 0, e) : e.flags & 1 || (As.push(e), e.flags |= 1), di();
}
function Xr(e, t, s = Et + 1) {
  for (; s < rt.length; s++) {
    const n = rt[s];
    if (n && n.flags & 2) {
      if (e && n.id !== e.uid)
        continue;
      rt.splice(s, 1), s--, n.flags & 4 && (n.flags &= -2), n(), n.flags & 4 || (n.flags &= -2);
    }
  }
}
function ci(e) {
  if (As.length) {
    const t = [...new Set(As)].sort(
      (s, n) => xn(s) - xn(n)
    );
    if (As.length = 0, Zt) {
      Zt.push(...t);
      return;
    }
    for (Zt = t, ks = 0; ks < Zt.length; ks++) {
      const s = Zt[ks];
      s.flags & 4 && (s.flags &= -2), s.flags & 8 || s(), s.flags &= -2;
    }
    Zt = null, ks = 0;
  }
}
const xn = (e) => e.id == null ? e.flags & 2 ? -1 : 1 / 0 : e.id;
function fi(e) {
  try {
    for (Et = 0; Et < rt.length; Et++) {
      const t = rt[Et];
      t && !(t.flags & 8) && (t.flags & 4 && (t.flags &= -2), Sn(
        t,
        t.i,
        t.i ? 15 : 14
      ), t.flags & 4 || (t.flags &= -2));
    }
  } finally {
    for (; Et < rt.length; Et++) {
      const t = rt[Et];
      t && (t.flags &= -2);
    }
    Et = -1, rt.length = 0, ci(), Zn = null, (rt.length || As.length) && fi();
  }
}
let Xe = null, pi = null;
function Xn(e) {
  const t = Xe;
  return Xe = e, pi = e && e.type.__scopeId || null, t;
}
function k(e, t = Xe, s) {
  if (!t || e._n)
    return e;
  const n = (...o) => {
    n._d && so(-1);
    const l = Xn(t);
    let i;
    try {
      i = e(...o);
    } finally {
      Xn(l), n._d && so(1);
    }
    return i;
  };
  return n._n = !0, n._c = !0, n._d = !0, n;
}
function mr(e, t) {
  if (Xe === null)
    return e;
  const s = vo(Xe), n = e.dirs || (e.dirs = []);
  for (let o = 0; o < t.length; o++) {
    let [l, i, a, d = ke] = t[o];
    l && (X(l) && (l = {
      mounted: l,
      updated: l
    }), l.deep && Ft(i), n.push({
      dir: l,
      instance: s,
      value: i,
      oldValue: void 0,
      arg: a,
      modifiers: d
    }));
  }
  return e;
}
function ls(e, t, s, n) {
  const o = e.dirs, l = t && t.dirs;
  for (let i = 0; i < o.length; i++) {
    const a = o[i];
    l && (a.oldValue = l[i].value);
    let d = a.dir[n];
    d && (Mt(), xt(d, s, 8, [
      e.el,
      a,
      e,
      t
    ]), Vt());
  }
}
function mi(e, t) {
  if (Ze) {
    let s = Ze.provides;
    const n = Ze.parent && Ze.parent.provides;
    n === s && (s = Ze.provides = Object.create(n)), s[e] = t;
  }
}
function pn(e, t, s = !1) {
  const n = ps();
  if (n || Is) {
    let o = Is ? Is._context.provides : n ? n.parent == null || n.ce ? n.vnode.appContext && n.vnode.appContext.provides : n.parent.provides : void 0;
    if (o && e in o)
      return o[e];
    if (arguments.length > 1)
      return s && X(t) ? t.call(n && n.proxy) : t;
  }
}
const Bu = /* @__PURE__ */ Symbol.for("v-scx"), Fu = () => pn(Bu);
function gt(e, t, s) {
  return gi(e, t, s);
}
function gi(e, t, s = ke) {
  const { immediate: n, deep: o, flush: l, once: i } = s, a = Le({}, s), d = t && n || !t && l !== "post";
  let m;
  if (Rs) {
    if (l === "sync") {
      const E = Fu();
      m = E.__watcherHandles || (E.__watcherHandles = []);
    } else if (!d) {
      const E = () => {
      };
      return E.stop = Rt, E.resume = Rt, E.pause = Rt, E;
    }
  }
  const g = Ze;
  a.call = (E, U, A) => xt(E, g, U, A);
  let x = !1;
  l === "post" ? a.scheduler = (E) => {
    at(E, g && g.suspense);
  } : l !== "sync" && (x = !0, a.scheduler = (E, U) => {
    U ? E() : pr(E);
  }), a.augmentJob = (E) => {
    t && (E.flags |= 4), x && (E.flags |= 2, g && (E.id = g.uid, E.i = g));
  };
  const C = Nu(e, t, a);
  return Rs && (m ? m.push(C) : d && C()), C;
}
function Hu(e, t, s) {
  const n = this.proxy, o = Ve(e) ? e.includes(".") ? hi(n, e) : () => n[e] : e.bind(n, n);
  let l;
  X(t) ? l = t : (l = t.handler, s = t);
  const i = En(this), a = gi(o, l.bind(n), s);
  return i(), a;
}
function hi(e, t) {
  const s = t.split(".");
  return () => {
    let n = e;
    for (let o = 0; o < s.length && n; o++)
      n = n[s[o]];
    return n;
  };
}
const zu = /* @__PURE__ */ Symbol("_vte"), Wu = (e) => e.__isTeleport, No = /* @__PURE__ */ Symbol("_leaveCb");
function gr(e, t) {
  e.shapeFlag & 6 && e.component ? (e.transition = t, gr(e.component.subTree, t)) : e.shapeFlag & 128 ? (e.ssContent.transition = t.clone(e.ssContent), e.ssFallback.transition = t.clone(e.ssFallback)) : e.transition = t;
}
// @__NO_SIDE_EFFECTS__
function qe(e, t) {
  return X(e) ? (
    // #8236: extend call and options.name access are considered side-effects
    // by Rollup, so we have to wrap it in a pure-annotated IIFE.
    Le({ name: e.name }, t, { setup: e })
  ) : e;
}
function hr(e) {
  e.ids = [e.ids[0] + e.ids[2]++ + "-", 0, 0];
}
function el(e, t) {
  let s;
  return !!((s = Object.getOwnPropertyDescriptor(e, t)) && !s.configurable);
}
const eo = /* @__PURE__ */ new WeakMap();
function mn(e, t, s, n, o = !1) {
  if (G(e)) {
    e.forEach(
      (A, w) => mn(
        A,
        t && (G(t) ? t[w] : t),
        s,
        n,
        o
      )
    );
    return;
  }
  if (Es(n) && !o) {
    n.shapeFlag & 512 && n.type.__asyncResolved && n.component.subTree.component && mn(e, t, s, n.component.subTree);
    return;
  }
  const l = n.shapeFlag & 4 ? vo(n.component) : n.el, i = o ? null : l, { i: a, r: d } = e, m = t && t.r, g = a.refs === ke ? a.refs = {} : a.refs, x = a.setupState, C = /* @__PURE__ */ me(x), E = x === ke ? Ll : (A) => el(g, A) ? !1 : ge(C, A), U = (A, w) => !(w && el(g, w));
  if (m != null && m !== d) {
    if (tl(t), Ve(m))
      g[m] = null, E(m) && (x[m] = null);
    else if (/* @__PURE__ */ Ue(m)) {
      const A = t;
      U(m, A.k) && (m.value = null), A.k && (g[A.k] = null);
    }
  }
  if (X(d)) {
    Mt();
    try {
      Sn(d, a, 12, [i, g]);
    } finally {
      Vt();
    }
  } else {
    const A = Ve(d), w = /* @__PURE__ */ Ue(d);
    if (A || w) {
      const H = () => {
        if (e.f) {
          const D = A ? E(d) ? x[d] : g[d] : U() || !e.k ? d.value : g[e.k];
          if (o)
            G(D) && rr(D, l);
          else if (G(D))
            D.includes(l) || D.push(l);
          else if (A)
            g[d] = [l], E(d) && (x[d] = g[d]);
          else {
            const K = [l];
            U(d, e.k) && (d.value = K), e.k && (g[e.k] = K);
          }
        } else A ? (g[d] = i, E(d) && (x[d] = i)) : w && (U(d, e.k) && (d.value = i), e.k && (g[e.k] = i));
      };
      if (i) {
        const D = () => {
          H(), eo.delete(e);
        };
        D.id = -1, eo.set(e, D), at(D, s);
      } else
        tl(e), H();
    }
  }
}
function tl(e) {
  const t = eo.get(e);
  t && (t.flags |= 8, eo.delete(e));
}
const sl = (e) => e.nodeType === 8;
fo().requestIdleCallback;
fo().cancelIdleCallback;
function Ku(e, t) {
  if (sl(e) && e.data === "[") {
    let s = 1, n = e.nextSibling;
    for (; n; ) {
      if (n.nodeType === 1) {
        if (t(n) === !1)
          break;
      } else if (sl(n))
        if (n.data === "]") {
          if (--s === 0) break;
        } else n.data === "[" && s++;
      n = n.nextSibling;
    }
  } else
    t(e);
}
const Es = (e) => !!e.type.__asyncLoader;
// @__NO_SIDE_EFFECTS__
function qu(e) {
  X(e) && (e = { loader: e });
  const {
    loader: t,
    loadingComponent: s,
    errorComponent: n,
    delay: o = 200,
    hydrate: l,
    timeout: i,
    // undefined = never times out
    suspensible: a = !0,
    onError: d
  } = e;
  let m = null, g, x = 0;
  const C = () => (x++, m = null, E()), E = () => {
    let U;
    return m || (U = m = t().catch((A) => {
      if (A = A instanceof Error ? A : new Error(String(A)), d)
        return new Promise((w, H) => {
          d(A, () => w(C()), () => H(A), x + 1);
        });
      throw A;
    }).then((A) => U !== m && m ? m : (A && (A.__esModule || A[Symbol.toStringTag] === "Module") && (A = A.default), g = A, A)));
  };
  return /* @__PURE__ */ qe({
    name: "AsyncComponentWrapper",
    __asyncLoader: E,
    __asyncHydrate(U, A, w) {
      let H = !1;
      (A.bu || (A.bu = [])).push(() => H = !0);
      const D = () => {
        H || w();
      }, K = l ? () => {
        const B = l(
          D,
          (Q) => Ku(U, Q)
        );
        B && (A.bum || (A.bum = [])).push(B);
      } : D;
      g ? K() : E().then(() => !A.isUnmounted && K());
    },
    get __asyncResolved() {
      return g;
    },
    setup() {
      const U = Ze;
      if (hr(U), g)
        return () => Hn(g, U);
      const A = (Q) => {
        m = null, Cn(
          Q,
          U,
          13,
          !n
        );
      };
      if (a && U.suspense || Rs)
        return E().then((Q) => () => Hn(Q, U)).catch((Q) => (A(Q), () => n ? v(n, {
          error: Q
        }) : null));
      const w = /* @__PURE__ */ L(!1), H = /* @__PURE__ */ L(), D = /* @__PURE__ */ L(!!o);
      let K, B;
      return vr(() => {
        K != null && clearTimeout(K), B != null && clearTimeout(B);
      }), o && (B = setTimeout(() => {
        U.isUnmounted || (D.value = !1);
      }, o)), i != null && (K = setTimeout(() => {
        if (!U.isUnmounted && !w.value && !H.value) {
          const Q = new Error(
            `Async component timed out after ${i}ms.`
          );
          A(Q), H.value = Q;
        }
      }, i)), E().then(() => {
        U.isUnmounted || (w.value = !0, U.parent && br(U.parent.vnode) && U.parent.update());
      }).catch((Q) => {
        if (U.isUnmounted) {
          m = null;
          return;
        }
        A(Q), H.value = Q;
      }), () => {
        if (w.value && g)
          return Hn(g, U);
        if (H.value && n)
          return v(n, {
            error: H.value
          });
        if (s && !D.value)
          return Hn(
            s,
            U
          );
      };
    }
  });
}
function Hn(e, t) {
  const { ref: s, props: n, children: o, ce: l } = t.vnode, i = v(e, n, o);
  return i.ref = s, i.ce = l, delete t.vnode.ce, i;
}
const br = (e) => e.type.__isKeepAlive;
function Gu(e, t) {
  bi(e, "a", t);
}
function Ju(e, t) {
  bi(e, "da", t);
}
function bi(e, t, s = Ze) {
  const n = e.__wdc || (e.__wdc = () => {
    let o = s;
    for (; o; ) {
      if (o.isDeactivated)
        return;
      o = o.parent;
    }
    return e();
  });
  if (go(t, n, s), s) {
    let o = s.parent;
    for (; o && o.parent; )
      br(o.parent.vnode) && Yu(n, t, s, o), o = o.parent;
  }
}
function Yu(e, t, s, n) {
  const o = go(
    t,
    e,
    n,
    !0
    /* prepend */
  );
  vr(() => {
    rr(n[t], o);
  }, s);
}
function go(e, t, s = Ze, n = !1) {
  if (s) {
    const o = s[e] || (s[e] = []), l = t.__weh || (t.__weh = (...i) => {
      Mt();
      const a = En(s), d = xt(t, s, e, i);
      return a(), Vt(), d;
    });
    return n ? o.unshift(l) : o.push(l), l;
  }
}
const Kt = (e) => (t, s = Ze) => {
  (!Rs || e === "sp") && go(e, (...n) => t(...n), s);
}, Qu = Kt("bm"), vi = Kt("m"), Zu = Kt(
  "bu"
), yi = Kt("u"), xi = Kt(
  "bum"
), vr = Kt("um"), Xu = Kt(
  "sp"
), ed = Kt("rtg"), td = Kt("rtc");
function sd(e, t = Ze) {
  go("ec", e, t);
}
const nd = /* @__PURE__ */ Symbol.for("v-ndc");
function Ye(e, t, s, n) {
  let o;
  const l = s, i = G(e);
  if (i || Ve(e)) {
    const a = i && /* @__PURE__ */ cs(e);
    let d = !1, m = !1;
    a && (d = !/* @__PURE__ */ ft(e), m = /* @__PURE__ */ Wt(e), e = po(e)), o = new Array(e.length);
    for (let g = 0, x = e.length; g < x; g++)
      o[g] = t(
        d ? m ? Ps(yt(e[g])) : yt(e[g]) : e[g],
        g,
        void 0,
        l
      );
  } else if (typeof e == "number") {
    o = new Array(e);
    for (let a = 0; a < e; a++)
      o[a] = t(a + 1, a, void 0, l);
  } else if (ye(e))
    if (e[Symbol.iterator])
      o = Array.from(
        e,
        (a, d) => t(a, d, void 0, l)
      );
    else {
      const a = Object.keys(e);
      o = new Array(a.length);
      for (let d = 0, m = a.length; d < m; d++) {
        const g = a[d];
        o[d] = t(e[g], g, d, l);
      }
    }
  else
    o = [];
  return o;
}
function ss(e, t, s = {}, n, o) {
  if (Xe.ce || Xe.parent && Es(Xe.parent) && Xe.parent.ce) {
    const m = Object.keys(s).length > 0;
    return S(), Ie(
      ue,
      null,
      [v("slot", s, n)],
      m ? -2 : 64
    );
  }
  let l = e[t];
  l && l._c && (l._d = !1), S();
  const i = l && _i(l(s)), a = s.key || // slot content array of a dynamic conditional slot may have a branch
  // key attached in the `createSlots` helper, respect that
  i && i.key, d = Ie(
    ue,
    {
      key: (a && !pt(a) ? a : `_${t}`) + // #7256 force differentiate fallback content from actual content
      (!i && n ? "_fb" : "")
    },
    i || [],
    i && e._ === 1 ? 64 : -2
  );
  return d.scopeId && (d.slotScopeIds = [d.scopeId + "-s"]), l && l._c && (l._d = !0), d;
}
function _i(e) {
  return e.some((t) => wn(t) ? !(t.type === $t || t.type === ue && !_i(t.children)) : !0) ? e : null;
}
const Yo = (e) => e ? Bi(e) ? vo(e) : Yo(e.parent) : null, gn = (
  // Move PURE marker to new line to workaround compiler discarding it
  // due to type annotation
  /* @__PURE__ */ Le(/* @__PURE__ */ Object.create(null), {
    $: (e) => e,
    $el: (e) => e.vnode.el,
    $data: (e) => e.data,
    $props: (e) => e.props,
    $attrs: (e) => e.attrs,
    $slots: (e) => e.slots,
    $refs: (e) => e.refs,
    $parent: (e) => Yo(e.parent),
    $root: (e) => Yo(e.root),
    $host: (e) => e.ce,
    $emit: (e) => e.emit,
    $options: (e) => ki(e),
    $forceUpdate: (e) => e.f || (e.f = () => {
      pr(e.update);
    }),
    $nextTick: (e) => e.n || (e.n = An.bind(e.proxy)),
    $watch: (e) => Hu.bind(e)
  })
), Lo = (e, t) => e !== ke && !e.__isScriptSetup && ge(e, t), od = {
  get({ _: e }, t) {
    if (t === "__v_skip")
      return !0;
    const { ctx: s, setupState: n, data: o, props: l, accessCache: i, type: a, appContext: d } = e;
    if (t[0] !== "$") {
      const C = i[t];
      if (C !== void 0)
        switch (C) {
          case 1:
            return n[t];
          case 2:
            return o[t];
          case 4:
            return s[t];
          case 3:
            return l[t];
        }
      else {
        if (Lo(n, t))
          return i[t] = 1, n[t];
        if (o !== ke && ge(o, t))
          return i[t] = 2, o[t];
        if (ge(l, t))
          return i[t] = 3, l[t];
        if (s !== ke && ge(s, t))
          return i[t] = 4, s[t];
        Qo && (i[t] = 0);
      }
    }
    const m = gn[t];
    let g, x;
    if (m)
      return t === "$attrs" && Qe(e.attrs, "get", ""), m(e);
    if (
      // css module (injected by vue-loader)
      (g = a.__cssModules) && (g = g[t])
    )
      return g;
    if (s !== ke && ge(s, t))
      return i[t] = 4, s[t];
    if (
      // global properties
      x = d.config.globalProperties, ge(x, t)
    )
      return x[t];
  },
  set({ _: e }, t, s) {
    const { data: n, setupState: o, ctx: l } = e;
    return Lo(o, t) ? (o[t] = s, !0) : n !== ke && ge(n, t) ? (n[t] = s, !0) : ge(e.props, t) || t[0] === "$" && t.slice(1) in e ? !1 : (l[t] = s, !0);
  },
  has({
    _: { data: e, setupState: t, accessCache: s, ctx: n, appContext: o, props: l, type: i }
  }, a) {
    let d;
    return !!(s[a] || e !== ke && a[0] !== "$" && ge(e, a) || Lo(t, a) || ge(l, a) || ge(n, a) || ge(gn, a) || ge(o.config.globalProperties, a) || (d = i.__cssModules) && d[a]);
  },
  defineProperty(e, t, s) {
    return s.get != null ? e._.accessCache[t] = 0 : ge(s, "value") && this.set(e, t, s.value, null), Reflect.defineProperty(e, t, s);
  }
};
function nl(e) {
  return G(e) ? e.reduce(
    (t, s) => (t[s] = null, t),
    {}
  ) : e;
}
let Qo = !0;
function rd(e) {
  const t = ki(e), s = e.proxy, n = e.ctx;
  Qo = !1, t.beforeCreate && ol(t.beforeCreate, e, "bc");
  const {
    // state
    data: o,
    computed: l,
    methods: i,
    watch: a,
    provide: d,
    inject: m,
    // lifecycle
    created: g,
    beforeMount: x,
    mounted: C,
    beforeUpdate: E,
    updated: U,
    activated: A,
    deactivated: w,
    beforeDestroy: H,
    beforeUnmount: D,
    destroyed: K,
    unmounted: B,
    render: Q,
    renderTracked: je,
    renderTriggered: W,
    errorCaptured: te,
    serverPrefetch: Re,
    // public API
    expose: _e,
    inheritAttrs: $e,
    // assets
    components: re,
    directives: xe,
    filters: He
  } = t;
  if (m && ld(m, n, null), i)
    for (const fe in i) {
      const se = i[fe];
      X(se) && (n[fe] = se.bind(s));
    }
  if (o) {
    const fe = o.call(s, s);
    ye(fe) && (e.data = /* @__PURE__ */ zt(fe));
  }
  if (Qo = !0, l)
    for (const fe in l) {
      const se = l[fe], Me = X(se) ? se.bind(s, s) : X(se.get) ? se.get.bind(s, s) : Rt, De = !X(se) && X(se.set) ? se.set.bind(s) : Rt, ze = he({
        get: Me,
        set: De
      });
      Object.defineProperty(n, fe, {
        enumerable: !0,
        configurable: !0,
        get: () => ze.value,
        set: (Be) => ze.value = Be
      });
    }
  if (a)
    for (const fe in a)
      wi(a[fe], n, s, fe);
  if (d) {
    const fe = X(d) ? d.call(s) : d;
    Reflect.ownKeys(fe).forEach((se) => {
      mi(se, fe[se]);
    });
  }
  g && ol(g, e, "c");
  function we(fe, se) {
    G(se) ? se.forEach((Me) => fe(Me.bind(s))) : se && fe(se.bind(s));
  }
  if (we(Qu, x), we(vi, C), we(Zu, E), we(yi, U), we(Gu, A), we(Ju, w), we(sd, te), we(td, je), we(ed, W), we(xi, D), we(vr, B), we(Xu, Re), G(_e))
    if (_e.length) {
      const fe = e.exposed || (e.exposed = {});
      _e.forEach((se) => {
        Object.defineProperty(fe, se, {
          get: () => s[se],
          set: (Me) => s[se] = Me,
          enumerable: !0
        });
      });
    } else e.exposed || (e.exposed = {});
  Q && e.render === Rt && (e.render = Q), $e != null && (e.inheritAttrs = $e), re && (e.components = re), xe && (e.directives = xe), Re && hr(e);
}
function ld(e, t, s = Rt) {
  G(e) && (e = Zo(e));
  for (const n in e) {
    const o = e[n];
    let l;
    ye(o) ? "default" in o ? l = pn(
      o.from || n,
      o.default,
      !0
    ) : l = pn(o.from || n) : l = pn(o), /* @__PURE__ */ Ue(l) ? Object.defineProperty(t, n, {
      enumerable: !0,
      configurable: !0,
      get: () => l.value,
      set: (i) => l.value = i
    }) : t[n] = l;
  }
}
function ol(e, t, s) {
  xt(
    G(e) ? e.map((n) => n.bind(t.proxy)) : e.bind(t.proxy),
    t,
    s
  );
}
function wi(e, t, s, n) {
  let o = n.includes(".") ? hi(s, n) : () => s[n];
  if (Ve(e)) {
    const l = t[e];
    X(l) && gt(o, l);
  } else if (X(e))
    gt(o, e.bind(s));
  else if (ye(e))
    if (G(e))
      e.forEach((l) => wi(l, t, s, n));
    else {
      const l = X(e.handler) ? e.handler.bind(s) : t[e.handler];
      X(l) && gt(o, l, e);
    }
}
function ki(e) {
  const t = e.type, { mixins: s, extends: n } = t, {
    mixins: o,
    optionsCache: l,
    config: { optionMergeStrategies: i }
  } = e.appContext, a = l.get(t);
  let d;
  return a ? d = a : !o.length && !s && !n ? d = t : (d = {}, o.length && o.forEach(
    (m) => to(d, m, i, !0)
  ), to(d, t, i)), ye(t) && l.set(t, d), d;
}
function to(e, t, s, n = !1) {
  const { mixins: o, extends: l } = t;
  l && to(e, l, s, !0), o && o.forEach(
    (i) => to(e, i, s, !0)
  );
  for (const i in t)
    if (!(n && i === "expose")) {
      const a = id[i] || s && s[i];
      e[i] = a ? a(e[i], t[i]) : t[i];
    }
  return e;
}
const id = {
  data: rl,
  props: ll,
  emits: ll,
  // objects
  methods: rn,
  computed: rn,
  // lifecycle
  beforeCreate: nt,
  created: nt,
  beforeMount: nt,
  mounted: nt,
  beforeUpdate: nt,
  updated: nt,
  beforeDestroy: nt,
  beforeUnmount: nt,
  destroyed: nt,
  unmounted: nt,
  activated: nt,
  deactivated: nt,
  errorCaptured: nt,
  serverPrefetch: nt,
  // assets
  components: rn,
  directives: rn,
  // watch
  watch: ud,
  // provide / inject
  provide: rl,
  inject: ad
};
function rl(e, t) {
  return t ? e ? function() {
    return Le(
      X(e) ? e.call(this, this) : e,
      X(t) ? t.call(this, this) : t
    );
  } : t : e;
}
function ad(e, t) {
  return rn(Zo(e), Zo(t));
}
function Zo(e) {
  if (G(e)) {
    const t = {};
    for (let s = 0; s < e.length; s++)
      t[e[s]] = e[s];
    return t;
  }
  return e;
}
function nt(e, t) {
  return e ? [...new Set([].concat(e, t))] : t;
}
function rn(e, t) {
  return e ? Le(/* @__PURE__ */ Object.create(null), e, t) : t;
}
function ll(e, t) {
  return e ? G(e) && G(t) ? [.../* @__PURE__ */ new Set([...e, ...t])] : Le(
    /* @__PURE__ */ Object.create(null),
    nl(e),
    nl(t ?? {})
  ) : t;
}
function ud(e, t) {
  if (!e) return t;
  if (!t) return e;
  const s = Le(/* @__PURE__ */ Object.create(null), e);
  for (const n in t)
    s[n] = nt(e[n], t[n]);
  return s;
}
function Si() {
  return {
    app: null,
    config: {
      isNativeTag: Ll,
      performance: !1,
      globalProperties: {},
      optionMergeStrategies: {},
      errorHandler: void 0,
      warnHandler: void 0,
      compilerOptions: {}
    },
    mixins: [],
    components: {},
    directives: {},
    provides: /* @__PURE__ */ Object.create(null),
    optionsCache: /* @__PURE__ */ new WeakMap(),
    propsCache: /* @__PURE__ */ new WeakMap(),
    emitsCache: /* @__PURE__ */ new WeakMap()
  };
}
let dd = 0;
function cd(e, t) {
  return function(n, o = null) {
    X(n) || (n = Le({}, n)), o != null && !ye(o) && (o = null);
    const l = Si(), i = /* @__PURE__ */ new WeakSet(), a = [];
    let d = !1;
    const m = l.app = {
      _uid: dd++,
      _component: n,
      _props: o,
      _container: null,
      _context: l,
      _instance: null,
      version: Fd,
      get config() {
        return l.config;
      },
      set config(g) {
      },
      use(g, ...x) {
        return i.has(g) || (g && X(g.install) ? (i.add(g), g.install(m, ...x)) : X(g) && (i.add(g), g(m, ...x))), m;
      },
      mixin(g) {
        return l.mixins.includes(g) || l.mixins.push(g), m;
      },
      component(g, x) {
        return x ? (l.components[g] = x, m) : l.components[g];
      },
      directive(g, x) {
        return x ? (l.directives[g] = x, m) : l.directives[g];
      },
      mount(g, x, C) {
        if (!d) {
          const E = m._ceVNode || v(n, o);
          return E.appContext = l, C === !0 ? C = "svg" : C === !1 && (C = void 0), e(E, g, C), d = !0, m._container = g, g.__vue_app__ = m, vo(E.component);
        }
      },
      onUnmount(g) {
        a.push(g);
      },
      unmount() {
        d && (xt(
          a,
          m._instance,
          16
        ), e(null, m._container), delete m._container.__vue_app__);
      },
      provide(g, x) {
        return l.provides[g] = x, m;
      },
      runWithContext(g) {
        const x = Is;
        Is = m;
        try {
          return g();
        } finally {
          Is = x;
        }
      }
    };
    return m;
  };
}
let Is = null;
const fd = (e, t) => t === "modelValue" || t === "model-value" ? e.modelModifiers : e[`${t}Modifiers`] || e[`${et(t)}Modifiers`] || e[`${dt(t)}Modifiers`];
function pd(e, t, ...s) {
  if (e.isUnmounted) return;
  const n = e.vnode.props || ke;
  let o = s;
  const l = t.startsWith("update:"), i = l && fd(n, t.slice(7));
  i && (i.trim && (o = s.map((g) => Ve(g) ? g.trim() : g)), i.number && (o = s.map(co)));
  let a, d = n[a = Kn(t)] || // also try camelCase event handler (#2249)
  n[a = Kn(et(t))];
  !d && l && (d = n[a = Kn(dt(t))]), d && xt(
    d,
    e,
    6,
    o
  );
  const m = n[a + "Once"];
  if (m) {
    if (!e.emitted)
      e.emitted = {};
    else if (e.emitted[a])
      return;
    e.emitted[a] = !0, xt(
      m,
      e,
      6,
      o
    );
  }
}
const md = /* @__PURE__ */ new WeakMap();
function Ci(e, t, s = !1) {
  const n = s ? md : t.emitsCache, o = n.get(e);
  if (o !== void 0)
    return o;
  const l = e.emits;
  let i = {}, a = !1;
  if (!X(e)) {
    const d = (m) => {
      const g = Ci(m, t, !0);
      g && (a = !0, Le(i, g));
    };
    !s && t.mixins.length && t.mixins.forEach(d), e.extends && d(e.extends), e.mixins && e.mixins.forEach(d);
  }
  return !l && !a ? (ye(e) && n.set(e, null), null) : (G(l) ? l.forEach((d) => i[d] = null) : Le(i, l), ye(e) && n.set(e, i), i);
}
function ho(e, t) {
  return !e || !ro(t) ? !1 : (t = t.slice(2), t = t === "Once" ? t : t.replace(/Once$/, ""), ge(e, t[0].toLowerCase() + t.slice(1)) || ge(e, dt(t)) || ge(e, t));
}
function il(e) {
  const {
    type: t,
    vnode: s,
    proxy: n,
    withProxy: o,
    propsOptions: [l],
    slots: i,
    attrs: a,
    emit: d,
    render: m,
    renderCache: g,
    props: x,
    data: C,
    setupState: E,
    ctx: U,
    inheritAttrs: A
  } = e, w = Xn(e);
  let H, D;
  try {
    if (s.shapeFlag & 4) {
      const B = o || n, Q = B;
      H = Tt(
        m.call(
          Q,
          B,
          g,
          x,
          E,
          C,
          U
        )
      ), D = a;
    } else {
      const B = t;
      H = Tt(
        B.length > 1 ? B(
          x,
          { attrs: a, slots: i, emit: d }
        ) : B(
          x,
          null
        )
      ), D = t.props ? a : gd(a);
    }
  } catch (B) {
    hn.length = 0, Cn(B, e, 1), H = v($t);
  }
  let K = H;
  if (D && A !== !1) {
    const B = Object.keys(D), { shapeFlag: Q } = K;
    B.length && Q & 7 && (l && B.some(lo) && (D = hd(
      D,
      l
    )), K = fs(K, D, !1, !0));
  }
  return s.dirs && (K = fs(K, null, !1, !0), K.dirs = K.dirs ? K.dirs.concat(s.dirs) : s.dirs), s.transition && gr(K, s.transition), H = K, Xn(w), H;
}
const gd = (e) => {
  let t;
  for (const s in e)
    (s === "class" || s === "style" || ro(s)) && ((t || (t = {}))[s] = e[s]);
  return t;
}, hd = (e, t) => {
  const s = {};
  for (const n in e)
    (!lo(n) || !(n.slice(9) in t)) && (s[n] = e[n]);
  return s;
};
function bd(e, t, s) {
  const { props: n, children: o, component: l } = e, { props: i, children: a, patchFlag: d } = t, m = l.emitsOptions;
  if (t.dirs || t.transition)
    return !0;
  if (s && d >= 0) {
    if (d & 1024)
      return !0;
    if (d & 16)
      return n ? al(n, i, m) : !!i;
    if (d & 8) {
      const g = t.dynamicProps;
      for (let x = 0; x < g.length; x++) {
        const C = g[x];
        if (Ai(i, n, C) && !ho(m, C))
          return !0;
      }
    }
  } else
    return (o || a) && (!a || !a.$stable) ? !0 : n === i ? !1 : n ? i ? al(n, i, m) : !0 : !!i;
  return !1;
}
function al(e, t, s) {
  const n = Object.keys(t);
  if (n.length !== Object.keys(e).length)
    return !0;
  for (let o = 0; o < n.length; o++) {
    const l = n[o];
    if (Ai(t, e, l) && !ho(s, l))
      return !0;
  }
  return !1;
}
function Ai(e, t, s) {
  const n = e[s], o = t[s];
  return s === "style" && ye(n) && ye(o) ? !Xt(n, o) : n !== o;
}
function vd({ vnode: e, parent: t, suspense: s }, n) {
  for (; t; ) {
    const o = t.subTree;
    if (o.suspense && o.suspense.activeBranch === e && (o.suspense.vnode.el = o.el = n, e = o), o === e)
      (e = t.vnode).el = n, t = t.parent;
    else
      break;
  }
  s && s.activeBranch === e && (s.vnode.el = n);
}
const Ei = {}, Ii = () => Object.create(Ei), Ti = (e) => Object.getPrototypeOf(e) === Ei;
function yd(e, t, s, n = !1) {
  const o = {}, l = Ii();
  e.propsDefaults = /* @__PURE__ */ Object.create(null), Pi(e, t, o, l);
  for (const i in e.propsOptions[0])
    i in o || (o[i] = void 0);
  s ? e.props = n ? o : /* @__PURE__ */ Su(o) : e.type.props ? e.props = o : e.props = l, e.attrs = l;
}
function xd(e, t, s, n) {
  const {
    props: o,
    attrs: l,
    vnode: { patchFlag: i }
  } = e, a = /* @__PURE__ */ me(o), [d] = e.propsOptions;
  let m = !1;
  if (
    // always force full diff in dev
    // - #1942 if hmr is enabled with sfc component
    // - vite#872 non-sfc component used by sfc component
    (n || i > 0) && !(i & 16)
  ) {
    if (i & 8) {
      const g = e.vnode.dynamicProps;
      for (let x = 0; x < g.length; x++) {
        let C = g[x];
        if (ho(e.emitsOptions, C))
          continue;
        const E = t[C];
        if (d)
          if (ge(l, C))
            E !== l[C] && (l[C] = E, m = !0);
          else {
            const U = et(C);
            o[U] = Xo(
              d,
              a,
              U,
              E,
              e,
              !1
            );
          }
        else
          E !== l[C] && (l[C] = E, m = !0);
      }
    }
  } else {
    Pi(e, t, o, l) && (m = !0);
    let g;
    for (const x in a)
      (!t || // for camelCase
      !ge(t, x) && // it's possible the original props was passed in as kebab-case
      // and converted to camelCase (#955)
      ((g = dt(x)) === x || !ge(t, g))) && (d ? s && // for camelCase
      (s[x] !== void 0 || // for kebab-case
      s[g] !== void 0) && (o[x] = Xo(
        d,
        a,
        x,
        void 0,
        e,
        !0
      )) : delete o[x]);
    if (l !== a)
      for (const x in l)
        (!t || !ge(t, x)) && (delete l[x], m = !0);
  }
  m && Bt(e.attrs, "set", "");
}
function Pi(e, t, s, n) {
  const [o, l] = e.propsOptions;
  let i = !1, a;
  if (t)
    for (let d in t) {
      if (dn(d))
        continue;
      const m = t[d];
      let g;
      o && ge(o, g = et(d)) ? !l || !l.includes(g) ? s[g] = m : (a || (a = {}))[g] = m : ho(e.emitsOptions, d) || (!(d in n) || m !== n[d]) && (n[d] = m, i = !0);
    }
  if (l) {
    const d = /* @__PURE__ */ me(s), m = a || ke;
    for (let g = 0; g < l.length; g++) {
      const x = l[g];
      s[x] = Xo(
        o,
        d,
        x,
        m[x],
        e,
        !ge(m, x)
      );
    }
  }
  return i;
}
function Xo(e, t, s, n, o, l) {
  const i = e[s];
  if (i != null) {
    const a = ge(i, "default");
    if (a && n === void 0) {
      const d = i.default;
      if (i.type !== Function && !i.skipFactory && X(d)) {
        const { propsDefaults: m } = o;
        if (s in m)
          n = m[s];
        else {
          const g = En(o);
          n = m[s] = d.call(
            null,
            t
          ), g();
        }
      } else
        n = d;
      o.ce && o.ce._setProp(s, n);
    }
    i[
      0
      /* shouldCast */
    ] && (l && !a ? n = !1 : i[
      1
      /* shouldCastTrue */
    ] && (n === "" || n === dt(s)) && (n = !0));
  }
  return n;
}
const _d = /* @__PURE__ */ new WeakMap();
function Ri(e, t, s = !1) {
  const n = s ? _d : t.propsCache, o = n.get(e);
  if (o)
    return o;
  const l = e.props, i = {}, a = [];
  let d = !1;
  if (!X(e)) {
    const g = (x) => {
      d = !0;
      const [C, E] = Ri(x, t, !0);
      Le(i, C), E && a.push(...E);
    };
    !s && t.mixins.length && t.mixins.forEach(g), e.extends && g(e.extends), e.mixins && e.mixins.forEach(g);
  }
  if (!l && !d)
    return ye(e) && n.set(e, Ss), Ss;
  if (G(l))
    for (let g = 0; g < l.length; g++) {
      const x = et(l[g]);
      ul(x) && (i[x] = ke);
    }
  else if (l)
    for (const g in l) {
      const x = et(g);
      if (ul(x)) {
        const C = l[g], E = i[x] = G(C) || X(C) ? { type: C } : Le({}, C), U = E.type;
        let A = !1, w = !0;
        if (G(U))
          for (let H = 0; H < U.length; ++H) {
            const D = U[H], K = X(D) && D.name;
            if (K === "Boolean") {
              A = !0;
              break;
            } else K === "String" && (w = !1);
          }
        else
          A = X(U) && U.name === "Boolean";
        E[
          0
          /* shouldCast */
        ] = A, E[
          1
          /* shouldCastTrue */
        ] = w, (A || ge(E, "default")) && a.push(x);
      }
    }
  const m = [i, a];
  return ye(e) && n.set(e, m), m;
}
function ul(e) {
  return e[0] !== "$" && !dn(e);
}
const yr = (e) => e === "_" || e === "_ctx" || e === "$stable", xr = (e) => G(e) ? e.map(Tt) : [Tt(e)], wd = (e, t, s) => {
  if (t._n)
    return t;
  const n = k((...o) => xr(t(...o)), s);
  return n._c = !1, n;
}, Mi = (e, t, s) => {
  const n = e._ctx;
  for (const o in e) {
    if (yr(o)) continue;
    const l = e[o];
    if (X(l))
      t[o] = wd(o, l, n);
    else if (l != null) {
      const i = xr(l);
      t[o] = () => i;
    }
  }
}, Vi = (e, t) => {
  const s = xr(t);
  e.slots.default = () => s;
}, $i = (e, t, s) => {
  for (const n in t)
    (s || !yr(n)) && (e[n] = t[n]);
}, kd = (e, t, s) => {
  const n = e.slots = Ii();
  if (e.vnode.shapeFlag & 32) {
    const o = t._;
    o ? ($i(n, t, s), s && Fl(n, "_", o, !0)) : Mi(t, n);
  } else t && Vi(e, t);
}, Sd = (e, t, s) => {
  const { vnode: n, slots: o } = e;
  let l = !0, i = ke;
  if (n.shapeFlag & 32) {
    const a = t._;
    a ? s && a === 1 ? l = !1 : $i(o, t, s) : (l = !t.$stable, Mi(t, o)), i = t;
  } else t && (Vi(e, t), i = { default: 1 });
  if (l)
    for (const a in o)
      !yr(a) && i[a] == null && delete o[a];
}, at = Td;
function Cd(e) {
  return Ad(e);
}
function Ad(e, t) {
  const s = fo();
  s.__VUE__ = !0;
  const {
    insert: n,
    remove: o,
    patchProp: l,
    createElement: i,
    createText: a,
    createComment: d,
    setText: m,
    setElementText: g,
    parentNode: x,
    nextSibling: C,
    setScopeId: E = Rt,
    insertStaticContent: U
  } = e, A = (f, b, _, R = null, I = null, T = null, j = void 0, N = null, O = !!b.dynamicChildren) => {
    if (f === b)
      return;
    f && !tn(f, b) && (R = ms(f), Be(f, I, T, !0), f = null), b.patchFlag === -2 && (O = !1, b.dynamicChildren = null);
    const { type: P, ref: J, shapeFlag: F } = b;
    switch (P) {
      case bo:
        w(f, b, _, R);
        break;
      case $t:
        H(f, b, _, R);
        break;
      case Gn:
        f == null && D(b, _, R, j);
        break;
      case ue:
        re(
          f,
          b,
          _,
          R,
          I,
          T,
          j,
          N,
          O
        );
        break;
      default:
        F & 1 ? Q(
          f,
          b,
          _,
          R,
          I,
          T,
          j,
          N,
          O
        ) : F & 6 ? xe(
          f,
          b,
          _,
          R,
          I,
          T,
          j,
          N,
          O
        ) : (F & 64 || F & 128) && P.process(
          f,
          b,
          _,
          R,
          I,
          T,
          j,
          N,
          O,
          Te
        );
    }
    J != null && I ? mn(J, f && f.ref, T, b || f, !b) : J == null && f && f.ref != null && mn(f.ref, null, T, f, !0);
  }, w = (f, b, _, R) => {
    if (f == null)
      n(
        b.el = a(b.children),
        _,
        R
      );
    else {
      const I = b.el = f.el;
      b.children !== f.children && m(I, b.children);
    }
  }, H = (f, b, _, R) => {
    f == null ? n(
      b.el = d(b.children || ""),
      _,
      R
    ) : b.el = f.el;
  }, D = (f, b, _, R) => {
    [f.el, f.anchor] = U(
      f.children,
      b,
      _,
      R,
      f.el,
      f.anchor
    );
  }, K = ({ el: f, anchor: b }, _, R) => {
    let I;
    for (; f && f !== b; )
      I = C(f), n(f, _, R), f = I;
    n(b, _, R);
  }, B = ({ el: f, anchor: b }) => {
    let _;
    for (; f && f !== b; )
      _ = C(f), o(f), f = _;
    o(b);
  }, Q = (f, b, _, R, I, T, j, N, O) => {
    if (b.type === "svg" ? j = "svg" : b.type === "math" && (j = "mathml"), f == null)
      je(
        b,
        _,
        R,
        I,
        T,
        j,
        N,
        O
      );
    else {
      const P = f.el && f.el._isVueCE ? f.el : null;
      try {
        P && P._beginPatch(), Re(
          f,
          b,
          I,
          T,
          j,
          N,
          O
        );
      } finally {
        P && P._endPatch();
      }
    }
  }, je = (f, b, _, R, I, T, j, N) => {
    let O, P;
    const { props: J, shapeFlag: F, transition: q, dirs: Y } = f;
    if (O = f.el = i(
      f.type,
      T,
      J && J.is,
      J
    ), F & 8 ? g(O, f.children) : F & 16 && te(
      f.children,
      O,
      null,
      R,
      I,
      Uo(f, T),
      j,
      N
    ), Y && ls(f, null, R, "created"), W(O, f, f.scopeId, j, R), J) {
      for (const ae in J)
        ae !== "value" && !dn(ae) && l(O, ae, null, J[ae], T, R);
      "value" in J && l(O, "value", null, J.value, T), (P = J.onVnodeBeforeMount) && At(P, R, f);
    }
    Y && ls(f, null, R, "beforeMount");
    const ie = Ed(I, q);
    ie && q.beforeEnter(O), n(O, b, _), ((P = J && J.onVnodeMounted) || ie || Y) && at(() => {
      try {
        P && At(P, R, f), ie && q.enter(O), Y && ls(f, null, R, "mounted");
      } finally {
      }
    }, I);
  }, W = (f, b, _, R, I) => {
    if (_ && E(f, _), R)
      for (let T = 0; T < R.length; T++)
        E(f, R[T]);
    if (I) {
      let T = I.subTree;
      if (b === T || Li(T.type) && (T.ssContent === b || T.ssFallback === b)) {
        const j = I.vnode;
        W(
          f,
          j,
          j.scopeId,
          j.slotScopeIds,
          I.parent
        );
      }
    }
  }, te = (f, b, _, R, I, T, j, N, O = 0) => {
    for (let P = O; P < f.length; P++) {
      const J = f[P] = N ? Dt(f[P]) : Tt(f[P]);
      A(
        null,
        J,
        b,
        _,
        R,
        I,
        T,
        j,
        N
      );
    }
  }, Re = (f, b, _, R, I, T, j) => {
    const N = b.el = f.el;
    let { patchFlag: O, dynamicChildren: P, dirs: J } = b;
    O |= f.patchFlag & 16;
    const F = f.props || ke, q = b.props || ke;
    let Y;
    if (_ && is(_, !1), (Y = q.onVnodeBeforeUpdate) && At(Y, _, b, f), J && ls(b, f, _, "beforeUpdate"), _ && is(_, !0), // #6385 the old vnode may be a user-wrapped non-isomorphic block
    // Force full diff when block metadata is unstable.
    P && (!f.dynamicChildren || f.dynamicChildren.length !== P.length) && (O = 0, j = !1, P = null), (F.innerHTML && q.innerHTML == null || F.textContent && q.textContent == null) && g(N, ""), P ? _e(
      f.dynamicChildren,
      P,
      N,
      _,
      R,
      Uo(b, I),
      T
    ) : j || se(
      f,
      b,
      N,
      null,
      _,
      R,
      Uo(b, I),
      T,
      !1
    ), O > 0) {
      if (O & 16)
        $e(N, F, q, _, I);
      else if (O & 2 && F.class !== q.class && l(N, "class", null, q.class, I), O & 4 && l(N, "style", F.style, q.style, I), O & 8) {
        const ie = b.dynamicProps;
        for (let ae = 0; ae < ie.length; ae++) {
          const le = ie[ae], Se = F[le], Ae = q[le];
          (Ae !== Se || le === "value") && l(N, le, Se, Ae, I, _);
        }
      }
      O & 1 && f.children !== b.children && g(N, b.children);
    } else !j && P == null && $e(N, F, q, _, I);
    ((Y = q.onVnodeUpdated) || J) && at(() => {
      Y && At(Y, _, b, f), J && ls(b, f, _, "updated");
    }, R);
  }, _e = (f, b, _, R, I, T, j) => {
    for (let N = 0; N < b.length; N++) {
      const O = f[N], P = b[N], J = (
        // oldVNode may be an errored async setup() component inside Suspense
        // which will not have a mounted element
        O.el && // - In the case of a Fragment, we need to provide the actual parent
        // of the Fragment itself so it can move its children.
        (O.type === ue || // - In the case of different nodes, there is going to be a replacement
        // which also requires the correct parent container
        !tn(O, P) || // - In the case of a component, it could contain anything.
        O.shapeFlag & 198) ? x(O.el) : (
          // In other cases, the parent container is not actually used so we
          // just pass the block element here to avoid a DOM parentNode call.
          _
        )
      );
      A(
        O,
        P,
        J,
        null,
        R,
        I,
        T,
        j,
        !0
      );
    }
  }, $e = (f, b, _, R, I) => {
    if (b !== _) {
      if (b !== ke)
        for (const T in b)
          !dn(T) && !(T in _) && l(
            f,
            T,
            b[T],
            null,
            I,
            R
          );
      for (const T in _) {
        if (dn(T)) continue;
        const j = _[T], N = b[T];
        j !== N && T !== "value" && l(f, T, N, j, I, R);
      }
      "value" in _ && l(f, "value", b.value, _.value, I);
    }
  }, re = (f, b, _, R, I, T, j, N, O) => {
    const P = b.el = f ? f.el : a(""), J = b.anchor = f ? f.anchor : a("");
    let { patchFlag: F, dynamicChildren: q, slotScopeIds: Y } = b;
    Y && (N = N ? N.concat(Y) : Y), f == null ? (n(P, _, R), n(J, _, R), te(
      // #10007
      // such fragment like `<></>` will be compiled into
      // a fragment which doesn't have a children.
      // In this case fallback to an empty array
      b.children || [],
      _,
      J,
      I,
      T,
      j,
      N,
      O
    )) : F > 0 && F & 64 && q && // #2715 the previous fragment could've been a BAILed one as a result
    // of renderSlot() with no valid children
    f.dynamicChildren && f.dynamicChildren.length === q.length ? (_e(
      f.dynamicChildren,
      q,
      _,
      I,
      T,
      j,
      N
    ), // #2080 if the stable fragment has a key, it's a <template v-for> that may
    //  get moved around. Make sure all root level vnodes inherit el.
    // #2134 or if it's a component root, it may also get moved around
    // as the component is being moved.
    (b.key != null || I && b === I.subTree) && Oi(
      f,
      b,
      !0
      /* shallow */
    )) : se(
      f,
      b,
      _,
      J,
      I,
      T,
      j,
      N,
      O
    );
  }, xe = (f, b, _, R, I, T, j, N, O) => {
    b.slotScopeIds = N, f == null ? b.shapeFlag & 512 ? I.ctx.activate(
      b,
      _,
      R,
      j,
      O
    ) : He(
      b,
      _,
      R,
      I,
      T,
      j,
      O
    ) : bt(f, b, O);
  }, He = (f, b, _, R, I, T, j) => {
    const N = f.component = jd(
      f,
      R,
      I
    );
    if (br(f) && (N.ctx.renderer = Te), Nd(N, !1, j), N.asyncDep) {
      if (I && I.registerDep(N, we, j), !f.el) {
        const O = N.subTree = v($t);
        H(null, O, b, _), f.placeholder = O.el;
      }
    } else
      we(
        N,
        f,
        b,
        _,
        I,
        T,
        j
      );
  }, bt = (f, b, _) => {
    const R = b.component = f.component;
    if (bd(f, b, _))
      if (R.asyncDep && !R.asyncResolved) {
        fe(R, b, _);
        return;
      } else
        R.next = b, R.update();
    else
      b.el = f.el, R.vnode = b;
  }, we = (f, b, _, R, I, T, j) => {
    const N = () => {
      if (f.isMounted) {
        let { next: F, bu: q, u: Y, parent: ie, vnode: ae } = f;
        {
          const Ge = ji(f);
          if (Ge) {
            F && (F.el = ae.el, fe(f, F, j)), Ge.asyncDep.then(() => {
              at(() => {
                f.isUnmounted || P();
              }, I);
            });
            return;
          }
        }
        let le = F, Se;
        is(f, !1), F ? (F.el = ae.el, fe(f, F, j)) : F = ae, q && qn(q), (Se = F.props && F.props.onVnodeBeforeUpdate) && At(Se, ie, F, ae), is(f, !0);
        const Ae = il(f), tt = f.subTree;
        f.subTree = Ae, A(
          tt,
          Ae,
          // parent may have changed if it's in a teleport
          x(tt.el),
          // anchor may have changed if it's in a fragment
          ms(tt),
          f,
          I,
          T
        ), F.el = Ae.el, le === null && vd(f, Ae.el), Y && at(Y, I), (Se = F.props && F.props.onVnodeUpdated) && at(
          () => At(Se, ie, F, ae),
          I
        );
      } else {
        let F;
        const { el: q, props: Y } = b, { bm: ie, m: ae, parent: le, root: Se, type: Ae } = f, tt = Es(b);
        is(f, !1), ie && qn(ie), !tt && (F = Y && Y.onVnodeBeforeMount) && At(F, le, b), is(f, !0);
        {
          Se.ce && Se.ce._hasShadowRoot() && Se.ce._injectChildStyle(
            Ae,
            f.parent ? f.parent.type : void 0
          );
          const Ge = f.subTree = il(f);
          A(
            null,
            Ge,
            _,
            R,
            f,
            I,
            T
          ), b.el = Ge.el;
        }
        if (ae && at(ae, I), !tt && (F = Y && Y.onVnodeMounted)) {
          const Ge = b;
          at(
            () => At(F, le, Ge),
            I
          );
        }
        (b.shapeFlag & 256 || le && Es(le.vnode) && le.vnode.shapeFlag & 256) && f.a && at(f.a, I), f.isMounted = !0, b = _ = R = null;
      }
    };
    f.scope.on();
    const O = f.effect = new Kl(N);
    f.scope.off();
    const P = f.update = O.run.bind(O), J = f.job = O.runIfDirty.bind(O);
    J.i = f, J.id = f.uid, O.scheduler = () => pr(J), is(f, !0), P();
  }, fe = (f, b, _) => {
    b.component = f;
    const R = f.vnode.props;
    f.vnode = b, f.next = null, xd(f, b.props, R, _), Sd(f, b.children, _), Mt(), Xr(f), Vt();
  }, se = (f, b, _, R, I, T, j, N, O = !1) => {
    const P = f && f.children, J = f ? f.shapeFlag : 0, F = b.children, { patchFlag: q, shapeFlag: Y } = b;
    if (q > 0) {
      if (q & 128) {
        De(
          P,
          F,
          _,
          R,
          I,
          T,
          j,
          N,
          O
        );
        return;
      } else if (q & 256) {
        Me(
          P,
          F,
          _,
          R,
          I,
          T,
          j,
          N,
          O
        );
        return;
      }
    }
    Y & 8 ? (J & 16 && _t(P, I, T), F !== P && g(_, F)) : J & 16 ? Y & 16 ? De(
      P,
      F,
      _,
      R,
      I,
      T,
      j,
      N,
      O
    ) : _t(P, I, T, !0) : (J & 8 && g(_, ""), Y & 16 && te(
      F,
      _,
      R,
      I,
      T,
      j,
      N,
      O
    ));
  }, Me = (f, b, _, R, I, T, j, N, O) => {
    f = f || Ss, b = b || Ss;
    const P = f.length, J = b.length, F = Math.min(P, J);
    let q;
    for (q = 0; q < F; q++) {
      const Y = b[q] = O ? Dt(b[q]) : Tt(b[q]);
      A(
        f[q],
        Y,
        _,
        null,
        I,
        T,
        j,
        N,
        O
      );
    }
    P > J ? _t(
      f,
      I,
      T,
      !0,
      !1,
      F
    ) : te(
      b,
      _,
      R,
      I,
      T,
      j,
      N,
      O,
      F
    );
  }, De = (f, b, _, R, I, T, j, N, O) => {
    let P = 0;
    const J = b.length;
    let F = f.length - 1, q = J - 1;
    for (; P <= F && P <= q; ) {
      const Y = f[P], ie = b[P] = O ? Dt(b[P]) : Tt(b[P]);
      if (tn(Y, ie))
        A(
          Y,
          ie,
          _,
          null,
          I,
          T,
          j,
          N,
          O
        );
      else
        break;
      P++;
    }
    for (; P <= F && P <= q; ) {
      const Y = f[F], ie = b[q] = O ? Dt(b[q]) : Tt(b[q]);
      if (tn(Y, ie))
        A(
          Y,
          ie,
          _,
          null,
          I,
          T,
          j,
          N,
          O
        );
      else
        break;
      F--, q--;
    }
    if (P > F) {
      if (P <= q) {
        const Y = q + 1, ie = Y < J ? b[Y].el : R;
        for (; P <= q; )
          A(
            null,
            b[P] = O ? Dt(b[P]) : Tt(b[P]),
            _,
            ie,
            I,
            T,
            j,
            N,
            O
          ), P++;
      }
    } else if (P > q)
      for (; P <= F; )
        Be(f[P], I, T, !0), P++;
    else {
      const Y = P, ie = P, ae = /* @__PURE__ */ new Map();
      for (P = ie; P <= q; P++) {
        const st = b[P] = O ? Dt(b[P]) : Tt(b[P]);
        st.key != null && ae.set(st.key, P);
      }
      let le, Se = 0;
      const Ae = q - ie + 1;
      let tt = !1, Ge = 0;
      const qt = new Array(Ae);
      for (P = 0; P < Ae; P++) qt[P] = 0;
      for (P = Y; P <= F; P++) {
        const st = f[P];
        if (Se >= Ae) {
          Be(st, I, T, !0);
          continue;
        }
        let We;
        if (st.key != null)
          We = ae.get(st.key);
        else
          for (le = ie; le <= q; le++)
            if (qt[le - ie] === 0 && tn(st, b[le])) {
              We = le;
              break;
            }
        We === void 0 ? Be(st, I, T, !0) : (qt[We - ie] = P + 1, We >= Ge ? Ge = We : tt = !0, A(
          st,
          b[We],
          _,
          null,
          I,
          T,
          j,
          N,
          O
        ), Se++);
      }
      const ns = tt ? Id(qt) : Ss;
      for (le = ns.length - 1, P = Ae - 1; P >= 0; P--) {
        const st = ie + P, We = b[st], wt = b[st + 1], ut = st + 1 < J ? (
          // #13559, #14173 fallback to el placeholder for unresolved async component
          wt.el || Ni(wt)
        ) : R;
        qt[P] === 0 ? A(
          null,
          We,
          _,
          ut,
          I,
          T,
          j,
          N,
          O
        ) : tt && (le < 0 || P !== ns[le] ? ze(We, _, ut, 2) : le--);
      }
    }
  }, ze = (f, b, _, R, I = null) => {
    const { el: T, type: j, transition: N, children: O, shapeFlag: P } = f;
    if (P & 6) {
      ze(f.component.subTree, b, _, R);
      return;
    }
    if (P & 128) {
      f.suspense.move(b, _, R);
      return;
    }
    if (P & 64) {
      j.move(f, b, _, Te);
      return;
    }
    if (j === ue) {
      n(T, b, _);
      for (let F = 0; F < O.length; F++)
        ze(O[F], b, _, R);
      n(f.anchor, b, _);
      return;
    }
    if (j === Gn) {
      K(f, b, _);
      return;
    }
    if (R !== 2 && P & 1 && N)
      if (R === 0)
        N.persisted && !T[No] ? n(T, b, _) : (N.beforeEnter(T), n(T, b, _), at(() => N.enter(T), I));
      else {
        const { leave: F, delayLeave: q, afterLeave: Y } = N, ie = () => {
          f.ctx.isUnmounted ? o(T) : n(T, b, _);
        }, ae = () => {
          const le = T._isLeaving || !!T[No];
          T._isLeaving && T[No](
            !0
            /* cancelled */
          ), N.persisted && !le ? ie() : F(T, () => {
            ie(), Y && Y();
          });
        };
        q ? q(T, ie, ae) : ae();
      }
    else
      n(T, b, _);
  }, Be = (f, b, _, R = !1, I = !1) => {
    const {
      type: T,
      props: j,
      ref: N,
      children: O,
      dynamicChildren: P,
      shapeFlag: J,
      patchFlag: F,
      dirs: q,
      cacheIndex: Y,
      memo: ie
    } = f;
    if (F === -2 && (I = !1), N != null && (Mt(), mn(N, null, _, f, !0), Vt()), Y != null && (b.renderCache[Y] = void 0), J & 256) {
      b.ctx.deactivate(f);
      return;
    }
    const ae = J & 1 && q, le = !Es(f);
    let Se;
    if (le && (Se = j && j.onVnodeBeforeUnmount) && At(Se, b, f), J & 6)
      xo(f.component, _, R);
    else {
      if (J & 128) {
        f.suspense.unmount(_, R);
        return;
      }
      ae && ls(f, null, b, "beforeUnmount"), J & 64 ? f.type.remove(
        f,
        b,
        _,
        Te,
        R
      ) : P && // #5154
      // when v-once is used inside a block, setBlockTracking(-1) marks the
      // parent block with hasOnce: true
      // so that it doesn't take the fast path during unmount - otherwise
      // components nested in v-once are never unmounted.
      !P.hasOnce && // #1153: fast path should not be taken for non-stable (v-for) fragments
      (T !== ue || F > 0 && F & 64) ? _t(
        P,
        b,
        _,
        !1,
        !0
      ) : (T === ue && F & 384 || !I && J & 16) && _t(O, b, _), R && In(f);
    }
    const Ae = ie != null && Y == null;
    (le && (Se = j && j.onVnodeUnmounted) || ae || Ae) && at(() => {
      Se && At(Se, b, f), ae && ls(f, null, b, "unmounted"), Ae && (f.el = null);
    }, _);
  }, In = (f) => {
    const { type: b, el: _, anchor: R, transition: I } = f;
    if (b === ue) {
      Tn(_, R);
      return;
    }
    if (b === Gn) {
      B(f);
      return;
    }
    const T = () => {
      o(_), I && !I.persisted && I.afterLeave && I.afterLeave();
    };
    if (f.shapeFlag & 1 && I && !I.persisted) {
      const { leave: j, delayLeave: N } = I, O = () => j(_, T);
      N ? N(f.el, T, O) : O();
    } else
      T();
  }, Tn = (f, b) => {
    let _;
    for (; f !== b; )
      _ = C(f), o(f), f = _;
    o(b);
  }, xo = (f, b, _) => {
    const { bum: R, scope: I, job: T, subTree: j, um: N, m: O, a: P } = f;
    dl(O), dl(P), R && qn(R), I.stop(), T && (T.flags |= 8, Be(j, f, b, _)), N && at(N, b), at(() => {
      f.isUnmounted = !0;
    }, b);
  }, _t = (f, b, _, R = !1, I = !1, T = 0) => {
    for (let j = T; j < f.length; j++)
      Be(f[j], b, _, R, I);
  }, ms = (f) => {
    if (f.shapeFlag & 6)
      return ms(f.component.subTree);
    if (f.shapeFlag & 128)
      return f.suspense.next();
    const b = C(f.anchor || f.el), _ = b && b[zu];
    return _ ? C(_) : b;
  };
  let Os = !1;
  const de = (f, b, _) => {
    let R;
    f == null ? b._vnode && (Be(b._vnode, null, null, !0), R = b._vnode.component) : A(
      b._vnode || null,
      f,
      b,
      null,
      null,
      null,
      _
    ), b._vnode = f, Os || (Os = !0, Xr(R), ci(), Os = !1);
  }, Te = {
    p: A,
    um: Be,
    m: ze,
    r: In,
    mt: He,
    mc: te,
    pc: se,
    pbc: _e,
    n: ms,
    o: e
  };
  return {
    render: de,
    hydrate: void 0,
    createApp: cd(de)
  };
}
function Uo({ type: e, props: t }, s) {
  return s === "svg" && e === "foreignObject" || s === "mathml" && e === "annotation-xml" && t && t.encoding && t.encoding.includes("html") ? void 0 : s;
}
function is({ effect: e, job: t }, s) {
  s ? (e.flags |= 32, t.flags |= 4) : (e.flags &= -33, t.flags &= -5);
}
function Ed(e, t) {
  return (!e || e && !e.pendingBranch) && t && !t.persisted;
}
function Oi(e, t, s = !1) {
  const n = e.children, o = t.children;
  if (G(n) && G(o))
    for (let l = 0; l < n.length; l++) {
      const i = n[l];
      let a = o[l];
      a.shapeFlag & 1 && !a.dynamicChildren && ((a.patchFlag <= 0 || a.patchFlag === 32) && (a = o[l] = Dt(o[l]), a.el = i.el), !s && a.patchFlag !== -2 && Oi(i, a)), a.type === bo && (a.patchFlag === -1 && (a = o[l] = Dt(a)), a.el = i.el), a.type === $t && !a.el && (a.el = i.el);
    }
}
function Id(e) {
  const t = e.slice(), s = [0];
  let n, o, l, i, a;
  const d = e.length;
  for (n = 0; n < d; n++) {
    const m = e[n];
    if (m !== 0) {
      if (o = s[s.length - 1], e[o] < m) {
        t[n] = o, s.push(n);
        continue;
      }
      for (l = 0, i = s.length - 1; l < i; )
        a = l + i >> 1, e[s[a]] < m ? l = a + 1 : i = a;
      m < e[s[l]] && (l > 0 && (t[n] = s[l - 1]), s[l] = n);
    }
  }
  for (l = s.length, i = s[l - 1]; l-- > 0; )
    s[l] = i, i = t[i];
  return s;
}
function ji(e) {
  const t = e.subTree.component;
  if (t)
    return t.asyncDep && !t.asyncResolved ? t : ji(t);
}
function dl(e) {
  if (e)
    for (let t = 0; t < e.length; t++)
      e[t].flags |= 8;
}
function Ni(e) {
  if (e.placeholder)
    return e.placeholder;
  const t = e.component;
  return t ? Ni(t.subTree) : null;
}
const Li = (e) => e.__isSuspense;
function Td(e, t) {
  t && t.pendingBranch ? G(e) ? t.effects.push(...e) : t.effects.push(e) : Du(e);
}
const ue = /* @__PURE__ */ Symbol.for("v-fgt"), bo = /* @__PURE__ */ Symbol.for("v-txt"), $t = /* @__PURE__ */ Symbol.for("v-cmt"), Gn = /* @__PURE__ */ Symbol.for("v-stc"), hn = [];
let ct = null;
function S(e = !1) {
  hn.push(ct = e ? null : []);
}
function Pd() {
  hn.pop(), ct = hn[hn.length - 1] || null;
}
let _n = 1;
function so(e, t = !1) {
  _n += e, e < 0 && ct && t && (ct.hasOnce = !0);
}
function Ui(e) {
  return e.dynamicChildren = _n > 0 ? ct || Ss : null, Pd(), _n > 0 && ct && ct.push(e), e;
}
function M(e, t, s, n, o, l) {
  return Ui(
    p(
      e,
      t,
      s,
      n,
      o,
      l,
      !0
    )
  );
}
function Ie(e, t, s, n, o) {
  return Ui(
    v(
      e,
      t,
      s,
      n,
      o,
      !0
    )
  );
}
function wn(e) {
  return e ? e.__v_isVNode === !0 : !1;
}
function tn(e, t) {
  return e.type === t.type && e.key === t.key;
}
const Di = ({ key: e }) => e ?? null, Jn = ({
  ref: e,
  ref_key: t,
  ref_for: s
}) => (typeof e == "number" && (e = "" + e), e != null ? Ve(e) || /* @__PURE__ */ Ue(e) || X(e) ? { i: Xe, r: e, k: t, f: !!s } : e : null);
function p(e, t = null, s = null, n = 0, o = null, l = e === ue ? 0 : 1, i = !1, a = !1) {
  const d = {
    __v_isVNode: !0,
    __v_skip: !0,
    type: e,
    props: t,
    key: t && Di(t),
    ref: t && Jn(t),
    scopeId: pi,
    slotScopeIds: null,
    children: s,
    component: null,
    suspense: null,
    ssContent: null,
    ssFallback: null,
    dirs: null,
    transition: null,
    el: null,
    anchor: null,
    target: null,
    targetStart: null,
    targetAnchor: null,
    staticCount: 0,
    shapeFlag: l,
    patchFlag: n,
    dynamicProps: o,
    dynamicChildren: null,
    appContext: null,
    ctx: Xe
  };
  return a ? (no(d, s), l & 128 && e.normalize(d)) : s && (d.shapeFlag |= Ve(s) ? 8 : 16), _n > 0 && // avoid a block node from tracking itself
  !i && // has current parent block
  ct && // presence of a patch flag indicates this node needs patching on updates.
  // component nodes also should always be patched, because even if the
  // component doesn't need to update, it needs to persist the instance on to
  // the next vnode so that it can be properly unmounted later.
  (d.patchFlag > 0 || l & 6) && // the EVENTS flag is only for hydration and if it is the only flag, the
  // vnode should not be considered dynamic due to handler caching.
  d.patchFlag !== 32 && ct.push(d), d;
}
const v = Rd;
function Rd(e, t = null, s = null, n = 0, o = null, l = !1) {
  if ((!e || e === nd) && (e = $t), wn(e)) {
    const a = fs(
      e,
      t,
      !0
      /* mergeRef: true */
    );
    return s && no(a, s), _n > 0 && !l && ct && (a.shapeFlag & 6 ? ct[ct.indexOf(e)] = a : ct.push(a)), a.patchFlag = -2, a;
  }
  if (Bd(e) && (e = e.__vccOpts), t) {
    t = Md(t);
    let { class: a, style: d } = t;
    a && !Ve(a) && (t.class = ot(a)), ye(d) && (/* @__PURE__ */ mo(d) && !G(d) && (d = Le({}, d)), t.style = bn(d));
  }
  const i = Ve(e) ? 1 : Li(e) ? 128 : Wu(e) ? 64 : ye(e) ? 4 : X(e) ? 2 : 0;
  return p(
    e,
    t,
    s,
    n,
    o,
    i,
    l,
    !0
  );
}
function Md(e) {
  return e ? /* @__PURE__ */ mo(e) || Ti(e) ? Le({}, e) : e : null;
}
function fs(e, t, s = !1, n = !1) {
  const { props: o, ref: l, patchFlag: i, children: a, transition: d } = e, m = t ? es(o || {}, t) : o, g = {
    __v_isVNode: !0,
    __v_skip: !0,
    type: e.type,
    props: m,
    key: m && Di(m),
    ref: t && t.ref ? (
      // #2078 in the case of <component :is="vnode" ref="extra"/>
      // if the vnode itself already has a ref, cloneVNode will need to merge
      // the refs so the single vnode can be set on multiple refs
      s && l ? G(l) ? l.concat(Jn(t)) : [l, Jn(t)] : Jn(t)
    ) : l,
    scopeId: e.scopeId,
    slotScopeIds: e.slotScopeIds,
    children: a,
    target: e.target,
    targetStart: e.targetStart,
    targetAnchor: e.targetAnchor,
    staticCount: e.staticCount,
    shapeFlag: e.shapeFlag,
    // if the vnode is cloned with extra props, we can no longer assume its
    // existing patch flag to be reliable and need to add the FULL_PROPS flag.
    // note: preserve flag for fragments since they use the flag for children
    // fast paths only.
    patchFlag: t && e.type !== ue ? i === -1 ? 16 : i | 16 : i,
    dynamicProps: e.dynamicProps,
    dynamicChildren: e.dynamicChildren,
    appContext: e.appContext,
    dirs: e.dirs,
    transition: d,
    // These should technically only be non-null on mounted VNodes. However,
    // they *should* be copied for kept-alive vnodes. So we just always copy
    // them since them being non-null during a mount doesn't affect the logic as
    // they will simply be overwritten.
    component: e.component,
    suspense: e.suspense,
    ssContent: e.ssContent && fs(e.ssContent),
    ssFallback: e.ssFallback && fs(e.ssFallback),
    placeholder: e.placeholder,
    el: e.el,
    anchor: e.anchor,
    ctx: e.ctx,
    ce: e.ce
  };
  return d && n && gr(
    g,
    d.clone(g)
  ), g;
}
function y(e = " ", t = 0) {
  return v(bo, null, e, t);
}
function Vd(e, t) {
  const s = v(Gn, null, e);
  return s.staticCount = t, s;
}
function z(e = "", t = !1) {
  return t ? (S(), Ie($t, null, e)) : v($t, null, e);
}
function Tt(e) {
  return e == null || typeof e == "boolean" ? v($t) : G(e) ? v(
    ue,
    null,
    // #3666, avoid reference pollution when reusing vnode
    e.slice()
  ) : wn(e) ? Dt(e) : v(bo, null, String(e));
}
function Dt(e) {
  return e.el === null && e.patchFlag !== -1 || e.memo ? e : fs(e);
}
function no(e, t) {
  let s = 0;
  const { shapeFlag: n } = e;
  if (t == null)
    t = null;
  else if (G(t))
    s = 16;
  else if (typeof t == "object")
    if (n & 65) {
      const o = t.default;
      o && (o._c && (o._d = !1), no(e, o()), o._c && (o._d = !0));
      return;
    } else {
      s = 32;
      const o = t._;
      !o && !Ti(t) ? t._ctx = Xe : o === 3 && Xe && (Xe.slots._ === 1 ? t._ = 1 : (t._ = 2, e.patchFlag |= 1024));
    }
  else if (X(t)) {
    if (n & 65) {
      no(e, { default: t });
      return;
    }
    t = { default: t, _ctx: Xe }, s = 32;
  } else
    t = String(t), n & 64 ? (s = 16, t = [y(t)]) : s = 8;
  e.children = t, e.shapeFlag |= s;
}
function es(...e) {
  const t = {};
  for (let s = 0; s < e.length; s++) {
    const n = e[s];
    for (const o in n)
      if (o === "class")
        t.class !== n.class && (t.class = ot([t.class, n.class]));
      else if (o === "style")
        t.style = bn([t.style, n.style]);
      else if (ro(o)) {
        const l = t[o], i = n[o];
        i && l !== i && !(G(l) && l.includes(i)) ? t[o] = l ? [].concat(l, i) : i : i == null && l == null && // mergeProps({ 'onUpdate:modelValue': undefined }) should not retain
        // the model listener.
        !lo(o) && (t[o] = i);
      } else o !== "" && (t[o] = n[o]);
  }
  return t;
}
function At(e, t, s, n = null) {
  xt(e, t, 7, [
    s,
    n
  ]);
}
const $d = Si();
let Od = 0;
function jd(e, t, s) {
  const n = e.type, o = (t ? t.appContext : e.appContext) || $d, l = {
    uid: Od++,
    vnode: e,
    type: n,
    parent: t,
    appContext: o,
    root: null,
    // to be immediately set
    next: null,
    subTree: null,
    // will be set synchronously right after creation
    effect: null,
    update: null,
    // will be set synchronously right after creation
    job: null,
    scope: new ou(
      !0
      /* detached */
    ),
    render: null,
    proxy: null,
    exposed: null,
    exposeProxy: null,
    withProxy: null,
    provides: t ? t.provides : Object.create(o.provides),
    ids: t ? t.ids : ["", 0, 0],
    accessCache: null,
    renderCache: [],
    // local resolved assets
    components: null,
    directives: null,
    // resolved props and emits options
    propsOptions: Ri(n, o),
    emitsOptions: Ci(n, o),
    // emit
    emit: null,
    // to be set immediately
    emitted: null,
    // props default value
    propsDefaults: ke,
    // inheritAttrs
    inheritAttrs: n.inheritAttrs,
    // state
    ctx: ke,
    data: ke,
    props: ke,
    attrs: ke,
    slots: ke,
    refs: ke,
    setupState: ke,
    setupContext: null,
    // suspense related
    suspense: s,
    suspenseId: s ? s.pendingId : 0,
    asyncDep: null,
    asyncResolved: !1,
    // lifecycle hooks
    // not using enums here because it results in computed properties
    isMounted: !1,
    isUnmounted: !1,
    isDeactivated: !1,
    bc: null,
    c: null,
    bm: null,
    m: null,
    bu: null,
    u: null,
    um: null,
    bum: null,
    da: null,
    a: null,
    rtg: null,
    rtc: null,
    ec: null,
    sp: null
  };
  return l.ctx = { _: l }, l.root = t ? t.root : l, l.emit = pd.bind(null, l), e.ce && e.ce(l), l;
}
let Ze = null;
const ps = () => Ze || Xe;
let oo, er;
{
  const e = fo(), t = (s, n) => {
    let o;
    return (o = e[s]) || (o = e[s] = []), o.push(n), (l) => {
      o.length > 1 ? o.forEach((i) => i(l)) : o[0](l);
    };
  };
  oo = t(
    "__VUE_INSTANCE_SETTERS__",
    (s) => Ze = s
  ), er = t(
    "__VUE_SSR_SETTERS__",
    (s) => Rs = s
  );
}
const En = (e) => {
  const t = Ze;
  return oo(e), e.scope.on(), () => {
    e.scope.off(), oo(t);
  };
}, cl = () => {
  Ze && Ze.scope.off(), oo(null);
};
function Bi(e) {
  return e.vnode.shapeFlag & 4;
}
let Rs = !1;
function Nd(e, t = !1, s = !1) {
  t && er(t);
  const { props: n, children: o } = e.vnode, l = Bi(e);
  yd(e, n, l, t), kd(e, o, s || t);
  const i = l ? Ld(e, t) : void 0;
  return t && er(!1), i;
}
function Ld(e, t) {
  const s = e.type;
  e.accessCache = /* @__PURE__ */ Object.create(null), e.proxy = new Proxy(e.ctx, od);
  const { setup: n } = s;
  if (n) {
    Mt();
    const o = e.setupContext = n.length > 1 ? Dd(e) : null, l = En(e), i = Sn(
      n,
      e,
      0,
      [
        e.props,
        o
      ]
    ), a = Ul(i);
    if (Vt(), l(), (a || e.sp) && !Es(e) && hr(e), a) {
      if (i.then(cl, cl), t)
        return i.then((d) => {
          fl(e, d);
        }).catch((d) => {
          Cn(d, e, 0);
        });
      e.asyncDep = i;
    } else
      fl(e, i);
  } else
    Fi(e);
}
function fl(e, t, s) {
  X(t) ? e.type.__ssrInlineRender ? e.ssrRender = t : e.render = t : ye(t) && (e.setupState = ii(t)), Fi(e);
}
function Fi(e, t, s) {
  const n = e.type;
  e.render || (e.render = n.render || Rt);
  {
    const o = En(e);
    Mt();
    try {
      rd(e);
    } finally {
      Vt(), o();
    }
  }
}
const Ud = {
  get(e, t) {
    return Qe(e, "get", ""), e[t];
  }
};
function Dd(e) {
  const t = (s) => {
    e.exposed = s || {};
  };
  return {
    attrs: new Proxy(e.attrs, Ud),
    slots: e.slots,
    emit: e.emit,
    expose: t
  };
}
function vo(e) {
  return e.exposed ? e.exposeProxy || (e.exposeProxy = new Proxy(ii(Cu(e.exposed)), {
    get(t, s) {
      if (s in t)
        return t[s];
      if (s in gn)
        return gn[s](e);
    },
    has(t, s) {
      return s in t || s in gn;
    }
  })) : e.proxy;
}
function Bd(e) {
  return X(e) && "__vccOpts" in e;
}
const he = (e, t) => /* @__PURE__ */ Ou(e, t, Rs);
function Do(e, t, s) {
  try {
    so(-1);
    const n = arguments.length;
    return n === 2 ? ye(t) && !G(t) ? wn(t) ? v(e, null, [t]) : v(e, t) : v(e, null, t) : (n > 3 ? s = Array.prototype.slice.call(arguments, 2) : n === 3 && wn(s) && (s = [s]), v(e, t, s));
  } finally {
    so(1);
  }
}
const Fd = "3.5.39";
/**
* @vue/runtime-dom v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
let tr;
const pl = typeof window < "u" && window.trustedTypes;
if (pl)
  try {
    tr = /* @__PURE__ */ pl.createPolicy("vue", {
      createHTML: (e) => e
    });
  } catch {
  }
const Hi = tr ? (e) => tr.createHTML(e) : (e) => e, Hd = "http://www.w3.org/2000/svg", zd = "http://www.w3.org/1998/Math/MathML", Ut = typeof document < "u" ? document : null, ml = Ut && /* @__PURE__ */ Ut.createElement("template"), Wd = {
  insert: (e, t, s) => {
    t.insertBefore(e, s || null);
  },
  remove: (e) => {
    const t = e.parentNode;
    t && t.removeChild(e);
  },
  createElement: (e, t, s, n) => {
    const o = t === "svg" ? Ut.createElementNS(Hd, e) : t === "mathml" ? Ut.createElementNS(zd, e) : s ? Ut.createElement(e, { is: s }) : Ut.createElement(e);
    return e === "select" && n && n.multiple != null && o.setAttribute("multiple", n.multiple), o;
  },
  createText: (e) => Ut.createTextNode(e),
  createComment: (e) => Ut.createComment(e),
  setText: (e, t) => {
    e.nodeValue = t;
  },
  setElementText: (e, t) => {
    e.textContent = t;
  },
  parentNode: (e) => e.parentNode,
  nextSibling: (e) => e.nextSibling,
  querySelector: (e) => Ut.querySelector(e),
  setScopeId(e, t) {
    e.setAttribute(t, "");
  },
  // __UNSAFE__
  // Reason: innerHTML.
  // Static content here can only come from compiled templates.
  // As long as the user only uses trusted templates, this is safe.
  insertStaticContent(e, t, s, n, o, l) {
    const i = s ? s.previousSibling : t.lastChild;
    if (o && (o === l || o.nextSibling))
      for (; t.insertBefore(o.cloneNode(!0), s), !(o === l || !(o = o.nextSibling)); )
        ;
    else {
      ml.innerHTML = Hi(
        n === "svg" ? `<svg>${e}</svg>` : n === "mathml" ? `<math>${e}</math>` : e
      );
      const a = ml.content;
      if (n === "svg" || n === "mathml") {
        const d = a.firstChild;
        for (; d.firstChild; )
          a.appendChild(d.firstChild);
        a.removeChild(d);
      }
      t.insertBefore(a, s);
    }
    return [
      // first
      i ? i.nextSibling : t.firstChild,
      // last
      s ? s.previousSibling : t.lastChild
    ];
  }
}, Kd = /* @__PURE__ */ Symbol("_vtc");
function qd(e, t, s) {
  const n = e[Kd];
  n && (t = (t ? [t, ...n] : [...n]).join(" ")), t == null ? e.removeAttribute("class") : s ? e.setAttribute("class", t) : e.className = t;
}
const gl = /* @__PURE__ */ Symbol("_vod"), Gd = /* @__PURE__ */ Symbol("_vsh"), Jd = /* @__PURE__ */ Symbol(""), Yd = /(?:^|;)\s*display\s*:/;
function Qd(e, t, s) {
  const n = e.style, o = Ve(s);
  let l = !1;
  if (s && !o) {
    if (t)
      if (Ve(t))
        for (const i of t.split(";")) {
          const a = i.slice(0, i.indexOf(":")).trim();
          s[a] == null && ln(n, a, "");
        }
      else
        for (const i in t)
          s[i] == null && ln(n, i, "");
    for (const i in s) {
      i === "display" && (l = !0);
      const a = s[i];
      a != null ? Xd(
        e,
        i,
        !Ve(t) && t ? t[i] : void 0,
        a
      ) || ln(n, i, a) : ln(n, i, "");
    }
  } else if (o) {
    if (t !== s) {
      const i = n[Jd];
      i && (s += ";" + i), n.cssText = s, l = Yd.test(s);
    }
  } else t && e.removeAttribute("style");
  gl in e && (e[gl] = l ? n.display : "", e[Gd] && (n.display = "none"));
}
const hl = /\s*!important$/;
function ln(e, t, s) {
  if (G(s))
    s.forEach((n) => ln(e, t, n));
  else if (s == null && (s = ""), t.startsWith("--"))
    e.setProperty(t, s);
  else {
    const n = Zd(e, t);
    hl.test(s) ? e.setProperty(
      dt(n),
      s.replace(hl, ""),
      "important"
    ) : e[n] = s;
  }
}
const bl = ["Webkit", "Moz", "ms"], Bo = {};
function Zd(e, t) {
  const s = Bo[t];
  if (s)
    return s;
  let n = et(t);
  if (n !== "filter" && n in e)
    return Bo[t] = n;
  n = Bl(n);
  for (let o = 0; o < bl.length; o++) {
    const l = bl[o] + n;
    if (l in e)
      return Bo[t] = l;
  }
  return t;
}
function Xd(e, t, s, n) {
  return e.tagName === "TEXTAREA" && (t === "width" || t === "height") && Ve(n) && s === n;
}
const vl = "http://www.w3.org/1999/xlink";
function yl(e, t, s, n, o, l = su(t)) {
  n && t.startsWith("xlink:") ? s == null ? e.removeAttributeNS(vl, t.slice(6, t.length)) : e.setAttributeNS(vl, t, s) : s == null || l && !Hl(s) ? e.removeAttribute(t) : e.setAttribute(
    t,
    l ? "" : pt(s) ? String(s) : s
  );
}
function xl(e, t, s, n, o) {
  if (t === "innerHTML" || t === "textContent") {
    s != null && (e[t] = t === "innerHTML" ? Hi(s) : s);
    return;
  }
  const l = e.tagName;
  if (t === "value" && l !== "PROGRESS" && // custom elements may use _value internally
  !l.includes("-")) {
    const a = l === "OPTION" ? e.getAttribute("value") || "" : e.value, d = s == null ? (
      // #11647: value should be set as empty string for null and undefined,
      // but <input type="checkbox"> should be set as 'on'.
      e.type === "checkbox" ? "on" : ""
    ) : String(s);
    (a !== d || !("_value" in e)) && (e.value = d), s == null && e.removeAttribute(t), e._value = s;
    return;
  }
  let i = !1;
  if (s === "" || s == null) {
    const a = typeof e[t];
    a === "boolean" ? s = Hl(s) : s == null && a === "string" ? (s = "", i = !0) : a === "number" && (s = 0, i = !0);
  }
  try {
    e[t] = s;
  } catch {
  }
  i && e.removeAttribute(o || t);
}
function Ht(e, t, s, n) {
  e.addEventListener(t, s, n);
}
function ec(e, t, s, n) {
  e.removeEventListener(t, s, n);
}
const _l = /* @__PURE__ */ Symbol("_vei");
function tc(e, t, s, n, o = null) {
  const l = e[_l] || (e[_l] = {}), i = l[t];
  if (n && i)
    i.value = n;
  else {
    const [a, d] = oc(t);
    if (n) {
      const m = l[t] = ic(
        n,
        o
      );
      Ht(e, a, m, d);
    } else i && (ec(e, a, i, d), l[t] = void 0);
  }
}
const sc = /(Once|Passive|Capture)$/, nc = /^on:?(?:Once|Passive|Capture)$/;
function oc(e) {
  let t, s;
  for (; (s = e.match(sc)) && !nc.test(e); )
    t || (t = {}), e = e.slice(0, e.length - s[1].length), t[s[1].toLowerCase()] = !0;
  return [e[2] === ":" ? e.slice(3) : dt(e.slice(2)), t];
}
let Fo = 0;
const rc = /* @__PURE__ */ Promise.resolve(), lc = () => Fo || (rc.then(() => Fo = 0), Fo = Date.now());
function ic(e, t) {
  const s = (n) => {
    if (!n._vts)
      n._vts = Date.now();
    else if (n._vts <= s.attached)
      return;
    const o = s.value;
    if (G(o)) {
      const l = n.stopImmediatePropagation;
      n.stopImmediatePropagation = () => {
        l.call(n), n._stopped = !0;
      };
      const i = o.slice(), a = [n];
      for (let d = 0; d < i.length && !n._stopped; d++) {
        const m = i[d];
        m && xt(
          m,
          t,
          5,
          a
        );
      }
    } else
      xt(
        o,
        t,
        5,
        [n]
      );
  };
  return s.value = e, s.attached = lc(), s;
}
const wl = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && // lowercase letter
e.charCodeAt(2) > 96 && e.charCodeAt(2) < 123, ac = (e, t, s, n, o, l) => {
  const i = o === "svg";
  t === "class" ? qd(e, n, i) : t === "style" ? Qd(e, s, n) : ro(t) ? lo(t) || tc(e, t, s, n, l) : (t[0] === "." ? (t = t.slice(1), !0) : t[0] === "^" ? (t = t.slice(1), !1) : uc(e, t, n, i)) ? (xl(e, t, n), !e.tagName.includes("-") && (t === "value" || t === "checked" || t === "selected") && yl(e, t, n, i, l, t !== "value")) : /* #11081 force set props for possible async custom element */ e._isVueCE && // #12408 check if it's declared prop or it's async custom element
  (dc(e, t) || // @ts-expect-error _def is private
  e._def.__asyncLoader && (/[A-Z]/.test(t) || !Ve(n))) ? xl(e, et(t), n, l, t) : (t === "true-value" ? e._trueValue = n : t === "false-value" && (e._falseValue = n), yl(e, t, n, i));
};
function uc(e, t, s, n) {
  if (n)
    return !!(t === "innerHTML" || t === "textContent" || t in e && wl(t) && X(s));
  if (t === "spellcheck" || t === "draggable" || t === "translate" || t === "autocorrect" || t === "sandbox" && e.tagName === "IFRAME" || t === "form" || t === "list" && e.tagName === "INPUT" || t === "type" && e.tagName === "TEXTAREA")
    return !1;
  if (t === "width" || t === "height") {
    const o = e.tagName;
    if (o === "IMG" || o === "VIDEO" || o === "CANVAS" || o === "SOURCE")
      return !1;
  }
  return wl(t) && Ve(s) ? !1 : t in e;
}
function dc(e, t) {
  const s = (
    // @ts-expect-error _def is private
    e._def.props
  );
  if (!s)
    return !1;
  const n = et(t);
  return Array.isArray(s) ? s.some((o) => et(o) === n) : Object.keys(s).some((o) => et(o) === n);
}
const kl = {};
// @__NO_SIDE_EFFECTS__
function cc(e, t, s) {
  let n = /* @__PURE__ */ qe(e, t);
  io(n) && (n = Le({}, n, t));
  class o extends _r {
    constructor(i) {
      super(n, i, s);
    }
  }
  return o.def = n, o;
}
const fc = typeof HTMLElement < "u" ? HTMLElement : class {
};
class _r extends fc {
  constructor(t, s = {}, n = Tl) {
    super(), this._def = t, this._props = s, this._createApp = n, this._isVueCE = !0, this._instance = null, this._app = null, this._nonce = this._def.nonce, this._connected = !1, this._resolved = !1, this._patching = !1, this._dirty = !1, this._numberProps = null, this._styleChildren = /* @__PURE__ */ new WeakSet(), this._styleAnchors = /* @__PURE__ */ new WeakMap(), this._ob = null, this.shadowRoot && n !== Tl ? this._root = this.shadowRoot : t.shadowRoot !== !1 ? (this.attachShadow(
      Le({}, t.shadowRootOptions, {
        mode: "open"
      })
    ), this._root = this.shadowRoot) : this._root = this;
  }
  connectedCallback() {
    if (!this.isConnected) return;
    !this.shadowRoot && !this._resolved && this._parseSlots(), this._connected = !0;
    let t = this;
    for (; t = t && // #12479 should check assignedSlot first to get correct parent
    (t.assignedSlot || t.parentNode || t.host); )
      if (t instanceof _r) {
        this._parent = t;
        break;
      }
    this._instance || (this._resolved ? this._mount(this._def) : t && t._pendingResolve ? this._pendingResolve = t._pendingResolve.then(() => {
      this._pendingResolve = void 0, this._resolveDef();
    }) : this._resolveDef());
  }
  _setParent(t = this._parent) {
    t && (this._instance.parent = t._instance, this._inheritParentContext(t));
  }
  _inheritParentContext(t = this._parent) {
    t && this._app && Object.setPrototypeOf(
      this._app._context.provides,
      t._instance.provides
    );
  }
  disconnectedCallback() {
    this._connected = !1, An(() => {
      this._connected || (this._ob && (this._ob.disconnect(), this._ob = null), this._app && this._app.unmount(), this._instance && (this._instance.ce = void 0), this._app = this._instance = null, this._teleportTargets && (this._teleportTargets.clear(), this._teleportTargets = void 0));
    });
  }
  _processMutations(t) {
    for (const s of t)
      this._setAttr(s.attributeName);
  }
  /**
   * resolve inner component definition (handle possible async component)
   */
  _resolveDef() {
    if (this._pendingResolve)
      return;
    for (let n = 0; n < this.attributes.length; n++)
      this._setAttr(this.attributes[n].name);
    this._ob = new MutationObserver(this._processMutations.bind(this)), this._ob.observe(this, { attributes: !0 });
    const t = (n, o = !1) => {
      this._resolved = !0, this._pendingResolve = void 0;
      const { props: l, styles: i } = n;
      let a;
      if (l && !G(l))
        for (const d in l) {
          const m = l[d];
          (m === Number || m && m.type === Number) && (d in this._props && (this._props[d] = Jr(this._props[d])), (a || (a = /* @__PURE__ */ Object.create(null)))[et(d)] = !0);
        }
      this._numberProps = a, this._resolveProps(n), this.shadowRoot && this._applyStyles(i), this._mount(n);
    }, s = this._def.__asyncLoader;
    s ? this._pendingResolve = s().then((n) => {
      n.configureApp = this._def.configureApp, t(this._def = n, !0);
    }) : t(this._def);
  }
  _mount(t) {
    this._app = this._createApp(t), this._inheritParentContext(), t.configureApp && t.configureApp(this._app), this._app._ceVNode = this._createVNode(), this._app.mount(this._root);
    const s = this._instance && this._instance.exposed;
    if (s)
      for (const n in s)
        ge(this, n) || Object.defineProperty(this, n, {
          // unwrap ref to be consistent with public instance behavior
          get: () => h(s[n])
        });
  }
  _resolveProps(t) {
    const { props: s } = t, n = G(s) ? s : Object.keys(s || {});
    for (const o of Object.keys(this))
      o[0] !== "_" && n.includes(o) && this._setProp(o, this[o]);
    for (const o of n.map(et))
      Object.defineProperty(this, o, {
        get() {
          return this._getProp(o);
        },
        set(l) {
          this._setProp(o, l, !0, !this._patching);
        }
      });
  }
  _setAttr(t) {
    if (t.startsWith("data-v-")) return;
    const s = this.hasAttribute(t);
    let n = s ? this.getAttribute(t) : kl;
    const o = et(t);
    s && this._numberProps && this._numberProps[o] && (n = Jr(n)), this._setProp(o, n, !1, !0);
  }
  /**
   * @internal
   */
  _getProp(t) {
    return this._props[t];
  }
  /**
   * @internal
   */
  _setProp(t, s, n = !0, o = !1) {
    if (s !== this._props[t] && (this._dirty = !0, s === kl ? delete this._props[t] : (this._props[t] = s, t === "key" && this._app && (this._app._ceVNode.key = s)), o && this._instance && this._update(), n)) {
      const l = this._ob;
      l && (this._processMutations(l.takeRecords()), l.disconnect()), s === !0 ? this.setAttribute(dt(t), "") : typeof s == "string" || typeof s == "number" ? this.setAttribute(dt(t), s + "") : s || this.removeAttribute(dt(t)), l && l.observe(this, { attributes: !0 });
    }
  }
  _update() {
    const t = this._createVNode();
    this._app && (t.appContext = this._app._context), wc(t, this._root);
  }
  _createVNode() {
    const t = {};
    this.shadowRoot || (t.onVnodeMounted = t.onVnodeUpdated = this._renderSlots.bind(this));
    const s = v(this._def, Le(t, this._props));
    return this._instance || (s.ce = (n) => {
      this._instance = n, n.ce = this, n.isCE = !0;
      const o = (l, i) => {
        this.dispatchEvent(
          new CustomEvent(
            l,
            io(i[0]) ? Le({ detail: i }, i[0]) : { detail: i }
          )
        );
      };
      n.emit = (l, ...i) => {
        o(l, i), dt(l) !== l && o(dt(l), i);
      }, this._setParent();
    }), s;
  }
  _applyStyles(t, s, n) {
    if (!t) return;
    if (s) {
      if (s === this._def || this._styleChildren.has(s))
        return;
      this._styleChildren.add(s);
    }
    const o = this._nonce, l = this.shadowRoot, i = n ? this._getStyleAnchor(n) || this._getStyleAnchor(this._def) : this._getRootStyleInsertionAnchor(l);
    let a = null;
    for (let d = t.length - 1; d >= 0; d--) {
      const m = document.createElement("style");
      o && m.setAttribute("nonce", o), m.textContent = t[d], l.insertBefore(m, a || i), a = m, d === 0 && (n || this._styleAnchors.set(this._def, m), s && this._styleAnchors.set(s, m));
    }
  }
  _getStyleAnchor(t) {
    if (!t)
      return null;
    const s = this._styleAnchors.get(t);
    return s && s.parentNode === this.shadowRoot ? s : (s && this._styleAnchors.delete(t), null);
  }
  _getRootStyleInsertionAnchor(t) {
    for (let s = 0; s < t.childNodes.length; s++) {
      const n = t.childNodes[s];
      if (!(n instanceof HTMLStyleElement))
        return n;
    }
    return null;
  }
  /**
   * Only called when shadowRoot is false
   */
  _parseSlots() {
    const t = this._slots = {};
    let s;
    for (; s = this.firstChild; ) {
      const n = s.nodeType === 1 && s.getAttribute("slot") || "default";
      (t[n] || (t[n] = [])).push(s), this.removeChild(s);
    }
  }
  /**
   * Only called when shadowRoot is false
   */
  _renderSlots() {
    const t = this._getSlots(), s = this._instance.type.__scopeId;
    for (let n = 0; n < t.length; n++) {
      const o = t[n], l = o.getAttribute("name") || "default", i = this._slots[l], a = o.parentNode;
      if (i)
        for (const d of i) {
          if (s && d.nodeType === 1) {
            const m = s + "-s", g = document.createTreeWalker(d, 1);
            d.setAttribute(m, "");
            let x;
            for (; x = g.nextNode(); )
              x.setAttribute(m, "");
          }
          a.insertBefore(d, o);
        }
      else
        for (; o.firstChild; ) a.insertBefore(o.firstChild, o);
      a.removeChild(o);
    }
  }
  /**
   * @internal
   */
  _getSlots() {
    const t = [this];
    this._teleportTargets && t.push(...this._teleportTargets);
    const s = /* @__PURE__ */ new Set();
    for (const n of t) {
      const o = n.querySelectorAll("slot");
      for (let l = 0; l < o.length; l++)
        s.add(o[l]);
    }
    return Array.from(s);
  }
  /**
   * @internal
   */
  _injectChildStyle(t, s) {
    this._applyStyles(t.styles, t, s);
  }
  /**
   * @internal
   */
  _beginPatch() {
    this._patching = !0, this._dirty = !1;
  }
  /**
   * @internal
   */
  _endPatch() {
    this._patching = !1, this._dirty && this._instance && this._update();
  }
  /**
   * @internal
   */
  _hasShadowRoot() {
    return this._def.shadowRoot !== !1;
  }
  /**
   * @internal
   */
  _removeChildStyle(t) {
  }
}
const ts = (e) => {
  const t = e.props["onUpdate:modelValue"] || !1;
  return G(t) ? (s) => qn(t, s) : t;
};
function pc(e) {
  e.target.composing = !0;
}
function Sl(e) {
  const t = e.target;
  t.composing && (t.composing = !1, t.dispatchEvent(new Event("input")));
}
const ht = /* @__PURE__ */ Symbol("_assign");
function Cl(e, t, s) {
  return t && (e = e.trim()), s && (e = co(e)), e;
}
const sr = {
  created(e, { modifiers: { lazy: t, trim: s, number: n } }, o) {
    e[ht] = ts(o);
    const l = n || o.props && o.props.type === "number";
    Ht(e, t ? "change" : "input", (i) => {
      i.target.composing || e[ht](Cl(e.value, s, l));
    }), (s || l) && Ht(e, "change", () => {
      e.value = Cl(e.value, s, l);
    }), t || (Ht(e, "compositionstart", pc), Ht(e, "compositionend", Sl), Ht(e, "change", Sl));
  },
  // set value on mounted so it's after min/max for type="range"
  mounted(e, { value: t }) {
    e.value = t ?? "";
  },
  beforeUpdate(e, { value: t, oldValue: s, modifiers: { lazy: n, trim: o, number: l } }, i) {
    if (e[ht] = ts(i), e.composing) return;
    const a = (l || e.type === "number") && !/^0\d/.test(e.value) ? co(e.value) : e.value, d = t ?? "";
    if (a === d)
      return;
    const m = e.getRootNode();
    (m instanceof Document || m instanceof ShadowRoot) && m.activeElement === e && e.type !== "range" && (n && t === s || o && e.value.trim() === d) || (e.value = d);
  }
}, mc = {
  // #4096 array checkboxes need to be deep traversed
  deep: !0,
  created(e, t, s) {
    e[ht] = ts(s), Ht(e, "change", () => {
      const n = e._modelValue, o = Ms(e), l = e.checked, i = e[ht];
      if (G(n)) {
        const a = lr(n, o), d = a !== -1;
        if (l && !d)
          i(n.concat(o));
        else if (!l && d) {
          const m = [...n];
          m.splice(a, 1), i(m);
        }
      } else if (Vs(n)) {
        const a = new Set(n);
        l ? a.add(o) : a.delete(o), i(a);
      } else
        i(Wi(e, l));
    });
  },
  // set initial checked on mount to wait for true-value/false-value
  mounted: Al,
  beforeUpdate(e, t, s) {
    e[ht] = ts(s), Al(e, t, s);
  }
};
function Al(e, { value: t, oldValue: s }, n) {
  e._modelValue = t;
  let o;
  if (G(t))
    o = lr(t, n.props.value) > -1;
  else if (Vs(t))
    o = t.has(n.props.value);
  else {
    if (t === s) return;
    o = Xt(t, Wi(e, !0));
  }
  e.checked !== o && (e.checked = o);
}
const gc = {
  created(e, { value: t }, s) {
    e.checked = Xt(t, s.props.value), e[ht] = ts(s), Ht(e, "change", () => {
      e[ht](Ms(e));
    });
  },
  beforeUpdate(e, { value: t, oldValue: s }, n) {
    e[ht] = ts(n), t !== s && (e.checked = Xt(t, n.props.value));
  }
}, zi = {
  // <select multiple> value need to be deep traversed
  deep: !0,
  created(e, { value: t, modifiers: { number: s } }, n) {
    const o = Vs(t);
    Ht(e, "change", () => {
      const l = Array.prototype.filter.call(e.options, (i) => i.selected).map(
        (i) => s ? co(Ms(i)) : Ms(i)
      );
      e[ht](
        e.multiple ? o ? new Set(l) : l : l[0]
      ), e._assigning = !0, An(() => {
        e._assigning = !1;
      });
    }), e[ht] = ts(n);
  },
  // set value in mounted & updated because <select> relies on its children
  // <option>s.
  mounted(e, { value: t }) {
    El(e, t);
  },
  beforeUpdate(e, t, s) {
    e[ht] = ts(s);
  },
  updated(e, { value: t }) {
    e._assigning || El(e, t);
  }
};
function El(e, t) {
  const s = e.multiple, n = G(t);
  if (!(s && !n && !Vs(t))) {
    for (let o = 0, l = e.options.length; o < l; o++) {
      const i = e.options[o], a = Ms(i);
      if (s)
        if (n) {
          const d = typeof a;
          d === "string" || d === "number" ? i.selected = t.some((m) => String(m) === String(a)) : i.selected = lr(t, a) > -1;
        } else
          i.selected = t.has(a);
      else if (Xt(Ms(i), t)) {
        e.selectedIndex !== o && (e.selectedIndex = o);
        return;
      }
    }
    !s && e.selectedIndex !== -1 && (e.selectedIndex = -1);
  }
}
function Ms(e) {
  return "_value" in e ? e._value : e.value;
}
function Wi(e, t) {
  const s = t ? "_trueValue" : "_falseValue";
  return s in e ? e[s] : t;
}
const hc = {
  created(e, t, s) {
    zn(e, t, s, null, "created");
  },
  mounted(e, t, s) {
    zn(e, t, s, null, "mounted");
  },
  beforeUpdate(e, t, s, n) {
    zn(e, t, s, n, "beforeUpdate");
  },
  updated(e, t, s, n) {
    zn(e, t, s, n, "updated");
  }
};
function bc(e, t) {
  switch (e) {
    case "SELECT":
      return zi;
    case "TEXTAREA":
      return sr;
    default:
      switch (t) {
        case "checkbox":
          return mc;
        case "radio":
          return gc;
        default:
          return sr;
      }
  }
}
function zn(e, t, s, n, o) {
  const i = bc(
    e.tagName,
    s.props && s.props.type
  )[o];
  i && i(e, t, s, n);
}
const vc = ["ctrl", "shift", "alt", "meta"], yc = {
  stop: (e) => e.stopPropagation(),
  prevent: (e) => e.preventDefault(),
  self: (e) => e.target !== e.currentTarget,
  ctrl: (e) => !e.ctrlKey,
  shift: (e) => !e.shiftKey,
  alt: (e) => !e.altKey,
  meta: (e) => !e.metaKey,
  left: (e) => "button" in e && e.button !== 0,
  middle: (e) => "button" in e && e.button !== 1,
  right: (e) => "button" in e && e.button !== 2,
  exact: (e, t) => vc.some((s) => e[`${s}Key`] && !t.includes(s))
}, an = (e, t) => {
  if (!e) return e;
  const s = e._withMods || (e._withMods = {}), n = t.join(".");
  return s[n] || (s[n] = ((o, ...l) => {
    for (let i = 0; i < t.length; i++) {
      const a = yc[t[i]];
      if (a && a(o, t)) return;
    }
    return e(o, ...l);
  }));
}, xc = {
  esc: "escape",
  space: " ",
  up: "arrow-up",
  left: "arrow-left",
  right: "arrow-right",
  down: "arrow-down",
  delete: "backspace"
}, un = (e, t) => {
  const s = e._withKeys || (e._withKeys = {}), n = t.join(".");
  return s[n] || (s[n] = ((o) => {
    if (!("key" in o))
      return;
    const l = dt(o.key);
    if (t.some(
      (i) => i === l || xc[i] === l
    ))
      return e(o);
  }));
}, _c = /* @__PURE__ */ Le({ patchProp: ac }, Wd);
let Il;
function Ki() {
  return Il || (Il = Cd(_c));
}
const wc = ((...e) => {
  Ki().render(...e);
}), Tl = ((...e) => {
  const t = Ki().createApp(...e), { mount: s } = t;
  return t.mount = (n) => {
    const o = Sc(n);
    if (!o) return;
    const l = t._component;
    !X(l) && !l.render && !l.template && (l.template = o.innerHTML), o.nodeType === 1 && (o.textContent = "");
    const i = s(o, !1, kc(o));
    return o instanceof Element && (o.removeAttribute("v-cloak"), o.setAttribute("data-v-app", "")), i;
  }, t;
});
function kc(e) {
  if (e instanceof SVGElement)
    return "svg";
  if (typeof MathMLElement == "function" && e instanceof MathMLElement)
    return "mathml";
}
function Sc(e) {
  return Ve(e) ? document.querySelector(e) : e;
}
function qi(e) {
  var t, s, n = "";
  if (typeof e == "string" || typeof e == "number") n += e;
  else if (typeof e == "object") if (Array.isArray(e)) {
    var o = e.length;
    for (t = 0; t < o; t++) e[t] && (s = qi(e[t])) && (n && (n += " "), n += s);
  } else for (s in e) e[s] && (n && (n += " "), n += s);
  return n;
}
function Gi() {
  for (var e, t, s = 0, n = "", o = arguments.length; s < o; s++) (e = arguments[s]) && (t = qi(e)) && (n && (n += " "), n += t);
  return n;
}
const Pl = (e) => typeof e == "boolean" ? `${e}` : e === 0 ? "0" : e, Rl = Gi, Ji = (e, t) => (s) => {
  var n;
  if ((t == null ? void 0 : t.variants) == null) return Rl(e, s == null ? void 0 : s.class, s == null ? void 0 : s.className);
  const { variants: o, defaultVariants: l } = t, i = Object.keys(o).map((m) => {
    const g = s == null ? void 0 : s[m], x = l == null ? void 0 : l[m];
    if (g === null) return null;
    const C = Pl(g) || Pl(x);
    return o[m][C];
  }), a = s && Object.entries(s).reduce((m, g) => {
    let [x, C] = g;
    return C === void 0 || (m[x] = C), m;
  }, {}), d = t == null || (n = t.compoundVariants) === null || n === void 0 ? void 0 : n.reduce((m, g) => {
    let { class: x, className: C, ...E } = g;
    return Object.entries(E).every((U) => {
      let [A, w] = U;
      return Array.isArray(w) ? w.includes({
        ...l,
        ...a
      }[A]) : {
        ...l,
        ...a
      }[A] === w;
    }) ? [
      ...m,
      x,
      C
    ] : m;
  }, []);
  return Rl(e, i, d, s == null ? void 0 : s.class, s == null ? void 0 : s.className);
}, Cc = Ji(
  "inline-flex items-center justify-center rounded-md text-base font-medium ring-offset-background transition-colors focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-pointer select-none",
  {
    variants: {
      variant: {
        primary: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground"
      },
      size: {
        sm: "rounded-md px-3 py-1",
        md: "h-10 px-4 py-2",
        lg: "h-11 rounded-md px-8"
      }
    },
    defaultVariants: {
      variant: "primary",
      size: "md"
    }
  }
), wr = "-", Ac = (e) => {
  const t = Ic(e), {
    conflictingClassGroups: s,
    conflictingClassGroupModifiers: n
  } = e;
  return {
    getClassGroupId: (i) => {
      const a = i.split(wr);
      return a[0] === "" && a.length !== 1 && a.shift(), Yi(a, t) || Ec(i);
    },
    getConflictingClassGroupIds: (i, a) => {
      const d = s[i] || [];
      return a && n[i] ? [...d, ...n[i]] : d;
    }
  };
}, Yi = (e, t) => {
  var i;
  if (e.length === 0)
    return t.classGroupId;
  const s = e[0], n = t.nextPart.get(s), o = n ? Yi(e.slice(1), n) : void 0;
  if (o)
    return o;
  if (t.validators.length === 0)
    return;
  const l = e.join(wr);
  return (i = t.validators.find(({
    validator: a
  }) => a(l))) == null ? void 0 : i.classGroupId;
}, Ml = /^\[(.+)\]$/, Ec = (e) => {
  if (Ml.test(e)) {
    const t = Ml.exec(e)[1], s = t == null ? void 0 : t.substring(0, t.indexOf(":"));
    if (s)
      return "arbitrary.." + s;
  }
}, Ic = (e) => {
  const {
    theme: t,
    prefix: s
  } = e, n = {
    nextPart: /* @__PURE__ */ new Map(),
    validators: []
  };
  return Pc(Object.entries(e.classGroups), s).forEach(([l, i]) => {
    nr(i, n, l, t);
  }), n;
}, nr = (e, t, s, n) => {
  e.forEach((o) => {
    if (typeof o == "string") {
      const l = o === "" ? t : Vl(t, o);
      l.classGroupId = s;
      return;
    }
    if (typeof o == "function") {
      if (Tc(o)) {
        nr(o(n), t, s, n);
        return;
      }
      t.validators.push({
        validator: o,
        classGroupId: s
      });
      return;
    }
    Object.entries(o).forEach(([l, i]) => {
      nr(i, Vl(t, l), s, n);
    });
  });
}, Vl = (e, t) => {
  let s = e;
  return t.split(wr).forEach((n) => {
    s.nextPart.has(n) || s.nextPart.set(n, {
      nextPart: /* @__PURE__ */ new Map(),
      validators: []
    }), s = s.nextPart.get(n);
  }), s;
}, Tc = (e) => e.isThemeGetter, Pc = (e, t) => t ? e.map(([s, n]) => {
  const o = n.map((l) => typeof l == "string" ? t + l : typeof l == "object" ? Object.fromEntries(Object.entries(l).map(([i, a]) => [t + i, a])) : l);
  return [s, o];
}) : e, Rc = (e) => {
  if (e < 1)
    return {
      get: () => {
      },
      set: () => {
      }
    };
  let t = 0, s = /* @__PURE__ */ new Map(), n = /* @__PURE__ */ new Map();
  const o = (l, i) => {
    s.set(l, i), t++, t > e && (t = 0, n = s, s = /* @__PURE__ */ new Map());
  };
  return {
    get(l) {
      let i = s.get(l);
      if (i !== void 0)
        return i;
      if ((i = n.get(l)) !== void 0)
        return o(l, i), i;
    },
    set(l, i) {
      s.has(l) ? s.set(l, i) : o(l, i);
    }
  };
}, Qi = "!", Mc = (e) => {
  const {
    separator: t,
    experimentalParseClassName: s
  } = e, n = t.length === 1, o = t[0], l = t.length, i = (a) => {
    const d = [];
    let m = 0, g = 0, x;
    for (let w = 0; w < a.length; w++) {
      let H = a[w];
      if (m === 0) {
        if (H === o && (n || a.slice(w, w + l) === t)) {
          d.push(a.slice(g, w)), g = w + l;
          continue;
        }
        if (H === "/") {
          x = w;
          continue;
        }
      }
      H === "[" ? m++ : H === "]" && m--;
    }
    const C = d.length === 0 ? a : a.substring(g), E = C.startsWith(Qi), U = E ? C.substring(1) : C, A = x && x > g ? x - g : void 0;
    return {
      modifiers: d,
      hasImportantModifier: E,
      baseClassName: U,
      maybePostfixModifierPosition: A
    };
  };
  return s ? (a) => s({
    className: a,
    parseClassName: i
  }) : i;
}, Vc = (e) => {
  if (e.length <= 1)
    return e;
  const t = [];
  let s = [];
  return e.forEach((n) => {
    n[0] === "[" ? (t.push(...s.sort(), n), s = []) : s.push(n);
  }), t.push(...s.sort()), t;
}, $c = (e) => ({
  cache: Rc(e.cacheSize),
  parseClassName: Mc(e),
  ...Ac(e)
}), Oc = /\s+/, jc = (e, t) => {
  const {
    parseClassName: s,
    getClassGroupId: n,
    getConflictingClassGroupIds: o
  } = t, l = [], i = e.trim().split(Oc);
  let a = "";
  for (let d = i.length - 1; d >= 0; d -= 1) {
    const m = i[d], {
      modifiers: g,
      hasImportantModifier: x,
      baseClassName: C,
      maybePostfixModifierPosition: E
    } = s(m);
    let U = !!E, A = n(U ? C.substring(0, E) : C);
    if (!A) {
      if (!U) {
        a = m + (a.length > 0 ? " " + a : a);
        continue;
      }
      if (A = n(C), !A) {
        a = m + (a.length > 0 ? " " + a : a);
        continue;
      }
      U = !1;
    }
    const w = Vc(g).join(":"), H = x ? w + Qi : w, D = H + A;
    if (l.includes(D))
      continue;
    l.push(D);
    const K = o(A, U);
    for (let B = 0; B < K.length; ++B) {
      const Q = K[B];
      l.push(H + Q);
    }
    a = m + (a.length > 0 ? " " + a : a);
  }
  return a;
};
function Nc() {
  let e = 0, t, s, n = "";
  for (; e < arguments.length; )
    (t = arguments[e++]) && (s = Zi(t)) && (n && (n += " "), n += s);
  return n;
}
const Zi = (e) => {
  if (typeof e == "string")
    return e;
  let t, s = "";
  for (let n = 0; n < e.length; n++)
    e[n] && (t = Zi(e[n])) && (s && (s += " "), s += t);
  return s;
};
function Lc(e, ...t) {
  let s, n, o, l = i;
  function i(d) {
    const m = t.reduce((g, x) => x(g), e());
    return s = $c(m), n = s.cache.get, o = s.cache.set, l = a, a(d);
  }
  function a(d) {
    const m = n(d);
    if (m)
      return m;
    const g = jc(d, s);
    return o(d, g), g;
  }
  return function() {
    return l(Nc.apply(null, arguments));
  };
}
const Ee = (e) => {
  const t = (s) => s[e] || [];
  return t.isThemeGetter = !0, t;
}, Xi = /^\[(?:([a-z-]+):)?(.+)\]$/i, Uc = /^\d+\/\d+$/, Dc = /* @__PURE__ */ new Set(["px", "full", "screen"]), Bc = /^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/, Fc = /\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/, Hc = /^(rgba?|hsla?|hwb|(ok)?(lab|lch)|color-mix)\(.+\)$/, zc = /^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/, Wc = /^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/, Nt = (e) => Ts(e) || Dc.has(e) || Uc.test(e), Yt = (e) => $s(e, "length", Xc), Ts = (e) => !!e && !Number.isNaN(Number(e)), Ho = (e) => $s(e, "number", Ts), sn = (e) => !!e && Number.isInteger(Number(e)), Kc = (e) => e.endsWith("%") && Ts(e.slice(0, -1)), ee = (e) => Xi.test(e), Qt = (e) => Bc.test(e), qc = /* @__PURE__ */ new Set(["length", "size", "percentage"]), Gc = (e) => $s(e, qc, ea), Jc = (e) => $s(e, "position", ea), Yc = /* @__PURE__ */ new Set(["image", "url"]), Qc = (e) => $s(e, Yc, tf), Zc = (e) => $s(e, "", ef), nn = () => !0, $s = (e, t, s) => {
  const n = Xi.exec(e);
  return n ? n[1] ? typeof t == "string" ? n[1] === t : t.has(n[1]) : s(n[2]) : !1;
}, Xc = (e) => (
  // `colorFunctionRegex` check is necessary because color functions can have percentages in them which which would be incorrectly classified as lengths.
  // For example, `hsl(0 0% 0%)` would be classified as a length without this check.
  // I could also use lookbehind assertion in `lengthUnitRegex` but that isn't supported widely enough.
  Fc.test(e) && !Hc.test(e)
), ea = () => !1, ef = (e) => zc.test(e), tf = (e) => Wc.test(e), sf = () => {
  const e = Ee("colors"), t = Ee("spacing"), s = Ee("blur"), n = Ee("brightness"), o = Ee("borderColor"), l = Ee("borderRadius"), i = Ee("borderSpacing"), a = Ee("borderWidth"), d = Ee("contrast"), m = Ee("grayscale"), g = Ee("hueRotate"), x = Ee("invert"), C = Ee("gap"), E = Ee("gradientColorStops"), U = Ee("gradientColorStopPositions"), A = Ee("inset"), w = Ee("margin"), H = Ee("opacity"), D = Ee("padding"), K = Ee("saturate"), B = Ee("scale"), Q = Ee("sepia"), je = Ee("skew"), W = Ee("space"), te = Ee("translate"), Re = () => ["auto", "contain", "none"], _e = () => ["auto", "hidden", "clip", "visible", "scroll"], $e = () => ["auto", ee, t], re = () => [ee, t], xe = () => ["", Nt, Yt], He = () => ["auto", Ts, ee], bt = () => ["bottom", "center", "left", "left-bottom", "left-top", "right", "right-bottom", "right-top", "top"], we = () => ["solid", "dashed", "dotted", "double", "none"], fe = () => ["normal", "multiply", "screen", "overlay", "darken", "lighten", "color-dodge", "color-burn", "hard-light", "soft-light", "difference", "exclusion", "hue", "saturation", "color", "luminosity"], se = () => ["start", "end", "center", "between", "around", "evenly", "stretch"], Me = () => ["", "0", ee], De = () => ["auto", "avoid", "all", "avoid-page", "page", "left", "right", "column"], ze = () => [Ts, ee];
  return {
    cacheSize: 500,
    separator: ":",
    theme: {
      colors: [nn],
      spacing: [Nt, Yt],
      blur: ["none", "", Qt, ee],
      brightness: ze(),
      borderColor: [e],
      borderRadius: ["none", "", "full", Qt, ee],
      borderSpacing: re(),
      borderWidth: xe(),
      contrast: ze(),
      grayscale: Me(),
      hueRotate: ze(),
      invert: Me(),
      gap: re(),
      gradientColorStops: [e],
      gradientColorStopPositions: [Kc, Yt],
      inset: $e(),
      margin: $e(),
      opacity: ze(),
      padding: re(),
      saturate: ze(),
      scale: ze(),
      sepia: Me(),
      skew: ze(),
      space: re(),
      translate: re()
    },
    classGroups: {
      // Layout
      /**
       * Aspect Ratio
       * @see https://tailwindcss.com/docs/aspect-ratio
       */
      aspect: [{
        aspect: ["auto", "square", "video", ee]
      }],
      /**
       * Container
       * @see https://tailwindcss.com/docs/container
       */
      container: ["container"],
      /**
       * Columns
       * @see https://tailwindcss.com/docs/columns
       */
      columns: [{
        columns: [Qt]
      }],
      /**
       * Break After
       * @see https://tailwindcss.com/docs/break-after
       */
      "break-after": [{
        "break-after": De()
      }],
      /**
       * Break Before
       * @see https://tailwindcss.com/docs/break-before
       */
      "break-before": [{
        "break-before": De()
      }],
      /**
       * Break Inside
       * @see https://tailwindcss.com/docs/break-inside
       */
      "break-inside": [{
        "break-inside": ["auto", "avoid", "avoid-page", "avoid-column"]
      }],
      /**
       * Box Decoration Break
       * @see https://tailwindcss.com/docs/box-decoration-break
       */
      "box-decoration": [{
        "box-decoration": ["slice", "clone"]
      }],
      /**
       * Box Sizing
       * @see https://tailwindcss.com/docs/box-sizing
       */
      box: [{
        box: ["border", "content"]
      }],
      /**
       * Display
       * @see https://tailwindcss.com/docs/display
       */
      display: ["block", "inline-block", "inline", "flex", "inline-flex", "table", "inline-table", "table-caption", "table-cell", "table-column", "table-column-group", "table-footer-group", "table-header-group", "table-row-group", "table-row", "flow-root", "grid", "inline-grid", "contents", "list-item", "hidden"],
      /**
       * Floats
       * @see https://tailwindcss.com/docs/float
       */
      float: [{
        float: ["right", "left", "none", "start", "end"]
      }],
      /**
       * Clear
       * @see https://tailwindcss.com/docs/clear
       */
      clear: [{
        clear: ["left", "right", "both", "none", "start", "end"]
      }],
      /**
       * Isolation
       * @see https://tailwindcss.com/docs/isolation
       */
      isolation: ["isolate", "isolation-auto"],
      /**
       * Object Fit
       * @see https://tailwindcss.com/docs/object-fit
       */
      "object-fit": [{
        object: ["contain", "cover", "fill", "none", "scale-down"]
      }],
      /**
       * Object Position
       * @see https://tailwindcss.com/docs/object-position
       */
      "object-position": [{
        object: [...bt(), ee]
      }],
      /**
       * Overflow
       * @see https://tailwindcss.com/docs/overflow
       */
      overflow: [{
        overflow: _e()
      }],
      /**
       * Overflow X
       * @see https://tailwindcss.com/docs/overflow
       */
      "overflow-x": [{
        "overflow-x": _e()
      }],
      /**
       * Overflow Y
       * @see https://tailwindcss.com/docs/overflow
       */
      "overflow-y": [{
        "overflow-y": _e()
      }],
      /**
       * Overscroll Behavior
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      overscroll: [{
        overscroll: Re()
      }],
      /**
       * Overscroll Behavior X
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      "overscroll-x": [{
        "overscroll-x": Re()
      }],
      /**
       * Overscroll Behavior Y
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      "overscroll-y": [{
        "overscroll-y": Re()
      }],
      /**
       * Position
       * @see https://tailwindcss.com/docs/position
       */
      position: ["static", "fixed", "absolute", "relative", "sticky"],
      /**
       * Top / Right / Bottom / Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      inset: [{
        inset: [A]
      }],
      /**
       * Right / Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      "inset-x": [{
        "inset-x": [A]
      }],
      /**
       * Top / Bottom
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      "inset-y": [{
        "inset-y": [A]
      }],
      /**
       * Start
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      start: [{
        start: [A]
      }],
      /**
       * End
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      end: [{
        end: [A]
      }],
      /**
       * Top
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      top: [{
        top: [A]
      }],
      /**
       * Right
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      right: [{
        right: [A]
      }],
      /**
       * Bottom
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      bottom: [{
        bottom: [A]
      }],
      /**
       * Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      left: [{
        left: [A]
      }],
      /**
       * Visibility
       * @see https://tailwindcss.com/docs/visibility
       */
      visibility: ["visible", "invisible", "collapse"],
      /**
       * Z-Index
       * @see https://tailwindcss.com/docs/z-index
       */
      z: [{
        z: ["auto", sn, ee]
      }],
      // Flexbox and Grid
      /**
       * Flex Basis
       * @see https://tailwindcss.com/docs/flex-basis
       */
      basis: [{
        basis: $e()
      }],
      /**
       * Flex Direction
       * @see https://tailwindcss.com/docs/flex-direction
       */
      "flex-direction": [{
        flex: ["row", "row-reverse", "col", "col-reverse"]
      }],
      /**
       * Flex Wrap
       * @see https://tailwindcss.com/docs/flex-wrap
       */
      "flex-wrap": [{
        flex: ["wrap", "wrap-reverse", "nowrap"]
      }],
      /**
       * Flex
       * @see https://tailwindcss.com/docs/flex
       */
      flex: [{
        flex: ["1", "auto", "initial", "none", ee]
      }],
      /**
       * Flex Grow
       * @see https://tailwindcss.com/docs/flex-grow
       */
      grow: [{
        grow: Me()
      }],
      /**
       * Flex Shrink
       * @see https://tailwindcss.com/docs/flex-shrink
       */
      shrink: [{
        shrink: Me()
      }],
      /**
       * Order
       * @see https://tailwindcss.com/docs/order
       */
      order: [{
        order: ["first", "last", "none", sn, ee]
      }],
      /**
       * Grid Template Columns
       * @see https://tailwindcss.com/docs/grid-template-columns
       */
      "grid-cols": [{
        "grid-cols": [nn]
      }],
      /**
       * Grid Column Start / End
       * @see https://tailwindcss.com/docs/grid-column
       */
      "col-start-end": [{
        col: ["auto", {
          span: ["full", sn, ee]
        }, ee]
      }],
      /**
       * Grid Column Start
       * @see https://tailwindcss.com/docs/grid-column
       */
      "col-start": [{
        "col-start": He()
      }],
      /**
       * Grid Column End
       * @see https://tailwindcss.com/docs/grid-column
       */
      "col-end": [{
        "col-end": He()
      }],
      /**
       * Grid Template Rows
       * @see https://tailwindcss.com/docs/grid-template-rows
       */
      "grid-rows": [{
        "grid-rows": [nn]
      }],
      /**
       * Grid Row Start / End
       * @see https://tailwindcss.com/docs/grid-row
       */
      "row-start-end": [{
        row: ["auto", {
          span: [sn, ee]
        }, ee]
      }],
      /**
       * Grid Row Start
       * @see https://tailwindcss.com/docs/grid-row
       */
      "row-start": [{
        "row-start": He()
      }],
      /**
       * Grid Row End
       * @see https://tailwindcss.com/docs/grid-row
       */
      "row-end": [{
        "row-end": He()
      }],
      /**
       * Grid Auto Flow
       * @see https://tailwindcss.com/docs/grid-auto-flow
       */
      "grid-flow": [{
        "grid-flow": ["row", "col", "dense", "row-dense", "col-dense"]
      }],
      /**
       * Grid Auto Columns
       * @see https://tailwindcss.com/docs/grid-auto-columns
       */
      "auto-cols": [{
        "auto-cols": ["auto", "min", "max", "fr", ee]
      }],
      /**
       * Grid Auto Rows
       * @see https://tailwindcss.com/docs/grid-auto-rows
       */
      "auto-rows": [{
        "auto-rows": ["auto", "min", "max", "fr", ee]
      }],
      /**
       * Gap
       * @see https://tailwindcss.com/docs/gap
       */
      gap: [{
        gap: [C]
      }],
      /**
       * Gap X
       * @see https://tailwindcss.com/docs/gap
       */
      "gap-x": [{
        "gap-x": [C]
      }],
      /**
       * Gap Y
       * @see https://tailwindcss.com/docs/gap
       */
      "gap-y": [{
        "gap-y": [C]
      }],
      /**
       * Justify Content
       * @see https://tailwindcss.com/docs/justify-content
       */
      "justify-content": [{
        justify: ["normal", ...se()]
      }],
      /**
       * Justify Items
       * @see https://tailwindcss.com/docs/justify-items
       */
      "justify-items": [{
        "justify-items": ["start", "end", "center", "stretch"]
      }],
      /**
       * Justify Self
       * @see https://tailwindcss.com/docs/justify-self
       */
      "justify-self": [{
        "justify-self": ["auto", "start", "end", "center", "stretch"]
      }],
      /**
       * Align Content
       * @see https://tailwindcss.com/docs/align-content
       */
      "align-content": [{
        content: ["normal", ...se(), "baseline"]
      }],
      /**
       * Align Items
       * @see https://tailwindcss.com/docs/align-items
       */
      "align-items": [{
        items: ["start", "end", "center", "baseline", "stretch"]
      }],
      /**
       * Align Self
       * @see https://tailwindcss.com/docs/align-self
       */
      "align-self": [{
        self: ["auto", "start", "end", "center", "stretch", "baseline"]
      }],
      /**
       * Place Content
       * @see https://tailwindcss.com/docs/place-content
       */
      "place-content": [{
        "place-content": [...se(), "baseline"]
      }],
      /**
       * Place Items
       * @see https://tailwindcss.com/docs/place-items
       */
      "place-items": [{
        "place-items": ["start", "end", "center", "baseline", "stretch"]
      }],
      /**
       * Place Self
       * @see https://tailwindcss.com/docs/place-self
       */
      "place-self": [{
        "place-self": ["auto", "start", "end", "center", "stretch"]
      }],
      // Spacing
      /**
       * Padding
       * @see https://tailwindcss.com/docs/padding
       */
      p: [{
        p: [D]
      }],
      /**
       * Padding X
       * @see https://tailwindcss.com/docs/padding
       */
      px: [{
        px: [D]
      }],
      /**
       * Padding Y
       * @see https://tailwindcss.com/docs/padding
       */
      py: [{
        py: [D]
      }],
      /**
       * Padding Start
       * @see https://tailwindcss.com/docs/padding
       */
      ps: [{
        ps: [D]
      }],
      /**
       * Padding End
       * @see https://tailwindcss.com/docs/padding
       */
      pe: [{
        pe: [D]
      }],
      /**
       * Padding Top
       * @see https://tailwindcss.com/docs/padding
       */
      pt: [{
        pt: [D]
      }],
      /**
       * Padding Right
       * @see https://tailwindcss.com/docs/padding
       */
      pr: [{
        pr: [D]
      }],
      /**
       * Padding Bottom
       * @see https://tailwindcss.com/docs/padding
       */
      pb: [{
        pb: [D]
      }],
      /**
       * Padding Left
       * @see https://tailwindcss.com/docs/padding
       */
      pl: [{
        pl: [D]
      }],
      /**
       * Margin
       * @see https://tailwindcss.com/docs/margin
       */
      m: [{
        m: [w]
      }],
      /**
       * Margin X
       * @see https://tailwindcss.com/docs/margin
       */
      mx: [{
        mx: [w]
      }],
      /**
       * Margin Y
       * @see https://tailwindcss.com/docs/margin
       */
      my: [{
        my: [w]
      }],
      /**
       * Margin Start
       * @see https://tailwindcss.com/docs/margin
       */
      ms: [{
        ms: [w]
      }],
      /**
       * Margin End
       * @see https://tailwindcss.com/docs/margin
       */
      me: [{
        me: [w]
      }],
      /**
       * Margin Top
       * @see https://tailwindcss.com/docs/margin
       */
      mt: [{
        mt: [w]
      }],
      /**
       * Margin Right
       * @see https://tailwindcss.com/docs/margin
       */
      mr: [{
        mr: [w]
      }],
      /**
       * Margin Bottom
       * @see https://tailwindcss.com/docs/margin
       */
      mb: [{
        mb: [w]
      }],
      /**
       * Margin Left
       * @see https://tailwindcss.com/docs/margin
       */
      ml: [{
        ml: [w]
      }],
      /**
       * Space Between X
       * @see https://tailwindcss.com/docs/space
       */
      "space-x": [{
        "space-x": [W]
      }],
      /**
       * Space Between X Reverse
       * @see https://tailwindcss.com/docs/space
       */
      "space-x-reverse": ["space-x-reverse"],
      /**
       * Space Between Y
       * @see https://tailwindcss.com/docs/space
       */
      "space-y": [{
        "space-y": [W]
      }],
      /**
       * Space Between Y Reverse
       * @see https://tailwindcss.com/docs/space
       */
      "space-y-reverse": ["space-y-reverse"],
      // Sizing
      /**
       * Width
       * @see https://tailwindcss.com/docs/width
       */
      w: [{
        w: ["auto", "min", "max", "fit", "svw", "lvw", "dvw", ee, t]
      }],
      /**
       * Min-Width
       * @see https://tailwindcss.com/docs/min-width
       */
      "min-w": [{
        "min-w": [ee, t, "min", "max", "fit"]
      }],
      /**
       * Max-Width
       * @see https://tailwindcss.com/docs/max-width
       */
      "max-w": [{
        "max-w": [ee, t, "none", "full", "min", "max", "fit", "prose", {
          screen: [Qt]
        }, Qt]
      }],
      /**
       * Height
       * @see https://tailwindcss.com/docs/height
       */
      h: [{
        h: [ee, t, "auto", "min", "max", "fit", "svh", "lvh", "dvh"]
      }],
      /**
       * Min-Height
       * @see https://tailwindcss.com/docs/min-height
       */
      "min-h": [{
        "min-h": [ee, t, "min", "max", "fit", "svh", "lvh", "dvh"]
      }],
      /**
       * Max-Height
       * @see https://tailwindcss.com/docs/max-height
       */
      "max-h": [{
        "max-h": [ee, t, "min", "max", "fit", "svh", "lvh", "dvh"]
      }],
      /**
       * Size
       * @see https://tailwindcss.com/docs/size
       */
      size: [{
        size: [ee, t, "auto", "min", "max", "fit"]
      }],
      // Typography
      /**
       * Font Size
       * @see https://tailwindcss.com/docs/font-size
       */
      "font-size": [{
        text: ["base", Qt, Yt]
      }],
      /**
       * Font Smoothing
       * @see https://tailwindcss.com/docs/font-smoothing
       */
      "font-smoothing": ["antialiased", "subpixel-antialiased"],
      /**
       * Font Style
       * @see https://tailwindcss.com/docs/font-style
       */
      "font-style": ["italic", "not-italic"],
      /**
       * Font Weight
       * @see https://tailwindcss.com/docs/font-weight
       */
      "font-weight": [{
        font: ["thin", "extralight", "light", "normal", "medium", "semibold", "bold", "extrabold", "black", Ho]
      }],
      /**
       * Font Family
       * @see https://tailwindcss.com/docs/font-family
       */
      "font-family": [{
        font: [nn]
      }],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      "fvn-normal": ["normal-nums"],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      "fvn-ordinal": ["ordinal"],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      "fvn-slashed-zero": ["slashed-zero"],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      "fvn-figure": ["lining-nums", "oldstyle-nums"],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      "fvn-spacing": ["proportional-nums", "tabular-nums"],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      "fvn-fraction": ["diagonal-fractions", "stacked-fractions"],
      /**
       * Letter Spacing
       * @see https://tailwindcss.com/docs/letter-spacing
       */
      tracking: [{
        tracking: ["tighter", "tight", "normal", "wide", "wider", "widest", ee]
      }],
      /**
       * Line Clamp
       * @see https://tailwindcss.com/docs/line-clamp
       */
      "line-clamp": [{
        "line-clamp": ["none", Ts, Ho]
      }],
      /**
       * Line Height
       * @see https://tailwindcss.com/docs/line-height
       */
      leading: [{
        leading: ["none", "tight", "snug", "normal", "relaxed", "loose", Nt, ee]
      }],
      /**
       * List Style Image
       * @see https://tailwindcss.com/docs/list-style-image
       */
      "list-image": [{
        "list-image": ["none", ee]
      }],
      /**
       * List Style Type
       * @see https://tailwindcss.com/docs/list-style-type
       */
      "list-style-type": [{
        list: ["none", "disc", "decimal", ee]
      }],
      /**
       * List Style Position
       * @see https://tailwindcss.com/docs/list-style-position
       */
      "list-style-position": [{
        list: ["inside", "outside"]
      }],
      /**
       * Placeholder Color
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/placeholder-color
       */
      "placeholder-color": [{
        placeholder: [e]
      }],
      /**
       * Placeholder Opacity
       * @see https://tailwindcss.com/docs/placeholder-opacity
       */
      "placeholder-opacity": [{
        "placeholder-opacity": [H]
      }],
      /**
       * Text Alignment
       * @see https://tailwindcss.com/docs/text-align
       */
      "text-alignment": [{
        text: ["left", "center", "right", "justify", "start", "end"]
      }],
      /**
       * Text Color
       * @see https://tailwindcss.com/docs/text-color
       */
      "text-color": [{
        text: [e]
      }],
      /**
       * Text Opacity
       * @see https://tailwindcss.com/docs/text-opacity
       */
      "text-opacity": [{
        "text-opacity": [H]
      }],
      /**
       * Text Decoration
       * @see https://tailwindcss.com/docs/text-decoration
       */
      "text-decoration": ["underline", "overline", "line-through", "no-underline"],
      /**
       * Text Decoration Style
       * @see https://tailwindcss.com/docs/text-decoration-style
       */
      "text-decoration-style": [{
        decoration: [...we(), "wavy"]
      }],
      /**
       * Text Decoration Thickness
       * @see https://tailwindcss.com/docs/text-decoration-thickness
       */
      "text-decoration-thickness": [{
        decoration: ["auto", "from-font", Nt, Yt]
      }],
      /**
       * Text Underline Offset
       * @see https://tailwindcss.com/docs/text-underline-offset
       */
      "underline-offset": [{
        "underline-offset": ["auto", Nt, ee]
      }],
      /**
       * Text Decoration Color
       * @see https://tailwindcss.com/docs/text-decoration-color
       */
      "text-decoration-color": [{
        decoration: [e]
      }],
      /**
       * Text Transform
       * @see https://tailwindcss.com/docs/text-transform
       */
      "text-transform": ["uppercase", "lowercase", "capitalize", "normal-case"],
      /**
       * Text Overflow
       * @see https://tailwindcss.com/docs/text-overflow
       */
      "text-overflow": ["truncate", "text-ellipsis", "text-clip"],
      /**
       * Text Wrap
       * @see https://tailwindcss.com/docs/text-wrap
       */
      "text-wrap": [{
        text: ["wrap", "nowrap", "balance", "pretty"]
      }],
      /**
       * Text Indent
       * @see https://tailwindcss.com/docs/text-indent
       */
      indent: [{
        indent: re()
      }],
      /**
       * Vertical Alignment
       * @see https://tailwindcss.com/docs/vertical-align
       */
      "vertical-align": [{
        align: ["baseline", "top", "middle", "bottom", "text-top", "text-bottom", "sub", "super", ee]
      }],
      /**
       * Whitespace
       * @see https://tailwindcss.com/docs/whitespace
       */
      whitespace: [{
        whitespace: ["normal", "nowrap", "pre", "pre-line", "pre-wrap", "break-spaces"]
      }],
      /**
       * Word Break
       * @see https://tailwindcss.com/docs/word-break
       */
      break: [{
        break: ["normal", "words", "all", "keep"]
      }],
      /**
       * Hyphens
       * @see https://tailwindcss.com/docs/hyphens
       */
      hyphens: [{
        hyphens: ["none", "manual", "auto"]
      }],
      /**
       * Content
       * @see https://tailwindcss.com/docs/content
       */
      content: [{
        content: ["none", ee]
      }],
      // Backgrounds
      /**
       * Background Attachment
       * @see https://tailwindcss.com/docs/background-attachment
       */
      "bg-attachment": [{
        bg: ["fixed", "local", "scroll"]
      }],
      /**
       * Background Clip
       * @see https://tailwindcss.com/docs/background-clip
       */
      "bg-clip": [{
        "bg-clip": ["border", "padding", "content", "text"]
      }],
      /**
       * Background Opacity
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/background-opacity
       */
      "bg-opacity": [{
        "bg-opacity": [H]
      }],
      /**
       * Background Origin
       * @see https://tailwindcss.com/docs/background-origin
       */
      "bg-origin": [{
        "bg-origin": ["border", "padding", "content"]
      }],
      /**
       * Background Position
       * @see https://tailwindcss.com/docs/background-position
       */
      "bg-position": [{
        bg: [...bt(), Jc]
      }],
      /**
       * Background Repeat
       * @see https://tailwindcss.com/docs/background-repeat
       */
      "bg-repeat": [{
        bg: ["no-repeat", {
          repeat: ["", "x", "y", "round", "space"]
        }]
      }],
      /**
       * Background Size
       * @see https://tailwindcss.com/docs/background-size
       */
      "bg-size": [{
        bg: ["auto", "cover", "contain", Gc]
      }],
      /**
       * Background Image
       * @see https://tailwindcss.com/docs/background-image
       */
      "bg-image": [{
        bg: ["none", {
          "gradient-to": ["t", "tr", "r", "br", "b", "bl", "l", "tl"]
        }, Qc]
      }],
      /**
       * Background Color
       * @see https://tailwindcss.com/docs/background-color
       */
      "bg-color": [{
        bg: [e]
      }],
      /**
       * Gradient Color Stops From Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-from-pos": [{
        from: [U]
      }],
      /**
       * Gradient Color Stops Via Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-via-pos": [{
        via: [U]
      }],
      /**
       * Gradient Color Stops To Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-to-pos": [{
        to: [U]
      }],
      /**
       * Gradient Color Stops From
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-from": [{
        from: [E]
      }],
      /**
       * Gradient Color Stops Via
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-via": [{
        via: [E]
      }],
      /**
       * Gradient Color Stops To
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-to": [{
        to: [E]
      }],
      // Borders
      /**
       * Border Radius
       * @see https://tailwindcss.com/docs/border-radius
       */
      rounded: [{
        rounded: [l]
      }],
      /**
       * Border Radius Start
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-s": [{
        "rounded-s": [l]
      }],
      /**
       * Border Radius End
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-e": [{
        "rounded-e": [l]
      }],
      /**
       * Border Radius Top
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-t": [{
        "rounded-t": [l]
      }],
      /**
       * Border Radius Right
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-r": [{
        "rounded-r": [l]
      }],
      /**
       * Border Radius Bottom
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-b": [{
        "rounded-b": [l]
      }],
      /**
       * Border Radius Left
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-l": [{
        "rounded-l": [l]
      }],
      /**
       * Border Radius Start Start
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-ss": [{
        "rounded-ss": [l]
      }],
      /**
       * Border Radius Start End
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-se": [{
        "rounded-se": [l]
      }],
      /**
       * Border Radius End End
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-ee": [{
        "rounded-ee": [l]
      }],
      /**
       * Border Radius End Start
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-es": [{
        "rounded-es": [l]
      }],
      /**
       * Border Radius Top Left
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-tl": [{
        "rounded-tl": [l]
      }],
      /**
       * Border Radius Top Right
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-tr": [{
        "rounded-tr": [l]
      }],
      /**
       * Border Radius Bottom Right
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-br": [{
        "rounded-br": [l]
      }],
      /**
       * Border Radius Bottom Left
       * @see https://tailwindcss.com/docs/border-radius
       */
      "rounded-bl": [{
        "rounded-bl": [l]
      }],
      /**
       * Border Width
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w": [{
        border: [a]
      }],
      /**
       * Border Width X
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-x": [{
        "border-x": [a]
      }],
      /**
       * Border Width Y
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-y": [{
        "border-y": [a]
      }],
      /**
       * Border Width Start
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-s": [{
        "border-s": [a]
      }],
      /**
       * Border Width End
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-e": [{
        "border-e": [a]
      }],
      /**
       * Border Width Top
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-t": [{
        "border-t": [a]
      }],
      /**
       * Border Width Right
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-r": [{
        "border-r": [a]
      }],
      /**
       * Border Width Bottom
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-b": [{
        "border-b": [a]
      }],
      /**
       * Border Width Left
       * @see https://tailwindcss.com/docs/border-width
       */
      "border-w-l": [{
        "border-l": [a]
      }],
      /**
       * Border Opacity
       * @see https://tailwindcss.com/docs/border-opacity
       */
      "border-opacity": [{
        "border-opacity": [H]
      }],
      /**
       * Border Style
       * @see https://tailwindcss.com/docs/border-style
       */
      "border-style": [{
        border: [...we(), "hidden"]
      }],
      /**
       * Divide Width X
       * @see https://tailwindcss.com/docs/divide-width
       */
      "divide-x": [{
        "divide-x": [a]
      }],
      /**
       * Divide Width X Reverse
       * @see https://tailwindcss.com/docs/divide-width
       */
      "divide-x-reverse": ["divide-x-reverse"],
      /**
       * Divide Width Y
       * @see https://tailwindcss.com/docs/divide-width
       */
      "divide-y": [{
        "divide-y": [a]
      }],
      /**
       * Divide Width Y Reverse
       * @see https://tailwindcss.com/docs/divide-width
       */
      "divide-y-reverse": ["divide-y-reverse"],
      /**
       * Divide Opacity
       * @see https://tailwindcss.com/docs/divide-opacity
       */
      "divide-opacity": [{
        "divide-opacity": [H]
      }],
      /**
       * Divide Style
       * @see https://tailwindcss.com/docs/divide-style
       */
      "divide-style": [{
        divide: we()
      }],
      /**
       * Border Color
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color": [{
        border: [o]
      }],
      /**
       * Border Color X
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-x": [{
        "border-x": [o]
      }],
      /**
       * Border Color Y
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-y": [{
        "border-y": [o]
      }],
      /**
       * Border Color S
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-s": [{
        "border-s": [o]
      }],
      /**
       * Border Color E
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-e": [{
        "border-e": [o]
      }],
      /**
       * Border Color Top
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-t": [{
        "border-t": [o]
      }],
      /**
       * Border Color Right
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-r": [{
        "border-r": [o]
      }],
      /**
       * Border Color Bottom
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-b": [{
        "border-b": [o]
      }],
      /**
       * Border Color Left
       * @see https://tailwindcss.com/docs/border-color
       */
      "border-color-l": [{
        "border-l": [o]
      }],
      /**
       * Divide Color
       * @see https://tailwindcss.com/docs/divide-color
       */
      "divide-color": [{
        divide: [o]
      }],
      /**
       * Outline Style
       * @see https://tailwindcss.com/docs/outline-style
       */
      "outline-style": [{
        outline: ["", ...we()]
      }],
      /**
       * Outline Offset
       * @see https://tailwindcss.com/docs/outline-offset
       */
      "outline-offset": [{
        "outline-offset": [Nt, ee]
      }],
      /**
       * Outline Width
       * @see https://tailwindcss.com/docs/outline-width
       */
      "outline-w": [{
        outline: [Nt, Yt]
      }],
      /**
       * Outline Color
       * @see https://tailwindcss.com/docs/outline-color
       */
      "outline-color": [{
        outline: [e]
      }],
      /**
       * Ring Width
       * @see https://tailwindcss.com/docs/ring-width
       */
      "ring-w": [{
        ring: xe()
      }],
      /**
       * Ring Width Inset
       * @see https://tailwindcss.com/docs/ring-width
       */
      "ring-w-inset": ["ring-inset"],
      /**
       * Ring Color
       * @see https://tailwindcss.com/docs/ring-color
       */
      "ring-color": [{
        ring: [e]
      }],
      /**
       * Ring Opacity
       * @see https://tailwindcss.com/docs/ring-opacity
       */
      "ring-opacity": [{
        "ring-opacity": [H]
      }],
      /**
       * Ring Offset Width
       * @see https://tailwindcss.com/docs/ring-offset-width
       */
      "ring-offset-w": [{
        "ring-offset": [Nt, Yt]
      }],
      /**
       * Ring Offset Color
       * @see https://tailwindcss.com/docs/ring-offset-color
       */
      "ring-offset-color": [{
        "ring-offset": [e]
      }],
      // Effects
      /**
       * Box Shadow
       * @see https://tailwindcss.com/docs/box-shadow
       */
      shadow: [{
        shadow: ["", "inner", "none", Qt, Zc]
      }],
      /**
       * Box Shadow Color
       * @see https://tailwindcss.com/docs/box-shadow-color
       */
      "shadow-color": [{
        shadow: [nn]
      }],
      /**
       * Opacity
       * @see https://tailwindcss.com/docs/opacity
       */
      opacity: [{
        opacity: [H]
      }],
      /**
       * Mix Blend Mode
       * @see https://tailwindcss.com/docs/mix-blend-mode
       */
      "mix-blend": [{
        "mix-blend": [...fe(), "plus-lighter", "plus-darker"]
      }],
      /**
       * Background Blend Mode
       * @see https://tailwindcss.com/docs/background-blend-mode
       */
      "bg-blend": [{
        "bg-blend": fe()
      }],
      // Filters
      /**
       * Filter
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/filter
       */
      filter: [{
        filter: ["", "none"]
      }],
      /**
       * Blur
       * @see https://tailwindcss.com/docs/blur
       */
      blur: [{
        blur: [s]
      }],
      /**
       * Brightness
       * @see https://tailwindcss.com/docs/brightness
       */
      brightness: [{
        brightness: [n]
      }],
      /**
       * Contrast
       * @see https://tailwindcss.com/docs/contrast
       */
      contrast: [{
        contrast: [d]
      }],
      /**
       * Drop Shadow
       * @see https://tailwindcss.com/docs/drop-shadow
       */
      "drop-shadow": [{
        "drop-shadow": ["", "none", Qt, ee]
      }],
      /**
       * Grayscale
       * @see https://tailwindcss.com/docs/grayscale
       */
      grayscale: [{
        grayscale: [m]
      }],
      /**
       * Hue Rotate
       * @see https://tailwindcss.com/docs/hue-rotate
       */
      "hue-rotate": [{
        "hue-rotate": [g]
      }],
      /**
       * Invert
       * @see https://tailwindcss.com/docs/invert
       */
      invert: [{
        invert: [x]
      }],
      /**
       * Saturate
       * @see https://tailwindcss.com/docs/saturate
       */
      saturate: [{
        saturate: [K]
      }],
      /**
       * Sepia
       * @see https://tailwindcss.com/docs/sepia
       */
      sepia: [{
        sepia: [Q]
      }],
      /**
       * Backdrop Filter
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/backdrop-filter
       */
      "backdrop-filter": [{
        "backdrop-filter": ["", "none"]
      }],
      /**
       * Backdrop Blur
       * @see https://tailwindcss.com/docs/backdrop-blur
       */
      "backdrop-blur": [{
        "backdrop-blur": [s]
      }],
      /**
       * Backdrop Brightness
       * @see https://tailwindcss.com/docs/backdrop-brightness
       */
      "backdrop-brightness": [{
        "backdrop-brightness": [n]
      }],
      /**
       * Backdrop Contrast
       * @see https://tailwindcss.com/docs/backdrop-contrast
       */
      "backdrop-contrast": [{
        "backdrop-contrast": [d]
      }],
      /**
       * Backdrop Grayscale
       * @see https://tailwindcss.com/docs/backdrop-grayscale
       */
      "backdrop-grayscale": [{
        "backdrop-grayscale": [m]
      }],
      /**
       * Backdrop Hue Rotate
       * @see https://tailwindcss.com/docs/backdrop-hue-rotate
       */
      "backdrop-hue-rotate": [{
        "backdrop-hue-rotate": [g]
      }],
      /**
       * Backdrop Invert
       * @see https://tailwindcss.com/docs/backdrop-invert
       */
      "backdrop-invert": [{
        "backdrop-invert": [x]
      }],
      /**
       * Backdrop Opacity
       * @see https://tailwindcss.com/docs/backdrop-opacity
       */
      "backdrop-opacity": [{
        "backdrop-opacity": [H]
      }],
      /**
       * Backdrop Saturate
       * @see https://tailwindcss.com/docs/backdrop-saturate
       */
      "backdrop-saturate": [{
        "backdrop-saturate": [K]
      }],
      /**
       * Backdrop Sepia
       * @see https://tailwindcss.com/docs/backdrop-sepia
       */
      "backdrop-sepia": [{
        "backdrop-sepia": [Q]
      }],
      // Tables
      /**
       * Border Collapse
       * @see https://tailwindcss.com/docs/border-collapse
       */
      "border-collapse": [{
        border: ["collapse", "separate"]
      }],
      /**
       * Border Spacing
       * @see https://tailwindcss.com/docs/border-spacing
       */
      "border-spacing": [{
        "border-spacing": [i]
      }],
      /**
       * Border Spacing X
       * @see https://tailwindcss.com/docs/border-spacing
       */
      "border-spacing-x": [{
        "border-spacing-x": [i]
      }],
      /**
       * Border Spacing Y
       * @see https://tailwindcss.com/docs/border-spacing
       */
      "border-spacing-y": [{
        "border-spacing-y": [i]
      }],
      /**
       * Table Layout
       * @see https://tailwindcss.com/docs/table-layout
       */
      "table-layout": [{
        table: ["auto", "fixed"]
      }],
      /**
       * Caption Side
       * @see https://tailwindcss.com/docs/caption-side
       */
      caption: [{
        caption: ["top", "bottom"]
      }],
      // Transitions and Animation
      /**
       * Tranisition Property
       * @see https://tailwindcss.com/docs/transition-property
       */
      transition: [{
        transition: ["none", "all", "", "colors", "opacity", "shadow", "transform", ee]
      }],
      /**
       * Transition Duration
       * @see https://tailwindcss.com/docs/transition-duration
       */
      duration: [{
        duration: ze()
      }],
      /**
       * Transition Timing Function
       * @see https://tailwindcss.com/docs/transition-timing-function
       */
      ease: [{
        ease: ["linear", "in", "out", "in-out", ee]
      }],
      /**
       * Transition Delay
       * @see https://tailwindcss.com/docs/transition-delay
       */
      delay: [{
        delay: ze()
      }],
      /**
       * Animation
       * @see https://tailwindcss.com/docs/animation
       */
      animate: [{
        animate: ["none", "spin", "ping", "pulse", "bounce", ee]
      }],
      // Transforms
      /**
       * Transform
       * @see https://tailwindcss.com/docs/transform
       */
      transform: [{
        transform: ["", "gpu", "none"]
      }],
      /**
       * Scale
       * @see https://tailwindcss.com/docs/scale
       */
      scale: [{
        scale: [B]
      }],
      /**
       * Scale X
       * @see https://tailwindcss.com/docs/scale
       */
      "scale-x": [{
        "scale-x": [B]
      }],
      /**
       * Scale Y
       * @see https://tailwindcss.com/docs/scale
       */
      "scale-y": [{
        "scale-y": [B]
      }],
      /**
       * Rotate
       * @see https://tailwindcss.com/docs/rotate
       */
      rotate: [{
        rotate: [sn, ee]
      }],
      /**
       * Translate X
       * @see https://tailwindcss.com/docs/translate
       */
      "translate-x": [{
        "translate-x": [te]
      }],
      /**
       * Translate Y
       * @see https://tailwindcss.com/docs/translate
       */
      "translate-y": [{
        "translate-y": [te]
      }],
      /**
       * Skew X
       * @see https://tailwindcss.com/docs/skew
       */
      "skew-x": [{
        "skew-x": [je]
      }],
      /**
       * Skew Y
       * @see https://tailwindcss.com/docs/skew
       */
      "skew-y": [{
        "skew-y": [je]
      }],
      /**
       * Transform Origin
       * @see https://tailwindcss.com/docs/transform-origin
       */
      "transform-origin": [{
        origin: ["center", "top", "top-right", "right", "bottom-right", "bottom", "bottom-left", "left", "top-left", ee]
      }],
      // Interactivity
      /**
       * Accent Color
       * @see https://tailwindcss.com/docs/accent-color
       */
      accent: [{
        accent: ["auto", e]
      }],
      /**
       * Appearance
       * @see https://tailwindcss.com/docs/appearance
       */
      appearance: [{
        appearance: ["none", "auto"]
      }],
      /**
       * Cursor
       * @see https://tailwindcss.com/docs/cursor
       */
      cursor: [{
        cursor: ["auto", "default", "pointer", "wait", "text", "move", "help", "not-allowed", "none", "context-menu", "progress", "cell", "crosshair", "vertical-text", "alias", "copy", "no-drop", "grab", "grabbing", "all-scroll", "col-resize", "row-resize", "n-resize", "e-resize", "s-resize", "w-resize", "ne-resize", "nw-resize", "se-resize", "sw-resize", "ew-resize", "ns-resize", "nesw-resize", "nwse-resize", "zoom-in", "zoom-out", ee]
      }],
      /**
       * Caret Color
       * @see https://tailwindcss.com/docs/just-in-time-mode#caret-color-utilities
       */
      "caret-color": [{
        caret: [e]
      }],
      /**
       * Pointer Events
       * @see https://tailwindcss.com/docs/pointer-events
       */
      "pointer-events": [{
        "pointer-events": ["none", "auto"]
      }],
      /**
       * Resize
       * @see https://tailwindcss.com/docs/resize
       */
      resize: [{
        resize: ["none", "y", "x", ""]
      }],
      /**
       * Scroll Behavior
       * @see https://tailwindcss.com/docs/scroll-behavior
       */
      "scroll-behavior": [{
        scroll: ["auto", "smooth"]
      }],
      /**
       * Scroll Margin
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-m": [{
        "scroll-m": re()
      }],
      /**
       * Scroll Margin X
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mx": [{
        "scroll-mx": re()
      }],
      /**
       * Scroll Margin Y
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-my": [{
        "scroll-my": re()
      }],
      /**
       * Scroll Margin Start
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-ms": [{
        "scroll-ms": re()
      }],
      /**
       * Scroll Margin End
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-me": [{
        "scroll-me": re()
      }],
      /**
       * Scroll Margin Top
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mt": [{
        "scroll-mt": re()
      }],
      /**
       * Scroll Margin Right
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mr": [{
        "scroll-mr": re()
      }],
      /**
       * Scroll Margin Bottom
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mb": [{
        "scroll-mb": re()
      }],
      /**
       * Scroll Margin Left
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-ml": [{
        "scroll-ml": re()
      }],
      /**
       * Scroll Padding
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-p": [{
        "scroll-p": re()
      }],
      /**
       * Scroll Padding X
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-px": [{
        "scroll-px": re()
      }],
      /**
       * Scroll Padding Y
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-py": [{
        "scroll-py": re()
      }],
      /**
       * Scroll Padding Start
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-ps": [{
        "scroll-ps": re()
      }],
      /**
       * Scroll Padding End
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pe": [{
        "scroll-pe": re()
      }],
      /**
       * Scroll Padding Top
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pt": [{
        "scroll-pt": re()
      }],
      /**
       * Scroll Padding Right
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pr": [{
        "scroll-pr": re()
      }],
      /**
       * Scroll Padding Bottom
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pb": [{
        "scroll-pb": re()
      }],
      /**
       * Scroll Padding Left
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pl": [{
        "scroll-pl": re()
      }],
      /**
       * Scroll Snap Align
       * @see https://tailwindcss.com/docs/scroll-snap-align
       */
      "snap-align": [{
        snap: ["start", "end", "center", "align-none"]
      }],
      /**
       * Scroll Snap Stop
       * @see https://tailwindcss.com/docs/scroll-snap-stop
       */
      "snap-stop": [{
        snap: ["normal", "always"]
      }],
      /**
       * Scroll Snap Type
       * @see https://tailwindcss.com/docs/scroll-snap-type
       */
      "snap-type": [{
        snap: ["none", "x", "y", "both"]
      }],
      /**
       * Scroll Snap Type Strictness
       * @see https://tailwindcss.com/docs/scroll-snap-type
       */
      "snap-strictness": [{
        snap: ["mandatory", "proximity"]
      }],
      /**
       * Touch Action
       * @see https://tailwindcss.com/docs/touch-action
       */
      touch: [{
        touch: ["auto", "none", "manipulation"]
      }],
      /**
       * Touch Action X
       * @see https://tailwindcss.com/docs/touch-action
       */
      "touch-x": [{
        "touch-pan": ["x", "left", "right"]
      }],
      /**
       * Touch Action Y
       * @see https://tailwindcss.com/docs/touch-action
       */
      "touch-y": [{
        "touch-pan": ["y", "up", "down"]
      }],
      /**
       * Touch Action Pinch Zoom
       * @see https://tailwindcss.com/docs/touch-action
       */
      "touch-pz": ["touch-pinch-zoom"],
      /**
       * User Select
       * @see https://tailwindcss.com/docs/user-select
       */
      select: [{
        select: ["none", "text", "all", "auto"]
      }],
      /**
       * Will Change
       * @see https://tailwindcss.com/docs/will-change
       */
      "will-change": [{
        "will-change": ["auto", "scroll", "contents", "transform", ee]
      }],
      // SVG
      /**
       * Fill
       * @see https://tailwindcss.com/docs/fill
       */
      fill: [{
        fill: [e, "none"]
      }],
      /**
       * Stroke Width
       * @see https://tailwindcss.com/docs/stroke-width
       */
      "stroke-w": [{
        stroke: [Nt, Yt, Ho]
      }],
      /**
       * Stroke
       * @see https://tailwindcss.com/docs/stroke
       */
      stroke: [{
        stroke: [e, "none"]
      }],
      // Accessibility
      /**
       * Screen Readers
       * @see https://tailwindcss.com/docs/screen-readers
       */
      sr: ["sr-only", "not-sr-only"],
      /**
       * Forced Color Adjust
       * @see https://tailwindcss.com/docs/forced-color-adjust
       */
      "forced-color-adjust": [{
        "forced-color-adjust": ["auto", "none"]
      }]
    },
    conflictingClassGroups: {
      overflow: ["overflow-x", "overflow-y"],
      overscroll: ["overscroll-x", "overscroll-y"],
      inset: ["inset-x", "inset-y", "start", "end", "top", "right", "bottom", "left"],
      "inset-x": ["right", "left"],
      "inset-y": ["top", "bottom"],
      flex: ["basis", "grow", "shrink"],
      gap: ["gap-x", "gap-y"],
      p: ["px", "py", "ps", "pe", "pt", "pr", "pb", "pl"],
      px: ["pr", "pl"],
      py: ["pt", "pb"],
      m: ["mx", "my", "ms", "me", "mt", "mr", "mb", "ml"],
      mx: ["mr", "ml"],
      my: ["mt", "mb"],
      size: ["w", "h"],
      "font-size": ["leading"],
      "fvn-normal": ["fvn-ordinal", "fvn-slashed-zero", "fvn-figure", "fvn-spacing", "fvn-fraction"],
      "fvn-ordinal": ["fvn-normal"],
      "fvn-slashed-zero": ["fvn-normal"],
      "fvn-figure": ["fvn-normal"],
      "fvn-spacing": ["fvn-normal"],
      "fvn-fraction": ["fvn-normal"],
      "line-clamp": ["display", "overflow"],
      rounded: ["rounded-s", "rounded-e", "rounded-t", "rounded-r", "rounded-b", "rounded-l", "rounded-ss", "rounded-se", "rounded-ee", "rounded-es", "rounded-tl", "rounded-tr", "rounded-br", "rounded-bl"],
      "rounded-s": ["rounded-ss", "rounded-es"],
      "rounded-e": ["rounded-se", "rounded-ee"],
      "rounded-t": ["rounded-tl", "rounded-tr"],
      "rounded-r": ["rounded-tr", "rounded-br"],
      "rounded-b": ["rounded-br", "rounded-bl"],
      "rounded-l": ["rounded-tl", "rounded-bl"],
      "border-spacing": ["border-spacing-x", "border-spacing-y"],
      "border-w": ["border-w-s", "border-w-e", "border-w-t", "border-w-r", "border-w-b", "border-w-l"],
      "border-w-x": ["border-w-r", "border-w-l"],
      "border-w-y": ["border-w-t", "border-w-b"],
      "border-color": ["border-color-s", "border-color-e", "border-color-t", "border-color-r", "border-color-b", "border-color-l"],
      "border-color-x": ["border-color-r", "border-color-l"],
      "border-color-y": ["border-color-t", "border-color-b"],
      "scroll-m": ["scroll-mx", "scroll-my", "scroll-ms", "scroll-me", "scroll-mt", "scroll-mr", "scroll-mb", "scroll-ml"],
      "scroll-mx": ["scroll-mr", "scroll-ml"],
      "scroll-my": ["scroll-mt", "scroll-mb"],
      "scroll-p": ["scroll-px", "scroll-py", "scroll-ps", "scroll-pe", "scroll-pt", "scroll-pr", "scroll-pb", "scroll-pl"],
      "scroll-px": ["scroll-pr", "scroll-pl"],
      "scroll-py": ["scroll-pt", "scroll-pb"],
      touch: ["touch-x", "touch-y", "touch-pz"],
      "touch-x": ["touch"],
      "touch-y": ["touch"],
      "touch-pz": ["touch"]
    },
    conflictingClassGroupModifiers: {
      "font-size": ["leading"]
    }
  };
}, nf = /* @__PURE__ */ Lc(sf);
function yo(...e) {
  return nf(Gi(e));
}
const of = ["disabled"], ce = /* @__PURE__ */ qe({
  __name: "Button",
  props: {
    variant: { default: "primary", type: null },
    size: { default: "md", type: null },
    class: { type: String },
    disabled: { type: Boolean, default: !1 }
  },
  emits: ["click"],
  setup(e, { emit: t }) {
    const s = e, n = t, o = he(
      () => yo(
        Cc({ variant: s.variant, size: s.size }),
        s.disabled && "pointer-events-none opacity-50",
        s.class
      )
    );
    function l(i) {
      s.disabled || n("click", i);
    }
    return (i, a) => (S(), M("button", {
      type: "button",
      class: ot(o.value),
      disabled: e.disabled,
      onClick: l
    }, [
      ss(i.$slots, "default")
    ], 10, of));
  }
});
function rf(e, t) {
  const s = `${e}Context`, n = Symbol(s);
  return [(i) => {
    const a = pn(n, i);
    if (a || a === null) return a;
    throw new Error(`Injection \`${n.toString()}\` not found. Component must be used within ${Array.isArray(e) ? `one of the following components: ${e.join(", ")}` : `\`${e}\``}`);
  }, (i) => (mi(n, i), i)];
}
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const lf = (e) => typeof e < "u";
function kr(e) {
  var t;
  const s = li(e);
  return (t = s == null ? void 0 : s.$el) !== null && t !== void 0 ? t : s;
}
function af(e) {
  return JSON.parse(JSON.stringify(e));
}
// @__NO_SIDE_EFFECTS__
function uf(e, t, s, n = {}) {
  var o, l;
  const { clone: i = !1, passive: a = !1, eventName: d, deep: m = !1, defaultValue: g, shouldEmit: x } = n, C = ps(), E = s || (C == null ? void 0 : C.emit) || (C == null || (o = C.$emit) === null || o === void 0 ? void 0 : o.bind(C)) || (C == null || (l = C.proxy) === null || l === void 0 || (l = l.$emit) === null || l === void 0 ? void 0 : l.bind(C == null ? void 0 : C.proxy));
  let U = d;
  U = U || `update:${t.toString()}`;
  const A = (D) => i ? typeof i == "function" ? i(D) : af(D) : D, w = () => lf(e[t]) ? A(e[t]) : g, H = (D) => {
    x ? x(D) && E(U, D) : E(U, D);
  };
  if (a) {
    const D = /* @__PURE__ */ L(w());
    let K = !1;
    return gt(() => e[t], (B) => {
      K || (K = !0, D.value = A(B), An(() => K = !1));
    }), gt(D, (B) => {
      !K && (B !== e[t] || m) && H(B);
    }, { deep: m }), D;
  } else return he({
    get() {
      return w();
    },
    set(D) {
      H(D);
    }
  });
}
function ta(e) {
  return e ? e.flatMap((t) => t.type === ue ? ta(t.children) : [t]) : [];
}
function df(e) {
  const t = ps(), s = t == null ? void 0 : t.type.emits, n = {};
  return s != null && s.length || console.warn(`No emitted event found. Please check component: ${t == null ? void 0 : t.type.__name}`), s == null || s.forEach((o) => {
    n[Kn(et(o))] = (...l) => e(o, ...l);
  }), n;
}
function cf(e) {
  return he(() => {
    var t;
    return li(e) ? !!((t = kr(e)) != null && t.closest("form")) : !0;
  });
}
function sa() {
  const e = ps(), t = /* @__PURE__ */ L(), s = he(() => n());
  yi(() => {
    s.value !== n() && Iu(t);
  });
  function n() {
    return t.value && "$el" in t.value && ["#text", "#comment"].includes(t.value.$el.nodeName) ? t.value.$el.nextElementSibling : kr(t);
  }
  const o = Object.assign({}, e.exposed), l = {};
  for (const a in e.props) Object.defineProperty(l, a, {
    enumerable: !0,
    configurable: !0,
    get: () => e.props[a]
  });
  if (Object.keys(o).length > 0) for (const a in o) Object.defineProperty(l, a, {
    enumerable: !0,
    configurable: !0,
    get: () => o[a]
  });
  Object.defineProperty(l, "$el", {
    enumerable: !0,
    configurable: !0,
    get: () => e.vnode.el
  }), e.exposed = l;
  function i(a) {
    if (t.value = a, !!a && (Object.defineProperty(l, "$el", {
      enumerable: !0,
      configurable: !0,
      get: () => a instanceof Element ? a : a.$el
    }), !(a instanceof Element) && !Object.hasOwn(a, "$el"))) {
      const d = a.$.exposed, m = Object.assign({}, l);
      for (const g in d) Object.defineProperty(m, g, {
        enumerable: !0,
        configurable: !0,
        get: () => d[g]
      });
      e.exposed = m;
    }
  }
  return {
    forwardRef: i,
    currentRef: t,
    currentElement: s
  };
}
function ff(e) {
  const t = ps(), s = Object.keys((t == null ? void 0 : t.type.props) ?? {}).reduce((o, l) => {
    const i = (t == null ? void 0 : t.type.props[l]).default;
    return i !== void 0 && (o[l] = i), o;
  }, {}), n = /* @__PURE__ */ Vu(e);
  return he(() => {
    const o = {}, l = (t == null ? void 0 : t.vnode.props) ?? {};
    return Object.keys(l).forEach((i) => {
      o[et(i)] = l[i];
    }), Object.keys({
      ...s,
      ...o
    }).reduce((i, a) => (n.value[a] !== void 0 && (i[a] = n.value[a]), i), {});
  });
}
function pf(e, t) {
  const s = ff(e), n = t ? df(t) : {};
  return he(() => ({
    ...s.value,
    ...n
  }));
}
function mf() {
  var t, s;
  const e = (s = (t = ps()) == null ? void 0 : t.vnode) == null ? void 0 : s.scopeId;
  return e ? { [e]: "" } : {};
}
const gf = /* @__PURE__ */ qe({
  name: "PrimitiveSlot",
  inheritAttrs: !1,
  setup(e, { attrs: t, slots: s }) {
    return () => {
      var d;
      if (!s.default) return null;
      const n = ta(s.default()), o = n.findIndex((m) => m.type !== $t);
      if (o === -1) return n;
      const l = n[o];
      (d = l.props) == null || delete d.ref;
      const i = l.props ? es(t, l.props) : t, a = fs({
        ...l,
        props: {}
      }, i);
      return n.length === 1 ? a : (n[o] = a, n);
    };
  }
}), hf = [
  "area",
  "img",
  "input"
], Sr = /* @__PURE__ */ qe({
  name: "Primitive",
  inheritAttrs: !1,
  props: {
    asChild: {
      type: Boolean,
      default: !1
    },
    as: {
      type: [String, Object],
      default: "div"
    }
  },
  setup(e, { attrs: t, slots: s }) {
    const n = e.asChild ? "template" : e.as;
    return typeof n == "string" && hf.includes(n) ? () => Do(n, t) : n !== "template" ? () => Do(e.as, t, { default: s.default }) : () => Do(gf, t, { default: s.default });
  }
});
function bf() {
  const e = /* @__PURE__ */ L(), t = he(() => {
    var s, n;
    return ["#text", "#comment"].includes((s = e.value) == null ? void 0 : s.$el.nodeName) ? (n = e.value) == null ? void 0 : n.$el.nextElementSibling : kr(e);
  });
  return {
    primitiveElement: e,
    currentElement: t
  };
}
var vf = /* @__PURE__ */ qe({
  __name: "VisuallyHidden",
  props: {
    feature: {
      type: String,
      required: !1,
      default: "focusable"
    },
    asChild: {
      type: Boolean,
      required: !1
    },
    as: {
      type: null,
      required: !1,
      default: "span"
    }
  },
  setup(e) {
    return (t, s) => (S(), Ie(h(Sr), {
      as: t.as,
      "as-child": t.asChild,
      "aria-hidden": t.feature === "focusable" || t.feature === "fully-hidden" ? "true" : void 0,
      "data-hidden": t.feature === "fully-hidden" ? "" : void 0,
      tabindex: t.feature === "fully-hidden" ? "-1" : void 0,
      style: {
        position: "absolute",
        border: 0,
        width: "1px",
        height: "1px",
        padding: 0,
        margin: "-1px",
        overflow: "hidden",
        clip: "rect(0, 0, 0, 0)",
        clipPath: "inset(50%)",
        whiteSpace: "nowrap",
        wordWrap: "normal",
        top: "-1px",
        left: "-1px"
      }
    }, {
      default: k(() => [ss(t.$slots, "default")]),
      _: 3
    }, 8, [
      "as",
      "as-child",
      "aria-hidden",
      "data-hidden",
      "tabindex"
    ]));
  }
}), yf = vf, xf = /* @__PURE__ */ qe({
  inheritAttrs: !1,
  __name: "VisuallyHiddenInputBubble",
  props: {
    name: {
      type: String,
      required: !0
    },
    value: {
      type: null,
      required: !0
    },
    checked: {
      type: Boolean,
      required: !1,
      default: void 0
    },
    required: {
      type: Boolean,
      required: !1
    },
    disabled: {
      type: Boolean,
      required: !1
    },
    feature: {
      type: String,
      required: !1,
      default: "fully-hidden"
    }
  },
  setup(e) {
    const t = e, { primitiveElement: s, currentElement: n } = bf(), o = he(() => t.checked ?? t.value);
    return gt(o, (l, i) => {
      if (!n.value) return;
      const a = n.value, d = window.HTMLInputElement.prototype, g = Object.getOwnPropertyDescriptor(d, "value").set;
      if (g && l !== i) {
        const x = new Event("input", { bubbles: !0 }), C = new Event("change", { bubbles: !0 });
        g.call(a, l), a.dispatchEvent(x), a.dispatchEvent(C);
      }
    }), (l, i) => (S(), Ie(yf, es({
      ref_key: "primitiveElement",
      ref: s
    }, {
      ...t,
      ...l.$attrs
    }, { as: "input" }), null, 16));
  }
}), $l = xf, _f = /* @__PURE__ */ qe({
  inheritAttrs: !1,
  __name: "VisuallyHiddenInput",
  props: {
    name: {
      type: String,
      required: !0
    },
    value: {
      type: null,
      required: !0
    },
    checked: {
      type: Boolean,
      required: !1,
      default: void 0
    },
    required: {
      type: Boolean,
      required: !1
    },
    disabled: {
      type: Boolean,
      required: !1
    },
    feature: {
      type: String,
      required: !1,
      default: "fully-hidden"
    }
  },
  setup(e) {
    const t = e, s = he(() => typeof t.value == "object" && Array.isArray(t.value) && t.value.length === 0 && t.required), n = he(() => typeof t.value == "string" || typeof t.value == "number" || typeof t.value == "boolean" || t.value === null || t.value === void 0 ? [{
      name: t.name,
      value: t.value
    }] : typeof t.value == "object" && Array.isArray(t.value) ? t.value.flatMap((o, l) => typeof o == "object" ? Object.entries(o).map(([i, a]) => ({
      name: `${t.name}[${l}][${i}]`,
      value: a
    })) : {
      name: `${t.name}[${l}]`,
      value: o
    }) : t.value !== null && typeof t.value == "object" && !Array.isArray(t.value) ? Object.entries(t.value).map(([o, l]) => ({
      name: `${t.name}[${o}]`,
      value: l
    })) : []);
    return (o, l) => (S(), M(ue, null, [z(" We render single input if it's required "), s.value ? (S(), Ie($l, es({ key: o.name }, {
      ...t,
      ...o.$attrs
    }, {
      name: o.name,
      value: o.value
    }), null, 16, ["name", "value"])) : (S(!0), M(ue, { key: 1 }, Ye(n.value, (i) => (S(), Ie($l, es({ key: i.name }, { ref_for: !0 }, {
      ...t,
      ...o.$attrs
    }, {
      name: i.name,
      value: i.value
    }), null, 16, ["name", "value"]))), 128))], 2112));
  }
}), wf = _f;
const [kf, Sf] = /* @__PURE__ */ rf("SwitchRoot");
var Cf = /* @__PURE__ */ qe({
  inheritAttrs: !1,
  __name: "SwitchRoot",
  props: {
    defaultValue: {
      type: null,
      required: !1
    },
    modelValue: {
      type: null,
      required: !1,
      default: void 0
    },
    disabled: {
      type: Boolean,
      required: !1
    },
    id: {
      type: String,
      required: !1
    },
    value: {
      type: String,
      required: !1,
      default: "on"
    },
    trueValue: {
      type: null,
      required: !1,
      default: () => !0
    },
    falseValue: {
      type: null,
      required: !1,
      default: () => !1
    },
    asChild: {
      type: Boolean,
      required: !1
    },
    as: {
      type: null,
      required: !1,
      default: "button"
    },
    name: {
      type: String,
      required: !1
    },
    required: {
      type: Boolean,
      required: !1
    }
  },
  emits: ["update:modelValue"],
  setup(e, { emit: t }) {
    const s = e, n = t, { disabled: o } = /* @__PURE__ */ Pu(s), l = /* @__PURE__ */ uf(s, "modelValue", n, {
      defaultValue: s.defaultValue ?? s.falseValue,
      passive: s.modelValue === void 0
    }), i = he(() => l.value === s.trueValue);
    function a() {
      o.value || (l.value = i.value ? s.falseValue : s.trueValue);
    }
    const { forwardRef: d, currentElement: m } = sa(), g = cf(m), x = mf(), C = he(() => {
      var E;
      return s.id && m.value ? (E = document.querySelector(`[for="${s.id}"]`)) == null ? void 0 : E.innerText : void 0;
    });
    return Sf({
      checked: i,
      toggleCheck: a,
      disabled: o
    }), (E, U) => (S(), M(ue, null, [v(h(Sr), es({
      id: E.id,
      ref: h(d),
      role: "switch",
      type: E.as === "button" ? "button" : void 0,
      value: E.value,
      "aria-label": E.$attrs["aria-label"] || C.value,
      "aria-checked": i.value,
      "aria-required": E.required,
      "data-state": i.value ? "checked" : "unchecked",
      "data-disabled": h(o) ? "" : void 0,
      "as-child": E.asChild,
      as: E.as,
      disabled: h(o)
    }, {
      ...h(x),
      ...E.$attrs
    }, {
      onClick: a,
      onKeydown: un(an(a, ["prevent"]), ["enter"])
    }), {
      default: k(() => [ss(E.$slots, "default", {
        modelValue: h(l),
        checked: i.value
      })]),
      _: 3
    }, 16, [
      "id",
      "type",
      "value",
      "aria-label",
      "aria-checked",
      "aria-required",
      "data-state",
      "data-disabled",
      "as-child",
      "as",
      "disabled",
      "onKeydown"
    ]), h(g) && E.name ? (S(), Ie(h(wf), es({
      key: 0,
      type: "checkbox",
      name: E.name,
      disabled: h(o),
      required: E.required,
      value: E.value,
      checked: i.value
    }, h(x)), null, 16, [
      "name",
      "disabled",
      "required",
      "value",
      "checked"
    ])) : z("v-if", !0)], 64));
  }
}), Af = Cf, Ef = /* @__PURE__ */ qe({
  __name: "SwitchThumb",
  props: {
    asChild: {
      type: Boolean,
      required: !1
    },
    as: {
      type: null,
      required: !1,
      default: "span"
    }
  },
  setup(e) {
    const t = kf();
    return sa(), (s, n) => (S(), Ie(h(Sr), {
      "data-state": h(t).checked.value ? "checked" : "unchecked",
      "data-disabled": h(t).disabled.value ? "" : void 0,
      "as-child": s.asChild,
      as: s.as
    }, {
      default: k(() => [ss(s.$slots, "default")]),
      _: 3
    }, 8, [
      "data-state",
      "data-disabled",
      "as-child",
      "as"
    ]));
  }
}), If = Ef;
const on = /* @__PURE__ */ qe({
  __name: "Switch",
  props: {
    defaultValue: { type: null },
    modelValue: { type: null },
    disabled: { type: Boolean },
    id: { type: String },
    value: { type: String },
    trueValue: { type: null },
    falseValue: { type: null },
    asChild: { type: Boolean },
    as: { type: null },
    name: { type: String },
    required: { type: Boolean },
    class: { type: String }
  },
  emits: ["update:modelValue"],
  setup(e, { emit: t }) {
    const s = e, n = t, o = he(() => {
      const { class: i, ...a } = s;
      return a;
    }), l = pf(o, n);
    return (i, a) => (S(), Ie(h(Af), es(h(l), {
      as: "span",
      tabindex: s.disabled ? -1 : 0,
      class: h(yo)(
        "peer focus-visible:ring-ring focus-visible:ring-offset-background data-[state=checked]:bg-primary data-[state=unchecked]:bg-input inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50",
        s.class
      )
    }), {
      default: k(() => [
        v(h(If), { class: "bg-background pointer-events-none block h-5 w-5 rounded-full shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0" })
      ]),
      _: 1
    }, 16, ["tabindex", "class"]));
  }
}), Tf = Ji(
  "inline-flex items-center rounded-full font-semibold leading-tight transition-all duration-200 ease-in-out h-fit",
  {
    variants: {
      variant: {
        green: "bg-unraid-green-200 text-unraid-green-800",
        red: "bg-unraid-red text-white",
        gray: "bg-gray-200 text-gray-800",
        orange: "bg-orange text-white"
      },
      size: {
        sm: "text-sm px-2 py-1 gap-2",
        md: "text-base px-3 py-2 gap-2"
      }
    },
    defaultVariants: {
      variant: "gray",
      size: "sm"
    }
  }
), Lt = /* @__PURE__ */ qe({
  __name: "Badge",
  props: {
    variant: { default: "gray", type: null },
    size: { default: "sm", type: null },
    class: { default: "", type: String }
  },
  setup(e) {
    const t = e, s = he(() => Tf({ variant: t.variant, size: t.size }));
    return (n, o) => (S(), M("span", {
      class: ot([s.value, t.class])
    }, [
      ss(n.$slots, "default")
    ], 2));
  }
});
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Pf = (e) => typeof e < "u";
function Rf(e) {
  return JSON.parse(JSON.stringify(e));
}
// @__NO_SIDE_EFFECTS__
function na(e, t, s, n = {}) {
  var o, l, i;
  const {
    clone: a = !1,
    passive: d = !1,
    eventName: m,
    deep: g = !1,
    defaultValue: x,
    shouldEmit: C
  } = n, E = ps(), U = s || (E == null ? void 0 : E.emit) || ((o = E == null ? void 0 : E.$emit) == null ? void 0 : o.bind(E)) || ((i = (l = E == null ? void 0 : E.proxy) == null ? void 0 : l.$emit) == null ? void 0 : i.bind(E == null ? void 0 : E.proxy));
  let A = m;
  A = A || `update:${t.toString()}`;
  const w = (K) => a ? typeof a == "function" ? a(K) : Rf(K) : K, H = () => Pf(e[t]) ? w(e[t]) : x, D = (K) => {
    C ? C(K) && U(A, K) : U(A, K);
  };
  if (d) {
    const K = H(), B = /* @__PURE__ */ L(K);
    let Q = !1;
    return gt(
      () => e[t],
      (je) => {
        Q || (Q = !0, B.value = w(je), An(() => Q = !1));
      }
    ), gt(
      B,
      (je) => {
        !Q && (je !== e[t] || g) && D(je);
      },
      { deep: g }
    ), B;
  } else
    return he({
      get() {
        return H();
      },
      set(K) {
        D(K);
      }
    });
}
const Mf = ["type", "placeholder"], pe = /* @__PURE__ */ qe({
  __name: "Input",
  props: {
    defaultValue: { type: [String, Number] },
    modelValue: { type: [String, Number] },
    type: { type: String },
    placeholder: { type: String },
    class: { type: String }
  },
  emits: ["update:modelValue"],
  setup(e, { emit: t }) {
    const s = e, o = /* @__PURE__ */ na(s, "modelValue", t, {
      passive: !0,
      defaultValue: s.defaultValue
    });
    return (l, i) => mr((S(), M("input", {
      "onUpdate:modelValue": i[0] || (i[0] = (a) => /* @__PURE__ */ Ue(o) ? o.value = a : null),
      type: e.type ?? "text",
      placeholder: e.placeholder,
      class: ot(
        h(yo)(
          "border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50",
          s.class
        )
      )
    }, null, 10, Mf)), [
      [hc, h(o)]
    ]);
  }
}), Vf = ["id", "disabled"], ws = /* @__PURE__ */ qe({
  __name: "Select",
  props: {
    modelValue: { type: String },
    class: { type: String },
    id: { type: String },
    disabled: { type: Boolean }
  },
  emits: ["update:modelValue"],
  setup(e, { emit: t }) {
    const s = e, o = /* @__PURE__ */ na(s, "modelValue", t, { passive: !0 });
    return (l, i) => (S(), M("div", {
      class: ot(h(yo)("relative inline-block", s.class))
    }, [
      mr(p("select", {
        id: e.id,
        "onUpdate:modelValue": i[0] || (i[0] = (a) => /* @__PURE__ */ Ue(o) ? o.value = a : null),
        disabled: e.disabled,
        class: "border-input bg-background ring-offset-background focus-visible:ring-ring h-10 w-full cursor-pointer appearance-none rounded-md border py-2 pr-8 pl-3 text-sm focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50"
      }, [
        ss(l.$slots, "default")
      ], 8, Vf), [
        [zi, h(o)]
      ]),
      i[1] || (i[1] = p("svg", {
        class: "text-muted-foreground pointer-events-none absolute top-1/2 right-2.5 -translate-y-1/2",
        width: "10",
        height: "6",
        viewBox: "0 0 10 6",
        fill: "none",
        "aria-hidden": "true"
      }, [
        p("path", {
          d: "M1 1L5 5L9 1",
          stroke: "currentColor",
          "stroke-width": "1.5",
          "stroke-linecap": "round",
          "stroke-linejoin": "round"
        })
      ], -1))
    ], 2));
  }
}), $f = ["for"], ne = /* @__PURE__ */ qe({
  __name: "Label",
  props: {
    for: { type: String },
    class: { type: String }
  },
  setup(e) {
    return (t, s) => (S(), M("label", {
      for: t.$props.for,
      class: ot(["text-sm leading-none font-medium", t.$props.class])
    }, [
      ss(t.$slots, "default")
    ], 10, $f));
  }
}), Of = { class: "inline_help" }, oe = /* @__PURE__ */ qe({
  __name: "HelpText",
  setup(e) {
    return (t, s) => (S(), M("blockquote", Of, [
      ss(t.$slots, "default")
    ]));
  }
});
class oa extends Error {
  constructor(t, s) {
    super(t), this.errors = s;
  }
}
let Ol = null;
function jf() {
  return window.csrf_token ? Promise.resolve() : (Ol ?? (Ol = new Promise((e) => {
    const t = Date.now() + 2e3, s = () => {
      window.csrf_token || Date.now() >= t ? e() : setTimeout(s, 20);
    };
    s();
  })), Ol);
}
async function jl(e, t) {
  var o, l;
  const s = await fetch("/graphql", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "x-csrf-token": window.csrf_token ?? ""
    },
    body: JSON.stringify({ query: e, variables: t })
  });
  if (!s.ok)
    throw new Error(`GraphQL request failed: HTTP ${s.status}`);
  const n = await s.json();
  if ((o = n.errors) != null && o.length)
    throw new oa(((l = n.errors[0]) == null ? void 0 : l.message) ?? "GraphQL error", n.errors);
  return n.data;
}
const Nf = (e) => new Promise((t) => setTimeout(t, e));
function Lf(e) {
  const t = e.replace(/^\s*(?:#[^\n]*\n\s*)*/, "");
  return t.startsWith("query") || t.startsWith("{");
}
async function ve(e, t) {
  await jf();
  try {
    return await jl(e, t);
  } catch (s) {
    if (s instanceof oa || !Lf(e)) throw s;
    return await Nf(300), jl(e, t);
  }
}
function Wn(e, t, s = {}) {
  let n = !1, o = null, l = null;
  const i = typeof document > "u" ? null : document, a = () => {
    n || (l = setTimeout(() => void d(), t));
  }, d = async () => {
    if (!n) {
      if (i != null && i.hidden) {
        a();
        return;
      }
      return o || (o = e().catch((g) => {
        var x;
        return (x = s.onError) == null ? void 0 : x.call(s, g);
      }).finally(() => {
        o = null, a();
      }), o);
    }
  };
  s.immediate ? d() : a();
  const m = () => {
    !(i != null && i.hidden) && !n && !o && (l && clearTimeout(l), l = null, d());
  };
  return i == null || i.addEventListener("visibilitychange", m), {
    stop() {
      n = !0, l && clearTimeout(l), l = null, i == null || i.removeEventListener("visibilitychange", m);
    },
    trigger: d
  };
}
function Uf(e, t) {
  const { tsAuthKeyConfigured: s, ...n } = e;
  return t.clear ? { ...n, tsAuthKey: "" } : t.replacement ? { ...n, tsAuthKey: t.replacement } : n;
}
function Df(e, t) {
  const s = /* @__PURE__ */ zt(/* @__PURE__ */ new Map()), n = /* @__PURE__ */ zt(/* @__PURE__ */ new Map()), o = /* @__PURE__ */ L([]), l = /* @__PURE__ */ zt(/* @__PURE__ */ new Map()), i = 30, a = he(() => e.value.filter((W) => W.status.toLowerCase() === "running")), d = he(() => e.value.length - a.value.length), m = he(() => a.value.reduce((W, te) => W + Number(te.memoryUsageBytes ?? 0), 0)), g = he(() => a.value.reduce((W, te) => W + BigInt(te.cpuUsageNs ?? "0"), 0n));
  function x(W) {
    if (W == null) return "—";
    const te = Math.floor(W / 1e9), Re = Math.floor(te / 3600), _e = Math.floor(te % 3600 / 60), $e = te % 60;
    return Re > 0 ? `${Re}h ${_e}m ${$e}s` : _e > 0 ? `${_e}m ${$e}s` : `${$e}s`;
  }
  function C(W) {
    if (W == null) return "—";
    if (W === 0) return "0 B";
    const te = ["B", "KiB", "MiB", "GiB", "TiB"], Re = Math.min(Math.floor(Math.log(W) / Math.log(1024)), te.length - 1), _e = W / 1024 ** Re;
    return `${_e >= 10 || Re === 0 ? Math.round(_e) : _e.toFixed(1)} ${te[Re]}`;
  }
  function E(W) {
    if (W.memoryUsageBytes == null) return "—";
    const te = C(Number(W.memoryUsageBytes));
    return W.memoryTotalBytes ? `${te} / ${C(Number(W.memoryTotalBytes))}` : te;
  }
  function U(W) {
    return !W.memoryTotalBytes || W.memoryUsageBytes == null ? null : Math.min(100, Math.round(Number(W.memoryUsageBytes) / Number(W.memoryTotalBytes) * 100));
  }
  function A() {
    const W = t().trim();
    if (!/^\d+$/.test(W)) return null;
    const te = Number(W);
    return te > 0 ? te : null;
  }
  function w() {
    const W = Date.now();
    let te = 0, Re = !1, _e = 0, $e = 0;
    for (const xe of e.value) {
      if (xe.cpuUsageNs == null) {
        s.delete(xe.name), l.delete(xe.name);
        continue;
      }
      const He = BigInt(xe.cpuUsageNs), bt = s.get(xe.name);
      if (bt) {
        const we = He - bt.cpuUsageNs, fe = W - bt.atMs;
        if (we >= 0n && fe > 0) {
          const se = Number(we) / (fe * 1e6) * 100;
          l.set(xe.name, se);
          const Me = U(xe), De = n.get(xe.name) ?? [];
          De.push({ atMs: W, cpuPct: se, memPct: Me }), De.length > i && De.shift(), n.set(xe.name, De), xe.status.toLowerCase() === "running" && (te += se, Re = !0, Me !== null && (_e += Me, $e++));
        } else l.delete(xe.name);
      } else l.delete(xe.name);
      s.set(xe.name, { atMs: W, cpuUsageNs: He });
    }
    const re = new Set(e.value.map((xe) => xe.name));
    for (const xe of [s, n, l])
      for (const He of Array.from(xe.keys())) re.has(He) || xe.delete(He);
    Re && (o.value.push({ atMs: W, cpuPct: te, memPct: $e ? _e / $e : null }), o.value.length > i && o.value.shift());
  }
  return {
    runningJails: a,
    stoppedJailsCount: d,
    totalMemoryUsageBytes: m,
    totalCpuUsageNs: g,
    fleetHistory: o,
    formatDuration: x,
    formatBytes: C,
    formatMemory: E,
    memoryFillPct: U,
    updateCpuSamplesAndHistory: w,
    cpuRateLabel: (W) => l.has(W.name) ? `${l.get(W.name).toFixed(l.get(W.name) < 10 ? 1 : 0)}%` : "—",
    cpuRatePct: (W) => {
      const te = l.get(W.name);
      return te === void 0 ? null : Math.min(100, Math.max(0, Math.round(A() ? te / A() : te)));
    },
    cpuRateSuffix: () => A() ? `of ${A()} core${A() === 1 ? "" : "s"}` : "of 1 core",
    jailCpuHistory: (W) => n.get(W) ?? [],
    totalCpuRateLabel: () => o.value.length ? `${o.value.at(-1).cpuPct.toFixed(o.value.at(-1).cpuPct < 10 ? 1 : 0)}%` : "—",
    sparklinePoints: (W, te, Re = 80, _e = 24) => W.map(($e, re) => $e[te] === null ? null : `${(re * (Re / Math.max(1, W.length - 1))).toFixed(1)},${(_e - Math.min(100, Math.max(0, $e[te])) / 100 * _e).toFixed(1)}`).filter(Boolean).join(" ")
  };
}
const Bf = `query { incusConfig {
  enabled stateDir storageDriver storageSource storagePoolName jailBridge jailSubnet jailNat jailIpv6
  aclName aclBlock aclAllow aclDefaultEgress aclDefaultIngress jailProfile jailImage jailNesting jailCpu jailMemory
  jailWorkspaceRoot jailAgentUid jailAgentGid jailBindMounts tsAuthKeyConfigured dashboardWidgetEnable
} }`, Ff = "query { incusHealthy jails { name status ipv4 cpuUsageNs memoryUsageBytes memoryTotalBytes } }", Nl = "mutation($input: IncusConfigInput!) { updateIncusConfig(input: $input) { enabled } }", Hf = "mutation($name: String!, $action: JailAction!) { setJailState(name: $name, action: $action) }", zf = "mutation($name: String!) { deleteJail(name: $name) }", Wf = "mutation($name: String!, $image: String, $allowSudo: Boolean) { launchJail(name: $name, image: $image, allowSudo: $allowSudo) }", Kf = "query($name: String!) { jailDetail(name: $name) { name profiles imageOs imageRelease imageDescription storagePool networkBridge cpuLimit cpuLimitIsOverride memoryLimit memoryLimitIsOverride workspaceHostPath workspaceIsOverride sudoEnabled } }", qf = "mutation($name: String!) { grantJailSudo(name: $name) }", Gf = "mutation($name: String!, $command: String!) { startPrivilegedCommand(name: $name, command: $command) }", Jf = "query($id: String!) { privilegedCommandStatus(id: $id) { id command status exitCode stdout stderr message } }", Yf = "mutation($name: String!, $hostPath: String!) { setJailWorkspace(name: $name, hostPath: $hostPath) }", Qf = "mutation($name: String!) { clearJailWorkspace(name: $name) }", zo = "mutation($name: String!, $cpu: String, $memory: String) { setJailLimits(name: $name, cpu: $cpu, memory: $memory) }", Zf = "mutation($distro: String!, $release: String!, $packages: [String!]!, $alias: String!, $basedOn: String, $postInstallCommands: [String!]) { buildJailImage(distro: $distro, release: $release, packages: $packages, alias: $alias, basedOn: $basedOn, postInstallCommands: $postInstallCommands) }", Xf = "mutation($alias: String!) { deleteJailImage(alias: $alias) }", ep = "query($query: String!, $distro: String, $release: String) { searchAllPackages(query: $query, distro: $distro, release: $release) { results { ecosystem name description version } errors { ecosystem message } } }", tp = "query($buildId: String!) { jailImageBuildStatus(buildId: $buildId) { id status alias distro release packages logTail error } }", sp = "query { builderPresets { name distro release packages } }", np = "mutation($input: BuilderPresetInput!) { saveBuilderPreset(input: $input) { name } }", op = "mutation($name: String!) { deleteBuilderPreset(name: $name) }", rp = "query { jailImages { alias distro release packages isMaster basedOn createdAt } }", lp = "mutation($alias: String!, $isMaster: Boolean!) { setMasterImage(alias: $alias, isMaster: $isMaster) { alias isMaster } }", ip = "mutation { pruneStaleImageRecords }", ap = "mutation { deleteStoppedJails }", up = "mutation($name: String!) { migrateJailWorkspace(name: $name) }", dp = "mutation($name: String!, $formula: String!) { installHomebrewFormula(name: $name, formula: $formula) }", cp = "query($id: String!) { homebrewInstallStatus(id: $id) { id formula status message } }", fp = { class: "unapi w-full max-w-4xl text-foreground xl:max-w-6xl 2xl:max-w-[1600px] min-[1920px]:max-w-[1880px] min-[2560px]:max-w-[2200px]" }, pp = {
  key: 0,
  class: "py-8 text-muted-foreground"
}, mp = {
  key: 0,
  class: "mb-4 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
}, gp = { class: "mb-6 flex items-center gap-3 border-b border-border pb-4" }, hp = { class: "ml-auto flex items-center gap-3" }, bp = { class: "mb-6 flex gap-1 border-b border-border" }, vp = ["onClick"], yp = { key: 1 }, xp = { class: "grid grid-cols-1 items-start gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]" }, _p = { class: "mb-6 rounded-lg border border-border bg-card p-4 xl:mb-0" }, wp = {
  key: 0,
  class: "mb-3 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, kp = {
  key: 1,
  class: "text-sm text-muted-foreground"
}, Sp = {
  key: 2,
  class: "mb-3 flex flex-wrap gap-2"
}, Cp = ["onClick"], Ap = { class: "font-mono text-muted-foreground" }, Ep = ["onClick"], Ip = { class: "flex gap-2" }, Tp = { class: "mt-5 border-t border-border pt-4" }, Pp = { class: "mb-2 flex items-center justify-between gap-3" }, Rp = {
  key: 0,
  class: "mb-3 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, Mp = {
  key: 1,
  class: "mb-3 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs"
}, Vp = {
  key: 2,
  class: "text-sm text-muted-foreground"
}, $p = {
  key: 3,
  class: "flex flex-col gap-2"
}, Op = { class: "min-w-0 flex-1" }, jp = { class: "flex items-center gap-2" }, Np = { class: "font-mono text-[13px] font-medium" }, Lp = { class: "text-xs text-muted-foreground" }, Up = { class: "mt-0.5 truncate text-xs text-muted-foreground" }, Dp = { class: "mt-5 border-t border-border pt-4" }, Bp = {
  key: 0,
  class: "mt-3 flex flex-col gap-4"
}, Fp = {
  key: 0,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, Hp = {
  key: 1,
  class: "mt-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs"
}, zp = {
  key: 0,
  class: "text-foreground"
}, Wp = {
  key: 1,
  class: "mt-1"
}, Kp = { class: "font-mono" }, qp = {
  key: 2,
  class: "mt-1"
}, Gp = {
  key: 3,
  class: "mt-1"
}, Jp = { class: "ml-4 list-disc text-muted-foreground" }, Yp = { class: "border-t border-border pt-4" }, Qp = { class: "flex gap-2" }, Zp = {
  key: 0,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, Xp = {
  key: 1,
  class: "mt-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs"
}, em = { class: "font-mono" }, tm = { class: "border-t border-border pt-4" }, sm = { class: "flex flex-wrap gap-2" }, nm = { class: "mb-6 rounded-lg border border-border bg-card p-4" }, om = {
  key: 0,
  class: "mb-4 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
}, rm = {
  key: 1,
  class: "mb-4 flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-3 py-2 text-xs"
}, lm = { class: "font-mono font-medium" }, im = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, am = { class: "flex justify-self-end gap-2" }, um = ["value"], dm = { class: "flex justify-self-end gap-2" }, cm = ["value"], fm = { class: "mt-5 border-t border-border pt-4" }, pm = {
  key: 0,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, mm = {
  key: 1,
  class: "mt-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs text-muted-foreground"
}, gm = {
  key: 2,
  class: "mt-2 text-xs text-muted-foreground"
}, hm = {
  key: 3,
  class: "mt-2 flex max-h-64 flex-col gap-1 overflow-y-auto"
}, bm = { class: "min-w-0 flex-1" }, vm = { class: "font-mono font-medium" }, ym = {
  key: 0,
  class: "ml-1.5 font-mono text-muted-foreground"
}, xm = {
  key: 1,
  class: "truncate text-muted-foreground"
}, _m = {
  key: 1,
  class: "shrink-0 text-muted-foreground"
}, wm = {
  key: 4,
  class: "mt-2 text-xs text-muted-foreground"
}, km = {
  key: 5,
  class: "mt-3"
}, Sm = { class: "flex flex-wrap gap-1.5" }, Cm = ["onClick"], Am = {
  key: 6,
  class: "mt-3"
}, Em = { class: "flex flex-col gap-1" }, Im = { class: "flex-1" }, Tm = ["onClick"], Pm = { class: "mt-4" }, Rm = { class: "mt-4 flex justify-end" }, Mm = { class: "rounded-lg border border-border bg-card p-4" }, Vm = {
  key: 0,
  class: "flex items-center gap-2 rounded-md border border-neutral-800 bg-neutral-950 px-3 py-2.5"
}, $m = {
  key: 1,
  class: "flex flex-col gap-4"
}, Om = { class: "mb-2 flex items-center justify-between gap-3" }, jm = { class: "flex items-center gap-2" }, Nm = { class: "text-sm font-medium" }, Lm = { class: "text-xs text-muted-foreground" }, Um = {
  key: 0,
  class: "mb-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, Dm = { class: "flex items-center gap-2 rounded-t-md border border-b-0 border-neutral-800 bg-neutral-950 px-3 py-1.5" }, Bm = { class: "font-mono text-[11px] text-neutral-400" }, Fm = { class: "max-h-48 overflow-auto rounded-b-md border border-neutral-800 bg-neutral-950 p-2.5 text-xs font-mono whitespace-pre-wrap text-neutral-200" }, Hm = { key: 2 }, zm = { class: "mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6" }, Wm = { class: "rounded-lg border border-border bg-card p-3" }, Km = { class: "mt-1 font-mono text-xl" }, qm = { class: "rounded-lg border border-border bg-card p-3" }, Gm = { class: "mt-1 font-mono text-xl" }, Jm = { class: "rounded-lg border border-border bg-card p-3" }, Ym = { class: "mt-1 font-mono text-xl" }, Qm = { class: "rounded-lg border border-border bg-card p-3" }, Zm = { class: "mt-1.5" }, Xm = { class: "rounded-lg border border-border bg-card p-3" }, eg = { class: "mt-1 font-mono text-xl" }, tg = { class: "rounded-lg border border-border bg-card p-3" }, sg = { class: "mt-1 font-mono text-xl" }, ng = {
  key: 0,
  viewBox: "0 0 80 24",
  width: "80",
  height: "24",
  class: "mt-1 text-primary",
  preserveAspectRatio: "none"
}, og = ["points"], rg = { class: "mb-6 grid grid-cols-1 items-start gap-4 xl:grid-cols-2" }, lg = { class: "rounded-lg border border-border bg-card p-4" }, ig = { class: "grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-2 2xl:grid-cols-3" }, ag = { class: "mt-1 font-mono text-sm" }, ug = { class: "mt-1 font-mono text-sm" }, dg = { class: "mt-1 font-mono text-sm" }, cg = { class: "mt-1 font-mono text-sm" }, fg = { class: "mt-1 font-mono text-sm" }, pg = { class: "rounded-lg border border-border bg-card p-4" }, mg = { class: "flex flex-col gap-3 sm:flex-row sm:items-end" }, gg = { class: "flex-1" }, hg = { class: "flex-1" }, bg = { value: "" }, vg = ["value"], yg = {
  key: 0,
  class: "mt-2 text-xs text-destructive"
}, xg = { class: "mt-3 flex items-center gap-2.5" }, _g = { class: "rounded-lg border border-border bg-card p-4" }, wg = { class: "mb-4 flex items-center justify-between gap-3" }, kg = {
  key: 0,
  class: "text-sm text-muted-foreground"
}, Sg = { class: "mb-3 text-xs text-muted-foreground" }, Cg = { class: "grid grid-cols-1 gap-4 xl:grid-cols-2" }, Ag = { class: "flex flex-wrap items-center justify-between gap-2" }, Eg = { class: "flex min-w-0 items-center gap-2" }, Ig = { class: "truncate font-mono text-[13px] font-medium" }, Tg = {
  key: 0,
  class: "shrink-0 inline-flex items-center rounded-full bg-unraid-green-200 px-1.5 py-0.5 text-[10px] font-semibold text-unraid-green-800",
  title: "This container's IPv4 falls within the configured subnet."
}, Pg = { class: "shrink-0 font-mono text-xs text-muted-foreground" }, Rg = { class: "mt-3 grid grid-cols-2 gap-3" }, Mg = ["title"], Vg = { class: "mt-1 flex items-center gap-2" }, $g = { class: "h-1.5 w-16 overflow-hidden rounded-full bg-muted" }, Og = { class: "font-mono text-[13px]" }, jg = {
  key: 0,
  viewBox: "0 0 80 24",
  width: "60",
  height: "18",
  class: "text-primary",
  preserveAspectRatio: "none"
}, Ng = ["points"], Lg = { class: "mt-1 flex items-center gap-2" }, Ug = { class: "font-mono text-[13px]" }, Dg = {
  key: 0,
  viewBox: "0 0 80 24",
  width: "60",
  height: "18",
  class: "text-primary",
  preserveAspectRatio: "none"
}, Bg = ["points"], Fg = {
  key: 0,
  class: "mt-1 h-1 w-20 overflow-hidden rounded-full bg-muted"
}, Hg = { class: "mt-3 flex flex-wrap gap-2" }, zg = {
  key: 0,
  class: "mt-3 rounded-md border border-border bg-muted/30 p-3"
}, Wg = {
  key: 0,
  class: "text-xs text-muted-foreground"
}, Kg = { class: "grid grid-cols-2 gap-3 sm:grid-cols-4" }, qg = { class: "mt-1 font-mono text-xs" }, Gg = { class: "mt-1 font-mono text-xs" }, Jg = { class: "mt-1 font-mono text-xs" }, Yg = { class: "mt-1 font-mono text-xs" }, Qg = { class: "mt-4 grid grid-cols-1 gap-3 border-t border-border pt-3 sm:grid-cols-2" }, Zg = { class: "flex flex-wrap items-end gap-2" }, Xg = { class: "flex gap-1.5" }, eh = { class: "flex gap-1.5" }, th = { class: "flex gap-2" }, sh = {
  key: 0,
  class: "mt-3 flex flex-wrap items-center gap-3 rounded-md border border-orange-500/40 bg-orange-500/10 px-3 py-2 text-xs"
}, nh = {
  key: 1,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, oh = { class: "mt-4 border-t border-border pt-3" }, rh = { class: "mb-1 flex items-center gap-1.5 text-xs font-medium" }, lh = { class: "mt-4 border-t border-border pt-3" }, ih = { class: "flex flex-wrap gap-2" }, ah = {
  key: 0,
  class: "mt-1.5 text-xs text-unraid-green-800"
}, uh = {
  key: 1,
  class: "mt-1.5 text-xs text-destructive"
}, dh = { class: "mt-4 border-t border-border pt-3" }, ch = { class: "flex flex-wrap gap-2" }, fh = {
  key: 0,
  class: "mt-2"
}, ph = {
  key: 0,
  class: "mt-1 max-h-40 overflow-auto rounded-md border border-neutral-800 bg-neutral-950 p-2 text-[11px] whitespace-pre-wrap text-neutral-200"
}, mh = { key: 3 }, gh = { class: "columns-1 gap-4 xl:columns-2" }, hh = { class: "mb-4 break-inside-avoid rounded-lg border border-border bg-card p-4" }, bh = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, vh = { class: "mt-4 border-t border-border pt-4" }, yh = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, xh = { class: "mb-4 break-inside-avoid rounded-lg border border-border bg-card p-4" }, _h = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, wh = { class: "mt-4 border-t border-border pt-4" }, kh = {
  key: 0,
  class: "mb-2 flex flex-wrap gap-1.5"
}, Sh = ["onClick"], Ch = { class: "flex gap-2" }, Ah = {
  key: 1,
  class: "mt-1.5 text-xs text-destructive"
}, Eh = { class: "mt-4" }, Ih = {
  key: 0,
  class: "mb-2 flex flex-wrap gap-1.5"
}, Th = ["onClick"], Ph = { class: "flex gap-2" }, Rh = {
  key: 1,
  class: "mt-1.5 text-xs text-destructive"
}, Mh = { class: "mt-4 border-t border-border pt-4" }, Vh = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, $h = { class: "flex justify-self-end gap-2" }, Oh = { class: "mb-4 break-inside-avoid rounded-lg border border-border bg-card p-4" }, jh = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, Nh = {
  key: 0,
  class: "col-span-2 -mt-2 text-xs text-destructive"
}, Lh = {
  key: 1,
  class: "col-span-2 -mt-2 text-xs text-destructive"
}, Uh = { class: "mt-4 border-t border-border pt-4" }, Dh = { class: "mb-8 flex justify-end" }, Bh = 5e3, Wo = "__other__", as = "__other__", Fh = 400, Hh = /* @__PURE__ */ qe({
  __name: "App",
  setup(e) {
    const t = /* @__PURE__ */ qu(() => import("./incus-settings-Terminal-CjPQgd_G.js")), s = /* @__PURE__ */ L("jails"), n = { builder: "Builder", jails: "Containers", config: "Config" }, o = /* @__PURE__ */ L(!0), l = /* @__PURE__ */ L(!1), i = /* @__PURE__ */ L(null), a = /* @__PURE__ */ L(!1), d = /* @__PURE__ */ L([]), m = /* @__PURE__ */ L(""), g = he(() => da(m.value)), x = he(() => Er(w.jailCpu)), C = he(() => Ir(w.jailMemory)), E = /* @__PURE__ */ L(""), U = /* @__PURE__ */ L(!1), A = /* @__PURE__ */ L(null), w = /* @__PURE__ */ zt({
      enabled: !1,
      stateDir: "",
      storageDriver: "dir",
      storageSource: "",
      storagePoolName: "",
      jailBridge: "",
      jailSubnet: "",
      jailNat: !0,
      jailIpv6: "none",
      aclName: "",
      aclBlock: "",
      aclAllow: "",
      aclDefaultEgress: "allow",
      aclDefaultIngress: "drop",
      jailProfile: "",
      jailImage: "",
      jailNesting: !1,
      jailCpu: "",
      jailMemory: "",
      jailWorkspaceRoot: "",
      jailAgentUid: "",
      jailAgentGid: "",
      jailBindMounts: "",
      tsAuthKeyConfigured: !1,
      dashboardWidgetEnable: !0
    }), {
      runningJails: H,
      stoppedJailsCount: D,
      totalMemoryUsageBytes: K,
      totalCpuUsageNs: B,
      fleetHistory: Q,
      formatDuration: je,
      formatBytes: W,
      formatMemory: te,
      memoryFillPct: Re,
      updateCpuSamplesAndHistory: _e,
      cpuRateLabel: $e,
      cpuRatePct: re,
      cpuRateSuffix: xe,
      jailCpuHistory: He,
      totalCpuRateLabel: bt,
      sparklinePoints: we
    } = Df(d, () => w.jailCpu), fe = he(() => w.storageDriver === "zfs"), se = /* @__PURE__ */ L(!1), Me = /* @__PURE__ */ L(""), De = /* @__PURE__ */ L(!1);
    async function ze() {
      const c = await ve(Bf);
      Object.assign(w, c.incusConfig);
    }
    async function Be() {
      try {
        const c = await ve(Ff);
        a.value = c.incusHealthy, d.value = c.jails, _e();
      } catch {
        a.value = !1;
      }
    }
    vi(async () => {
      try {
        await ze(), await Be(), await Promise.all([To(), qr()]);
      } catch (c) {
        i.value = c instanceof Error ? c.message : String(c);
      } finally {
        o.value = !1;
      }
      s.value === "jails" && Mr();
    }), gt(s, (c) => {
      c === "jails" ? (Be(), Mr()) : wo();
    });
    async function In() {
      l.value = !0, i.value = null;
      try {
        const c = Uf(w, {
          replacement: Me.value,
          clear: De.value
        });
        await ve(Nl, { input: c }), (De.value || Me.value) && (w.tsAuthKeyConfigured = !De.value, Me.value = "", De.value = !1), await Be();
      } catch (c) {
        i.value = c instanceof Error ? c.message : String(c);
      } finally {
        l.value = !1;
      }
    }
    async function Tn(c, r) {
      i.value = null;
      try {
        await ve(Hf, { name: c, action: r }), await Be();
      } catch (u) {
        i.value = u instanceof Error ? u.message : String(u);
      }
    }
    async function xo(c) {
      if (confirm(`Delete container "${c}"? This cannot be undone.`)) {
        i.value = null;
        try {
          await ve(zf, { name: c }), await Be();
        } catch (r) {
          i.value = r instanceof Error ? r.message : String(r);
        }
      }
    }
    const _t = /* @__PURE__ */ L(!1);
    async function ms() {
      if (confirm("Delete every stopped container? Running containers are never touched. This cannot be undone.")) {
        _t.value = !0, i.value = null;
        try {
          (await ve(ap)).deleteStoppedJails.length === 0 && (i.value = "No stopped containers to delete."), await Be();
        } catch (c) {
          i.value = c instanceof Error ? c.message : String(c);
        } finally {
          _t.value = !1;
        }
      }
    }
    async function Os() {
      if (!(!m.value.trim() || g.value)) {
        i.value = null;
        try {
          await ve(Wf, {
            name: m.value.trim(),
            image: E.value || null,
            allowSudo: U.value
          }), m.value = "", U.value = !1, await Be();
        } catch (c) {
          i.value = c instanceof Error ? c.message : String(c);
        }
      }
    }
    const de = /* @__PURE__ */ L(null), Te = /* @__PURE__ */ L(null), Pn = /* @__PURE__ */ L(!1), f = /* @__PURE__ */ L(""), b = /* @__PURE__ */ L(!1), _ = /* @__PURE__ */ L(""), R = /* @__PURE__ */ L(""), I = /* @__PURE__ */ L("");
    async function T(c) {
      if (Ge(), le.value = !1, js(), wt.value = !1, de.value === c) {
        de.value = null, Te.value = null;
        return;
      }
      de.value = c, ae.value = "", Se.value = "", Ae.value = "", We.value = "", ut.value = null, await j(c);
    }
    async function j(c) {
      Pn.value = !0, f.value = "";
      try {
        const r = await ve(Kf, { name: c });
        Te.value = r.jailDetail, _.value = r.jailDetail.cpuLimit ?? "", R.value = r.jailDetail.memoryLimit ?? "", I.value = r.jailDetail.workspaceHostPath ?? "";
      } catch (r) {
        f.value = r instanceof Error ? r.message : String(r);
      } finally {
        Pn.value = !1;
      }
    }
    async function N() {
      if (!de.value) return;
      const c = Er(_.value);
      if (c) {
        f.value = c;
        return;
      }
      b.value = !0, f.value = "";
      try {
        await ve(zo, { name: de.value, cpu: _.value.trim() }), await j(de.value);
      } catch (r) {
        f.value = r instanceof Error ? r.message : String(r);
      } finally {
        b.value = !1;
      }
    }
    async function O() {
      if (!de.value) return;
      const c = Ir(R.value);
      if (c) {
        f.value = c;
        return;
      }
      b.value = !0, f.value = "";
      try {
        await ve(zo, { name: de.value, memory: R.value.trim() }), await j(de.value);
      } catch (r) {
        f.value = r instanceof Error ? r.message : String(r);
      } finally {
        b.value = !1;
      }
    }
    async function P() {
      if (de.value) {
        _.value = "", R.value = "", b.value = !0, f.value = "";
        try {
          await ve(zo, { name: de.value, cpu: "", memory: "" }), await j(de.value);
        } catch (c) {
          f.value = c instanceof Error ? c.message : String(c);
        } finally {
          b.value = !1;
        }
      }
    }
    async function J() {
      if (!(!de.value || !I.value.trim())) {
        b.value = !0, f.value = "";
        try {
          await ve(Yf, {
            name: de.value,
            hostPath: I.value.trim()
          }), await j(de.value);
        } catch (c) {
          f.value = c instanceof Error ? c.message : String(c);
        } finally {
          b.value = !1;
        }
      }
    }
    async function F() {
      if (de.value) {
        b.value = !0, f.value = "";
        try {
          await ve(Qf, { name: de.value }), await j(de.value);
        } catch (c) {
          f.value = c instanceof Error ? c.message : String(c);
        } finally {
          b.value = !1;
        }
      }
    }
    function q(c) {
      var r;
      return !c.workspaceIsOverride && !!((r = c.workspaceHostPath) != null && r.endsWith("/default-workspace"));
    }
    const Y = /* @__PURE__ */ L(!1);
    async function ie() {
      if (de.value) {
        Y.value = !0, f.value = "";
        try {
          await ve(up, { name: de.value }), await j(de.value);
        } catch (c) {
          f.value = c instanceof Error ? c.message : String(c);
        } finally {
          Y.value = !1;
        }
      }
    }
    const ae = /* @__PURE__ */ L(""), le = /* @__PURE__ */ L(!1), Se = /* @__PURE__ */ L(""), Ae = /* @__PURE__ */ L("");
    let tt = null;
    function Ge() {
      tt !== null && (tt.stop(), tt = null);
    }
    async function qt() {
      if (!(!de.value || !ae.value.trim())) {
        Ge(), le.value = !0, Se.value = "", Ae.value = "";
        try {
          const r = (await ve(dp, {
            name: de.value,
            formula: ae.value.trim()
          })).installHomebrewFormula;
          tt = Wn(async () => {
            try {
              const $ = (await ve(
                cp,
                { id: r }
              )).homebrewInstallStatus;
              if (!$ || $.status === "running") return;
              Ge(), le.value = !1, $.status === "success" ? (Se.value = $.message, ae.value = "") : Ae.value = $.message;
            } catch (u) {
              Ge(), le.value = !1, Ae.value = u instanceof Error ? u.message : String(u);
            }
          }, 2e3);
        } catch (c) {
          Ae.value = c instanceof Error ? c.message : String(c), le.value = !1;
        }
      }
    }
    const ns = /* @__PURE__ */ L(!1);
    async function st() {
      if (de.value) {
        ns.value = !0, f.value = "";
        try {
          await ve(qf, { name: de.value }), await j(de.value);
        } catch (c) {
          f.value = c instanceof Error ? c.message : String(c);
        } finally {
          ns.value = !1;
        }
      }
    }
    const We = /* @__PURE__ */ L(""), wt = /* @__PURE__ */ L(!1), ut = /* @__PURE__ */ L(null);
    let Rn = null;
    function js() {
      Rn !== null && (Rn.stop(), Rn = null);
    }
    async function Cr() {
      if (!(!de.value || !We.value.trim())) {
        js(), wt.value = !0, ut.value = null, f.value = "";
        try {
          const r = (await ve(Gf, {
            name: de.value,
            command: We.value.trim()
          })).startPrivilegedCommand;
          Rn = Wn(async () => {
            try {
              const $ = (await ve(
                Jf,
                { id: r }
              )).privilegedCommandStatus;
              if (!$ || $.status === "running") return;
              js(), wt.value = !1, ut.value = $;
            } catch (u) {
              js(), wt.value = !1, f.value = u instanceof Error ? u.message : String(u);
            }
          }, 2e3);
        } catch (c) {
          f.value = c instanceof Error ? c.message : String(c), wt.value = !1;
        }
      }
    }
    function ra(c) {
      const r = c.toLowerCase();
      return r === "running" ? "green" : r === "stopped" ? "gray" : "orange";
    }
    function _o(c) {
      return c.split(",").map((r) => r.trim()).filter((r) => r.length > 0);
    }
    function la() {
      return _o(w.aclBlock).length;
    }
    const Ar = /^[0-9a-fA-F:.]+\/\d{1,3}$/, ia = /^\d+(-\d+)?(,\d+(-\d+)?)*$/, aa = /^\d+(\.\d+)?(B|KB|MB|GB|TB|PB|KiB|MiB|GiB|TiB|PiB)?$/i, ua = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
    function Er(c) {
      return c.trim() ? ia.test(c.trim()) ? "" : `"${c}" doesn't look like a CPU limit — expected a core count (e.g. 2) or a set/range (e.g. 0-3).` : "";
    }
    function Ir(c) {
      return c.trim() ? aa.test(c.trim()) ? "" : `"${c}" doesn't look like a memory limit — expected a byte count with an optional unit (e.g. 4GiB).` : "";
    }
    function da(c) {
      return c.trim() ? ua.test(c.trim()) ? "" : `"${c}" isn't a valid container name — letters, digits, and hyphens only, can't start or end with a hyphen.` : "";
    }
    const Ns = he(() => _o(w.aclBlock)), Ls = he(() => _o(w.aclAllow)), Us = /* @__PURE__ */ L(""), Ds = /* @__PURE__ */ L(""), Bs = /* @__PURE__ */ L(""), Fs = /* @__PURE__ */ L("");
    function Tr() {
      const c = Us.value.trim();
      if (Bs.value = "", !!c) {
        if (!Ar.test(c)) {
          Bs.value = `"${c}" doesn't look like a CIDR — expected e.g. 10.0.0.0/8 or fd00::/8.`;
          return;
        }
        if (Ns.value.includes(c)) {
          Bs.value = `${c} is already in the list.`;
          return;
        }
        w.aclBlock = [...Ns.value, c].join(","), Us.value = "";
      }
    }
    function ca(c) {
      w.aclBlock = Ns.value.filter((r) => r !== c).join(",");
    }
    function Pr() {
      const c = Ds.value.trim();
      if (Fs.value = "", !!c) {
        if (!Ar.test(c)) {
          Fs.value = `"${c}" doesn't look like a CIDR — expected e.g. 100.64.0.0/10 or fd00::/8.`;
          return;
        }
        if (Ls.value.includes(c)) {
          Fs.value = `${c} is already in the list.`;
          return;
        }
        w.aclAllow = [...Ls.value, c].join(","), Ds.value = "";
      }
    }
    function fa(c) {
      w.aclAllow = Ls.value.filter((r) => r !== c).join(",");
    }
    function Rr(c) {
      const r = c.split(".");
      if (r.length !== 4) return null;
      let u = 0;
      for (const $ of r) {
        if (!/^\d{1,3}$/.test($)) return null;
        const Z = Number($);
        if (Z < 0 || Z > 255) return null;
        u = u << 8 | Z;
      }
      return u >>> 0;
    }
    function pa(c, r) {
      const [u, $] = r.split("/");
      if (!u || $ === void 0) return !1;
      const Z = Number($);
      if (!Number.isInteger(Z) || Z < 0 || Z > 32) return !1;
      const be = Rr(c), Fe = Rr(u);
      if (be === null || Fe === null) return !1;
      if (Z === 0) return !0;
      const Je = 4294967295 << 32 - Z >>> 0;
      return (be & Je) === (Fe & Je);
    }
    function ma(c) {
      return !c.ipv4 || !w.jailSubnet || c.status.toLowerCase() !== "running" ? !1 : pa(c.ipv4, w.jailSubnet);
    }
    let Mn = null;
    function Mr() {
      wo(), Mn = Wn(Be, Bh);
    }
    function wo() {
      Mn !== null && (Mn.stop(), Mn = null);
    }
    const Vr = [
      { value: "debian", label: "Debian" },
      { value: "ubuntu", label: "Ubuntu" },
      { value: "alpinelinux", label: "Alpine Linux" },
      { value: "rockylinux", label: "Rocky Linux" },
      { value: "almalinux", label: "AlmaLinux" },
      { value: "fedora", label: "Fedora" }
    ], Ot = {
      debian: [
        { value: "bookworm", label: "Bookworm (12, oldstable)" },
        { value: "trixie", label: "Trixie (13, stable)" },
        { value: "sid", label: "Sid (unstable)" }
      ],
      ubuntu: [
        { value: "jammy", label: "Jammy (22.04 LTS)" },
        { value: "noble", label: "Noble (24.04 LTS)" },
        { value: "resolute", label: "Resolute (26.04 LTS)" }
      ],
      alpinelinux: [
        { value: "3.21", label: "3.21" },
        { value: "3.22", label: "3.22" },
        { value: "3.23", label: "3.23" },
        { value: "3.24", label: "3.24 (latest stable)" },
        { value: "edge", label: "Edge (rolling)" }
      ],
      rockylinux: [
        { value: "9", label: "9" },
        { value: "10", label: "10 (latest)" }
      ],
      almalinux: [
        { value: "9", label: "9" },
        { value: "10", label: "10 (latest)" }
      ],
      fedora: [
        { value: "41", label: "41" },
        { value: "44", label: "44 (latest)" }
      ]
    }, $r = {
      debian: [
        { key: "build-tools", label: "Build tools", packages: ["build-essential"] },
        { key: "git", label: "Git", packages: ["git"] },
        { key: "python3", label: "Python 3", packages: ["python3", "python3-pip", "python3-venv"] },
        { key: "nodejs", label: "Node.js", packages: ["nodejs", "npm"] },
        { key: "curl", label: "curl", packages: ["curl"] },
        { key: "openssh-server", label: "OpenSSH server", packages: ["openssh-server"] },
        { key: "sudo", label: "sudo", packages: ["sudo"] },
        { key: "ca-certificates", label: "CA certificates", packages: ["ca-certificates"] }
      ],
      ubuntu: [
        { key: "build-tools", label: "Build tools", packages: ["build-essential"] },
        { key: "git", label: "Git", packages: ["git"] },
        { key: "python3", label: "Python 3", packages: ["python3", "python3-pip", "python3-venv"] },
        { key: "nodejs", label: "Node.js", packages: ["nodejs", "npm"] },
        { key: "curl", label: "curl", packages: ["curl"] },
        { key: "openssh-server", label: "OpenSSH server", packages: ["openssh-server"] },
        { key: "sudo", label: "sudo", packages: ["sudo"] },
        { key: "ca-certificates", label: "CA certificates", packages: ["ca-certificates"] }
      ],
      alpinelinux: [
        { key: "build-tools", label: "Build tools", packages: ["build-base"] },
        { key: "git", label: "Git", packages: ["git"] },
        { key: "python3", label: "Python 3", packages: ["python3", "py3-pip"] },
        { key: "curl", label: "curl", packages: ["curl"] },
        { key: "openssh-server", label: "OpenSSH server", packages: ["openssh"] },
        { key: "sudo", label: "sudo", packages: ["sudo"] },
        { key: "ca-certificates", label: "CA certificates", packages: ["ca-certificates"] }
      ],
      rockylinux: [
        { key: "build-tools", label: "Build tools", packages: ["gcc", "gcc-c++", "make"] },
        { key: "git", label: "Git", packages: ["git"] },
        { key: "python3", label: "Python 3", packages: ["python3", "python3-pip"] },
        { key: "curl", label: "curl", packages: ["curl"] },
        { key: "openssh-server", label: "OpenSSH server", packages: ["openssh-server"] },
        { key: "sudo", label: "sudo", packages: ["sudo"] },
        { key: "ca-certificates", label: "CA certificates", packages: ["ca-certificates"] }
      ],
      almalinux: [
        { key: "build-tools", label: "Build tools", packages: ["gcc", "gcc-c++", "make"] },
        { key: "git", label: "Git", packages: ["git"] },
        { key: "python3", label: "Python 3", packages: ["python3", "python3-pip"] },
        { key: "curl", label: "curl", packages: ["curl"] },
        { key: "openssh-server", label: "OpenSSH server", packages: ["openssh-server"] },
        { key: "sudo", label: "sudo", packages: ["sudo"] },
        { key: "ca-certificates", label: "CA certificates", packages: ["ca-certificates"] }
      ],
      fedora: [
        { key: "build-tools", label: "Build tools", packages: ["gcc", "gcc-c++", "make"] },
        { key: "git", label: "Git", packages: ["git"] },
        { key: "python3", label: "Python 3", packages: ["python3", "python3-pip"] },
        { key: "curl", label: "curl", packages: ["curl"] },
        { key: "openssh-server", label: "OpenSSH server", packages: ["openssh-server"] },
        { key: "sudo", label: "sudo", packages: ["sudo"] },
        { key: "ca-certificates", label: "CA certificates", packages: ["ca-certificates"] }
      ]
    }, lt = /* @__PURE__ */ L("debian"), kt = /* @__PURE__ */ L(""), Vn = /* @__PURE__ */ L(""), Gt = /* @__PURE__ */ L(""), Or = he(() => lt.value === Wo), jr = he(() => kt.value === as), ko = he(() => Or.value ? Vn.value : lt.value), So = he(
      () => jr.value ? Gt.value : kt.value
    ), ga = he(() => Ot[lt.value] ?? []);
    gt(lt, () => {
      const c = Ot[lt.value];
      kt.value = c && c.length > 0 ? c[0].value : as, Gt.value = "";
    });
    {
      const c = Ot[lt.value];
      kt.value = c && c.length > 0 ? c[0].value : as;
    }
    const os = /* @__PURE__ */ L(""), gs = /* @__PURE__ */ L(""), $n = /* @__PURE__ */ L(!1), Hs = /* @__PURE__ */ L(null), zs = /* @__PURE__ */ L([]), hs = /* @__PURE__ */ L(null), On = /* @__PURE__ */ L(!1);
    function ha(c) {
      return c.split(/[\n,]/).map((r) => r.trim()).filter((r) => r.length > 0);
    }
    function Nr() {
      const c = ha(os.value);
      return Array.from(/* @__PURE__ */ new Set([...Array.from(Oe), ...c]));
    }
    const rs = /* @__PURE__ */ L(""), bs = /* @__PURE__ */ L([]), Ws = /* @__PURE__ */ L([]), Co = /* @__PURE__ */ L(!1), Ks = /* @__PURE__ */ L(null);
    let qs = null, jn = 0;
    const Oe = /* @__PURE__ */ zt(/* @__PURE__ */ new Set()), Ne = /* @__PURE__ */ zt(/* @__PURE__ */ new Map()), Lr = { apt: "apt", npm: "npm", pypi: "PyPI", brew: "brew" };
    function Ur() {
      if (qs && clearTimeout(qs), rs.value.trim().length < 2) {
        bs.value = [], Ws.value = [], Ks.value = null;
        return;
      }
      qs = setTimeout(ba, Fh);
    }
    gt(rs, Ur), gt(lt, () => {
      Oe.clear(), Ne.clear(), Ur();
    });
    async function ba() {
      const c = rs.value.trim();
      if (c.length < 2) return;
      const r = ++jn;
      Co.value = !0, Ks.value = null;
      try {
        const u = await ve(
          ep,
          { query: c, distro: ko.value, release: So.value }
        );
        if (r !== jn) return;
        bs.value = u.searchAllPackages.results, Ws.value = u.searchAllPackages.errors;
      } catch (u) {
        if (r !== jn) return;
        Ks.value = u instanceof Error ? u.message : String(u), bs.value = [], Ws.value = [];
      } finally {
        r === jn && (Co.value = !1);
      }
    }
    function va(c) {
      Oe.add(c.name);
    }
    function ya(c) {
      Oe.delete(c);
    }
    function Ao(c) {
      var u;
      const r = (u = $r[lt.value]) == null ? void 0 : u.find(($) => $.key === c);
      if (r)
        for (const $ of r.packages) Oe.add($);
    }
    function xa(c) {
      Ao("nodejs"), Ne.set(`npm:${c.name}`, `npm install -g ${c.name}`);
    }
    function _a(c) {
      Ao("python3"), Ne.set(`pypi:${c.name}`, `pip3 install ${c.name}`);
    }
    function wa(c) {
      Ne.delete(c);
    }
    function ka(c) {
      c.ecosystem === "apt" ? va(c) : c.ecosystem === "npm" ? xa(c) : c.ecosystem === "pypi" && _a(c);
    }
    function Dr(c) {
      return c.ecosystem === "apt" ? Oe.has(c.name) : c.ecosystem === "npm" ? Ne.has(`npm:${c.name}`) : c.ecosystem === "pypi" ? Ne.has(`pypi:${c.name}`) : !1;
    }
    function Eo(c, r) {
      Vr.some((u) => u.value === c) ? (lt.value = c, (Ot[c] ?? []).some(($) => $.value === r) ? (kt.value = r, Gt.value = "") : (kt.value = as, Gt.value = r)) : (lt.value = Wo, Vn.value = c, kt.value = as, Gt.value = r);
    }
    function Gs() {
      hs.value = null;
    }
    function Sa(c) {
      var be, Fe, Je, it;
      const r = c.toLowerCase(), u = (Pe) => Pe.find((mt) => r.includes(mt));
      if (r.includes("alpine")) {
        const Pe = (be = r.match(/(\d+\.\d+)/)) == null ? void 0 : be[1];
        return { distro: "alpinelinux", release: Pe && Ot.alpinelinux.some((Mo) => Mo.value === Pe) ? Pe : "3.24" };
      }
      if (r.includes("fedora")) {
        const Pe = (Fe = r.match(/fedora[:\-](\d+)/)) == null ? void 0 : Fe[1];
        return { distro: "fedora", release: Pe && Ot.fedora.some((Mo) => Mo.value === Pe) ? Pe : "44" };
      }
      if (r.includes("rockylinux") || r.includes("rocky")) {
        const Pe = (Je = r.match(/(\d+)/)) == null ? void 0 : Je[1];
        return { distro: "rockylinux", release: Pe === "9" || Pe === "10" ? Pe : "10" };
      }
      if (r.includes("almalinux") || r.includes("alma")) {
        const Pe = (it = r.match(/(\d+)/)) == null ? void 0 : it[1];
        return { distro: "almalinux", release: Pe === "9" || Pe === "10" ? Pe : "10" };
      }
      const $ = u(["jammy", "noble", "resolute", "focal", "bionic"]);
      if (r.includes("ubuntu") || $)
        return { distro: "ubuntu", release: $ && Ot.ubuntu.some((mt) => mt.value === $) ? $ : "noble" };
      const Z = u(["bookworm", "trixie", "sid", "bullseye", "buster"]);
      return r.includes("debian") || Z || r.startsWith("node:") || r.startsWith("python:") || r.includes("/node") || r.includes("/python") ? { distro: "debian", release: Z && Ot.debian.some((mt) => mt.value === Z) ? Z : "bookworm" } : null;
    }
    function Ca(c) {
      const r = c.toLowerCase();
      return r.includes("/node") ? "nodejs" : r.includes("/python") ? "python3" : null;
    }
    function Aa(c) {
      var Z;
      const r = JSON.parse(Ea(c)), u = { distroSet: !1, packagesAdded: [], commandsAdded: [], skipped: [] };
      if (Gs(), Oe.clear(), Ne.clear(), os.value = "", typeof r.image == "string") {
        const be = Sa(r.image);
        be ? (Eo(be.distro, be.release), u.distroSet = !0) : u.skipped.push(`image "${r.image}" — couldn't infer a matching distro/release, pick manually`);
      } else r.build && u.skipped.push(`"build.dockerfile" — Dockerfile-based devcontainers aren't translated, pick a distro/release manually`);
      if (r.features && typeof r.features == "object")
        for (const be of Object.keys(r.features)) {
          const Fe = Ca(be);
          if (Fe) {
            const Je = (Z = $r[lt.value]) == null ? void 0 : Z.find((it) => it.key === Fe);
            if (Je) {
              for (const it of Je.packages)
                Oe.has(it) || (Oe.add(it), u.packagesAdded.push(it));
              continue;
            }
          }
          if (be.includes("/git")) {
            Oe.has("git") || (Oe.add("git"), u.packagesAdded.push("git"));
            continue;
          }
          if (be.includes("/common-utils")) {
            for (const Je of ["curl", "sudo", "ca-certificates"])
              Oe.has(Je) || (Oe.add(Je), u.packagesAdded.push(Je));
            continue;
          }
          u.skipped.push(`feature "${be}" — not recognized, add its packages manually if needed`);
        }
      const $ = [
        ["postCreateCommand", r.postCreateCommand],
        ["postStartCommand", r.postStartCommand]
      ];
      for (const [be, Fe] of $) {
        if (!Fe) continue;
        (Array.isArray(Fe) ? Fe.map(String) : [String(Fe)]).forEach((it, Pe) => {
          const mt = `devcontainer:${be}:${Pe}`;
          Ne.set(mt, it), u.commandsAdded.push(it);
        });
      }
      return (r.remoteUser || r.containerUser) && u.skipped.push(`remoteUser/containerUser "${r.remoteUser ?? r.containerUser}" — not mapped, this plugin uses one fixed agent user (Config → Jail Defaults)`), (r.forwardPorts || r.mounts || r.workspaceFolder) && u.skipped.push("forwardPorts/mounts/workspaceFolder — IDE/runtime concerns, not applicable to image building"), u;
    }
    function Ea(c) {
      return c.replace(/\/\/.*$/gm, "").replace(/,(\s*[}\]])/g, "$1");
    }
    const Js = /* @__PURE__ */ L(null), St = /* @__PURE__ */ L(null), Br = /* @__PURE__ */ L(null);
    function Ia() {
      var c;
      (c = Br.value) == null || c.click();
    }
    function Ta(c) {
      var $;
      const r = ($ = c.target.files) == null ? void 0 : $[0];
      if (!r) return;
      Js.value = null, St.value = null;
      const u = new FileReader();
      u.onload = () => {
        try {
          St.value = Aa(String(u.result));
        } catch (Z) {
          Js.value = Z instanceof Error ? Z.message : String(Z);
        }
      }, u.onerror = () => {
        Js.value = "Failed to read the file.";
      }, u.readAsText(r), c.target.value = "";
    }
    function Pa(c) {
      const r = c == null ? void 0 : c.tools;
      if (!r || typeof r != "object") return [];
      const u = [];
      for (const [$, Z] of Object.entries(r))
        typeof Z == "string" ? u.push({ tool: $, version: Z }) : Array.isArray(Z) && typeof Z[0] == "string" ? u.push({ tool: $, version: Z[0] }) : Z && typeof Z == "object" && typeof Z.version == "string" && u.push({ tool: $, version: Z.version });
      return u;
    }
    function Ra(c) {
      const r = [];
      for (const u of c.split(`
`)) {
        const $ = u.split("#")[0].trim();
        if (!$) continue;
        const [Z, be] = $.split(/\s+/);
        Z && be && r.push({ tool: Z, version: be });
      }
      return r;
    }
    function Fr() {
      Ao("build-tools"), Oe.has("curl") || Oe.add("curl"), Oe.has("ca-certificates") || Oe.add("ca-certificates"), Ne.set("mise:env", "export MISE_DATA_DIR=/opt/mise MISE_CONFIG_DIR=/etc/mise"), Ne.set("mise:install", "curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh"), Ne.set(
        "mise:profile",
        `printf 'export MISE_DATA_DIR=/opt/mise MISE_CONFIG_DIR=/etc/mise\\neval "$(/usr/local/bin/mise activate bash)"\\n' > /etc/profile.d/mise.sh && chmod +x /etc/profile.d/mise.sh`
      );
    }
    function Hr(c) {
      if (c.length === 0) return [];
      Fr();
      const r = c.map((u) => `${u.tool}@${u.version}`);
      return Ne.set("mise:use-tools", `mise use -g ${r.join(" ")}`), r;
    }
    async function Ma(c) {
      const u = (await import("./incus-settings-index-D8Q71tKU.js")).parse(c), $ = Pa(u);
      if ($.length === 0) throw new Error("No [tools] entries found in this mise.toml.");
      return { toolsAdded: Hr($) };
    }
    function Va(c) {
      const r = Ra(c);
      if (r.length === 0) throw new Error("No tool/version lines found in this .tool-versions file.");
      return { toolsAdded: Hr(r) };
    }
    const vs = /* @__PURE__ */ L(null), Ys = /* @__PURE__ */ L(null), zr = /* @__PURE__ */ L(null), Wr = /* @__PURE__ */ L(null);
    function Kr(c, r) {
      var Z;
      const u = (Z = c.target.files) == null ? void 0 : Z[0];
      if (!u) return;
      vs.value = null, Ys.value = null;
      const $ = new FileReader();
      $.onload = async () => {
        try {
          const be = r === "toml" ? await Ma(String($.result)) : Va(String($.result));
          Ys.value = be.toolsAdded;
        } catch (be) {
          vs.value = be instanceof Error ? be.message : String(be);
        }
      }, $.onerror = () => {
        vs.value = "Failed to read the file.";
      }, $.readAsText(u), c.target.value = "";
    }
    const ys = /* @__PURE__ */ L(""), Qs = /* @__PURE__ */ L("");
    function $a() {
      const c = ys.value.trim();
      if (!c) return;
      Fr(), Oe.has("git") || Oe.add("git");
      const r = Qs.value.trim(), u = r ? `git clone --depth 1 --branch ${r} ${c} /opt/dotfiles-src` : `git clone --depth 1 ${c} /opt/dotfiles-src`;
      Ne.set("mise:dotfiles-clone", u), Ne.set(
        "mise:dotfiles-bootstrap",
        "cp /opt/dotfiles-src/mise.toml /opt/dotfiles-src/.mise.toml /etc/mise/config.d/dotfiles.toml 2>/dev/null; MISE_EXPERIMENTAL=1 mise bootstrap --yes || true"
      );
    }
    function Oa() {
      Ne.delete("mise:dotfiles-clone"), Ne.delete("mise:dotfiles-bootstrap"), ys.value = "", Qs.value = "";
    }
    const Io = /* @__PURE__ */ L([]), Zs = /* @__PURE__ */ L(""), Nn = /* @__PURE__ */ L(!1), xs = /* @__PURE__ */ L(null);
    async function To() {
      const c = await ve(sp);
      Io.value = c.builderPresets;
    }
    async function ja() {
      const c = Zs.value.trim();
      if (c) {
        xs.value = null, Nn.value = !0;
        try {
          await ve(np, {
            input: {
              name: c,
              distro: ko.value.trim(),
              release: So.value.trim(),
              packages: Nr()
            }
          }), Zs.value = "", await To();
        } catch (r) {
          xs.value = r instanceof Error ? r.message : String(r);
        } finally {
          Nn.value = !1;
        }
      }
    }
    function Na(c) {
      Eo(c.distro, c.release), os.value = c.packages.join(`
`), gs.value = "", Gs();
    }
    async function La(c) {
      xs.value = null;
      try {
        await ve(op, { name: c }), await To();
      } catch (r) {
        xs.value = r instanceof Error ? r.message : String(r);
      }
    }
    const Ct = /* @__PURE__ */ L([]), Jt = /* @__PURE__ */ L(null), Po = /* @__PURE__ */ L(null);
    async function qr() {
      const c = await ve(rp);
      Ct.value = c.jailImages;
    }
    async function Ua(c) {
      Jt.value = null, Po.value = c.alias;
      const r = !c.isMaster;
      try {
        if (await ve(lp, { alias: c.alias, isMaster: r }), r) {
          for (const u of Ct.value) u.isMaster = u.alias === c.alias;
          await ve(Nl, { input: { jailImage: c.alias } }), w.jailImage = c.alias;
        } else
          c.isMaster = !1;
      } catch (u) {
        Jt.value = u instanceof Error ? u.message : String(u);
      } finally {
        Po.value = null;
      }
    }
    function Da(c) {
      Eo(c.distro, c.release), os.value = c.packages.join(`
`), gs.value = "", hs.value = c.alias;
    }
    const Ro = /* @__PURE__ */ L(null);
    async function Ba(c) {
      if (confirm(`Delete image "${c.alias}"? This removes it from Incus and cannot be undone.`)) {
        Jt.value = null, Ro.value = c.alias;
        try {
          await ve(Xf, { alias: c.alias }), Ct.value = Ct.value.filter((r) => r.alias !== c.alias), hs.value === c.alias && Gs();
        } catch (r) {
          Jt.value = r instanceof Error ? r.message : String(r);
        } finally {
          Ro.value = null;
        }
      }
    }
    function Fa(c) {
      return c.length === 0 ? "no packages" : c.join(", ");
    }
    const Ln = /* @__PURE__ */ L(!1), Xs = /* @__PURE__ */ L("");
    async function Ha() {
      Ln.value = !0, Jt.value = null, Xs.value = "";
      try {
        const c = await ve(ip);
        c.pruneStaleImageRecords.length === 0 ? Xs.value = "Nothing to prune — every saved image still exists in Incus." : (Xs.value = `Untracked ${c.pruneStaleImageRecords.length}: ${c.pruneStaleImageRecords.join(", ")}`, Ct.value = Ct.value.filter((r) => !c.pruneStaleImageRecords.includes(r.alias)));
      } catch (c) {
        Jt.value = c instanceof Error ? c.message : String(c);
      } finally {
        Ln.value = !1;
      }
    }
    function Un(c) {
      c.intervalId !== null && (c.intervalId.stop(), c.intervalId = null);
    }
    function za(c) {
      c.intervalId = Wn(async () => {
        var r, u;
        try {
          const $ = await ve(tp, {
            buildId: c.buildId
          });
          c.status = $.jailImageBuildStatus, ((r = c.status) == null ? void 0 : r.status) === "success" ? (Un(c), qr()) : ((u = c.status) == null ? void 0 : u.status) === "failed" && Un(c);
        } catch ($) {
          c.error = $ instanceof Error ? $.message : String($), Un(c);
        }
      }, 2e3);
    }
    async function Wa() {
      Hs.value = null;
      const c = ko.value.trim(), r = So.value.trim(), u = gs.value.trim(), $ = Nr();
      if (!c || !r || !u) {
        Hs.value = "Distro, release, and alias are required.";
        return;
      }
      $n.value = !0;
      try {
        const be = {
          buildId: (await ve(Zf, {
            distro: c,
            release: r,
            packages: $,
            alias: u,
            basedOn: hs.value || null,
            postInstallCommands: Array.from(Ne.values())
          })).buildJailImage,
          distro: c,
          release: r,
          alias: u,
          status: null,
          error: null,
          intervalId: null
        };
        zs.value.unshift(be), za(zs.value[0]);
        const Fe = Ot[lt.value];
        kt.value = Fe && Fe.length > 0 ? Fe[0].value : as, Gt.value = "", gs.value = "", os.value = "", Oe.clear(), Ne.clear(), bs.value = [], rs.value = "", Ys.value = null, vs.value = null, ys.value = "", Qs.value = "", Gs();
      } catch (Z) {
        Hs.value = Z instanceof Error ? Z.message : String(Z);
      } finally {
        $n.value = !1;
      }
    }
    function Ka(c) {
      switch (c) {
        case "success":
          return "green";
        case "failed":
          return "red";
        case "running":
          return "orange";
        default:
          return "gray";
      }
    }
    return xi(() => {
      for (const c of zs.value) Un(c);
      wo(), Ge(), js(), qs && clearTimeout(qs);
    }), (c, r) => (S(), M("div", fp, [
      o.value ? (S(), M("div", pp, "Loading incus configuration…")) : (S(), M(ue, { key: 1 }, [
        i.value ? (S(), M("div", mp, V(i.value), 1)) : z("", !0),
        p("header", gp, [
          r[52] || (r[52] = Vd('<svg width="14" height="20" viewBox="0 0 10 14" fill="none" aria-hidden="true" class="shrink-0 text-foreground"><path d="M5 0L9 2.5L5 5L1 2.5Z" fill="currentColor" opacity="0.95"></path><path d="M5 3L9 5.5L5 8L1 5.5Z" fill="currentColor" opacity="0.7"></path><path d="M5 6L9 8.5L5 11L1 8.5Z" fill="currentColor" opacity="0.45"></path><path d="M5 9L9 11.5L5 14L1 11.5Z" fill="currentColor" opacity="0.25"></path></svg><span class="text-sm font-semibold tracking-[0.14em] uppercase">Incus</span><span class="text-xs text-muted-foreground">dev containers</span>', 3)),
          p("div", hp, [
            v(h(Lt), {
              variant: a.value ? "green" : "red"
            }, {
              default: k(() => [
                y(V(a.value ? "Reachable" : "Not running"), 1)
              ]),
              _: 1
            }, 8, ["variant"]),
            v(h(ce), {
              size: "sm",
              variant: "outline",
              onClick: Be
            }, {
              default: k(() => [...r[51] || (r[51] = [
                y("Refresh", -1)
              ])]),
              _: 1
            })
          ])
        ]),
        p("div", bp, [
          (S(), M(ue, null, Ye(["builder", "jails", "config"], (u) => p("button", {
            key: u,
            type: "button",
            class: ot([
              "-mb-px border-b-[3px] px-4 py-2 text-xs font-semibold tracking-[0.08em] uppercase transition-colors cursor-pointer",
              s.value === u ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            ]),
            onClick: ($) => s.value = u
          }, V(n[u]), 11, vp)), 64))
        ]),
        s.value === "builder" ? (S(), M("section", yp, [
          p("div", xp, [
            p("div", null, [
              r[76] || (r[76] = p("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Starting points", -1)),
              p("div", _p, [
                r[75] || (r[75] = p("h3", { class: "mb-2 text-sm font-semibold" }, "Presets", -1)),
                xs.value ? (S(), M("p", wp, V(xs.value), 1)) : z("", !0),
                Io.value.length === 0 ? (S(), M("p", kp, "Save the form below as a preset to reuse it later.")) : (S(), M("div", Sp, [
                  (S(!0), M(ue, null, Ye(Io.value, (u) => (S(), M("div", {
                    key: u.name,
                    class: "flex items-center gap-2 rounded-md border border-border px-2.5 py-1.5 text-xs"
                  }, [
                    p("button", {
                      type: "button",
                      class: "cursor-pointer font-medium hover:text-primary",
                      onClick: ($) => Na(u)
                    }, V(u.name), 9, Cp),
                    p("span", Ap, V(u.distro) + "/" + V(u.release), 1),
                    p("button", {
                      type: "button",
                      class: "cursor-pointer text-muted-foreground hover:text-destructive",
                      "aria-label": "Delete preset",
                      onClick: ($) => La(u.name)
                    }, "✕", 8, Ep)
                  ]))), 128))
                ])),
                p("div", Ip, [
                  v(h(pe), {
                    modelValue: Zs.value,
                    "onUpdate:modelValue": r[0] || (r[0] = (u) => Zs.value = u),
                    placeholder: "Preset name",
                    class: "w-56"
                  }, null, 8, ["modelValue"]),
                  v(h(ce), {
                    size: "sm",
                    variant: "outline",
                    disabled: Nn.value || !Zs.value.trim(),
                    onClick: ja
                  }, {
                    default: k(() => [
                      y(V(Nn.value ? "Saving…" : "Save as preset"), 1)
                    ]),
                    _: 1
                  }, 8, ["disabled"])
                ]),
                v(h(oe), null, {
                  default: k(() => [...r[53] || (r[53] = [
                    y(" Saves distro, release, and the current package/tool list — not the alias, since that should stay unique per build. Saving under a name that already exists overwrites it. ", -1)
                  ])]),
                  _: 1
                }),
                p("div", Tp, [
                  p("div", Pp, [
                    r[54] || (r[54] = p("h3", { class: "text-sm font-semibold" }, "Saved images", -1)),
                    Ct.value.length > 0 ? (S(), Ie(h(ce), {
                      key: 0,
                      size: "sm",
                      variant: "outline",
                      disabled: Ln.value,
                      onClick: Ha
                    }, {
                      default: k(() => [
                        y(V(Ln.value ? "Checking…" : "Prune stale records"), 1)
                      ]),
                      _: 1
                    }, 8, ["disabled"])) : z("", !0)
                  ]),
                  Jt.value ? (S(), M("p", Rp, V(Jt.value), 1)) : z("", !0),
                  Xs.value ? (S(), M("p", Mp, V(Xs.value), 1)) : z("", !0),
                  Ct.value.length === 0 ? (S(), M("p", Vp, " No images built yet — the first one you build can become the golden master. ")) : (S(), M("div", $p, [
                    (S(!0), M(ue, null, Ye([...Ct.value].sort((u, $) => ($.isMaster ? 1 : 0) - (u.isMaster ? 1 : 0)), (u) => (S(), M("div", {
                      key: u.alias,
                      class: ot(["flex items-center gap-3 rounded-md border px-3 py-2", u.isMaster ? "border-primary bg-primary/5" : "border-border"])
                    }, [
                      p("div", Op, [
                        p("div", jp, [
                          p("span", Np, V(u.alias), 1),
                          u.isMaster ? (S(), Ie(h(Lt), {
                            key: 0,
                            variant: "orange"
                          }, {
                            default: k(() => [...r[55] || (r[55] = [
                              y("Golden master", -1)
                            ])]),
                            _: 1
                          })) : z("", !0),
                          p("span", Lp, V(u.distro) + "/" + V(u.release), 1)
                        ]),
                        p("p", Up, V(Fa(u.packages)), 1)
                      ]),
                      v(h(ce), {
                        size: "sm",
                        variant: "outline",
                        disabled: Po.value === u.alias,
                        onClick: ($) => Ua(u),
                        title: u.isMaster ? "Stop launching new containers from this image by default" : "New containers launch from this image by default"
                      }, {
                        default: k(() => [
                          y(V(u.isMaster ? "Unset default" : "Set as default"), 1)
                        ]),
                        _: 2
                      }, 1032, ["disabled", "onClick", "title"]),
                      v(h(ce), {
                        size: "sm",
                        variant: "secondary",
                        onClick: ($) => Da(u)
                      }, {
                        default: k(() => [...r[56] || (r[56] = [
                          y("Build variant", -1)
                        ])]),
                        _: 1
                      }, 8, ["onClick"]),
                      v(h(ce), {
                        size: "sm",
                        variant: "destructive",
                        disabled: Ro.value === u.alias,
                        onClick: ($) => Ba(u)
                      }, {
                        default: k(() => [...r[57] || (r[57] = [
                          y("Delete", -1)
                        ])]),
                        _: 1
                      }, 8, ["disabled", "onClick"])
                    ], 2))), 128))
                  ])),
                  v(h(oe), null, {
                    default: k(() => [...r[58] || (r[58] = [
                      y(` Only one image can be the golden master at a time — marking a new one unmarks the previous. Marking it also sets it as the default image new containers launch from (Config → Container Defaults), so this is more than a label. "Build variant" pre-fills the form from that image's distro/release/packages so you can edit, extend, or strip it down before building a new one. "Prune stale records" checks every saved image still actually exists in Incus and untracks any that don't — useful if one was deleted directly via the incus CLI instead of through here. `, -1)
                    ])]),
                    _: 1
                  })
                ]),
                p("div", Dp, [
                  p("button", {
                    type: "button",
                    class: "flex w-full cursor-pointer items-center gap-1.5 text-left text-sm font-semibold",
                    onClick: r[1] || (r[1] = (u) => On.value = !On.value)
                  }, [
                    p("span", {
                      class: ot(["text-muted-foreground transition-transform", On.value ? "rotate-90" : ""])
                    }, "▸", 2),
                    r[59] || (r[59] = y(" Import from a config file ", -1)),
                    r[60] || (r[60] = p("span", { class: "font-normal text-xs text-muted-foreground" }, "devcontainer.json, mise.toml, .tool-versions", -1))
                  ]),
                  On.value ? (S(), M("div", Bp, [
                    p("div", null, [
                      r[65] || (r[65] = p("p", { class: "mb-2 text-xs text-muted-foreground" }, " devcontainer.json — maps the base image and recognized features to real packages; anything that isn't applicable to image building is reported, not silently dropped. ", -1)),
                      p("input", {
                        ref_key: "devcontainerFileInput",
                        ref: Br,
                        type: "file",
                        accept: ".json,application/json",
                        class: "hidden",
                        onChange: Ta
                      }, null, 544),
                      v(h(ce), {
                        size: "sm",
                        variant: "outline",
                        onClick: Ia
                      }, {
                        default: k(() => [...r[61] || (r[61] = [
                          y("Choose devcontainer.json…", -1)
                        ])]),
                        _: 1
                      }),
                      Js.value ? (S(), M("p", Fp, V(Js.value), 1)) : z("", !0),
                      St.value ? (S(), M("div", Hp, [
                        St.value.distroSet ? (S(), M("p", zp, [...r[62] || (r[62] = [
                          y("Distro/release set from ", -1),
                          p("span", { class: "font-mono" }, "image", -1),
                          y(".", -1)
                        ])])) : z("", !0),
                        St.value.packagesAdded.length > 0 ? (S(), M("p", Wp, [
                          r[63] || (r[63] = y(" Packages added: ", -1)),
                          p("span", Kp, V(St.value.packagesAdded.join(", ")), 1)
                        ])) : z("", !0),
                        St.value.commandsAdded.length > 0 ? (S(), M("p", qp, V(St.value.commandsAdded.length) + " lifecycle command(s) added below — review before building. ", 1)) : z("", !0),
                        St.value.skipped.length > 0 ? (S(), M("div", Gp, [
                          r[64] || (r[64] = p("p", { class: "text-muted-foreground" }, "Skipped (review manually):", -1)),
                          p("ul", Jp, [
                            (S(!0), M(ue, null, Ye(St.value.skipped, (u) => (S(), M("li", { key: u }, V(u), 1))), 128))
                          ])
                        ])) : z("", !0)
                      ])) : z("", !0)
                    ]),
                    p("div", Yp, [
                      r[70] || (r[70] = p("p", { class: "mb-2 text-xs text-muted-foreground" }, [
                        y(" mise.toml / .tool-versions — pins exact tool versions by baking in "),
                        p("span", { class: "font-mono" }, "mise"),
                        y(" itself as a post-install step, wired system-wide so the container's actual runtime user can use the tools too. ")
                      ], -1)),
                      p("input", {
                        ref_key: "miseTomlFileInput",
                        ref: zr,
                        type: "file",
                        accept: ".toml,application/toml",
                        class: "hidden",
                        onChange: r[2] || (r[2] = (u) => Kr(u, "toml"))
                      }, null, 544),
                      p("input", {
                        ref_key: "toolVersionsFileInput",
                        ref: Wr,
                        type: "file",
                        accept: ".tool-versions,text/plain",
                        class: "hidden",
                        onChange: r[3] || (r[3] = (u) => Kr(u, "tool-versions"))
                      }, null, 544),
                      p("div", Qp, [
                        v(h(ce), {
                          size: "sm",
                          variant: "outline",
                          onClick: r[4] || (r[4] = (u) => {
                            var $;
                            return ($ = zr.value) == null ? void 0 : $.click();
                          })
                        }, {
                          default: k(() => [...r[66] || (r[66] = [
                            y("Choose mise.toml…", -1)
                          ])]),
                          _: 1
                        }),
                        v(h(ce), {
                          size: "sm",
                          variant: "outline",
                          onClick: r[5] || (r[5] = (u) => {
                            var $;
                            return ($ = Wr.value) == null ? void 0 : $.click();
                          })
                        }, {
                          default: k(() => [...r[67] || (r[67] = [
                            y("Choose .tool-versions…", -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      vs.value ? (S(), M("p", Zp, V(vs.value), 1)) : z("", !0),
                      Ys.value ? (S(), M("p", Xp, [
                        r[68] || (r[68] = y(" Tools pinned: ", -1)),
                        p("span", em, V(Ys.value.join(", ")), 1),
                        r[69] || (r[69] = y(" — see the setup commands below. ", -1))
                      ])) : z("", !0)
                    ]),
                    p("div", tm, [
                      v(h(ne), {
                        for: "dotfiles-repo",
                        class: "mb-1 block"
                      }, {
                        default: k(() => [...r[71] || (r[71] = [
                          y("Bootstrap dotfiles from a repo", -1)
                        ])]),
                        _: 1
                      }),
                      r[74] || (r[74] = p("p", { class: "mb-2 text-xs text-muted-foreground" }, [
                        y(" Experimental — clones the repo and hands off to "),
                        p("span", { class: "font-mono" }, "mise bootstrap"),
                        y(", which only applies dotfiles if that repo's own mise config declares them. ")
                      ], -1)),
                      p("div", sm, [
                        v(h(pe), {
                          id: "dotfiles-repo",
                          modelValue: ys.value,
                          "onUpdate:modelValue": r[6] || (r[6] = (u) => ys.value = u),
                          class: "w-72 font-mono",
                          placeholder: "git@github.com:you/dotfiles.git"
                        }, null, 8, ["modelValue"]),
                        v(h(pe), {
                          modelValue: Qs.value,
                          "onUpdate:modelValue": r[7] || (r[7] = (u) => Qs.value = u),
                          class: "w-32 font-mono",
                          placeholder: "branch (optional)"
                        }, null, 8, ["modelValue"]),
                        v(h(ce), {
                          size: "sm",
                          variant: "outline",
                          disabled: !ys.value.trim(),
                          onClick: $a
                        }, {
                          default: k(() => [...r[72] || (r[72] = [
                            y("Add bootstrap", -1)
                          ])]),
                          _: 1
                        }, 8, ["disabled"]),
                        Ne.has("mise:dotfiles-clone") ? (S(), Ie(h(ce), {
                          key: 0,
                          size: "sm",
                          variant: "outline",
                          onClick: Oa
                        }, {
                          default: k(() => [...r[73] || (r[73] = [
                            y("Remove", -1)
                          ])]),
                          _: 1
                        })) : z("", !0)
                      ])
                    ])
                  ])) : z("", !0)
                ])
              ])
            ]),
            p("div", null, [
              r[92] || (r[92] = p("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Build", -1)),
              p("div", nm, [
                r[91] || (r[91] = p("h3", { class: "mb-4 text-base font-semibold" }, "Build container image", -1)),
                Hs.value ? (S(), M("div", om, V(Hs.value), 1)) : z("", !0),
                hs.value ? (S(), M("div", rm, [
                  p("span", null, [
                    r[77] || (r[77] = y("Building variant of: ", -1)),
                    p("span", lm, V(hs.value), 1)
                  ]),
                  p("button", {
                    type: "button",
                    class: "ml-auto cursor-pointer text-muted-foreground hover:text-foreground",
                    onClick: Gs
                  }, " ✕ Clear ")
                ])) : z("", !0),
                p("div", im, [
                  v(h(ne), { for: "builder-distro" }, {
                    default: k(() => [...r[78] || (r[78] = [
                      y("Distro", -1)
                    ])]),
                    _: 1
                  }),
                  p("div", am, [
                    v(h(ws), {
                      id: "builder-distro",
                      modelValue: lt.value,
                      "onUpdate:modelValue": r[8] || (r[8] = (u) => lt.value = u),
                      class: "w-48"
                    }, {
                      default: k(() => [
                        (S(), M(ue, null, Ye(Vr, (u) => p("option", {
                          key: u.value,
                          value: u.value
                        }, V(u.label), 9, um)), 64)),
                        p("option", { value: Wo }, "Other… (custom)")
                      ]),
                      _: 1
                    }, 8, ["modelValue"]),
                    Or.value ? (S(), Ie(h(pe), {
                      key: 0,
                      modelValue: Vn.value,
                      "onUpdate:modelValue": r[9] || (r[9] = (u) => Vn.value = u),
                      class: "w-40 font-mono",
                      placeholder: "e.g. archlinux"
                    }, null, 8, ["modelValue"])) : z("", !0)
                  ]),
                  v(h(oe), { class: "col-span-2" }, {
                    default: k(() => [...r[79] || (r[79] = [
                      y(` The curated list is verified against distrobuilder's own real image definitions — pick "Other" for anything else it supports; distrobuilder covers more than this list captures. `, -1)
                    ])]),
                    _: 1
                  }),
                  v(h(ne), { for: "builder-release" }, {
                    default: k(() => [...r[80] || (r[80] = [
                      y("Release", -1)
                    ])]),
                    _: 1
                  }),
                  p("div", dm, [
                    v(h(ws), {
                      id: "builder-release",
                      modelValue: kt.value,
                      "onUpdate:modelValue": r[10] || (r[10] = (u) => kt.value = u),
                      class: "w-48"
                    }, {
                      default: k(() => [
                        (S(!0), M(ue, null, Ye(ga.value, (u) => (S(), M("option", {
                          key: u.value,
                          value: u.value
                        }, V(u.label), 9, cm))), 128)),
                        p("option", { value: as }, "Other… (custom)")
                      ]),
                      _: 1
                    }, 8, ["modelValue"]),
                    jr.value ? (S(), Ie(h(pe), {
                      key: 0,
                      modelValue: Gt.value,
                      "onUpdate:modelValue": r[11] || (r[11] = (u) => Gt.value = u),
                      class: "w-40 font-mono",
                      placeholder: "e.g. rolling"
                    }, null, 8, ["modelValue"])) : z("", !0)
                  ]),
                  v(h(oe), { class: "col-span-2" }, {
                    default: k(() => [...r[81] || (r[81] = [
                      y("Options change with the distro above — a custom distro always shows the free-text field here too.", -1)
                    ])]),
                    _: 1
                  }),
                  v(h(ne), { for: "builder-alias" }, {
                    default: k(() => [...r[82] || (r[82] = [
                      y("Alias", -1)
                    ])]),
                    _: 1
                  }),
                  v(h(pe), {
                    id: "builder-alias",
                    modelValue: gs.value,
                    "onUpdate:modelValue": r[12] || (r[12] = (u) => gs.value = u),
                    class: "w-96 justify-self-end",
                    placeholder: "my-custom-image"
                  }, null, 8, ["modelValue"]),
                  v(h(oe), { class: "col-span-2" }, {
                    default: k(() => [...r[83] || (r[83] = [
                      y(` Becomes the image's name in Incus once the build succeeds — other containers (and "build variant") reference it by this alias, so it must be unique. Not required to match the container's own name. `, -1)
                    ])]),
                    _: 1
                  })
                ]),
                p("div", fm, [
                  r[88] || (r[88] = p("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Packages & tools", -1)),
                  v(h(pe), {
                    modelValue: rs.value,
                    "onUpdate:modelValue": r[13] || (r[13] = (u) => rs.value = u),
                    class: "w-full font-mono",
                    placeholder: "Search apt, npm, PyPI, Homebrew…"
                  }, null, 8, ["modelValue"]),
                  v(h(oe), null, {
                    default: k(() => [...r[84] || (r[84] = [
                      y(" apt only searches when Debian or Ubuntu is selected above. npm and PyPI results aren't OS packages — adding one adds a setup command that runs after packages install, and auto-adds the Node.js or Python packages it needs. Homebrew results show for browsing but can't be added yet — there's no way to bootstrap Homebrew itself inside an image build. ", -1)
                    ])]),
                    _: 1
                  }),
                  Ks.value ? (S(), M("p", pm, V(Ks.value), 1)) : z("", !0),
                  Ws.value.length > 0 ? (S(), M("p", mm, [
                    r[85] || (r[85] = y(" Some sources are unavailable right now, showing results from the rest: ", -1)),
                    (S(!0), M(ue, null, Ye(Ws.value, (u, $) => (S(), M("span", {
                      key: u.ecosystem
                    }, [
                      y(V($ > 0 ? ", " : " "), 1),
                      p("strong", null, V(Lr[u.ecosystem]), 1)
                    ]))), 128))
                  ])) : z("", !0),
                  Co.value ? (S(), M("p", gm, "Searching…")) : bs.value.length > 0 ? (S(), M("div", hm, [
                    (S(!0), M(ue, null, Ye(bs.value, (u) => (S(), M("div", {
                      key: `${u.ecosystem}:${u.name}`,
                      class: "flex items-center gap-2 rounded-md border border-border px-2.5 py-1.5 text-xs"
                    }, [
                      p("span", {
                        class: ot(["shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase", u.ecosystem === "apt" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"])
                      }, V(Lr[u.ecosystem]), 3),
                      p("div", bm, [
                        p("span", vm, V(u.name), 1),
                        u.version ? (S(), M("span", ym, V(u.version), 1)) : z("", !0),
                        u.description ? (S(), M("p", xm, V(u.description), 1)) : z("", !0)
                      ]),
                      u.ecosystem !== "brew" ? (S(), Ie(h(ce), {
                        key: 0,
                        size: "sm",
                        variant: "outline",
                        disabled: Dr(u),
                        onClick: ($) => ka(u)
                      }, {
                        default: k(() => [
                          y(V(Dr(u) ? "Added" : "+ Add"), 1)
                        ]),
                        _: 2
                      }, 1032, ["disabled", "onClick"])) : (S(), M("span", _m, "not build-time yet"))
                    ]))), 128))
                  ])) : rs.value.trim().length >= 2 ? (S(), M("p", wm, "No matches.")) : z("", !0),
                  Oe.size > 0 ? (S(), M("div", km, [
                    r[86] || (r[86] = p("p", { class: "mb-1.5 block text-xs font-medium" }, "Added from apt search", -1)),
                    p("div", Sm, [
                      (S(!0), M(ue, null, Ye(Oe, (u) => (S(), M("span", {
                        key: u,
                        class: "flex items-center gap-1.5 rounded-md border border-border px-2 py-1 font-mono text-xs"
                      }, [
                        y(V(u) + " ", 1),
                        p("button", {
                          type: "button",
                          class: "cursor-pointer text-muted-foreground hover:text-destructive",
                          onClick: ($) => ya(u)
                        }, "✕", 8, Cm)
                      ]))), 128))
                    ])
                  ])) : z("", !0),
                  Ne.size > 0 ? (S(), M("div", Am, [
                    r[87] || (r[87] = p("p", { class: "mb-1.5 block text-xs font-medium" }, "Extra setup commands (run after packages install)", -1)),
                    p("div", Em, [
                      (S(!0), M(ue, null, Ye(Ne, ([u, $]) => (S(), M("div", {
                        key: u,
                        class: "flex items-center gap-2 rounded-md border border-border px-2 py-1 font-mono text-xs"
                      }, [
                        p("span", Im, V($), 1),
                        p("button", {
                          type: "button",
                          class: "cursor-pointer text-muted-foreground hover:text-destructive",
                          onClick: (Z) => wa(u)
                        }, "✕", 8, Tm)
                      ]))), 128))
                    ])
                  ])) : z("", !0)
                ]),
                p("div", Pm, [
                  v(h(ne), {
                    for: "builder-extra-packages",
                    class: "mb-1.5 block text-xs text-muted-foreground"
                  }, {
                    default: k(() => [...r[89] || (r[89] = [
                      y("Anything else? (one per line, or comma-separated)", -1)
                    ])]),
                    _: 1
                  }),
                  mr(p("textarea", {
                    id: "builder-extra-packages",
                    "onUpdate:modelValue": r[14] || (r[14] = (u) => os.value = u),
                    rows: "2",
                    class: "border-input bg-background w-full rounded-md border px-3 py-2 text-sm font-mono",
                    placeholder: "e.g. htop"
                  }, null, 512), [
                    [sr, os.value]
                  ]),
                  v(h(oe), null, {
                    default: k(() => [...r[90] || (r[90] = [
                      y(" Exact OS package names for the selected distro's package manager — merged with anything added from search above, duplicates removed. Use this for anything search didn't turn up. ", -1)
                    ])]),
                    _: 1
                  })
                ]),
                p("div", Rm, [
                  v(h(ce), {
                    disabled: $n.value,
                    onClick: Wa
                  }, {
                    default: k(() => [
                      y(V($n.value ? "Starting…" : "Build"), 1)
                    ]),
                    _: 1
                  }, 8, ["disabled"])
                ])
              ])
            ])
          ]),
          r[96] || (r[96] = p("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Results", -1)),
          p("div", Mm, [
            r[95] || (r[95] = p("h3", { class: "mb-4 text-base font-semibold" }, "Builds", -1)),
            v(h(oe), null, {
              default: k(() => [...r[93] || (r[93] = [
                y(" Live distrobuilder log output, streamed while a build runs. This list is client-side only and resets on page reload — successful builds still land in Saved images above, but the log history itself isn't persisted. ", -1)
              ])]),
              _: 1
            }),
            zs.value.length === 0 ? (S(), M("div", Vm, [...r[94] || (r[94] = [
              p("span", { class: "h-1.5 w-1.5 shrink-0 rounded-full bg-neutral-700" }, null, -1),
              p("span", { class: "font-mono text-[11px] text-neutral-500" }, [
                y(" Pick a distro and release above, then hit Build — progress and logs stream in here."),
                p("span", { class: "motion-safe:animate-pulse" }, "_")
              ], -1)
            ])])) : (S(), M("div", $m, [
              (S(!0), M(ue, null, Ye(zs.value, (u) => {
                var $, Z, be, Fe, Je, it, Pe;
                return S(), M("div", {
                  key: u.buildId,
                  class: "rounded-md border border-border p-3"
                }, [
                  p("div", Om, [
                    p("div", jm, [
                      p("span", Nm, V(u.alias), 1),
                      p("span", Lm, V(u.distro) + " / " + V(u.release), 1)
                    ]),
                    v(h(Lt), {
                      variant: Ka(($ = u.status) == null ? void 0 : $.status)
                    }, {
                      default: k(() => {
                        var mt;
                        return [
                          y(V(((mt = u.status) == null ? void 0 : mt.status) ?? "queued"), 1)
                        ];
                      }),
                      _: 2
                    }, 1032, ["variant"])
                  ]),
                  (Z = u.status) != null && Z.error || u.error ? (S(), M("div", Um, V(((be = u.status) == null ? void 0 : be.error) || u.error), 1)) : z("", !0),
                  p("div", Dm, [
                    p("span", {
                      class: ot(["h-1.5 w-1.5 shrink-0 rounded-full", {
                        "bg-emerald-500": ((Fe = u.status) == null ? void 0 : Fe.status) === "success",
                        "bg-red-500": ((Je = u.status) == null ? void 0 : Je.status) === "failed",
                        "bg-amber-500": ((it = u.status) == null ? void 0 : it.status) === "running" || !u.status
                      }])
                    }, null, 2),
                    p("span", Bm, "distrobuilder · " + V(u.buildId.slice(0, 8)), 1)
                  ]),
                  p("pre", Fm, V(((Pe = u.status) == null ? void 0 : Pe.logTail) || "Waiting for log output…"), 1)
                ]);
              }), 128))
            ]))
          ])
        ])) : s.value === "jails" ? (S(), M("section", Hm, [
          r[149] || (r[149] = p("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Dashboard", -1)),
          p("div", zm, [
            p("div", Wm, [
              r[97] || (r[97] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Total Containers", -1)),
              p("p", Km, V(d.value.length), 1)
            ]),
            p("div", qm, [
              r[98] || (r[98] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Running", -1)),
              p("p", Gm, V(h(H).length), 1)
            ]),
            p("div", Jm, [
              r[99] || (r[99] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Stopped", -1)),
              p("p", Ym, V(h(D)), 1)
            ]),
            p("div", Qm, [
              r[100] || (r[100] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Daemon", -1)),
              p("div", Zm, [
                v(h(Lt), {
                  variant: a.value ? "green" : "red"
                }, {
                  default: k(() => [
                    y(V(a.value ? "Reachable" : "Not running"), 1)
                  ]),
                  _: 1
                }, 8, ["variant"])
              ])
            ]),
            p("div", Xm, [
              r[101] || (r[101] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Memory In Use", -1)),
              p("p", eg, V(h(W)(h(K))), 1)
            ]),
            p("div", tg, [
              r[102] || (r[102] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Total CPU (live)", -1)),
              p("p", sg, V(h(bt)()), 1),
              h(Q).length >= 2 ? (S(), M("svg", ng, [
                p("polyline", {
                  points: h(we)(h(Q), "cpuPct"),
                  fill: "none",
                  stroke: "currentColor",
                  "stroke-width": "1.5"
                }, null, 8, og)
              ])) : z("", !0),
              r[103] || (r[103] = p("p", { class: "mt-0.5 text-[10px] text-muted-foreground" }, "last ~2 min, sum of running containers", -1))
            ])
          ]),
          v(h(oe), { class: "mb-6" }, {
            default: k(() => [...r[104] || (r[104] = [
              y(" CPU shown here is a live rate (% of one core), computed from the change in cumulative CPU time between polls every 5 seconds — not the raw counter Incus reports, which only ever goes up. The sparkline is a rolling client-side window that resets on page reload; nothing is persisted server-side. ", -1)
            ])]),
            _: 1
          }),
          p("div", rg, [
            p("div", lg, [
              r[110] || (r[110] = p("h3", { class: "mb-1 text-base font-semibold" }, "Network & ACL", -1)),
              r[111] || (r[111] = p("p", { class: "mb-3 text-xs text-muted-foreground" }, " The policy currently configured for every container on this bridge (from saved config, not a live probe). ", -1)),
              p("div", ig, [
                p("div", null, [
                  r[105] || (r[105] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Bridge", -1)),
                  p("p", ag, V(w.jailBridge || "—"), 1)
                ]),
                p("div", null, [
                  r[106] || (r[106] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Subnet", -1)),
                  p("p", ug, V(w.jailSubnet || "—"), 1)
                ]),
                p("div", null, [
                  r[107] || (r[107] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "ACL Name", -1)),
                  p("p", dg, V(w.aclName || "—"), 1)
                ]),
                p("div", null, [
                  r[108] || (r[108] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Blocked Ranges", -1)),
                  p("p", cg, V(la()) + " blocked", 1)
                ]),
                p("div", null, [
                  r[109] || (r[109] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Default Egress / Ingress", -1)),
                  p("p", fg, V(w.aclDefaultEgress) + " / " + V(w.aclDefaultIngress), 1)
                ])
              ])
            ]),
            p("div", pg, [
              r[117] || (r[117] = p("h3", { class: "mb-1 text-base font-semibold" }, "Launch Container", -1)),
              r[118] || (r[118] = p("p", { class: "mb-3 text-xs text-muted-foreground" }, " Applies the Container Defaults profile — no build step. Each container gets its own independent root filesystem and workspace even when launched from the same image. ", -1)),
              p("div", mg, [
                p("div", gg, [
                  v(h(ne), {
                    for: "new-container-name",
                    class: "mb-2 block"
                  }, {
                    default: k(() => [...r[112] || (r[112] = [
                      y("Container name", -1)
                    ])]),
                    _: 1
                  }),
                  v(h(pe), {
                    id: "new-container-name",
                    modelValue: m.value,
                    "onUpdate:modelValue": r[15] || (r[15] = (u) => m.value = u),
                    placeholder: "new-container-name",
                    class: "w-full font-mono"
                  }, null, 8, ["modelValue"])
                ]),
                p("div", hg, [
                  v(h(ne), {
                    for: "launch-image",
                    class: "mb-2 block"
                  }, {
                    default: k(() => [...r[113] || (r[113] = [
                      y("Image", -1)
                    ])]),
                    _: 1
                  }),
                  v(h(ws), {
                    id: "launch-image",
                    modelValue: E.value,
                    "onUpdate:modelValue": r[16] || (r[16] = (u) => E.value = u),
                    class: "w-full"
                  }, {
                    default: k(() => [
                      p("option", bg, "Default (" + V(w.jailImage || "—") + ")", 1),
                      (S(!0), M(ue, null, Ye(Ct.value, (u) => (S(), M("option", {
                        key: u.alias,
                        value: u.alias
                      }, V(u.alias) + V(u.isMaster ? " (golden master)" : "") + " — " + V(u.distro) + "/" + V(u.release), 9, vg))), 128))
                    ]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                v(h(ce), {
                  size: "sm",
                  variant: "secondary",
                  disabled: !!g.value,
                  onClick: Os
                }, {
                  default: k(() => [...r[114] || (r[114] = [
                    y("Launch", -1)
                  ])]),
                  _: 1
                }, 8, ["disabled"])
              ]),
              m.value && g.value ? (S(), M("p", yg, V(g.value), 1)) : z("", !0),
              p("div", xg, [
                v(h(on), {
                  id: "launch-allow-sudo",
                  modelValue: U.value,
                  "onUpdate:modelValue": r[17] || (r[17] = (u) => U.value = u)
                }, null, 8, ["modelValue"]),
                r[115] || (r[115] = p("label", {
                  for: "launch-allow-sudo",
                  class: "cursor-pointer text-xs"
                }, " Allow sudo (NOPASSWD) for the agent user ", -1))
              ]),
              v(h(oe), null, {
                default: k(() => [...r[116] || (r[116] = [
                  y(` "Default" launches from Config → Container Defaults' image (the golden master, if one is set). Picking a specific image here launches from that image instead, just for this container — it doesn't change the default. Every launch, from any image, gets its own independent root filesystem; nothing is shared between containers built from the same source image. Sudo is off by default on purpose — the agent user having no path to root is what keeps a compromised dependency from escalating inside the container. Turning it on trades that away for convenience; you can also grant or check it later, per-container, from its Details panel. `, -1)
                ])]),
                _: 1
              })
            ])
          ]),
          p("div", _g, [
            p("div", wg, [
              r[119] || (r[119] = p("h3", { class: "text-base font-semibold" }, "Containers", -1)),
              h(D) > 0 ? (S(), Ie(h(ce), {
                key: 0,
                size: "sm",
                variant: "outline",
                disabled: _t.value,
                onClick: ms
              }, {
                default: k(() => [
                  y(V(_t.value ? "Deleting…" : `Delete ${h(D)} stopped`), 1)
                ]),
                _: 1
              }, 8, ["disabled"])) : z("", !0)
            ]),
            v(h(oe), null, {
              default: k(() => [...r[120] || (r[120] = [
                y(` "On bridge" means this container's address falls inside the configured subnet — a real check, not a claim that the LAN-ban ACL is actively enforced for it specifically (that's a daemon-level policy on the whole bridge, shown above under Network & ACL). Each row's mini charts are the same rolling client-side window as the summary cards above. `, -1)
              ])]),
              _: 1
            }),
            d.value.length === 0 ? (S(), M("p", kg, " No containers yet — launch one above to get started. ")) : (S(), M(ue, { key: 1 }, [
              p("p", Sg, " Total: " + V(h(H).length) + " container" + V(h(H).length === 1 ? "" : "s") + " running, " + V(h(W)(h(K))) + " memory, CPU time " + V(h(je)(Number(h(B)))), 1),
              p("div", Cg, [
                (S(!0), M(ue, null, Ye(d.value, (u) => (S(), M("div", {
                  key: u.name,
                  class: ot(["rounded-lg border border-border p-3", de.value === u.name ? "border-primary/50" : "border-border"])
                }, [
                  p("div", Ag, [
                    p("div", Eg, [
                      p("span", Ig, V(u.name), 1),
                      ma(u) ? (S(), M("span", Tg, "on bridge")) : z("", !0),
                      v(h(Lt), {
                        variant: ra(u.status)
                      }, {
                        default: k(() => [
                          y(V(u.status), 1)
                        ]),
                        _: 2
                      }, 1032, ["variant"])
                    ]),
                    p("span", Pg, V(u.ipv4 || "—"), 1)
                  ]),
                  p("div", Rg, [
                    p("div", null, [
                      p("p", {
                        class: "text-[10px] font-semibold tracking-[0.06em] uppercase text-muted-foreground",
                        title: `Live rate, % ${h(xe)()}`
                      }, "CPU", 8, Mg),
                      p("div", Vg, [
                        p("div", $g, [
                          h(re)(u) !== null ? (S(), M("div", {
                            key: 0,
                            class: "h-full rounded-full bg-primary",
                            style: bn({ width: h(re)(u) + "%" })
                          }, null, 4)) : z("", !0)
                        ]),
                        p("span", Og, V(h($e)(u)), 1),
                        h(He)(u.name).length >= 2 ? (S(), M("svg", jg, [
                          p("polyline", {
                            points: h(we)(h(He)(u.name), "cpuPct"),
                            fill: "none",
                            stroke: "currentColor",
                            "stroke-width": "1.5"
                          }, null, 8, Ng)
                        ])) : z("", !0)
                      ])
                    ]),
                    p("div", null, [
                      r[121] || (r[121] = p("p", { class: "text-[10px] font-semibold tracking-[0.06em] uppercase text-muted-foreground" }, "Memory", -1)),
                      p("div", Lg, [
                        p("span", Ug, V(h(te)(u)), 1),
                        h(He)(u.name).length >= 2 ? (S(), M("svg", Dg, [
                          p("polyline", {
                            points: h(we)(h(He)(u.name), "memPct"),
                            fill: "none",
                            stroke: "currentColor",
                            "stroke-width": "1.5"
                          }, null, 8, Bg)
                        ])) : z("", !0)
                      ]),
                      h(Re)(u) !== null ? (S(), M("div", Fg, [
                        p("div", {
                          class: "h-full rounded-full bg-primary",
                          style: bn({ width: h(Re)(u) + "%" })
                        }, null, 4)
                      ])) : z("", !0)
                    ])
                  ]),
                  p("div", Hg, [
                    v(h(ce), {
                      size: "sm",
                      variant: "outline",
                      onClick: ($) => Tn(u.name, "start")
                    }, {
                      default: k(() => [...r[122] || (r[122] = [
                        y("Start", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"]),
                    v(h(ce), {
                      size: "sm",
                      variant: "outline",
                      onClick: ($) => Tn(u.name, "stop")
                    }, {
                      default: k(() => [...r[123] || (r[123] = [
                        y("Stop", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"]),
                    v(h(ce), {
                      size: "sm",
                      variant: "secondary",
                      disabled: u.status.toLowerCase() !== "running",
                      onClick: ($) => A.value = u.name
                    }, {
                      default: k(() => [...r[124] || (r[124] = [
                        y("Console", -1)
                      ])]),
                      _: 1
                    }, 8, ["disabled", "onClick"]),
                    v(h(ce), {
                      size: "sm",
                      variant: "outline",
                      onClick: ($) => T(u.name)
                    }, {
                      default: k(() => [
                        y(V(de.value === u.name ? "Hide manage" : "Manage"), 1)
                      ]),
                      _: 2
                    }, 1032, ["onClick"]),
                    v(h(ce), {
                      size: "sm",
                      variant: "destructive",
                      onClick: ($) => xo(u.name)
                    }, {
                      default: k(() => [...r[125] || (r[125] = [
                        y("Delete", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"])
                  ]),
                  de.value === u.name ? (S(), M("div", zg, [
                    Pn.value ? (S(), M("p", Wg, "Loading…")) : Te.value ? (S(), M(ue, { key: 1 }, [
                      p("div", Kg, [
                        p("div", null, [
                          r[126] || (r[126] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Image", -1)),
                          p("p", qg, V(Te.value.imageOs || "—") + " " + V(Te.value.imageRelease || ""), 1)
                        ]),
                        p("div", null, [
                          r[127] || (r[127] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Profiles", -1)),
                          p("p", Gg, V(Te.value.profiles.join(", ")), 1)
                        ]),
                        p("div", null, [
                          r[128] || (r[128] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Storage pool", -1)),
                          p("p", Jg, V(Te.value.storagePool || "—"), 1)
                        ]),
                        p("div", null, [
                          r[129] || (r[129] = p("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Bridge", -1)),
                          p("p", Yg, V(Te.value.networkBridge || "—"), 1)
                        ])
                      ]),
                      p("div", Qg, [
                        p("div", Zg, [
                          p("div", null, [
                            v(h(ne), {
                              for: "detail-cpu-limit",
                              class: "mb-1 flex items-center gap-1.5 text-xs"
                            }, {
                              default: k(() => [
                                r[131] || (r[131] = y(" CPU limit ", -1)),
                                Te.value.cpuLimitIsOverride ? (S(), Ie(h(Lt), {
                                  key: 0,
                                  variant: "orange"
                                }, {
                                  default: k(() => [...r[130] || (r[130] = [
                                    y("override", -1)
                                  ])]),
                                  _: 1
                                })) : z("", !0)
                              ]),
                              _: 1
                            }),
                            p("div", Xg, [
                              v(h(pe), {
                                id: "detail-cpu-limit",
                                modelValue: _.value,
                                "onUpdate:modelValue": r[18] || (r[18] = ($) => _.value = $),
                                class: "w-24 font-mono",
                                placeholder: "e.g. 2"
                              }, null, 8, ["modelValue"]),
                              v(h(ce), {
                                size: "sm",
                                variant: "outline",
                                disabled: b.value,
                                onClick: N
                              }, {
                                default: k(() => [...r[132] || (r[132] = [
                                  y("Apply", -1)
                                ])]),
                                _: 1
                              }, 8, ["disabled"])
                            ])
                          ]),
                          p("div", null, [
                            v(h(ne), {
                              for: "detail-memory-limit",
                              class: "mb-1 flex items-center gap-1.5 text-xs"
                            }, {
                              default: k(() => [
                                r[134] || (r[134] = y(" Memory limit ", -1)),
                                Te.value.memoryLimitIsOverride ? (S(), Ie(h(Lt), {
                                  key: 0,
                                  variant: "orange"
                                }, {
                                  default: k(() => [...r[133] || (r[133] = [
                                    y("override", -1)
                                  ])]),
                                  _: 1
                                })) : z("", !0)
                              ]),
                              _: 1
                            }),
                            p("div", eh, [
                              v(h(pe), {
                                id: "detail-memory-limit",
                                modelValue: R.value,
                                "onUpdate:modelValue": r[19] || (r[19] = ($) => R.value = $),
                                class: "w-24 font-mono",
                                placeholder: "e.g. 4GiB"
                              }, null, 8, ["modelValue"]),
                              v(h(ce), {
                                size: "sm",
                                variant: "outline",
                                disabled: b.value,
                                onClick: O
                              }, {
                                default: k(() => [...r[135] || (r[135] = [
                                  y("Apply", -1)
                                ])]),
                                _: 1
                              }, 8, ["disabled"])
                            ])
                          ]),
                          Te.value.cpuLimitIsOverride || Te.value.memoryLimitIsOverride ? (S(), Ie(h(ce), {
                            key: 0,
                            size: "sm",
                            variant: "outline",
                            disabled: b.value,
                            onClick: P
                          }, {
                            default: k(() => [...r[136] || (r[136] = [
                              y("Use profile default", -1)
                            ])]),
                            _: 1
                          }, 8, ["disabled"])) : z("", !0)
                        ]),
                        p("div", null, [
                          v(h(ne), {
                            for: "detail-workspace",
                            class: "mb-1 flex items-center gap-1.5 text-xs"
                          }, {
                            default: k(() => [
                              r[138] || (r[138] = y(" Workspace host path (/workspace) ", -1)),
                              Te.value.workspaceIsOverride ? (S(), Ie(h(Lt), {
                                key: 0,
                                variant: "orange"
                              }, {
                                default: k(() => [...r[137] || (r[137] = [
                                  y("override", -1)
                                ])]),
                                _: 1
                              })) : z("", !0)
                            ]),
                            _: 1
                          }),
                          p("div", th, [
                            v(h(pe), {
                              id: "detail-workspace",
                              modelValue: I.value,
                              "onUpdate:modelValue": r[20] || (r[20] = ($) => I.value = $),
                              class: "flex-1 font-mono"
                            }, null, 8, ["modelValue"]),
                            v(h(ce), {
                              size: "sm",
                              variant: "outline",
                              disabled: b.value,
                              onClick: J
                            }, {
                              default: k(() => [...r[139] || (r[139] = [
                                y("Apply", -1)
                              ])]),
                              _: 1
                            }, 8, ["disabled"]),
                            Te.value.workspaceIsOverride ? (S(), Ie(h(ce), {
                              key: 0,
                              size: "sm",
                              variant: "outline",
                              disabled: b.value,
                              onClick: F
                            }, {
                              default: k(() => [...r[140] || (r[140] = [
                                y("Use profile default", -1)
                              ])]),
                              _: 1
                            }, 8, ["disabled"])) : z("", !0)
                          ])
                        ])
                      ]),
                      q(Te.value) ? (S(), M("div", sh, [
                        r[141] || (r[141] = p("span", null, [
                          y(" This container shares "),
                          p("span", { class: "font-mono" }, "/workspace"),
                          y(" with every other container still on the profile's default — file writes are live-visible between them. ")
                        ], -1)),
                        v(h(ce), {
                          size: "sm",
                          variant: "outline",
                          disabled: Y.value,
                          onClick: ie
                        }, {
                          default: k(() => [
                            y(V(Y.value ? "Isolating…" : "Isolate this container's workspace"), 1)
                          ]),
                          _: 1
                        }, 8, ["disabled"])
                      ])) : z("", !0),
                      f.value ? (S(), M("p", nh, V(f.value), 1)) : z("", !0),
                      v(h(oe), null, {
                        default: k(() => [...r[142] || (r[142] = [
                          y(` Values without an "override" badge are inherited straight from the container's profile and apply to every container using it. Applying here overrides just this one instance — it won't touch the profile or any other container. Memory limit changes need a restart of this container to actually take effect on a running instance (verified: clearing an override alone doesn't shrink an already-larger live cgroup limit back down). Isolating a shared workspace points it at a new, empty per-container directory — it does not copy any files already sitting in the old shared one. `, -1)
                        ])]),
                        _: 1
                      }),
                      p("div", oh, [
                        p("p", rh, [
                          r[143] || (r[143] = y(" Sudo (agent user) ", -1)),
                          v(h(Lt), {
                            variant: Te.value.sudoEnabled ? "green" : "gray"
                          }, {
                            default: k(() => [
                              y(V(Te.value.sudoEnabled ? "enabled" : "disabled"), 1)
                            ]),
                            _: 1
                          }, 8, ["variant"])
                        ]),
                        Te.value.sudoEnabled ? z("", !0) : (S(), Ie(h(ce), {
                          key: 0,
                          size: "sm",
                          variant: "outline",
                          disabled: ns.value,
                          onClick: st
                        }, {
                          default: k(() => [
                            y(V(ns.value ? "Granting…" : "Grant sudo (NOPASSWD)"), 1)
                          ]),
                          _: 1
                        }, 8, ["disabled"])),
                        v(h(oe), null, {
                          default: k(() => [...r[144] || (r[144] = [
                            y(" Off by default on purpose — this is what keeps a compromised dependency from escalating to root inside the container. Granting sudo here applies immediately to the running container and can't be un-granted from this panel (remove ", -1),
                            p("span", { class: "font-mono" }, "/etc/sudoers.d/agent", -1),
                            y(" manually, or via the privileged command box below, if you need to revoke it). ", -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      p("div", lh, [
                        v(h(ne), {
                          for: "homebrew-formula",
                          class: "mb-1 block text-xs"
                        }, {
                          default: k(() => [...r[145] || (r[145] = [
                            y("Install a package (Homebrew)", -1)
                          ])]),
                          _: 1
                        }),
                        p("div", ih, [
                          v(h(pe), {
                            id: "homebrew-formula",
                            modelValue: ae.value,
                            "onUpdate:modelValue": r[21] || (r[21] = ($) => ae.value = $),
                            class: "w-48 font-mono",
                            placeholder: "e.g. wget",
                            onKeydown: un(an(qt, ["prevent"]), ["enter"])
                          }, null, 8, ["modelValue", "onKeydown"]),
                          v(h(ce), {
                            size: "sm",
                            variant: "outline",
                            disabled: !ae.value.trim() || le.value,
                            onClick: qt
                          }, {
                            default: k(() => [
                              y(V(le.value ? "Installing…" : "Install"), 1)
                            ]),
                            _: 1
                          }, 8, ["disabled"])
                        ]),
                        Se.value ? (S(), M("p", ah, V(Se.value), 1)) : z("", !0),
                        Ae.value ? (S(), M("p", uh, V(Ae.value), 1)) : z("", !0),
                        v(h(oe), null, {
                          default: k(() => [...r[146] || (r[146] = [
                            y(` Best-effort: bootstraps Homebrew itself under this container's non-root "agent" user if it isn't already present (needs bash and git inside the container), installing to `, -1),
                            p("span", { class: "font-mono" }, "~/.linuxbrew", -1),
                            y(" rather than Homebrew's usual shared system path — the official installer needs ", -1),
                            p("span", { class: "font-mono" }, "sudo", -1),
                            y(` for that path, and "agent" deliberately has none inside these containers. This runs against the LIVE container over exec — it isn't baked into the image, so a rebuilt or replacement container won't have it. `, -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      p("div", dh, [
                        v(h(ne), {
                          for: "privileged-command",
                          class: "mb-1 block text-xs"
                        }, {
                          default: k(() => [...r[147] || (r[147] = [
                            y("Run a privileged command", -1)
                          ])]),
                          _: 1
                        }),
                        p("div", ch, [
                          v(h(pe), {
                            id: "privileged-command",
                            modelValue: We.value,
                            "onUpdate:modelValue": r[22] || (r[22] = ($) => We.value = $),
                            class: "flex-1 font-mono",
                            placeholder: "e.g. apt-get install -y htop",
                            onKeydown: un(an(Cr, ["prevent"]), ["enter"])
                          }, null, 8, ["modelValue", "onKeydown"]),
                          v(h(ce), {
                            size: "sm",
                            variant: "outline",
                            disabled: !We.value.trim() || wt.value,
                            onClick: Cr
                          }, {
                            default: k(() => [
                              y(V(wt.value ? "Running…" : "Run"), 1)
                            ]),
                            _: 1
                          }, 8, ["disabled"])
                        ]),
                        ut.value ? (S(), M("div", fh, [
                          p("p", {
                            class: ot(["text-xs", ut.value.status === "success" ? "text-unraid-green-800" : "text-destructive"])
                          }, V(ut.value.message), 3),
                          ut.value.stdout || ut.value.stderr ? (S(), M("pre", ph, V([ut.value.stdout, ut.value.stderr].filter(Boolean).join(`
`)), 1)) : z("", !0)
                        ])) : z("", !0),
                        v(h(oe), null, {
                          default: k(() => [...r[148] || (r[148] = [
                            y(` Runs as root, mediated by you here in the UI — the container's own "agent" user never gets this capability, so this stays safe even with sudo left off. Good for one-off fixes (a forgotten package) without needing the sudo toggle at all. `, -1)
                          ])]),
                          _: 1
                        })
                      ])
                    ], 64)) : z("", !0)
                  ])) : z("", !0)
                ], 2))), 128))
              ])
            ], 64))
          ])
        ])) : s.value === "config" ? (S(), M("section", mh, [
          p("div", gh, [
            p("section", hh, [
              r[164] || (r[164] = p("p", { class: "mb-1 text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Runtime", -1)),
              r[165] || (r[165] = p("h3", { class: "mb-4 text-base font-semibold" }, "Service", -1)),
              p("div", bh, [
                v(h(ne), { for: "config-enabled" }, {
                  default: k(() => [...r[150] || (r[150] = [
                    y("Enable Incus", -1)
                  ])]),
                  _: 1
                }),
                v(h(on), {
                  id: "config-enabled",
                  modelValue: w.enabled,
                  "onUpdate:modelValue": r[23] || (r[23] = (u) => w.enabled = u)
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[151] || (r[151] = [
                    y(" Starts incusd on array start. Leaving this off keeps the daemon — and its private-prefixed binaries under ", -1),
                    p("span", { class: "font-mono" }, "/usr/local/incus/", -1),
                    y(" — installed but never running. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-dashboard-widget" }, {
                  default: k(() => [...r[152] || (r[152] = [
                    y("Show Dashboard widget", -1)
                  ])]),
                  _: 1
                }),
                v(h(on), {
                  id: "config-dashboard-widget",
                  modelValue: w.dashboardWidgetEnable,
                  "onUpdate:modelValue": r[24] || (r[24] = (u) => w.dashboardWidgetEnable = u)
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[153] || (r[153] = [
                    y(" Shows a jail-status box (running/stopped/other counts) on Unraid's Main/Dashboard tab. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-state-dir" }, {
                  default: k(() => [...r[154] || (r[154] = [
                    y("Incus state directory", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-state-dir",
                  modelValue: w.stateDir,
                  "onUpdate:modelValue": r[25] || (r[25] = (u) => w.stateDir = u),
                  class: "w-96 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[155] || (r[155] = [
                    y(" Where incusd keeps its database, storage pool, and container state. Must be real persistent storage on the array, not tmpfs — this is the one thing that survives a reboot or plugin update. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              p("div", vh, [
                r[163] || (r[163] = p("h4", { class: "mb-3 text-sm font-semibold" }, "Storage pool", -1)),
                p("div", yh, [
                  v(h(ne), { for: "config-storage-driver" }, {
                    default: k(() => [...r[156] || (r[156] = [
                      y("Storage driver", -1)
                    ])]),
                    _: 1
                  }),
                  v(h(ws), {
                    id: "config-storage-driver",
                    modelValue: w.storageDriver,
                    "onUpdate:modelValue": r[26] || (r[26] = (u) => w.storageDriver = u),
                    class: "w-56 justify-self-end"
                  }, {
                    default: k(() => [...r[157] || (r[157] = [
                      p("option", { value: "dir" }, "dir (simple, no pool required)", -1),
                      p("option", { value: "zfs" }, "zfs (snapshots/speed, needs existing pool)", -1)
                    ])]),
                    _: 1
                  }, 8, ["modelValue"]),
                  v(h(oe), { class: "col-span-2" }, {
                    default: k(() => [...r[158] || (r[158] = [
                      p("span", { class: "font-mono" }, "dir", -1),
                      y(" needs no existing pool and always works — it's the default for exactly that reason. ", -1),
                      p("span", { class: "font-mono" }, "zfs", -1),
                      y(" gets snapshots and speed, but the pool or dataset must already exist on your system; there's no safe way to auto-create one on your array. ", -1)
                    ])]),
                    _: 1
                  }),
                  fe.value ? (S(), M(ue, { key: 0 }, [
                    v(h(ne), { for: "config-storage-source" }, {
                      default: k(() => [...r[159] || (r[159] = [
                        y("ZFS pool/dataset", -1)
                      ])]),
                      _: 1
                    }),
                    v(h(pe), {
                      id: "config-storage-source",
                      modelValue: w.storageSource,
                      "onUpdate:modelValue": r[27] || (r[27] = (u) => w.storageSource = u),
                      class: "w-96 justify-self-end font-mono"
                    }, null, 8, ["modelValue"]),
                    v(h(oe), { class: "col-span-2" }, {
                      default: k(() => [...r[160] || (r[160] = [
                        y(" An existing pool or dataset path, e.g. ", -1),
                        p("span", { class: "font-mono" }, "nvme/incus", -1),
                        y(". A dataset under this path is created if missing, but the pool itself must already exist. ", -1)
                      ])]),
                      _: 1
                    })
                  ], 64)) : z("", !0),
                  v(h(ne), { for: "config-storage-pool" }, {
                    default: k(() => [...r[161] || (r[161] = [
                      y("Incus storage pool name", -1)
                    ])]),
                    _: 1
                  }),
                  v(h(pe), {
                    id: "config-storage-pool",
                    modelValue: w.storagePoolName,
                    "onUpdate:modelValue": r[28] || (r[28] = (u) => w.storagePoolName = u),
                    class: "w-48 justify-self-end font-mono"
                  }, null, 8, ["modelValue"]),
                  v(h(oe), { class: "col-span-2" }, {
                    default: k(() => [...r[162] || (r[162] = [
                      y(" The name Incus itself uses for this storage pool internally — cosmetic, doesn't need to match anything else on the host. ", -1)
                    ])]),
                    _: 1
                  })
                ])
              ])
            ]),
            p("section", xh, [
              r[191] || (r[191] = p("p", { class: "mb-1 text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Network & Access", -1)),
              r[192] || (r[192] = p("h3", { class: "mb-4 text-base font-semibold" }, "Network & ACL (LAN-ban)", -1)),
              r[193] || (r[193] = p("p", { class: "mb-4 text-xs text-muted-foreground" }, " Controls the bridge/subnet containers attach to and the firewall rules governing what they can reach. ", -1)),
              p("div", _h, [
                v(h(ne), { for: "config-bridge" }, {
                  default: k(() => [...r[166] || (r[166] = [
                    y("Container bridge", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-bridge",
                  modelValue: w.jailBridge,
                  "onUpdate:modelValue": r[29] || (r[29] = (u) => w.jailBridge = u),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[167] || (r[167] = [
                    y(" A dedicated NAT bridge name for containers, kept separate from Unraid's own br0 so container traffic never touches host networking directly. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-subnet" }, {
                  default: k(() => [...r[168] || (r[168] = [
                    y("Container subnet", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-subnet",
                  modelValue: w.jailSubnet,
                  "onUpdate:modelValue": r[30] || (r[30] = (u) => w.jailSubnet = u),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[169] || (r[169] = [
                    y(" CIDR for the bridge. Defaults to an RFC 2544 benchmark range specifically because it won't collide with a typical home or office LAN. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-nat" }, {
                  default: k(() => [...r[170] || (r[170] = [
                    y("NAT", -1)
                  ])]),
                  _: 1
                }),
                v(h(on), {
                  id: "config-nat",
                  modelValue: w.jailNat,
                  "onUpdate:modelValue": r[31] || (r[31] = (u) => w.jailNat = u)
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[171] || (r[171] = [
                    y(" Routes container traffic to the Internet through the host. Turning this off isolates containers with no outbound access at all — no Internet, no LAN. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-ipv6" }, {
                  default: k(() => [...r[172] || (r[172] = [
                    y("IPv6", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-ipv6",
                  modelValue: w.jailIpv6,
                  "onUpdate:modelValue": r[32] || (r[32] = (u) => w.jailIpv6 = u),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[173] || (r[173] = [
                    y("An IPv6 address for the bridge, or ", -1),
                    p("span", { class: "font-mono" }, "none", -1),
                    y(" to disable IPv6 for containers entirely.", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-acl-name" }, {
                  default: k(() => [...r[174] || (r[174] = [
                    y("ACL name", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-acl-name",
                  modelValue: w.aclName,
                  "onUpdate:modelValue": r[33] || (r[33] = (u) => w.aclName = u),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[175] || (r[175] = [
                    y(" The name of the Incus network ACL that enforces the LAN ban — created and applied to the bridge by the array-start init script. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-egress" }, {
                  default: k(() => [...r[176] || (r[176] = [
                    y("Default egress action", -1)
                  ])]),
                  _: 1
                }),
                v(h(ws), {
                  id: "config-egress",
                  modelValue: w.aclDefaultEgress,
                  "onUpdate:modelValue": r[34] || (r[34] = (u) => w.aclDefaultEgress = u),
                  class: "w-32 justify-self-end"
                }, {
                  default: k(() => [...r[177] || (r[177] = [
                    p("option", { value: "allow" }, "allow", -1),
                    p("option", { value: "drop" }, "drop", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"]),
                v(h(ne), { for: "config-ingress" }, {
                  default: k(() => [...r[178] || (r[178] = [
                    y("Default ingress action", -1)
                  ])]),
                  _: 1
                }),
                v(h(ws), {
                  id: "config-ingress",
                  modelValue: w.aclDefaultIngress,
                  "onUpdate:modelValue": r[35] || (r[35] = (u) => w.aclDefaultIngress = u),
                  class: "w-32 justify-self-end"
                }, {
                  default: k(() => [...r[179] || (r[179] = [
                    p("option", { value: "allow" }, "allow", -1),
                    p("option", { value: "drop" }, "drop", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[180] || (r[180] = [
                    y(" What happens to traffic not covered by a rule above. Egress defaults to allow (deny-list model — Internet stays reachable unless explicitly blocked); ingress defaults to drop (nothing reaches a container unsolicited). Tailscale's CGNAT range (100.64.0.0/10) is intentionally excluded from the block list by default so containers can reach your tailnet. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              p("div", wh, [
                v(h(ne), {
                  for: "new-blocked-cidr",
                  class: "mb-1.5 block"
                }, {
                  default: k(() => [...r[181] || (r[181] = [
                    y("Blocked CIDRs (deny-list)", -1)
                  ])]),
                  _: 1
                }),
                Ns.value.length > 0 ? (S(), M("div", kh, [
                  (S(!0), M(ue, null, Ye(Ns.value, (u) => (S(), M("span", {
                    key: u,
                    class: "flex items-center gap-1.5 rounded-md border border-border px-2 py-1 font-mono text-xs"
                  }, [
                    y(V(u) + " ", 1),
                    p("button", {
                      type: "button",
                      class: "cursor-pointer text-muted-foreground hover:text-destructive",
                      onClick: ($) => ca(u)
                    }, "✕", 8, Sh)
                  ]))), 128))
                ])) : z("", !0),
                p("div", Ch, [
                  v(h(pe), {
                    id: "new-blocked-cidr",
                    modelValue: Us.value,
                    "onUpdate:modelValue": r[36] || (r[36] = (u) => Us.value = u),
                    class: "w-full font-mono",
                    placeholder: "e.g. 10.0.0.0/8",
                    onKeydown: un(an(Tr, ["prevent"]), ["enter"])
                  }, null, 8, ["modelValue", "onKeydown"]),
                  v(h(ce), {
                    size: "sm",
                    variant: "outline",
                    disabled: !Us.value.trim(),
                    onClick: Tr
                  }, {
                    default: k(() => [...r[182] || (r[182] = [
                      y("Add", -1)
                    ])]),
                    _: 1
                  }, 8, ["disabled"])
                ]),
                Bs.value ? (S(), M("p", Ah, V(Bs.value), 1)) : z("", !0),
                v(h(oe), null, {
                  default: k(() => [...r[183] || (r[183] = [
                    y(" Ranges containers may not reach — this is the actual LAN ban. Add one CIDR at a time; defaults to the private IPv4 ranges (RFC 1918) plus link-local addresses. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              p("div", Eh, [
                v(h(ne), {
                  for: "new-allow-cidr",
                  class: "mb-1.5 block"
                }, {
                  default: k(() => [...r[184] || (r[184] = [
                    y("Allow-holes (punched before block rules)", -1)
                  ])]),
                  _: 1
                }),
                Ls.value.length > 0 ? (S(), M("div", Ih, [
                  (S(!0), M(ue, null, Ye(Ls.value, (u) => (S(), M("span", {
                    key: u,
                    class: "flex items-center gap-1.5 rounded-md border border-border px-2 py-1 font-mono text-xs"
                  }, [
                    y(V(u) + " ", 1),
                    p("button", {
                      type: "button",
                      class: "cursor-pointer text-muted-foreground hover:text-destructive",
                      onClick: ($) => fa(u)
                    }, "✕", 8, Th)
                  ]))), 128))
                ])) : z("", !0),
                p("div", Ph, [
                  v(h(pe), {
                    id: "new-allow-cidr",
                    modelValue: Ds.value,
                    "onUpdate:modelValue": r[37] || (r[37] = (u) => Ds.value = u),
                    class: "w-full font-mono",
                    placeholder: "e.g. 100.64.0.0/10",
                    onKeydown: un(an(Pr, ["prevent"]), ["enter"])
                  }, null, 8, ["modelValue", "onKeydown"]),
                  v(h(ce), {
                    size: "sm",
                    variant: "outline",
                    disabled: !Ds.value.trim(),
                    onClick: Pr
                  }, {
                    default: k(() => [...r[185] || (r[185] = [
                      y("Add", -1)
                    ])]),
                    _: 1
                  }, 8, ["disabled"])
                ]),
                Fs.value ? (S(), M("p", Rh, V(Fs.value), 1)) : z("", !0),
                v(h(oe), null, {
                  default: k(() => [...r[186] || (r[186] = [
                    y(" Exceptions punched through the block list before it's evaluated — e.g. one specific internal service (a local LLM, a search index) a container legitimately needs to reach. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              p("div", Mh, [
                r[189] || (r[189] = p("h4", { class: "mb-3 text-sm font-semibold" }, "Tailscale", -1)),
                r[190] || (r[190] = p("p", { class: "mb-4 text-xs text-muted-foreground" }, " Optional — when set, new containers automatically join your tailnet using this key. ", -1)),
                p("div", Vh, [
                  v(h(ne), { for: "tailscale-auth-key" }, {
                    default: k(() => [...r[187] || (r[187] = [
                      y("Tailscale auth key", -1)
                    ])]),
                    _: 1
                  }),
                  p("div", $h, [
                    v(h(pe), {
                      id: "tailscale-auth-key",
                      modelValue: Me.value,
                      "onUpdate:modelValue": r[38] || (r[38] = (u) => Me.value = u),
                      type: se.value ? "text" : "password",
                      class: "w-72 font-mono",
                      placeholder: w.tsAuthKeyConfigured ? "Configured — enter a replacement" : "tskey-auth-…"
                    }, null, 8, ["modelValue", "type", "placeholder"]),
                    v(h(ce), {
                      size: "sm",
                      variant: "outline",
                      onClick: r[39] || (r[39] = (u) => se.value = !se.value)
                    }, {
                      default: k(() => [
                        y(V(se.value ? "Hide" : "Show"), 1)
                      ]),
                      _: 1
                    }),
                    w.tsAuthKeyConfigured ? (S(), Ie(h(ce), {
                      key: 0,
                      size: "sm",
                      variant: "outline",
                      onClick: r[40] || (r[40] = (u) => De.value = !De.value)
                    }, {
                      default: k(() => [
                        y(V(De.value ? "Keep key" : "Clear on save"), 1)
                      ]),
                      _: 1
                    })) : z("", !0)
                  ]),
                  v(h(oe), { class: "col-span-2" }, {
                    default: k(() => [...r[188] || (r[188] = [
                      y(" The stored key is write-only and is never returned to this page. A reusable or ephemeral key from your Tailscale admin console. Best-effort: if a container's image doesn't have Tailscale installed, joining is silently skipped rather than failing the launch — it never blocks a container from starting. ", -1)
                    ])]),
                    _: 1
                  })
                ])
              ])
            ]),
            p("section", Oh, [
              r[212] || (r[212] = p("p", { class: "mb-1 text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Container Defaults", -1)),
              r[213] || (r[213] = p("h3", { class: "mb-4 text-base font-semibold" }, "Defaults", -1)),
              p("div", jh, [
                v(h(ne), { for: "config-profile" }, {
                  default: k(() => [...r[194] || (r[194] = [
                    y("Container profile", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-profile",
                  modelValue: w.jailProfile,
                  "onUpdate:modelValue": r[41] || (r[41] = (u) => w.jailProfile = u),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[195] || (r[195] = [
                    y(" The Incus profile new containers launch with — sets resource limits, network, and mounts, defined in the array-start init script's profile template. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-image" }, {
                  default: k(() => [...r[196] || (r[196] = [
                    y("Default image", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-image",
                  modelValue: w.jailImage,
                  "onUpdate:modelValue": r[42] || (r[42] = (u) => w.jailImage = u),
                  class: "w-96 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[197] || (r[197] = [
                    y(" Used when launching a container without picking a specific image — either a remote reference like ", -1),
                    p("span", { class: "font-mono" }, "images:debian/trixie/cloud", -1),
                    y(", or a locally-built image's alias. Marking an image as the golden master in the Builder tab sets this automatically. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-nesting" }, {
                  default: k(() => [...r[198] || (r[198] = [
                    y("Allow nesting", -1)
                  ])]),
                  _: 1
                }),
                v(h(on), {
                  id: "config-nesting",
                  modelValue: w.jailNesting,
                  "onUpdate:modelValue": r[43] || (r[43] = (u) => w.jailNesting = u)
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[199] || (r[199] = [
                    y(" Lets a container run Docker or Incus inside itself — needed for agents that spin up their own sandboxes, but widens what a compromised container could reach. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-cpu" }, {
                  default: k(() => [...r[200] || (r[200] = [
                    y("CPU limit", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-cpu",
                  modelValue: w.jailCpu,
                  "onUpdate:modelValue": r[44] || (r[44] = (u) => w.jailCpu = u),
                  class: "w-24 justify-self-end font-mono",
                  placeholder: "empty = no cap"
                }, null, 8, ["modelValue"]),
                x.value ? (S(), M("p", Nh, V(x.value), 1)) : z("", !0),
                v(h(ne), { for: "config-memory" }, {
                  default: k(() => [...r[201] || (r[201] = [
                    y("Memory limit", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-memory",
                  modelValue: w.jailMemory,
                  "onUpdate:modelValue": r[45] || (r[45] = (u) => w.jailMemory = u),
                  class: "w-24 justify-self-end font-mono",
                  placeholder: "empty = no cap"
                }, null, 8, ["modelValue"]),
                C.value ? (S(), M("p", Lh, V(C.value), 1)) : z("", !0),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[202] || (r[202] = [
                    y(" Hard resource ceiling applied via the container profile at launch — CPU as a core count (e.g. ", -1),
                    p("span", { class: "font-mono" }, "2", -1),
                    y("), memory with a unit (e.g. ", -1),
                    p("span", { class: "font-mono" }, "4GiB", -1),
                    y("). Leave either empty for no cap. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-workspace" }, {
                  default: k(() => [...r[203] || (r[203] = [
                    y("Workspace root", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-workspace",
                  modelValue: w.jailWorkspaceRoot,
                  "onUpdate:modelValue": r[46] || (r[46] = (u) => w.jailWorkspaceRoot = u),
                  class: "w-96 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[204] || (r[204] = [
                    y(` Host directory holding per-container workspaces, bind-mounted in with idmap shifting. Must be real persistent storage — the init script refuses to start if it's tmpfs, since that would silently lose "persistent" data on every reboot. Prefer a real device mount (e.g. `, -1),
                    p("span", { class: "font-mono" }, "/mnt/cache/appdata/...", -1),
                    y(") over a ", -1),
                    p("span", { class: "font-mono" }, "/mnt/user/...", -1),
                    y(" path — Unraid's shfs FUSE union view generally doesn't support the idmapped-mount feature the shift needs. ", -1)
                  ])]),
                  _: 1
                }),
                v(h(ne), { for: "config-agent-uid" }, {
                  default: k(() => [...r[205] || (r[205] = [
                    y("Agent UID", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-agent-uid",
                  modelValue: w.jailAgentUid,
                  "onUpdate:modelValue": r[47] || (r[47] = (u) => w.jailAgentUid = u),
                  class: "w-24 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(ne), { for: "config-agent-gid" }, {
                  default: k(() => [...r[206] || (r[206] = [
                    y("Agent GID", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-agent-gid",
                  modelValue: w.jailAgentGid,
                  "onUpdate:modelValue": r[48] || (r[48] = (u) => w.jailAgentGid = u),
                  class: "w-24 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                v(h(oe), { class: "col-span-2" }, {
                  default: k(() => [...r[207] || (r[207] = [
                    y(" The uid/gid inside each container mapped to your host user — match your own host user if you want files under the bind-mounted workspace to show correct ownership from outside the container. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              p("div", Uh, [
                r[210] || (r[210] = p("h4", { class: "mb-3 text-sm font-semibold" }, "Bind mounts", -1)),
                v(h(ne), {
                  for: "config-bind-mounts",
                  class: "mb-2 block"
                }, {
                  default: k(() => [...r[208] || (r[208] = [
                    y("Host config bind-mounts", -1)
                  ])]),
                  _: 1
                }),
                v(h(pe), {
                  id: "config-bind-mounts",
                  modelValue: w.jailBindMounts,
                  "onUpdate:modelValue": r[49] || (r[49] = (u) => w.jailBindMounts = u),
                  class: "w-full font-mono",
                  placeholder: "/root/.claude:/home/agent/.claude,/root/.codex:/home/agent/.codex:ro"
                }, null, 8, ["modelValue"]),
                r[211] || (r[211] = p("p", { class: "mt-2 text-xs text-muted-foreground" }, " Comma-separated host:container[:ro] triples, mounted into every dev container for agent auth/config reuse. ", -1)),
                v(h(oe), null, {
                  default: k(() => [...r[209] || (r[209] = [
                    y(" Mounted into every container at launch, not baked into any built image — so updating credentials or config on the host applies to containers immediately, without rebuilding. Append ", -1),
                    p("span", { class: "font-mono" }, ":ro", -1),
                    y(" to a triple to mount it read-only (e.g. for something you don't want an agent able to modify). ", -1)
                  ])]),
                  _: 1
                })
              ])
            ])
          ]),
          p("div", Dh, [
            v(h(ce), {
              disabled: l.value || !!x.value || !!C.value,
              onClick: In
            }, {
              default: k(() => [
                y(V(l.value ? "Applying…" : "Apply"), 1)
              ]),
              _: 1
            }, 8, ["disabled"])
          ])
        ])) : z("", !0)
      ], 64)),
      A.value ? (S(), Ie(h(t), {
        key: 2,
        "jail-name": A.value,
        onClose: r[50] || (r[50] = (u) => A.value = null)
      }, null, 8, ["jail-name"])) : z("", !0)
    ]));
  }
}), zh = /* @__PURE__ */ cc(Hh, { shadowRoot: !1 });
customElements.get("incus-settings-app") || customElements.define("incus-settings-app", zh);
export {
  ce as _,
  xi as a,
  S as b,
  M as c,
  qe as d,
  p as e,
  v as f,
  y as g,
  z as h,
  ve as i,
  bn as n,
  vi as o,
  L as r,
  V as t,
  h as u,
  k as w
};
