/**
* @vue/shared v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
// @__NO_SIDE_EFFECTS__
function ir(e) {
  const t = /* @__PURE__ */ Object.create(null);
  for (const s of e.split(",")) t[s] = 1;
  return (s) => s in t;
}
const ge = {}, Es = [], Mt = () => {
}, Dl = () => !1, lo = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && // uppercase letter
(e.charCodeAt(2) > 122 || e.charCodeAt(2) < 97), io = (e) => e.startsWith("onUpdate:"), Ue = Object.assign, ar = (e, t) => {
  const s = e.indexOf(t);
  s > -1 && e.splice(s, 1);
}, Ja = Object.prototype.hasOwnProperty, ye = (e, t) => Ja.call(e, t), J = Array.isArray, Is = (e) => An(e) === "[object Map]", js = (e) => An(e) === "[object Set]", Yr = (e) => An(e) === "[object Date]", X = (e) => typeof e == "function", Ve = (e) => typeof e == "string", ht = (e) => typeof e == "symbol", _e = (e) => e !== null && typeof e == "object", Bl = (e) => (_e(e) || X(e)) && X(e.then) && X(e.catch), Fl = Object.prototype.toString, An = (e) => Fl.call(e), Ya = (e) => An(e).slice(8, -1), ao = (e) => An(e) === "[object Object]", uo = (e) => Ve(e) && e !== "NaN" && e[0] !== "-" && "" + parseInt(e, 10) === e, pn = /* @__PURE__ */ ir(
  // the leading comma is intentional so empty string "" is also included
  ",key,ref,ref_for,ref_key,onVnodeBeforeMount,onVnodeMounted,onVnodeBeforeUpdate,onVnodeUpdated,onVnodeBeforeUnmount,onVnodeUnmounted"
), co = (e) => {
  const t = /* @__PURE__ */ Object.create(null);
  return ((s) => t[s] || (t[s] = e(s)));
}, Qa = /-\w/g, Ge = co(
  (e) => e.replace(Qa, (t) => t.slice(1).toUpperCase())
), Za = /\B([A-Z])/g, ct = co(
  (e) => e.replace(Za, "-$1").toLowerCase()
), Hl = co((e) => e.charAt(0).toUpperCase() + e.slice(1)), qn = co(
  (e) => e ? `on${Hl(e)}` : ""
), qe = (e, t) => !Object.is(e, t), Gn = (e, ...t) => {
  for (let s = 0; s < e.length; s++)
    e[s](...t);
}, zl = (e, t, s, n = !1) => {
  Object.defineProperty(e, t, {
    configurable: !0,
    enumerable: !1,
    writable: n,
    value: s
  });
}, fo = (e) => {
  const t = parseFloat(e);
  return isNaN(t) ? e : t;
}, Qr = (e) => {
  const t = Ve(e) ? Number(e) : NaN;
  return isNaN(t) ? e : t;
};
let Zr;
const po = () => Zr || (Zr = typeof globalThis < "u" ? globalThis : typeof self < "u" ? self : typeof window < "u" ? window : typeof global < "u" ? global : {});
function xn(e) {
  if (J(e)) {
    const t = {};
    for (let s = 0; s < e.length; s++) {
      const n = e[s], o = Ve(n) ? su(n) : xn(n);
      if (o)
        for (const l in o)
          t[l] = o[l];
    }
    return t;
  } else if (Ve(e) || _e(e))
    return e;
}
const Xa = /;(?![^(]*\))/g, eu = /:([^]+)/, tu = /\/\*[^]*?\*\//g;
function su(e) {
  const t = {};
  return e.replace(tu, "").split(Xa).forEach((s) => {
    if (s) {
      const n = s.split(eu);
      n.length > 1 && (t[n[0].trim()] = n[1].trim());
    }
  }), t;
}
function lt(e) {
  let t = "";
  if (Ve(e))
    t = e;
  else if (J(e))
    for (let s = 0; s < e.length; s++) {
      const n = lt(e[s]);
      n && (t += n + " ");
    }
  else if (_e(e))
    for (const s in e)
      e[s] && (t += s + " ");
  return t.trim();
}
const nu = "itemscope,allowfullscreen,formnovalidate,ismap,nomodule,novalidate,readonly", ou = /* @__PURE__ */ ir(nu);
function Wl(e) {
  return !!e || e === "";
}
function ru(e, t) {
  if (e.length !== t.length) return !1;
  let s = !0;
  for (let n = 0; s && n < e.length; n++)
    s = es(e[n], t[n]);
  return s;
}
function es(e, t) {
  if (e === t) return !0;
  let s = Yr(e), n = Yr(t);
  if (s || n)
    return s && n ? e.getTime() === t.getTime() : !1;
  if (s = ht(e), n = ht(t), s || n)
    return e === t;
  if (s = J(e), n = J(t), s || n)
    return s && n ? ru(e, t) : !1;
  if (s = _e(e), n = _e(t), s || n) {
    if (!s || !n)
      return !1;
    const o = Object.keys(e).length, l = Object.keys(t).length;
    if (o !== l)
      return !1;
    for (const i in e) {
      const a = e.hasOwnProperty(i), u = t.hasOwnProperty(i);
      if (a && !u || !a && u || !es(e[i], t[i]))
        return !1;
    }
  }
  return String(e) === String(t);
}
function ur(e, t) {
  return e.findIndex((s) => es(s, t));
}
const Kl = (e) => !!(e && e.__v_isRef === !0), M = (e) => Ve(e) ? e : e == null ? "" : J(e) || _e(e) && (e.toString === Fl || !X(e.toString)) ? Kl(e) ? M(e.value) : JSON.stringify(e, ql, 2) : String(e), ql = (e, t) => Kl(t) ? ql(e, t.value) : Is(t) ? {
  [`Map(${t.size})`]: [...t.entries()].reduce(
    (s, [n, o], l) => (s[Oo(n, l) + " =>"] = o, s),
    {}
  )
} : js(t) ? {
  [`Set(${t.size})`]: [...t.values()].map((s) => Oo(s))
} : ht(t) ? Oo(t) : _e(t) && !J(t) && !ao(t) ? String(t) : t, Oo = (e, t = "") => {
  var s;
  return (
    // Symbol.description in es2019+ so we need to cast here to pass
    // the lib: es2016 check
    ht(e) ? `Symbol(${(s = e.description) != null ? s : t})` : e
  );
};
/**
* @vue/reactivity v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
let Ke;
class lu {
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
function iu() {
  return Ke;
}
let Se;
const jo = /* @__PURE__ */ new WeakSet();
class Gl {
  constructor(t) {
    this.fn = t, this.deps = void 0, this.depsTail = void 0, this.flags = 5, this.next = void 0, this.cleanup = void 0, this.scheduler = void 0, Ke && (Ke.active ? Ke.effects.push(this) : this.flags &= -2);
  }
  pause() {
    this.flags |= 64;
  }
  resume() {
    this.flags & 64 && (this.flags &= -65, jo.has(this) && (jo.delete(this), this.trigger()));
  }
  /**
   * @internal
   */
  notify() {
    this.flags & 2 && !(this.flags & 32) || this.flags & 8 || Yl(this);
  }
  run() {
    if (!(this.flags & 1))
      return this.fn();
    this.flags |= 2, Xr(this), Ql(this);
    const t = Se, s = xt;
    Se = this, xt = !0;
    try {
      return this.fn();
    } finally {
      Zl(this), Se = t, xt = s, this.flags &= -3;
    }
  }
  stop() {
    if (this.flags & 1) {
      for (let t = this.deps; t; t = t.nextDep)
        fr(t);
      this.deps = this.depsTail = void 0, Xr(this), this.onStop && this.onStop(), this.flags &= -2;
    }
  }
  trigger() {
    this.flags & 64 ? jo.add(this) : this.scheduler ? this.scheduler() : this.runIfDirty();
  }
  /**
   * @internal
   */
  runIfDirty() {
    Jo(this) && this.run();
  }
  get dirty() {
    return Jo(this);
  }
}
let Jl = 0, mn, gn;
function Yl(e, t = !1) {
  if (e.flags |= 8, t) {
    e.next = gn, gn = e;
    return;
  }
  e.next = mn, mn = e;
}
function dr() {
  Jl++;
}
function cr() {
  if (--Jl > 0)
    return;
  if (gn) {
    let t = gn;
    for (gn = void 0; t; ) {
      const s = t.next;
      t.next = void 0, t.flags &= -9, t = s;
    }
  }
  let e;
  for (; mn; ) {
    let t = mn;
    for (mn = void 0; t; ) {
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
function Ql(e) {
  for (let t = e.deps; t; t = t.nextDep)
    t.version = -1, t.prevActiveLink = t.dep.activeLink, t.dep.activeLink = t;
}
function Zl(e) {
  let t, s = e.depsTail, n = s;
  for (; n; ) {
    const o = n.prevDep;
    n.version === -1 ? (n === s && (s = o), fr(n), au(n)) : t = n, n.dep.activeLink = n.prevActiveLink, n.prevActiveLink = void 0, n = o;
  }
  e.deps = t, e.depsTail = s;
}
function Jo(e) {
  for (let t = e.deps; t; t = t.nextDep)
    if (t.dep.version !== t.version || t.dep.computed && (Xl(t.dep.computed) || t.dep.version !== t.version))
      return !0;
  return !!e._dirty;
}
function Xl(e) {
  if (e.flags & 4 && !(e.flags & 16) || (e.flags &= -17, e.globalVersion === _n) || (e.globalVersion = _n, !e.isSSR && e.flags & 128 && (!e.deps && !e._dirty || !Jo(e))))
    return;
  e.flags |= 2;
  const t = e.dep, s = Se, n = xt;
  Se = e, xt = !0;
  try {
    Ql(e);
    const o = e.fn(e._value);
    (t.version === 0 || qe(o, e._value)) && (e.flags |= 128, e._value = o, t.version++);
  } catch (o) {
    throw t.version++, o;
  } finally {
    Se = s, xt = n, Zl(e), e.flags &= -3;
  }
}
function fr(e, t = !1) {
  const { dep: s, prevSub: n, nextSub: o } = e;
  if (n && (n.nextSub = o, e.prevSub = void 0), o && (o.prevSub = n, e.nextSub = void 0), s.subs === e && (s.subs = n, !n && s.computed)) {
    s.computed.flags &= -5;
    for (let l = s.computed.deps; l; l = l.nextDep)
      fr(l, !0);
  }
  !t && !--s.sc && s.map && s.map.delete(s.key);
}
function au(e) {
  const { prevDep: t, nextDep: s } = e;
  t && (t.nextDep = s, e.prevDep = void 0), s && (s.prevDep = t, e.nextDep = void 0);
}
let xt = !0;
const ei = [];
function Vt() {
  ei.push(xt), xt = !1;
}
function $t() {
  const e = ei.pop();
  xt = e === void 0 ? !0 : e;
}
function Xr(e) {
  const { cleanup: t } = e;
  if (e.cleanup = void 0, t) {
    const s = Se;
    Se = void 0;
    try {
      t();
    } finally {
      Se = s;
    }
  }
}
let _n = 0;
class uu {
  constructor(t, s) {
    this.sub = t, this.dep = s, this.version = s.version, this.nextDep = this.prevDep = this.nextSub = this.prevSub = this.prevActiveLink = void 0;
  }
}
class mo {
  // TODO isolatedDeclarations "__v_skip"
  constructor(t) {
    this.computed = t, this.version = 0, this.activeLink = void 0, this.subs = void 0, this.map = void 0, this.key = void 0, this.sc = 0, this.__v_skip = !0;
  }
  track(t) {
    if (!Se || !xt || Se === this.computed)
      return;
    let s = this.activeLink;
    if (s === void 0 || s.sub !== Se)
      s = this.activeLink = new uu(Se, this), Se.deps ? (s.prevDep = Se.depsTail, Se.depsTail.nextDep = s, Se.depsTail = s) : Se.deps = Se.depsTail = s, ti(s);
    else if (s.version === -1 && (s.version = this.version, s.nextDep)) {
      const n = s.nextDep;
      n.prevDep = s.prevDep, s.prevDep && (s.prevDep.nextDep = n), s.prevDep = Se.depsTail, s.nextDep = void 0, Se.depsTail.nextDep = s, Se.depsTail = s, Se.deps === s && (Se.deps = n);
    }
    return s;
  }
  trigger(t) {
    this.version++, _n++, this.notify(t);
  }
  notify(t) {
    dr();
    try {
      for (let s = this.subs; s; s = s.prevSub)
        s.sub.notify() && s.sub.dep.notify();
    } finally {
      cr();
    }
  }
}
function ti(e) {
  if (e.dep.sc++, e.sub.flags & 4) {
    const t = e.dep.computed;
    if (t && !e.dep.subs) {
      t.flags |= 20;
      for (let n = t.deps; n; n = n.nextDep)
        ti(n);
    }
    const s = e.dep.subs;
    s !== e && (e.prevSub = s, s && (s.nextSub = e)), e.dep.subs = e;
  }
}
const Qn = /* @__PURE__ */ new WeakMap(), fs = /* @__PURE__ */ Symbol(
  ""
), Yo = /* @__PURE__ */ Symbol(
  ""
), wn = /* @__PURE__ */ Symbol(
  ""
);
function et(e, t, s) {
  if (xt && Se) {
    let n = Qn.get(e);
    n || Qn.set(e, n = /* @__PURE__ */ new Map());
    let o = n.get(s);
    o || (n.set(s, o = new mo()), o.map = n, o.key = s), o.track();
  }
}
function Ht(e, t, s, n, o, l) {
  const i = Qn.get(e);
  if (!i) {
    _n++;
    return;
  }
  const a = (u) => {
    u && u.trigger();
  };
  if (dr(), t === "clear")
    i.forEach(a);
  else {
    const u = J(e), h = u && uo(s);
    if (u && s === "length") {
      const g = Number(n);
      i.forEach((x, A) => {
        (A === "length" || A === wn || !ht(A) && A >= g) && a(x);
      });
    } else
      switch ((s !== void 0 || i.has(void 0)) && a(i.get(s)), h && a(i.get(wn)), t) {
        case "add":
          u ? h && a(i.get("length")) : (a(i.get(fs)), Is(e) && a(i.get(Yo)));
          break;
        case "delete":
          u || (a(i.get(fs)), Is(e) && a(i.get(Yo)));
          break;
        case "set":
          Is(e) && a(i.get(fs));
          break;
      }
  }
  cr();
}
function du(e, t) {
  const s = Qn.get(e);
  return s && s.get(t);
}
function Ss(e) {
  const t = /* @__PURE__ */ ve(e);
  return t === e ? t : (et(t, "iterate", wn), /* @__PURE__ */ gt(e) ? t : t.map(_t));
}
function go(e) {
  return et(e = /* @__PURE__ */ ve(e), "iterate", wn), e;
}
function Pt(e, t) {
  return /* @__PURE__ */ qt(e) ? Vs(/* @__PURE__ */ ps(e) ? _t(t) : t) : _t(t);
}
const cu = {
  __proto__: null,
  [Symbol.iterator]() {
    return No(this, Symbol.iterator, (e) => Pt(this, e));
  },
  concat(...e) {
    return Ss(this).concat(
      ...e.map((t) => J(t) ? Ss(t) : t)
    );
  },
  entries() {
    return No(this, "entries", (e) => (e[1] = Pt(this, e[1]), e));
  },
  every(e, t) {
    return Lt(this, "every", e, t, void 0, arguments);
  },
  filter(e, t) {
    return Lt(
      this,
      "filter",
      e,
      t,
      (s) => s.map((n) => Pt(this, n)),
      arguments
    );
  },
  find(e, t) {
    return Lt(
      this,
      "find",
      e,
      t,
      (s) => Pt(this, s),
      arguments
    );
  },
  findIndex(e, t) {
    return Lt(this, "findIndex", e, t, void 0, arguments);
  },
  findLast(e, t) {
    return Lt(
      this,
      "findLast",
      e,
      t,
      (s) => Pt(this, s),
      arguments
    );
  },
  findLastIndex(e, t) {
    return Lt(this, "findLastIndex", e, t, void 0, arguments);
  },
  // flat, flatMap could benefit from ARRAY_ITERATE but are not straight-forward to implement
  forEach(e, t) {
    return Lt(this, "forEach", e, t, void 0, arguments);
  },
  includes(...e) {
    return Lo(this, "includes", e);
  },
  indexOf(...e) {
    return Lo(this, "indexOf", e);
  },
  join(e) {
    return Ss(this).join(e);
  },
  // keys() iterator only reads `length`, no optimization required
  lastIndexOf(...e) {
    return Lo(this, "lastIndexOf", e);
  },
  map(e, t) {
    return Lt(this, "map", e, t, void 0, arguments);
  },
  pop() {
    return nn(this, "pop");
  },
  push(...e) {
    return nn(this, "push", e);
  },
  reduce(e, ...t) {
    return el(this, "reduce", e, t);
  },
  reduceRight(e, ...t) {
    return el(this, "reduceRight", e, t);
  },
  shift() {
    return nn(this, "shift");
  },
  // slice could use ARRAY_ITERATE but also seems to beg for range tracking
  some(e, t) {
    return Lt(this, "some", e, t, void 0, arguments);
  },
  splice(...e) {
    return nn(this, "splice", e);
  },
  toReversed() {
    return Ss(this).toReversed();
  },
  toSorted(e) {
    return Ss(this).toSorted(e);
  },
  toSpliced(...e) {
    return Ss(this).toSpliced(...e);
  },
  unshift(...e) {
    return nn(this, "unshift", e);
  },
  values() {
    return No(this, "values", (e) => Pt(this, e));
  }
};
function No(e, t, s) {
  const n = go(e), o = n[t]();
  return n !== e && !/* @__PURE__ */ gt(e) && (o._next = o.next, o.next = () => {
    const l = o._next();
    return l.done || (l.value = s(l.value)), l;
  }), o;
}
const fu = Array.prototype;
function Lt(e, t, s, n, o, l) {
  const i = go(e), a = i !== e && !/* @__PURE__ */ gt(e), u = i[t];
  if (u !== fu[t]) {
    const x = u.apply(e, l);
    return a ? _t(x) : x;
  }
  let h = s;
  i !== e && (a ? h = function(x, A) {
    return s.call(this, Pt(e, x), A, e);
  } : s.length > 2 && (h = function(x, A) {
    return s.call(this, x, A, e);
  }));
  const g = u.call(i, h, n);
  return a && o ? o(g) : g;
}
function el(e, t, s, n) {
  const o = go(e), l = o !== e && !/* @__PURE__ */ gt(e);
  let i = s, a = !1;
  o !== e && (l ? (a = n.length === 0, i = function(h, g, x) {
    return a && (a = !1, h = Pt(e, h)), s.call(this, h, Pt(e, g), x, e);
  }) : s.length > 3 && (i = function(h, g, x) {
    return s.call(this, h, g, x, e);
  }));
  const u = o[t](i, ...n);
  return a ? Pt(e, u) : u;
}
function Lo(e, t, s) {
  const n = /* @__PURE__ */ ve(e);
  et(n, "iterate", wn);
  const o = n[t](...s);
  return (o === -1 || o === !1) && /* @__PURE__ */ ho(s[0]) ? (s[0] = /* @__PURE__ */ ve(s[0]), n[t](...s)) : o;
}
function nn(e, t, s = []) {
  Vt(), dr();
  const n = (/* @__PURE__ */ ve(e))[t].apply(e, s);
  return cr(), $t(), n;
}
const pu = /* @__PURE__ */ ir("__proto__,__v_isRef,__isVue"), si = new Set(
  /* @__PURE__ */ Object.getOwnPropertyNames(Symbol).filter((e) => e !== "arguments" && e !== "caller").map((e) => Symbol[e]).filter(ht)
);
function mu(e) {
  ht(e) || (e = String(e));
  const t = /* @__PURE__ */ ve(this);
  return et(t, "has", e), t.hasOwnProperty(e);
}
class ni {
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
      return n === (o ? l ? Su : ii : l ? li : ri).get(t) || // receiver is not the reactive proxy, but has the same prototype
      // this means the receiver is a user proxy of the reactive proxy
      Object.getPrototypeOf(t) === Object.getPrototypeOf(n) ? t : void 0;
    const i = J(t);
    if (!o) {
      let u;
      if (i && (u = cu[s]))
        return u;
      if (s === "hasOwnProperty")
        return mu;
    }
    const a = Reflect.get(
      t,
      s,
      // if this is a proxy wrapping a ref, return methods using the raw ref
      // as receiver so that we don't have to call `toRaw` on the ref in all
      // its class methods
      /* @__PURE__ */ Re(t) ? t : n
    );
    if ((ht(s) ? si.has(s) : pu(s)) || (o || et(t, "get", s), l))
      return a;
    if (/* @__PURE__ */ Re(a)) {
      const u = i && uo(s) ? a : a.value;
      return o && _e(u) ? /* @__PURE__ */ Zo(u) : u;
    }
    return _e(a) ? o ? /* @__PURE__ */ Zo(a) : /* @__PURE__ */ Kt(a) : a;
  }
}
class oi extends ni {
  constructor(t = !1) {
    super(!1, t);
  }
  set(t, s, n, o) {
    let l = t[s];
    const i = J(t) && uo(s);
    if (!this._isShallow) {
      const h = /* @__PURE__ */ qt(l);
      if (!/* @__PURE__ */ gt(n) && !/* @__PURE__ */ qt(n) && (l = /* @__PURE__ */ ve(l), n = /* @__PURE__ */ ve(n)), !i && /* @__PURE__ */ Re(l) && !/* @__PURE__ */ Re(n))
        return h || (l.value = n), !0;
    }
    const a = i ? Number(s) < t.length : ye(t, s), u = Reflect.set(
      t,
      s,
      n,
      /* @__PURE__ */ Re(t) ? t : o
    );
    return t === /* @__PURE__ */ ve(o) && u && (a ? qe(n, l) && Ht(t, "set", s, n) : Ht(t, "add", s, n)), u;
  }
  deleteProperty(t, s) {
    const n = ye(t, s);
    t[s];
    const o = Reflect.deleteProperty(t, s);
    return o && n && Ht(t, "delete", s, void 0), o;
  }
  has(t, s) {
    const n = Reflect.has(t, s);
    return (!ht(s) || !si.has(s)) && et(t, "has", s), n;
  }
  ownKeys(t) {
    return et(
      t,
      "iterate",
      J(t) ? "length" : fs
    ), Reflect.ownKeys(t);
  }
}
class gu extends ni {
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
const hu = /* @__PURE__ */ new oi(), bu = /* @__PURE__ */ new gu(), vu = /* @__PURE__ */ new oi(!0);
const Qo = (e) => e, Bn = (e) => Reflect.getPrototypeOf(e);
function yu(e, t, s) {
  return function(...n) {
    const o = this.__v_raw, l = /* @__PURE__ */ ve(o), i = Is(l), a = e === "entries" || e === Symbol.iterator && i, u = e === "keys" && i, h = o[e](...n), g = s ? Qo : t ? Vs : _t;
    return !t && et(
      l,
      "iterate",
      u ? Yo : fs
    ), Ue(
      // inheriting all iterator properties
      Object.create(h),
      {
        // iterator protocol
        next() {
          const { value: x, done: A } = h.next();
          return A ? { value: x, done: A } : {
            value: a ? [g(x[0]), g(x[1])] : g(x),
            done: A
          };
        }
      }
    );
  };
}
function Fn(e) {
  return function(...t) {
    return e === "delete" ? !1 : e === "clear" ? void 0 : this;
  };
}
function xu(e, t) {
  const s = {
    get(o) {
      const l = this.__v_raw, i = /* @__PURE__ */ ve(l), a = /* @__PURE__ */ ve(o);
      e || (qe(o, a) && et(i, "get", o), et(i, "get", a));
      const { has: u } = Bn(i), h = t ? Qo : e ? Vs : _t;
      if (u.call(i, o))
        return h(l.get(o));
      if (u.call(i, a))
        return h(l.get(a));
      l !== i && l.get(o);
    },
    get size() {
      const o = this.__v_raw;
      return !e && et(/* @__PURE__ */ ve(o), "iterate", fs), o.size;
    },
    has(o) {
      const l = this.__v_raw, i = /* @__PURE__ */ ve(l), a = /* @__PURE__ */ ve(o);
      return e || (qe(o, a) && et(i, "has", o), et(i, "has", a)), o === a ? l.has(o) : l.has(o) || l.has(a);
    },
    forEach(o, l) {
      const i = this, a = i.__v_raw, u = /* @__PURE__ */ ve(a), h = t ? Qo : e ? Vs : _t;
      return !e && et(u, "iterate", fs), a.forEach((g, x) => o.call(l, h(g), h(x), i));
    }
  };
  return Ue(
    s,
    e ? {
      add: Fn("add"),
      set: Fn("set"),
      delete: Fn("delete"),
      clear: Fn("clear")
    } : {
      add(o) {
        const l = /* @__PURE__ */ ve(this), i = Bn(l), a = /* @__PURE__ */ ve(o), u = !t && !/* @__PURE__ */ gt(o) && !/* @__PURE__ */ qt(o) ? a : o;
        return i.has.call(l, u) || qe(o, u) && i.has.call(l, o) || qe(a, u) && i.has.call(l, a) || (l.add(u), Ht(l, "add", u, u)), this;
      },
      set(o, l) {
        !t && !/* @__PURE__ */ gt(l) && !/* @__PURE__ */ qt(l) && (l = /* @__PURE__ */ ve(l));
        const i = /* @__PURE__ */ ve(this), { has: a, get: u } = Bn(i);
        let h = a.call(i, o);
        h || (o = /* @__PURE__ */ ve(o), h = a.call(i, o));
        const g = u.call(i, o);
        return i.set(o, l), h ? qe(l, g) && Ht(i, "set", o, l) : Ht(i, "add", o, l), this;
      },
      delete(o) {
        const l = /* @__PURE__ */ ve(this), { has: i, get: a } = Bn(l);
        let u = i.call(l, o);
        u || (o = /* @__PURE__ */ ve(o), u = i.call(l, o)), a && a.call(l, o);
        const h = l.delete(o);
        return u && Ht(l, "delete", o, void 0), h;
      },
      clear() {
        const o = /* @__PURE__ */ ve(this), l = o.size !== 0, i = o.clear();
        return l && Ht(
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
    s[o] = yu(o, e, t);
  }), s;
}
function pr(e, t) {
  const s = xu(e, t);
  return (n, o, l) => o === "__v_isReactive" ? !e : o === "__v_isReadonly" ? e : o === "__v_raw" ? n : Reflect.get(
    ye(s, o) && o in n ? s : n,
    o,
    l
  );
}
const _u = {
  get: /* @__PURE__ */ pr(!1, !1)
}, wu = {
  get: /* @__PURE__ */ pr(!1, !0)
}, ku = {
  get: /* @__PURE__ */ pr(!0, !1)
};
const ri = /* @__PURE__ */ new WeakMap(), li = /* @__PURE__ */ new WeakMap(), ii = /* @__PURE__ */ new WeakMap(), Su = /* @__PURE__ */ new WeakMap();
function Cu(e) {
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
function Kt(e) {
  return /* @__PURE__ */ qt(e) ? e : mr(
    e,
    !1,
    hu,
    _u,
    ri
  );
}
// @__NO_SIDE_EFFECTS__
function Au(e) {
  return mr(
    e,
    !1,
    vu,
    wu,
    li
  );
}
// @__NO_SIDE_EFFECTS__
function Zo(e) {
  return mr(
    e,
    !0,
    bu,
    ku,
    ii
  );
}
function mr(e, t, s, n, o) {
  if (!_e(e) || e.__v_raw && !(t && e.__v_isReactive) || e.__v_skip || !Object.isExtensible(e))
    return e;
  const l = o.get(e);
  if (l)
    return l;
  const i = Cu(Ya(e));
  if (i === 0)
    return e;
  const a = new Proxy(
    e,
    i === 2 ? n : s
  );
  return o.set(e, a), a;
}
// @__NO_SIDE_EFFECTS__
function ps(e) {
  return /* @__PURE__ */ qt(e) ? /* @__PURE__ */ ps(e.__v_raw) : !!(e && e.__v_isReactive);
}
// @__NO_SIDE_EFFECTS__
function qt(e) {
  return !!(e && e.__v_isReadonly);
}
// @__NO_SIDE_EFFECTS__
function gt(e) {
  return !!(e && e.__v_isShallow);
}
// @__NO_SIDE_EFFECTS__
function ho(e) {
  return e ? !!e.__v_raw : !1;
}
// @__NO_SIDE_EFFECTS__
function ve(e) {
  const t = e && e.__v_raw;
  return t ? /* @__PURE__ */ ve(t) : e;
}
function Eu(e) {
  return !ye(e, "__v_skip") && Object.isExtensible(e) && zl(e, "__v_skip", !0), e;
}
const _t = (e) => _e(e) ? /* @__PURE__ */ Kt(e) : e, Vs = (e) => _e(e) ? /* @__PURE__ */ Zo(e) : e;
// @__NO_SIDE_EFFECTS__
function Re(e) {
  return e ? e.__v_isRef === !0 : !1;
}
// @__NO_SIDE_EFFECTS__
function L(e) {
  return Iu(e, !1);
}
function Iu(e, t) {
  return /* @__PURE__ */ Re(e) ? e : new Tu(e, t);
}
class Tu {
  constructor(t, s) {
    this.dep = new mo(), this.__v_isRef = !0, this.__v_isShallow = !1, this._rawValue = s ? t : /* @__PURE__ */ ve(t), this._value = s ? t : _t(t), this.__v_isShallow = s;
  }
  get value() {
    return this.dep.track(), this._value;
  }
  set value(t) {
    const s = this._rawValue, n = this.__v_isShallow || /* @__PURE__ */ gt(t) || /* @__PURE__ */ qt(t);
    t = n ? t : /* @__PURE__ */ ve(t), qe(t, s) && (this._rawValue = t, this._value = n ? t : _t(t), this.dep.trigger());
  }
}
function Pu(e) {
  e.dep && e.dep.trigger();
}
function p(e) {
  return /* @__PURE__ */ Re(e) ? e.value : e;
}
function ai(e) {
  return X(e) ? e() : p(e);
}
const Ru = {
  get: (e, t, s) => t === "__v_raw" ? e : p(Reflect.get(e, t, s)),
  set: (e, t, s, n) => {
    const o = e[t];
    return /* @__PURE__ */ Re(o) && !/* @__PURE__ */ Re(s) ? (o.value = s, !0) : Reflect.set(e, t, s, n);
  }
};
function ui(e) {
  return /* @__PURE__ */ ps(e) ? e : new Proxy(e, Ru);
}
class Mu {
  constructor(t) {
    this.__v_isRef = !0, this._value = void 0;
    const s = this.dep = new mo(), { get: n, set: o } = t(s.track.bind(s), s.trigger.bind(s));
    this._get = n, this._set = o;
  }
  get value() {
    return this._value = this._get();
  }
  set value(t) {
    this._set(t);
  }
}
function Vu(e) {
  return new Mu(e);
}
// @__NO_SIDE_EFFECTS__
function $u(e) {
  const t = J(e) ? new Array(e.length) : {};
  for (const s in e)
    t[s] = di(e, s);
  return t;
}
class Ou {
  constructor(t, s, n) {
    this._object = t, this._defaultValue = n, this.__v_isRef = !0, this._value = void 0, this._key = ht(s) ? s : String(s), this._raw = /* @__PURE__ */ ve(t);
    let o = !0, l = t;
    if (!J(t) || ht(this._key) || !uo(this._key))
      do
        o = !/* @__PURE__ */ ho(l) || /* @__PURE__ */ gt(l);
      while (o && (l = l.__v_raw));
    this._shallow = o;
  }
  get value() {
    let t = this._object[this._key];
    return this._shallow && (t = p(t)), this._value = t === void 0 ? this._defaultValue : t;
  }
  set value(t) {
    if (this._shallow && /* @__PURE__ */ Re(this._raw[this._key])) {
      const s = this._object[this._key];
      if (/* @__PURE__ */ Re(s)) {
        s.value = t;
        return;
      }
    }
    this._object[this._key] = t;
  }
  get dep() {
    return du(this._raw, this._key);
  }
}
class ju {
  constructor(t) {
    this._getter = t, this.__v_isRef = !0, this.__v_isReadonly = !0, this._value = void 0;
  }
  get value() {
    return this._value = this._getter();
  }
}
// @__NO_SIDE_EFFECTS__
function Nu(e, t, s) {
  return /* @__PURE__ */ Re(e) ? e : X(e) ? new ju(e) : _e(e) && arguments.length > 1 ? di(e, t, s) : /* @__PURE__ */ L(e);
}
function di(e, t, s) {
  return new Ou(e, t, s);
}
class Lu {
  constructor(t, s, n) {
    this.fn = t, this.setter = s, this._value = void 0, this.dep = new mo(this), this.__v_isRef = !0, this.deps = void 0, this.depsTail = void 0, this.flags = 16, this.globalVersion = _n - 1, this.next = void 0, this.effect = this, this.__v_isReadonly = !s, this.isSSR = n;
  }
  /**
   * @internal
   */
  notify() {
    if (this.flags |= 16, !(this.flags & 8) && // avoid infinite self recursion
    Se !== this)
      return Yl(this, !0), !0;
  }
  get value() {
    const t = this.dep.track();
    return Xl(this), t && (t.version = this.dep.version), this._value;
  }
  set value(t) {
    this.setter && this.setter(t);
  }
}
// @__NO_SIDE_EFFECTS__
function Uu(e, t, s = !1) {
  let n, o;
  return X(e) ? n = e : (n = e.get, o = e.set), new Lu(n, o, s);
}
const Hn = {}, Zn = /* @__PURE__ */ new WeakMap();
let cs;
function Du(e, t = !1, s = cs) {
  if (s) {
    let n = Zn.get(s);
    n || Zn.set(s, n = []), n.push(e);
  }
}
function Bu(e, t, s = ge) {
  const { immediate: n, deep: o, once: l, scheduler: i, augmentJob: a, call: u } = s, h = (U) => o ? U : /* @__PURE__ */ gt(U) || o === !1 || o === 0 ? zt(U, 1) : zt(U);
  let g, x, A, k, $ = !1, v = !1;
  if (/* @__PURE__ */ Re(e) ? (x = () => e.value, $ = /* @__PURE__ */ gt(e)) : /* @__PURE__ */ ps(e) ? (x = () => h(e), $ = !0) : J(e) ? (v = !0, $ = e.some((U) => /* @__PURE__ */ ps(U) || /* @__PURE__ */ gt(U)), x = () => e.map((U) => {
    if (/* @__PURE__ */ Re(U))
      return U.value;
    if (/* @__PURE__ */ ps(U))
      return h(U);
    if (X(U))
      return u ? u(U, 2) : U();
  })) : X(e) ? t ? x = u ? () => u(e, 2) : e : x = () => {
    if (A) {
      Vt();
      try {
        A();
      } finally {
        $t();
      }
    }
    const U = cs;
    cs = g;
    try {
      return u ? u(e, 3, [k]) : e(k);
    } finally {
      cs = U;
    }
  } : x = Mt, t && o) {
    const U = x, Z = o === !0 ? 1 / 0 : o;
    x = () => zt(U(), Z);
  }
  const H = iu(), z = () => {
    g.stop(), H && H.active && ar(H.effects, g);
  };
  if (l && t) {
    const U = t;
    t = (...Z) => {
      const $e = U(...Z);
      return z(), $e;
    };
  }
  let D = v ? new Array(e.length).fill(Hn) : Hn;
  const q = (U) => {
    if (!(!(g.flags & 1) || !g.dirty && !U))
      if (t) {
        const Z = g.run();
        if (U || o || $ || (v ? Z.some(($e, K) => qe($e, D[K])) : qe(Z, D))) {
          A && A();
          const $e = cs;
          cs = g;
          try {
            const K = [
              Z,
              // pass undefined as the old value when it's changed for the first time
              D === Hn ? void 0 : v && D[0] === Hn ? [] : D,
              k
            ];
            D = Z, u ? u(t, 3, K) : (
              // @ts-expect-error
              t(...K)
            );
          } finally {
            cs = $e;
          }
        }
      } else
        g.run();
  };
  return a && a(q), g = new Gl(x), g.scheduler = i ? () => i(q, !1) : q, k = (U) => Du(U, !1, g), A = g.onStop = () => {
    const U = Zn.get(g);
    if (U) {
      if (u)
        u(U, 4);
      else
        for (const Z of U) Z();
      Zn.delete(g);
    }
  }, t ? n ? q(!0) : D = g.run() : i ? i(q.bind(null, !0), !0) : g.run(), z.pause = g.pause.bind(g), z.resume = g.resume.bind(g), z.stop = z, z;
}
function zt(e, t = 1 / 0, s) {
  if (t <= 0 || !_e(e) || e.__v_skip || (s = s || /* @__PURE__ */ new Map(), (s.get(e) || 0) >= t))
    return e;
  if (s.set(e, t), t--, /* @__PURE__ */ Re(e))
    zt(e.value, t, s);
  else if (J(e))
    for (let n = 0; n < e.length; n++)
      zt(e[n], t, s);
  else if (js(e) || Is(e))
    e.forEach((n) => {
      zt(n, t, s);
    });
  else if (ao(e)) {
    for (const n in e)
      zt(e[n], t, s);
    for (const n of Object.getOwnPropertySymbols(e))
      Object.prototype.propertyIsEnumerable.call(e, n) && zt(e[n], t, s);
  }
  return e;
}
/**
* @vue/runtime-core v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
function En(e, t, s, n) {
  try {
    return n ? e(...n) : e();
  } catch (o) {
    In(o, t, s);
  }
}
function wt(e, t, s, n) {
  if (X(e)) {
    const o = En(e, t, s, n);
    return o && Bl(o) && o.catch((l) => {
      In(l, t, s);
    }), o;
  }
  if (J(e)) {
    const o = [];
    for (let l = 0; l < e.length; l++)
      o.push(wt(e[l], t, s, n));
    return o;
  }
}
function In(e, t, s, n = !0) {
  const o = t ? t.vnode : null, { errorHandler: l, throwUnhandledErrorInProduction: i } = t && t.appContext.config || ge;
  if (t) {
    let a = t.parent;
    const u = t.proxy, h = `https://vuejs.org/error-reference/#runtime-${s}`;
    for (; a; ) {
      const g = a.ec;
      if (g) {
        for (let x = 0; x < g.length; x++)
          if (g[x](e, u, h) === !1)
            return;
      }
      a = a.parent;
    }
    if (l) {
      Vt(), En(l, null, 10, [
        e,
        u,
        h
      ]), $t();
      return;
    }
  }
  Fu(e, s, o, n, i);
}
function Fu(e, t, s, n = !0, o = !1) {
  if (o)
    throw e;
  console.error(e);
}
const it = [];
let Tt = -1;
const Ts = [];
let Xt = null, As = 0;
const ci = /* @__PURE__ */ Promise.resolve();
let Xn = null;
function Tn(e) {
  const t = Xn || ci;
  return e ? t.then(this ? e.bind(this) : e) : t;
}
function Hu(e) {
  let t = Tt + 1, s = it.length;
  for (; t < s; ) {
    const n = t + s >>> 1, o = it[n], l = kn(o);
    l < e || l === e && o.flags & 2 ? t = n + 1 : s = n;
  }
  return t;
}
function gr(e) {
  if (!(e.flags & 1)) {
    const t = kn(e), s = it[it.length - 1];
    !s || // fast path when the job id is larger than the tail
    !(e.flags & 2) && t >= kn(s) ? it.push(e) : it.splice(Hu(t), 0, e), e.flags |= 1, fi();
  }
}
function fi() {
  Xn || (Xn = ci.then(mi));
}
function zu(e) {
  J(e) ? Ts.push(...e) : Xt && e.id === -1 ? Xt.splice(As + 1, 0, e) : e.flags & 1 || (Ts.push(e), e.flags |= 1), fi();
}
function tl(e, t, s = Tt + 1) {
  for (; s < it.length; s++) {
    const n = it[s];
    if (n && n.flags & 2) {
      if (e && n.id !== e.uid)
        continue;
      it.splice(s, 1), s--, n.flags & 4 && (n.flags &= -2), n(), n.flags & 4 || (n.flags &= -2);
    }
  }
}
function pi(e) {
  if (Ts.length) {
    const t = [...new Set(Ts)].sort(
      (s, n) => kn(s) - kn(n)
    );
    if (Ts.length = 0, Xt) {
      Xt.push(...t);
      return;
    }
    for (Xt = t, As = 0; As < Xt.length; As++) {
      const s = Xt[As];
      s.flags & 4 && (s.flags &= -2), s.flags & 8 || s(), s.flags &= -2;
    }
    Xt = null, As = 0;
  }
}
const kn = (e) => e.id == null ? e.flags & 2 ? -1 : 1 / 0 : e.id;
function mi(e) {
  try {
    for (Tt = 0; Tt < it.length; Tt++) {
      const t = it[Tt];
      t && !(t.flags & 8) && (t.flags & 4 && (t.flags &= -2), En(
        t,
        t.i,
        t.i ? 15 : 14
      ), t.flags & 4 || (t.flags &= -2));
    }
  } finally {
    for (; Tt < it.length; Tt++) {
      const t = it[Tt];
      t && (t.flags &= -2);
    }
    Tt = -1, it.length = 0, pi(), Xn = null, (it.length || Ts.length) && mi();
  }
}
let st = null, gi = null;
function eo(e) {
  const t = st;
  return st = e, gi = e && e.type.__scopeId || null, t;
}
function S(e, t = st, s) {
  if (!t || e._n)
    return e;
  const n = (...o) => {
    n._d && no(-1);
    const l = eo(t);
    let i;
    try {
      i = e(...o);
    } finally {
      eo(l), n._d && no(1);
    }
    return i;
  };
  return n._n = !0, n._c = !0, n._d = !0, n;
}
function hr(e, t) {
  if (st === null)
    return e;
  const s = xo(st), n = e.dirs || (e.dirs = []);
  for (let o = 0; o < t.length; o++) {
    let [l, i, a, u = ge] = t[o];
    l && (X(l) && (l = {
      mounted: l,
      updated: l
    }), l.deep && zt(i), n.push({
      dir: l,
      instance: s,
      value: i,
      oldValue: void 0,
      arg: a,
      modifiers: u
    }));
  }
  return e;
}
function as(e, t, s, n) {
  const o = e.dirs, l = t && t.dirs;
  for (let i = 0; i < o.length; i++) {
    const a = o[i];
    l && (a.oldValue = l[i].value);
    let u = a.dir[n];
    u && (Vt(), wt(u, s, 8, [
      e.el,
      a,
      e,
      t
    ]), $t());
  }
}
function hi(e, t) {
  if (tt) {
    let s = tt.provides;
    const n = tt.parent && tt.parent.provides;
    n === s && (s = tt.provides = Object.create(n)), s[e] = t;
  }
}
function hn(e, t, s = !1) {
  const n = os();
  if (n || Rs) {
    let o = Rs ? Rs._context.provides : n ? n.parent == null || n.ce ? n.vnode.appContext && n.vnode.appContext.provides : n.parent.provides : void 0;
    if (o && e in o)
      return o[e];
    if (arguments.length > 1)
      return s && X(t) ? t.call(n && n.proxy) : t;
  }
}
const Wu = /* @__PURE__ */ Symbol.for("v-scx"), Ku = () => hn(Wu);
function qu(e, t) {
  return br(
    e,
    null,
    { flush: "sync" }
  );
}
function vt(e, t, s) {
  return br(e, t, s);
}
function br(e, t, s = ge) {
  const { immediate: n, deep: o, flush: l, once: i } = s, a = Ue({}, s), u = t && n || !t && l !== "post";
  let h;
  if ($s) {
    if (l === "sync") {
      const k = Ku();
      h = k.__watcherHandles || (k.__watcherHandles = []);
    } else if (!u) {
      const k = () => {
      };
      return k.stop = Mt, k.resume = Mt, k.pause = Mt, k;
    }
  }
  const g = tt;
  a.call = (k, $, v) => wt(k, g, $, v);
  let x = !1;
  l === "post" ? a.scheduler = (k) => {
    dt(k, g && g.suspense);
  } : l !== "sync" && (x = !0, a.scheduler = (k, $) => {
    $ ? k() : gr(k);
  }), a.augmentJob = (k) => {
    t && (k.flags |= 4), x && (k.flags |= 2, g && (k.id = g.uid, k.i = g));
  };
  const A = Bu(e, t, a);
  return $s && (h ? h.push(A) : u && A()), A;
}
function Gu(e, t, s) {
  const n = this.proxy, o = Ve(e) ? e.includes(".") ? bi(n, e) : () => n[e] : e.bind(n, n);
  let l;
  X(t) ? l = t : (l = t.handler, s = t);
  const i = Pn(this), a = br(o, l.bind(n), s);
  return i(), a;
}
function bi(e, t) {
  const s = t.split(".");
  return () => {
    let n = e;
    for (let o = 0; o < s.length && n; o++)
      n = n[s[o]];
    return n;
  };
}
const Ju = /* @__PURE__ */ Symbol("_vte"), Yu = (e) => e.__isTeleport, Uo = /* @__PURE__ */ Symbol("_leaveCb");
function vr(e, t) {
  e.shapeFlag & 6 && e.component ? (e.transition = t, vr(e.component.subTree, t)) : e.shapeFlag & 128 ? (e.ssContent.transition = t.clone(e.ssContent), e.ssFallback.transition = t.clone(e.ssFallback)) : e.transition = t;
}
// @__NO_SIDE_EFFECTS__
function He(e, t) {
  return X(e) ? (
    // #8236: extend call and options.name access are considered side-effects
    // by Rollup, so we have to wrap it in a pure-annotated IIFE.
    Ue({ name: e.name }, t, { setup: e })
  ) : e;
}
function yr(e) {
  e.ids = [e.ids[0] + e.ids[2]++ + "-", 0, 0];
}
function sl(e, t) {
  let s;
  return !!((s = Object.getOwnPropertyDescriptor(e, t)) && !s.configurable);
}
const to = /* @__PURE__ */ new WeakMap();
function bn(e, t, s, n, o = !1) {
  if (J(e)) {
    e.forEach(
      (v, H) => bn(
        v,
        t && (J(t) ? t[H] : t),
        s,
        n,
        o
      )
    );
    return;
  }
  if (Ps(n) && !o) {
    n.shapeFlag & 512 && n.type.__asyncResolved && n.component.subTree.component && bn(e, t, s, n.component.subTree);
    return;
  }
  const l = n.shapeFlag & 4 ? xo(n.component) : n.el, i = o ? null : l, { i: a, r: u } = e, h = t && t.r, g = a.refs === ge ? a.refs = {} : a.refs, x = a.setupState, A = /* @__PURE__ */ ve(x), k = x === ge ? Dl : (v) => sl(g, v) ? !1 : ye(A, v), $ = (v, H) => !(H && sl(g, H));
  if (h != null && h !== u) {
    if (nl(t), Ve(h))
      g[h] = null, k(h) && (x[h] = null);
    else if (/* @__PURE__ */ Re(h)) {
      const v = t;
      $(h, v.k) && (h.value = null), v.k && (g[v.k] = null);
    }
  }
  if (X(u)) {
    Vt();
    try {
      En(u, a, 12, [i, g]);
    } finally {
      $t();
    }
  } else {
    const v = Ve(u), H = /* @__PURE__ */ Re(u);
    if (v || H) {
      const z = () => {
        if (e.f) {
          const D = v ? k(u) ? x[u] : g[u] : $() || !e.k ? u.value : g[e.k];
          if (o)
            J(D) && ar(D, l);
          else if (J(D))
            D.includes(l) || D.push(l);
          else if (v)
            g[u] = [l], k(u) && (x[u] = g[u]);
          else {
            const q = [l];
            $(u, e.k) && (u.value = q), e.k && (g[e.k] = q);
          }
        } else v ? (g[u] = i, k(u) && (x[u] = i)) : H && ($(u, e.k) && (u.value = i), e.k && (g[e.k] = i));
      };
      if (i) {
        const D = () => {
          z(), to.delete(e);
        };
        D.id = -1, to.set(e, D), dt(D, s);
      } else
        nl(e), z();
    }
  }
}
function nl(e) {
  const t = to.get(e);
  t && (t.flags |= 8, to.delete(e));
}
const ol = (e) => e.nodeType === 8;
po().requestIdleCallback;
po().cancelIdleCallback;
function Qu(e, t) {
  if (ol(e) && e.data === "[") {
    let s = 1, n = e.nextSibling;
    for (; n; ) {
      if (n.nodeType === 1) {
        if (t(n) === !1)
          break;
      } else if (ol(n))
        if (n.data === "]") {
          if (--s === 0) break;
        } else n.data === "[" && s++;
      n = n.nextSibling;
    }
  } else
    t(e);
}
const Ps = (e) => !!e.type.__asyncLoader;
// @__NO_SIDE_EFFECTS__
function Zu(e) {
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
    onError: u
  } = e;
  let h = null, g, x = 0;
  const A = () => (x++, h = null, k()), k = () => {
    let $;
    return h || ($ = h = t().catch((v) => {
      if (v = v instanceof Error ? v : new Error(String(v)), u)
        return new Promise((H, z) => {
          u(v, () => H(A()), () => z(v), x + 1);
        });
      throw v;
    }).then((v) => $ !== h && h ? h : (v && (v.__esModule || v[Symbol.toStringTag] === "Module") && (v = v.default), g = v, v)));
  };
  return /* @__PURE__ */ He({
    name: "AsyncComponentWrapper",
    __asyncLoader: k,
    __asyncHydrate($, v, H) {
      let z = !1;
      (v.bu || (v.bu = [])).push(() => z = !0);
      const D = () => {
        z || H();
      }, q = l ? () => {
        const U = l(
          D,
          (Z) => Qu($, Z)
        );
        U && (v.bum || (v.bum = [])).push(U);
      } : D;
      g ? q() : k().then(() => !v.isUnmounted && q());
    },
    get __asyncResolved() {
      return g;
    },
    setup() {
      const $ = tt;
      if (yr($), g)
        return () => zn(g, $);
      const v = (Z) => {
        h = null, In(
          Z,
          $,
          13,
          !n
        );
      };
      if (a && $.suspense || $s)
        return k().then((Z) => () => zn(Z, $)).catch((Z) => (v(Z), () => n ? y(n, {
          error: Z
        }) : null));
      const H = /* @__PURE__ */ L(!1), z = /* @__PURE__ */ L(), D = /* @__PURE__ */ L(!!o);
      let q, U;
      return _r(() => {
        q != null && clearTimeout(q), U != null && clearTimeout(U);
      }), o && (U = setTimeout(() => {
        $.isUnmounted || (D.value = !1);
      }, o)), i != null && (q = setTimeout(() => {
        if (!$.isUnmounted && !H.value && !z.value) {
          const Z = new Error(
            `Async component timed out after ${i}ms.`
          );
          v(Z), z.value = Z;
        }
      }, i)), k().then(() => {
        $.isUnmounted || (H.value = !0, $.parent && xr($.parent.vnode) && $.parent.update());
      }).catch((Z) => {
        if ($.isUnmounted) {
          h = null;
          return;
        }
        v(Z), z.value = Z;
      }), () => {
        if (H.value && g)
          return zn(g, $);
        if (z.value && n)
          return y(n, {
            error: z.value
          });
        if (s && !D.value)
          return zn(
            s,
            $
          );
      };
    }
  });
}
function zn(e, t) {
  const { ref: s, props: n, children: o, ce: l } = t.vnode, i = y(e, n, o);
  return i.ref = s, i.ce = l, delete t.vnode.ce, i;
}
const xr = (e) => e.type.__isKeepAlive;
function Xu(e, t) {
  vi(e, "a", t);
}
function ed(e, t) {
  vi(e, "da", t);
}
function vi(e, t, s = tt) {
  const n = e.__wdc || (e.__wdc = () => {
    let o = s;
    for (; o; ) {
      if (o.isDeactivated)
        return;
      o = o.parent;
    }
    return e();
  });
  if (bo(t, n, s), s) {
    let o = s.parent;
    for (; o && o.parent; )
      xr(o.parent.vnode) && td(n, t, s, o), o = o.parent;
  }
}
function td(e, t, s, n) {
  const o = bo(
    t,
    e,
    n,
    !0
    /* prepend */
  );
  _r(() => {
    ar(n[t], o);
  }, s);
}
function bo(e, t, s = tt, n = !1) {
  if (s) {
    const o = s[e] || (s[e] = []), l = t.__weh || (t.__weh = (...i) => {
      Vt();
      const a = Pn(s), u = wt(t, s, e, i);
      return a(), $t(), u;
    });
    return n ? o.unshift(l) : o.push(l), l;
  }
}
const Gt = (e) => (t, s = tt) => {
  (!$s || e === "sp") && bo(e, (...n) => t(...n), s);
}, sd = Gt("bm"), yi = Gt("m"), nd = Gt(
  "bu"
), xi = Gt("u"), _i = Gt(
  "bum"
), _r = Gt("um"), od = Gt(
  "sp"
), rd = Gt("rtg"), ld = Gt("rtc");
function id(e, t = tt) {
  bo("ec", e, t);
}
const ad = /* @__PURE__ */ Symbol.for("v-ndc");
function Xe(e, t, s, n) {
  let o;
  const l = s, i = J(e);
  if (i || Ve(e)) {
    const a = i && /* @__PURE__ */ ps(e);
    let u = !1, h = !1;
    a && (u = !/* @__PURE__ */ gt(e), h = /* @__PURE__ */ qt(e), e = go(e)), o = new Array(e.length);
    for (let g = 0, x = e.length; g < x; g++)
      o[g] = t(
        u ? h ? Vs(_t(e[g])) : _t(e[g]) : e[g],
        g,
        void 0,
        l
      );
  } else if (typeof e == "number") {
    o = new Array(e);
    for (let a = 0; a < e; a++)
      o[a] = t(a + 1, a, void 0, l);
  } else if (_e(e))
    if (e[Symbol.iterator])
      o = Array.from(
        e,
        (a, u) => t(a, u, void 0, l)
      );
    else {
      const a = Object.keys(e);
      o = new Array(a.length);
      for (let u = 0, h = a.length; u < h; u++) {
        const g = a[u];
        o[u] = t(e[g], g, u, l);
      }
    }
  else
    o = [];
  return o;
}
function ns(e, t, s = {}, n, o) {
  if (st.ce || st.parent && Ps(st.parent) && st.parent.ce) {
    const h = Object.keys(s).length > 0;
    return C(), Te(
      ce,
      null,
      [y("slot", s, n)],
      h ? -2 : 64
    );
  }
  let l = e[t];
  l && l._c && (l._d = !1), C();
  const i = l && wi(l(s)), a = s.key || // slot content array of a dynamic conditional slot may have a branch
  // key attached in the `createSlots` helper, respect that
  i && i.key, u = Te(
    ce,
    {
      key: (a && !ht(a) ? a : `_${t}`) + // #7256 force differentiate fallback content from actual content
      (!i && n ? "_fb" : "")
    },
    i || [],
    i && e._ === 1 ? 64 : -2
  );
  return u.scopeId && (u.slotScopeIds = [u.scopeId + "-s"]), l && l._c && (l._d = !0), u;
}
function wi(e) {
  return e.some((t) => Cn(t) ? !(t.type === Ot || t.type === ce && !wi(t.children)) : !0) ? e : null;
}
const Xo = (e) => e ? Hi(e) ? xo(e) : Xo(e.parent) : null, vn = (
  // Move PURE marker to new line to workaround compiler discarding it
  // due to type annotation
  /* @__PURE__ */ Ue(/* @__PURE__ */ Object.create(null), {
    $: (e) => e,
    $el: (e) => e.vnode.el,
    $data: (e) => e.data,
    $props: (e) => e.props,
    $attrs: (e) => e.attrs,
    $slots: (e) => e.slots,
    $refs: (e) => e.refs,
    $parent: (e) => Xo(e.parent),
    $root: (e) => Xo(e.root),
    $host: (e) => e.ce,
    $emit: (e) => e.emit,
    $options: (e) => Si(e),
    $forceUpdate: (e) => e.f || (e.f = () => {
      gr(e.update);
    }),
    $nextTick: (e) => e.n || (e.n = Tn.bind(e.proxy)),
    $watch: (e) => Gu.bind(e)
  })
), Do = (e, t) => e !== ge && !e.__isScriptSetup && ye(e, t), ud = {
  get({ _: e }, t) {
    if (t === "__v_skip")
      return !0;
    const { ctx: s, setupState: n, data: o, props: l, accessCache: i, type: a, appContext: u } = e;
    if (t[0] !== "$") {
      const A = i[t];
      if (A !== void 0)
        switch (A) {
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
        if (Do(n, t))
          return i[t] = 1, n[t];
        if (o !== ge && ye(o, t))
          return i[t] = 2, o[t];
        if (ye(l, t))
          return i[t] = 3, l[t];
        if (s !== ge && ye(s, t))
          return i[t] = 4, s[t];
        er && (i[t] = 0);
      }
    }
    const h = vn[t];
    let g, x;
    if (h)
      return t === "$attrs" && et(e.attrs, "get", ""), h(e);
    if (
      // css module (injected by vue-loader)
      (g = a.__cssModules) && (g = g[t])
    )
      return g;
    if (s !== ge && ye(s, t))
      return i[t] = 4, s[t];
    if (
      // global properties
      x = u.config.globalProperties, ye(x, t)
    )
      return x[t];
  },
  set({ _: e }, t, s) {
    const { data: n, setupState: o, ctx: l } = e;
    return Do(o, t) ? (o[t] = s, !0) : n !== ge && ye(n, t) ? (n[t] = s, !0) : ye(e.props, t) || t[0] === "$" && t.slice(1) in e ? !1 : (l[t] = s, !0);
  },
  has({
    _: { data: e, setupState: t, accessCache: s, ctx: n, appContext: o, props: l, type: i }
  }, a) {
    let u;
    return !!(s[a] || e !== ge && a[0] !== "$" && ye(e, a) || Do(t, a) || ye(l, a) || ye(n, a) || ye(vn, a) || ye(o.config.globalProperties, a) || (u = i.__cssModules) && u[a]);
  },
  defineProperty(e, t, s) {
    return s.get != null ? e._.accessCache[t] = 0 : ye(s, "value") && this.set(e, t, s.value, null), Reflect.defineProperty(e, t, s);
  }
};
function rl(e) {
  return J(e) ? e.reduce(
    (t, s) => (t[s] = null, t),
    {}
  ) : e;
}
let er = !0;
function dd(e) {
  const t = Si(e), s = e.proxy, n = e.ctx;
  er = !1, t.beforeCreate && ll(t.beforeCreate, e, "bc");
  const {
    // state
    data: o,
    computed: l,
    methods: i,
    watch: a,
    provide: u,
    inject: h,
    // lifecycle
    created: g,
    beforeMount: x,
    mounted: A,
    beforeUpdate: k,
    updated: $,
    activated: v,
    deactivated: H,
    beforeDestroy: z,
    beforeUnmount: D,
    destroyed: q,
    unmounted: U,
    render: Z,
    renderTracked: $e,
    renderTriggered: K,
    errorCaptured: te,
    serverPrefetch: Oe,
    // public API
    expose: we,
    inheritAttrs: Me,
    // assets
    components: ae,
    directives: he,
    filters: Je
  } = t;
  if (h && cd(h, n, null), i)
    for (const fe in i) {
      const ne = i[fe];
      X(ne) && (n[fe] = ne.bind(s));
    }
  if (o) {
    const fe = o.call(s, s);
    _e(fe) && (e.data = /* @__PURE__ */ Kt(fe));
  }
  if (er = !0, l)
    for (const fe in l) {
      const ne = l[fe], Ae = X(ne) ? ne.bind(s, s) : X(ne.get) ? ne.get.bind(s, s) : Mt, Ye = !X(ne) && X(ne.set) ? ne.set.bind(s) : Mt, je = xe({
        get: Ae,
        set: Ye
      });
      Object.defineProperty(n, fe, {
        enumerable: !0,
        configurable: !0,
        get: () => je.value,
        set: (De) => je.value = De
      });
    }
  if (a)
    for (const fe in a)
      ki(a[fe], n, s, fe);
  if (u) {
    const fe = X(u) ? u.call(s) : u;
    Reflect.ownKeys(fe).forEach((ne) => {
      hi(ne, fe[ne]);
    });
  }
  g && ll(g, e, "c");
  function Ce(fe, ne) {
    J(ne) ? ne.forEach((Ae) => fe(Ae.bind(s))) : ne && fe(ne.bind(s));
  }
  if (Ce(sd, x), Ce(yi, A), Ce(nd, k), Ce(xi, $), Ce(Xu, v), Ce(ed, H), Ce(id, te), Ce(ld, $e), Ce(rd, K), Ce(_i, D), Ce(_r, U), Ce(od, Oe), J(we))
    if (we.length) {
      const fe = e.exposed || (e.exposed = {});
      we.forEach((ne) => {
        Object.defineProperty(fe, ne, {
          get: () => s[ne],
          set: (Ae) => s[ne] = Ae,
          enumerable: !0
        });
      });
    } else e.exposed || (e.exposed = {});
  Z && e.render === Mt && (e.render = Z), Me != null && (e.inheritAttrs = Me), ae && (e.components = ae), he && (e.directives = he), Oe && yr(e);
}
function cd(e, t, s = Mt) {
  J(e) && (e = tr(e));
  for (const n in e) {
    const o = e[n];
    let l;
    _e(o) ? "default" in o ? l = hn(
      o.from || n,
      o.default,
      !0
    ) : l = hn(o.from || n) : l = hn(o), /* @__PURE__ */ Re(l) ? Object.defineProperty(t, n, {
      enumerable: !0,
      configurable: !0,
      get: () => l.value,
      set: (i) => l.value = i
    }) : t[n] = l;
  }
}
function ll(e, t, s) {
  wt(
    J(e) ? e.map((n) => n.bind(t.proxy)) : e.bind(t.proxy),
    t,
    s
  );
}
function ki(e, t, s, n) {
  let o = n.includes(".") ? bi(s, n) : () => s[n];
  if (Ve(e)) {
    const l = t[e];
    X(l) && vt(o, l);
  } else if (X(e))
    vt(o, e.bind(s));
  else if (_e(e))
    if (J(e))
      e.forEach((l) => ki(l, t, s, n));
    else {
      const l = X(e.handler) ? e.handler.bind(s) : t[e.handler];
      X(l) && vt(o, l, e);
    }
}
function Si(e) {
  const t = e.type, { mixins: s, extends: n } = t, {
    mixins: o,
    optionsCache: l,
    config: { optionMergeStrategies: i }
  } = e.appContext, a = l.get(t);
  let u;
  return a ? u = a : !o.length && !s && !n ? u = t : (u = {}, o.length && o.forEach(
    (h) => so(u, h, i, !0)
  ), so(u, t, i)), _e(t) && l.set(t, u), u;
}
function so(e, t, s, n = !1) {
  const { mixins: o, extends: l } = t;
  l && so(e, l, s, !0), o && o.forEach(
    (i) => so(e, i, s, !0)
  );
  for (const i in t)
    if (!(n && i === "expose")) {
      const a = fd[i] || s && s[i];
      e[i] = a ? a(e[i], t[i]) : t[i];
    }
  return e;
}
const fd = {
  data: il,
  props: al,
  emits: al,
  // objects
  methods: un,
  computed: un,
  // lifecycle
  beforeCreate: rt,
  created: rt,
  beforeMount: rt,
  mounted: rt,
  beforeUpdate: rt,
  updated: rt,
  beforeDestroy: rt,
  beforeUnmount: rt,
  destroyed: rt,
  unmounted: rt,
  activated: rt,
  deactivated: rt,
  errorCaptured: rt,
  serverPrefetch: rt,
  // assets
  components: un,
  directives: un,
  // watch
  watch: md,
  // provide / inject
  provide: il,
  inject: pd
};
function il(e, t) {
  return t ? e ? function() {
    return Ue(
      X(e) ? e.call(this, this) : e,
      X(t) ? t.call(this, this) : t
    );
  } : t : e;
}
function pd(e, t) {
  return un(tr(e), tr(t));
}
function tr(e) {
  if (J(e)) {
    const t = {};
    for (let s = 0; s < e.length; s++)
      t[e[s]] = e[s];
    return t;
  }
  return e;
}
function rt(e, t) {
  return e ? [...new Set([].concat(e, t))] : t;
}
function un(e, t) {
  return e ? Ue(/* @__PURE__ */ Object.create(null), e, t) : t;
}
function al(e, t) {
  return e ? J(e) && J(t) ? [.../* @__PURE__ */ new Set([...e, ...t])] : Ue(
    /* @__PURE__ */ Object.create(null),
    rl(e),
    rl(t ?? {})
  ) : t;
}
function md(e, t) {
  if (!e) return t;
  if (!t) return e;
  const s = Ue(/* @__PURE__ */ Object.create(null), e);
  for (const n in t)
    s[n] = rt(e[n], t[n]);
  return s;
}
function Ci() {
  return {
    app: null,
    config: {
      isNativeTag: Dl,
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
let gd = 0;
function hd(e, t) {
  return function(n, o = null) {
    X(n) || (n = Ue({}, n)), o != null && !_e(o) && (o = null);
    const l = Ci(), i = /* @__PURE__ */ new WeakSet(), a = [];
    let u = !1;
    const h = l.app = {
      _uid: gd++,
      _component: n,
      _props: o,
      _container: null,
      _context: l,
      _instance: null,
      version: qd,
      get config() {
        return l.config;
      },
      set config(g) {
      },
      use(g, ...x) {
        return i.has(g) || (g && X(g.install) ? (i.add(g), g.install(h, ...x)) : X(g) && (i.add(g), g(h, ...x))), h;
      },
      mixin(g) {
        return l.mixins.includes(g) || l.mixins.push(g), h;
      },
      component(g, x) {
        return x ? (l.components[g] = x, h) : l.components[g];
      },
      directive(g, x) {
        return x ? (l.directives[g] = x, h) : l.directives[g];
      },
      mount(g, x, A) {
        if (!u) {
          const k = h._ceVNode || y(n, o);
          return k.appContext = l, A === !0 ? A = "svg" : A === !1 && (A = void 0), e(k, g, A), u = !0, h._container = g, g.__vue_app__ = h, xo(k.component);
        }
      },
      onUnmount(g) {
        a.push(g);
      },
      unmount() {
        u && (wt(
          a,
          h._instance,
          16
        ), e(null, h._container), delete h._container.__vue_app__);
      },
      provide(g, x) {
        return l.provides[g] = x, h;
      },
      runWithContext(g) {
        const x = Rs;
        Rs = h;
        try {
          return g();
        } finally {
          Rs = x;
        }
      }
    };
    return h;
  };
}
let Rs = null;
function bd(e, t, s = ge) {
  const n = os(), o = Ge(t), l = ct(t), i = Ai(e, o), a = Vu((u, h) => {
    let g, x = ge, A;
    return qu(() => {
      const k = e[o];
      qe(g, k) && (g = k, h());
    }), {
      get() {
        return u(), s.get ? s.get(g) : g;
      },
      set(k) {
        const $ = s.set ? s.set(k) : k;
        if (!qe($, g) && !(x !== ge && qe(k, x)))
          return;
        const v = n.vnode.props, H = !!(v && // check if parent has passed v-model
        (t in v || o in v || l in v) && (`onUpdate:${t}` in v || `onUpdate:${o}` in v || `onUpdate:${l}` in v));
        H || (g = k, h()), n.emit(`update:${t}`, $), qe(k, x) && (qe(k, $) && !qe($, A) || // #13524: browsers differ in when they flush microtasks between
        // event listeners. If a v-model listener emits an intermediate value
        // and a following listener restores the model to its previous prop
        // value before parent updates are flushed, the parent render can be
        // deduped as having no prop change. Force a local update so DOM state
        // such as an input's value is synchronized back to the current model.
        H && x !== ge && !qe($, g)) && h(), x = k, A = $;
      }
    };
  });
  return a[Symbol.iterator] = () => {
    let u = 0;
    return {
      next() {
        return u < 2 ? { value: u++ ? i || ge : a, done: !1 } : { done: !0 };
      }
    };
  }, a;
}
const Ai = (e, t) => t === "modelValue" || t === "model-value" ? e.modelModifiers : e[`${t}Modifiers`] || e[`${Ge(t)}Modifiers`] || e[`${ct(t)}Modifiers`];
function vd(e, t, ...s) {
  if (e.isUnmounted) return;
  const n = e.vnode.props || ge;
  let o = s;
  const l = t.startsWith("update:"), i = l && Ai(n, t.slice(7));
  i && (i.trim && (o = s.map((g) => Ve(g) ? g.trim() : g)), i.number && (o = s.map(fo)));
  let a, u = n[a = qn(t)] || // also try camelCase event handler (#2249)
  n[a = qn(Ge(t))];
  !u && l && (u = n[a = qn(ct(t))]), u && wt(
    u,
    e,
    6,
    o
  );
  const h = n[a + "Once"];
  if (h) {
    if (!e.emitted)
      e.emitted = {};
    else if (e.emitted[a])
      return;
    e.emitted[a] = !0, wt(
      h,
      e,
      6,
      o
    );
  }
}
const yd = /* @__PURE__ */ new WeakMap();
function Ei(e, t, s = !1) {
  const n = s ? yd : t.emitsCache, o = n.get(e);
  if (o !== void 0)
    return o;
  const l = e.emits;
  let i = {}, a = !1;
  if (!X(e)) {
    const u = (h) => {
      const g = Ei(h, t, !0);
      g && (a = !0, Ue(i, g));
    };
    !s && t.mixins.length && t.mixins.forEach(u), e.extends && u(e.extends), e.mixins && e.mixins.forEach(u);
  }
  return !l && !a ? (_e(e) && n.set(e, null), null) : (J(l) ? l.forEach((u) => i[u] = null) : Ue(i, l), _e(e) && n.set(e, i), i);
}
function vo(e, t) {
  return !e || !lo(t) ? !1 : (t = t.slice(2), t = t === "Once" ? t : t.replace(/Once$/, ""), ye(e, t[0].toLowerCase() + t.slice(1)) || ye(e, ct(t)) || ye(e, t));
}
function ul(e) {
  const {
    type: t,
    vnode: s,
    proxy: n,
    withProxy: o,
    propsOptions: [l],
    slots: i,
    attrs: a,
    emit: u,
    render: h,
    renderCache: g,
    props: x,
    data: A,
    setupState: k,
    ctx: $,
    inheritAttrs: v
  } = e, H = eo(e);
  let z, D;
  try {
    if (s.shapeFlag & 4) {
      const U = o || n, Z = U;
      z = Rt(
        h.call(
          Z,
          U,
          g,
          x,
          k,
          A,
          $
        )
      ), D = a;
    } else {
      const U = t;
      z = Rt(
        U.length > 1 ? U(
          x,
          { attrs: a, slots: i, emit: u }
        ) : U(
          x,
          null
        )
      ), D = t.props ? a : xd(a);
    }
  } catch (U) {
    yn.length = 0, In(U, e, 1), z = y(Ot);
  }
  let q = z;
  if (D && v !== !1) {
    const U = Object.keys(D), { shapeFlag: Z } = q;
    U.length && Z & 7 && (l && U.some(io) && (D = _d(
      D,
      l
    )), q = ms(q, D, !1, !0));
  }
  return s.dirs && (q = ms(q, null, !1, !0), q.dirs = q.dirs ? q.dirs.concat(s.dirs) : s.dirs), s.transition && vr(q, s.transition), z = q, eo(H), z;
}
const xd = (e) => {
  let t;
  for (const s in e)
    (s === "class" || s === "style" || lo(s)) && ((t || (t = {}))[s] = e[s]);
  return t;
}, _d = (e, t) => {
  const s = {};
  for (const n in e)
    (!io(n) || !(n.slice(9) in t)) && (s[n] = e[n]);
  return s;
};
function wd(e, t, s) {
  const { props: n, children: o, component: l } = e, { props: i, children: a, patchFlag: u } = t, h = l.emitsOptions;
  if (t.dirs || t.transition)
    return !0;
  if (s && u >= 0) {
    if (u & 1024)
      return !0;
    if (u & 16)
      return n ? dl(n, i, h) : !!i;
    if (u & 8) {
      const g = t.dynamicProps;
      for (let x = 0; x < g.length; x++) {
        const A = g[x];
        if (Ii(i, n, A) && !vo(h, A))
          return !0;
      }
    }
  } else
    return (o || a) && (!a || !a.$stable) ? !0 : n === i ? !1 : n ? i ? dl(n, i, h) : !0 : !!i;
  return !1;
}
function dl(e, t, s) {
  const n = Object.keys(t);
  if (n.length !== Object.keys(e).length)
    return !0;
  for (let o = 0; o < n.length; o++) {
    const l = n[o];
    if (Ii(t, e, l) && !vo(s, l))
      return !0;
  }
  return !1;
}
function Ii(e, t, s) {
  const n = e[s], o = t[s];
  return s === "style" && _e(n) && _e(o) ? !es(n, o) : n !== o;
}
function kd({ vnode: e, parent: t, suspense: s }, n) {
  for (; t; ) {
    const o = t.subTree;
    if (o.suspense && o.suspense.activeBranch === e && (o.suspense.vnode.el = o.el = n, e = o), o === e)
      (e = t.vnode).el = n, t = t.parent;
    else
      break;
  }
  s && s.activeBranch === e && (s.vnode.el = n);
}
const Ti = {}, Pi = () => Object.create(Ti), Ri = (e) => Object.getPrototypeOf(e) === Ti;
function Sd(e, t, s, n = !1) {
  const o = {}, l = Pi();
  e.propsDefaults = /* @__PURE__ */ Object.create(null), Mi(e, t, o, l);
  for (const i in e.propsOptions[0])
    i in o || (o[i] = void 0);
  s ? e.props = n ? o : /* @__PURE__ */ Au(o) : e.type.props ? e.props = o : e.props = l, e.attrs = l;
}
function Cd(e, t, s, n) {
  const {
    props: o,
    attrs: l,
    vnode: { patchFlag: i }
  } = e, a = /* @__PURE__ */ ve(o), [u] = e.propsOptions;
  let h = !1;
  if (
    // always force full diff in dev
    // - #1942 if hmr is enabled with sfc component
    // - vite#872 non-sfc component used by sfc component
    (n || i > 0) && !(i & 16)
  ) {
    if (i & 8) {
      const g = e.vnode.dynamicProps;
      for (let x = 0; x < g.length; x++) {
        let A = g[x];
        if (vo(e.emitsOptions, A))
          continue;
        const k = t[A];
        if (u)
          if (ye(l, A))
            k !== l[A] && (l[A] = k, h = !0);
          else {
            const $ = Ge(A);
            o[$] = sr(
              u,
              a,
              $,
              k,
              e,
              !1
            );
          }
        else
          k !== l[A] && (l[A] = k, h = !0);
      }
    }
  } else {
    Mi(e, t, o, l) && (h = !0);
    let g;
    for (const x in a)
      (!t || // for camelCase
      !ye(t, x) && // it's possible the original props was passed in as kebab-case
      // and converted to camelCase (#955)
      ((g = ct(x)) === x || !ye(t, g))) && (u ? s && // for camelCase
      (s[x] !== void 0 || // for kebab-case
      s[g] !== void 0) && (o[x] = sr(
        u,
        a,
        x,
        void 0,
        e,
        !0
      )) : delete o[x]);
    if (l !== a)
      for (const x in l)
        (!t || !ye(t, x)) && (delete l[x], h = !0);
  }
  h && Ht(e.attrs, "set", "");
}
function Mi(e, t, s, n) {
  const [o, l] = e.propsOptions;
  let i = !1, a;
  if (t)
    for (let u in t) {
      if (pn(u))
        continue;
      const h = t[u];
      let g;
      o && ye(o, g = Ge(u)) ? !l || !l.includes(g) ? s[g] = h : (a || (a = {}))[g] = h : vo(e.emitsOptions, u) || (!(u in n) || h !== n[u]) && (n[u] = h, i = !0);
    }
  if (l) {
    const u = /* @__PURE__ */ ve(s), h = a || ge;
    for (let g = 0; g < l.length; g++) {
      const x = l[g];
      s[x] = sr(
        o,
        u,
        x,
        h[x],
        e,
        !ye(h, x)
      );
    }
  }
  return i;
}
function sr(e, t, s, n, o, l) {
  const i = e[s];
  if (i != null) {
    const a = ye(i, "default");
    if (a && n === void 0) {
      const u = i.default;
      if (i.type !== Function && !i.skipFactory && X(u)) {
        const { propsDefaults: h } = o;
        if (s in h)
          n = h[s];
        else {
          const g = Pn(o);
          n = h[s] = u.call(
            null,
            t
          ), g();
        }
      } else
        n = u;
      o.ce && o.ce._setProp(s, n);
    }
    i[
      0
      /* shouldCast */
    ] && (l && !a ? n = !1 : i[
      1
      /* shouldCastTrue */
    ] && (n === "" || n === ct(s)) && (n = !0));
  }
  return n;
}
const Ad = /* @__PURE__ */ new WeakMap();
function Vi(e, t, s = !1) {
  const n = s ? Ad : t.propsCache, o = n.get(e);
  if (o)
    return o;
  const l = e.props, i = {}, a = [];
  let u = !1;
  if (!X(e)) {
    const g = (x) => {
      u = !0;
      const [A, k] = Vi(x, t, !0);
      Ue(i, A), k && a.push(...k);
    };
    !s && t.mixins.length && t.mixins.forEach(g), e.extends && g(e.extends), e.mixins && e.mixins.forEach(g);
  }
  if (!l && !u)
    return _e(e) && n.set(e, Es), Es;
  if (J(l))
    for (let g = 0; g < l.length; g++) {
      const x = Ge(l[g]);
      cl(x) && (i[x] = ge);
    }
  else if (l)
    for (const g in l) {
      const x = Ge(g);
      if (cl(x)) {
        const A = l[g], k = i[x] = J(A) || X(A) ? { type: A } : Ue({}, A), $ = k.type;
        let v = !1, H = !0;
        if (J($))
          for (let z = 0; z < $.length; ++z) {
            const D = $[z], q = X(D) && D.name;
            if (q === "Boolean") {
              v = !0;
              break;
            } else q === "String" && (H = !1);
          }
        else
          v = X($) && $.name === "Boolean";
        k[
          0
          /* shouldCast */
        ] = v, k[
          1
          /* shouldCastTrue */
        ] = H, (v || ye(k, "default")) && a.push(x);
      }
    }
  const h = [i, a];
  return _e(e) && n.set(e, h), h;
}
function cl(e) {
  return e[0] !== "$" && !pn(e);
}
const wr = (e) => e === "_" || e === "_ctx" || e === "$stable", kr = (e) => J(e) ? e.map(Rt) : [Rt(e)], Ed = (e, t, s) => {
  if (t._n)
    return t;
  const n = S((...o) => kr(t(...o)), s);
  return n._c = !1, n;
}, $i = (e, t, s) => {
  const n = e._ctx;
  for (const o in e) {
    if (wr(o)) continue;
    const l = e[o];
    if (X(l))
      t[o] = Ed(o, l, n);
    else if (l != null) {
      const i = kr(l);
      t[o] = () => i;
    }
  }
}, Oi = (e, t) => {
  const s = kr(t);
  e.slots.default = () => s;
}, ji = (e, t, s) => {
  for (const n in t)
    (s || !wr(n)) && (e[n] = t[n]);
}, Id = (e, t, s) => {
  const n = e.slots = Pi();
  if (e.vnode.shapeFlag & 32) {
    const o = t._;
    o ? (ji(n, t, s), s && zl(n, "_", o, !0)) : $i(t, n);
  } else t && Oi(e, t);
}, Td = (e, t, s) => {
  const { vnode: n, slots: o } = e;
  let l = !0, i = ge;
  if (n.shapeFlag & 32) {
    const a = t._;
    a ? s && a === 1 ? l = !1 : ji(o, t, s) : (l = !t.$stable, $i(t, o)), i = t;
  } else t && (Oi(e, t), i = { default: 1 });
  if (l)
    for (const a in o)
      !wr(a) && i[a] == null && delete o[a];
}, dt = $d;
function Pd(e) {
  return Rd(e);
}
function Rd(e, t) {
  const s = po();
  s.__VUE__ = !0;
  const {
    insert: n,
    remove: o,
    patchProp: l,
    createElement: i,
    createText: a,
    createComment: u,
    setText: h,
    setElementText: g,
    parentNode: x,
    nextSibling: A,
    setScopeId: k = Mt,
    insertStaticContent: $
  } = e, v = (m, b, w, P = null, E = null, I = null, j = void 0, N = null, O = !!b.dynamicChildren) => {
    if (m === b)
      return;
    m && !on(m, b) && (P = gs(m), De(m, E, I, !0), m = null), b.patchFlag === -2 && (O = !1, b.dynamicChildren = null);
    const { type: T, ref: Y, shapeFlag: B } = b;
    switch (T) {
      case yo:
        H(m, b, w, P);
        break;
      case Ot:
        z(m, b, w, P);
        break;
      case Jn:
        m == null && D(b, w, P, j);
        break;
      case ce:
        ae(
          m,
          b,
          w,
          P,
          E,
          I,
          j,
          N,
          O
        );
        break;
      default:
        B & 1 ? Z(
          m,
          b,
          w,
          P,
          E,
          I,
          j,
          N,
          O
        ) : B & 6 ? he(
          m,
          b,
          w,
          P,
          E,
          I,
          j,
          N,
          O
        ) : (B & 64 || B & 128) && T.process(
          m,
          b,
          w,
          P,
          E,
          I,
          j,
          N,
          O,
          oe
        );
    }
    Y != null && E ? bn(Y, m && m.ref, I, b || m, !b) : Y == null && m && m.ref != null && bn(m.ref, null, I, m, !0);
  }, H = (m, b, w, P) => {
    if (m == null)
      n(
        b.el = a(b.children),
        w,
        P
      );
    else {
      const E = b.el = m.el;
      b.children !== m.children && h(E, b.children);
    }
  }, z = (m, b, w, P) => {
    m == null ? n(
      b.el = u(b.children || ""),
      w,
      P
    ) : b.el = m.el;
  }, D = (m, b, w, P) => {
    [m.el, m.anchor] = $(
      m.children,
      b,
      w,
      P,
      m.el,
      m.anchor
    );
  }, q = ({ el: m, anchor: b }, w, P) => {
    let E;
    for (; m && m !== b; )
      E = A(m), n(m, w, P), m = E;
    n(b, w, P);
  }, U = ({ el: m, anchor: b }) => {
    let w;
    for (; m && m !== b; )
      w = A(m), o(m), m = w;
    o(b);
  }, Z = (m, b, w, P, E, I, j, N, O) => {
    if (b.type === "svg" ? j = "svg" : b.type === "math" && (j = "mathml"), m == null)
      $e(
        b,
        w,
        P,
        E,
        I,
        j,
        N,
        O
      );
    else {
      const T = m.el && m.el._isVueCE ? m.el : null;
      try {
        T && T._beginPatch(), Oe(
          m,
          b,
          E,
          I,
          j,
          N,
          O
        );
      } finally {
        T && T._endPatch();
      }
    }
  }, $e = (m, b, w, P, E, I, j, N) => {
    let O, T;
    const { props: Y, shapeFlag: B, transition: G, dirs: Q } = m;
    if (O = m.el = i(
      m.type,
      I,
      Y && Y.is,
      Y
    ), B & 8 ? g(O, m.children) : B & 16 && te(
      m.children,
      O,
      null,
      P,
      E,
      Bo(m, I),
      j,
      N
    ), Q && as(m, null, P, "created"), K(O, m, m.scopeId, j, P), Y) {
      for (const de in Y)
        de !== "value" && !pn(de) && l(O, de, null, Y[de], I, P);
      "value" in Y && l(O, "value", null, Y.value, I), (T = Y.onVnodeBeforeMount) && It(T, P, m);
    }
    Q && as(m, null, P, "beforeMount");
    const ue = Md(E, G);
    ue && G.beforeEnter(O), n(O, b, w), ((T = Y && Y.onVnodeMounted) || ue || Q) && dt(() => {
      try {
        T && It(T, P, m), ue && G.enter(O), Q && as(m, null, P, "mounted");
      } finally {
      }
    }, E);
  }, K = (m, b, w, P, E) => {
    if (w && k(m, w), P)
      for (let I = 0; I < P.length; I++)
        k(m, P[I]);
    if (E) {
      let I = E.subTree;
      if (b === I || Di(I.type) && (I.ssContent === b || I.ssFallback === b)) {
        const j = E.vnode;
        K(
          m,
          j,
          j.scopeId,
          j.slotScopeIds,
          E.parent
        );
      }
    }
  }, te = (m, b, w, P, E, I, j, N, O = 0) => {
    for (let T = O; T < m.length; T++) {
      const Y = m[T] = N ? Ft(m[T]) : Rt(m[T]);
      v(
        null,
        Y,
        b,
        w,
        P,
        E,
        I,
        j,
        N
      );
    }
  }, Oe = (m, b, w, P, E, I, j) => {
    const N = b.el = m.el;
    let { patchFlag: O, dynamicChildren: T, dirs: Y } = b;
    O |= m.patchFlag & 16;
    const B = m.props || ge, G = b.props || ge;
    let Q;
    if (w && us(w, !1), (Q = G.onVnodeBeforeUpdate) && It(Q, w, b, m), Y && as(b, m, w, "beforeUpdate"), w && us(w, !0), // #6385 the old vnode may be a user-wrapped non-isomorphic block
    // Force full diff when block metadata is unstable.
    T && (!m.dynamicChildren || m.dynamicChildren.length !== T.length) && (O = 0, j = !1, T = null), (B.innerHTML && G.innerHTML == null || B.textContent && G.textContent == null) && g(N, ""), T ? we(
      m.dynamicChildren,
      T,
      N,
      w,
      P,
      Bo(b, E),
      I
    ) : j || ne(
      m,
      b,
      N,
      null,
      w,
      P,
      Bo(b, E),
      I,
      !1
    ), O > 0) {
      if (O & 16)
        Me(N, B, G, w, E);
      else if (O & 2 && B.class !== G.class && l(N, "class", null, G.class, E), O & 4 && l(N, "style", B.style, G.style, E), O & 8) {
        const ue = b.dynamicProps;
        for (let de = 0; de < ue.length; de++) {
          const ie = ue[de], ke = B[ie], Ee = G[ie];
          (Ee !== ke || ie === "value") && l(N, ie, ke, Ee, E, w);
        }
      }
      O & 1 && m.children !== b.children && g(N, b.children);
    } else !j && T == null && Me(N, B, G, w, E);
    ((Q = G.onVnodeUpdated) || Y) && dt(() => {
      Q && It(Q, w, b, m), Y && as(b, m, w, "updated");
    }, P);
  }, we = (m, b, w, P, E, I, j) => {
    for (let N = 0; N < b.length; N++) {
      const O = m[N], T = b[N], Y = (
        // oldVNode may be an errored async setup() component inside Suspense
        // which will not have a mounted element
        O.el && // - In the case of a Fragment, we need to provide the actual parent
        // of the Fragment itself so it can move its children.
        (O.type === ce || // - In the case of different nodes, there is going to be a replacement
        // which also requires the correct parent container
        !on(O, T) || // - In the case of a component, it could contain anything.
        O.shapeFlag & 198) ? x(O.el) : (
          // In other cases, the parent container is not actually used so we
          // just pass the block element here to avoid a DOM parentNode call.
          w
        )
      );
      v(
        O,
        T,
        Y,
        null,
        P,
        E,
        I,
        j,
        !0
      );
    }
  }, Me = (m, b, w, P, E) => {
    if (b !== w) {
      if (b !== ge)
        for (const I in b)
          !pn(I) && !(I in w) && l(
            m,
            I,
            b[I],
            null,
            E,
            P
          );
      for (const I in w) {
        if (pn(I)) continue;
        const j = w[I], N = b[I];
        j !== N && I !== "value" && l(m, I, N, j, E, P);
      }
      "value" in w && l(m, "value", b.value, w.value, E);
    }
  }, ae = (m, b, w, P, E, I, j, N, O) => {
    const T = b.el = m ? m.el : a(""), Y = b.anchor = m ? m.anchor : a("");
    let { patchFlag: B, dynamicChildren: G, slotScopeIds: Q } = b;
    Q && (N = N ? N.concat(Q) : Q), m == null ? (n(T, w, P), n(Y, w, P), te(
      // #10007
      // such fragment like `<></>` will be compiled into
      // a fragment which doesn't have a children.
      // In this case fallback to an empty array
      b.children || [],
      w,
      Y,
      E,
      I,
      j,
      N,
      O
    )) : B > 0 && B & 64 && G && // #2715 the previous fragment could've been a BAILed one as a result
    // of renderSlot() with no valid children
    m.dynamicChildren && m.dynamicChildren.length === G.length ? (we(
      m.dynamicChildren,
      G,
      w,
      E,
      I,
      j,
      N
    ), // #2080 if the stable fragment has a key, it's a <template v-for> that may
    //  get moved around. Make sure all root level vnodes inherit el.
    // #2134 or if it's a component root, it may also get moved around
    // as the component is being moved.
    (b.key != null || E && b === E.subTree) && Ni(
      m,
      b,
      !0
      /* shallow */
    )) : ne(
      m,
      b,
      w,
      Y,
      E,
      I,
      j,
      N,
      O
    );
  }, he = (m, b, w, P, E, I, j, N, O) => {
    b.slotScopeIds = N, m == null ? b.shapeFlag & 512 ? E.ctx.activate(
      b,
      w,
      P,
      j,
      O
    ) : Je(
      b,
      w,
      P,
      E,
      I,
      j,
      O
    ) : ft(m, b, O);
  }, Je = (m, b, w, P, E, I, j) => {
    const N = m.component = Bd(
      m,
      P,
      E
    );
    if (xr(m) && (N.ctx.renderer = oe), Fd(N, !1, j), N.asyncDep) {
      if (E && E.registerDep(N, Ce, j), !m.el) {
        const O = N.subTree = y(Ot);
        z(null, O, b, w), m.placeholder = O.el;
      }
    } else
      Ce(
        N,
        m,
        b,
        w,
        E,
        I,
        j
      );
  }, ft = (m, b, w) => {
    const P = b.component = m.component;
    if (wd(m, b, w))
      if (P.asyncDep && !P.asyncResolved) {
        fe(P, b, w);
        return;
      } else
        P.next = b, P.update();
    else
      b.el = m.el, P.vnode = b;
  }, Ce = (m, b, w, P, E, I, j) => {
    const N = () => {
      if (m.isMounted) {
        let { next: B, bu: G, u: Q, parent: ue, vnode: de } = m;
        {
          const Qe = Li(m);
          if (Qe) {
            B && (B.el = de.el, fe(m, B, j)), Qe.asyncDep.then(() => {
              dt(() => {
                m.isUnmounted || T();
              }, E);
            });
            return;
          }
        }
        let ie = B, ke;
        us(m, !1), B ? (B.el = de.el, fe(m, B, j)) : B = de, G && Gn(G), (ke = B.props && B.props.onVnodeBeforeUpdate) && It(ke, ue, B, de), us(m, !0);
        const Ee = ul(m), nt = m.subTree;
        m.subTree = Ee, v(
          nt,
          Ee,
          // parent may have changed if it's in a teleport
          x(nt.el),
          // anchor may have changed if it's in a fragment
          gs(nt),
          m,
          E,
          I
        ), B.el = Ee.el, ie === null && kd(m, Ee.el), Q && dt(Q, E), (ke = B.props && B.props.onVnodeUpdated) && dt(
          () => It(ke, ue, B, de),
          E
        );
      } else {
        let B;
        const { el: G, props: Q } = b, { bm: ue, m: de, parent: ie, root: ke, type: Ee } = m, nt = Ps(b);
        us(m, !1), ue && Gn(ue), !nt && (B = Q && Q.onVnodeBeforeMount) && It(B, ie, b), us(m, !0);
        {
          ke.ce && ke.ce._hasShadowRoot() && ke.ce._injectChildStyle(
            Ee,
            m.parent ? m.parent.type : void 0
          );
          const Qe = m.subTree = ul(m);
          v(
            null,
            Qe,
            w,
            P,
            m,
            E,
            I
          ), b.el = Qe.el;
        }
        if (de && dt(de, E), !nt && (B = Q && Q.onVnodeMounted)) {
          const Qe = b;
          dt(
            () => It(B, ie, Qe),
            E
          );
        }
        (b.shapeFlag & 256 || ie && Ps(ie.vnode) && ie.vnode.shapeFlag & 256) && m.a && dt(m.a, E), m.isMounted = !0, b = w = P = null;
      }
    };
    m.scope.on();
    const O = m.effect = new Gl(N);
    m.scope.off();
    const T = m.update = O.run.bind(O), Y = m.job = O.runIfDirty.bind(O);
    Y.i = m, Y.id = m.uid, O.scheduler = () => gr(Y), us(m, !0), T();
  }, fe = (m, b, w) => {
    b.component = m;
    const P = m.vnode.props;
    m.vnode = b, m.next = null, Cd(m, b.props, P, w), Td(m, b.children, w), Vt(), tl(m), $t();
  }, ne = (m, b, w, P, E, I, j, N, O = !1) => {
    const T = m && m.children, Y = m ? m.shapeFlag : 0, B = b.children, { patchFlag: G, shapeFlag: Q } = b;
    if (G > 0) {
      if (G & 128) {
        Ye(
          T,
          B,
          w,
          P,
          E,
          I,
          j,
          N,
          O
        );
        return;
      } else if (G & 256) {
        Ae(
          T,
          B,
          w,
          P,
          E,
          I,
          j,
          N,
          O
        );
        return;
      }
    }
    Q & 8 ? (Y & 16 && kt(T, E, I), B !== T && g(w, B)) : Y & 16 ? Q & 16 ? Ye(
      T,
      B,
      w,
      P,
      E,
      I,
      j,
      N,
      O
    ) : kt(T, E, I, !0) : (Y & 8 && g(w, ""), Q & 16 && te(
      B,
      w,
      P,
      E,
      I,
      j,
      N,
      O
    ));
  }, Ae = (m, b, w, P, E, I, j, N, O) => {
    m = m || Es, b = b || Es;
    const T = m.length, Y = b.length, B = Math.min(T, Y);
    let G;
    for (G = 0; G < B; G++) {
      const Q = b[G] = O ? Ft(b[G]) : Rt(b[G]);
      v(
        m[G],
        Q,
        w,
        null,
        E,
        I,
        j,
        N,
        O
      );
    }
    T > Y ? kt(
      m,
      E,
      I,
      !0,
      !1,
      B
    ) : te(
      b,
      w,
      P,
      E,
      I,
      j,
      N,
      O,
      B
    );
  }, Ye = (m, b, w, P, E, I, j, N, O) => {
    let T = 0;
    const Y = b.length;
    let B = m.length - 1, G = Y - 1;
    for (; T <= B && T <= G; ) {
      const Q = m[T], ue = b[T] = O ? Ft(b[T]) : Rt(b[T]);
      if (on(Q, ue))
        v(
          Q,
          ue,
          w,
          null,
          E,
          I,
          j,
          N,
          O
        );
      else
        break;
      T++;
    }
    for (; T <= B && T <= G; ) {
      const Q = m[B], ue = b[G] = O ? Ft(b[G]) : Rt(b[G]);
      if (on(Q, ue))
        v(
          Q,
          ue,
          w,
          null,
          E,
          I,
          j,
          N,
          O
        );
      else
        break;
      B--, G--;
    }
    if (T > B) {
      if (T <= G) {
        const Q = G + 1, ue = Q < Y ? b[Q].el : P;
        for (; T <= G; )
          v(
            null,
            b[T] = O ? Ft(b[T]) : Rt(b[T]),
            w,
            ue,
            E,
            I,
            j,
            N,
            O
          ), T++;
      }
    } else if (T > G)
      for (; T <= B; )
        De(m[T], E, I, !0), T++;
    else {
      const Q = T, ue = T, de = /* @__PURE__ */ new Map();
      for (T = ue; T <= G; T++) {
        const ot = b[T] = O ? Ft(b[T]) : Rt(b[T]);
        ot.key != null && de.set(ot.key, T);
      }
      let ie, ke = 0;
      const Ee = G - ue + 1;
      let nt = !1, Qe = 0;
      const Jt = new Array(Ee);
      for (T = 0; T < Ee; T++) Jt[T] = 0;
      for (T = Q; T <= B; T++) {
        const ot = m[T];
        if (ke >= Ee) {
          De(ot, E, I, !0);
          continue;
        }
        let We;
        if (ot.key != null)
          We = de.get(ot.key);
        else
          for (ie = ue; ie <= G; ie++)
            if (Jt[ie - ue] === 0 && on(ot, b[ie])) {
              We = ie;
              break;
            }
        We === void 0 ? De(ot, E, I, !0) : (Jt[We - ue] = T + 1, We >= Qe ? Qe = We : nt = !0, v(
          ot,
          b[We],
          w,
          null,
          E,
          I,
          j,
          N,
          O
        ), ke++);
      }
      const rs = nt ? Vd(Jt) : Es;
      for (ie = rs.length - 1, T = Ee - 1; T >= 0; T--) {
        const ot = ue + T, We = b[ot], St = b[ot + 1], pt = ot + 1 < Y ? (
          // #13559, #14173 fallback to el placeholder for unresolved async component
          St.el || Ui(St)
        ) : P;
        Jt[T] === 0 ? v(
          null,
          We,
          w,
          pt,
          E,
          I,
          j,
          N,
          O
        ) : nt && (ie < 0 || T !== rs[ie] ? je(We, w, pt, 2) : ie--);
      }
    }
  }, je = (m, b, w, P, E = null) => {
    const { el: I, type: j, transition: N, children: O, shapeFlag: T } = m;
    if (T & 6) {
      je(m.component.subTree, b, w, P);
      return;
    }
    if (T & 128) {
      m.suspense.move(b, w, P);
      return;
    }
    if (T & 64) {
      j.move(m, b, w, oe);
      return;
    }
    if (j === ce) {
      n(I, b, w);
      for (let B = 0; B < O.length; B++)
        je(O[B], b, w, P);
      n(m.anchor, b, w);
      return;
    }
    if (j === Jn) {
      q(m, b, w);
      return;
    }
    if (P !== 2 && T & 1 && N)
      if (P === 0)
        N.persisted && !I[Uo] ? n(I, b, w) : (N.beforeEnter(I), n(I, b, w), dt(() => N.enter(I), E));
      else {
        const { leave: B, delayLeave: G, afterLeave: Q } = N, ue = () => {
          m.ctx.isUnmounted ? o(I) : n(I, b, w);
        }, de = () => {
          const ie = I._isLeaving || !!I[Uo];
          I._isLeaving && I[Uo](
            !0
            /* cancelled */
          ), N.persisted && !ie ? ue() : B(I, () => {
            ue(), Q && Q();
          });
        };
        G ? G(I, ue, de) : de();
      }
    else
      n(I, b, w);
  }, De = (m, b, w, P = !1, E = !1) => {
    const {
      type: I,
      props: j,
      ref: N,
      children: O,
      dynamicChildren: T,
      shapeFlag: Y,
      patchFlag: B,
      dirs: G,
      cacheIndex: Q,
      memo: ue
    } = m;
    if (B === -2 && (E = !1), N != null && (Vt(), bn(N, null, w, m, !0), $t()), Q != null && (b.renderCache[Q] = void 0), Y & 256) {
      b.ctx.deactivate(m);
      return;
    }
    const de = Y & 1 && G, ie = !Ps(m);
    let ke;
    if (ie && (ke = j && j.onVnodeBeforeUnmount) && It(ke, b, m), Y & 6)
      wo(m.component, w, P);
    else {
      if (Y & 128) {
        m.suspense.unmount(w, P);
        return;
      }
      de && as(m, null, b, "beforeUnmount"), Y & 64 ? m.type.remove(
        m,
        b,
        w,
        oe,
        P
      ) : T && // #5154
      // when v-once is used inside a block, setBlockTracking(-1) marks the
      // parent block with hasOnce: true
      // so that it doesn't take the fast path during unmount - otherwise
      // components nested in v-once are never unmounted.
      !T.hasOnce && // #1153: fast path should not be taken for non-stable (v-for) fragments
      (I !== ce || B > 0 && B & 64) ? kt(
        T,
        b,
        w,
        !1,
        !0
      ) : (I === ce && B & 384 || !E && Y & 16) && kt(O, b, w), P && Rn(m);
    }
    const Ee = ue != null && Q == null;
    (ie && (ke = j && j.onVnodeUnmounted) || de || Ee) && dt(() => {
      ke && It(ke, b, m), de && as(m, null, b, "unmounted"), Ee && (m.el = null);
    }, w);
  }, Rn = (m) => {
    const { type: b, el: w, anchor: P, transition: E } = m;
    if (b === ce) {
      Mn(w, P);
      return;
    }
    if (b === Jn) {
      U(m);
      return;
    }
    const I = () => {
      o(w), E && !E.persisted && E.afterLeave && E.afterLeave();
    };
    if (m.shapeFlag & 1 && E && !E.persisted) {
      const { leave: j, delayLeave: N } = E, O = () => j(w, I);
      N ? N(m.el, I, O) : O();
    } else
      I();
  }, Mn = (m, b) => {
    let w;
    for (; m !== b; )
      w = A(m), o(m), m = w;
    o(b);
  }, wo = (m, b, w) => {
    const { bum: P, scope: E, job: I, subTree: j, um: N, m: O, a: T } = m;
    fl(O), fl(T), P && Gn(P), E.stop(), I && (I.flags |= 8, De(j, m, b, w)), N && dt(N, b), dt(() => {
      m.isUnmounted = !0;
    }, b);
  }, kt = (m, b, w, P = !1, E = !1, I = 0) => {
    for (let j = I; j < m.length; j++)
      De(m[j], b, w, P, E);
  }, gs = (m) => {
    if (m.shapeFlag & 6)
      return gs(m.component.subTree);
    if (m.shapeFlag & 128)
      return m.suspense.next();
    const b = A(m.anchor || m.el), w = b && b[Ju];
    return w ? A(w) : b;
  };
  let Ls = !1;
  const Fe = (m, b, w) => {
    let P;
    m == null ? b._vnode && (De(b._vnode, null, null, !0), P = b._vnode.component) : v(
      b._vnode || null,
      m,
      b,
      null,
      null,
      null,
      w
    ), b._vnode = m, Ls || (Ls = !0, tl(P), pi(), Ls = !1);
  }, oe = {
    p: v,
    um: De,
    m: je,
    r: Rn,
    mt: Je,
    mc: te,
    pc: ne,
    pbc: we,
    n: gs,
    o: e
  };
  return {
    render: Fe,
    hydrate: void 0,
    createApp: hd(Fe)
  };
}
function Bo({ type: e, props: t }, s) {
  return s === "svg" && e === "foreignObject" || s === "mathml" && e === "annotation-xml" && t && t.encoding && t.encoding.includes("html") ? void 0 : s;
}
function us({ effect: e, job: t }, s) {
  s ? (e.flags |= 32, t.flags |= 4) : (e.flags &= -33, t.flags &= -5);
}
function Md(e, t) {
  return (!e || e && !e.pendingBranch) && t && !t.persisted;
}
function Ni(e, t, s = !1) {
  const n = e.children, o = t.children;
  if (J(n) && J(o))
    for (let l = 0; l < n.length; l++) {
      const i = n[l];
      let a = o[l];
      a.shapeFlag & 1 && !a.dynamicChildren && ((a.patchFlag <= 0 || a.patchFlag === 32) && (a = o[l] = Ft(o[l]), a.el = i.el), !s && a.patchFlag !== -2 && Ni(i, a)), a.type === yo && (a.patchFlag === -1 && (a = o[l] = Ft(a)), a.el = i.el), a.type === Ot && !a.el && (a.el = i.el);
    }
}
function Vd(e) {
  const t = e.slice(), s = [0];
  let n, o, l, i, a;
  const u = e.length;
  for (n = 0; n < u; n++) {
    const h = e[n];
    if (h !== 0) {
      if (o = s[s.length - 1], e[o] < h) {
        t[n] = o, s.push(n);
        continue;
      }
      for (l = 0, i = s.length - 1; l < i; )
        a = l + i >> 1, e[s[a]] < h ? l = a + 1 : i = a;
      h < e[s[l]] && (l > 0 && (t[n] = s[l - 1]), s[l] = n);
    }
  }
  for (l = s.length, i = s[l - 1]; l-- > 0; )
    s[l] = i, i = t[i];
  return s;
}
function Li(e) {
  const t = e.subTree.component;
  if (t)
    return t.asyncDep && !t.asyncResolved ? t : Li(t);
}
function fl(e) {
  if (e)
    for (let t = 0; t < e.length; t++)
      e[t].flags |= 8;
}
function Ui(e) {
  if (e.placeholder)
    return e.placeholder;
  const t = e.component;
  return t ? Ui(t.subTree) : null;
}
const Di = (e) => e.__isSuspense;
function $d(e, t) {
  t && t.pendingBranch ? J(e) ? t.effects.push(...e) : t.effects.push(e) : zu(e);
}
const ce = /* @__PURE__ */ Symbol.for("v-fgt"), yo = /* @__PURE__ */ Symbol.for("v-txt"), Ot = /* @__PURE__ */ Symbol.for("v-cmt"), Jn = /* @__PURE__ */ Symbol.for("v-stc"), yn = [];
let mt = null;
function C(e = !1) {
  yn.push(mt = e ? null : []);
}
function Od() {
  yn.pop(), mt = yn[yn.length - 1] || null;
}
let Sn = 1;
function no(e, t = !1) {
  Sn += e, e < 0 && mt && t && (mt.hasOnce = !0);
}
function Bi(e) {
  return e.dynamicChildren = Sn > 0 ? mt || Es : null, Od(), Sn > 0 && mt && mt.push(e), e;
}
function R(e, t, s, n, o, l) {
  return Bi(
    f(
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
function Te(e, t, s, n, o) {
  return Bi(
    y(
      e,
      t,
      s,
      n,
      o,
      !0
    )
  );
}
function Cn(e) {
  return e ? e.__v_isVNode === !0 : !1;
}
function on(e, t) {
  return e.type === t.type && e.key === t.key;
}
const Fi = ({ key: e }) => e ?? null, Yn = ({
  ref: e,
  ref_key: t,
  ref_for: s
}) => (typeof e == "number" && (e = "" + e), e != null ? Ve(e) || /* @__PURE__ */ Re(e) || X(e) ? { i: st, r: e, k: t, f: !!s } : e : null);
function f(e, t = null, s = null, n = 0, o = null, l = e === ce ? 0 : 1, i = !1, a = !1) {
  const u = {
    __v_isVNode: !0,
    __v_skip: !0,
    type: e,
    props: t,
    key: t && Fi(t),
    ref: t && Yn(t),
    scopeId: gi,
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
    ctx: st
  };
  return a ? (oo(u, s), l & 128 && e.normalize(u)) : s && (u.shapeFlag |= Ve(s) ? 8 : 16), Sn > 0 && // avoid a block node from tracking itself
  !i && // has current parent block
  mt && // presence of a patch flag indicates this node needs patching on updates.
  // component nodes also should always be patched, because even if the
  // component doesn't need to update, it needs to persist the instance on to
  // the next vnode so that it can be properly unmounted later.
  (u.patchFlag > 0 || l & 6) && // the EVENTS flag is only for hydration and if it is the only flag, the
  // vnode should not be considered dynamic due to handler caching.
  u.patchFlag !== 32 && mt.push(u), u;
}
const y = jd;
function jd(e, t = null, s = null, n = 0, o = null, l = !1) {
  if ((!e || e === ad) && (e = Ot), Cn(e)) {
    const a = ms(
      e,
      t,
      !0
      /* mergeRef: true */
    );
    return s && oo(a, s), Sn > 0 && !l && mt && (a.shapeFlag & 6 ? mt[mt.indexOf(e)] = a : mt.push(a)), a.patchFlag = -2, a;
  }
  if (Kd(e) && (e = e.__vccOpts), t) {
    t = Nd(t);
    let { class: a, style: u } = t;
    a && !Ve(a) && (t.class = lt(a)), _e(u) && (/* @__PURE__ */ ho(u) && !J(u) && (u = Ue({}, u)), t.style = xn(u));
  }
  const i = Ve(e) ? 1 : Di(e) ? 128 : Yu(e) ? 64 : _e(e) ? 4 : X(e) ? 2 : 0;
  return f(
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
function Nd(e) {
  return e ? /* @__PURE__ */ ho(e) || Ri(e) ? Ue({}, e) : e : null;
}
function ms(e, t, s = !1, n = !1) {
  const { props: o, ref: l, patchFlag: i, children: a, transition: u } = e, h = t ? ts(o || {}, t) : o, g = {
    __v_isVNode: !0,
    __v_skip: !0,
    type: e.type,
    props: h,
    key: h && Fi(h),
    ref: t && t.ref ? (
      // #2078 in the case of <component :is="vnode" ref="extra"/>
      // if the vnode itself already has a ref, cloneVNode will need to merge
      // the refs so the single vnode can be set on multiple refs
      s && l ? J(l) ? l.concat(Yn(t)) : [l, Yn(t)] : Yn(t)
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
    patchFlag: t && e.type !== ce ? i === -1 ? 16 : i | 16 : i,
    dynamicProps: e.dynamicProps,
    dynamicChildren: e.dynamicChildren,
    appContext: e.appContext,
    dirs: e.dirs,
    transition: u,
    // These should technically only be non-null on mounted VNodes. However,
    // they *should* be copied for kept-alive vnodes. So we just always copy
    // them since them being non-null during a mount doesn't affect the logic as
    // they will simply be overwritten.
    component: e.component,
    suspense: e.suspense,
    ssContent: e.ssContent && ms(e.ssContent),
    ssFallback: e.ssFallback && ms(e.ssFallback),
    placeholder: e.placeholder,
    el: e.el,
    anchor: e.anchor,
    ctx: e.ctx,
    ce: e.ce
  };
  return u && n && vr(
    g,
    u.clone(g)
  ), g;
}
function _(e = " ", t = 0) {
  return y(yo, null, e, t);
}
function Ld(e, t) {
  const s = y(Jn, null, e);
  return s.staticCount = t, s;
}
function W(e = "", t = !1) {
  return t ? (C(), Te(Ot, null, e)) : y(Ot, null, e);
}
function Rt(e) {
  return e == null || typeof e == "boolean" ? y(Ot) : J(e) ? y(
    ce,
    null,
    // #3666, avoid reference pollution when reusing vnode
    e.slice()
  ) : Cn(e) ? Ft(e) : y(yo, null, String(e));
}
function Ft(e) {
  return e.el === null && e.patchFlag !== -1 || e.memo ? e : ms(e);
}
function oo(e, t) {
  let s = 0;
  const { shapeFlag: n } = e;
  if (t == null)
    t = null;
  else if (J(t))
    s = 16;
  else if (typeof t == "object")
    if (n & 65) {
      const o = t.default;
      o && (o._c && (o._d = !1), oo(e, o()), o._c && (o._d = !0));
      return;
    } else {
      s = 32;
      const o = t._;
      !o && !Ri(t) ? t._ctx = st : o === 3 && st && (st.slots._ === 1 ? t._ = 1 : (t._ = 2, e.patchFlag |= 1024));
    }
  else if (X(t)) {
    if (n & 65) {
      oo(e, { default: t });
      return;
    }
    t = { default: t, _ctx: st }, s = 32;
  } else
    t = String(t), n & 64 ? (s = 16, t = [_(t)]) : s = 8;
  e.children = t, e.shapeFlag |= s;
}
function ts(...e) {
  const t = {};
  for (let s = 0; s < e.length; s++) {
    const n = e[s];
    for (const o in n)
      if (o === "class")
        t.class !== n.class && (t.class = lt([t.class, n.class]));
      else if (o === "style")
        t.style = xn([t.style, n.style]);
      else if (lo(o)) {
        const l = t[o], i = n[o];
        i && l !== i && !(J(l) && l.includes(i)) ? t[o] = l ? [].concat(l, i) : i : i == null && l == null && // mergeProps({ 'onUpdate:modelValue': undefined }) should not retain
        // the model listener.
        !io(o) && (t[o] = i);
      } else o !== "" && (t[o] = n[o]);
  }
  return t;
}
function It(e, t, s, n = null) {
  wt(e, t, 7, [
    s,
    n
  ]);
}
const Ud = Ci();
let Dd = 0;
function Bd(e, t, s) {
  const n = e.type, o = (t ? t.appContext : e.appContext) || Ud, l = {
    uid: Dd++,
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
    scope: new lu(
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
    propsOptions: Vi(n, o),
    emitsOptions: Ei(n, o),
    // emit
    emit: null,
    // to be set immediately
    emitted: null,
    // props default value
    propsDefaults: ge,
    // inheritAttrs
    inheritAttrs: n.inheritAttrs,
    // state
    ctx: ge,
    data: ge,
    props: ge,
    attrs: ge,
    slots: ge,
    refs: ge,
    setupState: ge,
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
  return l.ctx = { _: l }, l.root = t ? t.root : l, l.emit = vd.bind(null, l), e.ce && e.ce(l), l;
}
let tt = null;
const os = () => tt || st;
let ro, nr;
{
  const e = po(), t = (s, n) => {
    let o;
    return (o = e[s]) || (o = e[s] = []), o.push(n), (l) => {
      o.length > 1 ? o.forEach((i) => i(l)) : o[0](l);
    };
  };
  ro = t(
    "__VUE_INSTANCE_SETTERS__",
    (s) => tt = s
  ), nr = t(
    "__VUE_SSR_SETTERS__",
    (s) => $s = s
  );
}
const Pn = (e) => {
  const t = tt;
  return ro(e), e.scope.on(), () => {
    e.scope.off(), ro(t);
  };
}, pl = () => {
  tt && tt.scope.off(), ro(null);
};
function Hi(e) {
  return e.vnode.shapeFlag & 4;
}
let $s = !1;
function Fd(e, t = !1, s = !1) {
  t && nr(t);
  const { props: n, children: o } = e.vnode, l = Hi(e);
  Sd(e, n, l, t), Id(e, o, s || t);
  const i = l ? Hd(e, t) : void 0;
  return t && nr(!1), i;
}
function Hd(e, t) {
  const s = e.type;
  e.accessCache = /* @__PURE__ */ Object.create(null), e.proxy = new Proxy(e.ctx, ud);
  const { setup: n } = s;
  if (n) {
    Vt();
    const o = e.setupContext = n.length > 1 ? Wd(e) : null, l = Pn(e), i = En(
      n,
      e,
      0,
      [
        e.props,
        o
      ]
    ), a = Bl(i);
    if ($t(), l(), (a || e.sp) && !Ps(e) && yr(e), a) {
      if (i.then(pl, pl), t)
        return i.then((u) => {
          ml(e, u);
        }).catch((u) => {
          In(u, e, 0);
        });
      e.asyncDep = i;
    } else
      ml(e, i);
  } else
    zi(e);
}
function ml(e, t, s) {
  X(t) ? e.type.__ssrInlineRender ? e.ssrRender = t : e.render = t : _e(t) && (e.setupState = ui(t)), zi(e);
}
function zi(e, t, s) {
  const n = e.type;
  e.render || (e.render = n.render || Mt);
  {
    const o = Pn(e);
    Vt();
    try {
      dd(e);
    } finally {
      $t(), o();
    }
  }
}
const zd = {
  get(e, t) {
    return et(e, "get", ""), e[t];
  }
};
function Wd(e) {
  const t = (s) => {
    e.exposed = s || {};
  };
  return {
    attrs: new Proxy(e.attrs, zd),
    slots: e.slots,
    emit: e.emit,
    expose: t
  };
}
function xo(e) {
  return e.exposed ? e.exposeProxy || (e.exposeProxy = new Proxy(ui(Eu(e.exposed)), {
    get(t, s) {
      if (s in t)
        return t[s];
      if (s in vn)
        return vn[s](e);
    },
    has(t, s) {
      return s in t || s in vn;
    }
  })) : e.proxy;
}
function Kd(e) {
  return X(e) && "__vccOpts" in e;
}
const xe = (e, t) => /* @__PURE__ */ Uu(e, t, $s);
function Fo(e, t, s) {
  try {
    no(-1);
    const n = arguments.length;
    return n === 2 ? _e(t) && !J(t) ? Cn(t) ? y(e, null, [t]) : y(e, t) : y(e, null, t) : (n > 3 ? s = Array.prototype.slice.call(arguments, 2) : n === 3 && Cn(s) && (s = [s]), y(e, t, s));
  } finally {
    no(1);
  }
}
const qd = "3.5.39";
/**
* @vue/runtime-dom v3.5.39
* (c) 2018-present Yuxi (Evan) You and Vue contributors
* @license MIT
**/
let or;
const gl = typeof window < "u" && window.trustedTypes;
if (gl)
  try {
    or = /* @__PURE__ */ gl.createPolicy("vue", {
      createHTML: (e) => e
    });
  } catch {
  }
const Wi = or ? (e) => or.createHTML(e) : (e) => e, Gd = "http://www.w3.org/2000/svg", Jd = "http://www.w3.org/1998/Math/MathML", Bt = typeof document < "u" ? document : null, hl = Bt && /* @__PURE__ */ Bt.createElement("template"), Yd = {
  insert: (e, t, s) => {
    t.insertBefore(e, s || null);
  },
  remove: (e) => {
    const t = e.parentNode;
    t && t.removeChild(e);
  },
  createElement: (e, t, s, n) => {
    const o = t === "svg" ? Bt.createElementNS(Gd, e) : t === "mathml" ? Bt.createElementNS(Jd, e) : s ? Bt.createElement(e, { is: s }) : Bt.createElement(e);
    return e === "select" && n && n.multiple != null && o.setAttribute("multiple", n.multiple), o;
  },
  createText: (e) => Bt.createTextNode(e),
  createComment: (e) => Bt.createComment(e),
  setText: (e, t) => {
    e.nodeValue = t;
  },
  setElementText: (e, t) => {
    e.textContent = t;
  },
  parentNode: (e) => e.parentNode,
  nextSibling: (e) => e.nextSibling,
  querySelector: (e) => Bt.querySelector(e),
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
      hl.innerHTML = Wi(
        n === "svg" ? `<svg>${e}</svg>` : n === "mathml" ? `<math>${e}</math>` : e
      );
      const a = hl.content;
      if (n === "svg" || n === "mathml") {
        const u = a.firstChild;
        for (; u.firstChild; )
          a.appendChild(u.firstChild);
        a.removeChild(u);
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
}, Qd = /* @__PURE__ */ Symbol("_vtc");
function Zd(e, t, s) {
  const n = e[Qd];
  n && (t = (t ? [t, ...n] : [...n]).join(" ")), t == null ? e.removeAttribute("class") : s ? e.setAttribute("class", t) : e.className = t;
}
const bl = /* @__PURE__ */ Symbol("_vod"), Xd = /* @__PURE__ */ Symbol("_vsh"), ec = /* @__PURE__ */ Symbol(""), tc = /(?:^|;)\s*display\s*:/;
function sc(e, t, s) {
  const n = e.style, o = Ve(s);
  let l = !1;
  if (s && !o) {
    if (t)
      if (Ve(t))
        for (const i of t.split(";")) {
          const a = i.slice(0, i.indexOf(":")).trim();
          s[a] == null && dn(n, a, "");
        }
      else
        for (const i in t)
          s[i] == null && dn(n, i, "");
    for (const i in s) {
      i === "display" && (l = !0);
      const a = s[i];
      a != null ? oc(
        e,
        i,
        !Ve(t) && t ? t[i] : void 0,
        a
      ) || dn(n, i, a) : dn(n, i, "");
    }
  } else if (o) {
    if (t !== s) {
      const i = n[ec];
      i && (s += ";" + i), n.cssText = s, l = tc.test(s);
    }
  } else t && e.removeAttribute("style");
  bl in e && (e[bl] = l ? n.display : "", e[Xd] && (n.display = "none"));
}
const vl = /\s*!important$/;
function dn(e, t, s) {
  if (J(s))
    s.forEach((n) => dn(e, t, n));
  else if (s == null && (s = ""), t.startsWith("--"))
    e.setProperty(t, s);
  else {
    const n = nc(e, t);
    vl.test(s) ? e.setProperty(
      ct(n),
      s.replace(vl, ""),
      "important"
    ) : e[n] = s;
  }
}
const yl = ["Webkit", "Moz", "ms"], Ho = {};
function nc(e, t) {
  const s = Ho[t];
  if (s)
    return s;
  let n = Ge(t);
  if (n !== "filter" && n in e)
    return Ho[t] = n;
  n = Hl(n);
  for (let o = 0; o < yl.length; o++) {
    const l = yl[o] + n;
    if (l in e)
      return Ho[t] = l;
  }
  return t;
}
function oc(e, t, s, n) {
  return e.tagName === "TEXTAREA" && (t === "width" || t === "height") && Ve(n) && s === n;
}
const xl = "http://www.w3.org/1999/xlink";
function _l(e, t, s, n, o, l = ou(t)) {
  n && t.startsWith("xlink:") ? s == null ? e.removeAttributeNS(xl, t.slice(6, t.length)) : e.setAttributeNS(xl, t, s) : s == null || l && !Wl(s) ? e.removeAttribute(t) : e.setAttribute(
    t,
    l ? "" : ht(s) ? String(s) : s
  );
}
function wl(e, t, s, n, o) {
  if (t === "innerHTML" || t === "textContent") {
    s != null && (e[t] = t === "innerHTML" ? Wi(s) : s);
    return;
  }
  const l = e.tagName;
  if (t === "value" && l !== "PROGRESS" && // custom elements may use _value internally
  !l.includes("-")) {
    const a = l === "OPTION" ? e.getAttribute("value") || "" : e.value, u = s == null ? (
      // #11647: value should be set as empty string for null and undefined,
      // but <input type="checkbox"> should be set as 'on'.
      e.type === "checkbox" ? "on" : ""
    ) : String(s);
    (a !== u || !("_value" in e)) && (e.value = u), s == null && e.removeAttribute(t), e._value = s;
    return;
  }
  let i = !1;
  if (s === "" || s == null) {
    const a = typeof e[t];
    a === "boolean" ? s = Wl(s) : s == null && a === "string" ? (s = "", i = !0) : a === "number" && (s = 0, i = !0);
  }
  try {
    e[t] = s;
  } catch {
  }
  i && e.removeAttribute(o || t);
}
function Wt(e, t, s, n) {
  e.addEventListener(t, s, n);
}
function rc(e, t, s, n) {
  e.removeEventListener(t, s, n);
}
const kl = /* @__PURE__ */ Symbol("_vei");
function lc(e, t, s, n, o = null) {
  const l = e[kl] || (e[kl] = {}), i = l[t];
  if (n && i)
    i.value = n;
  else {
    const [a, u] = uc(t);
    if (n) {
      const h = l[t] = fc(
        n,
        o
      );
      Wt(e, a, h, u);
    } else i && (rc(e, a, i, u), l[t] = void 0);
  }
}
const ic = /(Once|Passive|Capture)$/, ac = /^on:?(?:Once|Passive|Capture)$/;
function uc(e) {
  let t, s;
  for (; (s = e.match(ic)) && !ac.test(e); )
    t || (t = {}), e = e.slice(0, e.length - s[1].length), t[s[1].toLowerCase()] = !0;
  return [e[2] === ":" ? e.slice(3) : ct(e.slice(2)), t];
}
let zo = 0;
const dc = /* @__PURE__ */ Promise.resolve(), cc = () => zo || (dc.then(() => zo = 0), zo = Date.now());
function fc(e, t) {
  const s = (n) => {
    if (!n._vts)
      n._vts = Date.now();
    else if (n._vts <= s.attached)
      return;
    const o = s.value;
    if (J(o)) {
      const l = n.stopImmediatePropagation;
      n.stopImmediatePropagation = () => {
        l.call(n), n._stopped = !0;
      };
      const i = o.slice(), a = [n];
      for (let u = 0; u < i.length && !n._stopped; u++) {
        const h = i[u];
        h && wt(
          h,
          t,
          5,
          a
        );
      }
    } else
      wt(
        o,
        t,
        5,
        [n]
      );
  };
  return s.value = e, s.attached = cc(), s;
}
const Sl = (e) => e.charCodeAt(0) === 111 && e.charCodeAt(1) === 110 && // lowercase letter
e.charCodeAt(2) > 96 && e.charCodeAt(2) < 123, pc = (e, t, s, n, o, l) => {
  const i = o === "svg";
  t === "class" ? Zd(e, n, i) : t === "style" ? sc(e, s, n) : lo(t) ? io(t) || lc(e, t, s, n, l) : (t[0] === "." ? (t = t.slice(1), !0) : t[0] === "^" ? (t = t.slice(1), !1) : mc(e, t, n, i)) ? (wl(e, t, n), !e.tagName.includes("-") && (t === "value" || t === "checked" || t === "selected") && _l(e, t, n, i, l, t !== "value")) : /* #11081 force set props for possible async custom element */ e._isVueCE && // #12408 check if it's declared prop or it's async custom element
  (gc(e, t) || // @ts-expect-error _def is private
  e._def.__asyncLoader && (/[A-Z]/.test(t) || !Ve(n))) ? wl(e, Ge(t), n, l, t) : (t === "true-value" ? e._trueValue = n : t === "false-value" && (e._falseValue = n), _l(e, t, n, i));
};
function mc(e, t, s, n) {
  if (n)
    return !!(t === "innerHTML" || t === "textContent" || t in e && Sl(t) && X(s));
  if (t === "spellcheck" || t === "draggable" || t === "translate" || t === "autocorrect" || t === "sandbox" && e.tagName === "IFRAME" || t === "form" || t === "list" && e.tagName === "INPUT" || t === "type" && e.tagName === "TEXTAREA")
    return !1;
  if (t === "width" || t === "height") {
    const o = e.tagName;
    if (o === "IMG" || o === "VIDEO" || o === "CANVAS" || o === "SOURCE")
      return !1;
  }
  return Sl(t) && Ve(s) ? !1 : t in e;
}
function gc(e, t) {
  const s = (
    // @ts-expect-error _def is private
    e._def.props
  );
  if (!s)
    return !1;
  const n = Ge(t);
  return Array.isArray(s) ? s.some((o) => Ge(o) === n) : Object.keys(s).some((o) => Ge(o) === n);
}
const Cl = {};
// @__NO_SIDE_EFFECTS__
function hc(e, t, s) {
  let n = /* @__PURE__ */ He(e, t);
  ao(n) && (n = Ue({}, n, t));
  class o extends Sr {
    constructor(i) {
      super(n, i, s);
    }
  }
  return o.def = n, o;
}
const bc = typeof HTMLElement < "u" ? HTMLElement : class {
};
class Sr extends bc {
  constructor(t, s = {}, n = Rl) {
    super(), this._def = t, this._props = s, this._createApp = n, this._isVueCE = !0, this._instance = null, this._app = null, this._nonce = this._def.nonce, this._connected = !1, this._resolved = !1, this._patching = !1, this._dirty = !1, this._numberProps = null, this._styleChildren = /* @__PURE__ */ new WeakSet(), this._styleAnchors = /* @__PURE__ */ new WeakMap(), this._ob = null, this.shadowRoot && n !== Rl ? this._root = this.shadowRoot : t.shadowRoot !== !1 ? (this.attachShadow(
      Ue({}, t.shadowRootOptions, {
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
      if (t instanceof Sr) {
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
    this._connected = !1, Tn(() => {
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
      if (l && !J(l))
        for (const u in l) {
          const h = l[u];
          (h === Number || h && h.type === Number) && (u in this._props && (this._props[u] = Qr(this._props[u])), (a || (a = /* @__PURE__ */ Object.create(null)))[Ge(u)] = !0);
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
        ye(this, n) || Object.defineProperty(this, n, {
          // unwrap ref to be consistent with public instance behavior
          get: () => p(s[n])
        });
  }
  _resolveProps(t) {
    const { props: s } = t, n = J(s) ? s : Object.keys(s || {});
    for (const o of Object.keys(this))
      o[0] !== "_" && n.includes(o) && this._setProp(o, this[o]);
    for (const o of n.map(Ge))
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
    let n = s ? this.getAttribute(t) : Cl;
    const o = Ge(t);
    s && this._numberProps && this._numberProps[o] && (n = Qr(n)), this._setProp(o, n, !1, !0);
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
    if (s !== this._props[t] && (this._dirty = !0, s === Cl ? delete this._props[t] : (this._props[t] = s, t === "key" && this._app && (this._app._ceVNode.key = s)), o && this._instance && this._update(), n)) {
      const l = this._ob;
      l && (this._processMutations(l.takeRecords()), l.disconnect()), s === !0 ? this.setAttribute(ct(t), "") : typeof s == "string" || typeof s == "number" ? this.setAttribute(ct(t), s + "") : s || this.removeAttribute(ct(t)), l && l.observe(this, { attributes: !0 });
    }
  }
  _update() {
    const t = this._createVNode();
    this._app && (t.appContext = this._app._context), Ec(t, this._root);
  }
  _createVNode() {
    const t = {};
    this.shadowRoot || (t.onVnodeMounted = t.onVnodeUpdated = this._renderSlots.bind(this));
    const s = y(this._def, Ue(t, this._props));
    return this._instance || (s.ce = (n) => {
      this._instance = n, n.ce = this, n.isCE = !0;
      const o = (l, i) => {
        this.dispatchEvent(
          new CustomEvent(
            l,
            ao(i[0]) ? Ue({ detail: i }, i[0]) : { detail: i }
          )
        );
      };
      n.emit = (l, ...i) => {
        o(l, i), ct(l) !== l && o(ct(l), i);
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
    for (let u = t.length - 1; u >= 0; u--) {
      const h = document.createElement("style");
      o && h.setAttribute("nonce", o), h.textContent = t[u], l.insertBefore(h, a || i), a = h, u === 0 && (n || this._styleAnchors.set(this._def, h), s && this._styleAnchors.set(s, h));
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
        for (const u of i) {
          if (s && u.nodeType === 1) {
            const h = s + "-s", g = document.createTreeWalker(u, 1);
            u.setAttribute(h, "");
            let x;
            for (; x = g.nextNode(); )
              x.setAttribute(h, "");
          }
          a.insertBefore(u, o);
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
const ss = (e) => {
  const t = e.props["onUpdate:modelValue"] || !1;
  return J(t) ? (s) => Gn(t, s) : t;
};
function vc(e) {
  e.target.composing = !0;
}
function Al(e) {
  const t = e.target;
  t.composing && (t.composing = !1, t.dispatchEvent(new Event("input")));
}
const yt = /* @__PURE__ */ Symbol("_assign");
function El(e, t, s) {
  return t && (e = e.trim()), s && (e = fo(e)), e;
}
const rr = {
  created(e, { modifiers: { lazy: t, trim: s, number: n } }, o) {
    e[yt] = ss(o);
    const l = n || o.props && o.props.type === "number";
    Wt(e, t ? "change" : "input", (i) => {
      i.target.composing || e[yt](El(e.value, s, l));
    }), (s || l) && Wt(e, "change", () => {
      e.value = El(e.value, s, l);
    }), t || (Wt(e, "compositionstart", vc), Wt(e, "compositionend", Al), Wt(e, "change", Al));
  },
  // set value on mounted so it's after min/max for type="range"
  mounted(e, { value: t }) {
    e.value = t ?? "";
  },
  beforeUpdate(e, { value: t, oldValue: s, modifiers: { lazy: n, trim: o, number: l } }, i) {
    if (e[yt] = ss(i), e.composing) return;
    const a = (l || e.type === "number") && !/^0\d/.test(e.value) ? fo(e.value) : e.value, u = t ?? "";
    if (a === u)
      return;
    const h = e.getRootNode();
    (h instanceof Document || h instanceof ShadowRoot) && h.activeElement === e && e.type !== "range" && (n && t === s || o && e.value.trim() === u) || (e.value = u);
  }
}, yc = {
  // #4096 array checkboxes need to be deep traversed
  deep: !0,
  created(e, t, s) {
    e[yt] = ss(s), Wt(e, "change", () => {
      const n = e._modelValue, o = Os(e), l = e.checked, i = e[yt];
      if (J(n)) {
        const a = ur(n, o), u = a !== -1;
        if (l && !u)
          i(n.concat(o));
        else if (!l && u) {
          const h = [...n];
          h.splice(a, 1), i(h);
        }
      } else if (js(n)) {
        const a = new Set(n);
        l ? a.add(o) : a.delete(o), i(a);
      } else
        i(qi(e, l));
    });
  },
  // set initial checked on mount to wait for true-value/false-value
  mounted: Il,
  beforeUpdate(e, t, s) {
    e[yt] = ss(s), Il(e, t, s);
  }
};
function Il(e, { value: t, oldValue: s }, n) {
  e._modelValue = t;
  let o;
  if (J(t))
    o = ur(t, n.props.value) > -1;
  else if (js(t))
    o = t.has(n.props.value);
  else {
    if (t === s) return;
    o = es(t, qi(e, !0));
  }
  e.checked !== o && (e.checked = o);
}
const xc = {
  created(e, { value: t }, s) {
    e.checked = es(t, s.props.value), e[yt] = ss(s), Wt(e, "change", () => {
      e[yt](Os(e));
    });
  },
  beforeUpdate(e, { value: t, oldValue: s }, n) {
    e[yt] = ss(n), t !== s && (e.checked = es(t, n.props.value));
  }
}, Ki = {
  // <select multiple> value need to be deep traversed
  deep: !0,
  created(e, { value: t, modifiers: { number: s } }, n) {
    const o = js(t);
    Wt(e, "change", () => {
      const l = Array.prototype.filter.call(e.options, (i) => i.selected).map(
        (i) => s ? fo(Os(i)) : Os(i)
      );
      e[yt](
        e.multiple ? o ? new Set(l) : l : l[0]
      ), e._assigning = !0, Tn(() => {
        e._assigning = !1;
      });
    }), e[yt] = ss(n);
  },
  // set value in mounted & updated because <select> relies on its children
  // <option>s.
  mounted(e, { value: t }) {
    Tl(e, t);
  },
  beforeUpdate(e, t, s) {
    e[yt] = ss(s);
  },
  updated(e, { value: t }) {
    e._assigning || Tl(e, t);
  }
};
function Tl(e, t) {
  const s = e.multiple, n = J(t);
  if (!(s && !n && !js(t))) {
    for (let o = 0, l = e.options.length; o < l; o++) {
      const i = e.options[o], a = Os(i);
      if (s)
        if (n) {
          const u = typeof a;
          u === "string" || u === "number" ? i.selected = t.some((h) => String(h) === String(a)) : i.selected = ur(t, a) > -1;
        } else
          i.selected = t.has(a);
      else if (es(Os(i), t)) {
        e.selectedIndex !== o && (e.selectedIndex = o);
        return;
      }
    }
    !s && e.selectedIndex !== -1 && (e.selectedIndex = -1);
  }
}
function Os(e) {
  return "_value" in e ? e._value : e.value;
}
function qi(e, t) {
  const s = t ? "_trueValue" : "_falseValue";
  return s in e ? e[s] : t;
}
const _c = {
  created(e, t, s) {
    Wn(e, t, s, null, "created");
  },
  mounted(e, t, s) {
    Wn(e, t, s, null, "mounted");
  },
  beforeUpdate(e, t, s, n) {
    Wn(e, t, s, n, "beforeUpdate");
  },
  updated(e, t, s, n) {
    Wn(e, t, s, n, "updated");
  }
};
function wc(e, t) {
  switch (e) {
    case "SELECT":
      return Ki;
    case "TEXTAREA":
      return rr;
    default:
      switch (t) {
        case "checkbox":
          return yc;
        case "radio":
          return xc;
        default:
          return rr;
      }
  }
}
function Wn(e, t, s, n, o) {
  const i = wc(
    e.tagName,
    s.props && s.props.type
  )[o];
  i && i(e, t, s, n);
}
const kc = ["ctrl", "shift", "alt", "meta"], Sc = {
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
  exact: (e, t) => kc.some((s) => e[`${s}Key`] && !t.includes(s))
}, cn = (e, t) => {
  if (!e) return e;
  const s = e._withMods || (e._withMods = {}), n = t.join(".");
  return s[n] || (s[n] = ((o, ...l) => {
    for (let i = 0; i < t.length; i++) {
      const a = Sc[t[i]];
      if (a && a(o, t)) return;
    }
    return e(o, ...l);
  }));
}, Cc = {
  esc: "escape",
  space: " ",
  up: "arrow-up",
  left: "arrow-left",
  right: "arrow-right",
  down: "arrow-down",
  delete: "backspace"
}, fn = (e, t) => {
  const s = e._withKeys || (e._withKeys = {}), n = t.join(".");
  return s[n] || (s[n] = ((o) => {
    if (!("key" in o))
      return;
    const l = ct(o.key);
    if (t.some(
      (i) => i === l || Cc[i] === l
    ))
      return e(o);
  }));
}, Ac = /* @__PURE__ */ Ue({ patchProp: pc }, Yd);
let Pl;
function Gi() {
  return Pl || (Pl = Pd(Ac));
}
const Ec = ((...e) => {
  Gi().render(...e);
}), Rl = ((...e) => {
  const t = Gi().createApp(...e), { mount: s } = t;
  return t.mount = (n) => {
    const o = Tc(n);
    if (!o) return;
    const l = t._component;
    !X(l) && !l.render && !l.template && (l.template = o.innerHTML), o.nodeType === 1 && (o.textContent = "");
    const i = s(o, !1, Ic(o));
    return o instanceof Element && (o.removeAttribute("v-cloak"), o.setAttribute("data-v-app", "")), i;
  }, t;
});
function Ic(e) {
  if (e instanceof SVGElement)
    return "svg";
  if (typeof MathMLElement == "function" && e instanceof MathMLElement)
    return "mathml";
}
function Tc(e) {
  return Ve(e) ? document.querySelector(e) : e;
}
function Ji(e) {
  var t, s, n = "";
  if (typeof e == "string" || typeof e == "number") n += e;
  else if (typeof e == "object") if (Array.isArray(e)) {
    var o = e.length;
    for (t = 0; t < o; t++) e[t] && (s = Ji(e[t])) && (n && (n += " "), n += s);
  } else for (s in e) e[s] && (n && (n += " "), n += s);
  return n;
}
function Yi() {
  for (var e, t, s = 0, n = "", o = arguments.length; s < o; s++) (e = arguments[s]) && (t = Ji(e)) && (n && (n += " "), n += t);
  return n;
}
const Ml = (e) => typeof e == "boolean" ? `${e}` : e === 0 ? "0" : e, Vl = Yi, Qi = (e, t) => (s) => {
  var n;
  if ((t == null ? void 0 : t.variants) == null) return Vl(e, s == null ? void 0 : s.class, s == null ? void 0 : s.className);
  const { variants: o, defaultVariants: l } = t, i = Object.keys(o).map((h) => {
    const g = s == null ? void 0 : s[h], x = l == null ? void 0 : l[h];
    if (g === null) return null;
    const A = Ml(g) || Ml(x);
    return o[h][A];
  }), a = s && Object.entries(s).reduce((h, g) => {
    let [x, A] = g;
    return A === void 0 || (h[x] = A), h;
  }, {}), u = t == null || (n = t.compoundVariants) === null || n === void 0 ? void 0 : n.reduce((h, g) => {
    let { class: x, className: A, ...k } = g;
    return Object.entries(k).every(($) => {
      let [v, H] = $;
      return Array.isArray(H) ? H.includes({
        ...l,
        ...a
      }[v]) : {
        ...l,
        ...a
      }[v] === H;
    }) ? [
      ...h,
      x,
      A
    ] : h;
  }, []);
  return Vl(e, i, u, s == null ? void 0 : s.class, s == null ? void 0 : s.className);
}, Pc = Qi(
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
), Cr = "-", Rc = (e) => {
  const t = Vc(e), {
    conflictingClassGroups: s,
    conflictingClassGroupModifiers: n
  } = e;
  return {
    getClassGroupId: (i) => {
      const a = i.split(Cr);
      return a[0] === "" && a.length !== 1 && a.shift(), Zi(a, t) || Mc(i);
    },
    getConflictingClassGroupIds: (i, a) => {
      const u = s[i] || [];
      return a && n[i] ? [...u, ...n[i]] : u;
    }
  };
}, Zi = (e, t) => {
  var i;
  if (e.length === 0)
    return t.classGroupId;
  const s = e[0], n = t.nextPart.get(s), o = n ? Zi(e.slice(1), n) : void 0;
  if (o)
    return o;
  if (t.validators.length === 0)
    return;
  const l = e.join(Cr);
  return (i = t.validators.find(({
    validator: a
  }) => a(l))) == null ? void 0 : i.classGroupId;
}, $l = /^\[(.+)\]$/, Mc = (e) => {
  if ($l.test(e)) {
    const t = $l.exec(e)[1], s = t == null ? void 0 : t.substring(0, t.indexOf(":"));
    if (s)
      return "arbitrary.." + s;
  }
}, Vc = (e) => {
  const {
    theme: t,
    prefix: s
  } = e, n = {
    nextPart: /* @__PURE__ */ new Map(),
    validators: []
  };
  return Oc(Object.entries(e.classGroups), s).forEach(([l, i]) => {
    lr(i, n, l, t);
  }), n;
}, lr = (e, t, s, n) => {
  e.forEach((o) => {
    if (typeof o == "string") {
      const l = o === "" ? t : Ol(t, o);
      l.classGroupId = s;
      return;
    }
    if (typeof o == "function") {
      if ($c(o)) {
        lr(o(n), t, s, n);
        return;
      }
      t.validators.push({
        validator: o,
        classGroupId: s
      });
      return;
    }
    Object.entries(o).forEach(([l, i]) => {
      lr(i, Ol(t, l), s, n);
    });
  });
}, Ol = (e, t) => {
  let s = e;
  return t.split(Cr).forEach((n) => {
    s.nextPart.has(n) || s.nextPart.set(n, {
      nextPart: /* @__PURE__ */ new Map(),
      validators: []
    }), s = s.nextPart.get(n);
  }), s;
}, $c = (e) => e.isThemeGetter, Oc = (e, t) => t ? e.map(([s, n]) => {
  const o = n.map((l) => typeof l == "string" ? t + l : typeof l == "object" ? Object.fromEntries(Object.entries(l).map(([i, a]) => [t + i, a])) : l);
  return [s, o];
}) : e, jc = (e) => {
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
}, Xi = "!", Nc = (e) => {
  const {
    separator: t,
    experimentalParseClassName: s
  } = e, n = t.length === 1, o = t[0], l = t.length, i = (a) => {
    const u = [];
    let h = 0, g = 0, x;
    for (let H = 0; H < a.length; H++) {
      let z = a[H];
      if (h === 0) {
        if (z === o && (n || a.slice(H, H + l) === t)) {
          u.push(a.slice(g, H)), g = H + l;
          continue;
        }
        if (z === "/") {
          x = H;
          continue;
        }
      }
      z === "[" ? h++ : z === "]" && h--;
    }
    const A = u.length === 0 ? a : a.substring(g), k = A.startsWith(Xi), $ = k ? A.substring(1) : A, v = x && x > g ? x - g : void 0;
    return {
      modifiers: u,
      hasImportantModifier: k,
      baseClassName: $,
      maybePostfixModifierPosition: v
    };
  };
  return s ? (a) => s({
    className: a,
    parseClassName: i
  }) : i;
}, Lc = (e) => {
  if (e.length <= 1)
    return e;
  const t = [];
  let s = [];
  return e.forEach((n) => {
    n[0] === "[" ? (t.push(...s.sort(), n), s = []) : s.push(n);
  }), t.push(...s.sort()), t;
}, Uc = (e) => ({
  cache: jc(e.cacheSize),
  parseClassName: Nc(e),
  ...Rc(e)
}), Dc = /\s+/, Bc = (e, t) => {
  const {
    parseClassName: s,
    getClassGroupId: n,
    getConflictingClassGroupIds: o
  } = t, l = [], i = e.trim().split(Dc);
  let a = "";
  for (let u = i.length - 1; u >= 0; u -= 1) {
    const h = i[u], {
      modifiers: g,
      hasImportantModifier: x,
      baseClassName: A,
      maybePostfixModifierPosition: k
    } = s(h);
    let $ = !!k, v = n($ ? A.substring(0, k) : A);
    if (!v) {
      if (!$) {
        a = h + (a.length > 0 ? " " + a : a);
        continue;
      }
      if (v = n(A), !v) {
        a = h + (a.length > 0 ? " " + a : a);
        continue;
      }
      $ = !1;
    }
    const H = Lc(g).join(":"), z = x ? H + Xi : H, D = z + v;
    if (l.includes(D))
      continue;
    l.push(D);
    const q = o(v, $);
    for (let U = 0; U < q.length; ++U) {
      const Z = q[U];
      l.push(z + Z);
    }
    a = h + (a.length > 0 ? " " + a : a);
  }
  return a;
};
function Fc() {
  let e = 0, t, s, n = "";
  for (; e < arguments.length; )
    (t = arguments[e++]) && (s = ea(t)) && (n && (n += " "), n += s);
  return n;
}
const ea = (e) => {
  if (typeof e == "string")
    return e;
  let t, s = "";
  for (let n = 0; n < e.length; n++)
    e[n] && (t = ea(e[n])) && (s && (s += " "), s += t);
  return s;
};
function Hc(e, ...t) {
  let s, n, o, l = i;
  function i(u) {
    const h = t.reduce((g, x) => x(g), e());
    return s = Uc(h), n = s.cache.get, o = s.cache.set, l = a, a(u);
  }
  function a(u) {
    const h = n(u);
    if (h)
      return h;
    const g = Bc(u, s);
    return o(u, g), g;
  }
  return function() {
    return l(Fc.apply(null, arguments));
  };
}
const Ie = (e) => {
  const t = (s) => s[e] || [];
  return t.isThemeGetter = !0, t;
}, ta = /^\[(?:([a-z-]+):)?(.+)\]$/i, zc = /^\d+\/\d+$/, Wc = /* @__PURE__ */ new Set(["px", "full", "screen"]), Kc = /^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/, qc = /\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/, Gc = /^(rgba?|hsla?|hwb|(ok)?(lab|lch)|color-mix)\(.+\)$/, Jc = /^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/, Yc = /^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/, Ut = (e) => Ms(e) || Wc.has(e) || zc.test(e), Qt = (e) => Ns(e, "length", of), Ms = (e) => !!e && !Number.isNaN(Number(e)), Wo = (e) => Ns(e, "number", Ms), rn = (e) => !!e && Number.isInteger(Number(e)), Qc = (e) => e.endsWith("%") && Ms(e.slice(0, -1)), se = (e) => ta.test(e), Zt = (e) => Kc.test(e), Zc = /* @__PURE__ */ new Set(["length", "size", "percentage"]), Xc = (e) => Ns(e, Zc, sa), ef = (e) => Ns(e, "position", sa), tf = /* @__PURE__ */ new Set(["image", "url"]), sf = (e) => Ns(e, tf, lf), nf = (e) => Ns(e, "", rf), ln = () => !0, Ns = (e, t, s) => {
  const n = ta.exec(e);
  return n ? n[1] ? typeof t == "string" ? n[1] === t : t.has(n[1]) : s(n[2]) : !1;
}, of = (e) => (
  // `colorFunctionRegex` check is necessary because color functions can have percentages in them which which would be incorrectly classified as lengths.
  // For example, `hsl(0 0% 0%)` would be classified as a length without this check.
  // I could also use lookbehind assertion in `lengthUnitRegex` but that isn't supported widely enough.
  qc.test(e) && !Gc.test(e)
), sa = () => !1, rf = (e) => Jc.test(e), lf = (e) => Yc.test(e), af = () => {
  const e = Ie("colors"), t = Ie("spacing"), s = Ie("blur"), n = Ie("brightness"), o = Ie("borderColor"), l = Ie("borderRadius"), i = Ie("borderSpacing"), a = Ie("borderWidth"), u = Ie("contrast"), h = Ie("grayscale"), g = Ie("hueRotate"), x = Ie("invert"), A = Ie("gap"), k = Ie("gradientColorStops"), $ = Ie("gradientColorStopPositions"), v = Ie("inset"), H = Ie("margin"), z = Ie("opacity"), D = Ie("padding"), q = Ie("saturate"), U = Ie("scale"), Z = Ie("sepia"), $e = Ie("skew"), K = Ie("space"), te = Ie("translate"), Oe = () => ["auto", "contain", "none"], we = () => ["auto", "hidden", "clip", "visible", "scroll"], Me = () => ["auto", se, t], ae = () => [se, t], he = () => ["", Ut, Qt], Je = () => ["auto", Ms, se], ft = () => ["bottom", "center", "left", "left-bottom", "left-top", "right", "right-bottom", "right-top", "top"], Ce = () => ["solid", "dashed", "dotted", "double", "none"], fe = () => ["normal", "multiply", "screen", "overlay", "darken", "lighten", "color-dodge", "color-burn", "hard-light", "soft-light", "difference", "exclusion", "hue", "saturation", "color", "luminosity"], ne = () => ["start", "end", "center", "between", "around", "evenly", "stretch"], Ae = () => ["", "0", se], Ye = () => ["auto", "avoid", "all", "avoid-page", "page", "left", "right", "column"], je = () => [Ms, se];
  return {
    cacheSize: 500,
    separator: ":",
    theme: {
      colors: [ln],
      spacing: [Ut, Qt],
      blur: ["none", "", Zt, se],
      brightness: je(),
      borderColor: [e],
      borderRadius: ["none", "", "full", Zt, se],
      borderSpacing: ae(),
      borderWidth: he(),
      contrast: je(),
      grayscale: Ae(),
      hueRotate: je(),
      invert: Ae(),
      gap: ae(),
      gradientColorStops: [e],
      gradientColorStopPositions: [Qc, Qt],
      inset: Me(),
      margin: Me(),
      opacity: je(),
      padding: ae(),
      saturate: je(),
      scale: je(),
      sepia: Ae(),
      skew: je(),
      space: ae(),
      translate: ae()
    },
    classGroups: {
      // Layout
      /**
       * Aspect Ratio
       * @see https://tailwindcss.com/docs/aspect-ratio
       */
      aspect: [{
        aspect: ["auto", "square", "video", se]
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
        columns: [Zt]
      }],
      /**
       * Break After
       * @see https://tailwindcss.com/docs/break-after
       */
      "break-after": [{
        "break-after": Ye()
      }],
      /**
       * Break Before
       * @see https://tailwindcss.com/docs/break-before
       */
      "break-before": [{
        "break-before": Ye()
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
        object: [...ft(), se]
      }],
      /**
       * Overflow
       * @see https://tailwindcss.com/docs/overflow
       */
      overflow: [{
        overflow: we()
      }],
      /**
       * Overflow X
       * @see https://tailwindcss.com/docs/overflow
       */
      "overflow-x": [{
        "overflow-x": we()
      }],
      /**
       * Overflow Y
       * @see https://tailwindcss.com/docs/overflow
       */
      "overflow-y": [{
        "overflow-y": we()
      }],
      /**
       * Overscroll Behavior
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      overscroll: [{
        overscroll: Oe()
      }],
      /**
       * Overscroll Behavior X
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      "overscroll-x": [{
        "overscroll-x": Oe()
      }],
      /**
       * Overscroll Behavior Y
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      "overscroll-y": [{
        "overscroll-y": Oe()
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
        inset: [v]
      }],
      /**
       * Right / Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      "inset-x": [{
        "inset-x": [v]
      }],
      /**
       * Top / Bottom
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      "inset-y": [{
        "inset-y": [v]
      }],
      /**
       * Start
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      start: [{
        start: [v]
      }],
      /**
       * End
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      end: [{
        end: [v]
      }],
      /**
       * Top
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      top: [{
        top: [v]
      }],
      /**
       * Right
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      right: [{
        right: [v]
      }],
      /**
       * Bottom
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      bottom: [{
        bottom: [v]
      }],
      /**
       * Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      left: [{
        left: [v]
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
        z: ["auto", rn, se]
      }],
      // Flexbox and Grid
      /**
       * Flex Basis
       * @see https://tailwindcss.com/docs/flex-basis
       */
      basis: [{
        basis: Me()
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
        flex: ["1", "auto", "initial", "none", se]
      }],
      /**
       * Flex Grow
       * @see https://tailwindcss.com/docs/flex-grow
       */
      grow: [{
        grow: Ae()
      }],
      /**
       * Flex Shrink
       * @see https://tailwindcss.com/docs/flex-shrink
       */
      shrink: [{
        shrink: Ae()
      }],
      /**
       * Order
       * @see https://tailwindcss.com/docs/order
       */
      order: [{
        order: ["first", "last", "none", rn, se]
      }],
      /**
       * Grid Template Columns
       * @see https://tailwindcss.com/docs/grid-template-columns
       */
      "grid-cols": [{
        "grid-cols": [ln]
      }],
      /**
       * Grid Column Start / End
       * @see https://tailwindcss.com/docs/grid-column
       */
      "col-start-end": [{
        col: ["auto", {
          span: ["full", rn, se]
        }, se]
      }],
      /**
       * Grid Column Start
       * @see https://tailwindcss.com/docs/grid-column
       */
      "col-start": [{
        "col-start": Je()
      }],
      /**
       * Grid Column End
       * @see https://tailwindcss.com/docs/grid-column
       */
      "col-end": [{
        "col-end": Je()
      }],
      /**
       * Grid Template Rows
       * @see https://tailwindcss.com/docs/grid-template-rows
       */
      "grid-rows": [{
        "grid-rows": [ln]
      }],
      /**
       * Grid Row Start / End
       * @see https://tailwindcss.com/docs/grid-row
       */
      "row-start-end": [{
        row: ["auto", {
          span: [rn, se]
        }, se]
      }],
      /**
       * Grid Row Start
       * @see https://tailwindcss.com/docs/grid-row
       */
      "row-start": [{
        "row-start": Je()
      }],
      /**
       * Grid Row End
       * @see https://tailwindcss.com/docs/grid-row
       */
      "row-end": [{
        "row-end": Je()
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
        "auto-cols": ["auto", "min", "max", "fr", se]
      }],
      /**
       * Grid Auto Rows
       * @see https://tailwindcss.com/docs/grid-auto-rows
       */
      "auto-rows": [{
        "auto-rows": ["auto", "min", "max", "fr", se]
      }],
      /**
       * Gap
       * @see https://tailwindcss.com/docs/gap
       */
      gap: [{
        gap: [A]
      }],
      /**
       * Gap X
       * @see https://tailwindcss.com/docs/gap
       */
      "gap-x": [{
        "gap-x": [A]
      }],
      /**
       * Gap Y
       * @see https://tailwindcss.com/docs/gap
       */
      "gap-y": [{
        "gap-y": [A]
      }],
      /**
       * Justify Content
       * @see https://tailwindcss.com/docs/justify-content
       */
      "justify-content": [{
        justify: ["normal", ...ne()]
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
        content: ["normal", ...ne(), "baseline"]
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
        "place-content": [...ne(), "baseline"]
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
        m: [H]
      }],
      /**
       * Margin X
       * @see https://tailwindcss.com/docs/margin
       */
      mx: [{
        mx: [H]
      }],
      /**
       * Margin Y
       * @see https://tailwindcss.com/docs/margin
       */
      my: [{
        my: [H]
      }],
      /**
       * Margin Start
       * @see https://tailwindcss.com/docs/margin
       */
      ms: [{
        ms: [H]
      }],
      /**
       * Margin End
       * @see https://tailwindcss.com/docs/margin
       */
      me: [{
        me: [H]
      }],
      /**
       * Margin Top
       * @see https://tailwindcss.com/docs/margin
       */
      mt: [{
        mt: [H]
      }],
      /**
       * Margin Right
       * @see https://tailwindcss.com/docs/margin
       */
      mr: [{
        mr: [H]
      }],
      /**
       * Margin Bottom
       * @see https://tailwindcss.com/docs/margin
       */
      mb: [{
        mb: [H]
      }],
      /**
       * Margin Left
       * @see https://tailwindcss.com/docs/margin
       */
      ml: [{
        ml: [H]
      }],
      /**
       * Space Between X
       * @see https://tailwindcss.com/docs/space
       */
      "space-x": [{
        "space-x": [K]
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
        "space-y": [K]
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
        w: ["auto", "min", "max", "fit", "svw", "lvw", "dvw", se, t]
      }],
      /**
       * Min-Width
       * @see https://tailwindcss.com/docs/min-width
       */
      "min-w": [{
        "min-w": [se, t, "min", "max", "fit"]
      }],
      /**
       * Max-Width
       * @see https://tailwindcss.com/docs/max-width
       */
      "max-w": [{
        "max-w": [se, t, "none", "full", "min", "max", "fit", "prose", {
          screen: [Zt]
        }, Zt]
      }],
      /**
       * Height
       * @see https://tailwindcss.com/docs/height
       */
      h: [{
        h: [se, t, "auto", "min", "max", "fit", "svh", "lvh", "dvh"]
      }],
      /**
       * Min-Height
       * @see https://tailwindcss.com/docs/min-height
       */
      "min-h": [{
        "min-h": [se, t, "min", "max", "fit", "svh", "lvh", "dvh"]
      }],
      /**
       * Max-Height
       * @see https://tailwindcss.com/docs/max-height
       */
      "max-h": [{
        "max-h": [se, t, "min", "max", "fit", "svh", "lvh", "dvh"]
      }],
      /**
       * Size
       * @see https://tailwindcss.com/docs/size
       */
      size: [{
        size: [se, t, "auto", "min", "max", "fit"]
      }],
      // Typography
      /**
       * Font Size
       * @see https://tailwindcss.com/docs/font-size
       */
      "font-size": [{
        text: ["base", Zt, Qt]
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
        font: ["thin", "extralight", "light", "normal", "medium", "semibold", "bold", "extrabold", "black", Wo]
      }],
      /**
       * Font Family
       * @see https://tailwindcss.com/docs/font-family
       */
      "font-family": [{
        font: [ln]
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
        tracking: ["tighter", "tight", "normal", "wide", "wider", "widest", se]
      }],
      /**
       * Line Clamp
       * @see https://tailwindcss.com/docs/line-clamp
       */
      "line-clamp": [{
        "line-clamp": ["none", Ms, Wo]
      }],
      /**
       * Line Height
       * @see https://tailwindcss.com/docs/line-height
       */
      leading: [{
        leading: ["none", "tight", "snug", "normal", "relaxed", "loose", Ut, se]
      }],
      /**
       * List Style Image
       * @see https://tailwindcss.com/docs/list-style-image
       */
      "list-image": [{
        "list-image": ["none", se]
      }],
      /**
       * List Style Type
       * @see https://tailwindcss.com/docs/list-style-type
       */
      "list-style-type": [{
        list: ["none", "disc", "decimal", se]
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
        "placeholder-opacity": [z]
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
        "text-opacity": [z]
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
        decoration: [...Ce(), "wavy"]
      }],
      /**
       * Text Decoration Thickness
       * @see https://tailwindcss.com/docs/text-decoration-thickness
       */
      "text-decoration-thickness": [{
        decoration: ["auto", "from-font", Ut, Qt]
      }],
      /**
       * Text Underline Offset
       * @see https://tailwindcss.com/docs/text-underline-offset
       */
      "underline-offset": [{
        "underline-offset": ["auto", Ut, se]
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
        indent: ae()
      }],
      /**
       * Vertical Alignment
       * @see https://tailwindcss.com/docs/vertical-align
       */
      "vertical-align": [{
        align: ["baseline", "top", "middle", "bottom", "text-top", "text-bottom", "sub", "super", se]
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
        content: ["none", se]
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
        "bg-opacity": [z]
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
        bg: [...ft(), ef]
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
        bg: ["auto", "cover", "contain", Xc]
      }],
      /**
       * Background Image
       * @see https://tailwindcss.com/docs/background-image
       */
      "bg-image": [{
        bg: ["none", {
          "gradient-to": ["t", "tr", "r", "br", "b", "bl", "l", "tl"]
        }, sf]
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
        from: [$]
      }],
      /**
       * Gradient Color Stops Via Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-via-pos": [{
        via: [$]
      }],
      /**
       * Gradient Color Stops To Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-to-pos": [{
        to: [$]
      }],
      /**
       * Gradient Color Stops From
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-from": [{
        from: [k]
      }],
      /**
       * Gradient Color Stops Via
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-via": [{
        via: [k]
      }],
      /**
       * Gradient Color Stops To
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      "gradient-to": [{
        to: [k]
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
        "border-opacity": [z]
      }],
      /**
       * Border Style
       * @see https://tailwindcss.com/docs/border-style
       */
      "border-style": [{
        border: [...Ce(), "hidden"]
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
        "divide-opacity": [z]
      }],
      /**
       * Divide Style
       * @see https://tailwindcss.com/docs/divide-style
       */
      "divide-style": [{
        divide: Ce()
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
        outline: ["", ...Ce()]
      }],
      /**
       * Outline Offset
       * @see https://tailwindcss.com/docs/outline-offset
       */
      "outline-offset": [{
        "outline-offset": [Ut, se]
      }],
      /**
       * Outline Width
       * @see https://tailwindcss.com/docs/outline-width
       */
      "outline-w": [{
        outline: [Ut, Qt]
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
        ring: he()
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
        "ring-opacity": [z]
      }],
      /**
       * Ring Offset Width
       * @see https://tailwindcss.com/docs/ring-offset-width
       */
      "ring-offset-w": [{
        "ring-offset": [Ut, Qt]
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
        shadow: ["", "inner", "none", Zt, nf]
      }],
      /**
       * Box Shadow Color
       * @see https://tailwindcss.com/docs/box-shadow-color
       */
      "shadow-color": [{
        shadow: [ln]
      }],
      /**
       * Opacity
       * @see https://tailwindcss.com/docs/opacity
       */
      opacity: [{
        opacity: [z]
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
        contrast: [u]
      }],
      /**
       * Drop Shadow
       * @see https://tailwindcss.com/docs/drop-shadow
       */
      "drop-shadow": [{
        "drop-shadow": ["", "none", Zt, se]
      }],
      /**
       * Grayscale
       * @see https://tailwindcss.com/docs/grayscale
       */
      grayscale: [{
        grayscale: [h]
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
        saturate: [q]
      }],
      /**
       * Sepia
       * @see https://tailwindcss.com/docs/sepia
       */
      sepia: [{
        sepia: [Z]
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
        "backdrop-contrast": [u]
      }],
      /**
       * Backdrop Grayscale
       * @see https://tailwindcss.com/docs/backdrop-grayscale
       */
      "backdrop-grayscale": [{
        "backdrop-grayscale": [h]
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
        "backdrop-opacity": [z]
      }],
      /**
       * Backdrop Saturate
       * @see https://tailwindcss.com/docs/backdrop-saturate
       */
      "backdrop-saturate": [{
        "backdrop-saturate": [q]
      }],
      /**
       * Backdrop Sepia
       * @see https://tailwindcss.com/docs/backdrop-sepia
       */
      "backdrop-sepia": [{
        "backdrop-sepia": [Z]
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
        transition: ["none", "all", "", "colors", "opacity", "shadow", "transform", se]
      }],
      /**
       * Transition Duration
       * @see https://tailwindcss.com/docs/transition-duration
       */
      duration: [{
        duration: je()
      }],
      /**
       * Transition Timing Function
       * @see https://tailwindcss.com/docs/transition-timing-function
       */
      ease: [{
        ease: ["linear", "in", "out", "in-out", se]
      }],
      /**
       * Transition Delay
       * @see https://tailwindcss.com/docs/transition-delay
       */
      delay: [{
        delay: je()
      }],
      /**
       * Animation
       * @see https://tailwindcss.com/docs/animation
       */
      animate: [{
        animate: ["none", "spin", "ping", "pulse", "bounce", se]
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
        scale: [U]
      }],
      /**
       * Scale X
       * @see https://tailwindcss.com/docs/scale
       */
      "scale-x": [{
        "scale-x": [U]
      }],
      /**
       * Scale Y
       * @see https://tailwindcss.com/docs/scale
       */
      "scale-y": [{
        "scale-y": [U]
      }],
      /**
       * Rotate
       * @see https://tailwindcss.com/docs/rotate
       */
      rotate: [{
        rotate: [rn, se]
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
        "skew-x": [$e]
      }],
      /**
       * Skew Y
       * @see https://tailwindcss.com/docs/skew
       */
      "skew-y": [{
        "skew-y": [$e]
      }],
      /**
       * Transform Origin
       * @see https://tailwindcss.com/docs/transform-origin
       */
      "transform-origin": [{
        origin: ["center", "top", "top-right", "right", "bottom-right", "bottom", "bottom-left", "left", "top-left", se]
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
        cursor: ["auto", "default", "pointer", "wait", "text", "move", "help", "not-allowed", "none", "context-menu", "progress", "cell", "crosshair", "vertical-text", "alias", "copy", "no-drop", "grab", "grabbing", "all-scroll", "col-resize", "row-resize", "n-resize", "e-resize", "s-resize", "w-resize", "ne-resize", "nw-resize", "se-resize", "sw-resize", "ew-resize", "ns-resize", "nesw-resize", "nwse-resize", "zoom-in", "zoom-out", se]
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
        "scroll-m": ae()
      }],
      /**
       * Scroll Margin X
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mx": [{
        "scroll-mx": ae()
      }],
      /**
       * Scroll Margin Y
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-my": [{
        "scroll-my": ae()
      }],
      /**
       * Scroll Margin Start
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-ms": [{
        "scroll-ms": ae()
      }],
      /**
       * Scroll Margin End
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-me": [{
        "scroll-me": ae()
      }],
      /**
       * Scroll Margin Top
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mt": [{
        "scroll-mt": ae()
      }],
      /**
       * Scroll Margin Right
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mr": [{
        "scroll-mr": ae()
      }],
      /**
       * Scroll Margin Bottom
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-mb": [{
        "scroll-mb": ae()
      }],
      /**
       * Scroll Margin Left
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      "scroll-ml": [{
        "scroll-ml": ae()
      }],
      /**
       * Scroll Padding
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-p": [{
        "scroll-p": ae()
      }],
      /**
       * Scroll Padding X
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-px": [{
        "scroll-px": ae()
      }],
      /**
       * Scroll Padding Y
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-py": [{
        "scroll-py": ae()
      }],
      /**
       * Scroll Padding Start
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-ps": [{
        "scroll-ps": ae()
      }],
      /**
       * Scroll Padding End
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pe": [{
        "scroll-pe": ae()
      }],
      /**
       * Scroll Padding Top
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pt": [{
        "scroll-pt": ae()
      }],
      /**
       * Scroll Padding Right
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pr": [{
        "scroll-pr": ae()
      }],
      /**
       * Scroll Padding Bottom
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pb": [{
        "scroll-pb": ae()
      }],
      /**
       * Scroll Padding Left
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      "scroll-pl": [{
        "scroll-pl": ae()
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
        "will-change": ["auto", "scroll", "contents", "transform", se]
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
        stroke: [Ut, Qt, Wo]
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
}, uf = /* @__PURE__ */ Hc(af);
function _o(...e) {
  return uf(Yi(e));
}
const df = ["disabled"], pe = /* @__PURE__ */ He({
  __name: "Button",
  props: {
    variant: { default: "primary", type: null },
    size: { default: "md", type: null },
    class: { type: String },
    disabled: { type: Boolean, default: !1 }
  },
  emits: ["click"],
  setup(e, { emit: t }) {
    const s = e, n = t, o = xe(
      () => _o(
        Pc({ variant: s.variant, size: s.size }),
        s.disabled && "pointer-events-none opacity-50",
        s.class
      )
    );
    function l(i) {
      s.disabled || n("click", i);
    }
    return (i, a) => (C(), R("button", {
      type: "button",
      class: lt(o.value),
      disabled: e.disabled,
      onClick: l
    }, [
      ns(i.$slots, "default")
    ], 10, df));
  }
});
function cf(e, t) {
  const s = `${e}Context`, n = Symbol(s);
  return [(i) => {
    const a = hn(n, i);
    if (a || a === null) return a;
    throw new Error(`Injection \`${n.toString()}\` not found. Component must be used within ${Array.isArray(e) ? `one of the following components: ${e.join(", ")}` : `\`${e}\``}`);
  }, (i) => (hi(n, i), i)];
}
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const ff = (e) => typeof e < "u";
function Ar(e) {
  var t;
  const s = ai(e);
  return (t = s == null ? void 0 : s.$el) !== null && t !== void 0 ? t : s;
}
function pf(e) {
  return JSON.parse(JSON.stringify(e));
}
// @__NO_SIDE_EFFECTS__
function mf(e, t, s, n = {}) {
  var o, l;
  const { clone: i = !1, passive: a = !1, eventName: u, deep: h = !1, defaultValue: g, shouldEmit: x } = n, A = os(), k = s || (A == null ? void 0 : A.emit) || (A == null || (o = A.$emit) === null || o === void 0 ? void 0 : o.bind(A)) || (A == null || (l = A.proxy) === null || l === void 0 || (l = l.$emit) === null || l === void 0 ? void 0 : l.bind(A == null ? void 0 : A.proxy));
  let $ = u;
  $ = $ || `update:${t.toString()}`;
  const v = (D) => i ? typeof i == "function" ? i(D) : pf(D) : D, H = () => ff(e[t]) ? v(e[t]) : g, z = (D) => {
    x ? x(D) && k($, D) : k($, D);
  };
  if (a) {
    const D = /* @__PURE__ */ L(H());
    let q = !1;
    return vt(() => e[t], (U) => {
      q || (q = !0, D.value = v(U), Tn(() => q = !1));
    }), vt(D, (U) => {
      !q && (U !== e[t] || h) && z(U);
    }, { deep: h }), D;
  } else return xe({
    get() {
      return H();
    },
    set(D) {
      z(D);
    }
  });
}
function na(e) {
  return e ? e.flatMap((t) => t.type === ce ? na(t.children) : [t]) : [];
}
function gf(e) {
  const t = os(), s = t == null ? void 0 : t.type.emits, n = {};
  return s != null && s.length || console.warn(`No emitted event found. Please check component: ${t == null ? void 0 : t.type.__name}`), s == null || s.forEach((o) => {
    n[qn(Ge(o))] = (...l) => e(o, ...l);
  }), n;
}
function hf(e) {
  return xe(() => {
    var t;
    return ai(e) ? !!((t = Ar(e)) != null && t.closest("form")) : !0;
  });
}
function oa() {
  const e = os(), t = /* @__PURE__ */ L(), s = xe(() => n());
  xi(() => {
    s.value !== n() && Pu(t);
  });
  function n() {
    return t.value && "$el" in t.value && ["#text", "#comment"].includes(t.value.$el.nodeName) ? t.value.$el.nextElementSibling : Ar(t);
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
      const u = a.$.exposed, h = Object.assign({}, l);
      for (const g in u) Object.defineProperty(h, g, {
        enumerable: !0,
        configurable: !0,
        get: () => u[g]
      });
      e.exposed = h;
    }
  }
  return {
    forwardRef: i,
    currentRef: t,
    currentElement: s
  };
}
function bf(e) {
  const t = os(), s = Object.keys((t == null ? void 0 : t.type.props) ?? {}).reduce((o, l) => {
    const i = (t == null ? void 0 : t.type.props[l]).default;
    return i !== void 0 && (o[l] = i), o;
  }, {}), n = /* @__PURE__ */ Nu(e);
  return xe(() => {
    const o = {}, l = (t == null ? void 0 : t.vnode.props) ?? {};
    return Object.keys(l).forEach((i) => {
      o[Ge(i)] = l[i];
    }), Object.keys({
      ...s,
      ...o
    }).reduce((i, a) => (n.value[a] !== void 0 && (i[a] = n.value[a]), i), {});
  });
}
function vf(e, t) {
  const s = bf(e), n = t ? gf(t) : {};
  return xe(() => ({
    ...s.value,
    ...n
  }));
}
function yf() {
  var t, s;
  const e = (s = (t = os()) == null ? void 0 : t.vnode) == null ? void 0 : s.scopeId;
  return e ? { [e]: "" } : {};
}
const xf = /* @__PURE__ */ He({
  name: "PrimitiveSlot",
  inheritAttrs: !1,
  setup(e, { attrs: t, slots: s }) {
    return () => {
      var u;
      if (!s.default) return null;
      const n = na(s.default()), o = n.findIndex((h) => h.type !== Ot);
      if (o === -1) return n;
      const l = n[o];
      (u = l.props) == null || delete u.ref;
      const i = l.props ? ts(t, l.props) : t, a = ms({
        ...l,
        props: {}
      }, i);
      return n.length === 1 ? a : (n[o] = a, n);
    };
  }
}), _f = [
  "area",
  "img",
  "input"
], Er = /* @__PURE__ */ He({
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
    return typeof n == "string" && _f.includes(n) ? () => Fo(n, t) : n !== "template" ? () => Fo(e.as, t, { default: s.default }) : () => Fo(xf, t, { default: s.default });
  }
});
function wf() {
  const e = /* @__PURE__ */ L(), t = xe(() => {
    var s, n;
    return ["#text", "#comment"].includes((s = e.value) == null ? void 0 : s.$el.nodeName) ? (n = e.value) == null ? void 0 : n.$el.nextElementSibling : Ar(e);
  });
  return {
    primitiveElement: e,
    currentElement: t
  };
}
var kf = /* @__PURE__ */ He({
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
    return (t, s) => (C(), Te(p(Er), {
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
      default: S(() => [ns(t.$slots, "default")]),
      _: 3
    }, 8, [
      "as",
      "as-child",
      "aria-hidden",
      "data-hidden",
      "tabindex"
    ]));
  }
}), Sf = kf, Cf = /* @__PURE__ */ He({
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
    const t = e, { primitiveElement: s, currentElement: n } = wf(), o = xe(() => t.checked ?? t.value);
    return vt(o, (l, i) => {
      if (!n.value) return;
      const a = n.value, u = window.HTMLInputElement.prototype, g = Object.getOwnPropertyDescriptor(u, "value").set;
      if (g && l !== i) {
        const x = new Event("input", { bubbles: !0 }), A = new Event("change", { bubbles: !0 });
        g.call(a, l), a.dispatchEvent(x), a.dispatchEvent(A);
      }
    }), (l, i) => (C(), Te(Sf, ts({
      ref_key: "primitiveElement",
      ref: s
    }, {
      ...t,
      ...l.$attrs
    }, { as: "input" }), null, 16));
  }
}), jl = Cf, Af = /* @__PURE__ */ He({
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
    const t = e, s = xe(() => typeof t.value == "object" && Array.isArray(t.value) && t.value.length === 0 && t.required), n = xe(() => typeof t.value == "string" || typeof t.value == "number" || typeof t.value == "boolean" || t.value === null || t.value === void 0 ? [{
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
    return (o, l) => (C(), R(ce, null, [W(" We render single input if it's required "), s.value ? (C(), Te(jl, ts({ key: o.name }, {
      ...t,
      ...o.$attrs
    }, {
      name: o.name,
      value: o.value
    }), null, 16, ["name", "value"])) : (C(!0), R(ce, { key: 1 }, Xe(n.value, (i) => (C(), Te(jl, ts({ key: i.name }, { ref_for: !0 }, {
      ...t,
      ...o.$attrs
    }, {
      name: i.name,
      value: i.value
    }), null, 16, ["name", "value"]))), 128))], 2112));
  }
}), Ef = Af;
const [If, Tf] = /* @__PURE__ */ cf("SwitchRoot");
var Pf = /* @__PURE__ */ He({
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
    const s = e, n = t, { disabled: o } = /* @__PURE__ */ $u(s), l = /* @__PURE__ */ mf(s, "modelValue", n, {
      defaultValue: s.defaultValue ?? s.falseValue,
      passive: s.modelValue === void 0
    }), i = xe(() => l.value === s.trueValue);
    function a() {
      o.value || (l.value = i.value ? s.falseValue : s.trueValue);
    }
    const { forwardRef: u, currentElement: h } = oa(), g = hf(h), x = yf(), A = xe(() => {
      var k;
      return s.id && h.value ? (k = document.querySelector(`[for="${s.id}"]`)) == null ? void 0 : k.innerText : void 0;
    });
    return Tf({
      checked: i,
      toggleCheck: a,
      disabled: o
    }), (k, $) => (C(), R(ce, null, [y(p(Er), ts({
      id: k.id,
      ref: p(u),
      role: "switch",
      type: k.as === "button" ? "button" : void 0,
      value: k.value,
      "aria-label": k.$attrs["aria-label"] || A.value,
      "aria-checked": i.value,
      "aria-required": k.required,
      "data-state": i.value ? "checked" : "unchecked",
      "data-disabled": p(o) ? "" : void 0,
      "as-child": k.asChild,
      as: k.as,
      disabled: p(o)
    }, {
      ...p(x),
      ...k.$attrs
    }, {
      onClick: a,
      onKeydown: fn(cn(a, ["prevent"]), ["enter"])
    }), {
      default: S(() => [ns(k.$slots, "default", {
        modelValue: p(l),
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
    ]), p(g) && k.name ? (C(), Te(p(Ef), ts({
      key: 0,
      type: "checkbox",
      name: k.name,
      disabled: p(o),
      required: k.required,
      value: k.value,
      checked: i.value
    }, p(x)), null, 16, [
      "name",
      "disabled",
      "required",
      "value",
      "checked"
    ])) : W("v-if", !0)], 64));
  }
}), Rf = Pf, Mf = /* @__PURE__ */ He({
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
    const t = If();
    return oa(), (s, n) => (C(), Te(p(Er), {
      "data-state": p(t).checked.value ? "checked" : "unchecked",
      "data-disabled": p(t).disabled.value ? "" : void 0,
      "as-child": s.asChild,
      as: s.as
    }, {
      default: S(() => [ns(s.$slots, "default")]),
      _: 3
    }, 8, [
      "data-state",
      "data-disabled",
      "as-child",
      "as"
    ]));
  }
}), Vf = Mf;
const an = /* @__PURE__ */ He({
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
    const s = e, n = t, o = xe(() => {
      const { class: i, ...a } = s;
      return a;
    }), l = vf(o, n);
    return (i, a) => (C(), Te(p(Rf), ts(p(l), {
      as: "button",
      type: "button",
      class: p(_o)(
        "peer focus-visible:ring-ring focus-visible:ring-offset-background data-[state=checked]:bg-primary data-[state=unchecked]:bg-input inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50",
        s.class
      )
    }), {
      default: S(() => [
        y(p(Vf), { class: "bg-background pointer-events-none block h-5 w-5 rounded-full shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0" })
      ]),
      _: 1
    }, 16, ["class"]));
  }
}), $f = Qi(
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
), Dt = /* @__PURE__ */ He({
  __name: "Badge",
  props: {
    variant: { default: "gray", type: null },
    size: { default: "sm", type: null },
    class: { default: "", type: String }
  },
  setup(e) {
    const t = e, s = xe(() => $f({ variant: t.variant, size: t.size }));
    return (n, o) => (C(), R("span", {
      class: lt([s.value, t.class])
    }, [
      ns(n.$slots, "default")
    ], 2));
  }
});
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Of = (e) => typeof e < "u";
function jf(e) {
  return JSON.parse(JSON.stringify(e));
}
// @__NO_SIDE_EFFECTS__
function ra(e, t, s, n = {}) {
  var o, l, i;
  const {
    clone: a = !1,
    passive: u = !1,
    eventName: h,
    deep: g = !1,
    defaultValue: x,
    shouldEmit: A
  } = n, k = os(), $ = s || (k == null ? void 0 : k.emit) || ((o = k == null ? void 0 : k.$emit) == null ? void 0 : o.bind(k)) || ((i = (l = k == null ? void 0 : k.proxy) == null ? void 0 : l.$emit) == null ? void 0 : i.bind(k == null ? void 0 : k.proxy));
  let v = h;
  v = v || `update:${t.toString()}`;
  const H = (q) => a ? typeof a == "function" ? a(q) : jf(q) : q, z = () => Of(e[t]) ? H(e[t]) : x, D = (q) => {
    A ? A(q) && $(v, q) : $(v, q);
  };
  if (u) {
    const q = z(), U = /* @__PURE__ */ L(q);
    let Z = !1;
    return vt(
      () => e[t],
      ($e) => {
        Z || (Z = !0, U.value = H($e), Tn(() => Z = !1));
      }
    ), vt(
      U,
      ($e) => {
        !Z && ($e !== e[t] || g) && D($e);
      },
      { deep: g }
    ), U;
  } else
    return xe({
      get() {
        return z();
      },
      set(q) {
        D(q);
      }
    });
}
const Nf = ["type", "placeholder"], be = /* @__PURE__ */ He({
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
    const s = e, o = /* @__PURE__ */ ra(s, "modelValue", t, {
      passive: !0,
      defaultValue: s.defaultValue
    });
    return (l, i) => hr((C(), R("input", {
      "onUpdate:modelValue": i[0] || (i[0] = (a) => /* @__PURE__ */ Re(o) ? o.value = a : null),
      type: e.type ?? "text",
      placeholder: e.placeholder,
      class: lt(
        p(_o)(
          "border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50",
          s.class
        )
      )
    }, null, 10, Nf)), [
      [_c, p(o)]
    ]);
  }
}), Lf = ["id", "disabled"], Cs = /* @__PURE__ */ He({
  __name: "Select",
  props: {
    modelValue: { type: String },
    class: { type: String },
    id: { type: String },
    disabled: { type: Boolean }
  },
  emits: ["update:modelValue"],
  setup(e, { emit: t }) {
    const s = e, o = /* @__PURE__ */ ra(s, "modelValue", t, { passive: !0 });
    return (l, i) => (C(), R("div", {
      class: lt(p(_o)("relative inline-block", s.class))
    }, [
      hr(f("select", {
        id: e.id,
        "onUpdate:modelValue": i[0] || (i[0] = (a) => /* @__PURE__ */ Re(o) ? o.value = a : null),
        disabled: e.disabled,
        class: "border-input bg-background ring-offset-background focus-visible:ring-ring h-10 w-full cursor-pointer appearance-none rounded-md border py-2 pr-8 pl-3 text-sm focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50"
      }, [
        ns(l.$slots, "default")
      ], 8, Lf), [
        [Ki, p(o)]
      ]),
      i[1] || (i[1] = f("svg", {
        class: "text-muted-foreground pointer-events-none absolute top-1/2 right-2.5 -translate-y-1/2",
        width: "10",
        height: "6",
        viewBox: "0 0 10 6",
        fill: "none",
        "aria-hidden": "true"
      }, [
        f("path", {
          d: "M1 1L5 5L9 1",
          stroke: "currentColor",
          "stroke-width": "1.5",
          "stroke-linecap": "round",
          "stroke-linejoin": "round"
        })
      ], -1))
    ], 2));
  }
}), Uf = ["for"], re = /* @__PURE__ */ He({
  __name: "Label",
  props: {
    for: { type: String },
    class: { type: String }
  },
  setup(e) {
    return (t, s) => (C(), R("label", {
      for: t.$props.for,
      class: lt(["text-sm leading-none font-medium", t.$props.class])
    }, [
      ns(t.$slots, "default")
    ], 10, Uf));
  }
}), Df = { class: "inline_help" }, le = /* @__PURE__ */ He({
  __name: "HelpText",
  setup(e) {
    return (t, s) => (C(), R("blockquote", Df, [
      ns(t.$slots, "default")
    ]));
  }
}), Bf = {
  role: "tablist",
  "aria-label": "Incus settings sections",
  class: "mb-6 flex gap-1 border-b border-border"
}, Ff = ["id", "aria-selected", "aria-controls", "tabindex", "onClick", "onKeydown"], Hf = /* @__PURE__ */ He({
  __name: "TabNavigation",
  props: {
    modelValue: { required: !0 },
    modelModifiers: {}
  },
  emits: ["update:modelValue"],
  setup(e) {
    const t = bd(e, "modelValue"), s = [
      { id: "builder", label: "Builder" },
      { id: "jails", label: "Containers" },
      { id: "config", label: "Config" }
    ];
    function n(o, l) {
      var u;
      const i = s.findIndex((h) => h.id === l);
      let a = null;
      o.key === "ArrowRight" ? a = (i + 1) % s.length : o.key === "ArrowLeft" ? a = (i - 1 + s.length) % s.length : o.key === "Home" ? a = 0 : o.key === "End" && (a = s.length - 1), a !== null && (o.preventDefault(), t.value = s[a].id, (u = document.getElementById(`incus-tab-${s[a].id}`)) == null || u.focus());
    }
    return (o, l) => (C(), R("div", Bf, [
      (C(), R(ce, null, Xe(s, (i) => f("button", {
        id: `incus-tab-${i.id}`,
        key: i.id,
        role: "tab",
        type: "button",
        "aria-selected": t.value === i.id,
        "aria-controls": `incus-panel-${i.id}`,
        tabindex: t.value === i.id ? 0 : -1,
        class: lt(["-mb-px cursor-pointer border-b-[3px] px-4 py-2 text-xs font-semibold tracking-[0.08em] uppercase transition-colors", t.value === i.id ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"]),
        onClick: (a) => t.value = i.id,
        onKeydown: (a) => n(a, i.id)
      }, M(i.label), 43, Ff)), 64))
    ]));
  }
});
class la extends Error {
  constructor(t, s) {
    super(t), this.errors = s;
  }
}
let Nl = null;
function zf() {
  return window.csrf_token ? Promise.resolve() : (Nl ?? (Nl = new Promise((e) => {
    const t = Date.now() + 2e3, s = () => {
      window.csrf_token || Date.now() >= t ? e() : setTimeout(s, 20);
    };
    s();
  })), Nl);
}
async function Ll(e, t) {
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
    throw new la(((l = n.errors[0]) == null ? void 0 : l.message) ?? "GraphQL error", n.errors);
  return n.data;
}
const Wf = (e) => new Promise((t) => setTimeout(t, e));
function Kf(e) {
  const t = e.replace(/^\s*(?:#[^\n]*\n\s*)*/, "");
  return t.startsWith("query") || t.startsWith("{");
}
async function me(e, t) {
  await zf();
  try {
    return await Ll(e, t);
  } catch (s) {
    if (s instanceof la || !Kf(e)) throw s;
    return await Wf(300), Ll(e, t);
  }
}
function Kn(e, t, s = {}) {
  let n = !1, o = null, l = null;
  const i = new AbortController(), a = typeof document > "u" ? null : document, u = {
    signal: i.signal,
    isActive: () => !n && !i.signal.aborted
  }, h = () => {
    n || (l = setTimeout(() => void g(), t));
  }, g = async () => {
    if (!n) {
      if (a != null && a.hidden) {
        h();
        return;
      }
      return o || (o = e(u).catch((A) => {
        var k;
        u.isActive() && ((k = s.onError) == null || k.call(s, A));
      }).finally(() => {
        o = null, h();
      }), o);
    }
  };
  s.immediate ? g() : h();
  const x = () => {
    !(a != null && a.hidden) && !n && !o && (l && clearTimeout(l), l = null, g());
  };
  return a == null || a.addEventListener("visibilitychange", x), {
    stop() {
      n = !0, i.abort(), l && clearTimeout(l), l = null, a == null || a.removeEventListener("visibilitychange", x);
    },
    trigger: g
  };
}
function qf(e, t) {
  const { tsAuthKeyConfigured: s, ...n } = e;
  return t.clear ? { ...n, tsAuthKey: "" } : t.replacement ? { ...n, tsAuthKey: t.replacement } : n;
}
function Gf(e, t) {
  const s = /* @__PURE__ */ Kt(/* @__PURE__ */ new Map()), n = /* @__PURE__ */ Kt(/* @__PURE__ */ new Map()), o = /* @__PURE__ */ L([]), l = /* @__PURE__ */ Kt(/* @__PURE__ */ new Map()), i = 30, a = xe(() => e.value.filter((K) => K.status.toLowerCase() === "running")), u = xe(() => e.value.length - a.value.length), h = xe(() => a.value.reduce((K, te) => K + Number(te.memoryUsageBytes ?? 0), 0)), g = xe(() => a.value.reduce((K, te) => K + BigInt(te.cpuUsageNs ?? "0"), 0n));
  function x(K) {
    if (K == null) return "—";
    const te = Math.floor(K / 1e9), Oe = Math.floor(te / 3600), we = Math.floor(te % 3600 / 60), Me = te % 60;
    return Oe > 0 ? `${Oe}h ${we}m ${Me}s` : we > 0 ? `${we}m ${Me}s` : `${Me}s`;
  }
  function A(K) {
    if (K == null) return "—";
    if (K === 0) return "0 B";
    const te = ["B", "KiB", "MiB", "GiB", "TiB"], Oe = Math.min(Math.floor(Math.log(K) / Math.log(1024)), te.length - 1), we = K / 1024 ** Oe;
    return `${we >= 10 || Oe === 0 ? Math.round(we) : we.toFixed(1)} ${te[Oe]}`;
  }
  function k(K) {
    if (K.memoryUsageBytes == null) return "—";
    const te = A(Number(K.memoryUsageBytes));
    return K.memoryTotalBytes ? `${te} / ${A(Number(K.memoryTotalBytes))}` : te;
  }
  function $(K) {
    return !K.memoryTotalBytes || K.memoryUsageBytes == null ? null : Math.min(100, Math.round(Number(K.memoryUsageBytes) / Number(K.memoryTotalBytes) * 100));
  }
  function v() {
    const K = t().trim();
    if (!/^\d+$/.test(K)) return null;
    const te = Number(K);
    return te > 0 ? te : null;
  }
  function H() {
    const K = Date.now();
    let te = 0, Oe = !1, we = 0, Me = 0;
    for (const he of e.value) {
      if (he.cpuUsageNs == null) {
        s.delete(he.name), l.delete(he.name);
        continue;
      }
      const Je = BigInt(he.cpuUsageNs), ft = s.get(he.name);
      if (ft) {
        const Ce = Je - ft.cpuUsageNs, fe = K - ft.atMs;
        if (Ce >= 0n && fe > 0) {
          const ne = Number(Ce) / (fe * 1e6) * 100;
          l.set(he.name, ne);
          const Ae = $(he), Ye = n.get(he.name) ?? [];
          Ye.push({ atMs: K, cpuPct: ne, memPct: Ae }), Ye.length > i && Ye.shift(), n.set(he.name, Ye), he.status.toLowerCase() === "running" && (te += ne, Oe = !0, Ae !== null && (we += Ae, Me++));
        } else l.delete(he.name);
      } else l.delete(he.name);
      s.set(he.name, { atMs: K, cpuUsageNs: Je });
    }
    const ae = new Set(e.value.map((he) => he.name));
    for (const he of [s, n, l])
      for (const Je of Array.from(he.keys())) ae.has(Je) || he.delete(Je);
    Oe && (o.value.push({ atMs: K, cpuPct: te, memPct: Me ? we / Me : null }), o.value.length > i && o.value.shift());
  }
  return {
    runningJails: a,
    stoppedJailsCount: u,
    totalMemoryUsageBytes: h,
    totalCpuUsageNs: g,
    fleetHistory: o,
    formatDuration: x,
    formatBytes: A,
    formatMemory: k,
    memoryFillPct: $,
    updateCpuSamplesAndHistory: H,
    cpuRateLabel: (K) => l.has(K.name) ? `${l.get(K.name).toFixed(l.get(K.name) < 10 ? 1 : 0)}%` : "—",
    cpuRatePct: (K) => {
      const te = l.get(K.name);
      return te === void 0 ? null : Math.min(100, Math.max(0, Math.round(v() ? te / v() : te)));
    },
    cpuRateSuffix: () => v() ? `of ${v()} core${v() === 1 ? "" : "s"}` : "of 1 core",
    jailCpuHistory: (K) => n.get(K) ?? [],
    totalCpuRateLabel: () => o.value.length ? `${o.value.at(-1).cpuPct.toFixed(o.value.at(-1).cpuPct < 10 ? 1 : 0)}%` : "—",
    sparklinePoints: (K, te, Oe = 80, we = 24) => K.map((Me, ae) => Me[te] === null ? null : `${(ae * (Oe / Math.max(1, K.length - 1))).toFixed(1)},${(we - Math.min(100, Math.max(0, Me[te])) / 100 * we).toFixed(1)}`).filter(Boolean).join(" ")
  };
}
const Jf = `query { incusConfig {
  enabled stateDir storageDriver storageSource storagePoolName jailBridge jailSubnet jailNat jailIpv6
  aclName aclBlock aclAllow aclDefaultEgress aclDefaultIngress jailProfile jailImage jailNesting jailCpu jailMemory
  jailWorkspaceRoot jailAgentUid jailAgentGid jailBindMounts tsAuthKeyConfigured dashboardWidgetEnable
} }`, Yf = "query { incusHealthy jails { name status ipv4 cpuUsageNs memoryUsageBytes memoryTotalBytes } }", Ul = "mutation($input: IncusConfigInput!) { updateIncusConfig(input: $input) { enabled } }", Qf = "mutation($name: String!, $action: JailAction!) { setJailState(name: $name, action: $action) }", Zf = "mutation($name: String!) { deleteJail(name: $name) }", Xf = "mutation($name: String!, $image: String, $allowSudo: Boolean) { launchJail(name: $name, image: $image, allowSudo: $allowSudo) }", ep = "query($name: String!) { jailDetail(name: $name) { name profiles imageOs imageRelease imageDescription storagePool networkBridge cpuLimit cpuLimitIsOverride memoryLimit memoryLimitIsOverride workspaceHostPath workspaceIsOverride sudoEnabled } }", tp = "mutation($name: String!) { grantJailSudo(name: $name) }", sp = "mutation($name: String!, $command: String!) { startPrivilegedCommand(name: $name, command: $command) }", np = "query($id: String!) { privilegedCommandStatus(id: $id) { id command status exitCode stdout stderr message } }", op = "mutation($name: String!, $hostPath: String!) { setJailWorkspace(name: $name, hostPath: $hostPath) }", rp = "mutation($name: String!) { clearJailWorkspace(name: $name) }", Ko = "mutation($name: String!, $cpu: String, $memory: String) { setJailLimits(name: $name, cpu: $cpu, memory: $memory) }", lp = "mutation($distro: String!, $release: String!, $packages: [String!]!, $alias: String!, $basedOn: String, $postInstallCommands: [String!]) { buildJailImage(distro: $distro, release: $release, packages: $packages, alias: $alias, basedOn: $basedOn, postInstallCommands: $postInstallCommands) }", ip = "mutation($alias: String!) { deleteJailImage(alias: $alias) }", ap = "query($query: String!, $distro: String, $release: String) { searchAllPackages(query: $query, distro: $distro, release: $release) { results { ecosystem name description version } errors { ecosystem message } } }", up = "query($buildId: String!) { jailImageBuildStatus(buildId: $buildId) { id status alias distro release packages logTail error } }", dp = "query { builderPresets { name distro release packages } }", cp = "mutation($input: BuilderPresetInput!) { saveBuilderPreset(input: $input) { name } }", fp = "mutation($name: String!) { deleteBuilderPreset(name: $name) }", pp = "query { jailImages { alias distro release packages isMaster basedOn createdAt } }", qo = "mutation($alias: String!, $isMaster: Boolean!) { setMasterImage(alias: $alias, isMaster: $isMaster) { alias isMaster } }", mp = "mutation { pruneStaleImageRecords }", gp = "mutation { deleteStoppedJails }", hp = "mutation($name: String!) { migrateJailWorkspace(name: $name) }", bp = "mutation($name: String!, $formula: String!) { installHomebrewFormula(name: $name, formula: $formula) }", vp = "query($id: String!) { homebrewInstallStatus(id: $id) { id formula status message } }";
function yp(e) {
  const t = /* @__PURE__ */ L(null), s = /* @__PURE__ */ L(null), n = /* @__PURE__ */ L(!1), o = /* @__PURE__ */ L(""), l = /* @__PURE__ */ L(""), i = /* @__PURE__ */ L(""), a = /* @__PURE__ */ L("");
  let u = 0;
  async function h(x) {
    if (e(), t.value === x) {
      ++u, t.value = null, s.value = null, n.value = !1;
      return;
    }
    t.value = x, await g(x);
  }
  async function g(x) {
    const A = ++u;
    n.value = !0, o.value = "";
    try {
      const k = await me(ep, { name: x });
      if (A !== u || t.value !== x) return;
      s.value = k.jailDetail, l.value = k.jailDetail.cpuLimit ?? "", i.value = k.jailDetail.memoryLimit ?? "", a.value = k.jailDetail.workspaceHostPath ?? "";
    } catch (k) {
      if (A !== u || t.value !== x) return;
      o.value = k instanceof Error ? k.message : String(k);
    } finally {
      A === u && (n.value = !1);
    }
  }
  return {
    detailsJailName: t,
    jailDetail: s,
    detailLoading: n,
    detailError: o,
    editCpuLimit: l,
    editMemoryLimit: i,
    editWorkspacePath: a,
    toggleJailDetails: h,
    loadJailDetail: g
  };
}
const xp = { class: "unapi w-full max-w-4xl text-foreground xl:max-w-6xl 2xl:max-w-[1600px] min-[1920px]:max-w-[1880px] min-[2560px]:max-w-[2200px]" }, _p = {
  key: 0,
  class: "py-8 text-muted-foreground"
}, wp = {
  key: 0,
  role: "alert",
  class: "mb-4 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
}, kp = { class: "mb-6 flex items-center gap-3 border-b border-border pb-4" }, Sp = { class: "ml-auto flex items-center gap-3" }, Cp = {
  key: 1,
  id: "incus-panel-builder",
  role: "tabpanel",
  "aria-labelledby": "incus-tab-builder",
  tabindex: "0"
}, Ap = { class: "grid grid-cols-1 items-start gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]" }, Ep = { class: "mb-6 rounded-lg border border-border bg-card p-4 xl:mb-0" }, Ip = {
  key: 0,
  class: "mb-3 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, Tp = {
  key: 1,
  class: "text-sm text-muted-foreground"
}, Pp = {
  key: 2,
  class: "mb-3 flex flex-wrap gap-2"
}, Rp = ["onClick"], Mp = { class: "font-mono text-muted-foreground" }, Vp = ["onClick"], $p = { class: "flex gap-2" }, Op = { class: "mt-5 border-t border-border pt-4" }, jp = { class: "mb-2 flex items-center justify-between gap-3" }, Np = {
  key: 0,
  class: "mb-3 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, Lp = {
  key: 1,
  class: "mb-3 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs"
}, Up = {
  key: 2,
  class: "text-sm text-muted-foreground"
}, Dp = {
  key: 3,
  class: "flex flex-col gap-2"
}, Bp = { class: "min-w-0 flex-1" }, Fp = { class: "flex items-center gap-2" }, Hp = { class: "font-mono text-[13px] font-medium" }, zp = { class: "text-xs text-muted-foreground" }, Wp = { class: "mt-0.5 truncate text-xs text-muted-foreground" }, Kp = { class: "mt-5 border-t border-border pt-4" }, qp = ["aria-expanded"], Gp = {
  key: 0,
  id: "config-import-panel",
  class: "mt-3 flex flex-col gap-4"
}, Jp = {
  key: 0,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, Yp = {
  key: 1,
  class: "mt-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs"
}, Qp = {
  key: 0,
  class: "text-foreground"
}, Zp = {
  key: 1,
  class: "mt-1"
}, Xp = { class: "font-mono" }, em = {
  key: 2,
  class: "mt-1"
}, tm = {
  key: 3,
  class: "mt-1"
}, sm = { class: "ml-4 list-disc text-muted-foreground" }, nm = { class: "border-t border-border pt-4" }, om = { class: "flex gap-2" }, rm = {
  key: 0,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, lm = {
  key: 1,
  class: "mt-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs"
}, im = { class: "font-mono" }, am = { class: "border-t border-border pt-4" }, um = { class: "flex flex-wrap gap-2" }, dm = { class: "mb-6 rounded-lg border border-border bg-card p-4" }, cm = {
  key: 0,
  class: "mb-4 rounded-md border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
}, fm = {
  key: 1,
  class: "mb-4 flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-3 py-2 text-xs"
}, pm = { class: "font-mono font-medium" }, mm = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, gm = { class: "flex justify-self-end gap-2" }, hm = ["value"], bm = { class: "flex justify-self-end gap-2" }, vm = ["value"], ym = { class: "mt-5 border-t border-border pt-4" }, xm = {
  key: 0,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, _m = {
  key: 1,
  class: "mt-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-xs text-muted-foreground"
}, wm = {
  key: 2,
  class: "mt-2 text-xs text-muted-foreground"
}, km = {
  key: 3,
  class: "mt-2 flex max-h-64 flex-col gap-1 overflow-y-auto"
}, Sm = { class: "min-w-0 flex-1" }, Cm = { class: "font-mono font-medium" }, Am = {
  key: 0,
  class: "ml-1.5 font-mono text-muted-foreground"
}, Em = {
  key: 1,
  class: "truncate text-muted-foreground"
}, Im = {
  key: 1,
  class: "shrink-0 text-muted-foreground"
}, Tm = {
  key: 4,
  class: "mt-2 text-xs text-muted-foreground"
}, Pm = {
  key: 5,
  class: "mt-3"
}, Rm = { class: "flex flex-wrap gap-1.5" }, Mm = ["aria-label", "onClick"], Vm = {
  key: 6,
  class: "mt-3"
}, $m = { class: "flex flex-col gap-1" }, Om = { class: "flex-1" }, jm = ["aria-label", "onClick"], Nm = { class: "mt-4" }, Lm = { class: "mt-4 flex justify-end" }, Um = { class: "rounded-lg border border-border bg-card p-4" }, Dm = {
  key: 0,
  class: "flex items-center gap-2 rounded-md border border-neutral-800 bg-neutral-950 px-3 py-2.5"
}, Bm = {
  key: 1,
  class: "flex flex-col gap-4"
}, Fm = { class: "mb-2 flex items-center justify-between gap-3" }, Hm = { class: "flex items-center gap-2" }, zm = { class: "text-sm font-medium" }, Wm = { class: "text-xs text-muted-foreground" }, Km = {
  key: 0,
  class: "mb-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, qm = { class: "flex items-center gap-2 rounded-t-md border border-b-0 border-neutral-800 bg-neutral-950 px-3 py-1.5" }, Gm = { class: "font-mono text-[11px] text-neutral-400" }, Jm = { class: "max-h-48 overflow-auto rounded-b-md border border-neutral-800 bg-neutral-950 p-2.5 text-xs font-mono whitespace-pre-wrap text-neutral-200" }, Ym = {
  key: 2,
  id: "incus-panel-jails",
  role: "tabpanel",
  "aria-labelledby": "incus-tab-jails",
  tabindex: "0"
}, Qm = { class: "mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6" }, Zm = { class: "rounded-lg border border-border bg-card p-3" }, Xm = { class: "mt-1 font-mono text-xl" }, eg = { class: "rounded-lg border border-border bg-card p-3" }, tg = { class: "mt-1 font-mono text-xl" }, sg = { class: "rounded-lg border border-border bg-card p-3" }, ng = { class: "mt-1 font-mono text-xl" }, og = { class: "rounded-lg border border-border bg-card p-3" }, rg = { class: "mt-1.5" }, lg = { class: "rounded-lg border border-border bg-card p-3" }, ig = { class: "mt-1 font-mono text-xl" }, ag = { class: "rounded-lg border border-border bg-card p-3" }, ug = { class: "mt-1 font-mono text-xl" }, dg = {
  key: 0,
  viewBox: "0 0 80 24",
  width: "80",
  height: "24",
  class: "mt-1 text-primary",
  preserveAspectRatio: "none"
}, cg = ["points"], fg = { class: "mb-6 grid grid-cols-1 items-start gap-4 xl:grid-cols-2" }, pg = { class: "rounded-lg border border-border bg-card p-4" }, mg = { class: "grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-2 2xl:grid-cols-3" }, gg = { class: "mt-1 font-mono text-sm" }, hg = { class: "mt-1 font-mono text-sm" }, bg = { class: "mt-1 font-mono text-sm" }, vg = { class: "mt-1 font-mono text-sm" }, yg = { class: "mt-1 font-mono text-sm" }, xg = { class: "rounded-lg border border-border bg-card p-4" }, _g = { class: "flex flex-col gap-3 sm:flex-row sm:items-end" }, wg = { class: "flex-1" }, kg = { class: "flex-1" }, Sg = { value: "" }, Cg = ["value"], Ag = {
  key: 0,
  class: "mt-2 text-xs text-destructive"
}, Eg = { class: "mt-3 flex items-center gap-2.5" }, Ig = { class: "rounded-lg border border-border bg-card p-4" }, Tg = { class: "mb-4 flex items-center justify-between gap-3" }, Pg = {
  key: 0,
  class: "text-sm text-muted-foreground"
}, Rg = { class: "mb-3 text-xs text-muted-foreground" }, Mg = { class: "grid grid-cols-1 gap-4 xl:grid-cols-2" }, Vg = { class: "flex flex-wrap items-center justify-between gap-2" }, $g = { class: "flex min-w-0 items-center gap-2" }, Og = { class: "truncate font-mono text-[13px] font-medium" }, jg = {
  key: 0,
  class: "shrink-0 inline-flex items-center rounded-full bg-unraid-green-200 px-1.5 py-0.5 text-[10px] font-semibold text-unraid-green-800",
  title: "This container's IPv4 falls within the configured subnet."
}, Ng = { class: "shrink-0 font-mono text-xs text-muted-foreground" }, Lg = { class: "mt-3 grid grid-cols-2 gap-3" }, Ug = ["title"], Dg = { class: "mt-1 flex items-center gap-2" }, Bg = { class: "h-1.5 w-16 overflow-hidden rounded-full bg-muted" }, Fg = { class: "font-mono text-[13px]" }, Hg = {
  key: 0,
  viewBox: "0 0 80 24",
  width: "60",
  height: "18",
  class: "text-primary",
  preserveAspectRatio: "none"
}, zg = ["points"], Wg = { class: "mt-1 flex items-center gap-2" }, Kg = { class: "font-mono text-[13px]" }, qg = {
  key: 0,
  viewBox: "0 0 80 24",
  width: "60",
  height: "18",
  class: "text-primary",
  preserveAspectRatio: "none"
}, Gg = ["points"], Jg = {
  key: 0,
  class: "mt-1 h-1 w-20 overflow-hidden rounded-full bg-muted"
}, Yg = { class: "mt-3 flex flex-wrap gap-2" }, Qg = {
  key: 0,
  class: "mt-3 rounded-md border border-border bg-muted/30 p-3"
}, Zg = {
  key: 0,
  class: "text-xs text-muted-foreground"
}, Xg = { class: "grid grid-cols-2 gap-3 sm:grid-cols-4" }, eh = { class: "mt-1 font-mono text-xs" }, th = { class: "mt-1 font-mono text-xs" }, sh = { class: "mt-1 font-mono text-xs" }, nh = { class: "mt-1 font-mono text-xs" }, oh = { class: "mt-4 grid grid-cols-1 gap-3 border-t border-border pt-3 sm:grid-cols-2" }, rh = { class: "flex flex-wrap items-end gap-2" }, lh = { class: "flex gap-1.5" }, ih = { class: "flex gap-1.5" }, ah = { class: "flex gap-2" }, uh = {
  key: 0,
  class: "mt-3 flex flex-wrap items-center gap-3 rounded-md border border-orange-500/40 bg-orange-500/10 px-3 py-2 text-xs"
}, dh = {
  key: 1,
  class: "mt-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive"
}, ch = { class: "mt-4 border-t border-border pt-3" }, fh = { class: "mb-1 flex items-center gap-1.5 text-xs font-medium" }, ph = { class: "mt-4 border-t border-border pt-3" }, mh = { class: "flex flex-wrap gap-2" }, gh = {
  key: 0,
  class: "mt-1.5 text-xs text-unraid-green-800"
}, hh = {
  key: 1,
  class: "mt-1.5 text-xs text-destructive"
}, bh = { class: "mt-4 border-t border-border pt-3" }, vh = { class: "flex flex-wrap gap-2" }, yh = {
  key: 0,
  class: "mt-2"
}, xh = {
  key: 0,
  class: "mt-1 max-h-40 overflow-auto rounded-md border border-neutral-800 bg-neutral-950 p-2 text-[11px] whitespace-pre-wrap text-neutral-200"
}, _h = {
  key: 3,
  id: "incus-panel-config",
  role: "tabpanel",
  "aria-labelledby": "incus-tab-config",
  tabindex: "0"
}, wh = { class: "columns-1 gap-4 xl:columns-2" }, kh = { class: "mb-4 break-inside-avoid rounded-lg border border-border bg-card p-4" }, Sh = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, Ch = { class: "mt-4 border-t border-border pt-4" }, Ah = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, Eh = { class: "mb-4 break-inside-avoid rounded-lg border border-border bg-card p-4" }, Ih = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, Th = { class: "mt-4 border-t border-border pt-4" }, Ph = {
  key: 0,
  class: "mb-2 flex flex-wrap gap-1.5"
}, Rh = ["aria-label", "onClick"], Mh = { class: "flex gap-2" }, Vh = {
  key: 1,
  class: "mt-1.5 text-xs text-destructive"
}, $h = { class: "mt-4" }, Oh = {
  key: 0,
  class: "mb-2 flex flex-wrap gap-1.5"
}, jh = ["aria-label", "onClick"], Nh = { class: "flex gap-2" }, Lh = {
  key: 1,
  class: "mt-1.5 text-xs text-destructive"
}, Uh = { class: "mt-4 border-t border-border pt-4" }, Dh = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, Bh = { class: "flex justify-self-end gap-2" }, Fh = { class: "mb-4 break-inside-avoid rounded-lg border border-border bg-card p-4" }, Hh = { class: "grid max-w-xl grid-cols-[1fr_auto] items-center gap-y-4" }, zh = {
  key: 0,
  class: "col-span-2 -mt-2 text-xs text-destructive"
}, Wh = {
  key: 1,
  class: "col-span-2 -mt-2 text-xs text-destructive"
}, Kh = { class: "mt-4 border-t border-border pt-4" }, qh = { class: "mb-8 flex justify-end" }, Gh = 5e3, Go = "__other__", ds = "__other__", Jh = 400, Yh = /* @__PURE__ */ He({
  __name: "App",
  setup(e) {
    const t = /* @__PURE__ */ Zu(() => import("./incus-settings-Terminal-m9IzYAJr.js")), s = /* @__PURE__ */ L("jails"), n = /* @__PURE__ */ L(!0), o = /* @__PURE__ */ L(!1), l = /* @__PURE__ */ L(null), i = /* @__PURE__ */ L(!1), a = /* @__PURE__ */ L([]), u = /* @__PURE__ */ L(""), h = xe(() => fa(u.value)), g = xe(() => Pr(v.jailCpu)), x = xe(() => Rr(v.jailMemory)), A = /* @__PURE__ */ L(""), k = /* @__PURE__ */ L(!1), $ = /* @__PURE__ */ L(null), v = /* @__PURE__ */ Kt({
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
      stoppedJailsCount: z,
      totalMemoryUsageBytes: D,
      totalCpuUsageNs: q,
      fleetHistory: U,
      formatDuration: Z,
      formatBytes: $e,
      formatMemory: K,
      memoryFillPct: te,
      updateCpuSamplesAndHistory: Oe,
      cpuRateLabel: we,
      cpuRatePct: Me,
      cpuRateSuffix: ae,
      jailCpuHistory: he,
      totalCpuRateLabel: Je,
      sparklinePoints: ft
    } = Gf(a, () => v.jailCpu), Ce = xe(() => v.storageDriver === "zfs"), fe = /* @__PURE__ */ L(!1), ne = /* @__PURE__ */ L(""), Ae = /* @__PURE__ */ L(!1);
    async function Ye() {
      const c = await me(Jf);
      Object.assign(v, c.incusConfig);
    }
    let je = 0;
    async function De() {
      const c = ++je;
      try {
        const r = await me(Yf);
        if (c !== je) return;
        i.value = r.incusHealthy, a.value = r.jails, Oe();
      } catch {
        if (c !== je) return;
        i.value = !1;
      }
    }
    yi(async () => {
      try {
        await Ye(), await De(), await Promise.all([Ro(), Ln()]);
      } catch (c) {
        l.value = c instanceof Error ? c.message : String(c);
      } finally {
        n.value = !1;
      }
      s.value === "jails" && Or();
    }), vt(s, (c) => {
      c === "jails" ? (De(), Or()) : So();
    });
    async function Rn() {
      o.value = !0, l.value = null;
      try {
        const c = qf(v, {
          replacement: ne.value,
          clear: Ae.value
        });
        await me(Ul, { input: c }), (Ae.value || ne.value) && (v.tsAuthKeyConfigured = !Ae.value, ne.value = "", Ae.value = !1), await De();
      } catch (c) {
        l.value = c instanceof Error ? c.message : String(c);
      } finally {
        o.value = !1;
      }
    }
    async function Mn(c, r) {
      l.value = null;
      try {
        await me(Qf, { name: c, action: r }), await De();
      } catch (d) {
        l.value = d instanceof Error ? d.message : String(d);
      }
    }
    async function wo(c) {
      if (confirm(`Delete container "${c}"? This cannot be undone.`)) {
        l.value = null;
        try {
          await me(Zf, { name: c }), await De();
        } catch (r) {
          l.value = r instanceof Error ? r.message : String(r);
        }
      }
    }
    const kt = /* @__PURE__ */ L(!1);
    async function gs() {
      if (confirm("Delete every stopped container? Running containers are never touched. This cannot be undone.")) {
        kt.value = !0, l.value = null;
        try {
          (await me(gp)).deleteStoppedJails.length === 0 && (l.value = "No stopped containers to delete."), await De();
        } catch (c) {
          l.value = c instanceof Error ? c.message : String(c);
        } finally {
          kt.value = !1;
        }
      }
    }
    async function Ls() {
      if (!(!u.value.trim() || h.value)) {
        l.value = null;
        try {
          await me(Xf, {
            name: u.value.trim(),
            image: A.value || null,
            allowSudo: k.value
          }), u.value = "", k.value = !1, await De();
        } catch (c) {
          l.value = c instanceof Error ? c.message : String(c);
        }
      }
    }
    const Fe = /* @__PURE__ */ L(!1), {
      detailsJailName: oe,
      jailDetail: ze,
      detailLoading: m,
      detailError: b,
      editCpuLimit: w,
      editMemoryLimit: P,
      editWorkspacePath: E,
      toggleJailDetails: I,
      loadJailDetail: j
    } = yp(() => {
      Qe(), ie.value = !1, Us(), St.value = !1, de.value = "", ke.value = "", Ee.value = "", We.value = "", pt.value = null;
    });
    async function N() {
      if (!oe.value) return;
      const c = Pr(w.value);
      if (c) {
        b.value = c;
        return;
      }
      Fe.value = !0, b.value = "";
      try {
        await me(Ko, { name: oe.value, cpu: w.value.trim() }), await j(oe.value);
      } catch (r) {
        b.value = r instanceof Error ? r.message : String(r);
      } finally {
        Fe.value = !1;
      }
    }
    async function O() {
      if (!oe.value) return;
      const c = Rr(P.value);
      if (c) {
        b.value = c;
        return;
      }
      Fe.value = !0, b.value = "";
      try {
        await me(Ko, { name: oe.value, memory: P.value.trim() }), await j(oe.value);
      } catch (r) {
        b.value = r instanceof Error ? r.message : String(r);
      } finally {
        Fe.value = !1;
      }
    }
    async function T() {
      if (oe.value) {
        w.value = "", P.value = "", Fe.value = !0, b.value = "";
        try {
          await me(Ko, { name: oe.value, cpu: "", memory: "" }), await j(oe.value);
        } catch (c) {
          b.value = c instanceof Error ? c.message : String(c);
        } finally {
          Fe.value = !1;
        }
      }
    }
    async function Y() {
      if (!(!oe.value || !E.value.trim())) {
        Fe.value = !0, b.value = "";
        try {
          await me(op, {
            name: oe.value,
            hostPath: E.value.trim()
          }), await j(oe.value);
        } catch (c) {
          b.value = c instanceof Error ? c.message : String(c);
        } finally {
          Fe.value = !1;
        }
      }
    }
    async function B() {
      if (oe.value) {
        Fe.value = !0, b.value = "";
        try {
          await me(rp, { name: oe.value }), await j(oe.value);
        } catch (c) {
          b.value = c instanceof Error ? c.message : String(c);
        } finally {
          Fe.value = !1;
        }
      }
    }
    function G(c) {
      var r;
      return !c.workspaceIsOverride && !!((r = c.workspaceHostPath) != null && r.endsWith("/default-workspace"));
    }
    const Q = /* @__PURE__ */ L(!1);
    async function ue() {
      if (oe.value) {
        Q.value = !0, b.value = "";
        try {
          await me(hp, { name: oe.value }), await j(oe.value);
        } catch (c) {
          b.value = c instanceof Error ? c.message : String(c);
        } finally {
          Q.value = !1;
        }
      }
    }
    const de = /* @__PURE__ */ L(""), ie = /* @__PURE__ */ L(!1), ke = /* @__PURE__ */ L(""), Ee = /* @__PURE__ */ L("");
    let nt = null;
    function Qe() {
      nt !== null && (nt.stop(), nt = null);
    }
    async function Jt() {
      if (!oe.value || !de.value.trim()) return;
      const c = oe.value;
      Qe(), ie.value = !0, ke.value = "", Ee.value = "";
      try {
        const d = (await me(bp, {
          name: c,
          formula: de.value.trim()
        })).installHomebrewFormula;
        nt = Kn(async (V) => {
          try {
            const F = await me(
              vp,
              { id: d }
            );
            if (!V.isActive() || oe.value !== c) return;
            const ee = F.homebrewInstallStatus;
            if (!ee || ee.status === "running") return;
            Qe(), ie.value = !1, ee.status === "success" ? (ke.value = ee.message, de.value = "") : Ee.value = ee.message;
          } catch (F) {
            if (!V.isActive() || oe.value !== c) return;
            Qe(), ie.value = !1, Ee.value = F instanceof Error ? F.message : String(F);
          }
        }, 2e3);
      } catch (r) {
        Ee.value = r instanceof Error ? r.message : String(r), ie.value = !1;
      }
    }
    const rs = /* @__PURE__ */ L(!1);
    async function ot() {
      if (oe.value) {
        rs.value = !0, b.value = "";
        try {
          await me(tp, { name: oe.value }), await j(oe.value);
        } catch (c) {
          b.value = c instanceof Error ? c.message : String(c);
        } finally {
          rs.value = !1;
        }
      }
    }
    const We = /* @__PURE__ */ L(""), St = /* @__PURE__ */ L(!1), pt = /* @__PURE__ */ L(null);
    let Vn = null;
    function Us() {
      Vn !== null && (Vn.stop(), Vn = null);
    }
    async function Ir() {
      if (!(!oe.value || !We.value.trim())) {
        Us(), St.value = !0, pt.value = null, b.value = "";
        try {
          const r = (await me(sp, {
            name: oe.value,
            command: We.value.trim()
          })).startPrivilegedCommand, d = oe.value;
          Vn = Kn(async (V) => {
            try {
              const F = await me(
                np,
                { id: r }
              );
              if (!V.isActive() || oe.value !== d) return;
              const ee = F.privilegedCommandStatus;
              if (!ee || ee.status === "running") return;
              Us(), St.value = !1, pt.value = ee;
            } catch (F) {
              if (!V.isActive() || oe.value !== d) return;
              Us(), St.value = !1, b.value = F instanceof Error ? F.message : String(F);
            }
          }, 2e3);
        } catch (c) {
          b.value = c instanceof Error ? c.message : String(c), St.value = !1;
        }
      }
    }
    function ia(c) {
      const r = c.toLowerCase();
      return r === "running" ? "green" : r === "stopped" ? "gray" : "orange";
    }
    function ko(c) {
      return c.split(",").map((r) => r.trim()).filter((r) => r.length > 0);
    }
    function aa() {
      return ko(v.aclBlock).length;
    }
    const Tr = /^[0-9a-fA-F:.]+\/\d{1,3}$/, ua = /^\d+(-\d+)?(,\d+(-\d+)?)*$/, da = /^\d+(\.\d+)?(B|KB|MB|GB|TB|PB|KiB|MiB|GiB|TiB|PiB)?$/i, ca = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
    function Pr(c) {
      return c.trim() ? ua.test(c.trim()) ? "" : `"${c}" doesn't look like a CPU limit — expected a core count (e.g. 2) or a set/range (e.g. 0-3).` : "";
    }
    function Rr(c) {
      return c.trim() ? da.test(c.trim()) ? "" : `"${c}" doesn't look like a memory limit — expected a byte count with an optional unit (e.g. 4GiB).` : "";
    }
    function fa(c) {
      return c.trim() ? ca.test(c.trim()) ? "" : `"${c}" isn't a valid container name — letters, digits, and hyphens only, can't start or end with a hyphen.` : "";
    }
    const Ds = xe(() => ko(v.aclBlock)), Bs = xe(() => ko(v.aclAllow)), Fs = /* @__PURE__ */ L(""), Hs = /* @__PURE__ */ L(""), zs = /* @__PURE__ */ L(""), Ws = /* @__PURE__ */ L("");
    function Mr() {
      const c = Fs.value.trim();
      if (zs.value = "", !!c) {
        if (!Tr.test(c)) {
          zs.value = `"${c}" doesn't look like a CIDR — expected e.g. 10.0.0.0/8 or fd00::/8.`;
          return;
        }
        if (Ds.value.includes(c)) {
          zs.value = `${c} is already in the list.`;
          return;
        }
        v.aclBlock = [...Ds.value, c].join(","), Fs.value = "";
      }
    }
    function pa(c) {
      v.aclBlock = Ds.value.filter((r) => r !== c).join(",");
    }
    function Vr() {
      const c = Hs.value.trim();
      if (Ws.value = "", !!c) {
        if (!Tr.test(c)) {
          Ws.value = `"${c}" doesn't look like a CIDR — expected e.g. 100.64.0.0/10 or fd00::/8.`;
          return;
        }
        if (Bs.value.includes(c)) {
          Ws.value = `${c} is already in the list.`;
          return;
        }
        v.aclAllow = [...Bs.value, c].join(","), Hs.value = "";
      }
    }
    function ma(c) {
      v.aclAllow = Bs.value.filter((r) => r !== c).join(",");
    }
    function $r(c) {
      const r = c.split(".");
      if (r.length !== 4) return null;
      let d = 0;
      for (const V of r) {
        if (!/^\d{1,3}$/.test(V)) return null;
        const F = Number(V);
        if (F < 0 || F > 255) return null;
        d = d << 8 | F;
      }
      return d >>> 0;
    }
    function ga(c, r) {
      const [d, V] = r.split("/");
      if (!d || V === void 0) return !1;
      const F = Number(V);
      if (!Number.isInteger(F) || F < 0 || F > 32) return !1;
      const ee = $r(c), Be = $r(d);
      if (ee === null || Be === null) return !1;
      if (F === 0) return !0;
      const Ze = 4294967295 << 32 - F >>> 0;
      return (ee & Ze) === (Be & Ze);
    }
    function ha(c) {
      return !c.ipv4 || !v.jailSubnet || c.status.toLowerCase() !== "running" ? !1 : ga(c.ipv4, v.jailSubnet);
    }
    let $n = null;
    function Or() {
      So(), $n = Kn(De, Gh);
    }
    function So() {
      $n !== null && ($n.stop(), $n = null);
    }
    const jr = [
      { value: "debian", label: "Debian" },
      { value: "ubuntu", label: "Ubuntu" },
      { value: "alpinelinux", label: "Alpine Linux" },
      { value: "rockylinux", label: "Rocky Linux" },
      { value: "almalinux", label: "AlmaLinux" },
      { value: "fedora", label: "Fedora" }
    ], jt = {
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
    }, Nr = {
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
    }, at = /* @__PURE__ */ L("debian"), Ct = /* @__PURE__ */ L(""), On = /* @__PURE__ */ L(""), Yt = /* @__PURE__ */ L(""), Lr = xe(() => at.value === Go), Ur = xe(() => Ct.value === ds), Co = xe(() => Lr.value ? On.value : at.value), Ao = xe(
      () => Ur.value ? Yt.value : Ct.value
    ), ba = xe(() => jt[at.value] ?? []);
    vt(at, () => {
      const c = jt[at.value];
      Ct.value = c && c.length > 0 ? c[0].value : ds, Yt.value = "";
    });
    {
      const c = jt[at.value];
      Ct.value = c && c.length > 0 ? c[0].value : ds;
    }
    const ls = /* @__PURE__ */ L(""), hs = /* @__PURE__ */ L(""), jn = /* @__PURE__ */ L(!1), Ks = /* @__PURE__ */ L(null), qs = /* @__PURE__ */ L([]), bs = /* @__PURE__ */ L(null), Gs = /* @__PURE__ */ L(!1);
    function va(c) {
      return c.split(/[\n,]/).map((r) => r.trim()).filter((r) => r.length > 0);
    }
    function Dr() {
      const c = va(ls.value);
      return Array.from(/* @__PURE__ */ new Set([...Array.from(Ne), ...c]));
    }
    const is = /* @__PURE__ */ L(""), vs = /* @__PURE__ */ L([]), Js = /* @__PURE__ */ L([]), Eo = /* @__PURE__ */ L(!1), Ys = /* @__PURE__ */ L(null);
    let ys = null, xs = 0;
    const Ne = /* @__PURE__ */ Kt(/* @__PURE__ */ new Set()), Le = /* @__PURE__ */ Kt(/* @__PURE__ */ new Map()), Br = { apt: "apt", npm: "npm", pypi: "PyPI", brew: "brew" };
    function Fr() {
      if (ys && clearTimeout(ys), ys = null, ++xs, is.value.trim().length < 2) {
        vs.value = [], Js.value = [], Ys.value = null;
        return;
      }
      ys = setTimeout(ya, Jh);
    }
    vt(is, Fr), vt(at, () => {
      Ne.clear(), Le.clear(), Fr();
    });
    async function ya() {
      const c = is.value.trim();
      if (c.length < 2) return;
      const r = xs;
      Eo.value = !0, Ys.value = null;
      try {
        const d = await me(
          ap,
          { query: c, distro: Co.value, release: Ao.value }
        );
        if (r !== xs) return;
        vs.value = d.searchAllPackages.results, Js.value = d.searchAllPackages.errors;
      } catch (d) {
        if (r !== xs) return;
        Ys.value = d instanceof Error ? d.message : String(d), vs.value = [], Js.value = [];
      } finally {
        r === xs && (Eo.value = !1);
      }
    }
    function xa(c) {
      Ne.add(c.name);
    }
    function _a(c) {
      Ne.delete(c);
    }
    function Io(c) {
      var d;
      const r = (d = Nr[at.value]) == null ? void 0 : d.find((V) => V.key === c);
      if (r)
        for (const V of r.packages) Ne.add(V);
    }
    function wa(c) {
      Io("nodejs"), Le.set(`npm:${c.name}`, `npm install -g ${c.name}`);
    }
    function ka(c) {
      Io("python3"), Le.set(`pypi:${c.name}`, `pip3 install ${c.name}`);
    }
    function Sa(c) {
      Le.delete(c);
    }
    function Ca(c) {
      c.ecosystem === "apt" ? xa(c) : c.ecosystem === "npm" ? wa(c) : c.ecosystem === "pypi" && ka(c);
    }
    function Hr(c) {
      return c.ecosystem === "apt" ? Ne.has(c.name) : c.ecosystem === "npm" ? Le.has(`npm:${c.name}`) : c.ecosystem === "pypi" ? Le.has(`pypi:${c.name}`) : !1;
    }
    function To(c, r) {
      jr.some((d) => d.value === c) ? (at.value = c, (jt[c] ?? []).some((V) => V.value === r) ? (Ct.value = r, Yt.value = "") : (Ct.value = ds, Yt.value = r)) : (at.value = Go, On.value = c, Ct.value = ds, Yt.value = r);
    }
    function Qs() {
      bs.value = null;
    }
    function Aa(c) {
      var ee, Be, Ze, ut;
      const r = c.toLowerCase(), d = (Pe) => Pe.find((bt) => r.includes(bt));
      if (r.includes("alpine")) {
        const Pe = (ee = r.match(/(\d+\.\d+)/)) == null ? void 0 : ee[1];
        return { distro: "alpinelinux", release: Pe && jt.alpinelinux.some(($o) => $o.value === Pe) ? Pe : "3.24" };
      }
      if (r.includes("fedora")) {
        const Pe = (Be = r.match(/fedora[:\-](\d+)/)) == null ? void 0 : Be[1];
        return { distro: "fedora", release: Pe && jt.fedora.some(($o) => $o.value === Pe) ? Pe : "44" };
      }
      if (r.includes("rockylinux") || r.includes("rocky")) {
        const Pe = (Ze = r.match(/(\d+)/)) == null ? void 0 : Ze[1];
        return { distro: "rockylinux", release: Pe === "9" || Pe === "10" ? Pe : "10" };
      }
      if (r.includes("almalinux") || r.includes("alma")) {
        const Pe = (ut = r.match(/(\d+)/)) == null ? void 0 : ut[1];
        return { distro: "almalinux", release: Pe === "9" || Pe === "10" ? Pe : "10" };
      }
      const V = d(["jammy", "noble", "resolute", "focal", "bionic"]);
      if (r.includes("ubuntu") || V)
        return { distro: "ubuntu", release: V && jt.ubuntu.some((bt) => bt.value === V) ? V : "noble" };
      const F = d(["bookworm", "trixie", "sid", "bullseye", "buster"]);
      return r.includes("debian") || F || r.startsWith("node:") || r.startsWith("python:") || r.includes("/node") || r.includes("/python") ? { distro: "debian", release: F && jt.debian.some((bt) => bt.value === F) ? F : "bookworm" } : null;
    }
    function Ea(c) {
      const r = c.toLowerCase();
      return r.includes("/node") ? "nodejs" : r.includes("/python") ? "python3" : null;
    }
    function Ia(c) {
      var F;
      const r = JSON.parse(Ta(c)), d = { distroSet: !1, packagesAdded: [], commandsAdded: [], skipped: [] };
      if (Qs(), Ne.clear(), Le.clear(), ls.value = "", typeof r.image == "string") {
        const ee = Aa(r.image);
        ee ? (To(ee.distro, ee.release), d.distroSet = !0) : d.skipped.push(`image "${r.image}" — couldn't infer a matching distro/release, pick manually`);
      } else r.build && d.skipped.push(`"build.dockerfile" — Dockerfile-based devcontainers aren't translated, pick a distro/release manually`);
      if (r.features && typeof r.features == "object")
        for (const ee of Object.keys(r.features)) {
          const Be = Ea(ee);
          if (Be) {
            const Ze = (F = Nr[at.value]) == null ? void 0 : F.find((ut) => ut.key === Be);
            if (Ze) {
              for (const ut of Ze.packages)
                Ne.has(ut) || (Ne.add(ut), d.packagesAdded.push(ut));
              continue;
            }
          }
          if (ee.includes("/git")) {
            Ne.has("git") || (Ne.add("git"), d.packagesAdded.push("git"));
            continue;
          }
          if (ee.includes("/common-utils")) {
            for (const Ze of ["curl", "sudo", "ca-certificates"])
              Ne.has(Ze) || (Ne.add(Ze), d.packagesAdded.push(Ze));
            continue;
          }
          d.skipped.push(`feature "${ee}" — not recognized, add its packages manually if needed`);
        }
      const V = [
        ["postCreateCommand", r.postCreateCommand],
        ["postStartCommand", r.postStartCommand]
      ];
      for (const [ee, Be] of V) {
        if (!Be) continue;
        (Array.isArray(Be) ? Be.map(String) : [String(Be)]).forEach((ut, Pe) => {
          const bt = `devcontainer:${ee}:${Pe}`;
          Le.set(bt, ut), d.commandsAdded.push(ut);
        });
      }
      return (r.remoteUser || r.containerUser) && d.skipped.push(`remoteUser/containerUser "${r.remoteUser ?? r.containerUser}" — not mapped, this plugin uses one fixed agent user (Config → Jail Defaults)`), (r.forwardPorts || r.mounts || r.workspaceFolder) && d.skipped.push("forwardPorts/mounts/workspaceFolder — IDE/runtime concerns, not applicable to image building"), d;
    }
    function Ta(c) {
      return c.replace(/\/\/.*$/gm, "").replace(/,(\s*[}\]])/g, "$1");
    }
    const Zs = /* @__PURE__ */ L(null), At = /* @__PURE__ */ L(null), zr = /* @__PURE__ */ L(null);
    function Pa() {
      var c;
      (c = zr.value) == null || c.click();
    }
    function Ra(c) {
      var V;
      const r = (V = c.target.files) == null ? void 0 : V[0];
      if (!r) return;
      Zs.value = null, At.value = null;
      const d = new FileReader();
      d.onload = () => {
        try {
          At.value = Ia(String(d.result));
        } catch (F) {
          Zs.value = F instanceof Error ? F.message : String(F);
        }
      }, d.onerror = () => {
        Zs.value = "Failed to read the file.";
      }, d.readAsText(r), c.target.value = "";
    }
    function Ma(c) {
      const r = c == null ? void 0 : c.tools;
      if (!r || typeof r != "object") return [];
      const d = [];
      for (const [V, F] of Object.entries(r))
        typeof F == "string" ? d.push({ tool: V, version: F }) : Array.isArray(F) && typeof F[0] == "string" ? d.push({ tool: V, version: F[0] }) : F && typeof F == "object" && typeof F.version == "string" && d.push({ tool: V, version: F.version });
      return d;
    }
    function Va(c) {
      const r = [];
      for (const d of c.split(`
`)) {
        const V = d.split("#")[0].trim();
        if (!V) continue;
        const [F, ee] = V.split(/\s+/);
        F && ee && r.push({ tool: F, version: ee });
      }
      return r;
    }
    function Wr() {
      Io("build-tools"), Ne.has("curl") || Ne.add("curl"), Ne.has("ca-certificates") || Ne.add("ca-certificates"), Le.set("mise:env", "export MISE_DATA_DIR=/opt/mise MISE_CONFIG_DIR=/etc/mise"), Le.set("mise:install", "curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh"), Le.set(
        "mise:profile",
        `printf 'export MISE_DATA_DIR=/opt/mise MISE_CONFIG_DIR=/etc/mise\\neval "$(/usr/local/bin/mise activate bash)"\\n' > /etc/profile.d/mise.sh && chmod +x /etc/profile.d/mise.sh`
      );
    }
    function Kr(c) {
      if (c.length === 0) return [];
      Wr();
      const r = c.map((d) => `${d.tool}@${d.version}`);
      return Le.set("mise:use-tools", `mise use -g ${r.join(" ")}`), r;
    }
    async function $a(c) {
      const d = (await import("./incus-settings-index-D8Q71tKU.js")).parse(c), V = Ma(d);
      if (V.length === 0) throw new Error("No [tools] entries found in this mise.toml.");
      return { toolsAdded: Kr(V) };
    }
    function Oa(c) {
      const r = Va(c);
      if (r.length === 0) throw new Error("No tool/version lines found in this .tool-versions file.");
      return { toolsAdded: Kr(r) };
    }
    const _s = /* @__PURE__ */ L(null), Xs = /* @__PURE__ */ L(null), qr = /* @__PURE__ */ L(null), Gr = /* @__PURE__ */ L(null);
    function Jr(c, r) {
      var F;
      const d = (F = c.target.files) == null ? void 0 : F[0];
      if (!d) return;
      _s.value = null, Xs.value = null;
      const V = new FileReader();
      V.onload = async () => {
        try {
          const ee = r === "toml" ? await $a(String(V.result)) : Oa(String(V.result));
          Xs.value = ee.toolsAdded;
        } catch (ee) {
          _s.value = ee instanceof Error ? ee.message : String(ee);
        }
      }, V.onerror = () => {
        _s.value = "Failed to read the file.";
      }, V.readAsText(d), c.target.value = "";
    }
    const ws = /* @__PURE__ */ L(""), en = /* @__PURE__ */ L("");
    function ja() {
      const c = ws.value.trim();
      if (!c) return;
      Wr(), Ne.has("git") || Ne.add("git");
      const r = en.value.trim(), d = r ? `git clone --depth 1 --branch ${r} ${c} /opt/dotfiles-src` : `git clone --depth 1 ${c} /opt/dotfiles-src`;
      Le.set("mise:dotfiles-clone", d), Le.set(
        "mise:dotfiles-bootstrap",
        "cp /opt/dotfiles-src/mise.toml /opt/dotfiles-src/.mise.toml /etc/mise/config.d/dotfiles.toml 2>/dev/null; MISE_EXPERIMENTAL=1 mise bootstrap --yes || true"
      );
    }
    function Na() {
      Le.delete("mise:dotfiles-clone"), Le.delete("mise:dotfiles-bootstrap"), ws.value = "", en.value = "";
    }
    const Po = /* @__PURE__ */ L([]), tn = /* @__PURE__ */ L(""), Nn = /* @__PURE__ */ L(!1), ks = /* @__PURE__ */ L(null);
    async function Ro() {
      const c = await me(dp);
      Po.value = c.builderPresets;
    }
    async function La() {
      const c = tn.value.trim();
      if (c) {
        ks.value = null, Nn.value = !0;
        try {
          await me(cp, {
            input: {
              name: c,
              distro: Co.value.trim(),
              release: Ao.value.trim(),
              packages: Dr()
            }
          }), tn.value = "", await Ro();
        } catch (r) {
          ks.value = r instanceof Error ? r.message : String(r);
        } finally {
          Nn.value = !1;
        }
      }
    }
    function Ua(c) {
      To(c.distro, c.release), ls.value = c.packages.join(`
`), hs.value = "", Qs();
    }
    async function Da(c) {
      ks.value = null;
      try {
        await me(fp, { name: c }), await Ro();
      } catch (r) {
        ks.value = r instanceof Error ? r.message : String(r);
      }
    }
    const Et = /* @__PURE__ */ L([]), Nt = /* @__PURE__ */ L(null), Mo = /* @__PURE__ */ L(null);
    async function Ln() {
      const c = await me(pp);
      Et.value = c.jailImages;
    }
    async function Ba(c) {
      var V;
      Nt.value = null, Mo.value = c.alias;
      const r = !c.isMaster, d = ((V = Et.value.find((F) => F.isMaster)) == null ? void 0 : V.alias) ?? null;
      try {
        await me(qo, { alias: c.alias, isMaster: r }), r && await me(Ul, { input: { jailImage: c.alias } }), await Promise.all([Ln(), Ye()]);
      } catch (F) {
        await Promise.allSettled([
          d ? me(qo, { alias: d, isMaster: !0 }) : me(qo, { alias: c.alias, isMaster: !1 })
        ]), await Promise.allSettled([Ln(), Ye()]), Nt.value = F instanceof Error ? F.message : String(F);
      } finally {
        Mo.value = null;
      }
    }
    function Fa(c) {
      To(c.distro, c.release), ls.value = c.packages.join(`
`), hs.value = "", bs.value = c.alias;
    }
    const Vo = /* @__PURE__ */ L(null);
    async function Ha(c) {
      if (confirm(`Delete image "${c.alias}"? This removes it from Incus and cannot be undone.`)) {
        Nt.value = null, Vo.value = c.alias;
        try {
          await me(ip, { alias: c.alias }), Et.value = Et.value.filter((r) => r.alias !== c.alias), bs.value === c.alias && Qs();
        } catch (r) {
          Nt.value = r instanceof Error ? r.message : String(r);
        } finally {
          Vo.value = null;
        }
      }
    }
    function za(c) {
      return c.length === 0 ? "no packages" : c.join(", ");
    }
    const Un = /* @__PURE__ */ L(!1), sn = /* @__PURE__ */ L("");
    async function Wa() {
      Un.value = !0, Nt.value = null, sn.value = "";
      try {
        const c = await me(mp);
        c.pruneStaleImageRecords.length === 0 ? sn.value = "Nothing to prune — every saved image still exists in Incus." : (sn.value = `Untracked ${c.pruneStaleImageRecords.length}: ${c.pruneStaleImageRecords.join(", ")}`, Et.value = Et.value.filter((r) => !c.pruneStaleImageRecords.includes(r.alias)));
      } catch (c) {
        Nt.value = c instanceof Error ? c.message : String(c);
      } finally {
        Un.value = !1;
      }
    }
    function Dn(c) {
      c.intervalId !== null && (c.intervalId.stop(), c.intervalId = null);
    }
    function Ka(c) {
      c.intervalId = Kn(async (r) => {
        var d, V;
        try {
          const F = await me(up, {
            buildId: c.buildId
          });
          if (!r.isActive()) return;
          if (c.status = F.jailImageBuildStatus, ((d = c.status) == null ? void 0 : d.status) === "success") {
            Dn(c);
            try {
              await Ln();
            } catch (ee) {
              Nt.value = ee instanceof Error ? ee.message : String(ee);
            }
          } else ((V = c.status) == null ? void 0 : V.status) === "failed" && Dn(c);
        } catch (F) {
          if (!r.isActive()) return;
          c.error = F instanceof Error ? F.message : String(F), Dn(c);
        }
      }, 2e3);
    }
    async function qa() {
      Ks.value = null;
      const c = Co.value.trim(), r = Ao.value.trim(), d = hs.value.trim(), V = Dr();
      if (!c || !r || !d) {
        Ks.value = "Distro, release, and alias are required.";
        return;
      }
      jn.value = !0;
      try {
        const ee = {
          buildId: (await me(lp, {
            distro: c,
            release: r,
            packages: V,
            alias: d,
            basedOn: bs.value || null,
            postInstallCommands: Array.from(Le.values())
          })).buildJailImage,
          distro: c,
          release: r,
          alias: d,
          status: null,
          error: null,
          intervalId: null
        };
        qs.value.unshift(ee), Ka(qs.value[0]);
        const Be = jt[at.value];
        Ct.value = Be && Be.length > 0 ? Be[0].value : ds, Yt.value = "", hs.value = "", ls.value = "", Ne.clear(), Le.clear(), vs.value = [], is.value = "", Xs.value = null, _s.value = null, ws.value = "", en.value = "", Qs();
      } catch (F) {
        Ks.value = F instanceof Error ? F.message : String(F);
      } finally {
        jn.value = !1;
      }
    }
    function Ga(c) {
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
    return _i(() => {
      ++je, ++xs;
      for (const c of qs.value) Dn(c);
      So(), Qe(), Us(), ys && clearTimeout(ys);
    }), (c, r) => (C(), R("div", xp, [
      n.value ? (C(), R("div", _p, "Loading incus configuration…")) : (C(), R(ce, { key: 1 }, [
        l.value ? (C(), R("div", wp, M(l.value), 1)) : W("", !0),
        f("header", kp, [
          r[53] || (r[53] = Ld('<svg width="14" height="20" viewBox="0 0 10 14" fill="none" aria-hidden="true" class="shrink-0 text-foreground"><path d="M5 0L9 2.5L5 5L1 2.5Z" fill="currentColor" opacity="0.95"></path><path d="M5 3L9 5.5L5 8L1 5.5Z" fill="currentColor" opacity="0.7"></path><path d="M5 6L9 8.5L5 11L1 8.5Z" fill="currentColor" opacity="0.45"></path><path d="M5 9L9 11.5L5 14L1 11.5Z" fill="currentColor" opacity="0.25"></path></svg><span class="text-sm font-semibold tracking-[0.14em] uppercase">Incus</span><span class="text-xs text-muted-foreground">dev containers</span>', 3)),
          f("div", Sp, [
            y(p(Dt), {
              variant: i.value ? "green" : "red"
            }, {
              default: S(() => [
                _(M(i.value ? "Reachable" : "Not running"), 1)
              ]),
              _: 1
            }, 8, ["variant"]),
            y(p(pe), {
              size: "sm",
              variant: "outline",
              onClick: De
            }, {
              default: S(() => [...r[52] || (r[52] = [
                _("Refresh", -1)
              ])]),
              _: 1
            })
          ])
        ]),
        y(Hf, {
          modelValue: s.value,
          "onUpdate:modelValue": r[0] || (r[0] = (d) => s.value = d)
        }, null, 8, ["modelValue"]),
        s.value === "builder" ? (C(), R("section", Cp, [
          f("div", Ap, [
            f("div", null, [
              r[78] || (r[78] = f("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Starting points", -1)),
              f("div", Ep, [
                r[77] || (r[77] = f("h3", { class: "mb-2 text-sm font-semibold" }, "Presets", -1)),
                ks.value ? (C(), R("p", Ip, M(ks.value), 1)) : W("", !0),
                Po.value.length === 0 ? (C(), R("p", Tp, "Save the form below as a preset to reuse it later.")) : (C(), R("div", Pp, [
                  (C(!0), R(ce, null, Xe(Po.value, (d) => (C(), R("div", {
                    key: d.name,
                    class: "flex items-center gap-2 rounded-md border border-border px-2.5 py-1.5 text-xs"
                  }, [
                    f("button", {
                      type: "button",
                      class: "cursor-pointer font-medium hover:text-primary",
                      onClick: (V) => Ua(d)
                    }, M(d.name), 9, Rp),
                    f("span", Mp, M(d.distro) + "/" + M(d.release), 1),
                    f("button", {
                      type: "button",
                      class: "cursor-pointer text-muted-foreground hover:text-destructive",
                      "aria-label": "Delete preset",
                      onClick: (V) => Da(d.name)
                    }, "✕", 8, Vp)
                  ]))), 128))
                ])),
                f("div", $p, [
                  y(p(re), {
                    for: "new-preset-name",
                    class: "sr-only"
                  }, {
                    default: S(() => [...r[54] || (r[54] = [
                      _("Preset name", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(be), {
                    id: "new-preset-name",
                    modelValue: tn.value,
                    "onUpdate:modelValue": r[1] || (r[1] = (d) => tn.value = d),
                    placeholder: "Preset name",
                    class: "w-56"
                  }, null, 8, ["modelValue"]),
                  y(p(pe), {
                    size: "sm",
                    variant: "outline",
                    disabled: Nn.value || !tn.value.trim(),
                    onClick: La
                  }, {
                    default: S(() => [
                      _(M(Nn.value ? "Saving…" : "Save as preset"), 1)
                    ]),
                    _: 1
                  }, 8, ["disabled"])
                ]),
                y(p(le), null, {
                  default: S(() => [...r[55] || (r[55] = [
                    _(" Saves distro, release, and the current package/tool list — not the alias, since that should stay unique per build. Saving under a name that already exists overwrites it. ", -1)
                  ])]),
                  _: 1
                }),
                f("div", Op, [
                  f("div", jp, [
                    r[56] || (r[56] = f("h3", { class: "text-sm font-semibold" }, "Saved images", -1)),
                    Et.value.length > 0 ? (C(), Te(p(pe), {
                      key: 0,
                      size: "sm",
                      variant: "outline",
                      disabled: Un.value,
                      onClick: Wa
                    }, {
                      default: S(() => [
                        _(M(Un.value ? "Checking…" : "Prune stale records"), 1)
                      ]),
                      _: 1
                    }, 8, ["disabled"])) : W("", !0)
                  ]),
                  Nt.value ? (C(), R("p", Np, M(Nt.value), 1)) : W("", !0),
                  sn.value ? (C(), R("p", Lp, M(sn.value), 1)) : W("", !0),
                  Et.value.length === 0 ? (C(), R("p", Up, " No images built yet — the first one you build can become the golden master. ")) : (C(), R("div", Dp, [
                    (C(!0), R(ce, null, Xe([...Et.value].sort((d, V) => (V.isMaster ? 1 : 0) - (d.isMaster ? 1 : 0)), (d) => (C(), R("div", {
                      key: d.alias,
                      class: lt(["flex items-center gap-3 rounded-md border px-3 py-2", d.isMaster ? "border-primary bg-primary/5" : "border-border"])
                    }, [
                      f("div", Bp, [
                        f("div", Fp, [
                          f("span", Hp, M(d.alias), 1),
                          d.isMaster ? (C(), Te(p(Dt), {
                            key: 0,
                            variant: "orange"
                          }, {
                            default: S(() => [...r[57] || (r[57] = [
                              _("Golden master", -1)
                            ])]),
                            _: 1
                          })) : W("", !0),
                          f("span", zp, M(d.distro) + "/" + M(d.release), 1)
                        ]),
                        f("p", Wp, M(za(d.packages)), 1)
                      ]),
                      y(p(pe), {
                        size: "sm",
                        variant: "outline",
                        disabled: Mo.value === d.alias,
                        onClick: (V) => Ba(d),
                        title: d.isMaster ? "Stop launching new containers from this image by default" : "New containers launch from this image by default"
                      }, {
                        default: S(() => [
                          _(M(d.isMaster ? "Unset default" : "Set as default"), 1)
                        ]),
                        _: 2
                      }, 1032, ["disabled", "onClick", "title"]),
                      y(p(pe), {
                        size: "sm",
                        variant: "secondary",
                        onClick: (V) => Fa(d)
                      }, {
                        default: S(() => [...r[58] || (r[58] = [
                          _("Build variant", -1)
                        ])]),
                        _: 1
                      }, 8, ["onClick"]),
                      y(p(pe), {
                        size: "sm",
                        variant: "destructive",
                        disabled: Vo.value === d.alias,
                        onClick: (V) => Ha(d)
                      }, {
                        default: S(() => [...r[59] || (r[59] = [
                          _("Delete", -1)
                        ])]),
                        _: 1
                      }, 8, ["disabled", "onClick"])
                    ], 2))), 128))
                  ])),
                  y(p(le), null, {
                    default: S(() => [...r[60] || (r[60] = [
                      _(` Only one image can be the golden master at a time — marking a new one unmarks the previous. Marking it also sets it as the default image new containers launch from (Config → Container Defaults), so this is more than a label. "Build variant" pre-fills the form from that image's distro/release/packages so you can edit, extend, or strip it down before building a new one. "Prune stale records" checks every saved image still actually exists in Incus and untracks any that don't — useful if one was deleted directly via the incus CLI instead of through here. `, -1)
                    ])]),
                    _: 1
                  })
                ]),
                f("div", Kp, [
                  f("button", {
                    type: "button",
                    "aria-expanded": Gs.value,
                    "aria-controls": "config-import-panel",
                    class: "flex w-full cursor-pointer items-center gap-1.5 text-left text-sm font-semibold",
                    onClick: r[2] || (r[2] = (d) => Gs.value = !Gs.value)
                  }, [
                    f("span", {
                      class: lt(["text-muted-foreground transition-transform", Gs.value ? "rotate-90" : ""])
                    }, "▸", 2),
                    r[61] || (r[61] = _(" Import from a config file ", -1)),
                    r[62] || (r[62] = f("span", { class: "font-normal text-xs text-muted-foreground" }, "devcontainer.json, mise.toml, .tool-versions", -1))
                  ], 8, qp),
                  Gs.value ? (C(), R("div", Gp, [
                    f("div", null, [
                      r[67] || (r[67] = f("p", { class: "mb-2 text-xs text-muted-foreground" }, " devcontainer.json — maps the base image and recognized features to real packages; anything that isn't applicable to image building is reported, not silently dropped. ", -1)),
                      f("input", {
                        ref_key: "devcontainerFileInput",
                        ref: zr,
                        type: "file",
                        accept: ".json,application/json",
                        class: "hidden",
                        onChange: Ra
                      }, null, 544),
                      y(p(pe), {
                        size: "sm",
                        variant: "outline",
                        onClick: Pa
                      }, {
                        default: S(() => [...r[63] || (r[63] = [
                          _("Choose devcontainer.json…", -1)
                        ])]),
                        _: 1
                      }),
                      Zs.value ? (C(), R("p", Jp, M(Zs.value), 1)) : W("", !0),
                      At.value ? (C(), R("div", Yp, [
                        At.value.distroSet ? (C(), R("p", Qp, [...r[64] || (r[64] = [
                          _("Distro/release set from ", -1),
                          f("span", { class: "font-mono" }, "image", -1),
                          _(".", -1)
                        ])])) : W("", !0),
                        At.value.packagesAdded.length > 0 ? (C(), R("p", Zp, [
                          r[65] || (r[65] = _(" Packages added: ", -1)),
                          f("span", Xp, M(At.value.packagesAdded.join(", ")), 1)
                        ])) : W("", !0),
                        At.value.commandsAdded.length > 0 ? (C(), R("p", em, M(At.value.commandsAdded.length) + " lifecycle command(s) added below — review before building. ", 1)) : W("", !0),
                        At.value.skipped.length > 0 ? (C(), R("div", tm, [
                          r[66] || (r[66] = f("p", { class: "text-muted-foreground" }, "Skipped (review manually):", -1)),
                          f("ul", sm, [
                            (C(!0), R(ce, null, Xe(At.value.skipped, (d) => (C(), R("li", { key: d }, M(d), 1))), 128))
                          ])
                        ])) : W("", !0)
                      ])) : W("", !0)
                    ]),
                    f("div", nm, [
                      r[72] || (r[72] = f("p", { class: "mb-2 text-xs text-muted-foreground" }, [
                        _(" mise.toml / .tool-versions — pins exact tool versions by baking in "),
                        f("span", { class: "font-mono" }, "mise"),
                        _(" itself as a post-install step, wired system-wide so the container's actual runtime user can use the tools too. ")
                      ], -1)),
                      f("input", {
                        ref_key: "miseTomlFileInput",
                        ref: qr,
                        type: "file",
                        accept: ".toml,application/toml",
                        class: "hidden",
                        onChange: r[3] || (r[3] = (d) => Jr(d, "toml"))
                      }, null, 544),
                      f("input", {
                        ref_key: "toolVersionsFileInput",
                        ref: Gr,
                        type: "file",
                        accept: ".tool-versions,text/plain",
                        class: "hidden",
                        onChange: r[4] || (r[4] = (d) => Jr(d, "tool-versions"))
                      }, null, 544),
                      f("div", om, [
                        y(p(pe), {
                          size: "sm",
                          variant: "outline",
                          onClick: r[5] || (r[5] = (d) => {
                            var V;
                            return (V = qr.value) == null ? void 0 : V.click();
                          })
                        }, {
                          default: S(() => [...r[68] || (r[68] = [
                            _("Choose mise.toml…", -1)
                          ])]),
                          _: 1
                        }),
                        y(p(pe), {
                          size: "sm",
                          variant: "outline",
                          onClick: r[6] || (r[6] = (d) => {
                            var V;
                            return (V = Gr.value) == null ? void 0 : V.click();
                          })
                        }, {
                          default: S(() => [...r[69] || (r[69] = [
                            _("Choose .tool-versions…", -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      _s.value ? (C(), R("p", rm, M(_s.value), 1)) : W("", !0),
                      Xs.value ? (C(), R("p", lm, [
                        r[70] || (r[70] = _(" Tools pinned: ", -1)),
                        f("span", im, M(Xs.value.join(", ")), 1),
                        r[71] || (r[71] = _(" — see the setup commands below. ", -1))
                      ])) : W("", !0)
                    ]),
                    f("div", am, [
                      y(p(re), {
                        for: "dotfiles-repo",
                        class: "mb-1 block"
                      }, {
                        default: S(() => [...r[73] || (r[73] = [
                          _("Bootstrap dotfiles from a repo", -1)
                        ])]),
                        _: 1
                      }),
                      r[76] || (r[76] = f("p", { class: "mb-2 text-xs text-muted-foreground" }, [
                        _(" Experimental — clones the repo and hands off to "),
                        f("span", { class: "font-mono" }, "mise bootstrap"),
                        _(", which only applies dotfiles if that repo's own mise config declares them. ")
                      ], -1)),
                      f("div", um, [
                        y(p(be), {
                          id: "dotfiles-repo",
                          modelValue: ws.value,
                          "onUpdate:modelValue": r[7] || (r[7] = (d) => ws.value = d),
                          class: "w-72 font-mono",
                          placeholder: "git@github.com:you/dotfiles.git"
                        }, null, 8, ["modelValue"]),
                        y(p(be), {
                          modelValue: en.value,
                          "onUpdate:modelValue": r[8] || (r[8] = (d) => en.value = d),
                          "aria-label": "Dotfiles branch or tag (optional)",
                          class: "w-32 font-mono",
                          placeholder: "branch (optional)"
                        }, null, 8, ["modelValue"]),
                        y(p(pe), {
                          size: "sm",
                          variant: "outline",
                          disabled: !ws.value.trim(),
                          onClick: ja
                        }, {
                          default: S(() => [...r[74] || (r[74] = [
                            _("Add bootstrap", -1)
                          ])]),
                          _: 1
                        }, 8, ["disabled"]),
                        Le.has("mise:dotfiles-clone") ? (C(), Te(p(pe), {
                          key: 0,
                          size: "sm",
                          variant: "outline",
                          onClick: Na
                        }, {
                          default: S(() => [...r[75] || (r[75] = [
                            _("Remove", -1)
                          ])]),
                          _: 1
                        })) : W("", !0)
                      ])
                    ])
                  ])) : W("", !0)
                ])
              ])
            ]),
            f("div", null, [
              r[95] || (r[95] = f("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Build", -1)),
              f("div", dm, [
                r[94] || (r[94] = f("h3", { class: "mb-4 text-base font-semibold" }, "Build container image", -1)),
                Ks.value ? (C(), R("div", cm, M(Ks.value), 1)) : W("", !0),
                bs.value ? (C(), R("div", fm, [
                  f("span", null, [
                    r[79] || (r[79] = _("Building variant of: ", -1)),
                    f("span", pm, M(bs.value), 1)
                  ]),
                  f("button", {
                    type: "button",
                    class: "ml-auto cursor-pointer text-muted-foreground hover:text-foreground",
                    onClick: Qs
                  }, " ✕ Clear ")
                ])) : W("", !0),
                f("div", mm, [
                  y(p(re), { for: "builder-distro" }, {
                    default: S(() => [...r[80] || (r[80] = [
                      _("Distro", -1)
                    ])]),
                    _: 1
                  }),
                  f("div", gm, [
                    y(p(Cs), {
                      id: "builder-distro",
                      modelValue: at.value,
                      "onUpdate:modelValue": r[9] || (r[9] = (d) => at.value = d),
                      class: "w-48"
                    }, {
                      default: S(() => [
                        (C(), R(ce, null, Xe(jr, (d) => f("option", {
                          key: d.value,
                          value: d.value
                        }, M(d.label), 9, hm)), 64)),
                        f("option", { value: Go }, "Other… (custom)")
                      ]),
                      _: 1
                    }, 8, ["modelValue"]),
                    Lr.value ? (C(), Te(p(be), {
                      key: 0,
                      id: "builder-custom-distro",
                      "aria-label": "Custom distro",
                      modelValue: On.value,
                      "onUpdate:modelValue": r[10] || (r[10] = (d) => On.value = d),
                      class: "w-40 font-mono",
                      placeholder: "e.g. archlinux"
                    }, null, 8, ["modelValue"])) : W("", !0)
                  ]),
                  y(p(le), { class: "col-span-2" }, {
                    default: S(() => [...r[81] || (r[81] = [
                      _(` The curated list is verified against distrobuilder's own real image definitions — pick "Other" for anything else it supports; distrobuilder covers more than this list captures. `, -1)
                    ])]),
                    _: 1
                  }),
                  y(p(re), { for: "builder-release" }, {
                    default: S(() => [...r[82] || (r[82] = [
                      _("Release", -1)
                    ])]),
                    _: 1
                  }),
                  f("div", bm, [
                    y(p(Cs), {
                      id: "builder-release",
                      modelValue: Ct.value,
                      "onUpdate:modelValue": r[11] || (r[11] = (d) => Ct.value = d),
                      class: "w-48"
                    }, {
                      default: S(() => [
                        (C(!0), R(ce, null, Xe(ba.value, (d) => (C(), R("option", {
                          key: d.value,
                          value: d.value
                        }, M(d.label), 9, vm))), 128)),
                        f("option", { value: ds }, "Other… (custom)")
                      ]),
                      _: 1
                    }, 8, ["modelValue"]),
                    Ur.value ? (C(), Te(p(be), {
                      key: 0,
                      id: "builder-custom-release",
                      "aria-label": "Custom release",
                      modelValue: Yt.value,
                      "onUpdate:modelValue": r[12] || (r[12] = (d) => Yt.value = d),
                      class: "w-40 font-mono",
                      placeholder: "e.g. rolling"
                    }, null, 8, ["modelValue"])) : W("", !0)
                  ]),
                  y(p(le), { class: "col-span-2" }, {
                    default: S(() => [...r[83] || (r[83] = [
                      _("Options change with the distro above — a custom distro always shows the free-text field here too.", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(re), { for: "builder-alias" }, {
                    default: S(() => [...r[84] || (r[84] = [
                      _("Alias", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(be), {
                    id: "builder-alias",
                    modelValue: hs.value,
                    "onUpdate:modelValue": r[13] || (r[13] = (d) => hs.value = d),
                    class: "w-96 justify-self-end",
                    placeholder: "my-custom-image"
                  }, null, 8, ["modelValue"]),
                  y(p(le), { class: "col-span-2" }, {
                    default: S(() => [...r[85] || (r[85] = [
                      _(` Becomes the image's name in Incus once the build succeeds — other containers (and "build variant") reference it by this alias, so it must be unique. Not required to match the container's own name. `, -1)
                    ])]),
                    _: 1
                  })
                ]),
                f("div", ym, [
                  r[91] || (r[91] = f("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Packages & tools", -1)),
                  y(p(re), {
                    for: "package-search",
                    class: "sr-only"
                  }, {
                    default: S(() => [...r[86] || (r[86] = [
                      _("Search packages and tools", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(be), {
                    id: "package-search",
                    modelValue: is.value,
                    "onUpdate:modelValue": r[14] || (r[14] = (d) => is.value = d),
                    class: "w-full font-mono",
                    placeholder: "Search apt, npm, PyPI, Homebrew…"
                  }, null, 8, ["modelValue"]),
                  y(p(le), null, {
                    default: S(() => [...r[87] || (r[87] = [
                      _(" apt only searches when Debian or Ubuntu is selected above. npm and PyPI results aren't OS packages — adding one adds a setup command that runs after packages install, and auto-adds the Node.js or Python packages it needs. Homebrew results show for browsing but can't be added yet — there's no way to bootstrap Homebrew itself inside an image build. ", -1)
                    ])]),
                    _: 1
                  }),
                  Ys.value ? (C(), R("p", xm, M(Ys.value), 1)) : W("", !0),
                  Js.value.length > 0 ? (C(), R("p", _m, [
                    r[88] || (r[88] = _(" Some sources are unavailable right now, showing results from the rest: ", -1)),
                    (C(!0), R(ce, null, Xe(Js.value, (d, V) => (C(), R("span", {
                      key: d.ecosystem
                    }, [
                      _(M(V > 0 ? ", " : " "), 1),
                      f("strong", null, M(Br[d.ecosystem]), 1)
                    ]))), 128))
                  ])) : W("", !0),
                  Eo.value ? (C(), R("p", wm, "Searching…")) : vs.value.length > 0 ? (C(), R("div", km, [
                    (C(!0), R(ce, null, Xe(vs.value, (d) => (C(), R("div", {
                      key: `${d.ecosystem}:${d.name}`,
                      class: "flex items-center gap-2 rounded-md border border-border px-2.5 py-1.5 text-xs"
                    }, [
                      f("span", {
                        class: lt(["shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase", d.ecosystem === "apt" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"])
                      }, M(Br[d.ecosystem]), 3),
                      f("div", Sm, [
                        f("span", Cm, M(d.name), 1),
                        d.version ? (C(), R("span", Am, M(d.version), 1)) : W("", !0),
                        d.description ? (C(), R("p", Em, M(d.description), 1)) : W("", !0)
                      ]),
                      d.ecosystem !== "brew" ? (C(), Te(p(pe), {
                        key: 0,
                        size: "sm",
                        variant: "outline",
                        disabled: Hr(d),
                        onClick: (V) => Ca(d)
                      }, {
                        default: S(() => [
                          _(M(Hr(d) ? "Added" : "+ Add"), 1)
                        ]),
                        _: 2
                      }, 1032, ["disabled", "onClick"])) : (C(), R("span", Im, "not build-time yet"))
                    ]))), 128))
                  ])) : is.value.trim().length >= 2 ? (C(), R("p", Tm, "No matches.")) : W("", !0),
                  Ne.size > 0 ? (C(), R("div", Pm, [
                    r[89] || (r[89] = f("p", { class: "mb-1.5 block text-xs font-medium" }, "Added from apt search", -1)),
                    f("div", Rm, [
                      (C(!0), R(ce, null, Xe(Ne, (d) => (C(), R("span", {
                        key: d,
                        class: "flex items-center gap-1.5 rounded-md border border-border px-2 py-1 font-mono text-xs"
                      }, [
                        _(M(d) + " ", 1),
                        f("button", {
                          type: "button",
                          "aria-label": `Remove apt package ${d}`,
                          class: "cursor-pointer text-muted-foreground hover:text-destructive",
                          onClick: (V) => _a(d)
                        }, "✕", 8, Mm)
                      ]))), 128))
                    ])
                  ])) : W("", !0),
                  Le.size > 0 ? (C(), R("div", Vm, [
                    r[90] || (r[90] = f("p", { class: "mb-1.5 block text-xs font-medium" }, "Extra setup commands (run after packages install)", -1)),
                    f("div", $m, [
                      (C(!0), R(ce, null, Xe(Le, ([d, V]) => (C(), R("div", {
                        key: d,
                        class: "flex items-center gap-2 rounded-md border border-border px-2 py-1 font-mono text-xs"
                      }, [
                        f("span", Om, M(V), 1),
                        f("button", {
                          type: "button",
                          "aria-label": `Remove setup command ${d}`,
                          class: "cursor-pointer text-muted-foreground hover:text-destructive",
                          onClick: (F) => Sa(d)
                        }, "✕", 8, jm)
                      ]))), 128))
                    ])
                  ])) : W("", !0)
                ]),
                f("div", Nm, [
                  y(p(re), {
                    for: "builder-extra-packages",
                    class: "mb-1.5 block text-xs text-muted-foreground"
                  }, {
                    default: S(() => [...r[92] || (r[92] = [
                      _("Anything else? (one per line, or comma-separated)", -1)
                    ])]),
                    _: 1
                  }),
                  hr(f("textarea", {
                    id: "builder-extra-packages",
                    "onUpdate:modelValue": r[15] || (r[15] = (d) => ls.value = d),
                    rows: "2",
                    class: "border-input bg-background w-full rounded-md border px-3 py-2 text-sm font-mono",
                    placeholder: "e.g. htop"
                  }, null, 512), [
                    [rr, ls.value]
                  ]),
                  y(p(le), null, {
                    default: S(() => [...r[93] || (r[93] = [
                      _(" Exact OS package names for the selected distro's package manager — merged with anything added from search above, duplicates removed. Use this for anything search didn't turn up. ", -1)
                    ])]),
                    _: 1
                  })
                ]),
                f("div", Lm, [
                  y(p(pe), {
                    disabled: jn.value,
                    onClick: qa
                  }, {
                    default: S(() => [
                      _(M(jn.value ? "Starting…" : "Build"), 1)
                    ]),
                    _: 1
                  }, 8, ["disabled"])
                ])
              ])
            ])
          ]),
          r[99] || (r[99] = f("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Results", -1)),
          f("div", Um, [
            r[98] || (r[98] = f("h3", { class: "mb-4 text-base font-semibold" }, "Builds", -1)),
            y(p(le), null, {
              default: S(() => [...r[96] || (r[96] = [
                _(" Live distrobuilder log output, streamed while a build runs. This list is client-side only and resets on page reload — successful builds still land in Saved images above, but the log history itself isn't persisted. ", -1)
              ])]),
              _: 1
            }),
            qs.value.length === 0 ? (C(), R("div", Dm, [...r[97] || (r[97] = [
              f("span", { class: "h-1.5 w-1.5 shrink-0 rounded-full bg-neutral-700" }, null, -1),
              f("span", { class: "font-mono text-[11px] text-neutral-500" }, [
                _(" Pick a distro and release above, then hit Build — progress and logs stream in here."),
                f("span", { class: "motion-safe:animate-pulse" }, "_")
              ], -1)
            ])])) : (C(), R("div", Bm, [
              (C(!0), R(ce, null, Xe(qs.value, (d) => {
                var V, F, ee, Be, Ze, ut, Pe;
                return C(), R("div", {
                  key: d.buildId,
                  class: "rounded-md border border-border p-3"
                }, [
                  f("div", Fm, [
                    f("div", Hm, [
                      f("span", zm, M(d.alias), 1),
                      f("span", Wm, M(d.distro) + " / " + M(d.release), 1)
                    ]),
                    y(p(Dt), {
                      variant: Ga((V = d.status) == null ? void 0 : V.status)
                    }, {
                      default: S(() => {
                        var bt;
                        return [
                          _(M(((bt = d.status) == null ? void 0 : bt.status) ?? "queued"), 1)
                        ];
                      }),
                      _: 2
                    }, 1032, ["variant"])
                  ]),
                  (F = d.status) != null && F.error || d.error ? (C(), R("div", Km, M(((ee = d.status) == null ? void 0 : ee.error) || d.error), 1)) : W("", !0),
                  f("div", qm, [
                    f("span", {
                      class: lt(["h-1.5 w-1.5 shrink-0 rounded-full", {
                        "bg-emerald-500": ((Be = d.status) == null ? void 0 : Be.status) === "success",
                        "bg-red-500": ((Ze = d.status) == null ? void 0 : Ze.status) === "failed",
                        "bg-amber-500": ((ut = d.status) == null ? void 0 : ut.status) === "running" || !d.status
                      }])
                    }, null, 2),
                    f("span", Gm, "distrobuilder · " + M(d.buildId.slice(0, 8)), 1)
                  ]),
                  f("pre", Jm, M(((Pe = d.status) == null ? void 0 : Pe.logTail) || "Waiting for log output…"), 1)
                ]);
              }), 128))
            ]))
          ])
        ])) : s.value === "jails" ? (C(), R("section", Ym, [
          r[152] || (r[152] = f("p", { class: "mb-2 text-xs font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Dashboard", -1)),
          f("div", Qm, [
            f("div", Zm, [
              r[100] || (r[100] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Total Containers", -1)),
              f("p", Xm, M(a.value.length), 1)
            ]),
            f("div", eg, [
              r[101] || (r[101] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Running", -1)),
              f("p", tg, M(p(H).length), 1)
            ]),
            f("div", sg, [
              r[102] || (r[102] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Stopped", -1)),
              f("p", ng, M(p(z)), 1)
            ]),
            f("div", og, [
              r[103] || (r[103] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Daemon", -1)),
              f("div", rg, [
                y(p(Dt), {
                  variant: i.value ? "green" : "red"
                }, {
                  default: S(() => [
                    _(M(i.value ? "Reachable" : "Not running"), 1)
                  ]),
                  _: 1
                }, 8, ["variant"])
              ])
            ]),
            f("div", lg, [
              r[104] || (r[104] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Memory In Use", -1)),
              f("p", ig, M(p($e)(p(D))), 1)
            ]),
            f("div", ag, [
              r[105] || (r[105] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Total CPU (live)", -1)),
              f("p", ug, M(p(Je)()), 1),
              p(U).length >= 2 ? (C(), R("svg", dg, [
                f("polyline", {
                  points: p(ft)(p(U), "cpuPct"),
                  fill: "none",
                  stroke: "currentColor",
                  "stroke-width": "1.5"
                }, null, 8, cg)
              ])) : W("", !0),
              r[106] || (r[106] = f("p", { class: "mt-0.5 text-[10px] text-muted-foreground" }, "last ~2 min, sum of running containers", -1))
            ])
          ]),
          y(p(le), { class: "mb-6" }, {
            default: S(() => [...r[107] || (r[107] = [
              _(" CPU shown here is a live rate (% of one core), computed from the change in cumulative CPU time between polls every 5 seconds — not the raw counter Incus reports, which only ever goes up. The sparkline is a rolling client-side window that resets on page reload; nothing is persisted server-side. ", -1)
            ])]),
            _: 1
          }),
          f("div", fg, [
            f("div", pg, [
              r[113] || (r[113] = f("h3", { class: "mb-1 text-base font-semibold" }, "Network & ACL", -1)),
              r[114] || (r[114] = f("p", { class: "mb-3 text-xs text-muted-foreground" }, " The policy currently configured for every container on this bridge (from saved config, not a live probe). ", -1)),
              f("div", mg, [
                f("div", null, [
                  r[108] || (r[108] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Bridge", -1)),
                  f("p", gg, M(v.jailBridge || "—"), 1)
                ]),
                f("div", null, [
                  r[109] || (r[109] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Subnet", -1)),
                  f("p", hg, M(v.jailSubnet || "—"), 1)
                ]),
                f("div", null, [
                  r[110] || (r[110] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "ACL Name", -1)),
                  f("p", bg, M(v.aclName || "—"), 1)
                ]),
                f("div", null, [
                  r[111] || (r[111] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Blocked Ranges", -1)),
                  f("p", vg, M(aa()) + " blocked", 1)
                ]),
                f("div", null, [
                  r[112] || (r[112] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Default Egress / Ingress", -1)),
                  f("p", yg, M(v.aclDefaultEgress) + " / " + M(v.aclDefaultIngress), 1)
                ])
              ])
            ]),
            f("div", xg, [
              r[120] || (r[120] = f("h3", { class: "mb-1 text-base font-semibold" }, "Launch Container", -1)),
              r[121] || (r[121] = f("p", { class: "mb-3 text-xs text-muted-foreground" }, " Applies the Container Defaults profile — no build step. Each container gets its own independent root filesystem and workspace even when launched from the same image. ", -1)),
              f("div", _g, [
                f("div", wg, [
                  y(p(re), {
                    for: "new-container-name",
                    class: "mb-2 block"
                  }, {
                    default: S(() => [...r[115] || (r[115] = [
                      _("Container name", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(be), {
                    id: "new-container-name",
                    modelValue: u.value,
                    "onUpdate:modelValue": r[16] || (r[16] = (d) => u.value = d),
                    placeholder: "new-container-name",
                    class: "w-full font-mono"
                  }, null, 8, ["modelValue"])
                ]),
                f("div", kg, [
                  y(p(re), {
                    for: "launch-image",
                    class: "mb-2 block"
                  }, {
                    default: S(() => [...r[116] || (r[116] = [
                      _("Image", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(Cs), {
                    id: "launch-image",
                    modelValue: A.value,
                    "onUpdate:modelValue": r[17] || (r[17] = (d) => A.value = d),
                    class: "w-full"
                  }, {
                    default: S(() => [
                      f("option", Sg, "Default (" + M(v.jailImage || "—") + ")", 1),
                      (C(!0), R(ce, null, Xe(Et.value, (d) => (C(), R("option", {
                        key: d.alias,
                        value: d.alias
                      }, M(d.alias) + M(d.isMaster ? " (golden master)" : "") + " — " + M(d.distro) + "/" + M(d.release), 9, Cg))), 128))
                    ]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                y(p(pe), {
                  size: "sm",
                  variant: "secondary",
                  disabled: !!h.value,
                  onClick: Ls
                }, {
                  default: S(() => [...r[117] || (r[117] = [
                    _("Launch", -1)
                  ])]),
                  _: 1
                }, 8, ["disabled"])
              ]),
              u.value && h.value ? (C(), R("p", Ag, M(h.value), 1)) : W("", !0),
              f("div", Eg, [
                y(p(an), {
                  id: "launch-allow-sudo",
                  modelValue: k.value,
                  "onUpdate:modelValue": r[18] || (r[18] = (d) => k.value = d)
                }, null, 8, ["modelValue"]),
                r[118] || (r[118] = f("label", {
                  for: "launch-allow-sudo",
                  class: "cursor-pointer text-xs"
                }, " Allow sudo (NOPASSWD) for the agent user ", -1))
              ]),
              y(p(le), null, {
                default: S(() => [...r[119] || (r[119] = [
                  _(` "Default" launches from Config → Container Defaults' image (the golden master, if one is set). Picking a specific image here launches from that image instead, just for this container — it doesn't change the default. Every launch, from any image, gets its own independent root filesystem; nothing is shared between containers built from the same source image. Sudo is off by default on purpose — the agent user having no path to root is what keeps a compromised dependency from escalating inside the container. Turning it on trades that away for convenience; you can also grant or check it later, per-container, from its Details panel. `, -1)
                ])]),
                _: 1
              })
            ])
          ]),
          f("div", Ig, [
            f("div", Tg, [
              r[122] || (r[122] = f("h3", { class: "text-base font-semibold" }, "Containers", -1)),
              p(z) > 0 ? (C(), Te(p(pe), {
                key: 0,
                size: "sm",
                variant: "outline",
                disabled: kt.value,
                onClick: gs
              }, {
                default: S(() => [
                  _(M(kt.value ? "Deleting…" : `Delete ${p(z)} stopped`), 1)
                ]),
                _: 1
              }, 8, ["disabled"])) : W("", !0)
            ]),
            y(p(le), null, {
              default: S(() => [...r[123] || (r[123] = [
                _(` "On bridge" means this container's address falls inside the configured subnet — a real check, not a claim that the LAN-ban ACL is actively enforced for it specifically (that's a daemon-level policy on the whole bridge, shown above under Network & ACL). Each row's mini charts are the same rolling client-side window as the summary cards above. `, -1)
              ])]),
              _: 1
            }),
            a.value.length === 0 ? (C(), R("p", Pg, " No containers yet — launch one above to get started. ")) : (C(), R(ce, { key: 1 }, [
              f("p", Rg, " Total: " + M(p(H).length) + " container" + M(p(H).length === 1 ? "" : "s") + " running, " + M(p($e)(p(D))) + " memory, CPU time " + M(p(Z)(Number(p(q)))), 1),
              f("div", Mg, [
                (C(!0), R(ce, null, Xe(a.value, (d) => (C(), R("div", {
                  key: d.name,
                  class: lt(["rounded-lg border border-border p-3", p(oe) === d.name ? "border-primary/50" : "border-border"])
                }, [
                  f("div", Vg, [
                    f("div", $g, [
                      f("span", Og, M(d.name), 1),
                      ha(d) ? (C(), R("span", jg, "on bridge")) : W("", !0),
                      y(p(Dt), {
                        variant: ia(d.status)
                      }, {
                        default: S(() => [
                          _(M(d.status), 1)
                        ]),
                        _: 2
                      }, 1032, ["variant"])
                    ]),
                    f("span", Ng, M(d.ipv4 || "—"), 1)
                  ]),
                  f("div", Lg, [
                    f("div", null, [
                      f("p", {
                        class: "text-[10px] font-semibold tracking-[0.06em] uppercase text-muted-foreground",
                        title: `Live rate, % ${p(ae)()}`
                      }, "CPU", 8, Ug),
                      f("div", Dg, [
                        f("div", Bg, [
                          p(Me)(d) !== null ? (C(), R("div", {
                            key: 0,
                            class: "h-full rounded-full bg-primary",
                            style: xn({ width: p(Me)(d) + "%" })
                          }, null, 4)) : W("", !0)
                        ]),
                        f("span", Fg, M(p(we)(d)), 1),
                        p(he)(d.name).length >= 2 ? (C(), R("svg", Hg, [
                          f("polyline", {
                            points: p(ft)(p(he)(d.name), "cpuPct"),
                            fill: "none",
                            stroke: "currentColor",
                            "stroke-width": "1.5"
                          }, null, 8, zg)
                        ])) : W("", !0)
                      ])
                    ]),
                    f("div", null, [
                      r[124] || (r[124] = f("p", { class: "text-[10px] font-semibold tracking-[0.06em] uppercase text-muted-foreground" }, "Memory", -1)),
                      f("div", Wg, [
                        f("span", Kg, M(p(K)(d)), 1),
                        p(he)(d.name).length >= 2 ? (C(), R("svg", qg, [
                          f("polyline", {
                            points: p(ft)(p(he)(d.name), "memPct"),
                            fill: "none",
                            stroke: "currentColor",
                            "stroke-width": "1.5"
                          }, null, 8, Gg)
                        ])) : W("", !0)
                      ]),
                      p(te)(d) !== null ? (C(), R("div", Jg, [
                        f("div", {
                          class: "h-full rounded-full bg-primary",
                          style: xn({ width: p(te)(d) + "%" })
                        }, null, 4)
                      ])) : W("", !0)
                    ])
                  ]),
                  f("div", Yg, [
                    y(p(pe), {
                      size: "sm",
                      variant: "outline",
                      onClick: (V) => Mn(d.name, "start")
                    }, {
                      default: S(() => [...r[125] || (r[125] = [
                        _("Start", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"]),
                    y(p(pe), {
                      size: "sm",
                      variant: "outline",
                      onClick: (V) => Mn(d.name, "stop")
                    }, {
                      default: S(() => [...r[126] || (r[126] = [
                        _("Stop", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"]),
                    y(p(pe), {
                      size: "sm",
                      variant: "secondary",
                      disabled: d.status.toLowerCase() !== "running",
                      onClick: (V) => $.value = d.name
                    }, {
                      default: S(() => [...r[127] || (r[127] = [
                        _("Console", -1)
                      ])]),
                      _: 1
                    }, 8, ["disabled", "onClick"]),
                    y(p(pe), {
                      size: "sm",
                      variant: "outline",
                      onClick: (V) => p(I)(d.name)
                    }, {
                      default: S(() => [
                        _(M(p(oe) === d.name ? "Hide manage" : "Manage"), 1)
                      ]),
                      _: 2
                    }, 1032, ["onClick"]),
                    y(p(pe), {
                      size: "sm",
                      variant: "destructive",
                      onClick: (V) => wo(d.name)
                    }, {
                      default: S(() => [...r[128] || (r[128] = [
                        _("Delete", -1)
                      ])]),
                      _: 1
                    }, 8, ["onClick"])
                  ]),
                  p(oe) === d.name ? (C(), R("div", Qg, [
                    p(m) ? (C(), R("p", Zg, "Loading…")) : p(ze) ? (C(), R(ce, { key: 1 }, [
                      f("div", Xg, [
                        f("div", null, [
                          r[129] || (r[129] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Image", -1)),
                          f("p", eh, M(p(ze).imageOs || "—") + " " + M(p(ze).imageRelease || ""), 1)
                        ]),
                        f("div", null, [
                          r[130] || (r[130] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Profiles", -1)),
                          f("p", th, M(p(ze).profiles.join(", ")), 1)
                        ]),
                        f("div", null, [
                          r[131] || (r[131] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Storage pool", -1)),
                          f("p", sh, M(p(ze).storagePool || "—"), 1)
                        ]),
                        f("div", null, [
                          r[132] || (r[132] = f("p", { class: "text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Bridge", -1)),
                          f("p", nh, M(p(ze).networkBridge || "—"), 1)
                        ])
                      ]),
                      f("div", oh, [
                        f("div", rh, [
                          f("div", null, [
                            y(p(re), {
                              for: "detail-cpu-limit",
                              class: "mb-1 flex items-center gap-1.5 text-xs"
                            }, {
                              default: S(() => [
                                r[134] || (r[134] = _(" CPU limit ", -1)),
                                p(ze).cpuLimitIsOverride ? (C(), Te(p(Dt), {
                                  key: 0,
                                  variant: "orange"
                                }, {
                                  default: S(() => [...r[133] || (r[133] = [
                                    _("override", -1)
                                  ])]),
                                  _: 1
                                })) : W("", !0)
                              ]),
                              _: 1
                            }),
                            f("div", lh, [
                              y(p(be), {
                                id: "detail-cpu-limit",
                                modelValue: p(w),
                                "onUpdate:modelValue": r[19] || (r[19] = (V) => /* @__PURE__ */ Re(w) ? w.value = V : null),
                                class: "w-24 font-mono",
                                placeholder: "e.g. 2"
                              }, null, 8, ["modelValue"]),
                              y(p(pe), {
                                size: "sm",
                                variant: "outline",
                                disabled: Fe.value,
                                onClick: N
                              }, {
                                default: S(() => [...r[135] || (r[135] = [
                                  _("Apply", -1)
                                ])]),
                                _: 1
                              }, 8, ["disabled"])
                            ])
                          ]),
                          f("div", null, [
                            y(p(re), {
                              for: "detail-memory-limit",
                              class: "mb-1 flex items-center gap-1.5 text-xs"
                            }, {
                              default: S(() => [
                                r[137] || (r[137] = _(" Memory limit ", -1)),
                                p(ze).memoryLimitIsOverride ? (C(), Te(p(Dt), {
                                  key: 0,
                                  variant: "orange"
                                }, {
                                  default: S(() => [...r[136] || (r[136] = [
                                    _("override", -1)
                                  ])]),
                                  _: 1
                                })) : W("", !0)
                              ]),
                              _: 1
                            }),
                            f("div", ih, [
                              y(p(be), {
                                id: "detail-memory-limit",
                                modelValue: p(P),
                                "onUpdate:modelValue": r[20] || (r[20] = (V) => /* @__PURE__ */ Re(P) ? P.value = V : null),
                                class: "w-24 font-mono",
                                placeholder: "e.g. 4GiB"
                              }, null, 8, ["modelValue"]),
                              y(p(pe), {
                                size: "sm",
                                variant: "outline",
                                disabled: Fe.value,
                                onClick: O
                              }, {
                                default: S(() => [...r[138] || (r[138] = [
                                  _("Apply", -1)
                                ])]),
                                _: 1
                              }, 8, ["disabled"])
                            ])
                          ]),
                          p(ze).cpuLimitIsOverride || p(ze).memoryLimitIsOverride ? (C(), Te(p(pe), {
                            key: 0,
                            size: "sm",
                            variant: "outline",
                            disabled: Fe.value,
                            onClick: T
                          }, {
                            default: S(() => [...r[139] || (r[139] = [
                              _("Use profile default", -1)
                            ])]),
                            _: 1
                          }, 8, ["disabled"])) : W("", !0)
                        ]),
                        f("div", null, [
                          y(p(re), {
                            for: "detail-workspace",
                            class: "mb-1 flex items-center gap-1.5 text-xs"
                          }, {
                            default: S(() => [
                              r[141] || (r[141] = _(" Workspace host path (/workspace) ", -1)),
                              p(ze).workspaceIsOverride ? (C(), Te(p(Dt), {
                                key: 0,
                                variant: "orange"
                              }, {
                                default: S(() => [...r[140] || (r[140] = [
                                  _("override", -1)
                                ])]),
                                _: 1
                              })) : W("", !0)
                            ]),
                            _: 1
                          }),
                          f("div", ah, [
                            y(p(be), {
                              id: "detail-workspace",
                              modelValue: p(E),
                              "onUpdate:modelValue": r[21] || (r[21] = (V) => /* @__PURE__ */ Re(E) ? E.value = V : null),
                              class: "flex-1 font-mono"
                            }, null, 8, ["modelValue"]),
                            y(p(pe), {
                              size: "sm",
                              variant: "outline",
                              disabled: Fe.value,
                              onClick: Y
                            }, {
                              default: S(() => [...r[142] || (r[142] = [
                                _("Apply", -1)
                              ])]),
                              _: 1
                            }, 8, ["disabled"]),
                            p(ze).workspaceIsOverride ? (C(), Te(p(pe), {
                              key: 0,
                              size: "sm",
                              variant: "outline",
                              disabled: Fe.value,
                              onClick: B
                            }, {
                              default: S(() => [...r[143] || (r[143] = [
                                _("Use profile default", -1)
                              ])]),
                              _: 1
                            }, 8, ["disabled"])) : W("", !0)
                          ])
                        ])
                      ]),
                      G(p(ze)) ? (C(), R("div", uh, [
                        r[144] || (r[144] = f("span", null, [
                          _(" This container shares "),
                          f("span", { class: "font-mono" }, "/workspace"),
                          _(" with every other container still on the profile's default — file writes are live-visible between them. ")
                        ], -1)),
                        y(p(pe), {
                          size: "sm",
                          variant: "outline",
                          disabled: Q.value,
                          onClick: ue
                        }, {
                          default: S(() => [
                            _(M(Q.value ? "Isolating…" : "Isolate this container's workspace"), 1)
                          ]),
                          _: 1
                        }, 8, ["disabled"])
                      ])) : W("", !0),
                      p(b) ? (C(), R("p", dh, M(p(b)), 1)) : W("", !0),
                      y(p(le), null, {
                        default: S(() => [...r[145] || (r[145] = [
                          _(` Values without an "override" badge are inherited straight from the container's profile and apply to every container using it. Applying here overrides just this one instance — it won't touch the profile or any other container. Memory limit changes need a restart of this container to actually take effect on a running instance (verified: clearing an override alone doesn't shrink an already-larger live cgroup limit back down). Isolating a shared workspace points it at a new, empty per-container directory — it does not copy any files already sitting in the old shared one. `, -1)
                        ])]),
                        _: 1
                      }),
                      f("div", ch, [
                        f("p", fh, [
                          r[146] || (r[146] = _(" Sudo (agent user) ", -1)),
                          y(p(Dt), {
                            variant: p(ze).sudoEnabled ? "green" : "gray"
                          }, {
                            default: S(() => [
                              _(M(p(ze).sudoEnabled ? "enabled" : "disabled"), 1)
                            ]),
                            _: 1
                          }, 8, ["variant"])
                        ]),
                        p(ze).sudoEnabled ? W("", !0) : (C(), Te(p(pe), {
                          key: 0,
                          size: "sm",
                          variant: "outline",
                          disabled: rs.value,
                          onClick: ot
                        }, {
                          default: S(() => [
                            _(M(rs.value ? "Granting…" : "Grant sudo (NOPASSWD)"), 1)
                          ]),
                          _: 1
                        }, 8, ["disabled"])),
                        y(p(le), null, {
                          default: S(() => [...r[147] || (r[147] = [
                            _(" Off by default on purpose — this is what keeps a compromised dependency from escalating to root inside the container. Granting sudo here applies immediately to the running container and can't be un-granted from this panel (remove ", -1),
                            f("span", { class: "font-mono" }, "/etc/sudoers.d/agent", -1),
                            _(" manually, or via the privileged command box below, if you need to revoke it). ", -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      f("div", ph, [
                        y(p(re), {
                          for: "homebrew-formula",
                          class: "mb-1 block text-xs"
                        }, {
                          default: S(() => [...r[148] || (r[148] = [
                            _("Install a package (Homebrew)", -1)
                          ])]),
                          _: 1
                        }),
                        f("div", mh, [
                          y(p(be), {
                            id: "homebrew-formula",
                            modelValue: de.value,
                            "onUpdate:modelValue": r[22] || (r[22] = (V) => de.value = V),
                            class: "w-48 font-mono",
                            placeholder: "e.g. wget",
                            onKeydown: fn(cn(Jt, ["prevent"]), ["enter"])
                          }, null, 8, ["modelValue", "onKeydown"]),
                          y(p(pe), {
                            size: "sm",
                            variant: "outline",
                            disabled: !de.value.trim() || ie.value,
                            onClick: Jt
                          }, {
                            default: S(() => [
                              _(M(ie.value ? "Installing…" : "Install"), 1)
                            ]),
                            _: 1
                          }, 8, ["disabled"])
                        ]),
                        ke.value ? (C(), R("p", gh, M(ke.value), 1)) : W("", !0),
                        Ee.value ? (C(), R("p", hh, M(Ee.value), 1)) : W("", !0),
                        y(p(le), null, {
                          default: S(() => [...r[149] || (r[149] = [
                            _(` Best-effort: bootstraps Homebrew itself under this container's non-root "agent" user if it isn't already present (needs bash and git inside the container), installing to `, -1),
                            f("span", { class: "font-mono" }, "~/.linuxbrew", -1),
                            _(" rather than Homebrew's usual shared system path — the official installer needs ", -1),
                            f("span", { class: "font-mono" }, "sudo", -1),
                            _(` for that path, and "agent" deliberately has none inside these containers. This runs against the LIVE container over exec — it isn't baked into the image, so a rebuilt or replacement container won't have it. `, -1)
                          ])]),
                          _: 1
                        })
                      ]),
                      f("div", bh, [
                        y(p(re), {
                          for: "privileged-command",
                          class: "mb-1 block text-xs"
                        }, {
                          default: S(() => [...r[150] || (r[150] = [
                            _("Run a privileged command", -1)
                          ])]),
                          _: 1
                        }),
                        f("div", vh, [
                          y(p(be), {
                            id: "privileged-command",
                            modelValue: We.value,
                            "onUpdate:modelValue": r[23] || (r[23] = (V) => We.value = V),
                            class: "flex-1 font-mono",
                            placeholder: "e.g. apt-get install -y htop",
                            onKeydown: fn(cn(Ir, ["prevent"]), ["enter"])
                          }, null, 8, ["modelValue", "onKeydown"]),
                          y(p(pe), {
                            size: "sm",
                            variant: "outline",
                            disabled: !We.value.trim() || St.value,
                            onClick: Ir
                          }, {
                            default: S(() => [
                              _(M(St.value ? "Running…" : "Run"), 1)
                            ]),
                            _: 1
                          }, 8, ["disabled"])
                        ]),
                        pt.value ? (C(), R("div", yh, [
                          f("p", {
                            class: lt(["text-xs", pt.value.status === "success" ? "text-unraid-green-800" : "text-destructive"])
                          }, M(pt.value.message), 3),
                          pt.value.stdout || pt.value.stderr ? (C(), R("pre", xh, M([pt.value.stdout, pt.value.stderr].filter(Boolean).join(`
`)), 1)) : W("", !0)
                        ])) : W("", !0),
                        y(p(le), null, {
                          default: S(() => [...r[151] || (r[151] = [
                            _(` Runs as root, mediated by you here in the UI — the container's own "agent" user never gets this capability, so this stays safe even with sudo left off. Good for one-off fixes (a forgotten package) without needing the sudo toggle at all. `, -1)
                          ])]),
                          _: 1
                        })
                      ])
                    ], 64)) : W("", !0)
                  ])) : W("", !0)
                ], 2))), 128))
              ])
            ], 64))
          ])
        ])) : s.value === "config" ? (C(), R("section", _h, [
          f("div", wh, [
            f("section", kh, [
              r[167] || (r[167] = f("p", { class: "mb-1 text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Runtime", -1)),
              r[168] || (r[168] = f("h3", { class: "mb-4 text-base font-semibold" }, "Service", -1)),
              f("div", Sh, [
                y(p(re), { for: "config-enabled" }, {
                  default: S(() => [...r[153] || (r[153] = [
                    _("Enable Incus", -1)
                  ])]),
                  _: 1
                }),
                y(p(an), {
                  id: "config-enabled",
                  modelValue: v.enabled,
                  "onUpdate:modelValue": r[24] || (r[24] = (d) => v.enabled = d)
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[154] || (r[154] = [
                    _(" Starts incusd on array start. Leaving this off keeps the daemon — and its private-prefixed binaries under ", -1),
                    f("span", { class: "font-mono" }, "/usr/local/incus/", -1),
                    _(" — installed but never running. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-dashboard-widget" }, {
                  default: S(() => [...r[155] || (r[155] = [
                    _("Show Dashboard widget", -1)
                  ])]),
                  _: 1
                }),
                y(p(an), {
                  id: "config-dashboard-widget",
                  modelValue: v.dashboardWidgetEnable,
                  "onUpdate:modelValue": r[25] || (r[25] = (d) => v.dashboardWidgetEnable = d)
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[156] || (r[156] = [
                    _(" Shows a jail-status box (running/stopped/other counts) on Unraid's Main/Dashboard tab. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-state-dir" }, {
                  default: S(() => [...r[157] || (r[157] = [
                    _("Incus state directory", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-state-dir",
                  modelValue: v.stateDir,
                  "onUpdate:modelValue": r[26] || (r[26] = (d) => v.stateDir = d),
                  class: "w-96 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[158] || (r[158] = [
                    _(" Where incusd keeps its database, storage pool, and container state. Must be real persistent storage on the array, not tmpfs — this is the one thing that survives a reboot or plugin update. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              f("div", Ch, [
                r[166] || (r[166] = f("h4", { class: "mb-3 text-sm font-semibold" }, "Storage pool", -1)),
                f("div", Ah, [
                  y(p(re), { for: "config-storage-driver" }, {
                    default: S(() => [...r[159] || (r[159] = [
                      _("Storage driver", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(Cs), {
                    id: "config-storage-driver",
                    modelValue: v.storageDriver,
                    "onUpdate:modelValue": r[27] || (r[27] = (d) => v.storageDriver = d),
                    class: "w-56 justify-self-end"
                  }, {
                    default: S(() => [...r[160] || (r[160] = [
                      f("option", { value: "dir" }, "dir (simple, no pool required)", -1),
                      f("option", { value: "zfs" }, "zfs (snapshots/speed, needs existing pool)", -1)
                    ])]),
                    _: 1
                  }, 8, ["modelValue"]),
                  y(p(le), { class: "col-span-2" }, {
                    default: S(() => [...r[161] || (r[161] = [
                      f("span", { class: "font-mono" }, "dir", -1),
                      _(" needs no existing pool and always works — it's the default for exactly that reason. ", -1),
                      f("span", { class: "font-mono" }, "zfs", -1),
                      _(" gets snapshots and speed, but the pool or dataset must already exist on your system; there's no safe way to auto-create one on your array. ", -1)
                    ])]),
                    _: 1
                  }),
                  Ce.value ? (C(), R(ce, { key: 0 }, [
                    y(p(re), { for: "config-storage-source" }, {
                      default: S(() => [...r[162] || (r[162] = [
                        _("ZFS pool/dataset", -1)
                      ])]),
                      _: 1
                    }),
                    y(p(be), {
                      id: "config-storage-source",
                      modelValue: v.storageSource,
                      "onUpdate:modelValue": r[28] || (r[28] = (d) => v.storageSource = d),
                      class: "w-96 justify-self-end font-mono"
                    }, null, 8, ["modelValue"]),
                    y(p(le), { class: "col-span-2" }, {
                      default: S(() => [...r[163] || (r[163] = [
                        _(" An existing pool or dataset path, e.g. ", -1),
                        f("span", { class: "font-mono" }, "nvme/incus", -1),
                        _(". A dataset under this path is created if missing, but the pool itself must already exist. ", -1)
                      ])]),
                      _: 1
                    })
                  ], 64)) : W("", !0),
                  y(p(re), { for: "config-storage-pool" }, {
                    default: S(() => [...r[164] || (r[164] = [
                      _("Incus storage pool name", -1)
                    ])]),
                    _: 1
                  }),
                  y(p(be), {
                    id: "config-storage-pool",
                    modelValue: v.storagePoolName,
                    "onUpdate:modelValue": r[29] || (r[29] = (d) => v.storagePoolName = d),
                    class: "w-48 justify-self-end font-mono"
                  }, null, 8, ["modelValue"]),
                  y(p(le), { class: "col-span-2" }, {
                    default: S(() => [...r[165] || (r[165] = [
                      _(" The name Incus itself uses for this storage pool internally — cosmetic, doesn't need to match anything else on the host. ", -1)
                    ])]),
                    _: 1
                  })
                ])
              ])
            ]),
            f("section", Eh, [
              r[194] || (r[194] = f("p", { class: "mb-1 text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Network & Access", -1)),
              r[195] || (r[195] = f("h3", { class: "mb-4 text-base font-semibold" }, "Network & ACL (LAN-ban)", -1)),
              r[196] || (r[196] = f("p", { class: "mb-4 text-xs text-muted-foreground" }, " Controls the bridge/subnet containers attach to and the firewall rules governing what they can reach. ", -1)),
              f("div", Ih, [
                y(p(re), { for: "config-bridge" }, {
                  default: S(() => [...r[169] || (r[169] = [
                    _("Container bridge", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-bridge",
                  modelValue: v.jailBridge,
                  "onUpdate:modelValue": r[30] || (r[30] = (d) => v.jailBridge = d),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[170] || (r[170] = [
                    _(" A dedicated NAT bridge name for containers, kept separate from Unraid's own br0 so container traffic never touches host networking directly. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-subnet" }, {
                  default: S(() => [...r[171] || (r[171] = [
                    _("Container subnet", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-subnet",
                  modelValue: v.jailSubnet,
                  "onUpdate:modelValue": r[31] || (r[31] = (d) => v.jailSubnet = d),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[172] || (r[172] = [
                    _(" CIDR for the bridge. Defaults to an RFC 2544 benchmark range specifically because it won't collide with a typical home or office LAN. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-nat" }, {
                  default: S(() => [...r[173] || (r[173] = [
                    _("NAT", -1)
                  ])]),
                  _: 1
                }),
                y(p(an), {
                  id: "config-nat",
                  modelValue: v.jailNat,
                  "onUpdate:modelValue": r[32] || (r[32] = (d) => v.jailNat = d)
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[174] || (r[174] = [
                    _(" Routes container traffic to the Internet through the host. Turning this off isolates containers with no outbound access at all — no Internet, no LAN. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-ipv6" }, {
                  default: S(() => [...r[175] || (r[175] = [
                    _("IPv6", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-ipv6",
                  modelValue: v.jailIpv6,
                  "onUpdate:modelValue": r[33] || (r[33] = (d) => v.jailIpv6 = d),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[176] || (r[176] = [
                    _("An IPv6 address for the bridge, or ", -1),
                    f("span", { class: "font-mono" }, "none", -1),
                    _(" to disable IPv6 for containers entirely.", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-acl-name" }, {
                  default: S(() => [...r[177] || (r[177] = [
                    _("ACL name", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-acl-name",
                  modelValue: v.aclName,
                  "onUpdate:modelValue": r[34] || (r[34] = (d) => v.aclName = d),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[178] || (r[178] = [
                    _(" The name of the Incus network ACL that enforces the LAN ban — created and applied to the bridge by the array-start init script. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-egress" }, {
                  default: S(() => [...r[179] || (r[179] = [
                    _("Default egress action", -1)
                  ])]),
                  _: 1
                }),
                y(p(Cs), {
                  id: "config-egress",
                  modelValue: v.aclDefaultEgress,
                  "onUpdate:modelValue": r[35] || (r[35] = (d) => v.aclDefaultEgress = d),
                  class: "w-32 justify-self-end"
                }, {
                  default: S(() => [...r[180] || (r[180] = [
                    f("option", { value: "allow" }, "allow", -1),
                    f("option", { value: "drop" }, "drop", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"]),
                y(p(re), { for: "config-ingress" }, {
                  default: S(() => [...r[181] || (r[181] = [
                    _("Default ingress action", -1)
                  ])]),
                  _: 1
                }),
                y(p(Cs), {
                  id: "config-ingress",
                  modelValue: v.aclDefaultIngress,
                  "onUpdate:modelValue": r[36] || (r[36] = (d) => v.aclDefaultIngress = d),
                  class: "w-32 justify-self-end"
                }, {
                  default: S(() => [...r[182] || (r[182] = [
                    f("option", { value: "allow" }, "allow", -1),
                    f("option", { value: "drop" }, "drop", -1)
                  ])]),
                  _: 1
                }, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[183] || (r[183] = [
                    _(" What happens to traffic not covered by a rule above. Egress defaults to allow (deny-list model — Internet stays reachable unless explicitly blocked); ingress defaults to drop (nothing reaches a container unsolicited). Tailscale's CGNAT range (100.64.0.0/10) is blocked by default; add only the narrow allow-hole a container genuinely needs rather than exposing the whole tailnet. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              f("div", Th, [
                y(p(re), {
                  for: "new-blocked-cidr",
                  class: "mb-1.5 block"
                }, {
                  default: S(() => [...r[184] || (r[184] = [
                    _("Blocked CIDRs (deny-list)", -1)
                  ])]),
                  _: 1
                }),
                Ds.value.length > 0 ? (C(), R("div", Ph, [
                  (C(!0), R(ce, null, Xe(Ds.value, (d) => (C(), R("span", {
                    key: d,
                    class: "flex items-center gap-1.5 rounded-md border border-border px-2 py-1 font-mono text-xs"
                  }, [
                    _(M(d) + " ", 1),
                    f("button", {
                      type: "button",
                      "aria-label": `Remove blocked CIDR ${d}`,
                      class: "cursor-pointer text-muted-foreground hover:text-destructive",
                      onClick: (V) => pa(d)
                    }, "✕", 8, Rh)
                  ]))), 128))
                ])) : W("", !0),
                f("div", Mh, [
                  y(p(be), {
                    id: "new-blocked-cidr",
                    modelValue: Fs.value,
                    "onUpdate:modelValue": r[37] || (r[37] = (d) => Fs.value = d),
                    class: "w-full font-mono",
                    placeholder: "e.g. 10.0.0.0/8",
                    onKeydown: fn(cn(Mr, ["prevent"]), ["enter"])
                  }, null, 8, ["modelValue", "onKeydown"]),
                  y(p(pe), {
                    size: "sm",
                    variant: "outline",
                    disabled: !Fs.value.trim(),
                    onClick: Mr
                  }, {
                    default: S(() => [...r[185] || (r[185] = [
                      _("Add", -1)
                    ])]),
                    _: 1
                  }, 8, ["disabled"])
                ]),
                zs.value ? (C(), R("p", Vh, M(zs.value), 1)) : W("", !0),
                y(p(le), null, {
                  default: S(() => [...r[186] || (r[186] = [
                    _(" Ranges containers may not reach — this is the actual LAN ban. Add one CIDR at a time; defaults to the private IPv4 ranges (RFC 1918) plus link-local addresses. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              f("div", $h, [
                y(p(re), {
                  for: "new-allow-cidr",
                  class: "mb-1.5 block"
                }, {
                  default: S(() => [...r[187] || (r[187] = [
                    _("Allow-holes (punched before block rules)", -1)
                  ])]),
                  _: 1
                }),
                Bs.value.length > 0 ? (C(), R("div", Oh, [
                  (C(!0), R(ce, null, Xe(Bs.value, (d) => (C(), R("span", {
                    key: d,
                    class: "flex items-center gap-1.5 rounded-md border border-border px-2 py-1 font-mono text-xs"
                  }, [
                    _(M(d) + " ", 1),
                    f("button", {
                      type: "button",
                      "aria-label": `Remove allowed CIDR ${d}`,
                      class: "cursor-pointer text-muted-foreground hover:text-destructive",
                      onClick: (V) => ma(d)
                    }, "✕", 8, jh)
                  ]))), 128))
                ])) : W("", !0),
                f("div", Nh, [
                  y(p(be), {
                    id: "new-allow-cidr",
                    modelValue: Hs.value,
                    "onUpdate:modelValue": r[38] || (r[38] = (d) => Hs.value = d),
                    class: "w-full font-mono",
                    placeholder: "e.g. 100.64.0.0/10",
                    onKeydown: fn(cn(Vr, ["prevent"]), ["enter"])
                  }, null, 8, ["modelValue", "onKeydown"]),
                  y(p(pe), {
                    size: "sm",
                    variant: "outline",
                    disabled: !Hs.value.trim(),
                    onClick: Vr
                  }, {
                    default: S(() => [...r[188] || (r[188] = [
                      _("Add", -1)
                    ])]),
                    _: 1
                  }, 8, ["disabled"])
                ]),
                Ws.value ? (C(), R("p", Lh, M(Ws.value), 1)) : W("", !0),
                y(p(le), null, {
                  default: S(() => [...r[189] || (r[189] = [
                    _(" Exceptions punched through the block list before it's evaluated — e.g. one specific internal service (a local LLM, a search index) a container legitimately needs to reach. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              f("div", Uh, [
                r[192] || (r[192] = f("h4", { class: "mb-3 text-sm font-semibold" }, "Tailscale", -1)),
                r[193] || (r[193] = f("p", { class: "mb-4 text-xs text-muted-foreground" }, " Optional — when set, new containers automatically join your tailnet using this key. ", -1)),
                f("div", Dh, [
                  y(p(re), { for: "tailscale-auth-key" }, {
                    default: S(() => [...r[190] || (r[190] = [
                      _("Tailscale auth key", -1)
                    ])]),
                    _: 1
                  }),
                  f("div", Bh, [
                    y(p(be), {
                      id: "tailscale-auth-key",
                      modelValue: ne.value,
                      "onUpdate:modelValue": r[39] || (r[39] = (d) => ne.value = d),
                      type: fe.value ? "text" : "password",
                      class: "w-72 font-mono",
                      placeholder: v.tsAuthKeyConfigured ? "Configured — enter a replacement" : "tskey-auth-…"
                    }, null, 8, ["modelValue", "type", "placeholder"]),
                    y(p(pe), {
                      size: "sm",
                      variant: "outline",
                      onClick: r[40] || (r[40] = (d) => fe.value = !fe.value)
                    }, {
                      default: S(() => [
                        _(M(fe.value ? "Hide" : "Show"), 1)
                      ]),
                      _: 1
                    }),
                    v.tsAuthKeyConfigured ? (C(), Te(p(pe), {
                      key: 0,
                      size: "sm",
                      variant: "outline",
                      onClick: r[41] || (r[41] = (d) => Ae.value = !Ae.value)
                    }, {
                      default: S(() => [
                        _(M(Ae.value ? "Keep key" : "Clear on save"), 1)
                      ]),
                      _: 1
                    })) : W("", !0)
                  ]),
                  y(p(le), { class: "col-span-2" }, {
                    default: S(() => [...r[191] || (r[191] = [
                      _(" The stored key is write-only and is never returned to this page. A reusable or ephemeral key from your Tailscale admin console. Best-effort: if a container's image doesn't have Tailscale installed, joining is silently skipped rather than failing the launch — it never blocks a container from starting. ", -1)
                    ])]),
                    _: 1
                  })
                ])
              ])
            ]),
            f("section", Fh, [
              r[215] || (r[215] = f("p", { class: "mb-1 text-[10px] font-semibold tracking-[0.08em] uppercase text-muted-foreground" }, "Container Defaults", -1)),
              r[216] || (r[216] = f("h3", { class: "mb-4 text-base font-semibold" }, "Defaults", -1)),
              f("div", Hh, [
                y(p(re), { for: "config-profile" }, {
                  default: S(() => [...r[197] || (r[197] = [
                    _("Container profile", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-profile",
                  modelValue: v.jailProfile,
                  "onUpdate:modelValue": r[42] || (r[42] = (d) => v.jailProfile = d),
                  class: "w-48 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[198] || (r[198] = [
                    _(" The Incus profile new containers launch with — sets resource limits, network, and mounts, defined in the array-start init script's profile template. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-image" }, {
                  default: S(() => [...r[199] || (r[199] = [
                    _("Default image", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-image",
                  modelValue: v.jailImage,
                  "onUpdate:modelValue": r[43] || (r[43] = (d) => v.jailImage = d),
                  class: "w-96 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[200] || (r[200] = [
                    _(" Used when launching a container without picking a specific image — either a remote reference like ", -1),
                    f("span", { class: "font-mono" }, "images:debian/trixie/cloud", -1),
                    _(", or a locally-built image's alias. Marking an image as the golden master in the Builder tab sets this automatically. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-nesting" }, {
                  default: S(() => [...r[201] || (r[201] = [
                    _("Allow nesting", -1)
                  ])]),
                  _: 1
                }),
                y(p(an), {
                  id: "config-nesting",
                  modelValue: v.jailNesting,
                  "onUpdate:modelValue": r[44] || (r[44] = (d) => v.jailNesting = d)
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[202] || (r[202] = [
                    _(" Lets a container run Docker or Incus inside itself — needed for agents that spin up their own sandboxes, but widens what a compromised container could reach. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-cpu" }, {
                  default: S(() => [...r[203] || (r[203] = [
                    _("CPU limit", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-cpu",
                  modelValue: v.jailCpu,
                  "onUpdate:modelValue": r[45] || (r[45] = (d) => v.jailCpu = d),
                  class: "w-24 justify-self-end font-mono",
                  placeholder: "empty = no cap"
                }, null, 8, ["modelValue"]),
                g.value ? (C(), R("p", zh, M(g.value), 1)) : W("", !0),
                y(p(re), { for: "config-memory" }, {
                  default: S(() => [...r[204] || (r[204] = [
                    _("Memory limit", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-memory",
                  modelValue: v.jailMemory,
                  "onUpdate:modelValue": r[46] || (r[46] = (d) => v.jailMemory = d),
                  class: "w-24 justify-self-end font-mono",
                  placeholder: "empty = no cap"
                }, null, 8, ["modelValue"]),
                x.value ? (C(), R("p", Wh, M(x.value), 1)) : W("", !0),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[205] || (r[205] = [
                    _(" Hard resource ceiling applied via the container profile at launch — CPU as a core count (e.g. ", -1),
                    f("span", { class: "font-mono" }, "2", -1),
                    _("), memory with a unit (e.g. ", -1),
                    f("span", { class: "font-mono" }, "4GiB", -1),
                    _("). Leave either empty for no cap. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-workspace" }, {
                  default: S(() => [...r[206] || (r[206] = [
                    _("Workspace root", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-workspace",
                  modelValue: v.jailWorkspaceRoot,
                  "onUpdate:modelValue": r[47] || (r[47] = (d) => v.jailWorkspaceRoot = d),
                  class: "w-96 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[207] || (r[207] = [
                    _(` Host directory holding per-container workspaces, bind-mounted in with idmap shifting. Must be real persistent storage — the init script refuses to start if it's tmpfs, since that would silently lose "persistent" data on every reboot. Prefer a real device mount (e.g. `, -1),
                    f("span", { class: "font-mono" }, "/mnt/cache/appdata/...", -1),
                    _(") over a ", -1),
                    f("span", { class: "font-mono" }, "/mnt/user/...", -1),
                    _(" path — Unraid's shfs FUSE union view generally doesn't support the idmapped-mount feature the shift needs. ", -1)
                  ])]),
                  _: 1
                }),
                y(p(re), { for: "config-agent-uid" }, {
                  default: S(() => [...r[208] || (r[208] = [
                    _("Agent UID", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-agent-uid",
                  modelValue: v.jailAgentUid,
                  "onUpdate:modelValue": r[48] || (r[48] = (d) => v.jailAgentUid = d),
                  class: "w-24 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(re), { for: "config-agent-gid" }, {
                  default: S(() => [...r[209] || (r[209] = [
                    _("Agent GID", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-agent-gid",
                  modelValue: v.jailAgentGid,
                  "onUpdate:modelValue": r[49] || (r[49] = (d) => v.jailAgentGid = d),
                  class: "w-24 justify-self-end font-mono"
                }, null, 8, ["modelValue"]),
                y(p(le), { class: "col-span-2" }, {
                  default: S(() => [...r[210] || (r[210] = [
                    _(" The uid/gid inside each container mapped to your host user — match your own host user if you want files under the bind-mounted workspace to show correct ownership from outside the container. ", -1)
                  ])]),
                  _: 1
                })
              ]),
              f("div", Kh, [
                r[213] || (r[213] = f("h4", { class: "mb-3 text-sm font-semibold" }, "Bind mounts", -1)),
                y(p(re), {
                  for: "config-bind-mounts",
                  class: "mb-2 block"
                }, {
                  default: S(() => [...r[211] || (r[211] = [
                    _("Host config bind-mounts", -1)
                  ])]),
                  _: 1
                }),
                y(p(be), {
                  id: "config-bind-mounts",
                  modelValue: v.jailBindMounts,
                  "onUpdate:modelValue": r[50] || (r[50] = (d) => v.jailBindMounts = d),
                  class: "w-full font-mono",
                  placeholder: "/boot/config/plugins/incus/bind-mounts/claude:/home/agent/.claude:ro"
                }, null, 8, ["modelValue"]),
                r[214] || (r[214] = f("p", { class: "mt-2 text-xs text-muted-foreground" }, " Comma-separated host:container[:ro|rw] triples from approved roots. Mounts default to read-only; only sources beneath the workspace root may be writable. ", -1)),
                y(p(le), null, {
                  default: S(() => [...r[212] || (r[212] = [
                    _(" Copy curated agent config under ", -1),
                    f("span", { class: "font-mono" }, "/boot/config/plugins/incus/bind-mounts", -1),
                    _(" rather than exposing host home or system paths. Sources must resolve beneath that directory or the configured workspace root; config-root mounts are always read-only. ", -1)
                  ])]),
                  _: 1
                })
              ])
            ])
          ]),
          f("div", qh, [
            y(p(pe), {
              disabled: o.value || !!g.value || !!x.value,
              onClick: Rn
            }, {
              default: S(() => [
                _(M(o.value ? "Applying…" : "Apply"), 1)
              ]),
              _: 1
            }, 8, ["disabled"])
          ])
        ])) : W("", !0)
      ], 64)),
      $.value ? (C(), Te(p(t), {
        key: 2,
        "jail-name": $.value,
        onClose: r[51] || (r[51] = (d) => $.value = null)
      }, null, 8, ["jail-name"])) : W("", !0)
    ]));
  }
}), Qh = /* @__PURE__ */ hc(Yh, { shadowRoot: !1 });
customElements.get("incus-settings-app") || customElements.define("incus-settings-app", Qh);
export {
  pe as _,
  _i as a,
  C as b,
  R as c,
  He as d,
  f as e,
  Ld as f,
  xn as g,
  y as h,
  _ as i,
  W as j,
  me as k,
  Tn as n,
  yi as o,
  L as r,
  M as t,
  p as u,
  S as w
};
