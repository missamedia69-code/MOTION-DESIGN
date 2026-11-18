<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<title>MISSA TV 360 — pub motion design 9:16</title>
<script src="vendor/gsap.min.js"></script>
<style>
@font-face { font-family: "Nunito"; src: url("vendor/Nunito-Variable.ttf") format("truetype"); font-weight: 200 1000; }
@font-face { font-family: "Mont"; src: url("vendor/Montserrat-Black.ttf") format("truetype"); font-weight: 900; }
@font-face { font-family: "MontXB"; src: url("vendor/Montserrat-ExtraBold.ttf") format("truetype"); font-weight: 800; }
:root { --jaune:#FDE503; --bleu:#0141AA; --nuit:#06122E; --nuit2:#0B2560; --vert:#08992D; --citron:#A6E31B; --rouge:#E53935; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1920px; overflow:hidden; background:var(--nuit); }
body { font-family:"Nunito",sans-serif; color:#fff; }
#root { position:relative; width:1080px; height:1920px; overflow:hidden; background:var(--nuit); }
.scene { position:absolute; inset:0; overflow:hidden; }
.cam { position:absolute; inset:0; transform-origin:50% 40%; }
.abs { position:absolute; }
.H { font-family:"Mont",sans-serif; font-weight:900; text-transform:uppercase; line-height:.98; }
.XB { font-family:"MontXB",sans-serif; font-weight:800; }
.it { font-style:italic; }
.c { left:0; right:0; text-align:center; }
.o0 { opacity:0; }
.nightbg { background: radial-gradient(ellipse 90% 60% at 50% 38%, var(--nuit2) 0%, var(--nuit) 62%, #030918 100%); }
.yellowbg { background: radial-gradient(ellipse 80% 60% at 50% 40%, #fff45a 0%, var(--jaune) 50%, #f0cf00 100%); }
.greybg { background: radial-gradient(ellipse 80% 60% at 50% 42%, #4a505c 0%, #2a2e36 60%, #15181e 100%); }
.grain { position:absolute; inset:-50px; opacity:.06; pointer-events:none;
  background-image: repeating-radial-gradient(circle at 17% 23%, #fff 0 1px, transparent 1px 3px), repeating-radial-gradient(circle at 71% 63%, #fff 0 1px, transparent 1px 4px); }
.rays { position:absolute; left:50%; top:40%; width:2600px; height:2600px; margin:-1300px 0 0 -1300px; border-radius:50%;
  background: repeating-conic-gradient(from 0deg, rgba(255,255,255,.28) 0deg 7deg, transparent 7deg 18deg);
  -webkit-mask: radial-gradient(circle, #000 0%, transparent 62%); mask: radial-gradient(circle, #000 0%, transparent 62%); }
.corner { position:absolute; width:620px; height:620px; overflow:hidden; pointer-events:none; }
.corner i { position:absolute; left:-40%; width:180%; height:46px; background:var(--vert); transform:rotate(-38deg); border-radius:30px; }
.corner i:nth-child(2) { height:20px; background:#13b53c; } .corner i:nth-child(3) { height:12px; background:var(--citron); }
.corner.tl { left:0; top:0; } .corner.tl i:nth-child(1){top:60px} .corner.tl i:nth-child(2){top:128px} .corner.tl i:nth-child(3){top:166px}
.corner.br { right:0; bottom:0; transform:rotate(180deg); } .corner.br i:nth-child(1){top:60px} .corner.br i:nth-child(2){top:128px} .corner.br i:nth-child(3){top:166px}
.dots { position:absolute; inset:0; pointer-events:none; }
.dots b { position:absolute; width:8px; height:8px; border-radius:50%; background:var(--citron); box-shadow:0 0 14px var(--citron); opacity:.55; }
.el { position:absolute; filter: drop-shadow(0 26px 30px rgba(0,0,0,.35)); }
.glow { filter: drop-shadow(0 0 30px rgba(166,227,27,.55)) drop-shadow(0 26px 30px rgba(0,0,0,.35)); }
.box-accent { display:inline-block; background:var(--jaune); color:var(--nuit); padding:0 .18em; border-radius:.12em; }
.box-vert { display:inline-block; background:var(--vert); color:#fff; padding:.06em .28em; border-radius:.5em; }
.flash { position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none; }

/* --- scène 1 : monde gris --- */
#tvgris { z-index:1; left:190px; top:520px; width:700px; filter: grayscale(1) brightness(.85) contrast(1.1) drop-shadow(0 30px 40px rgba(0,0,0,.6)); }
#tvscreen { z-index:2; left:330px; top:740px; width:420px; height:300px; border-radius:26px; overflow:hidden;
  background: repeating-linear-gradient(0deg, #8a8f98 0 3px, #6c717a 3px 6px); }
#tvscreen .lab { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#2a2e36; }
#tvscreen .lab .a { font-family:"Mont"; font-size:58px; letter-spacing:.02em; }
#tvscreen .lab .b { font-family:"MontXB"; font-size:30px; margin-top:6px; }
#chan { left:690px; top:760px; font-family:"MontXB"; font-size:34px; color:#d8dbe0; }
#ticket { z-index:0; left:770px; top:300px; width:300px; padding:28px 26px 40px; background:#e6e2d8; color:#2b2b2b; font-family:monospace; font-size:24px; line-height:1.55; transform:rotate(8deg);
  box-shadow: 0 20px 40px rgba(0,0,0,.5); -webkit-mask: linear-gradient(#000 92%, transparent); }
#ticket .row { display:flex; justify-content:space-between; }
.t1 { z-index:5; top:230px; font-size:92px; color:#e9ebef; text-shadow:0 8px 30px rgba(0,0,0,.6); }
.t1 span { display:inline-block; }
.glitch { position:relative; }
#g2 { z-index:5; top:1170px; font-size:86px; color:#fff; white-space:nowrap; }
#g2 .r, #g2 .cy { position:absolute; left:0; right:0; top:0; mix-blend-mode:screen; }
#g2 .r { color:#ff3355; } #g2 .cy { color:#33e0ff; }

/* --- scène 2 : pivot --- */
#ring { left:540px; top:900px; width:300px; height:300px; margin:-150px 0 0 -150px; border-radius:50%; border:26px solid var(--jaune); box-shadow:0 0 80px var(--jaune); }
#pv1 { top:640px; font-size:150px; color:#fff; }
#pv2 { top:820px; font-size:230px; color:var(--jaune); text-shadow:0 0 60px rgba(253,229,3,.45); }

/* --- scène 3 : révélation --- */
#logo3 { left:120px; top:200px; width:840px; }
#tag1 { top:960px; font-size:88px; color:var(--bleu); }
#tag2 { top:1170px; }
#tag2 span { font-family:"Mont"; font-size:64px; font-style:italic; padding:16px 44px; border-radius:60px; background:linear-gradient(180deg,#14b33e,var(--vert)); color:#fff; box-shadow:0 14px 0 #06701f, 0 24px 40px rgba(0,0,0,.25); display:inline-block; }

/* --- téléphone générique --- */
.phone { position:absolute; width:500px; height:1020px; border-radius:72px; background:#0a0f1d; padding:16px;
  box-shadow: inset 0 0 0 4px #2b3550, 0 50px 90px rgba(0,0,0,.55), 0 0 0 2px #000; }
.phone .scr { position:relative; width:100%; height:100%; border-radius:58px; overflow:hidden; background:#070b16; }
.phone .notch { position:absolute; left:50%; top:22px; width:130px; height:34px; margin-left:-65px; border-radius:20px; background:#000; z-index:5; }
.ui-top { position:absolute; left:0; right:0; top:70px; padding:0 28px; display:flex; align-items:center; justify-content:space-between; }
.ui-logo { font-family:"Mont"; font-size:34px; color:var(--jaune); }
.ui-logo b { font-size:20px; background:var(--vert); color:#fff; padding:2px 10px; border-radius:20px; margin-left:6px; vertical-align:middle; }
.ui-ic { width:44px; height:44px; border-radius:50%; background:#18213a; }
.pills { position:absolute; top:140px; left:24px; display:flex; gap:12px; }
.pills i { font-style:normal; font-family:"Nunito"; font-weight:800; font-size:22px; padding:8px 18px; border-radius:30px; background:#18213a; color:#cfd6e6; }
.pills i.on { background:var(--jaune); color:var(--nuit); }
.hero { position:absolute; left:24px; right:24px; top:200px; height:330px; border-radius:28px; overflow:hidden; background-size:cover; background-position:center 30%; }
.hero::after { content:""; position:absolute; inset:0; background:linear-gradient(180deg, transparent 40%, rgba(5,9,20,.95)); }
.hero .ht { position:absolute; left:24px; bottom:74px; z-index:2; font-family:"Mont"; font-size:40px; color:#fff; }
.hero .hb { position:absolute; left:24px; bottom:22px; z-index:2; font-family:"MontXB"; font-size:22px; background:var(--jaune); color:var(--nuit); padding:8px 22px; border-radius:30px; }
.rowt { position:absolute; left:28px; font-family:"MontXB"; font-size:24px; color:#fff; }
.rowt::before { content:""; display:inline-block; width:6px; height:24px; background:var(--jaune); margin-right:10px; vertical-align:-3px; border-radius:3px; }
.thumbs { position:absolute; left:24px; display:flex; gap:14px; }
.thumbs img { width:132px; height:200px; object-fit:cover; border-radius:16px; }
.live { position:absolute; font-family:"MontXB"; font-size:22px; background:var(--rouge); color:#fff; padding:4px 14px; border-radius:8px; }
.live::before { content:"●"; margin-right:6px; }

/* --- scène 4 : catalogue --- */
#ph4 { left:290px; top:400px; }
#h4a, #h4b { top:200px; font-size:92px; }
.lbl { position:absolute; font-family:"Mont"; font-size:40px; color:#fff; background:rgba(6,18,46,.85); border:3px solid var(--citron); padding:6px 22px; border-radius:40px; box-shadow:0 0 24px rgba(166,227,27,.45); }

/* --- scène 5 : recherche --- */
#h5 { top:190px; font-size:96px; }
#sbar { left:70px; top:380px; width:940px; height:130px; border-radius:70px; background:#fff; box-shadow:0 0 0 6px var(--citron), 0 0 50px rgba(166,227,27,.6), 0 30px 50px rgba(0,0,0,.4); display:flex; align-items:center; padding-left:120px; }
#sbar .q { font-family:"MontXB"; font-size:62px; color:var(--nuit); white-space:pre; }
#sbar .cur { width:6px; height:70px; background:var(--bleu); margin-left:6px; }
#sbar .mg { position:absolute; left:34px; top:31px; width:68px; height:68px; }
#kb { left:70px; top:1000px; width:940px; padding:24px; border-radius:40px; background:#111a33; display:grid; grid-template-columns:repeat(10,1fr); gap:12px; }
#kb i { font-style:normal; height:76px; border-radius:14px; background:#1f2a4a; color:#cfd6e6; font-family:"MontXB"; font-size:34px; display:flex; align-items:center; justify-content:center; }
#res { left:70px; top:570px; width:940px; display:flex; gap:22px; }
#res img { width:290px; height:420px; object-fit:cover; border-radius:26px; box-shadow:0 20px 40px rgba(0,0,0,.5); }
#big { left:250px; top:540px; width:580px; height:860px; border-radius:40px; overflow:hidden; box-shadow:0 0 0 8px var(--jaune), 0 0 80px rgba(253,229,3,.6), 0 40px 70px rgba(0,0,0,.6); }
#big img { width:100%; height:100%; object-fit:cover; }
#big .play { position:absolute; left:50%; bottom:60px; transform:translateX(-50%); font-family:"Mont"; font-size:46px; color:var(--nuit); background:var(--jaune); padding:20px 50px; border-radius:60px; white-space:nowrap; box-shadow:0 12px 0 #c9a800; }
#stamp5 { left:590px; top:500px; font-size:84px; color:var(--nuit); background:var(--citron); padding:10px 34px; border-radius:24px; transform:rotate(-8deg); box-shadow:0 18px 40px rgba(0,0,0,.45); }

/* --- scène 6 : technique --- */
#router { left:330px; top:600px; width:420px; height:190px; border-radius:40px; background:linear-gradient(180deg,#ffffff,#cfd6e6); box-shadow:inset 0 -10px 0 #aab3c7, 0 40px 60px rgba(0,0,0,.5); }
#router .ant { position:absolute; bottom:150px; width:22px; height:200px; border-radius:12px; background:linear-gradient(90deg,#e8ecf4,#aab3c7); }
#router .led { position:absolute; top:120px; width:22px; height:22px; border-radius:50%; background:var(--citron); box-shadow:0 0 16px var(--citron); }
#router .brand { position:absolute; left:0; right:0; top:40px; text-align:center; font-family:"Mont"; font-size:40px; color:var(--bleu); }
.arc { position:absolute; left:540px; top:600px; border:14px solid var(--citron); border-color:var(--citron) transparent transparent transparent; border-radius:50%; box-shadow:0 -6px 30px -6px var(--citron); }
#h6 { top:190px; font-size:84px; }
.card6 { position:absolute; border-radius:36px; background:rgba(11,37,96,.85); border:3px solid #23407f; box-shadow:0 30px 50px rgba(0,0,0,.4); }
#gauge { left:60px; top:840px; width:460px; height:400px; }
#player { left:560px; top:840px; width:460px; height:400px; overflow:hidden; }
#player img { position:absolute; left:20px; top:20px; width:420px; height:236px; object-fit:cover; border-radius:22px; }
#player .bar { position:absolute; left:30px; right:30px; top:286px; height:16px; border-radius:10px; background:#23407f; overflow:hidden; }
#player .bar i { position:absolute; left:0; top:0; bottom:0; width:100%; background:var(--citron); box-shadow:0 0 14px var(--citron); transform-origin:0 50%; }
.c6t { position:absolute; left:0; right:0; text-align:center; font-family:"Mont"; font-size:40px; }
#data { left:60px; top:1262px; width:960px; height:110px; display:flex; align-items:center; padding:0 36px; gap:24px; }
#data .dl { font-family:"Mont"; font-size:38px; white-space:nowrap; }
#data .db { position:relative; flex:1; height:30px; border-radius:16px; background:#23407f; overflow:hidden; }
#data .db i { position:absolute; left:0; top:0; bottom:0; width:100%; background:linear-gradient(90deg,var(--citron),var(--vert)); transform-origin:0 50%; }

/* --- scène 7 : écrans --- */
.tvset { position:absolute; width:980px; height:580px; border-radius:22px; background:#0a0f1d; padding:14px; box-shadow:0 0 0 3px #2b3550, 0 40px 80px rgba(0,0,0,.6); }
.tvset .scr, .tab .scr { position:relative; width:100%; height:100%; border-radius:12px; overflow:hidden; background-size:cover; background-position:center 30%; }
.tvset .foot { position:absolute; left:50%; bottom:-70px; width:300px; height:70px; margin-left:-150px; background:linear-gradient(#1a2238,#0a0f1d); clip-path:polygon(40% 0,60% 0,100% 100%,0 100%); }
.tab { position:absolute; width:620px; height:440px; border-radius:40px; background:#0a0f1d; padding:18px; box-shadow:0 0 0 3px #2b3550, 0 40px 80px rgba(0,0,0,.6); }
.scr .ov { position:absolute; inset:0; background:linear-gradient(180deg, transparent 45%, rgba(5,9,20,.9)); }
.scr .tt { position:absolute; left:4%; bottom:8%; font-family:"Mont"; color:#fff; }
.scr .tb { position:absolute; left:4%; top:5%; font-family:"Mont"; color:var(--jaune); }
.dlab { position:absolute; font-family:"Mont"; font-size:64px; }

/* --- scène 8 : essai --- */
#sw { left:20px; top:330px; width:420px; }
#arc8 { left:-30px; top:250px; width:520px; height:520px; }
#h24 { left:440px; top:380px; font-size:250px; color:var(--bleu); font-style:italic; text-shadow:0 10px 0 rgba(1,65,170,.25); }
#essai { left:470px; top:640px; font-size:96px; color:var(--bleu); font-style:italic; }
#gratuit { left:150px; top:880px; width:800px; text-align:center; font-size:150px; color:#fff; font-style:italic; background:linear-gradient(180deg,#ff4d4d,#d42020); border-radius:40px; padding:22px 0; transform:rotate(-5deg); box-shadow:0 18px 0 #9c1414, 0 40px 60px rgba(0,0,0,.3); }

/* --- scène 9 : prix --- */
#h9 { top:190px; font-size:110px; }
.pcard { position:absolute; left:110px; width:860px; border-radius:50px; padding:30px 40px; color:#fff; box-shadow:0 20px 0 rgba(0,0,0,.25), 0 40px 70px rgba(0,0,0,.45); }
#pc1 { top:360px; height:330px; background:linear-gradient(160deg,#2a6bff,var(--bleu) 60%,#012f7d); border:6px solid #fff; }
#pc2 { top:800px; height:330px; background:linear-gradient(160deg,#25c74e,var(--vert) 60%,#05701f); border:6px solid #fff; }
.pcard .s { font-family:"Mont"; font-style:italic; font-size:52px; }
.pcard .n { position:absolute; left:40px; top:110px; font-family:"Mont"; font-style:italic; font-size:170px; letter-spacing:-.02em; }
.pcard .u { position:absolute; right:50px; top:120px; font-family:"Mont"; font-style:italic; font-size:62px; text-align:left; line-height:1; }
.pcard .u b { color:var(--jaune); display:block; }
#ou { left:465px; top:680px; width:150px; height:150px; border-radius:50%; background:#fff; color:var(--bleu); font-family:"Mont"; font-style:italic; font-size:64px; display:flex; align-items:center; justify-content:center; box-shadow:0 14px 30px rgba(0,0,0,.4); z-index:3; }
#offert { left:170px; top:1110px; width:740px; text-align:center; font-family:"Mont"; font-style:italic; font-size:76px; color:var(--nuit); background:linear-gradient(180deg,#fff45a,var(--jaune)); border-radius:30px; padding:16px 0; transform:rotate(-3deg); box-shadow:0 14px 0 #c9a800, 0 30px 50px rgba(0,0,0,.35); z-index:4; }
#gift { left:860px; top:1180px; width:190px; z-index:5; }
#popper { left:20px; top:1180px; width:180px; z-index:5; }

/* --- scène 10 : CTA --- */
#logo10 { left:200px; top:150px; width:680px; }
#slogan { top:752px; font-size:56px; white-space:nowrap; color:var(--bleu); font-style:italic; }
#slogan b { color:var(--vert); }
#cta { left:90px; top:860px; width:900px; height:170px; border-radius:90px; background:linear-gradient(180deg,#1fc24a,var(--vert)); box-shadow:0 16px 0 #05701f, 0 0 0 8px rgba(255,255,255,.7), 0 40px 60px rgba(0,0,0,.3); display:flex; align-items:center; justify-content:center; gap:30px; }
#cta .ar { width:90px; height:90px; }
#cta .tx { font-family:"Mont"; font-style:italic; font-size:62px; line-height:1; color:#fff; text-shadow:0 5px 0 #05701f; }
#cta .tx b { color:var(--jaune); }
#qrc { left:250px; top:1080px; width:580px; height:250px; border-radius:36px; background:#fff; box-shadow:0 30px 50px rgba(0,0,0,.25); display:flex; align-items:center; gap:24px; padding:20px; }
#qrc img { width:210px; height:210px; }
#qrc .qt { font-family:"Mont"; font-size:34px; color:var(--nuit); line-height:1.1; }
#qrc .qt span { display:block; font-family:"MontXB"; font-size:30px; color:var(--bleu); margin-top:10px; }

/* --- sous-titres --- */
.sub { position:absolute; left:60px; right:60px; top:1395px; display:flex; justify-content:center; }
.sub p { background:rgba(6,18,46,.86); border-radius:26px; padding:14px 30px; font-family:"Nunito"; font-weight:900; font-size:52px; line-height:1.15; text-align:center; color:#fff; box-shadow:0 10px 30px rgba(0,0,0,.35); }
.sub p span { display:inline-block; margin:0 .16em; }
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="__DUR__" data-width="1080" data-height="1920">

<!-- 1 · accroche : le monde gris -->
<div id="sc1" class="scene clip greybg" data-start="0" data-duration="3.0" data-track-index="0">
 <div class="cam" id="cam1">
  <div id="ticket" class="abs" data-layout-allow-overlap>
   <div style="text-align:center;font-weight:bold">ABONNEMENT TÉLÉ</div><div>------------------</div>
   <div class="row"><span>JANVIER</span><span>PAYÉ</span></div><div class="row"><span>FÉVRIER</span><span>PAYÉ</span></div>
   <div class="row"><span>MARS</span><span>PAYÉ</span></div><div class="row"><span>AVRIL</span><span>PAYÉ</span></div>
   <div class="row"><span>MAI</span><span>PAYÉ</span></div><div class="row"><span>JUIN</span><span>PAYÉ</span></div>
   <div class="row"><span>JUILLET</span><span>PAYÉ</span></div><div class="row"><span>AOÛT</span><span>PAYÉ</span></div>
   <div>------------------</div><div style="text-align:center">PROGRAMME :</div><div style="text-align:center;font-weight:bold">TOUJOURS LE MÊME</div>
  </div>
  <img id="tvgris" class="abs" src="assets/elements/television-3d.png" />
  <div id="tvscreen" class="abs"><div class="lab"><div class="a">REDIFF</div><div class="b" id="rediff">ÉPISODE 1</div></div></div>
  <div id="chan" class="abs">CH 01</div>
  <div id="t1a" class="abs c H t1"><span>TU PAIES</span><br><span>CHAQUE MOIS…</span></div>
  <div id="t1b" class="abs c H t1 o0"><span>POUR TOUJOURS</span></div>
  <div id="g2" class="abs c H o0" data-layout-allow-overlap><div class="r">LA MÊME CHOSE ?</div><div class="cy">LA MÊME CHOSE ?</div><div>LA MÊME CHOSE ?</div></div>
  <div class="grain"></div>
 </div>
</div>

<!-- 2 · pivot -->
<div id="sc2" class="scene clip" data-start="2.95" data-duration="1.07" data-track-index="1" style="background:#020814">
 <div class="cam" id="cam2">
  <div id="ring" class="abs o0"></div>
  <div id="pv1" class="abs c H">ON MÉRITE</div>
  <div id="pv2" class="abs c H">MIEUX !</div>
 </div>
</div>

<!-- 3 · révélation -->
<div id="sc3" class="scene clip yellowbg" data-start="3.97" data-duration="4.56" data-track-index="2">
 <div class="cam" id="cam3">
  <div class="rays" id="rays3"></div>
  <div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>
  <img class="el" id="e3a" src="assets/elements/clapper-board-3d.png" style="left:40px;top:120px;width:220px" />
  <img class="el" id="e3b" src="assets/elements/popcorn-3d.png" style="left:820px;top:140px;width:210px" />
  <img class="el" id="e3c" src="assets/elements/headphone-3d.png" style="left:850px;top:760px;width:200px" />
  <img class="el" id="e3d" src="assets/elements/studio-microphone-3d.png" style="left:30px;top:760px;width:190px" />
  <img class="el" id="e3e" src="assets/elements/film-frames-3d.png" style="left:840px;top:1285px;width:170px" />
  <img class="el" id="logo3" src="assets/logo-3d-transparent.png" />
  <div id="tag1" class="abs c H it">TOUT TON<br>DIVERTISSEMENT,</div>
  <div id="tag2" class="abs c"><span>DANS UNE SEULE APPLI !</span></div>
 </div>
 <div class="flash" id="fl3"></div>
</div>

<!-- 4 · catalogue -->
<div id="sc4" class="scene clip nightbg" data-start="8.48" data-duration="5.32" data-track-index="3">
 <div class="cam" id="cam4">
  <div class="dots" id="dots4"></div>
  <div id="h4a" class="abs c H">DES <span class="box-accent">MILLIERS</span></div>
  <div id="h4b" class="abs c H o0">DES <span class="box-accent">CENTAINES</span><br><span style="font-size:70px">DE CHAÎNES EN DIRECT</span></div>
  <div id="ph4" class="phone" style="transform:perspective(1800px) rotateY(-16deg) rotateX(4deg)">
   <div class="scr"><div class="notch"></div>
    <div class="ui-top"><div class="ui-logo">MISSA TV<b>360+</b></div><div class="ui-ic"></div></div>
    <div class="pills"><i class="on">Accueil</i><i>Films</i><i>Séries</i><i>Live</i></div>
    <div id="feed4" class="abs" style="left:0;right:0;top:0">
     <div class="hero" style="background-image:url(assets/vignettes/royaume.jpg)"><div class="ht">ROYAUME</div><div class="hb">▶ Regarder</div></div>
     <div class="rowt" style="top:560px">Films & séries</div>
     <div class="thumbs" style="top:600px"><img src="assets/vignettes/horizon-2030.jpg"/><img src="assets/vignettes/amour-eternel.jpg"/><img src="assets/vignettes/operation-omega.jpg"/></div>
     <div class="rowt" style="top:830px">En direct</div>
     <div class="thumbs" style="top:870px"><img src="assets/vignettes/ligue-360.jpg"/><img src="assets/vignettes/nouveau-depart.jpg"/><img src="assets/vignettes/detective.jpg"/></div>
     <div class="live" style="left:36px;top:882px">LIVE</div>
     <div class="rowt" style="top:1100px">Mangas</div>
     <div class="thumbs" style="top:1140px"><img src="assets/vignettes/secret-foret.jpg"/><img src="assets/vignettes/royaume.jpg"/><img src="assets/vignettes/horizon-2030.jpg"/></div>
    </div>
   </div>
  </div>
  <img class="el glow" id="e4film" src="assets/elements/clapper-board-3d.png" style="left:40px;top:430px;width:230px" />
  <div class="lbl o0" id="l4film" style="left:50px;top:650px">FILMS</div>
  <img class="el glow" id="e4ser" src="assets/elements/film-frames-3d.png" style="left:800px;top:400px;width:240px" />
  <div class="lbl o0" id="l4ser" style="left:800px;top:620px">SÉRIES</div>
  <div class="lbl o0" id="l4man" style="left:40px;top:780px;font-size:52px;background:var(--rouge);border-color:#fff">MANGAS</div>
  <img class="el glow" id="e4tv" src="assets/elements/television-3d.png" style="left:800px;top:720px;width:240px" />
  <div class="live o0" id="l4live" style="left:850px;top:720px;font-size:30px">LIVE</div>
  <img class="el glow" id="e4ball" src="assets/elements/soccer-ball-3d.png" style="left:40px;top:960px;width:220px" />
  <div class="lbl o0" id="l4sport" style="left:50px;top:1170px">SPORT</div>
  <img class="el glow" id="e4radio" src="assets/elements/radio-3d.png" style="left:810px;top:1000px;width:240px" />
  <div class="lbl o0" id="l4radio" style="left:820px;top:1190px">RADIO</div>
  <img class="el glow" id="e4game" src="assets/elements/video-game-3d.png" style="left:340px;top:1060px;width:400px" />
  <div class="lbl o0" id="l4game" style="left:430px;top:1290px;font-size:52px">JEUX</div>
 </div>
</div>

<!-- 5 · recherche -->
<div id="sc5" class="scene clip nightbg" data-start="13.76" data-duration="2.54" data-track-index="4">
 <div class="cam" id="cam5">
  <div class="dots" id="dots5"></div>
  <div id="h5" class="abs c H">UN FILM <span class="box-accent">EN TÊTE ?</span></div>
  <div id="sbar" class="abs"><svg class="mg" viewBox="0 0 24 24" fill="none" stroke="#0141AA" stroke-width="3" stroke-linecap="round"><circle cx="10" cy="10" r="7"/><path d="M15.5 15.5 21 21"/></svg><span class="q" id="q5"></span><span class="cur" id="cur5"></span></div>
  <div id="kb" class="abs">__KEYS__</div>
  <div id="res" class="abs o0"><img src="assets/vignettes/horizon-2030.jpg"/><img src="assets/vignettes/operation-omega.jpg"/><img src="assets/vignettes/secret-foret.jpg"/></div>
  <div id="big" class="abs o0"><img src="assets/vignettes/horizon-2030.jpg"/><div class="play">▶ REGARDER</div></div>
  <img class="el" id="mag5" src="assets/elements/magnifying-glass-tilted-left-3d.png" style="left:700px;top:560px;width:300px" />
  <div id="stamp5" class="abs H o0">IL EST LÀ !</div>
  <img class="el o0" id="pop5" src="assets/elements/party-popper-3d.png" style="left:40px;top:1100px;width:240px" />
 </div>
</div>

<!-- 6 · technique -->
<div id="sc6" class="scene clip nightbg" data-start="16.25" data-duration="4.42" data-track-index="5">
 <div class="cam" id="cam6">
  <div class="dots" id="dots6"></div>
  <div id="h6" class="abs c H">TA <span class="box-accent">BOX WIFI</span> SUFFIT</div>
  <div class="arc" id="arc1" style="width:220px;height:220px;margin:-110px 0 0 -110px"></div>
  <div class="arc" id="arc2" style="width:380px;height:380px;margin:-190px 0 0 -190px"></div>
  <div class="arc" id="arc3" style="width:500px;height:500px;margin:-250px 0 0 -250px"></div>
  <div id="router" class="abs"><div class="ant" style="left:60px;transform:rotate(-12deg)"></div><div class="ant" style="right:60px;transform:rotate(12deg)"></div>
   <div class="brand">MISSA</div><div class="led" style="left:150px"></div><div class="led" style="left:200px"></div><div class="led" style="left:250px"></div></div>
  <div id="gauge" class="card6 o0">
   <svg viewBox="0 0 460 300" style="position:absolute;left:0;top:30px;width:460px;height:300px">
    <path d="M60 250 A170 170 0 0 1 400 250" fill="none" stroke="#23407f" stroke-width="34" stroke-linecap="round"/>
    <path d="M60 250 A170 170 0 0 1 150 102" fill="none" stroke="#ff8a3d" stroke-width="34" stroke-linecap="round"/>
    <g id="needle" style="transform-origin:230px 250px"><path d="M230 250 L230 100" stroke="#fff" stroke-width="12" stroke-linecap="round"/><circle cx="230" cy="250" r="20" fill="#fff"/></g>
   </svg>
   <div class="c6t" style="top:310px;color:#ff8a3d">PETIT DÉBIT</div>
  </div>
  <div id="player" class="card6 o0"><img src="assets/vignettes/ligue-360.jpg"/><div class="bar"><i id="pbar"></i></div><div class="c6t" id="fluide" style="top:320px;color:var(--citron)">FLUIDE ✓</div></div>
  <div id="data" class="card6 o0"><div class="dl">DONNÉES</div><div class="db"><i id="dbar"></i></div><div class="dl" style="color:var(--citron)">ÉCONOMISÉES</div></div>
 </div>
</div>

<!-- 7 · écrans -->
<div id="sc7" class="scene clip nightbg" data-start="20.61" data-duration="2.24" data-track-index="6">
 <div class="cam" id="cam7">
  <div class="dots" id="dots7"></div>
  <div id="tv7" class="tvset o0" style="left:50px;top:420px"><div class="scr" style="background-image:url(assets/vignettes/royaume.jpg)"><div class="ov"></div><div class="tb" style="font-size:40px">MISSA TV 360</div><div class="tt" style="font-size:70px">ROYAUME</div></div><div class="foot"></div></div>
  <div id="tab7" class="tab o0" style="left:420px;top:820px"><div class="scr" style="background-image:url(assets/vignettes/royaume.jpg)"><div class="ov"></div><div class="tb" style="font-size:28px">MISSA TV 360</div><div class="tt" style="font-size:48px">ROYAUME</div></div></div>
  <div id="ph7" class="phone o0" style="left:120px;top:640px;transform:scale(.62);transform-origin:0 0">
   <div class="scr"><div class="notch"></div><div class="hero" style="top:80px;height:600px;background-image:url(assets/vignettes/royaume.jpg)"><div class="ht">ROYAUME</div><div class="hb">▶ Regarder</div></div>
    <div class="rowt" style="top:720px">Films & séries</div><div class="thumbs" style="top:760px"><img src="assets/vignettes/horizon-2030.jpg"/><img src="assets/vignettes/amour-eternel.jpg"/><img src="assets/vignettes/ligue-360.jpg"/></div></div>
  </div>
  <div class="dlab H o0" id="d1" style="left:80px;top:230px;color:#fff">TÉLÉPHONE,</div>
  <div class="dlab H o0" id="d2" style="left:280px;top:230px;color:var(--citron)">TABLETTE</div>
  <div class="dlab H o0" id="d3" style="left:0;right:0;top:230px;text-align:center;color:var(--jaune);font-size:110px">OU TÉLÉ.</div>
 </div>
 <div class="flash" id="fl7"></div>
</div>

<!-- 8 · essai -->
<div id="sc8" class="scene clip yellowbg" data-start="22.80" data-duration="2.30" data-track-index="7">
 <div class="cam" id="cam8">
  <div class="rays" id="rays8"></div>
  <div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>
  <svg id="arc8" class="abs" viewBox="0 0 520 520"><circle cx="260" cy="300" r="230" fill="none" stroke="rgba(1,65,170,.15)" stroke-width="22"/>
   <circle id="arc8c" cx="260" cy="300" r="230" fill="none" stroke="#08992D" stroke-width="22" stroke-linecap="round" stroke-dasharray="1445" stroke-dashoffset="1445" transform="rotate(-90 260 300)"/></svg>
  <img class="el" id="sw" src="assets/elements/stopwatch-3d.png" />
  <div id="h24" class="abs H">24H</div>
  <div id="essai" class="abs H">D'ESSAI</div>
  <div id="gratuit" class="abs H">GRATUIT</div>
 </div>
</div>

<!-- 9 · prix -->
<div id="sc9" class="scene clip nightbg" data-start="25.03" data-duration="4.52" data-track-index="8">
 <div class="cam" id="cam9">
  <div class="dots" id="dots9"></div>
  <div id="h9" class="abs c H it">ENSUITE <span class="box-accent">?</span></div>
  <div id="pc1" class="pcard o0"><div class="s">SEULEMENT</div><div class="n" id="n1">1 000</div><div class="u"><b>FCFA</b>/ mois</div></div>
  <div id="ou" class="abs o0">OU</div>
  <div id="pc2" class="pcard o0"><div class="s">TOUTE L'ANNÉE</div><div class="n" style="font-size:150px;top:118px">10 000</div><div class="u"><b>FCFA</b>/ an</div></div>
  <div id="offert" class="abs o0">2 MOIS OFFERTS !</div>
  <img class="el o0" id="gift" src="assets/elements/wrapped-gift-3d.png" />
  <img class="el o0" id="popper" src="assets/elements/party-popper-3d.png" />
 </div>
</div>

<!-- 10 · appel final -->
<div id="sc10" class="scene clip yellowbg" data-start="29.50" data-duration="__D10__" data-track-index="9">
 <div class="cam" id="cam10">
  <div class="rays" id="rays10"></div>
  <div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>
  <img class="el" id="logo10" src="assets/logo-3d-transparent.png" />
  <div id="slogan" class="abs c H o0">TON ÉCRAN <b>MÉRITE MIEUX !</b></div>
  <div id="cta" class="abs"><svg class="ar" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M6 10l6 6 6-6M4 21h16"/></svg><div class="tx">TÉLÉCHARGE<br><b>MAINTENANT !</b></div></div>
  <div id="qrc" class="abs o0"><img src="assets/qr-missatv.png"/><div class="qt">SCANNE<br>ET TÉLÉCHARGE<span>missatv.pages.dev</span></div></div>
 </div>
 <div class="flash" id="fl10"></div>
</div>

__SUBS__
</div>

<script>
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({ paused: true });
const q = (s) => document.querySelector(s);
const qa = (s) => Array.from(document.querySelectorAll(s));
const DUR = __DUR__;
// apparition « trop grande et floue qui se pose »
function pop(sel, t, o = {}) {
  tl.fromTo(sel, { opacity: 0, scale: o.from ?? 1.8, filter: "blur(12px)", rotation: o.rot ?? 0, y: o.y ?? 0 },
    { opacity: 1, scale: 1, filter: "blur(0px)", rotation: o.rotTo ?? 0, y: 0, duration: o.d ?? 0.28, ease: o.ease ?? "back.out(2)" }, t);
}
function rise(sel, t, o = {}) {
  tl.fromTo(sel, { opacity: 0, y: o.y ?? 120, scale: o.s ?? 0.6, rotation: o.rot ?? -12 },
    { opacity: 1, y: 0, scale: 1, rotation: 0, duration: o.d ?? 0.4, ease: "back.out(1.8)" }, t);
}
function floaty(sel, t0, t1, amp = 18, per = 1.6) {
  const n = Math.max(1, Math.round((t1 - t0) / per));
  tl.to(sel, { y: "-=" + amp, duration: per / 2, ease: "sine.inOut", yoyo: true, repeat: n * 2 - 1 }, t0);
}
function cam(sel, t0, t1, s0 = 1, s1 = 1.08, r = 0) {
  tl.fromTo(sel, { scale: s0, rotation: -r }, { scale: s1, rotation: r, duration: t1 - t0, ease: "none" }, t0);
}
function dots(id, n, seed) {
  const box = q(id); let x = seed;
  const rnd = () => { x = (x * 9301 + 49297) % 233280; return x / 233280; };
  for (let i = 0; i < n; i++) { const b = document.createElement("b"); b.style.left = (rnd() * 1080) + "px"; b.style.top = (rnd() * 1920) + "px"; const s = 4 + rnd() * 9; b.style.width = b.style.height = s + "px"; b.style.opacity = (.25 + rnd() * .5).toFixed(2); box.appendChild(b); }
  return box;
}
["#dots4", "#dots5", "#dots6", "#dots7", "#dots9"].forEach((d, i) => dots(d, 34, 7 + i * 13));

/* ---------- 1 · accroche ---------- */
cam("#cam1", 0, 3.0, 1.0, 1.12, 1.2);
tl.fromTo("#ticket", { y: -260 }, { y: 420, duration: 3.0, ease: "none" }, 0);
pop("#t1a span:nth-child(1)", 0.02, { from: 2.2 });
pop("#t1a span:nth-child(3)", 0.70, { from: 2.2 });
["CH 01", "CH 02", "CH 03", "CH 04"].forEach((c, i) => {
  const t = [0.0, 0.37, 1.08, 1.59][i];
  tl.set("#chan", { textContent: c }, t);
  tl.fromTo("#tvscreen", { filter: "brightness(2.5)" }, { filter: "brightness(1)", duration: 0.18 }, t);
});
tl.fromTo("#tvgris", { x: -6 }, { x: 6, duration: 0.06, repeat: 5, yoyo: true }, 1.08);
tl.to("#t1a", { opacity: 0, y: -60, duration: 0.15 }, 1.38);
pop("#t1b", 1.40, { from: 2.2 });
tl.to("#t1b", { opacity: 0, duration: 0.1 }, 2.02);
tl.set("#g2", { opacity: 1 }, 2.02);
pop("#g2 div:nth-child(3)", 2.02, { from: 2.4 });
tl.fromTo("#g2 .r", { x: -14, opacity: 0.9 }, { x: 14, duration: 0.05, repeat: 9, yoyo: true }, 2.06);
tl.fromTo("#g2 .cy", { x: 12, opacity: 0.9 }, { x: -12, duration: 0.05, repeat: 9, yoyo: true }, 2.06);
tl.to("#cam1", { scale: 1.6, filter: "blur(14px)", opacity: 0, duration: 0.22, ease: "power2.in" }, 2.78);

/* ---------- 2 · pivot ---------- */
cam("#cam2", 2.95, 4.02, 1.0, 1.06);
tl.fromTo("#pv1", { opacity: 0, scale: 3, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out" }, 2.95);
tl.fromTo("#pv2", { opacity: 0, scale: 4, filter: "blur(20px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }, 3.50);
tl.fromTo("#cam2", { x: -24 }, { x: 0, duration: 0.25, ease: "elastic.out(1,0.3)" }, 3.55);
tl.fromTo("#ring", { opacity: 1, scale: 0.2 }, { opacity: 0, scale: 5, duration: 0.55, ease: "power2.out" }, 3.53);

/* ---------- 3 · révélation ---------- */
cam("#cam3", 3.97, 8.53, 1.0, 1.07);
tl.fromTo("#fl3", { opacity: 1 }, { opacity: 0, duration: 0.3 }, 3.97);
tl.fromTo("#rays3", { rotation: 0 }, { rotation: 40, duration: 4.56, ease: "none" }, 3.97);
tl.fromTo("#logo3", { opacity: 0, scale: 0.2, rotationY: -80, transformPerspective: 1600, filter: "blur(10px)" },
  { opacity: 1, scale: 1, rotationY: 0, filter: "blur(0px)", duration: 0.7, ease: "back.out(1.6)" }, 4.20);
tl.to("#logo3", { scale: 1.08, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, 5.00);
floaty("#logo3", 5.3, 8.5, 12, 1.5);
[["#e3a", 4.55, -20], ["#e3b", 4.70, 20], ["#e3c", 5.05, 15], ["#e3d", 5.20, -15], ["#e3e", 5.40, 10]].forEach(([s, t, r], i) => {
  rise(s, t, { rot: r }); floaty(s, t + 0.4, 8.5, 14 + i * 3, 1.3 + i * 0.2);
});
tl.fromTo("#tag1", { opacity: 0, x: -200, skewX: -12 }, { opacity: 1, x: 0, skewX: 0, duration: 0.35, ease: "back.out(2)" }, 5.92);
pop("#tag2", 7.30, { from: 0.3, ease: "back.out(3)" });
tl.to("#tag2 span", { scale: 1.06, duration: 0.14, yoyo: true, repeat: 1 }, 7.83);
tl.to("#cam3", { scale: 2.2, opacity: 0, duration: 0.25, ease: "power2.in" }, 8.30);

/* ---------- 4 · catalogue ---------- */
cam("#cam4", 8.48, 13.80, 1.04, 1.0);
tl.fromTo("#ph4", { y: 900, rotationY: -40 }, { y: 0, rotationY: -16, duration: 0.5, ease: "power3.out" }, 8.48);
tl.to("#feed4", { y: -560, duration: 4.8, ease: "none" }, 8.9);
pop("#h4a", 8.50, { from: 2.4 });
rise("#e4film", 8.87, { rot: -25 }); pop("#l4film", 8.95, { from: 0.4 });
rise("#e4ser", 9.07, { rot: 25 }); pop("#l4ser", 9.15, { from: 0.4 });
pop("#l4man", 9.36, { from: 0.3, rot: -20, rotTo: -6 });
tl.to("#h4a", { opacity: 0, y: -40, duration: 0.15 }, 9.84);
pop("#h4b", 9.99, { from: 2.2 });
rise("#e4tv", 10.43, { rot: 20 }); pop("#l4live", 10.90, { from: 0.3 });
tl.to("#l4live", { opacity: 0.4, duration: 0.25, yoyo: true, repeat: 7 }, 11.2);
rise("#e4ball", 11.52, { rot: -180, d: 0.5 }); pop("#l4sport", 11.60, { from: 0.4 });
rise("#e4radio", 11.82, { rot: 25 }); pop("#l4radio", 11.90, { from: 0.4 });
tl.to("#h4b", { opacity: 0, duration: 0.15 }, 12.6);
tl.fromTo("#e4game", { opacity: 0, scale: 0.2, rotation: -30 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.5)" }, 13.02);
pop("#l4game", 13.10, { from: 0.3 });
["#e4film", "#e4ser", "#e4tv", "#e4ball", "#e4radio"].forEach((s, i) => floaty(s, 9.3 + i * 0.3, 13.8, 12, 1.2 + i * 0.15));
tl.to("#cam4", { scale: 1.9, opacity: 0, filter: "blur(10px)", duration: 0.22, ease: "power2.in" }, 13.58);

/* ---------- 5 · recherche ---------- */
cam("#cam5", 13.76, 16.30, 1.0, 1.05);
pop("#h5", 13.78, { from: 2.2 });
tl.fromTo("#sbar", { opacity: 0, scaleX: 0.3 }, { opacity: 1, scaleX: 1, duration: 0.3, ease: "back.out(1.6)" }, 13.90);
tl.fromTo("#kb", { opacity: 0, y: 300 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, 14.0);
tl.fromTo("#mag5", { opacity: 0, x: 400, y: 300, rotation: 40, scale: 1.5 }, { opacity: 1, x: -600, y: -150, rotation: -10, scale: 0.6, duration: 0.55, ease: "power3.inOut" }, 13.99);
tl.to("#mag5", { opacity: 0, duration: 0.12 }, 14.54);
tl.to("#cur5", { opacity: 0, duration: 0.01, repeat: 9, yoyo: true, repeatDelay: 0.12 }, 13.95);
const QTXT = "Horizon 2030", T0 = 14.66, T1 = 15.40;
for (let i = 1; i <= QTXT.length; i++) {
  const t = T0 + (T1 - T0) * (i - 1) / (QTXT.length - 1);
  tl.set("#q5", { textContent: QTXT.slice(0, i) }, t);
  const k = qa("#kb i")[(i * 7) % 30];
  if (k) tl.fromTo(k, { backgroundColor: "#FDE503", color: "#06122E" }, { backgroundColor: "#1f2a4a", color: "#cfd6e6", duration: 0.15 }, t);
}
tl.to("#kb", { opacity: 0, y: 300, duration: 0.2, ease: "power2.in" }, 15.42);
tl.fromTo("#res", { opacity: 0, y: -80 }, { opacity: 1, y: 0, duration: 0.2, ease: "back.out(2)" }, 15.48);
tl.fromTo("#res img", { scale: 0.5 }, { scale: 1, duration: 0.2, stagger: 0.04, ease: "back.out(2)" }, 15.48);
tl.to("#res", { opacity: 0, duration: 0.1 }, 15.70);
tl.fromTo("#big", { opacity: 0, scale: 0.5, rotationY: 50, transformPerspective: 1600 }, { opacity: 1, scale: 1, rotationY: 0, duration: 0.3, ease: "back.out(1.8)" }, 15.70);
pop("#stamp5", 15.83, { from: 2.5, rot: -20, rotTo: -8 });
rise("#pop5", 15.86, { rot: -30 });
tl.to("#cam5", { scale: 1.6, opacity: 0, duration: 0.14, ease: "power2.in" }, 16.16);

/* ---------- 6 · technique ---------- */
cam("#cam6", 16.25, 20.67, 1.0, 1.06);
pop("#h6", 16.27, { from: 2.2 });
tl.fromTo("#router", { opacity: 0, y: 200, scale: 0.6 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.8)" }, 16.50);
["#arc1", "#arc2", "#arc3"].forEach((a, i) => {
  tl.fromTo(a, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }, 16.97 + i * 0.1);
  tl.to(a, { opacity: 0.25, duration: 0.3, yoyo: true, repeat: 5, ease: "sine.inOut" }, 17.4 + i * 0.15);
});
rise("#gauge", 17.34, { rot: -6 });
tl.fromTo("#needle", { rotation: 60 }, { rotation: -55, duration: 0.6, ease: "power3.inOut" }, 17.54);
tl.to("#needle", { rotation: -50, duration: 0.12, yoyo: true, repeat: 9, ease: "sine.inOut" }, 18.2);
rise("#player", 18.10, { rot: 6 });
tl.fromTo("#pbar", { scaleX: 0.05 }, { scaleX: 0.85, duration: 2.4, ease: "none" }, 18.2);
pop("#fluide", 18.50, { from: 2.0 });
rise("#data", 19.40, { rot: 0, y: 80 });
tl.fromTo("#dbar", { scaleX: 0.9 }, { scaleX: 0.25, duration: 0.7, ease: "power3.out" }, 19.58);
tl.to("#cam6", { x: -1080, duration: 0.25, ease: "power3.in" }, 20.42);

/* ---------- 7 · écrans ---------- */
cam("#cam7", 20.61, 22.85, 1.0, 1.05);
tl.fromTo("#ph7", { opacity: 0, y: 500, rotation: -15 }, { opacity: 1, y: 0, rotation: 0, duration: 0.35, ease: "back.out(1.6)" }, 20.61);
pop("#d1", 20.63, { from: 2 });
tl.fromTo("#tab7", { opacity: 0, x: 600, rotation: 15 }, { opacity: 1, x: 0, rotation: 0, duration: 0.35, ease: "back.out(1.6)" }, 21.25);
tl.to("#d1", { x: -60, opacity: 0.35, duration: 0.2 }, 21.25);
tl.set("#d2", { left: 560 }, 21.25); pop("#d2", 21.27, { from: 2 });
tl.fromTo("#tv7", { opacity: 0, scale: 0.4, y: -200 }, { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: "back.out(1.4)" }, 21.80);
tl.to(["#d1", "#d2"], { opacity: 0, duration: 0.12 }, 21.80);
pop("#d3", 21.85, { from: 2.4 });
tl.fromTo("#fl7", { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "power2.in" }, 22.66);

/* ---------- 8 · essai ---------- */
cam("#cam8", 22.80, 25.10, 1.0, 1.07);
tl.fromTo("#rays8", { rotation: 0 }, { rotation: 30, duration: 2.3, ease: "none" }, 22.8);
tl.fromTo("#sw", { opacity: 0, scale: 0.2, rotation: -90 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2)" }, 22.85);
tl.to("#sw", { rotation: 8, duration: 0.1, yoyo: true, repeat: 15, ease: "sine.inOut" }, 23.3);
tl.fromTo("#arc8c", { attr: { "stroke-dashoffset": 1445 } }, { attr: { "stroke-dashoffset": 0 }, duration: 2.1, ease: "power1.inOut" }, 22.9);
pop("#gratuit", 23.63, { from: 2.6, rot: -15, rotTo: -5, ease: "back.out(2.5)" });
pop("#h24", 23.28, { from: 3 });
pop("#essai", 23.95, { from: 2 });
tl.to("#h24", { scale: 1.12, duration: 0.14, yoyo: true, repeat: 1 }, 24.56);
tl.to("#cam8", { scale: 1.8, opacity: 0, duration: 0.2, ease: "power2.in" }, 24.92);

/* ---------- 9 · prix ---------- */
cam("#cam9", 25.03, 29.55, 1.0, 1.05);
pop("#h9", 25.05, { from: 2.4 });
rise("#pc1", 25.55, { rot: -6, y: 200 });
const cnt = { v: 0 };
tl.fromTo(cnt, { v: 0 }, { v: 1000, duration: 0.6, ease: "power2.out", onUpdate: () => { q("#n1").textContent = Math.round(cnt.v).toLocaleString("fr-FR").replace(/\s/g, " "); } }, 25.6);
pop("#ou", 27.22, { from: 0.2, ease: "back.out(3)" });
rise("#pc2", 27.42, { rot: 6, y: 200 });
pop("#offert", 28.32, { from: 2.5, rot: -12, rotTo: -3 });
rise("#gift", 28.55, { rot: 25 }); rise("#popper", 28.80, { rot: -25 });
floaty("#gift", 29.0, 29.5, 10, 0.5);
tl.to("#cam9", { scale: 1.8, opacity: 0, duration: 0.2, ease: "power2.in" }, 29.32);

/* ---------- 10 · appel final ---------- */
cam("#cam10", 29.50, DUR, 1.0, 1.05);
tl.fromTo("#fl10", { opacity: 1 }, { opacity: 0, duration: 0.3 }, 29.50);
tl.fromTo("#rays10", { rotation: 0 }, { rotation: 30, duration: DUR - 29.5, ease: "none" }, 29.5);
tl.fromTo("#cta", { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.4)" }, 29.52);
tl.to("#cta", { scale: 1.06, duration: 0.3, yoyo: true, repeat: Math.floor((DUR - 30.0) / 0.3) - 1, ease: "sine.inOut" }, 30.0);
tl.fromTo("#logo10", { opacity: 0, scale: 0.3, rotationY: 90, transformPerspective: 1600 }, { opacity: 1, scale: 1, rotationY: 0, duration: 0.6, ease: "back.out(1.6)" }, 30.05);
floaty("#logo10", 30.7, DUR, 10, 1.4);
rise("#qrc", 30.80, { rot: -4, y: 160 });
pop("#slogan", 31.94, { from: 2.2 });

/* ---------- sous-titres : mot courant en jaune ---------- */
__SUBJS__

window.__timelines["main"] = tl;
</script>
</body>
</html>
