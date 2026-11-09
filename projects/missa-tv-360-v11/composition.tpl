<!doctype html>
<html lang="fr" class="__FMT__">
  <head>
    <meta charset="utf-8" />
    <title>MISSA TV 360 — spot 60 s (DA v2, essai gratuit 24 h)</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Nunito"; src: url("vendor/Nunito-Variable.ttf") format("truetype"); font-weight: 200 1000; }
      @font-face { font-family: "Montserrat"; src: url("vendor/Montserrat-Black.ttf") format("truetype"); font-weight: 900; }
      @font-face { font-family: "MontserratXB"; src: url("vendor/Montserrat-ExtraBold.ttf") format("truetype"); font-weight: 800; }
      :root {
        --jaune: #fae504; --bleu: #1f34c8; --vert: #0b9a2f; --menthe: #2ecc71;
        --or: #f6be00; --noir: #0b0d12; --gris: #14171f; --blanc: #ffffff;
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 100%; height: 100%; overflow: hidden; background: var(--jaune); }
      body { font-family: "Nunito", sans-serif; color: var(--bleu); }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--jaune); }
      .scene { position: absolute; inset: 0; overflow: hidden; }
      .fill { position: absolute; inset: 0; }
      .yel { background: radial-gradient(ellipse 70% 60% at 50% 45%, #fff35a 0%, var(--jaune) 55%, #f3d600 100%); }
      .dark { background: radial-gradient(ellipse 80% 70% at 50% 40%, #151925 0%, var(--noir) 70%); }
      .grain { position: absolute; inset: 0; opacity: .05; background-image:
        repeating-radial-gradient(circle at 17% 23%, #fff 0 1px, transparent 1px 3px),
        repeating-radial-gradient(circle at 71% 63%, #fff 0 1px, transparent 1px 4px); }
      .H { font-family: "Montserrat", sans-serif; font-weight: 900; text-transform: uppercase; line-height: 1.02; letter-spacing: .01em; }
      .XB { font-family: "MontserratXB", sans-serif; font-weight: 800; }
      .bleu { color: var(--bleu); } .vert { color: var(--vert); } .blanc { color: #fff; } .or { color: var(--or); }
      .nb { white-space: nowrap; }
      .center { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
      .w { display: inline-block; }

      /* coins à bandes diagonales (bannière) */
      .corner { position: absolute; width: 520px; height: 520px; overflow: hidden; pointer-events: none; }
      .corner i { position: absolute; left: -40%; width: 180%; height: 34px; background: var(--vert); transform: rotate(-35deg); border-radius: 20px; }
      .corner.tl { left: 0; top: 0; } .corner.br { right: 0; bottom: 0; transform: rotate(180deg); }
      .corner i:nth-child(1) { top: 40px; } .corner i:nth-child(2) { top: 100px; height: 18px; background: #12b33a; } .corner i:nth-child(3) { top: 140px; height: 10px; }

      /* sous-titres incrustés */
      .sub { position: absolute; left: 50%; bottom: 34px; width: 1560px; margin-left: -780px; display: flex; justify-content: center; }
      .sub span { display: block; max-width: 1560px; text-align: center; font-weight: 800; font-size: 38px; line-height: 1.3; color: #fff;
        background: rgba(11,13,18,.84); border-radius: 18px; padding: 12px 30px; }
      .v .sub { bottom: 372px; width: 960px; margin-left: -480px; }
      .v .sub span { font-size: 44px; max-width: 960px; padding: 14px 30px; }

      .legal { position: absolute; left: 0; right: 0; bottom: 128px; text-align: center; font-weight: 700; font-size: 36px; color: var(--bleu); }
      .v .legal { bottom: 540px; font-size: 34px; padding: 0 70px; }

      /* rideau diagonal */
      #rideau { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
      #rpanel { position: absolute; top: -20%; height: 140%; transform-origin: 50% 50%;
        background: linear-gradient(90deg, #0b9a2f 0 12%, #fae504 12% 17%, #12b33a 17% 40%, #fae504 40% 44%, #0b9a2f 44% 83%, #fae504 83% 88%, #12b33a 88% 100%); }

      /* ── S1 ── */
      #s1icons { position: absolute; inset: 0; }
      .ico { position: absolute; width: 110px; height: 110px; }
      .ico svg { width: 100%; height: 100%; filter: drop-shadow(0 8px 10px rgba(0,0,0,.18)); }
      #s1txt { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; }
      #s1a, #s1b { font-size: 94px; text-align: center; }
      .v #s1a, .v #s1b { font-size: 84px; width: 1000px; }
      #s1tv { position: absolute; left: 50%; top: 50%; width: 160px; height: 160px; margin: -80px 0 0 -80px; }

      /* ── S2 ── */
      #s2glow { position: absolute; left: 50%; top: 50%; width: 1300px; height: 1300px; margin: -650px 0 0 -650px; border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,.95) 0%, rgba(255,250,190,.55) 25%, rgba(250,229,4,0) 62%); }
      .logoBox { position: absolute; width: 499px; height: 412px; }
      .logoBox img { position: absolute; inset: 0; width: 100%; height: 100%; }
      #s2logo { left: 50%; top: 50%; margin: -206px 0 0 -250px; }
      .pill { transform-origin: 48.6% 88.6%; }
      .part { position: absolute; width: 14px; height: 14px; border-radius: 50%; left: 50%; top: 50%; }

      /* ── S3 / S4 : monde application ── */
      #s3clip { position: absolute; inset: 0; }
      #nav { position: absolute; left: 60px; right: 60px; top: 42px; height: 92px; display: flex; align-items: center; gap: 18px; }
      #nav img { height: 84px; margin-right: 26px; }
      .np { height: 62px; padding: 0 30px; border-radius: 999px; background: var(--gris); color: #c9ccd6; font-weight: 800; font-size: 28px;
        display: flex; align-items: center; white-space: nowrap; }
      .np.on { background: var(--or); color: #111; }
      .v #nav { left: 40px; right: 40px; top: 260px; flex-wrap: wrap; height: auto; gap: 14px; justify-content: center; }
      .v #nav img { height: 90px; margin: 0 30px 10px; }
      .v .np { padding: 0 20px; font-size: 25px; height: 56px; }
      #hero { position: absolute; left: 80px; top: 175px; font-size: 118px; color: #fff; height: 130px; width: 1100px; }
      #hero b { position: absolute; left: 0; top: 0; white-space: nowrap; font-weight: 900; }
      .v #hero { left: 0; width: 1080px; top: 520px; text-align: center; font-size: 104px; }
      .v #hero b { left: 0; right: 0; }
      #count { position: absolute; right: 90px; top: 178px; display: flex; gap: 46px; }
      .v #count { right: auto; left: 0; width: 1080px; justify-content: center; top: 1290px; }
      .cnt .n { font-family: "Montserrat"; font-weight: 900; font-size: 74px; color: var(--or); line-height: 1; }
      .cnt .l { font-weight: 800; font-size: 26px; color: #fff; letter-spacing: .06em; text-transform: uppercase; }
      .row { position: absolute; left: 0; display: flex; gap: 24px; }
      #row1 { top: 335px; } #row2 { top: 670px; }
      .v #row1 { top: 680px; } .v #row2 { top: 1030px; }
      .card { position: relative; flex: none; width: 200px; height: 300px; border-radius: 22px; overflow: hidden; box-shadow: 0 16px 30px rgba(0,0,0,.5); }
      .card.wide { width: 320px; height: 180px; }
      .card .t { position: absolute; left: 14px; right: 14px; bottom: 12px; color: #fff; font-weight: 900; font-size: 22px; line-height: 1.05; text-shadow: 0 2px 8px rgba(0,0,0,.6); }
      .card .sh { position: absolute; border-radius: 50%; }
      .card .live { position: absolute; left: 12px; top: 12px; background: #e11d2e; color: #fff; font-weight: 900; font-size: 18px; padding: 4px 10px; border-radius: 8px; }
      .card .score { position: absolute; right: 12px; top: 12px; background: rgba(0,0,0,.6); color: #fff; font-weight: 900; font-size: 22px; padding: 4px 12px; border-radius: 8px; }
      .ring { position: absolute; left: 0; top: 0; border: 6px solid var(--menthe); border-radius: 28px; box-shadow: 0 0 26px rgba(46,204,113,.7); pointer-events: none; }

      #s4wrap { position: absolute; inset: 0; }
      #globe { position: absolute; left: 50%; top: 300px; width: 420px; height: 420px; margin-left: -210px; border-radius: 50%; overflow: hidden;
        background: radial-gradient(circle at 35% 30%, #4f6bff, var(--bleu) 60%, #101c6e); box-shadow: 0 0 80px rgba(46,204,113,.35); }
      .v #globe { top: 600px; }
      #land { position: absolute; top: 0; left: 0; width: 1260px; height: 420px; }
      .wave { position: absolute; left: 50%; top: 510px; width: 420px; height: 420px; margin: -210px 0 0 -210px; border-radius: 50%; border: 6px solid var(--menthe); }
      .v .wave { top: 810px; }
      #s4t { position: absolute; left: 0; right: 0; top: 140px; text-align: center; font-size: 84px; color: #fff; }
      .v #s4t { top: 290px; font-size: 76px; line-height: 1.15; }
      .v #s4t .dot { display: none; }
      .v #s4t .w { display: block; }
      #eq { position: absolute; left: 50%; top: 780px; width: 760px; margin-left: -380px; height: 80px; display: flex; gap: 10px; align-items: flex-end; }
      .v #eq { top: 1050px; width: 860px; margin-left: -430px; height: 120px; }
      #eq i { flex: 1; height: 100%; background: var(--or); border-radius: 6px; transform-origin: 50% 100%; }
      .side { position: absolute; top: 380px; width: 220px; height: 220px; border-radius: 50%; background: var(--gris); display: flex; align-items: center; justify-content: center; }
      .side svg { width: 130px; height: 130px; }
      #hp { left: 330px; } #mic { right: 330px; }
      .v .side { top: 1230px; width: 190px; height: 190px; } .v #hp { left: 150px; } .v #mic { right: 150px; }

      /* ── appareils ── */
      .phone { position: absolute; width: 250px; height: 500px; border-radius: 40px; background: #10131b; border: 10px solid #23283a; box-shadow: 0 30px 50px rgba(0,0,0,.28); overflow: hidden; }
      .phone .scr, .tab .scr, .tv .scr { position: absolute; inset: 0; overflow: hidden; }
      .phone .notch { position: absolute; left: 50%; top: 8px; width: 80px; height: 18px; margin-left: -40px; background: #23283a; border-radius: 10px; z-index: 3; }
      .tab { position: absolute; width: 400px; height: 300px; border-radius: 30px; background: #10131b; border: 12px solid #23283a; box-shadow: 0 30px 50px rgba(0,0,0,.28); overflow: hidden; }
      .tv { position: absolute; width: 720px; height: 420px; border-radius: 20px; background: #10131b; border: 14px solid #1b1f2c; box-shadow: 0 30px 60px rgba(0,0,0,.3); overflow: hidden; }
      .tvfoot { position: absolute; width: 180px; height: 26px; background: #1b1f2c; border-radius: 0 0 14px 14px; }
      .film { position: absolute; inset: 0; background: linear-gradient(135deg, #0b9a2f 0%, #1f34c8 45%, #2ecc71 70%, #fae504 100%); }
      .film::after { content: ""; position: absolute; left: 50%; top: 50%; width: 0; height: 0; margin: -28px 0 0 -16px;
        border-left: 48px solid rgba(255,255,255,.92); border-top: 28px solid transparent; border-bottom: 28px solid transparent; }
      .wavey { position: absolute; inset: -20% -60%; background: repeating-linear-gradient(115deg, rgba(255,255,255,.0) 0 60px, rgba(255,255,255,.18) 60px 120px); }

      /* ── S5 ── */
      #s5t1, #s5t2 { position: absolute; left: 0; right: 0; top: 70px; text-align: center; font-size: 92px; }
      .v #s5t1, .v #s5t2 { top: 300px; font-size: 84px; padding: 0 60px; }
      #ph5a { left: 560px; top: 270px; } #ph5b { left: 1110px; top: 270px; }
      .v #ph5a { left: 150px; top: 640px; } .v #ph5b { left: 680px; top: 640px; }
      .bars { position: absolute; right: 20px; top: 34px; display: flex; gap: 4px; align-items: flex-end; z-index: 4; }
      .bars i { width: 8px; background: rgba(255,255,255,.25); border-radius: 2px; }
      .bars i.on { background: #fff; }
      .spin { position: absolute; left: 50%; top: 50%; width: 90px; height: 90px; margin: -45px 0 0 -45px; border-radius: 50%;
        border: 10px solid rgba(255,255,255,.18); border-top-color: #fff; }
      .lab { position: absolute; left: 0; right: 0; bottom: 34px; text-align: center; font-weight: 800; font-size: 22px; color: #c9ccd6; }
      .tag5 { position: absolute; top: -70px; left: 0; right: 0; text-align: center; font-weight: 900; font-size: 30px; }
      #shield { position: absolute; left: 1310px; top: 210px; width: 230px; height: 96px; border-radius: 999px; background: var(--vert);
        color: #fff; display: flex; align-items: center; justify-content: center; gap: 10px; font-family: "Montserrat"; font-weight: 900; font-size: 36px;
        box-shadow: 0 12px 30px rgba(11,154,47,.45); }
      .v #shield { left: 760px; top: 590px; }
      .prog { position: absolute; left: 16px; right: 16px; bottom: 16px; height: 8px; background: rgba(255,255,255,.3); border-radius: 4px; overflow: hidden; z-index: 3; }
      .prog i { position: absolute; left: 0; top: 0; bottom: 0; width: 100%; background: var(--menthe); transform-origin: 0 50%; }

      /* ── S6 ── */
      #s6t { position: absolute; left: 0; right: 0; top: 80px; text-align: center; font-size: 96px; }
      .v #s6t { top: 290px; font-size: 92px; line-height: 1.1; }
      .v #s6t .w { display: block; }
      #box { position: absolute; left: 230px; top: 420px; width: 330px; height: 210px; }
      .v #box { left: 110px; top: 560px; }
      #box .b { position: absolute; left: 0; bottom: 0; width: 330px; height: 150px; border-radius: 30px; background: #fff; box-shadow: 0 20px 40px rgba(0,0,0,.2); }
      #box .ant { position: absolute; bottom: 140px; width: 16px; height: 90px; background: #fff; border-radius: 8px; }
      #box .led { position: absolute; bottom: 40px; width: 22px; height: 22px; border-radius: 50%; background: var(--menthe); box-shadow: 0 0 14px var(--menthe); }
      #box .nm { position: absolute; left: 0; right: 0; bottom: 70px; text-align: center; font-weight: 900; font-size: 30px; color: var(--bleu); }
      #net { position: absolute; left: 330px; top: 160px; width: 130px; height: 130px; }
      .v #net { left: 650px; top: 600px; }
      #plus6 { position: absolute; left: 620px; top: 440px; font-size: 130px; }
      #eq6 { position: absolute; left: 820px; top: 430px; font-size: 140px; }
      .v #plus6 { left: 480px; top: 590px; } .v #eq6 { left: 480px; top: 830px; }
      #tv6 { left: 1050px; top: 290px; width: 640px; height: 380px; }
      #tv6foot { left: 1280px; top: 670px; }
      .v #tv6 { left: 180px; top: 1030px; width: 720px; height: 380px; } .v #tv6foot { left: 450px; top: 1410px; }
      .wifi { position: absolute; left: 395px; top: 520px; width: 200px; height: 200px; margin: -100px 0 0 -100px; border-radius: 50%; border: 8px solid var(--vert); }
      .v .wifi { left: 275px; top: 665px; }
      #tvon6 { position: absolute; inset: 0; background: radial-gradient(circle at 50% 45%, #fff8a0, var(--jaune) 60%); display: flex; align-items: center; justify-content: center; }
      #tvon6 img { height: 82%; }

      /* ── S7 ── */
      #s7t { position: absolute; left: 0; right: 0; top: 70px; text-align: center; font-size: 84px; color: rgba(31,52,200,.25); }
      #s7t .w.on { color: var(--bleu); }
      .v #s7t { top: 300px; font-size: 80px; line-height: 1.2; } .v #s7t .w { display: block; } .v #s7t .dot { display: none; }
      #ph7 { left: 300px; top: 330px; width: 220px; height: 440px; }
      #tb7 { left: 590px; top: 430px; width: 420px; height: 310px; }
      #tv7 { left: 1080px; top: 260px; width: 700px; height: 420px; }
      #tv7foot { left: 1340px; top: 680px; }
      .v #ph7 { left: 130px; top: 1060px; width: 180px; height: 360px; }
      .v #tb7 { left: 380px; top: 1100px; width: 400px; height: 290px; }
      .v #tv7 { left: 90px; top: 610px; width: 900px; height: 400px; } .v #tv7foot { left: 450px; top: 1010px; }
      .scrOff { position: absolute; inset: 0; background: #0e1119; }
      #film7 { position: absolute; border-radius: 16px; overflow: hidden; }

      /* ── S8 ── */
      #s8a { position: absolute; left: 0; right: 0; top: 0; bottom: 120px; display: flex; align-items: center; justify-content: center; font-size: 130px; text-align: center; }
      .v #s8a { font-size: 112px; padding: 0 60px; bottom: 300px; }
      #ph8 { left: 835px; top: 160px; }
      .v #ph8 { left: 415px; top: 560px; }
      .dl { position: absolute; left: 22px; right: 22px; top: 250px; height: 82px; border-radius: 999px; background: var(--vert); color: #fff;
        display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: 900; font-size: 26px; }
      .dlic { position: absolute; left: 50%; top: 90px; width: 110px; height: 110px; margin-left: -55px; border-radius: 50%; border: 8px solid var(--menthe);
        display: flex; align-items: center; justify-content: center; }
      .bar8 { position: absolute; left: 22px; right: 22px; top: 360px; height: 18px; border-radius: 9px; background: rgba(255,255,255,.15); overflow: hidden; }
      .bar8 i { position: absolute; inset: 0; background: var(--menthe); transform-origin: 0 50%; }
      #check8 { position: absolute; left: 50%; top: 130px; width: 160px; height: 160px; margin-left: -80px; border-radius: 50%; background: var(--vert);
        display: flex; align-items: center; justify-content: center; box-shadow: 0 0 40px rgba(46,204,113,.7); z-index: 5; }
      #finger { position: absolute; left: 1010px; top: 470px; width: 70px; height: 70px; border-radius: 50%; background: rgba(255,255,255,.8); border: 6px solid var(--bleu); }
      .v #finger { left: 590px; top: 870px; }
      #dial { position: absolute; left: 560px; top: 150px; width: 470px; height: 470px; }
      .v #dial { left: 305px; top: 470px; }
      #dial .disc { position: absolute; inset: 40px; border-radius: 50%; background: var(--vert); box-shadow: 0 20px 50px rgba(11,154,47,.4);
        display: flex; align-items: center; justify-content: center; color: #fff; font-family: "Montserrat"; font-weight: 900; }
      #dial .disc .in { display: flex; align-items: baseline; margin-top: -40px; white-space: nowrap; }
      #dial .disc .n { font-size: 190px; line-height: 1; } #dial .disc .u { font-size: 76px; margin-left: 10px; }
      #dial svg { position: absolute; inset: 0; width: 100%; height: 100%; transform: rotate(-90deg); }
      #ruban { position: absolute; left: 520px; top: 500px; width: 550px; height: 100px; background: var(--vert); border: 6px solid #fff; border-radius: 14px;
        color: #fff; display: flex; align-items: center; justify-content: center; font-family: "Montserrat"; font-weight: 900; font-size: 64px; letter-spacing: .08em;
        box-shadow: 0 14px 30px rgba(0,0,0,.25); }
      .v #ruban { left: 265px; top: 820px; }
      #s8g { position: absolute; left: 515px; top: 668px; width: 560px; text-align: center; font-size: 76px; }
      #s8t { position: absolute; left: 1150px; top: 650px; width: 560px; text-align: center; font-size: 48px; }
      .v #s8g { left: 0; width: 1080px; top: 1000px; font-size: 92px; } .v #s8t { left: 0; width: 1080px; top: 1110px; font-size: 54px; }
      #ph8b { left: 1300px; top: 120px; width: 260px; height: 500px; }
      .v #ph8b { display: none; }
      .mini { position: absolute; inset: 0; background: var(--noir); padding: 40px 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; align-content: start; }
      .mini i { height: 120px; border-radius: 12px; }

      /* ── S9 ── */
      #q { position: absolute; left: 50%; top: 50%; width: 360px; height: 560px; margin: -330px 0 0 -180px; }
      #q svg { width: 100%; height: 100%; overflow: visible; }

      /* ── S10 / S11 ── */
      #s10wrap { position: absolute; inset: 0; }
      #seul { position: absolute; left: 0; right: 0; top: 70px; text-align: center; font-size: 60px; letter-spacing: .14em; }
      .v #seul { top: 290px; }
      #prices { position: absolute; left: 0; right: 0; top: 190px; display: flex; justify-content: center; align-items: center; gap: 60px; transform-origin: 50% 0; }
      .v #prices { flex-direction: column; top: 390px; gap: 75px; }
      .pc { position: relative; border-radius: 40px; color: #fff; text-align: center; box-shadow: 0 24px 50px rgba(0,0,0,.22); }
      #pc1 { width: 560px; height: 400px; background: linear-gradient(160deg, #3048e0, var(--bleu)); padding-top: 70px; }
      #pc2 { width: 650px; height: 470px; background: linear-gradient(160deg, #13b53b, var(--vert)); padding-top: 90px; }
      .v #pc1 { width: 760px; height: 360px; padding-top: 60px; } .v #pc2 { width: 860px; height: 440px; padding-top: 80px; }
      .pc .big { font-family: "Montserrat"; font-weight: 900; font-size: 150px; line-height: 1; white-space: nowrap; }
      #pc2 .big { font-size: 160px; }
      .pc .cur { font-family: "Montserrat"; font-weight: 900; font-size: 56px; letter-spacing: .04em; white-space: nowrap; }
      .pc .per { font-weight: 900; font-size: 50px; opacity: .95; }
      .crown { position: absolute; left: 50%; top: -38px; width: 360px; margin-left: -180px; height: 76px; border-radius: 999px; background: var(--jaune); color: var(--bleu);
        display: flex; align-items: center; justify-content: center; font-family: "Montserrat"; font-weight: 900; font-size: 34px; border: 6px solid #fff; }
      .b360 { position: absolute; width: 170px; height: 74px; border-radius: 999px; background: var(--vert); color: #fff; border: 5px solid #fff;
        display: flex; align-items: center; justify-content: center; font-family: "Montserrat"; font-weight: 900; font-size: 44px; box-shadow: 0 10px 24px rgba(0,0,0,.25); }
      #b10 { right: -50px; bottom: -30px; }
      .coin { position: absolute; width: 34px; height: 34px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #fff6a8, #f6be00 60%, #c99100); border: 3px solid #e8b000; }
      #confetti { position: absolute; inset: 0; pointer-events: none; }
      #s11 { position: absolute; left: 0; right: 0; top: 470px; }
      .v #s11 { top: 830px; }
      #eqn { text-align: center; font-family: "Montserrat"; font-weight: 900; font-size: 56px; color: var(--bleu); white-space: nowrap; }
      .v #eqn { font-size: 46px; }
      #eqn s { text-decoration-thickness: 6px; text-decoration-color: #e11d2e; opacity: .75; }
      #cal { margin: 26px auto 0; width: 1500px; display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; }
      .v #cal { width: 940px; grid-template-columns: repeat(6, 1fr); gap: 12px; }
      .m { height: 120px; border-radius: 18px; background: #fff; color: var(--bleu); font-weight: 900; font-size: 30px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; box-shadow: 0 8px 18px rgba(0,0,0,.12); position: relative; overflow: hidden; }
      .m::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 22px; background: var(--bleu); }
      .m.g::before { background: var(--vert); }
      .m .st { position: absolute; inset: 0; background: var(--vert); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 22px; letter-spacing: .04em; }
      #offerts { margin: 26px auto 0; width: max-content; padding: 10px 50px; border-radius: 16px; background: var(--vert); color: #fff; font-family: "Montserrat"; font-weight: 900; font-size: 74px;
        border: 6px solid #fff; box-shadow: 0 14px 30px rgba(0,0,0,.22); }
      .v #offerts { font-size: 70px; }

      /* ── S12 ── */
      #s12logo { left: 50%; top: 50%; margin: -206px 0 0 -250px; }

      /* ── S13 ── */
      #s13 { position: absolute; inset: 0; }
      #s13logo { left: 250px; top: 90px; }
      #s13line { position: absolute; left: 960px; top: 120px; width: 8px; height: 640px; background: var(--vert); border-radius: 4px; transform-origin: 50% 0; }
      #slog { position: absolute; left: 90px; top: 540px; width: 820px; text-align: center; }
      #slog div { font-size: 58px; line-height: 1.22; }
      #tv13 { left: 1040px; top: 200px; width: 700px; height: 420px; } #tv13foot { left: 1300px; top: 620px; }
      #tb13 { left: 1500px; top: 470px; width: 300px; height: 230px; } #ph13 { left: 1390px; top: 520px; width: 130px; height: 250px; border-radius: 24px; border-width: 7px; }
      .v #s13logo { left: 290px; top: 240px; } .v #s13line { left: 140px; top: 640px; width: 800px; height: 8px; transform-origin: 0 50%; }
      .v #slog { left: 0; width: 1080px; top: 1110px; } .v #slog div { font-size: 60px; }
      .v #tv13 { left: 150px; top: 690px; width: 600px; height: 330px; } .v #tv13foot { left: 360px; top: 1020px; }
      .v #tb13 { left: 680px; top: 830px; width: 280px; height: 210px; } .v #ph13 { left: 590px; top: 860px; width: 120px; height: 220px; }

      /* ── S14 ── */
      #s14logo { left: 50%; top: 40px; margin-left: -250px; transform-origin: 50% 0; }
      .v #s14logo { top: 260px; }
      #cta { position: absolute; left: 50%; top: 430px; width: 1240px; height: 150px; margin-left: -620px; white-space: nowrap; border-radius: 999px; background: linear-gradient(180deg, #13b53b, var(--vert));
        color: #fff; display: flex; align-items: center; justify-content: center; gap: 28px; font-family: "Montserrat"; font-weight: 900; font-size: 60px; border: 8px solid #fff;
        box-shadow: 0 22px 50px rgba(11,154,47,.45); }
      .v #cta { top: 780px; width: 940px; margin-left: -470px; height: 210px; font-size: 58px; line-height: 1.05; text-align: center; white-space: normal; }
      #arrow { width: 70px; height: 80px; flex: none; }
      #pill14 { position: absolute; left: 50%; top: 615px; width: 460px; margin-left: -230px; height: 72px; border-radius: 999px; background: #fff; color: var(--vert);
        display: flex; align-items: center; justify-content: center; font-family: "Montserrat"; font-weight: 900; font-size: 38px; }
      .v #pill14 { top: 1030px; }
      #dl14 { position: absolute; left: 0; right: 0; top: 715px; text-align: center; font-weight: 800; font-size: 34px; color: var(--bleu); }
      .v #dl14 { top: 1130px; padding: 0 80px; }
      #b14 { left: 50%; top: 382px; margin-left: 140px; }
      .v #b14 { top: 640px; margin-left: 150px; }
      #legal14 { bottom: 128px; font-size: 32px; }
      .v #legal14 { bottom: 540px; }
      #outro { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
      #outro .logoBox { position: relative; }

      /* ═════════ v11 : nouveau style du storyboard (bleu nuit, néon vert, étiquettes jaunes) ═════════ */
      :root { --nuit: #06103f; --roi: #1238c9; --neon: #3dff6e; --tag: #ffe600; --rouge: #e3132c; }
      html, body, #root { background: var(--nuit); }
      .yel { background: radial-gradient(ellipse 75% 65% at 50% 42%, #2a5ff2 0%, #1236b8 42%, #08185e 78%, #050c36 100%); }
      .dark { background: radial-gradient(ellipse 80% 70% at 50% 40%, #142a86 0%, #08154f 55%, #040a2c 100%); }
      .jaune .fill.yel { background: radial-gradient(ellipse 70% 60% at 50% 45%, #fff35a 0%, #fae504 55%, #f3d600 100%); }
      .corner { display: none; }
      .bleu { color: #ffffff; } .vert { color: var(--tag); }
      .jaune .bleu { color: var(--bleu); } .jaune .vert { color: var(--vert); }
      .H { font-style: italic; }
      .tag { display: inline-block; background: var(--tag); color: #0a1a6b; border-radius: 14px; padding: 4px 28px 8px; transform: rotate(-2deg); box-shadow: 0 10px 26px rgba(0,0,0,.35); }
      .sw { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
      .sw svg { position: absolute; left: -10%; width: 120%; bottom: -4%; height: 46%; }
      .glowtxt { text-shadow: 0 4px 0 rgba(0,0,0,.25), 0 0 30px rgba(0,0,0,.35); }
      .pcard { position: absolute; border-radius: 30px; overflow: hidden; background: #0a1a6b;
        box-shadow: 0 0 0 4px rgba(255,255,255,.9), 0 0 50px rgba(61,255,110,.45), 0 30px 60px rgba(0,0,0,.5); }
      .pcard img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .ico { border-radius: 50%; background: #fff; padding: 14px; box-shadow: 0 0 0 4px rgba(61,255,110,.85), 0 0 24px rgba(61,255,110,.6); }
      .ico svg { filter: none; }
      .legal, #dl14 { color: #fff; }
      #rpanel { background: linear-gradient(90deg, #3dff6e 0 9%, #ffe600 9% 12%, #1238c9 12% 88%, #ffe600 88% 91%, #3dff6e 91% 100%); }
      /* S1 */
      #p1 { left: 50%; top: 60px; width: 1180px; height: 760px; margin-left: -590px; }
      #p1 .ov { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(6,16,63,0) 35%, rgba(6,16,63,.85) 100%); }
      #s1txt { justify-content: flex-end; padding-bottom: 290px; gap: 14px; }
      #s1a { color: #fff; font-size: 92px; } #s1b { font-size: 70px; }
      .v #p1 { top: 330px; width: 980px; height: 900px; margin-left: -490px; }
      .v #s1txt { padding-bottom: 560px; } .v #s1a { font-size: 80px; } .v #s1b { font-size: 58px; width: auto; }
      /* S2 */
      #s2logo img { filter: drop-shadow(0 0 18px rgba(255,255,255,.35)); }
      /* S3 : défilé des univers */
      #nav, #hero, #row1, #row2, #ring3 { display: none; }
      .c3 { left: 50%; top: 90px; width: 1200px; height: 675px; margin-left: -600px; }
      .v .c3 { top: 470px; width: 980px; height: 620px; margin-left: -490px; }
      #c3films img { object-position: 50% 85%; }
      .codec { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; padding-bottom: 50px; }
      .codec .tt { font-family: "Montserrat"; font-weight: 900; font-style: italic; font-size: 92px; color: #fff; line-height: 1; text-shadow: 0 6px 0 rgba(0,0,0,.25); }
      .codec .tag { font-family: "Montserrat"; font-weight: 900; font-style: italic; font-size: 44px; margin-top: 8px; }
      .v .codec .tt { font-size: 78px; } .v .codec .tag { font-size: 38px; }
      .mosa { position: absolute; left: 50px; right: 50px; top: 46px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
      .mosa div { height: 118px; border-radius: 16px; display: flex; align-items: center; justify-content: center; color: #fff; font-family: "Montserrat"; font-weight: 900; font-size: 38px; position: relative; box-shadow: 0 8px 18px rgba(0,0,0,.35); }
      .v .mosa div { height: 104px; font-size: 32px; }
      .mosa div b { position: absolute; left: 10px; top: 8px; background: var(--rouge); font-size: 15px; padding: 2px 8px; border-radius: 6px; font-family: "Nunito"; }
      #count { right: auto; left: 0; width: 100%; justify-content: center; top: 800px; gap: 40px; }
      .v #count { top: 1130px; }
      .cnt { background: var(--tag); border-radius: 16px; padding: 8px 26px; transform: rotate(-2deg); display: flex; align-items: baseline; gap: 14px; }
      .cnt .n { color: #0a1a6b; font-size: 60px; } .cnt .l { color: #0a1a6b; font-size: 28px; }
      /* S4 */
      #globe, .wave { display: none; }
      #p4 { left: 50%; top: 255px; width: 900px; height: 489px; margin-left: -450px; }
      .v #p4 { top: 600px; width: 980px; height: 532px; margin-left: -490px; }
      #eq { top: 785px; } .v #eq { top: 1160px; height: 100px; }
      #hp { left: 140px; } #mic { right: 140px; } .side { background: rgba(255,255,255,.95); box-shadow: 0 0 0 5px rgba(61,255,110,.8), 0 0 30px rgba(61,255,110,.6); }
      .v .side { display: none; }
      #net { border-radius: 50%; background: #fff; padding: 12px; box-shadow: 0 0 0 4px rgba(61,255,110,.85), 0 0 24px rgba(61,255,110,.6); }
      /* S7 */
      #s7t, #tv7, #tv7foot, #tb7, #ph7, #film7 { display: none; }
      #p7 { left: 50%; top: 110px; width: 1300px; height: 638px; margin-left: -650px; }
      .v #p7 { top: 620px; width: 1000px; height: 491px; margin-left: -500px; }
      /* S8 */
      #ruban { background: var(--rouge); }
      /* S12 */
      #s12logo { display: none; }
      #s12q { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; text-align: center; padding-bottom: 80px; }
      #s12q .a { font-family: "Montserrat"; font-weight: 900; font-style: italic; font-size: 104px; color: #fff; }
      #s12q svg { width: 760px; height: 60px; }
      .v #s12q .a { font-size: 92px; padding: 0 60px; }
      /* S13 */
      #tv13, #tv13foot, #tb13, #ph13 { display: none; }
      #s13line { background: var(--neon); box-shadow: 0 0 20px var(--neon); }
      #cats { position: absolute; left: 1030px; top: 170px; width: 800px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px 20px; }
      .v #cats { left: 90px; top: 690px; width: 900px; gap: 26px 20px; }
      .cat { display: flex; flex-direction: column; align-items: center; gap: 12px; }
      .cat .c { width: 170px; height: 170px; border-radius: 50%; background: #fff; border: 6px solid var(--neon); box-shadow: 0 0 30px rgba(61,255,110,.55), inset 0 0 26px rgba(61,255,110,.3);
        display: flex; align-items: center; justify-content: center; }
      .v .cat .c { width: 130px; height: 130px; }
      .cat .c svg { width: 60%; height: 60%; }
      .cat span { font-family: "Montserrat"; font-weight: 900; font-style: italic; font-size: 36px; color: #fff; }
      .v .cat span { font-size: 32px; }
      .v #slog { top: 1120px; }
      /* S14 */
      #cta { background: linear-gradient(180deg, #33e85a, #0b8f2a); border: 6px solid #b9ffb0; box-shadow: 0 0 50px rgba(61,255,110,.75), 0 20px 50px rgba(0,0,0,.4); font-style: italic; }
      #pill14 { color: #0a1a6b; background: var(--tag); }
      #tag14 { position: absolute; left: 0; right: 0; top: 760px; text-align: center; }
      #tag14 span { font-family: "Montserrat"; font-weight: 900; font-style: italic; font-size: 64px; }
      .v #tag14 { top: 1080px; } .v #tag14 span { font-size: 56px; }
    </style>
  </head>
  <body>
    <svg width="0" height="0" style="position:absolute">
      <defs>
        <symbol id="i-clap" viewBox="0 0 64 64"><rect x="8" y="26" width="48" height="30" rx="6" fill="#1f34c8"/><path d="M8 18 L54 10 L56 20 L10 28 Z" fill="#0b9a2f"/><path d="M18 16 l6 10 M30 14 l6 10 M42 12 l6 10" stroke="#fff" stroke-width="4"/></symbol>
        <symbol id="i-ball" viewBox="0 0 64 64"><circle cx="32" cy="32" r="24" fill="#fff" stroke="#1f34c8" stroke-width="5"/><path d="M32 22 l9 7 -3 11 h-12 l-3 -11 z" fill="#1f34c8"/></symbol>
        <symbol id="i-head" viewBox="0 0 64 64"><path d="M12 38 V32 a20 20 0 0 1 40 0 V38" fill="none" stroke="#1f34c8" stroke-width="6"/><rect x="8" y="34" width="14" height="22" rx="6" fill="#0b9a2f"/><rect x="42" y="34" width="14" height="22" rx="6" fill="#0b9a2f"/></symbol>
        <symbol id="i-mic" viewBox="0 0 64 64"><rect x="22" y="6" width="20" height="32" rx="10" fill="#1f34c8"/><path d="M14 30 a18 18 0 0 0 36 0" fill="none" stroke="#0b9a2f" stroke-width="5"/><path d="M32 48 V58 M22 58 H42" stroke="#0b9a2f" stroke-width="5"/></symbol>
        <symbol id="i-radio" viewBox="0 0 64 64"><path d="M16 22 L44 8" stroke="#1f34c8" stroke-width="4"/><rect x="6" y="20" width="52" height="36" rx="8" fill="#1f34c8"/><circle cx="22" cy="38" r="10" fill="#0b9a2f"/><rect x="38" y="30" width="14" height="5" rx="2" fill="#fff"/><rect x="38" y="40" width="14" height="5" rx="2" fill="#fff"/></symbol>
        <symbol id="i-globe" viewBox="0 0 64 64"><circle cx="32" cy="32" r="24" fill="#1f34c8"/><path d="M8 32 H56 M32 8 C18 20 18 44 32 56 C46 44 46 20 32 8" fill="none" stroke="#fff" stroke-width="3"/><path d="M18 20 q6 4 10 0 q4 8 -4 12 q-8 0 -6 -12z M38 34 q8 -2 10 6 q-6 8 -10 4z" fill="#0b9a2f"/></symbol>
        <symbol id="i-cam" viewBox="0 0 64 64"><rect x="6" y="18" width="38" height="30" rx="6" fill="#1f34c8"/><path d="M44 28 L58 20 V46 L44 38 Z" fill="#0b9a2f"/><circle cx="18" cy="14" r="6" fill="#0b9a2f"/><circle cx="32" cy="14" r="6" fill="#0b9a2f"/></symbol>
        <symbol id="i-pad" viewBox="0 0 64 64"><path d="M14 20 H50 a10 10 0 0 1 10 12 l-3 14 a7 7 0 0 1 -12 3 l-5 -7 H24 l-5 7 a7 7 0 0 1 -12 -3 l-3 -14 A10 10 0 0 1 14 20z" fill="#1f34c8"/><path d="M20 28 v10 M15 33 h10" stroke="#fff" stroke-width="4"/><circle cx="44" cy="30" r="3.5" fill="#0b9a2f"/><circle cx="50" cy="36" r="3.5" fill="#0b9a2f"/></symbol>
        <symbol id="i-note" viewBox="0 0 64 64"><path d="M24 12 L52 6 V44" fill="none" stroke="#1f34c8" stroke-width="6"/><path d="M24 12 V50" stroke="#1f34c8" stroke-width="6"/><circle cx="18" cy="50" r="9" fill="#0b9a2f"/><circle cx="46" cy="44" r="9" fill="#0b9a2f"/></symbol>
        <symbol id="i-tv" viewBox="0 0 64 64"><path d="M22 8 L32 18 L42 8" fill="none" stroke="#1f34c8" stroke-width="4"/><rect x="6" y="18" width="52" height="36" rx="8" fill="#1f34c8"/><rect x="12" y="24" width="40" height="24" rx="4" fill="#0b9a2f"/><path d="M28 30 L38 36 L28 42 Z" fill="#fff"/></symbol>
        <symbol id="i-eye" viewBox="0 0 64 64"><path d="M4 32 C16 14 48 14 60 32 C48 50 16 50 4 32Z" fill="#fff" stroke="#1f34c8" stroke-width="4"/><circle cx="32" cy="32" r="12" fill="#1f34c8"/><circle cx="36" cy="27" r="4" fill="#fff"/><path d="M8 18 L18 24 M56 18 L46 24" stroke="#1f34c8" stroke-width="4"/></symbol>
        <symbol id="i-pop" viewBox="0 0 64 64"><path d="M14 24 H50 L44 58 H20 Z" fill="#fff" stroke="#1f34c8" stroke-width="4"/><path d="M24 26 L26 56 M32 26 V56 M40 26 L38 56" stroke="#0b9a2f" stroke-width="4"/><circle cx="20" cy="20" r="7" fill="#fff8c0"/><circle cx="32" cy="16" r="8" fill="#fff8c0"/><circle cx="44" cy="20" r="7" fill="#fff8c0"/></symbol>
        <symbol id="i-play" viewBox="0 0 64 64"><circle cx="32" cy="32" r="26" fill="#0b9a2f"/><path d="M26 20 L46 32 L26 44 Z" fill="#fff"/></symbol>
        <symbol id="i-star" viewBox="0 0 64 64"><path d="M32 6 l7.6 16 17.4 2.4 -12.6 12.2 3 17.4 -15.4 -8.4 -15.4 8.4 3 -17.4 -12.6 -12.2 17.4 -2.4z" fill="#0b9a2f"/></symbol>
        <symbol id="i-check" viewBox="0 0 64 64"><path d="M14 33 L27 46 L51 19" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></symbol>
        <symbol id="i-dl" viewBox="0 0 64 64"><path d="M32 8 V40 M18 28 L32 42 L46 28" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 52 H52" stroke="currentColor" stroke-width="8" stroke-linecap="round"/></symbol>
      </defs>
    </svg>

    <div id="root" data-composition-id="main" data-start="0" data-duration="60" data-width="__W__" data-height="__H__">

      <!-- S1 · accroche -->
      <div id="sc1" class="scene clip" data-start="0" data-duration="3.75" data-track-index="0">
        <div class="fill yel"></div>
        <div class="pcard" id="p1"><img src="assets/p-family.jpg" alt="" /><div class="ov"></div></div>
        <div id="s1icons"></div>
        <div id="s1txt">
          <div id="s1a" class="H bleu glowtxt"><span class="w">Tout</span> <span class="w">ton</span> <span class="w">divertissement</span></div>
          <div id="s1b" class="H tag"><span class="w">Une</span> <span class="w">seule</span> <span class="w">application</span></div>
        </div>
        <img id="s1tv" src="assets/icone-tele.png" alt="" />
      </div>

      <!-- S2 · logo -->
      <div id="sc2" class="scene clip" data-start="3.55" data-duration="2.85" data-track-index="1">
        <div class="fill yel"></div>
        <div class="corner tl" id="c2a"><i></i><i></i><i></i></div><div class="corner br" id="c2b"><i></i><i></i><i></i></div>
        <div id="s2glow"></div>
        <div id="s2parts"></div>
        <div id="s2logo" class="logoBox">
          <img id="s2top" src="assets/logo-top-w.png" alt="" />
          <img id="s2lines" src="assets/logo-lines.png" alt="" />
          <img id="s2pill" class="pill" src="assets/logo-pill.png" alt="" />
        </div>
      </div>

      <!-- S3 · catalogue (monde application) -->
      <div id="sc3" class="scene clip" data-start="6.0" data-duration="6.25" data-track-index="2">
        <div id="s3clip">
          <div class="fill dark"></div><div class="grain"></div>
          <div id="nav">
            <img src="assets/logo.png" alt="" />
            <div class="np" id="np0">Home</div><div class="np" id="np1">Movies</div><div class="np" id="np2">Series</div>
            <div class="np" id="np3">Docs &amp; Live</div><div class="np" id="np4">Shorts</div>
          </div>
          <div id="hero" class="H">
            <b id="h1">Films</b><b id="h2">Séries</b><b id="h3">Mangas</b><b id="h4">Sport</b><b id="h5">Docs</b><b id="h6" class="nb">En direct</b>
          </div>
          <div id="count">
            <div class="cnt" id="cn1"><div class="n"><span id="cv1">0</span>+</div><div class="l">films &amp; séries</div></div>
            <div class="cnt" id="cn2"><div class="n"><span id="cv2">0</span>+</div><div class="l">chaînes</div></div>
          </div>
          <div class="pcard c3" id="c3tv"><img src="assets/p-tv.jpg" alt="" /></div>
          <div class="pcard c3" id="c3films"><img src="assets/p-films.jpg" alt="" /></div>
          <div class="pcard c3" id="c3manga" style="background:linear-gradient(135deg,#ff4e9b,#7b2ff7 60%,#2a0b6b)">
            <svg viewBox="0 0 400 200" style="position:absolute;left:50%;top:40px;width:520px;height:260px;margin-left:-260px;opacity:.95"><use href="#i-eye" x="40" y="10" width="150" height="150"/><use href="#i-eye" x="210" y="10" width="150" height="150"/></svg>
            <div class="codec"><div class="tt">Mangas</div><div class="tag">&amp; animés</div></div></div>
          <div class="pcard c3" id="c3sport"><img src="assets/p-sport.jpg" alt="" /></div>
          <div class="pcard c3" id="c3docs" style="background:linear-gradient(180deg,#1cb5e0 0%,#0f4c75 55%,#0b2a3c 100%)">
            <div style="position:absolute;left:8%;bottom:28%;width:0;height:0;border-left:220px solid transparent;border-right:220px solid transparent;border-bottom:300px solid rgba(255,255,255,.22)"></div>
            <div style="position:absolute;right:10%;bottom:28%;width:0;height:0;border-left:160px solid transparent;border-right:160px solid transparent;border-bottom:220px solid rgba(255,255,255,.32)"></div>
            <div style="position:absolute;right:16%;top:12%;width:110px;height:110px;border-radius:50%;background:#ffe600;box-shadow:0 0 60px #ffe600"></div>
            <div class="codec"><div class="tt">Documentaires</div><div class="tag">du monde entier</div></div></div>
          <div class="pcard c3" id="c3live" style="background:linear-gradient(180deg,#0d2a9a,#06103f)">
            <div class="mosa">
              <div style="background:#e3132c"><b>● DIRECT</b>AFRIK 24</div><div style="background:#7b2ff7"><b>● DIRECT</b>CINÉ MAX</div><div style="background:#0b9a2f"><b>● DIRECT</b>SPORT+</div>
              <div style="background:#f7971e"><b>● DIRECT</b>KIDS TV</div><div style="background:#1cb5e0"><b>● DIRECT</b>INFO 360</div><div style="background:#ec008c"><b>● DIRECT</b>MUSIK</div>
            </div>
            <div class="codec"><div class="tt">TV en direct</div><div class="tag">des centaines de chaînes</div></div></div>
          <div id="row1" class="row"></div>
          <div id="row2" class="row"></div>
          <div id="ring3" class="ring"></div>
        </div>
      </div>

      <!-- S4 · radios / podcasts / musique -->
      <div id="sc4" class="scene clip" data-start="12.0" data-duration="4.2" data-track-index="3">
        <div class="fill dark"></div><div class="grain"></div>
        <div id="s4wrap">
          <div id="s4t" class="H"><span class="w" id="s4w1">Radios</span><span class="dot or"> · </span><span class="w" id="s4w2">Podcasts</span><span class="dot or"> · </span><span class="w or" id="s4w3">Musique</span></div>
          <div class="wave" id="wv1"></div><div class="wave" id="wv2"></div><div class="wave" id="wv3"></div>
          <div id="globe"><div id="land"></div></div>
          <div class="pcard" id="p4"><img src="assets/p-music.jpg" alt="" /></div>
          <div class="side" id="hp"><svg><use href="#i-head"/></svg></div>
          <div class="side" id="mic"><svg><use href="#i-mic"/></svg></div>
          <div id="eq"></div>
        </div>
      </div>

      <!-- S5 · streaming optimisé -->
      <div id="sc5" class="scene clip" data-start="15.8" data-duration="6.9" data-track-index="4">
        <div class="fill yel"></div>
        <div id="s5t1" class="H bleu">Connexion limitée ?</div>
        <div id="s5t2" class="H vert">Streaming stable ✓</div>
        <div class="phone" id="ph5a"><div class="notch"></div>
          <div class="scr" style="background:#1a1d27"><div class="bars"><i class="on" style="height:8px"></i><i style="height:14px"></i><i style="height:20px"></i><i style="height:26px"></i></div>
            <div class="spin" id="spin5"></div><div class="lab">Chargement…</div></div>
          </div>
        <div class="phone" id="ph5b"><div class="notch"></div>
          <div class="scr"><div class="film"><div class="wavey" id="wavey5"></div></div>
            <div class="bars"><i class="on" style="height:8px"></i><i style="height:14px"></i><i style="height:20px"></i><i style="height:26px"></i></div>
            <div class="prog"><i id="prog5"></i></div></div>
        </div>
        <div id="shield"><svg width="44" height="44"><use href="#i-check"/></svg>STABLE</div>
      </div>

      <!-- S6 · box Wi-Fi + Internet -->
      <div id="sc6" class="scene clip" data-start="22.4" data-duration="6.6" data-track-index="5">
        <div class="fill yel"></div>
        <div id="s6t" class="H bleu"><span class="w" id="s6w1">Box Wi-Fi</span> <span class="w vert" id="s6w2">+ Internet</span></div>
        <div class="wifi" id="wf1"></div><div class="wifi" id="wf2"></div><div class="wifi" id="wf3"></div>
        <div id="box"><div class="ant" style="left:60px;transform:rotate(-12deg)"></div><div class="ant" style="right:60px;transform:rotate(12deg)"></div>
          <div class="b"></div><div class="nm">BOX WI-FI</div><div class="led" style="left:110px"></div><div class="led" style="left:154px"></div><div class="led" style="left:198px"></div></div>
        <svg id="net"><use href="#i-globe"/></svg>
        <div id="plus6" class="H vert">+</div>
        <div id="eq6" class="H bleu">=</div>
        <div class="tv" id="tv6"><div class="scrOff"></div><div id="tvon6"><img src="assets/logo.png" alt="" /></div></div>
        <div class="tvfoot" id="tv6foot"></div>
      </div>

      <!-- S7 · tous tes écrans -->
      <div id="sc7" class="scene clip" data-start="28.7" data-duration="3.0" data-track-index="6">
        <div class="fill yel"></div>
        <div id="s7t" class="H"><span class="w" id="s7w1">Téléphone</span><span class="dot"> · </span><span class="w" id="s7w2">Tablette</span><span class="dot"> · </span><span class="w" id="s7w3">Télé</span></div>
        <div class="tv" id="tv7"><div class="scrOff"></div></div><div class="tvfoot" id="tv7foot"></div>
        <div class="tab" id="tb7"><div class="scrOff"></div></div>
        <div class="phone" id="ph7"><div class="scrOff"></div></div>
        <div id="film7"><div class="film"><div class="wavey" id="wavey7"></div></div></div>
        <div class="pcard" id="p7"><img src="assets/p-devices.jpg" alt="" /></div>
      </div>

      <!-- S8 · essai gratuit 24 h -->
      <div id="sc8" class="scene clip" data-start="31.4" data-duration="7.2" data-track-index="7">
        <div class="fill yel"></div>
        <div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>
        <div id="s8a" class="H bleu"><div id="s8aIn"><div>Et ce n'est</div><div>pas tout !</div></div></div>
        <div class="phone" id="ph8"><div class="notch"></div>
          <div class="scr" style="background:var(--noir)">
            <div class="dlic"><svg width="64" height="64" style="color:#2ecc71"><use href="#i-dl"/></svg></div>
            <div class="dl" id="dlbtn">Télécharger</div>
            <div class="bar8"><i id="bar8"></i></div>
          </div>
          <div id="check8"><svg width="110" height="110"><use href="#i-check"/></svg></div>
        </div>
        <div id="finger"></div>
        <div id="dial">
          <svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="46" fill="none" stroke="rgba(11,154,47,.18)" stroke-width="5"/>
            <circle id="dialRing" cx="50" cy="50" r="46" fill="none" stroke="#2ecc71" stroke-width="5" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/></svg>
          <div class="disc"><div class="in"><span class="n">24</span><span class="u">H</span></div></div>
        </div>
        <div id="ruban">GRATUIT</div>
        <div id="s8g" class="H vert">Gratuites</div>
        <div id="s8t" class="H bleu">Pour tester l'appli</div>
        <div class="phone" id="ph8b"><div class="notch"></div><div class="mini" id="mini8"></div><div class="ring" id="ring8" style="width:112px;height:132px;border-radius:16px;border-width:5px"></div></div>
        <div class="legal" id="legal8">Essai gratuit de 24 h dès le téléchargement — [conditions à fournir]</div>
      </div>

      <!-- S9 · suspense du prix -->
      <div id="sc9" class="scene clip" data-start="38.25" data-duration="2.25" data-track-index="8">
        <div class="fill yel"></div>
        <div id="q"><svg viewBox="0 0 360 560">
          <path id="qhook" d="M70 150 C70 60 140 30 190 30 C260 30 300 80 300 140 C300 210 240 230 205 265 C185 285 180 305 180 345" fill="none" stroke="#ffe600" stroke-width="64" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/>
          <circle id="qdot" cx="180" cy="470" r="46" fill="#ffe600"/></svg></div>
        <div id="qdisc" style="position:absolute;left:50%;top:50%;width:390px;height:390px;margin:-195px 0 0 -195px;border-radius:50%;background:#0b9a2f"></div>
      </div>

      <!-- S10 + S11 · les prix + l'année offerte -->
      <div id="sc10" class="scene clip jaune" data-start="40.2" data-duration="6.6" data-track-index="9">
        <div class="fill yel"></div>
        <div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>
        <div id="confetti"></div>
        <div id="s10wrap">
          <div id="seul" class="H bleu">Seulement</div>
          <div id="prices">
            <div class="pc" id="pc1"><div class="big"><span id="pv1">0</span></div><div class="cur">FCFA</div><div class="per">/ mois</div></div>
            <div class="pc" id="pc2"><div class="crown">MEILLEUR PRIX</div><div class="big"><span id="pv2">0</span></div><div class="cur">FCFA</div><div class="per">/ an</div>
              <div class="b360" id="b10">360</div></div>
          </div>
          <div id="s11">
            <div id="eqn">12 × 1 000 = <s>12 000</s> → 10 000 FCFA</div>
            <div id="cal"></div>
            <div id="offerts">2 MOIS OFFERTS</div>
          </div>
        </div>
      </div>

      <!-- S12 · pourquoi chercher ailleurs ? -->
      <div id="sc12" class="scene clip" data-start="46.6" data-duration="2.3" data-track-index="10">
        <div class="fill yel"></div>
        <div id="s12icons"></div>
        <div id="s12logo" class="logoBox"><img src="assets/logo.png" alt="" /></div>
        <div id="s12q"><div class="a" id="s12a">Pourquoi chercher ailleurs ?</div>
          <svg viewBox="0 0 760 60" id="s12u"><path id="s12p" d="M20 44 C220 8 520 4 740 30" fill="none" stroke="#ffe600" stroke-width="12" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/></svg></div>
      </div>

      <!-- S13 · message final -->
      <div id="sc13" class="scene clip" data-start="48.5" data-duration="5.9" data-track-index="11">
        <div class="fill yel"></div>
        <div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>
        <div id="s13">
          <div id="s13logo" class="logoBox"><img src="assets/logo-top-w.png" alt="" /><img src="assets/logo-lines.png" alt="" /><img class="pill" src="assets/logo-pill.png" alt="" /></div>
          <div id="s13line"></div>
          <div id="cats">
            <div class="cat"><div class="c"><svg><use href="#i-clap"/></svg></div><span>Films</span></div>
            <div class="cat"><div class="c"><svg><use href="#i-tv"/></svg></div><span>Séries</span></div>
            <div class="cat"><div class="c"><svg><use href="#i-ball"/></svg></div><span>Sport</span></div>
            <div class="cat"><div class="c"><svg><use href="#i-eye"/></svg></div><span>Mangas</span></div>
            <div class="cat"><div class="c"><svg><use href="#i-note"/></svg></div><span>Musique</span></div>
            <div class="cat"><div class="c"><svg><use href="#i-radio"/></svg></div><span>Radios</span></div>
          </div>
          <div id="slog"><div class="H bleu" id="sl1">Tout ton divertissement</div><div class="H vert" id="sl2">Une seule application</div><div class="H bleu" id="sl3">Un petit prix</div></div>
          <div class="tv" id="tv13"><div class="film"><div class="wavey" id="wavey13"></div></div></div><div class="tvfoot" id="tv13foot"></div>
          <div class="tab" id="tb13"><div class="film"></div></div>
          <div class="phone" id="ph13"><div class="film"></div></div>
        </div>
      </div>

      <!-- S14 · appel à l'action -->
      <div id="sc14" class="scene clip" data-start="54.0" data-duration="6.0" data-track-index="12">
        <div class="fill yel"></div>
        <div class="corner tl"><i></i><i></i><i></i></div><div class="corner br"><i></i><i></i><i></i></div>
        <div id="s14all">
          <div id="s14logo" class="logoBox"><img src="assets/logo-top-w.png" alt="" /><img src="assets/logo-lines.png" alt="" /><img id="s14pill" class="pill" src="assets/logo-pill.png" alt="" /></div>
          <div id="cta"><svg id="arrow" viewBox="0 0 64 64" style="color:#fff"><use href="#i-dl"/></svg><span>TÉLÉCHARGE MAINTENANT !</span></div>
          <div id="pill14">24 H GRATUITES</div>
          <div id="tag14"><span class="tag">Le divertissement sans limite !</span></div>
          <div id="dl14">[Lien de téléchargement / QR code / WhatsApp — à fournir]</div>
          <div class="legal" id="legal14">Conditions d'abonnement et de l'essai gratuit : [à fournir] · Prix en FCFA</div>
        </div>
      </div>

      <!-- rideau diagonal (transitions entre grandes séquences) -->
      <div id="rideau" class="clip" data-start="0" data-duration="60" data-track-index="13"><div id="rpanel"></div></div>

      <!-- sous-titres (calés sur la voix enregistrée) -->
      __SUBS__
    </div>

    <script>
      const ROOT = document.getElementById("root");
      const W = +ROOT.dataset.width, H = +ROOT.dataset.height, V = H > W;
      // PRNG déterministe (aucun Math.random)
      let seed = 360360;
      const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
      const $ = (s) => document.querySelector(s);
      const mk = (tag, cls, parent, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html) e.innerHTML = html; parent.appendChild(e); return e; };
      const ICONS = ["clap","ball","head","mic","radio","globe","cam","pad","note","tv","eye","pop","play","star"];

      // ── S1 : icônes éparpillées (hors de la bande de texte)
      const s1 = $("#s1icons"), s1list = [];
      let k = 0, tries = 0;
      while (s1list.length < 36 && tries < 3000) {
        tries++;
        const x = rnd() * (W - 140) + 20, y = rnd() * (H - 140) + 20;
        const cx = x + 55, cy = y + 55;
        const bandH = V ? 690 : 470;
        if (Math.abs(cy - H / 2) < bandH && Math.abs(cx - W / 2) < (V ? 700 : 690)) continue;
        if (s1list.some((o) => Math.hypot(o.x - x, o.y - y) < 120)) continue;
        const d = mk("div", "ico", s1, `<svg><use href="#i-${ICONS[k++ % ICONS.length]}"/></svg>`);
        d.style.left = x + "px"; d.style.top = y + "px";
        const sc = 0.7 + rnd() * 0.6; d.style.width = d.style.height = 110 * sc + "px";
        s1list.push({ el: d, x, y, r: (rnd() - .5) * 50 });
      }
      // ── S2 : particules
      const s2p = $("#s2parts"), parts = [];
      for (let i = 0; i < 26; i++) { const p = mk("div", "part", s2p); p.style.background = i % 2 ? "#0b9a2f" : "#1f34c8"; const a = rnd() * Math.PI * 2, r = 380 + rnd() * 380; parts.push({ el: p, x: Math.cos(a) * r, y: Math.sin(a) * r * 0.75 }); }
      // ── S3 : affiches fictives (aucune affiche réelle)
      const POST = [
        ["L'Éclipse d'Ébène", "#3a1c71", "#d76d77"], ["Douala Nights", "#0f2027", "#2c5364"], ["Le Dernier Griot", "#42275a", "#734b6d"], ["Kizuna 7", "#ff4e9b", "#7b2ff7"],
        ["Savane Rouge", "#8e2de2", "#f00000"], ["Neo Tokyo Kid", "#ec008c", "#fc6767"], ["La Saison des Pluies", "#134e5e", "#71b280"], ["Ryu & Sora", "#f953c6", "#b91d73"],
        ["Mission Kribi", "#141e30", "#243b55"], ["Les Lions d'Or", "#c79081", "#dfa579"], ["Cœur de Yaoundé", "#ee0979", "#ff6a00"], ["Hikari", "#4568dc", "#b06ab3"],
        ["Fleuve Sanaga", "#1d4350", "#a43931"], ["Akira no Uta", "#e65c00", "#f9d423"]];
      const MANGA = [3, 5, 7, 11, 13];
      const row1 = $("#row1"), row2 = $("#row2"), cards1 = [], cards2 = [];
      POST.forEach((p, i) => {
        const c = mk("div", "card", row1, `<div class="sh" style="width:150px;height:150px;left:${20 + (i * 37) % 60}px;top:${30 + (i * 53) % 90}px;background:rgba(255,255,255,.18)"></div><div class="t">${p[0]}</div>`);
        c.style.background = `linear-gradient(160deg, ${p[1]}, ${p[2]})`;
        if (MANGA.includes(i)) c.insertAdjacentHTML("beforeend", `<div style="position:absolute;right:10px;top:10px;background:#fff;color:#111;font-weight:900;font-size:16px;padding:3px 8px;border-radius:6px">MANGA</div>`);
        cards1.push(c);
      });
      const R2 = [
        ["sport", "Coupe des Nations · finale", "#0b6623", "#2ecc71"], ["live", "Afrik Info 24", "#1f34c8", "#4f6bff"], ["doc", "Les Géants de la Savane", "#3e5151", "#decba4"],
        ["live", "Ciné Max Direct", "#8e0e00", "#1f1c18"], ["sport", "Ligue Élite · J12", "#134e5e", "#71b280"], ["doc", "Océans Secrets", "#000046", "#1cb5e0"],
        ["live", "Kids TV", "#f7971e", "#ffd200"], ["live", "Musique Non-Stop", "#6a3093", "#a044ff"], ["doc", "Cités Perdues", "#614385", "#516395"], ["live", "Sport Plus", "#11998e", "#38ef7d"]];
      R2.forEach((p) => {
        const c = mk("div", "card wide", row2, `<div class="t">${p[1]}</div>`);
        c.style.background = `linear-gradient(135deg, ${p[2]}, ${p[3]})`;
        if (p[0] === "sport") c.insertAdjacentHTML("beforeend", `<svg style="position:absolute;left:50%;top:30px;width:70px;height:70px;margin-left:-35px"><use href="#i-ball"/></svg><div class="score">2 - 1</div>`);
        if (p[0] === "live") c.insertAdjacentHTML("beforeend", `<div class="live">● DIRECT</div>`);
        if (p[0] === "doc") c.insertAdjacentHTML("beforeend", `<div class="sh" style="left:30px;bottom:40px;width:0;height:0;border-radius:0;border-left:70px solid transparent;border-right:70px solid transparent;border-bottom:90px solid rgba(255,255,255,.3)"></div>`);
        cards2.push(c);
      });
      // ── S4 : continents (bandes qui défilent), égaliseur
      const land = $("#land");
      for (let i = 0; i < 18; i++) { const b = mk("div", "", land); const w = 80 + rnd() * 140, h = 50 + rnd() * 120; Object.assign(b.style, { position: "absolute", left: (i * 70) % 1260 + "px", top: 40 + rnd() * 300 + "px", width: w + "px", height: h + "px", borderRadius: "45%", background: "#0b9a2f", opacity: .9 }); }
      const eq = $("#eq"), eqb = [];
      for (let i = 0; i < 28; i++) eqb.push(mk("i", "", eq));
      // ── S8 : mini-interface
      const mini = $("#mini8");
      POST.slice(0, 8).forEach((p) => { const i = mk("i", "", mini); i.style.background = `linear-gradient(160deg, ${p[1]}, ${p[2]})`; });
      // ── S10 : pièces / confettis
      const conf = $("#confetti"), coins = [];
      for (let i = 0; i < 34; i++) { const c = mk("div", i % 3 ? "coin" : "", conf); if (!(i % 3)) Object.assign(c.style, { position: "absolute", width: "16px", height: "28px", borderRadius: "4px", background: i % 2 ? "#0b9a2f" : "#1f34c8" });
        c.style.left = rnd() * W + "px"; c.style.top = "-60px"; coins.push({ el: c, d: H * (0.7 + rnd() * 0.5), r: (rnd() - .5) * 720, t: rnd() * 0.9 }); }
      // ── S11 : calendrier
      const MOIS = ["JAN", "FÉV", "MAR", "AVR", "MAI", "JUIN", "JUIL", "AOÛT", "SEPT", "OCT", "NOV", "DÉC"];
      const cal = $("#cal"), months = [], stamps = [];
      MOIS.forEach((m, i) => { const d = mk("div", "m" + (i >= 10 ? " g" : ""), cal, `<span>${m}</span>`); months.push(d); if (i >= 10) stamps.push(mk("div", "st", d, "OFFERT")); });
      // ── S12 : icônes qui s'éloignent
      const s12 = $("#s12icons"), s12l = [];
      for (let i = 0; i < 10; i++) { const a = (i / 10) * Math.PI * 2 + 0.3, r = V ? 600 : 470; const d = mk("div", "ico", s12, `<svg><use href="#i-${ICONS[(i * 3) % ICONS.length]}"/></svg>`);
        d.style.left = W / 2 + Math.cos(a) * r * (V ? 0.9 : 1.5) - 55 + "px"; d.style.top = H / 2 + Math.sin(a) * r - 55 + "px"; s12l.push({ el: d, a }); }

      // positions du film voyageur (S7)
      function rectOf(id) { const e = document.getElementById(id); return { x: e.offsetLeft + 10, y: e.offsetTop + 10, w: e.offsetWidth - 20, h: e.offsetHeight - 20 }; }

      // rideau : dimension selon le format
      const PW = W + H * 1.0;
      Object.assign($("#rpanel").style, { width: PW + "px", left: "0px" });

      // traînées néon (style storyboard) sur chaque scène bleue
      document.querySelectorAll(".scene").forEach((sc) => {
        if (sc.classList.contains("jaune")) return;
        const f = sc.querySelector(".fill"); if (!f) return;
        const d = document.createElement("div"); d.className = "sw";
        d.innerHTML = '<svg viewBox="0 0 1200 400" preserveAspectRatio="none"><path d="M0 330 C300 200 700 420 1200 180" stroke="#3dff6e" stroke-width="10" fill="none" opacity=".9" style="filter:drop-shadow(0 0 12px #3dff6e)"/><path d="M0 372 C360 262 760 432 1200 242" stroke="#3dff6e" stroke-width="4" fill="none" opacity=".6"/><path d="M0 298 C320 188 680 378 1200 118" stroke="#ffe600" stroke-width="3" fill="none" opacity=".55"/></svg>';
        f.after(d);
      });

      // ════════════════ TIMELINE ════════════════
      const tl = gsap.timeline({ paused: true });
      const BO = "back.out(1.7)", OV = "cubic-bezier(0.34,1.56,0.64,1)";
      const inPop = (sel, t, d = 0.4, from = {}) => tl.fromTo(sel, { autoAlpha: 0, scale: 0.6, ...from }, { autoAlpha: 1, scale: 1, x: 0, y: 0, duration: d, ease: BO }, t);
      const inUp = (sel, t, d = 0.4, dy = 40) => tl.fromTo(sel, { autoAlpha: 0, y: dy }, { autoAlpha: 1, y: 0, duration: d, ease: BO }, t);
      const out = (sel, t, d = 0.25, to = {}) => tl.to(sel, { autoAlpha: 0, duration: d, ease: "power2.in", ...to }, t);
      const spin360 = (sel, t) => tl.fromTo(sel, { rotationY: 0 }, { rotationY: 360, duration: 0.9, ease: "back.inOut(1.4)" }, t);
      const curtain = (t) => tl.fromTo("#rpanel", { x: -PW - H * 0.4, skewX: -20 }, { x: W + H * 0.4, skewX: -20, duration: 0.65, ease: "cubic-bezier(0.65,0,0.35,1)" }, t);

      // S1 (0 → 3.6) — chaos puis aspiration
      s1list.forEach((o, i) => {
        tl.fromTo(o.el, { autoAlpha: 0, scale: 0, rotation: o.r }, { autoAlpha: 1, scale: 1, rotation: o.r, duration: 0.35, ease: BO }, 0.05 + i * 0.045);
        tl.to(o.el, { x: (rnd() - .5) * 60, y: (rnd() - .5) * 60, rotation: o.r + (rnd() - .5) * 80, duration: 1.6, ease: "sine.inOut" }, 0.9);
        tl.to(o.el, { x: W / 2 - o.x - 55, y: H / 2 - o.y - 55, scale: 0.1, rotation: o.r + 360, autoAlpha: 0, duration: 0.7, ease: "power3.in" }, 2.55 + (i % 9) * 0.03);
      });
      tl.from("#s1a .w", { autoAlpha: 0, y: 50, scale: .8, duration: 0.38, ease: OV, stagger: 0.17 }, 0.55);
      tl.from("#s1b .w", { autoAlpha: 0, y: 50, scale: .8, duration: 0.38, ease: OV, stagger: 0.2 }, 2.0);
      out("#s1txt", 3.0, 0.3, { scale: 0.85 });
      tl.fromTo("#s1tv", { autoAlpha: 0, scale: 0 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: BO }, 3.15);

      // S2 (3.6 → 6.0) — le logo se construit, le badge 360 fait le tour n° 1
      tl.fromTo("#s2glow", { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: "expo.out" }, 3.6);
      tl.to("#s2glow", { autoAlpha: 0.35, duration: 1.0, ease: "sine.out" }, 4.1);
      parts.forEach((p, i) => tl.fromTo(p.el, { x: 0, y: 0, autoAlpha: 1, scale: 1 }, { x: p.x, y: p.y, autoAlpha: 0, scale: 0.4, duration: 1.1, ease: "expo.out" }, 3.62 + (i % 5) * 0.02));
      tl.fromTo("#s2top", { autoAlpha: 0, scale: 0.35, y: 60 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.45, ease: BO, transformOrigin: "50% 40%" }, 3.6);
      tl.fromTo("#s2top", { rotation: 0 }, { rotation: 2.5, duration: 0.09, yoyo: true, repeat: 5, ease: "sine.inOut", transformOrigin: "50% 60%" }, 4.05);
      tl.fromTo("#s2lines", { autoAlpha: 0, scaleX: 0.2 }, { autoAlpha: 1, scaleX: 1, duration: 0.35, ease: BO }, 4.25);
      tl.fromTo("#s2pill", { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BO }, 4.35);
      spin360("#s2pill", 4.7);
      tl.fromTo("#s2logo", { scale: 1.25 }, { scale: 1.45, duration: 2.4, ease: "none" }, 3.6);
      tl.fromTo(".corner#c2a, .corner#c2b", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 }, 4.0);

      // S3 (6.0 → 12.0) — on entre dans l'application par le cadre-écran
      tl.fromTo("#s3clip", { clipPath: "inset(41% 40% 45% 40% round 40px)" }, { clipPath: "inset(0% 0% 0% 0% round 0px)", duration: 0.65, ease: "cubic-bezier(0.65,0,0.35,1)" }, 6.0);
      tl.fromTo("#nav", { autoAlpha: 0, y: -30 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: "power3.out" }, 6.3);
      tl.fromTo("#row1", { x: 0 }, { x: V ? -1500 : -1150, duration: 6.2, ease: "none" }, 6.0);
      tl.fromTo("#row2", { x: V ? -1900 : -1700 }, { x: V ? -900 : -800, duration: 6.2, ease: "none" }, 6.0);
      tl.fromTo("#row1, #row2", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, stagger: 0.12 }, 6.35);
      const NPON = { backgroundColor: "#f6be00", color: "#111111", duration: 0.12 }, NPOFF = { backgroundColor: "#14171f", color: "#c9ccd6", duration: 0.12 };
      tl.to("#np0", NPON, 6.4);
      const beats3 = [[6.9, "#np1", "#h1"], [7.65, "#np2", "#h2"], [8.1, null, "#h3"], [8.65, null, "#h4"], [9.5, "#np3", "#h5"], [10.6, null, "#h6"]];
      beats3.forEach(([t, np, h], i) => {
        if (np) { tl.to(".np", NPOFF, t); tl.to(np, NPON, t + 0.01); tl.fromTo(np, { scale: 1 }, { scale: 1.12, duration: 0.15, yoyo: true, repeat: 1 }, t); }
        tl.fromTo(h, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: OV }, t);
        const next = beats3[i + 1]; tl.to(h, { autoAlpha: 0, y: -30, duration: 0.18, ease: "power2.in" }, next ? next[0] - 0.18 : 11.85);
      });
      // anneau de focus vert : saute de carte en carte (positions calculées au moment voulu)
      const ringTo = (t, card, rowSel, rowX) => {
        const r = $(rowSel); const x = r.offsetLeft + card.offsetLeft + rowX - 8, y = r.offsetTop + card.offsetTop - 8;
        tl.set("#ring3", { width: card.offsetWidth + 16, height: card.offsetHeight + 16 }, t);
        tl.to("#ring3", { x, y, duration: 0.22, ease: "power3.out" }, t);
      };
      const rowXat = (t, a, b) => a + (b - a) * (t - 6.0) / 6.2;
      tl.fromTo("#ring3", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, 6.85);
      const R1 = [V ? 0 : -1150, V ? -1500 : -1150];
      ringTo(6.85, cards1[V ? 2 : 4], "#row1", rowXat(6.95, 0, V ? -1500 : -1150));
      ringTo(7.6, cards1[V ? 4 : 6], "#row1", rowXat(7.7, 0, V ? -1500 : -1150));
      ringTo(8.05, cards1[V ? 5 : 7], "#row1", rowXat(8.15, 0, V ? -1500 : -1150));
      ringTo(8.6, cards2[V ? 4 : 4], "#row2", rowXat(8.7, V ? -1900 : -1700, V ? -900 : -800));
      ringTo(9.45, cards2[V ? 5 : 5], "#row2", rowXat(9.55, V ? -1900 : -1700, V ? -900 : -800));
      ringTo(10.55, cards2[V ? 6 : 6], "#row2", rowXat(10.65, V ? -1900 : -1700, V ? -900 : -800));
      tl.to("#ring3", { autoAlpha: 0, duration: 0.2 }, 11.0);
      tl.fromTo(".card .live", { scale: 1 }, { scale: 1.25, duration: 0.2, yoyo: true, repeat: 3, ease: "sine.inOut" }, 10.6);
      tl.fromTo("#count", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: BO }, 10.75);
      const cv = { a: 0, b: 0 };
      tl.fromTo(cv, { a: 0, b: 0 }, { a: 1000, b: 100, duration: 0.6, ease: "power2.out",
        onUpdate: () => { $("#cv1").textContent = Math.round(cv.a).toLocaleString("fr-FR").replace(/ |\s/g, " "); $("#cv2").textContent = Math.round(cv.b); } }, 10.8);

      // S4 (12.0 → 15.9) — radios, podcasts, musique
      tl.fromTo("#s4wrap", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 12.0);
      tl.fromTo("#globe", { scale: 0.5, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.45, ease: BO }, 12.05);
      tl.fromTo("#land", { x: 0 }, { x: -840, duration: 4, ease: "none" }, 12.0);
      ["#wv1", "#wv2", "#wv3"].forEach((w, i) => tl.fromTo(w, { scale: 1, autoAlpha: 0.9 }, { scale: 2.3, autoAlpha: 0, duration: 1.2, ease: "sine.out", repeat: 2 }, 12.3 + i * 0.4));
      tl.fromTo("#s4w1", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: OV }, 12.6);
      tl.fromTo("#s4w2", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: OV }, 13.7);
      tl.fromTo("#mic", { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BO }, 13.7);
      tl.fromTo("#hp", { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BO }, 14.2);
      tl.fromTo("#s4w3", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: OV }, 14.7);
      tl.fromTo("#eq", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 14.5);
      eqb.forEach((b, i) => {
        const pts = []; for (let j = 0; j < 6; j++) pts.push(0.15 + rnd() * 0.85);
        tl.fromTo(b, { scaleY: 0.1 }, { keyframes: pts.map((p) => ({ scaleY: p, duration: 0.26 })), ease: "sine.inOut" }, 14.5 + (i % 4) * 0.02);
      });
      curtain(15.55);

      // S5 (15.9 → 22.5) — streaming stable
      tl.fromTo("#ph5a", { autoAlpha: 0, y: 120 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: BO }, 16.2);
      tl.fromTo("#ph5b", { autoAlpha: 0, y: 120 }, { autoAlpha: 1, y: 0, duration: 0.45, ease: BO }, 16.35);
      tl.fromTo("#spin5", { rotation: 0 }, { rotation: 360 * 6, duration: 6, ease: "none" }, 16.3);
      tl.fromTo("#wavey5", { x: 0 }, { x: 240, duration: 6, ease: "none" }, 16.3);
      tl.fromTo("#prog5", { scaleX: 0.05 }, { scaleX: 0.85, duration: 6, ease: "none" }, 16.3);
      tl.fromTo("#s5t1", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: OV }, 17.5);
      out("#s5t1", 19.25, 0.22);
      tl.fromTo("#s5t2", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: OV }, 19.45);
      tl.to("#ph5a", { autoAlpha: 0.45, scale: 0.92, duration: 0.4 }, 19.45);
      tl.fromTo("#ph5b", { scale: 1 }, { scale: 1.08, duration: 0.4, ease: BO }, 19.45);
      tl.fromTo("#shield", { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: BO }, 21.2);

      // S6 (22.5 → 28.8) — box Wi-Fi + Internet = Missa TV 360
      inPop("#box", 22.75, 0.45, { y: 60 });
      tl.fromTo("#s6w1", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: OV }, 23.1);
      tl.fromTo("#box .led", { autoAlpha: 0.2 }, { autoAlpha: 1, duration: 0.12, stagger: 0.12 }, 23.3);
      inPop("#net", 24.55, 0.4, { y: -60 });
      tl.fromTo("#s6w2", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: OV }, 24.6);
      if (!V) tl.to("#net", { x: 60, y: 210, scale: 0.55, duration: 0.5, ease: "power3.inOut" }, 25.25);
      inPop("#plus6", 24.75, 0.35);
      inPop("#tv6", 23.0, 0.45, { y: 60 }); inPop("#tv6foot", 23.0, 0.45);
      ["#wf1", "#wf2", "#wf3"].forEach((w, i) => { tl.fromTo(w, { scale: 0.6, autoAlpha: 0.9 }, { scale: V ? 4 : 5, autoAlpha: 0, duration: 1.3, ease: "sine.out" }, 23.3 + i * 0.4); tl.fromTo(w, { scale: 0.6, autoAlpha: 0.9 }, { immediateRender: false, scale: V ? 4 : 5, autoAlpha: 0, duration: 1.3, ease: "sine.out" }, 26.15 + i * 0.35); });
      // « … » : tout se fige 25,9 → 26,15, puis la TV s'allume sur « et tu accèdes »
      inPop("#eq6", 26.15, 0.35);
      tl.fromTo("#tvon6", { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: BO }, 26.45);
      tl.fromTo("#tv6", { boxShadow: "0 30px 60px rgba(0,0,0,.3)" }, { boxShadow: "0 0 90px rgba(46,204,113,.9)", duration: 0.5 }, 26.5);

      // S7 (28.8 → 31.4) — téléphone → tablette → télé
      tl.fromTo("#tv7, #tv7foot, #tb7, #ph7", { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: "power3.out", stagger: 0.04 }, 28.75);
      const P = rectOf("ph7"), T = rectOf("tb7"), TVr = rectOf("tv7");
      Object.assign($("#film7").style, { left: "0px", top: "0px", width: P.w + "px", height: P.h + "px", transformOrigin: "0 0" });
      tl.fromTo("#film7", { x: P.x, y: P.y, scaleX: 1, scaleY: 1, autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2 }, 29.3);
      tl.to("#film7", { x: T.x, y: T.y, scaleX: T.w / P.w, scaleY: T.h / P.h, duration: 0.55, ease: "power3.inOut" }, 29.7);
      tl.to("#film7", { x: TVr.x, y: TVr.y, scaleX: TVr.w / P.w, scaleY: TVr.h / P.h, duration: 0.5, ease: "power3.inOut" }, 30.2);
      tl.fromTo("#wavey7", { x: 0 }, { x: 300, duration: 2.4, ease: "none" }, 29.0);
      [["#s7w1", 29.3], ["#s7w2", 30.05], ["#s7w3", 30.6]].forEach(([w, t]) => { tl.to(w, { color: "#1f34c8", duration: 0.12 }, t); tl.fromTo(w, { scale: 1 }, { scale: 1.12, duration: 0.15, yoyo: true, repeat: 1 }, t); });
      curtain(31.05);

      // S8 (31.4 → 38.3) — essai gratuit 24 h
      tl.fromTo("#s8aIn", { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.42, ease: "back.out(2.4)" }, 31.8);
      tl.fromTo("#s8a", { x: 0 }, { keyframes: [{ x: 3, duration: 0.04 }, { x: -3, duration: 0.04 }, { x: 2, duration: 0.04 }, { x: 0, duration: 0.03 }] }, 31.95);
      out("#s8a", 32.62, 0.2, { scale: 1.1 });
      tl.fromTo("#ph8", { autoAlpha: 0, y: 140 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: BO }, 32.8);
      tl.fromTo("#check8", { autoAlpha: 0, scale: 0 }, { autoAlpha: 0, scale: 0, duration: 0.01 }, 31.4);
      tl.fromTo("#finger", { autoAlpha: 0, x: 120, y: 140 }, { autoAlpha: 1, x: 0, y: 0, duration: 0.35, ease: "power3.out" }, 32.95);
      tl.to("#finger", { scale: 0.75, duration: 0.08, yoyo: true, repeat: 1 }, 33.33);
      tl.fromTo("#dlbtn", { scale: 1 }, { scale: 0.92, duration: 0.08, yoyo: true, repeat: 1 }, 33.33);
      out("#finger", 33.6, 0.2);
      tl.fromTo("#bar8", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "power2.inOut" }, 33.4);
      tl.to("#check8", { autoAlpha: 1, scale: 1, duration: 0.3, ease: BO }, 34.0);
      tl.to("#check8", { x: V ? 600 : 900, y: -120, scale: 0.4, autoAlpha: 0, duration: 0.35, ease: "power2.in" }, 34.3);
      out("#ph8", 34.3, 0.3, { scale: 0.85 });
      tl.fromTo("#dial", { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1, duration: 0.42, ease: BO }, 34.3);
      tl.fromTo("#dialRing", { attr: { "stroke-dashoffset": 100 } }, { attr: { "stroke-dashoffset": 0 }, duration: 1.2, ease: "cubic-bezier(0.65,0,0.35,1)" }, 34.45);
      tl.fromTo("#legal8", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.3 }, 34.3);
      tl.fromTo("#ruban", { autoAlpha: 0, scale: 2.2, rotation: -14 }, { autoAlpha: 1, scale: 1, rotation: -8, duration: 0.3, ease: "back.out(2.2)" }, 35.95);
      tl.fromTo("#s8g", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: OV }, 35.9);
      tl.fromTo("#s8t", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: OV }, 36.6);
      tl.fromTo("#ph8b", { autoAlpha: 0, x: 120 }, { autoAlpha: 1, x: 0, duration: 0.4, ease: BO }, 36.6);
      tl.fromTo("#ring8", { x: 6, y: 32, autoAlpha: 0 }, { autoAlpha: 1, duration: 0.15 }, 36.9);
      tl.to("#ring8", { x: 122, duration: 0.2, ease: "power3.out" }, 37.25);
      tl.to("#ring8", { x: 6, y: 162, duration: 0.2, ease: "power3.out" }, 37.6);
      // morphing : le cadran devient le point du « ? »
      out("#ruban, #s8g, #s8t, #ph8b, #legal8", 38.05, 0.2);

      // S9 (38.3 → 40.3) — suspense
      // le disque part de la position exacte du cadran 24 h (scène 8) et rejoint le point du « ? »
      const dl = $("#dial"), dcx = dl.offsetLeft + dl.offsetWidth / 2, dcy = dl.offsetTop + dl.offsetHeight / 2;
      tl.fromTo("#qdisc", { scale: 1, backgroundColor: "#0b9a2f", x: dcx - W / 2, y: dcy - H / 2 }, { scale: 0.236, backgroundColor: "#ffe600", x: 0, y: 140, duration: 0.4, ease: "power3.inOut" }, 38.3);
      tl.set("#qdisc", { autoAlpha: 0 }, 38.71);
      tl.fromTo("#qdot", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.01 }, 38.7);
      tl.fromTo("#qhook", { attr: { "stroke-dashoffset": 100 } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.45, ease: "power2.out" }, 38.55);
      tl.fromTo("#q", { scale: 1 }, { scale: 1.18, duration: 1.4, ease: "sine.out" }, 38.6);
      [38.45, 38.97, 39.48, 40.0].forEach((t) => tl.fromTo("#qdot", { scale: 1, transformOrigin: "50% 50%" }, { scale: 1.25, duration: 0.12, yoyo: true, repeat: 1, ease: "sine.out" }, t));
      tl.to("#q", { rotationY: 90, scale: 1.4, autoAlpha: 0, duration: 0.3, ease: "power2.in" }, 40.0);

      // S10 (40.3 → 44.2) — les deux prix ; S11 (44.2 → 46.7) — l'année offerte
      tl.fromTo("#seul", { autoAlpha: 0, y: -30 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: OV }, 40.45);
      tl.fromTo("#pc1", V ? { autoAlpha: 0, y: -200 } : { autoAlpha: 0, x: -700 }, { autoAlpha: 1, x: 0, y: 0, duration: 0.45, ease: OV }, 40.85);
      const pv = { a: 0, b: 0 };
      const fmt = (n) => Math.round(n).toLocaleString("fr-FR").replace(/ |\s/g, " ");
      tl.fromTo(pv, { a: 0 }, { a: 1000, duration: 0.6, ease: "power2.out", onUpdate: () => ($("#pv1").textContent = fmt(pv.a)) }, 40.95);
      tl.fromTo("#pc2", V ? { autoAlpha: 0, y: 260 } : { autoAlpha: 0, x: 800 }, { autoAlpha: 1, x: 0, y: 0, duration: 0.45, ease: OV }, 42.7);
      tl.fromTo(pv, { b: 0 }, { b: 10000, duration: 0.6, ease: "power2.out", onUpdate: () => ($("#pv2").textContent = fmt(pv.b)) }, 42.8);
      tl.fromTo("#b10", { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.3, ease: BO }, 42.85);
      spin360("#b10", 43.0);
      coins.forEach((c) => tl.fromTo(c.el, { y: 0, rotation: 0 }, { y: c.d, rotation: c.r, duration: 1.4, ease: "power1.in" }, 42.9 + c.t));
      // S11 : les prix glissent pour laisser la place au calendrier (restent visibles)
      out("#seul", 44.15, 0.2);
      tl.to("#prices", { y: V ? -150 : -150, scale: V ? 0.62 : 0.62, duration: 0.45, ease: "cubic-bezier(0.65,0,0.35,1)" }, 44.15);
      tl.fromTo(months, { autoAlpha: 0, rotationX: -90, transformOrigin: "50% 0%" }, { autoAlpha: 1, rotationX: 0, duration: 0.18, stagger: 0.055, ease: "power2.out" }, 44.3);
      tl.fromTo("#eqn", { autoAlpha: 0, y: 20 }, { autoAlpha: 1, y: 0, duration: 0.3, ease: "power2.out" }, 45.0);
      tl.fromTo(stamps, { autoAlpha: 0, scale: 2.4 }, { autoAlpha: 1, scale: 1, duration: 0.22, ease: "back.out(2)", stagger: 0.06 }, 45.8);
      tl.fromTo("#offerts", { autoAlpha: 0, scale: 1.8, rotation: -6 }, { autoAlpha: 1, scale: 1, rotation: -3, duration: 0.3, ease: "back.out(2)" }, 45.85);

      // S12 (46.7 → 48.6) — les icônes s'éloignent, la caméra pousse vers le logo
      s12l.forEach((o, i) => { tl.fromTo(o.el, { autoAlpha: 1, x: 0, y: 0, scale: 1 }, { autoAlpha: 0, x: Math.cos(o.a) * 700, y: Math.sin(o.a) * 500, scale: 1.8, duration: 0.9, ease: "power2.in" }, 46.95 + i * 0.07); });
      tl.fromTo("#s12logo", { scale: 0.5, autoAlpha: 0 }, { scale: 1.2, autoAlpha: 1, duration: 1.7, ease: "power2.out" }, 46.75);
      curtain(48.25);

      // S13 (48.6 → 54.1) — recomposition de la bannière + slogan en trois temps
      tl.fromTo("#s13logo", { autoAlpha: 0, scale: 0.6 }, { autoAlpha: 1, scale: V ? 0.85 : 1.05, duration: 0.45, ease: BO, transformOrigin: "50% 0%" }, 48.85);
      tl.fromTo("#s13line", V ? { scaleX: 0 } : { scaleY: 0 }, V ? { scaleX: 1, duration: 0.45, ease: "power3.out" } : { scaleY: 1, duration: 0.45, ease: "power3.out" }, 49.1);
      tl.fromTo("#tv13, #tv13foot", { autoAlpha: 0, x: 120 }, { autoAlpha: 1, x: 0, duration: 0.45, ease: BO }, 49.3);
      tl.fromTo("#tb13", { autoAlpha: 0, y: 80 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: BO }, 49.5);
      tl.fromTo("#ph13", { autoAlpha: 0, y: 80 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: BO }, 49.65);
      tl.fromTo("#wavey13", { x: 0 }, { x: 260, duration: 5.4, ease: "none" }, 48.7);
      [["#sl1", 50.75], ["#sl2", 51.75], ["#sl3", 52.75]].forEach(([s, t]) => tl.fromTo(s, { autoAlpha: 0, y: 34 }, { autoAlpha: 1, y: 0, duration: 0.38, ease: OV }, t));

      // S14 (54.1 → 60) — appel à l'action, badge 360 : tour n° 3
      tl.fromTo("#s14logo", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 0.82, duration: 0.4, ease: BO }, 54.15);
      spin360("#s14pill", 54.55);
      tl.fromTo("#cta", { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.42, ease: "back.out(2)" }, 54.3);
      tl.fromTo("#cta", { scale: 1 }, { scale: 1.05, duration: 0.55, yoyo: true, repeat: 7, ease: "sine.inOut", immediateRender: false }, 54.8);
      tl.fromTo("#arrow", { y: -8 }, { y: 10, duration: 0.3, yoyo: true, repeat: 15, ease: "sine.inOut" }, 54.7);
      tl.fromTo("#pill14", { autoAlpha: 0, y: 26 }, { autoAlpha: 1, y: 0, duration: 0.35, ease: BO }, 54.85);
      tl.fromTo("#dl14", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.35 }, 55.2);
      tl.fromTo("#legal14", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.35 }, 55.3);

      // ═══ v11 : animations propres au nouveau style ═══
      tl.fromTo(".sw svg", { x: -50 }, { x: 50, duration: 60, ease: "none" }, 0);
      // S1 : la famille devant la télé, puis aspirée avec les icônes
      tl.fromTo("#p1", { autoAlpha: 0, scale: 1.08 }, { autoAlpha: 1, scale: 1, duration: 0.45, ease: "power2.out" }, 0.0);
      tl.to("#p1", { scale: 1.04, duration: 2.0, ease: "none" }, 0.5);
      tl.to("#p1", { scale: 0.08, autoAlpha: 0, duration: 0.55, ease: "power3.in" }, 2.6);
      tl.fromTo("#s1b", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.15 }, 1.95);
      tl.fromTo("#s4t .dot", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.2, stagger: 1.0 }, 13.65);
      // S3 : défilé des univers (une carte par mot de la voix)
      const C3 = [["#c3tv", 6.3], ["#c3films", 6.9], ["#c3manga", 8.1], ["#c3sport", 8.65], ["#c3docs", 9.5], ["#c3live", 10.6]];
      C3.forEach(([c, t], i) => {
        tl.fromTo(c, { autoAlpha: 0, x: 240, scale: 0.92 }, { autoAlpha: 1, x: 0, scale: 1, duration: 0.35, ease: OV }, t);
        if (i > 0) tl.to(C3[i - 1][0], { autoAlpha: 0, x: -240, scale: 0.92, duration: 0.3, ease: "power2.in" }, t);
      });
      // S4 : musique
      tl.fromTo("#p4", { autoAlpha: 0, scale: 0.8, y: 40 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.45, ease: BO }, 12.05);
      // S7 : tous les écrans
      tl.fromTo("#p7", { autoAlpha: 0, scale: 0.85 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: BO }, 28.75);
      tl.to("#p7", { scale: 1.05, duration: 2.3, ease: "none" }, 29.2);
      // S12 : la question
      tl.fromTo("#s12a", { autoAlpha: 0, scale: 0.7 }, { autoAlpha: 1, scale: 1, duration: 0.4, ease: OV }, 46.95);
      tl.fromTo("#s12p", { attr: { "stroke-dashoffset": 100 } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.45, ease: "power2.out" }, 47.3);
      // S13 : catégories (icônes néon)
      tl.fromTo(".cat", { autoAlpha: 0, scale: 0.5 }, { autoAlpha: 1, scale: 1, duration: 0.35, ease: BO, stagger: 0.12 }, 49.3);
      // S14 : carte de fin « Le divertissement sans limite ! »
      out("#cta, #pill14, #dl14", 57.0, 0.3);
      tl.to("#s14logo", { y: V ? 260 : 150, scale: 1.05, duration: 0.6, ease: "cubic-bezier(0.65,0,0.35,1)" }, 57.0);
      tl.fromTo("#tag14", { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.4, ease: OV }, 57.4);

      // ── recalage sur l'audio fourni : chaque animation est déplacée à l'instant correspondant de la voix
      const TMAP = __TMAP__;
      if (TMAP) {
        const O = TMAP.old, Nw = TMAP.new;
        const Mt = (t) => { let i = Math.min(Math.max(Math.floor(t / 0.1), 0), O.length - 2); while (i > 0 && O[i] > t) i--; while (i < O.length - 2 && O[i + 1] <= t) i++;
          return Nw[i] + (Nw[i + 1] - Nw[i]) * (t - O[i]) / (O[i + 1] - O[i]); };
        tl.getChildren(false, true, true).forEach((c) => {
          const s0 = c.startTime(), d0 = c.duration(), ns = Mt(s0);
          if (d0 > 1.0 && !c.vars.repeat) c.duration(Math.max(0.3, Mt(s0 + d0) - ns));
          c.startTime(ns);
        });
      }
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
