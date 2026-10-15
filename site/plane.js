(() => {
  'use strict';
  // A tiny software-rendered 3D high-wing Cessna. No WebGL or model download.
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = matchMedia('(any-hover: hover) and (any-pointer: fine)');
  const canvas = document.createElement('canvas');
  canvas.className = 'cursor-plane';
  canvas.setAttribute('aria-hidden', 'true');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const control = document.createElement('button');
  control.className = 'plane-control';
  control.type = 'button';
  document.querySelector('.footer').append(control);
  document.body.append(canvas);
  let paused = false;
  try { paused = sessionStorage.getItem('plane-paused') === 'true'; } catch { /* Storage is optional. */ }
  let width = innerWidth, height = innerHeight;
  let x = width * .72, y = 120, heading = .4, bank = 0;
  let target = {x: width * .55, y: height * .45};
  let frame = 0, previous = 0, propeller = 0;
  let passHeading = Math.atan2(target.y-y, target.x-x);
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const wrap = angle => Math.atan2(Math.sin(angle), Math.cos(angle));
  const faces = [];
  const face = (points, color) => faces.push({points, color});
  // Model coordinates: wings along X, nose toward -Y, up along Z.
  function box(x1, x2, y1, y2, z1, z2, color) {
    const a=[x1,y1,z1],b=[x2,y1,z1],c=[x2,y2,z1],d=[x1,y2,z1];
    const e=[x1,y1,z2],f=[x2,y1,z2],g=[x2,y2,z2],h=[x1,y2,z2];
    [[a,b,c,d],[e,h,g,f],[a,e,f,b],[b,f,g,c],[c,g,h,d],[d,h,e,a]].forEach(points=>face(points,color));
  }
  const white = [229,235,235], red = [171,57,31], glass = [45,77,94];
  const rings = [[-29,2,0],[-24,4,0],[-10,5,1],[4,4.5,0],[24,1.4,1],[30,.5,2]];
  for (let r=0;r<rings.length-1;r++) {
    const ring = ([cy,radius,cz],i) => [Math.cos(i*Math.PI/4)*radius,cy,cz+Math.sin(i*Math.PI/4)*radius];
    for (let i=0;i<8;i++) face([ring(rings[r],i),ring(rings[r],i+1),ring(rings[r+1],i+1),ring(rings[r+1],i)],white);
  }
  // High main wing, red tips, horizontal and vertical stabilizers.
  box(-39,39,-10,1,6,7.6,white);
  box(-39,-33,-10,1,6,7.8,red); box(33,39,-10,1,6,7.8,red);
  box(-14,14,22,28,2,3,white);
  box(-14,-10,22,28,2,3.2,red); box(10,14,22,28,2,3.2,red);
  face([[-.7,17,3],[-.7,25,15],[-.7,29,14],[-.7,30,3]],red);
  face([[.7,17,3],[.7,25,15],[.7,29,14],[.7,30,3]],red);
  face([[-.7,25,15],[.7,25,15],[.7,29,14],[-.7,29,14]],white);
  // Windshield and side glazing, with a narrow red fuselage stripe.
  face([[-3.7,-18,2],[3.7,-18,2],[4,-11,5],[-4,-11,5]],glass);
  for (const side of [-1,1]) {
    face([[side*4.6,-11,1],[side*4.7,-11,4],[side*4.2,1,4],[side*4.4,1,1]],glass);
    face([[side*4.6,-7,0],[side*4.4,3,0],[side*1.6,23,1],[side*1.6,23,2],[side*4.4,3,1]],red);
    // Wing struts and fixed landing gear are distinctive Cessna details.
    face([[side*4,-3,-2],[side*5,-3,-2],[side*27,-4,6],[side*26,-4,6]],[145,159,164]);
    box(side*9-.8,side*9+.8,-1,2,-8,-3,[108,119,125]);
    box(side*9-1.6,side*9+1.6,-2,3,-10,-7,[37,44,49]);
  }
  box(-1,1,-22,-19,-8,-3,[75,87,94]);
  box(-1.7,1.7,-23,-19,-10,-7,[37,44,49]);

  function render() {
    const size = 144, scale = Math.min(devicePixelRatio || 1, 2);
    if (canvas.width !== size*scale) { canvas.width=size*scale; canvas.height=size*scale; }
    ctx.setTransform(scale,0,0,scale,72*scale,72*scale);
    ctx.clearRect(-72,-72,size,size);
    const cb=Math.cos(bank), sb=Math.sin(bank), ch=Math.cos(heading), sh=Math.sin(heading);
    function transform([px,py,pz]) {
      const bx=px*cb+pz*sb, bz=pz*cb-px*sb;
      const wx=-py*ch-bx*sh, wy=-py*sh+bx*ch;
      return [wx,wy*.83-bz*.56,wy*.56+bz*.83];
    }
    const visible = faces.map(({points,color})=>({points:points.map(transform),color}));
    // Rotating propeller, drawn as geometry in the same depth-sorted scene.
    const p = propeller, blade = [[-12,-30,-.7],[12,-30,-.7],[12,-30,.7],[-12,-30,.7]];
    visible.push({points:blade.map(([a,b,c])=>transform([a*Math.cos(p)+c*Math.sin(p),b,c*Math.cos(p)-a*Math.sin(p)])),color:[82,94,99]});
    visible.sort((a,b)=>a.points.reduce((s,p)=>s+p[2],0)/a.points.length-b.points.reduce((s,p)=>s+p[2],0)/b.points.length);
    for (const {points,color} of visible) {
      const a=points[0], b=points[1], c=points[2];
      const u=b.map((v,i)=>v-a[i]), v=c.map((v,i)=>v-a[i]);
      const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
      const length=Math.hypot(...n)||1;
      const light=.68+.32*Math.abs((n[0]*-.3+n[1]*-.5+n[2]*.81)/length);
      ctx.fillStyle=`rgb(${color.map(c=>Math.round(c*light)).join(',')})`;
      ctx.beginPath(); points.forEach(([px,py],i)=>i ? ctx.lineTo(px,py) : ctx.moveTo(px,py)); ctx.closePath();ctx.fill();
      ctx.strokeStyle='rgba(37,53,62,.16)';ctx.lineWidth=.45;ctx.stroke();
    }
    canvas.style.transform=`translate3d(${x-72}px,${y-72}px,0)`;
  }
  function tick(now) {
    const dt=previous ? Math.min((now-previous)/1000,.04) : 0; previous=now;
    const center={x:clamp(target.x,70,width-70),y:clamp(target.y,70,height-70)};
    let dx=Math.cos(passHeading), dy=Math.sin(passHeading);
    let along=(x-center.x)*dx+(y-center.y)*dy;
    if (along>260) {
      passHeading=wrap(passHeading+Math.PI);
      dx=Math.cos(passHeading);dy=Math.sin(passHeading);
      along=-along;
    }
    // Follow a line through the cursor, looking ahead along it. Reverse after
    // each pass; the turn limit makes a wide teardrop before the next approach.
    // Chasing the cursor directly would settle into an orbit and never pass it.
    const lookAhead=along+100;
    const aim={x:center.x+dx*lookAhead,y:center.y+dy*lookAhead};
    const turn=clamp(wrap(Math.atan2(aim.y-y,aim.x-x)-heading)*1.6,-.72,.72);
    // Constant forward speed and bounded yaw produce broad, continuous passes.
    heading=wrap(heading+turn*dt);
    bank+=(turn*.8-bank)*(1-Math.exp(-dt*3));
    x+=Math.cos(heading)*125*dt; y+=Math.sin(heading)*125*dt;
    propeller+=dt*45;
    render(); frame=requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(frame); frame=0; previous=0;
    const available=pointer.matches && !motion.matches;
    control.hidden=!available;
    control.textContent=paused ? 'Resume little plane' : 'Pause little plane';
    canvas.hidden=!available || paused || document.hidden;
    if (!canvas.hidden) frame=requestAnimationFrame(tick);
  }
  control.addEventListener('click',()=>{
    paused=!paused;
    try { sessionStorage.setItem('plane-paused',String(paused)); } catch { /* Storage is optional. */ }
    sync();
  });
  window.addEventListener('pointermove',event=>{
    if (event.pointerType==='mouse' || event.pointerType==='pen') target={x:event.clientX,y:event.clientY};
  },{passive:true});
  window.addEventListener('resize',()=>{
    width=innerWidth;height=innerHeight;
    x=clamp(x,0,width);y=clamp(y,0,height);
    target={x:clamp(target.x,70,width-70),y:clamp(target.y,70,height-70)};
  },{passive:true});
  document.addEventListener('visibilitychange',sync);
  window.addEventListener('pagehide',()=>{cancelAnimationFrame(frame);frame=0;});
  window.addEventListener('pageshow',sync);
  motion.addEventListener('change',sync); pointer.addEventListener('change',sync);
  sync();
})();
