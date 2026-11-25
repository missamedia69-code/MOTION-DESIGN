/* MISSA TV 360 — procedural Three.js scene, synchronized to the existing GSAP master timeline. */
(() => {
"use strict";
const T=window.THREE, tl=window.__timelines&&window.__timelines.main, canvas=document.getElementById("hf3d-canvas");
if(!T||!tl||!canvas){console.warn("[MISSA 3D] Three.js/timeline unavailable.");return;}
let renderer;
try{renderer=new T.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:"high-performance"});}
catch(e){console.warn("[MISSA 3D] WebGL unavailable; keeping the 2.5D composition.",e);return;}
renderer.setPixelRatio(1);renderer.setSize(1080,1920,false);renderer.setClearColor(0x000000,0);
if("outputColorSpace"in renderer)renderer.outputColorSpace=T.SRGBColorSpace;
if("toneMapping"in renderer)renderer.toneMapping=T.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.12;renderer.shadowMap.enabled=false;
const scene=new T.Scene(),camera=new T.PerspectiveCamera(38,1080/1920,.1,100);
camera.position.set(0,0,20);camera.lookAt(0,0,0);
scene.add(new T.HemisphereLight(0xffffff,0x101b36,1.85));
const key=new T.DirectionalLight(0xffffff,2.15);key.position.set(-5,8,11);scene.add(key);
const rim=new T.PointLight(0x2fd37a,62,30,2);rim.position.set(4,1,7);scene.add(rim);
const gold=new T.PointLight(0xffe600,42,28,2);gold.position.set(-4,-3,6);scene.add(gold);
const M={
 blue:new T.MeshPhysicalMaterial({color:0x0141aa,metalness:.48,roughness:.26,clearcoat:.8}),
 blueDark:new T.MeshStandardMaterial({color:0x061a45,metalness:.32,roughness:.34}),
 navy:new T.MeshStandardMaterial({color:0x0b1020,metalness:.28,roughness:.38}),
 yellow:new T.MeshPhysicalMaterial({color:0xffe600,metalness:.28,roughness:.24,clearcoat:.8}),
 green:new T.MeshPhysicalMaterial({color:0x08992d,metalness:.36,roughness:.24,clearcoat:.8}),
 lime:new T.MeshStandardMaterial({color:0xa6e31b,emissive:0x304a00,emissiveIntensity:.32,roughness:.3}),
 white:new T.MeshStandardMaterial({color:0xf4f7ff,metalness:.08,roughness:.32}),
 silver:new T.MeshStandardMaterial({color:0xcbd5e1,metalness:.65,roughness:.28}),
 red:new T.MeshStandardMaterial({color:0xe53935,metalness:.22,roughness:.3}),
 violet:new T.MeshStandardMaterial({color:0x6b5cff,metalness:.35,roughness:.26})
};
const G=()=>new T.Group();
function mesh(g,geo,mat,x=0,y=0,z=0,rx=0,ry=0,rz=0){const o=new T.Mesh(geo,mat);o.position.set(x,y,z);o.rotation.set(rx,ry,rz);g.add(o);return o;}
const box=(g,w,h,d,m,x=0,y=0,z=0,rx=0,ry=0,rz=0)=>mesh(g,new T.BoxGeometry(w,h,d),m,x,y,z,rx,ry,rz);
const sphere=(g,r,m,x=0,y=0,z=0,sx=1,sy=1,sz=1)=>{const o=mesh(g,new T.SphereGeometry(r,28,20),m,x,y,z);o.scale.set(sx,sy,sz);return o;};
const cyl=(g,rt,rb,h,m,x=0,y=0,z=0,rx=0,ry=0,rz=0)=>mesh(g,new T.CylinderGeometry(rt,rb,h,28),m,x,y,z,rx,ry,rz);
const torus=(g,r,t,m,x=0,y=0,z=0,rx=0,ry=0,rz=0)=>mesh(g,new T.TorusGeometry(r,t,14,64),m,x,y,z,rx,ry,rz);
function triangle(m,s=.34){const p=new T.Shape();p.moveTo(-s,-s*.92);p.lineTo(s,0);p.lineTo(-s,s*.92);p.closePath();return new T.Mesh(new T.ShapeGeometry(p),m);}
function makeTV(){
 const g=G();box(g,4.25,2.55,.44,M.blue,0,0,0);box(g,3.86,2.16,.06,M.navy,0,0,.25);box(g,3.68,1.98,.04,M.blueDark,0,0,.30);
 cyl(g,.58,.58,.16,M.green,.82,0,.42,Math.PI/2);const tri=triangle(M.white,.36);tri.position.set(.88,0,.53);g.add(tri);
 cyl(g,.055,.055,1.72,M.blue,-1.06,1.96,0,0,0,-.52);cyl(g,.055,.055,1.72,M.blue,1.06,1.96,0,0,0,.52);
 sphere(g,.13,M.yellow,-1.48,2.68,0);sphere(g,.13,M.yellow,1.48,2.68,0);
 box(g,.72,.22,.52,M.blue,0,-1.43,0);box(g,2.2,.12,.78,M.blueDark,0,-1.66,0);
 box(g,.24,.72,.38,M.blue,-1.15,-1.85,.04,0,0,-.2);box(g,.24,.72,.38,M.blue,1.15,-1.85,.04,0,0,.2);return g;
}
function makeClapper(){const g=G();box(g,2.55,1.52,.22,M.navy,0,-.12,0);box(g,2.55,.42,.20,M.blue,0,.83,0);for(let i=0;i<5;i++)box(g,.28,.42,.23,i%2===0?M.yellow:M.white,-1.02+i*.51,.83,.13,0,0,-.38);box(g,1.9,.09,.06,M.green,0,-.12,.14);return g;}
function makePopcorn(){const g=G();cyl(g,.66,.88,1.35,M.red,0,-.12,0);cyl(g,.69,.69,.12,M.white,0,.57,0);for(let i=0;i<11;i++){const a=i*2.39996,r=.45+(i%3)*.08;sphere(g,.28+(i%2)*.035,M.white,Math.cos(a)*r,.82+(i%3)*.08,Math.sin(a)*r,1,1,.9);}return g;}
function makeHeadphones(){const g=G();torus(g,.92,.16,M.blue,0,.26,0);box(g,.34,.76,.42,M.navy,-.91,-.22,0);box(g,.34,.76,.42,M.navy,.91,-.22,0);box(g,.23,.54,.25,M.lime,-.91,-.22,.24);box(g,.23,.54,.25,M.lime,.91,-.22,.24);return g;}
function makeBall(){const g=G();sphere(g,.88,M.white);[[0,.67,.42],[-.62,-.15,.42],[.55,-.42,.4],[-.16,-.66,-.4],[.12,.25,-.82]].forEach(p=>{const q=sphere(g,.26,M.blue,p[0],p[1],p[2],1,.82,.22);q.lookAt(0,0,0);});return g;}
function makeRadio(){const g=G();box(g,2.25,1.42,.62,M.green);box(g,2.06,1.22,.08,M.blueDark,0,0,.36);torus(g,.45,.09,M.silver,-.47,0,.44);cyl(g,.31,.31,.06,M.navy,-.47,0,.45,Math.PI/2);for(let i=0;i<5;i++)box(g,.08,.55,.04,M.lime,.18+i*.20,0,.44);cyl(g,.04,.04,.85,M.silver,.86,1,0,0,0,-.28);return g;}
function makeGamepad(){const g=G();box(g,2.35,.95,.48,M.blueDark);sphere(g,.55,M.blueDark,-.86,-.02,0,1,.85,.65);sphere(g,.55,M.blueDark,.86,-.02,0,1,.85,.65);box(g,.19,.60,.13,M.white,-.62,0,.31);box(g,.60,.19,.13,M.white,-.62,0,.31);sphere(g,.12,M.yellow,.62,.18,.32);sphere(g,.12,M.red,.91,0,.32);sphere(g,.12,M.green,.62,-.18,.32);sphere(g,.12,M.violet,.33,0,.32);return g;}
function makeMagnifier(){const g=G();torus(g,.70,.12,M.lime,0,.28,0);cyl(g,.12,.18,1.22,M.blue,.72,-.76,0,0,0,-.55);sphere(g,.08,M.white,-.22,.52,.05);return g;}
function makeRouter(){const g=G();box(g,3.6,.55,1.28,M.silver);box(g,3.46,.34,1.12,M.blueDark,0,.12,.08);box(g,2.55,.08,.68,M.blue,0,.31,-.02);for(let i=0;i<6;i++)cyl(g,.045,.045,.82,M.navy,-1.3+i*.52,-.36,.05);cyl(g,.065,.065,1.65,M.blue,-1.36,.98,0,0,0,-.12);cyl(g,.065,.065,1.65,M.blue,1.36,.98,0,0,0,.12);sphere(g,.10,M.lime,-.72,-.06,.68);sphere(g,.10,M.green,-.38,-.06,.68);sphere(g,.10,M.yellow,-.04,-.06,.68);return g;}
function makeDevice(kind){const g=G(),s=kind==="phone"?[.95,1.9,.18]:kind==="tablet"?[2.55,1.8,.18]:[3.45,2.12,.26],w=s[0],h=s[1],d=s[2];box(g,w,h,d,M.navy);box(g,w-.14,h-.14,.025,M.blueDark,0,0,d/2+.01);box(g,w-.26,h-.30,.02,M.yellow,0,.02,d/2+.03);box(g,w*.48,.065,.025,M.green,0,-h*.32,d/2+.05);sphere(g,.065,M.white,0,h*.39,d/2+.05);return g;}
function makeStopwatch(){const g=G();cyl(g,.88,.88,.22,M.blueDark,0,0,0,Math.PI/2);torus(g,.82,.12,M.yellow,0,0,.20);cyl(g,.20,.20,.30,M.silver,0,.98,0);box(g,.11,.50,.06,M.white,0,.12,.36);box(g,.52,.10,.06,M.green,.21,-.06,.36,0,0,-.34);return g;}
function makeGift(){const g=G();box(g,1.75,1.35,1.25,M.green,0,-.18,0);box(g,1.86,.26,1.35,M.yellow,0,.52,0);box(g,.25,1.52,1.38,M.yellow,0,-.10,.05);box(g,1.84,1.46,.22,M.yellow,0,-.12,.67);torus(g,.38,.11,M.yellow,-.30,.92,.02,Math.PI/2,0,.6);torus(g,.38,.11,M.yellow,.30,.92,.02,Math.PI/2,0,-.6);return g;}
function makeBag(){const g=G();sphere(g,.82,M.yellow,0,-.10,0,1,1.1,.85);cyl(g,.34,.48,.36,M.green,0,.72,0);torus(g,.38,.08,M.blue,0,.65,0);const p=new T.Shape();p.moveTo(0,.48);p.bezierCurveTo(-.45,.48,-.50,.02,-.05,-.02);p.bezierCurveTo(.42,-.08,.38,-.43,0,-.43);p.lineTo(0,-.58);p.lineTo(.12,-.58);p.lineTo(.12,-.43);p.bezierCurveTo(.55,-.38,.62,.10,.12,.16);p.bezierCurveTo(-.28,.20,-.30,.36,0,.36);p.closePath();const mark=new T.Mesh(new T.ShapeGeometry(p),M.blue);mark.position.set(0,-.08,.72);g.add(mark);return g;}
function makeCoin(){const g=G();cyl(g,.48,.48,.16,M.yellow,0,0,0,Math.PI/2);torus(g,.36,.055,M.white,0,0,.12);return g;}
function makeCard(title,colors){const g=G(),c=document.createElement("canvas");c.width=512;c.height=768;const x=c.getContext("2d"),gr=x.createLinearGradient(0,0,512,768);gr.addColorStop(0,colors[0]);gr.addColorStop(1,colors[1]);x.fillStyle=gr;x.fillRect(0,0,512,768);x.fillStyle="rgba(255,255,255,.10)";for(let i=0;i<8;i++)x.fillRect(28+i*62,0,18,768);x.fillStyle="#fff";x.font="900 54px sans-serif";x.fillText("MISSA ORIGINAL",36,94);x.fillStyle="#ffe600";x.font="900 62px sans-serif";const w=title.split(" ");let y=570;for(let i=w.length-1;i>=0;i--){x.fillText(w[i],36,y);y-=66;}x.fillStyle="rgba(255,255,255,.8)";x.font="700 26px sans-serif";x.fillText("À DÉCOUVRIR",36,708);const tex=new T.CanvasTexture(c);tex.colorSpace=T.SRGBColorSpace;box(g,1.34,2.05,.16,M.navy);const front=new T.Mesh(new T.PlaneGeometry(1.26,1.97),new T.MeshStandardMaterial({map:tex,roughness:.38,metalness:.06}));front.position.z=.09;g.add(front);torus(g,.56,.022,M.yellow,0,0,.11);return g;}
function reveal(o,start,end,from,to,rf,rt,scale=1,ease="back.out(1.65)"){o.scale.setScalar(.001);o.position.set(from.x,from.y,from.z);o.rotation.set(rf.x,rf.y,rf.z);tl.fromTo(o.scale,{x:.001,y:.001,z:.001},{x:scale,y:scale,z:scale,duration:.48,ease,immediateRender:false},start);tl.fromTo(o.position,{x:from.x,y:from.y,z:from.z},{x:to.x,y:to.y,z:to.z,duration:.64,ease:"power3.out",immediateRender:false},start);tl.fromTo(o.rotation,{x:rf.x,y:rf.y,z:rf.z},{x:rt.x,y:rt.y,z:rt.z,duration:.66,ease:"power2.out",immediateRender:false},start);tl.to(o.scale,{x:.001,y:.001,z:.001,duration:.25,ease:"power2.in"},end-.24);}

const tv=makeTV(),clapper=makeClapper(),popcorn=makePopcorn(),headphones=makeHeadphones(),ball=makeBall(),radio=makeRadio(),gamepad=makeGamepad(),magnifier=makeMagnifier(),router=makeRouter(),phone=makeDevice("phone"),tablet=makeDevice("tablet"),tvScreen=makeDevice("tv"),stopwatch=makeStopwatch(),gift=makeGift(),bag=makeBag();
[tv,clapper,popcorn,headphones,ball,radio,gamepad,magnifier,router,phone,tablet,tvScreen,stopwatch,gift,bag].forEach(o=>scene.add(o));
const coinA=makeCoin(),coinB=makeCoin(),coinC=makeCoin();[coinA,coinB,coinC].forEach(o=>scene.add(o));
const cards=[makeCard("HORIZON 2030",["#06122e","#1458ae"]),makeCard("AMOUR ÉTERNEL",["#6c133c","#ef7a36"]),makeCard("OPÉRATION OMEGA",["#071d3b","#3c5b76"]),makeCard("LIGUE 360",["#072a46","#07992d"]),makeCard("ROYAUME FANTASTIQUE",["#39205d","#e0a63d"])];cards.forEach(o=>scene.add(o));
const orbit=G();torus(orbit,2.58,.045,M.yellow);torus(orbit,2.90,.035,M.green,0,0,0,Math.PI/2,.35,.15);sphere(orbit,.13,M.lime,2.58,0,0);sphere(orbit,.10,M.white,-2.90,0,0);scene.add(orbit);
const pg=new T.BufferGeometry(),pp=[];for(let i=0;i<150;i++){const a=i*2.399963,r=1.8+(i%9)*.24;pp.push(Math.cos(a)*r,Math.sin(a)*r,((i%7)-3)*.22);}pg.setAttribute("position",new T.Float32BufferAttribute(pp,3));const particles=new T.Points(pg,new T.PointsMaterial({color:0xffe600,size:.055,transparent:true,opacity:.9,sizeAttenuation:true}));particles.scale.setScalar(.001);scene.add(particles);

// Opening — dimensional television breaks out of the repeated grey screen.
reveal(tv,.10,2.92,{x:-7,y:1.65,z:-2},{x:0,y:1.65,z:0},{x:.2,y:-1.15,z:-.05},{x:-.08,y:-.12,z:.02},.90,"back.out(1.45)");
tl.to(tv.rotation,{y:.36,x:.05,duration:.8,ease:"power2.inOut"},1.16);
// Pivot — clapper impact and a controlled particle burst.
reveal(clapper,2.98,4.55,{x:-5,y:1.2,z:-1},{x:0,y:1.6,z:.8},{x:.3,y:-.9,z:-.2},{x:0,y:.1,z:-.06},.82);
tl.fromTo(particles.scale,{x:.001,y:.001,z:.001},{x:1,y:1,z:1,duration:.35,ease:"power3.out",immediateRender:false},3.25);
tl.to(particles.rotation,{z:1.2,duration:1.1,ease:"power1.out"},3.3);tl.to(particles.scale,{x:.001,y:.001,z:.001,duration:.25},4.55);
// Brand reveal — two physical orbit rings and floating entertainment objects.
reveal(orbit,4.18,8.36,{x:0,y:1.8,z:-1},{x:0,y:1.8,z:0},{x:.5,y:0,z:0},{x:.18,y:.4,z:0},.98,"power3.out");
tl.to(orbit.rotation,{x:.78,y:Math.PI*1.65,z:.25,duration:3.7,ease:"none"},4.3);
reveal(popcorn,4.60,8.25,{x:5,y:-1.25,z:-3},{x:2.65,y:-1.35,z:.5},{x:.2,y:1.8,z:.2},{x:-.1,y:.15,z:-.08},.68);
reveal(headphones,5,8.28,{x:-5,y:-1.6,z:-2},{x:-2.7,y:-1.55,z:.6},{x:.5,y:-1.3,z:-.3},{x:0,y:.2,z:.08},.70);
tl.to(tv.rotation,{y:Math.PI*.95,z:.1,duration:1.4,ease:"power2.inOut"},7);
// Catalogue — five original cards rotate through staggered depth planes.
const starts=[8.55,9.30,10.05,10.82,11.58],ends=[13.45,13.55,13.62,13.70,13.72];
const from=[{x:-5.4,y:2,z:-4},{x:5.2,y:1.55,z:-4},{x:-4.8,y:-1.9,z:-3},{x:4.9,y:-1.5,z:-4},{x:0,y:5.8,z:-5}];
const to=[{x:-2.35,y:1.55,z:.8},{x:2.3,y:1.35,z:1.2},{x:-2.55,y:-1.35,z:.4},{x:2.55,y:-1.25,z:.7},{x:0,y:2.55,z:.6}];
cards.forEach((o,i)=>{reveal(o,starts[i],ends[i],from[i],to[i],{x:.2+i*.08,y:(i%2?1:-1)*1,z:(i%2?.3:-.3)},{x:.02,y:(i%2?.18:-.18),z:(i-2)*.03},.76);tl.to(o.rotation,{y:(i%2?.38:-.38),duration:1.6,ease:"sine.inOut"},starts[i]+.55);});
reveal(ball,11.45,13.7,{x:5,y:-2.7,z:-2},{x:2.75,y:-2,z:.8},{x:0,y:2,z:.4},{x:.2,y:-.1,z:0},.58);
reveal(radio,12,13.7,{x:-5,y:-2.4,z:-3},{x:-2.7,y:-2.15,z:.5},{x:.1,y:-1.4,z:-.2},{x:0,y:.2,z:.05},.60);
reveal(gamepad,12.55,13.72,{x:5,y:2.9,z:-4},{x:2.55,y:2.35,z:.1},{x:.3,y:1.5,z:.2},{x:0,y:-.2,z:-.08},.53);
// Search — a 3D magnifier sweeps toward the viewer.
reveal(magnifier,13.82,16.18,{x:-5,y:2.1,z:-2},{x:1.6,y:1.65,z:1.8},{x:.15,y:-1.3,z:-.65},{x:.05,y:.2,z:-.55},.82);
tl.to(camera.position,{x:.55,y:.12,z:18.5,duration:1.05,ease:"power2.inOut"},14);
tl.to(magnifier.rotation,{z:-1,duration:.6,ease:"power2.inOut"},14.75);
// Wi-Fi — a sculpted router, antennas and concentric signal waves.
reveal(router,16.28,20.45,{x:0,y:-1.3,z:-3},{x:0,y:1.25,z:.7},{x:.55,y:-.85,z:-.1},{x:0,y:-.1,z:0},.82);
tl.to(router.rotation,{y:.32,x:-.06,duration:1,ease:"power2.inOut"},17.2);
[0,1,2].forEach(i=>{const wave=torus(router,1.05+i*.42,.035,M.lime,0,1.22,0.28);wave.scale.set(.001,.001,.001);tl.fromTo(wave.scale,{x:.001,y:.001,z:.001},{x:1.2,y:1.2,z:1.2,duration:.35,ease:"power2.out",immediateRender:false},17+i*.38);tl.to(wave.scale,{x:.001,y:.001,z:.001,duration:.22},18.4+i*.38);});
// Three devices land one after another.
reveal(phone,20.62,22.72,{x:-6,y:-.9,z:-2},{x:-2.35,y:.55,z:.8},{x:.2,y:-1,z:-.1},{x:.04,y:.16,z:-.03},.70);
reveal(tablet,21.12,22.75,{x:0,y:4,z:-4},{x:0,y:.35,z:.6},{x:-.8,y:.4,z:.15},{x:.05,y:-.08,z:0},.70);
reveal(tvScreen,21.62,22.78,{x:6,y:-1.2,z:-3},{x:2.45,y:.6,z:.5},{x:.2,y:1.15,z:.1},{x:-.04,y:-.16,z:.03},.68);
tl.to(camera.position,{x:-.3,y:0,z:19.4,duration:.85,ease:"power2.inOut"},21);
// A true 3D stopwatch marks the 24-hour trial.
reveal(stopwatch,22.86,24.95,{x:-5,y:1.7,z:-3},{x:-1.85,y:1.55,z:.8},{x:.2,y:-1.3,z:-.4},{x:.05,y:.12,z:.05},.90);
tl.to(stopwatch.rotation,{z:Math.PI*2.1,duration:1.8,ease:"none"},23);
// Gift and coins orbit the price cards.
reveal(bag,25.05,29.3,{x:-5,y:-1.3,z:-3},{x:-2.65,y:-1.55,z:.5},{x:.4,y:-1.1,z:-.3},{x:0,y:.15,z:.08},.70);
reveal(gift,25.85,29.3,{x:5,y:-1,z:-3},{x:2.6,y:-1.3,z:.6},{x:.15,y:1.4,z:.25},{x:0,y:-.15,z:-.05},.72);
reveal(coinA,26,29.2,{x:0,y:5,z:-2},{x:-1.4,y:2.75,z:1},{x:0,y:0,z:0},{x:1.8,y:.2,z:1.4},.47);
reveal(coinB,26.45,29.2,{x:4,y:4,z:-3},{x:1.55,y:2.75,z:.8},{x:0,y:0,z:0},{x:1.2,y:.7,z:-1.2},.42);
reveal(coinC,27,29.2,{x:-4,y:4,z:-3},{x:.05,y:2.75,z:.9},{x:0,y:0,z:0},{x:.6,y:-1.2,z:1.4},.40);
// Signature — a final 3D orbit and a controlled pull-back behind the official logo.
tl.fromTo(particles.scale,{x:.001,y:.001,z:.001},{x:1.25,y:1.25,z:1.25,duration:.6,ease:"power3.out",immediateRender:false},29.48);
// Keep the final logo/CTA unobstructed: the large orbit rings belong only to the brand reveal.
tl.to(camera.position,{x:0,y:0,z:20.8,duration:3,ease:"power2.out"},29.55);
const l3=document.getElementById("logo3"),l10=document.getElementById("logo10");
if(l3)tl.to(l3,{rotationX:8,rotationY:360,rotationZ:-1,transformPerspective:1800,duration:3.1,ease:"power2.inOut"},4.25);
if(l10)tl.to(l10,{rotationX:5,rotationY:360,rotationZ:0,transformPerspective:1800,duration:3,ease:"power2.inOut"},30);
function draw(){renderer.render(scene,camera);}
// Draw on timeline seeks/updates only; no idle 60fps loop during browser QA.
tl.eventCallback("onUpdate",draw);
draw();window.__MISSA_3D__={renderer,scene,camera};
})();