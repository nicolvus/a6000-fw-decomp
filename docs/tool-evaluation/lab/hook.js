for (const n of ['capture', 'expose']) {
  Interceptor.attach(DebugSymbol.fromName(n).address, {
    onEnter(a) { this.a0 = a[0].toInt32(); this.a1 = a[1].toInt32(); },
    onLeave(r) { console.log(`${n}(${this.a0}${n === 'expose' ? ', ' + this.a1 : ''}) -> ${r.toInt32()}`); }
  });
}
