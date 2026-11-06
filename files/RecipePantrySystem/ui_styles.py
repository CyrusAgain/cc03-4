"""The look of the Recipe Pantry System, kept inside Python.

app.py serves ICON_CSS + APP_CSS together at /theme.css, so there are no .css files.
(The Font Awesome icon font itself is the binary file static/webfonts/fa-solid-900.woff2.)
"""
import hashlib

# Only the Font Awesome icons the pages use. __FONT_URL__ is filled in per request.
ICON_CSS = r"""@font-face{font-family:"Font Awesome 6 Pro";font-style:normal;font-weight:900;font-display:block;src:url(__FONT_URL__) format("woff2")}
.fa,.fas,.fa-solid{font-family:"Font Awesome 6 Pro";font-weight:900;-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;display:inline-block;font-style:normal;font-variant:normal;line-height:1;text-rendering:auto}
.fa-arrow-left:before{content:"\f060"}
.fa-arrow-right:before{content:"\f061"}
.fa-basket-shopping:before{content:"\f291"}
.fa-book-open:before{content:"\f518"}
.fa-boxes-stacked:before{content:"\f468"}
.fa-circle-check:before{content:"\f058"}
.fa-clipboard-check:before{content:"\f46c"}
.fa-floppy-disk:before{content:"\f0c7"}
.fa-gauge-high:before{content:"\f625"}
.fa-hourglass-half:before{content:"\f254"}
.fa-layer-group:before{content:"\f5fd"}
.fa-lightbulb:before{content:"\f0eb"}
.fa-list-check:before{content:"\f0ae"}
.fa-pen:before{content:"\f304"}
.fa-right-from-bracket:before{content:"\f2f5"}
.fa-rotate:before{content:"\f2f1"}
.fa-star:before{content:"\f005"}
.fa-trash:before{content:"\f1f8"}
.fa-triangle-exclamation:before{content:"\f071"}
.fa-utensils:before{content:"\f2e7"}
.fa-wand-magic-sparkles:before{content:"\e2ca"}
"""

APP_CSS = r"""
:root {
  --primary: #e8281a;
  --primary-dark: #c01e12;
  --secondary: #f6a623;
  --dark: #1a1a1a;
  --green: #2d6a4f;
  --cream: #fff8f0;
  --cream2: #fef0dc;
  --surface: #fff;
  --ink: #444;
  --ink2: #777;
  --line: #f0e4d3;
  --ok: #2d6a4f; --ok-soft: #e1f1e8;
  --short: #c01e12; --short-soft: #fde7e3;
  --shadow: 0 8px 40px rgba(0, 0, 0, .08);
  --shadow-lg: 0 20px 60px rgba(0, 0, 0, .14);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; min-height: 100vh; display: flex; flex-direction: column;
  font-family: "Poppins", -apple-system, "Segoe UI", Roboto, sans-serif;
  color: var(--ink); background: var(--cream); overflow-x: hidden;
}
h1, h2, h3, h4 { font-family: "Playfair Display", Georgia, serif; color: var(--dark); }
a { color: var(--primary); text-decoration: none; transition: .3s; }
a:hover { color: var(--primary-dark); }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 10px; }


.topbar {
  position: sticky; top: 0; z-index: 990;
  display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
  padding: 0 28px; background: var(--surface); box-shadow: 0 2px 20px rgba(0, 0, 0, .07);
}
.topbar .brand { display: flex; align-items: center; gap: 10px; padding: 10px 0; text-decoration: none; }
.brand-ico {
  width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; font-size: 1.15rem;
  box-shadow: 0 4px 15px rgba(232, 40, 26, .35);
}
.brand-name { font-family: "Playfair Display", serif; font-size: 1.35rem; font-weight: 900; color: var(--dark); line-height: 1.1; }
.brand-name span { color: var(--primary); }
.brand-sub { display: block; font-family: "Poppins", sans-serif; font-size: .58rem; font-weight: 500; text-transform: uppercase; letter-spacing: 2px; color: #aaa; }
.topbar nav { display: flex; align-items: center; flex-wrap: wrap; }
.topbar nav a {
  position: relative; margin: 0; padding: 26px 13px; font-size: .87rem; font-weight: 500; color: #333;
}
.topbar nav a::after {
  content: ""; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%);
  width: 0; height: 3px; border-radius: 3px 3px 0 0; background: var(--primary); transition: .3s;
}
.topbar nav a:hover, .topbar nav a.current { color: var(--primary); }
.topbar nav a:hover::after, .topbar nav a.current::after { width: 55%; }
.topbar nav form { margin-left: 8px; }
.topbar nav .btn { padding: 8px 18px; font-size: .82rem; }


main { flex: 1; }
.wrap { max-width: 820px; margin: 0 auto; padding: 44px 20px 72px; }
.wrap.narrow { max-width: 460px; }
h1 { font-size: clamp(1.7rem, 4vw, 2.3rem); font-weight: 900; line-height: 1.2; margin: 0 0 6px; }
h1::after {
  content: ""; display: block; width: 58px; height: 4px; border-radius: 4px; margin-top: 10px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
}
.sub { color: var(--ink2); font-size: .93rem; line-height: 1.7; margin: 14px 0 24px; }
.muted { color: var(--ink2); }
.card {
  background: var(--surface); border: 1px solid var(--line); border-radius: 20px;
  padding: 28px; margin-bottom: 22px; box-shadow: var(--shadow);
}
.card h1 { font-size: 1.8rem; }


.field { margin-bottom: 16px; }
.field label, label { display: block; font-weight: 600; font-size: .85rem; color: var(--dark); margin-bottom: 6px; }
input[type=text], input[type=email], input[type=password], input[type=number], input[type=date], select {
  width: 100%; padding: 11px 14px; font: inherit; font-size: .92rem; color: var(--dark);
  background: var(--cream); border: 1.5px solid var(--line); border-radius: 12px; outline: none; transition: .25s;
}
input:focus, select:focus { border-color: var(--primary); background: #fff; box-shadow: 0 0 0 4px rgba(232, 40, 26, .1); }
input::placeholder { color: #b9ab98; }
input[type=radio] { accent-color: var(--primary); margin-right: 6px; }


.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer;
  padding: 11px 26px; border: 2px solid transparent; border-radius: 50px;
  font: 600 .9rem "Poppins", sans-serif; color: #fff; text-decoration: none; transition: .3s;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  box-shadow: 0 8px 22px rgba(232, 40, 26, .3);
}
.btn:hover { transform: translateY(-2px); color: #fff; box-shadow: 0 12px 28px rgba(232, 40, 26, .42); }
.btn.secondary { background: transparent; color: var(--primary); border-color: var(--primary); box-shadow: none; }
.btn.secondary:hover { background: var(--primary); color: #fff; }
.btn.ghost { background: #fff; color: var(--ink); border-color: var(--line); box-shadow: none; }
.btn.ghost:hover { color: var(--primary); border-color: var(--primary); }
.btn.danger { background: #fff; color: var(--short); border-color: #f4c9c2; box-shadow: none; }
.btn.danger:hover { background: var(--short); color: #fff; border-color: var(--short); }
.row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }


.flash { padding: 12px 18px; border-radius: 14px; margin-bottom: 14px; font-size: .9rem; border-left: 5px solid; }
.flash.error { background: var(--short-soft); color: var(--short); border-color: var(--primary); }
.flash.ok { background: var(--ok-soft); color: var(--ok); border-color: var(--green); }


table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 10px 8px; font-size: .72rem; letter-spacing: 1.2px; text-transform: uppercase; color: var(--primary); border-bottom: 2px solid var(--cream2); }
td { padding: 13px 8px; font-size: .92rem; border-top: 1px solid var(--line); vertical-align: middle; }
tr:first-child td { border-top: none; }
.list-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-top: 1px solid var(--line); }
.list-item:first-child { border-top: none; }
.card.list-item { padding: 22px 28px; transition: .3s; }
.card.list-item:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
.pill { display: inline-block; padding: 3px 12px; border-radius: 50px; font-size: .75rem; font-weight: 600; }
.pill.ok { background: var(--ok-soft); color: var(--ok); }
.pill.short { background: var(--short-soft); color: var(--short); }


.ing-row { display: grid; grid-template-columns: 2fr 1fr 1.5fr auto; gap: 8px; margin-bottom: 10px; align-items: stretch; }
.ing-row input[type=number] { min-width: 0; }
.ing-row .btn { padding: 8px 16px; }


.menu { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
.menu a {
  display: block; padding: 28px 24px; border-radius: 20px; background: var(--surface);
  border: 1px solid var(--line); box-shadow: var(--shadow); color: var(--dark); transition: .35s;
}
.menu a:hover { transform: translateY(-6px); box-shadow: 0 28px 70px rgba(232, 40, 26, .15); border-color: var(--primary); }
.menu a .m-ico {
  width: 54px; height: 54px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px; font-size: 1.3rem; color: #fff;
  background: linear-gradient(135deg, var(--primary), var(--secondary)); box-shadow: 0 6px 18px rgba(232, 40, 26, .3);
}
.menu a strong { display: block; font-family: "Playfair Display", serif; font-size: 1.2rem; margin-bottom: 4px; }
.menu a span { color: var(--ink2); font-size: .86rem; }


.hero { text-align: center; }
.hero .slbl { font-family: "Dancing Script", cursive; font-size: 1.5rem; color: var(--primary); display: block; margin-bottom: 2px; }
.hero h1::after { margin-left: auto; margin-right: auto; }


footer { background: var(--dark); color: #888; text-align: center; padding: 26px 20px; font-size: .82rem; }
footer strong { font-family: "Playfair Display", serif; font-size: 1.1rem; color: #fff; }
footer strong span { color: var(--primary); }

@media (max-width: 640px) {
  .topbar { padding: 0 16px; }
  .topbar nav a { padding: 12px 9px; }
  .ing-row { grid-template-columns: 1fr 1.5fr auto; }
  .ing-row > input[type=text] { grid-column: 1 / -1; }
  .card { padding: 20px; }
}


@keyframes riseIn   { from { opacity: 0; transform: translateY(22px); } to { opacity: 1; transform: none; } }
@keyframes fadeIn   { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideDown{ from { opacity: 0; transform: translateY(-14px); } to { opacity: 1; transform: none; } }
@keyframes popIn    { 0% { opacity: 0; transform: scale(.6); } 70% { transform: scale(1.08); } 100% { opacity: 1; transform: none; } }
@keyframes rowIn    { from { opacity: 0; transform: translateX(-14px); } to { opacity: 1; transform: none; } }
@keyframes rowOut   { to { opacity: 0; transform: translateX(18px); height: 0; margin: 0; } }
@keyframes spin     { to { transform: rotate(360deg); } }
@keyframes floaty   { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

.topbar { animation: slideDown .5s cubic-bezier(.2, .7, .2, 1) backwards; }
footer  { animation: fadeIn .8s .3s ease backwards; }


.wrap > * { animation: riseIn .55s cubic-bezier(.2, .7, .2, 1) backwards; }
.wrap > *:nth-child(1) { animation-delay: .02s; }
.wrap > *:nth-child(2) { animation-delay: .09s; }
.wrap > *:nth-child(3) { animation-delay: .16s; }
.wrap > *:nth-child(4) { animation-delay: .23s; }
.wrap > *:nth-child(5) { animation-delay: .30s; }
.wrap > *:nth-child(6) { animation-delay: .37s; }
.wrap > *:nth-child(n+7) { animation-delay: .44s; }


.menu a { animation: riseIn .6s cubic-bezier(.2, .7, .2, 1) backwards; }
.menu a:nth-child(1) { animation-delay: .20s; }
.menu a:nth-child(2) { animation-delay: .30s; }
.menu a:nth-child(3) { animation-delay: .40s; }
.card.list-item { animation: riseIn .55s cubic-bezier(.2, .7, .2, 1) backwards; }

tr { animation: rowIn .45s ease backwards; }
tr:nth-child(1) { animation-delay: .20s; } tr:nth-child(2) { animation-delay: .26s; }
tr:nth-child(3) { animation-delay: .32s; } tr:nth-child(4) { animation-delay: .38s; }
tr:nth-child(5) { animation-delay: .44s; } tr:nth-child(6) { animation-delay: .50s; }
tr:nth-child(n+7) { animation-delay: .56s; }
.list-item { animation: fadeIn .5s ease backwards; }
.flash { animation: slideDown .45s cubic-bezier(.2, .7, .2, 1) backwards; }
.pill  { animation: popIn .5s .35s cubic-bezier(.2, .7, .2, 1) backwards; }


main, footer { transition: opacity .22s ease, transform .22s ease; }
body.leaving main { opacity: 0; transform: translateY(-10px); }


.ing-row.row-in  { animation: rowIn .35s ease; }
.ing-row.row-out { animation: rowOut .22s ease forwards; overflow: hidden; }


.brand-ico { transition: transform .5s cubic-bezier(.2, .7, .2, 1); }
.brand:hover .brand-ico { transform: rotate(360deg) scale(1.06); }
.btn { transition: transform .25s, box-shadow .25s, background .25s, color .25s, border-color .25s; }
.btn:active { transform: translateY(0) scale(.97); }
.btn i { transition: transform .4s ease; }
.btn:hover .fa-rotate { animation: spin .7s ease; }
tr { transition: background .25s; }
tr:hover td { background: var(--cream); }
.ing-row input, .ing-row select { transition: border-color .25s, box-shadow .25s, background .25s; }
.field input:focus, .field select:focus { transform: translateY(-1px); }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}


.topbar nav a { display: inline-flex; align-items: center; gap: 7px; isolation: isolate; }
.topbar nav a i { font-size: .85rem; transition: transform .3s; }
.topbar nav a span { display: inline-block; transition: transform .3s cubic-bezier(.2, .7, .2, 1); }
.topbar nav a::before {
  content: ""; position: absolute; inset: 14px 2px; z-index: -1; border-radius: 50px;
  background: rgba(232, 40, 26, .09); opacity: 0; transform: scale(.55);
  transition: opacity .3s, transform .35s cubic-bezier(.2, .7, .2, 1);
}
.topbar nav a:hover::before, .topbar nav a.current::before { opacity: 1; transform: scale(1); }
.topbar nav a:hover span { transform: translateY(-2px); }
.topbar nav a:hover i { animation-duration: .7s; animation-timing-function: ease; }
.topbar nav a.n-dash:hover i    { animation-name: gaugeSwing; }
.topbar nav a.n-pantry:hover i  { animation-name: boxShake; }
.topbar nav a.n-recipes:hover i { animation-name: flipY; }
.topbar nav a.n-check:hover i   { animation-name: tickPop; }


.logout-btn:hover { background: var(--primary); border-color: var(--primary); color: #fff; box-shadow: 0 8px 22px rgba(232, 40, 26, .35); }
.logout-btn i { transition: transform .35s cubic-bezier(.2, .7, .2, 1); }
.logout-btn:hover i { animation: exitArrow .6s ease infinite; }


.menu a { position: relative; overflow: hidden; }
.menu a::before {            
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 5px;
  background: linear-gradient(var(--primary), var(--secondary));
  transform: scaleY(0); transform-origin: bottom; transition: transform .4s cubic-bezier(.2, .7, .2, 1);
}
.menu a::after {             
  content: ""; position: absolute; top: 0; bottom: 0; left: -60%; width: 40%;
  background: linear-gradient(100deg, transparent, rgba(246, 166, 35, .22), transparent);
  transform: skewX(-18deg); transition: left .7s ease; pointer-events: none;
}
.menu a:hover::before { transform: scaleY(1); }
.menu a:hover::after  { left: 130%; }
.menu a .m-ico { transition: transform .35s cubic-bezier(.2, .7, .2, 1), box-shadow .35s; }
.menu a:hover .m-ico { box-shadow: 0 10px 26px rgba(232, 40, 26, .45); }
.menu a.m-check:hover .m-ico   { animation: tickPop .7s ease forwards; }
.menu a.m-pantry:hover .m-ico  { animation: boxShake .7s ease; }
.menu a.m-recipes:hover .m-ico { animation: flipY .8s ease; }
.menu a strong { transition: color .3s, transform .3s; }
.menu a:hover strong { color: var(--primary); transform: translateX(4px); }
.menu a .go {
  position: absolute; right: 20px; bottom: 20px; width: 34px; height: 34px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-style: normal; font-size: .8rem;
  background: var(--cream2); color: var(--primary); opacity: 0; transform: translateX(-14px);
  transition: opacity .3s, transform .35s cubic-bezier(.2, .7, .2, 1), background .3s, color .3s;
}
.menu a:hover .go { opacity: 1; transform: none; }
.menu a:hover .go i { animation: nudgeRight .9s ease-in-out infinite; }
.menu a .go:hover { background: var(--primary); color: #fff; }


.title-ico {
  display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; margin-right: 12px;
  border-radius: 50%; vertical-align: middle; font-size: 1.1rem; color: #fff;
  background: linear-gradient(135deg, var(--primary), var(--secondary)); box-shadow: 0 6px 18px rgba(232, 40, 26, .3);
  animation: popIn .6s .1s cubic-bezier(.2, .7, .2, 1) backwards;
  transition: transform .4s cubic-bezier(.2, .7, .2, 1);
}
h1:hover .title-ico { transform: rotate(-10deg) scale(1.1); }


.back-row { margin-top: 8px; }
.btn.back-btn { background: #fff; color: var(--ink); border-color: var(--line); box-shadow: 0 4px 14px rgba(0, 0, 0, .05); }
.btn.back-btn:hover { background: var(--primary); border-color: var(--primary); color: #fff; box-shadow: 0 10px 26px rgba(232, 40, 26, .35); }
.btn.back-btn i { transition: transform .3s; }
.btn.back-btn:hover i { animation: nudgeLeft .8s ease-in-out infinite; }


@keyframes tickPop   { 0% { transform: scale(1); } 30% { transform: scale(1.3) rotate(-12deg); } 60% { transform: scale(.95) rotate(8deg); } 100% { transform: scale(1.12) rotate(0); } }
@keyframes boxShake  { 0%, 100% { transform: translateX(0) rotate(0); } 20% { transform: translateX(-4px) rotate(-9deg); } 40% { transform: translateX(4px) rotate(9deg); } 60% { transform: translateX(-3px) rotate(-5deg); } 80% { transform: translateX(3px) rotate(4deg); } }
@keyframes flipY     { from { transform: perspective(300px) rotateY(0); } to { transform: perspective(300px) rotateY(360deg); } }
@keyframes gaugeSwing{ 0%, 100% { transform: rotate(0); } 30% { transform: rotate(-25deg); } 65% { transform: rotate(20deg); } }
@keyframes nudgeLeft { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(-5px); } }
@keyframes nudgeRight{ 0%, 100% { transform: translateX(0); } 50% { transform: translateX(4px); } }
@keyframes exitArrow { 0% { transform: translateX(0); opacity: 1; } 45% { transform: translateX(8px); opacity: 0; } 55% { transform: translateX(-8px); opacity: 0; } 100% { transform: translateX(0); opacity: 1; } }


.unit-group {
  display: flex; align-items: stretch; min-width: 0; overflow: hidden;
  background: var(--cream); border: 1.5px solid var(--line); border-radius: 12px; transition: .25s;
}
.unit-group:focus-within { border-color: var(--primary); background: #fff; box-shadow: 0 0 0 4px rgba(232, 40, 26, .1); }
.unit-group .unit-num, .unit-group .unit-select {
  border: none; border-radius: 0; background: transparent; box-shadow: none; transform: none;
}
.unit-group .unit-num { flex: 1; min-width: 0; width: auto; }
.unit-group .unit-select {
  flex: 0 0 auto; width: 78px; padding: 0 6px 0 10px; cursor: pointer; font-weight: 600; color: var(--primary);
  border-left: 1.5px solid var(--line);
}
.unit-group .unit-num:focus, .unit-group .unit-select:focus { box-shadow: none; background: transparent; transform: none; }


.small { font-size: .8rem; }
.tight { margin-top: 3px; }
.note { margin: -4px 0 14px; }
.card-title { font-size: 1.15rem; margin: 0 0 4px; }
.card-title i, .group-save h3 i, .idea-block h3 i { color: var(--primary); margin-right: 6px; }
.flash.warn { background: #fff3da; color: #8a5a00; border-color: var(--secondary); }
.row.nowrap { flex-wrap: nowrap; }
.row.nowrap input { flex: 1; min-width: 0; }


.group-row {
  display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap;
  padding: 14px 0; border-top: 1px solid var(--line);
}
.group-row:first-of-type { margin-top: 8px; }
.group-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1 1 260px; }
.group-info strong { font-family: "Playfair Display", serif; font-size: 1.05rem; color: var(--dark); }
.group-row form { margin: 0; }


.pick-heading { font-weight: 600; color: var(--dark); display: inline-flex; align-items: center; gap: 10px; }
.pick-list { display: grid; gap: 10px; margin-bottom: 20px; }
.pick-row {
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 14px; cursor: pointer;
  margin: 0; padding: 12px 16px; background: var(--cream); border: 1.5px solid var(--line);
  border-radius: 14px; transition: .25s; font-weight: 400;
}
.pick-row:hover { border-color: var(--secondary); }
.pick-row.on { background: #fff; border-color: var(--primary); box-shadow: 0 6px 20px rgba(232, 40, 26, .1); }
.pick-row input[type=checkbox] { width: 20px; height: 20px; accent-color: var(--primary); cursor: pointer; margin: 0; }
.pick-name { display: flex; flex-direction: column; min-width: 0; }
.pick-name strong { color: var(--dark); overflow-wrap: anywhere; }
.pick-serv { display: inline-flex; align-items: center; gap: 8px; }
.pick-serv input[type=number] { width: 78px; padding: 7px 10px; text-align: center; }
.group-save { margin-top: 26px; padding-top: 20px; border-top: 2px dashed var(--cream2); }
.group-save h3 { margin: 0 0 4px; font-size: 1.1rem; }
.group-save p { margin: 0 0 12px; }


.section-split {
  display: flex; align-items: center; gap: 14px; margin: 30px 0 8px;
  font-family: "Playfair Display", serif; font-size: 1.25rem; color: var(--dark);
}
.section-split::before, .section-split::after { content: ""; flex: 1; height: 2px; background: var(--cream2); border-radius: 2px; }
.section-split i { color: var(--primary); margin-right: 6px; }
.section-split.together::before, .section-split.together::after { background: linear-gradient(90deg, var(--primary), var(--secondary)); opacity: .55; }
.recipe-card { padding: 22px 26px; }
.rc-head { display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }
.rc-num {
  width: 34px; height: 34px; flex: none; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
  font-weight: 700; color: #fff; background: linear-gradient(135deg, var(--primary), var(--secondary));
}
.rc-title { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.rc-title strong { font-family: "Playfair Display", serif; font-size: 1.15rem; color: var(--dark); overflow-wrap: anywhere; }
.together-card { border: 2px solid var(--primary); box-shadow: 0 12px 40px rgba(232, 40, 26, .12); }


.ideas { margin-top: 38px; }
.ideas-title { font-size: 1.6rem; margin: 0 0 16px; }
.title-ico.sm { width: 36px; height: 36px; font-size: .95rem; margin-right: 10px; }
.idea-block { margin-bottom: 28px; }
.idea-block h3 { margin: 0 0 2px; font-size: 1.2rem; }
.idea-block > p { margin: 0 0 14px; }
.dish-grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.dish {
  display: flex; flex-direction: column; gap: 8px; padding: 20px; background: var(--surface);
  border: 1px solid var(--line); border-radius: 18px; box-shadow: var(--shadow); transition: .3s;
}
.dish:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.dish.ready { border-top: 4px solid var(--green); }
.dish.almost { border-top: 4px solid var(--secondary); }
.dish.pick { border: 2px solid var(--primary); box-shadow: 0 12px 36px rgba(232, 40, 26, .14); }
.dish-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.dish-head strong { font-family: "Playfair Display", serif; font-size: 1.1rem; color: var(--dark); overflow-wrap: anywhere; }
.meter { height: 8px; border-radius: 8px; background: var(--cream2); overflow: hidden; }
.meter span { display: block; height: 100%; border-radius: 8px; background: linear-gradient(90deg, var(--secondary), var(--green)); }
.dish-reason { margin: 2px 0 0; font-size: .85rem; color: var(--dark); }
.dish-reason i { color: var(--primary); margin-right: 4px; }
.dish-reason.soft { color: var(--ink2); }
.dish-reason.soft i { color: var(--secondary); }
.chips { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.chips-label { font-size: .7rem; letter-spacing: 1px; text-transform: uppercase; color: var(--primary); font-weight: 600; }
.chip { padding: 3px 10px; border-radius: 50px; font-size: .78rem; background: var(--short-soft); color: var(--short); }
.chip em { font-style: normal; opacity: .75; }
.dish .btn { align-self: flex-start; margin-top: 4px; }

@media (max-width: 640px) {
  .pick-row { grid-template-columns: auto 1fr; }
  .pick-serv { grid-column: 2; }
  .row.nowrap { flex-wrap: wrap; }
  .recipe-card { padding: 18px; }
  .together-card table th:nth-child(4), .together-card table td:nth-child(4) { display: none; }
}
"""


def build_stylesheet(font_url):
    return ICON_CSS.replace("__FONT_URL__", font_url) + APP_CSS


CSS_VERSION = hashlib.sha1((ICON_CSS + APP_CSS).encode("utf-8")).hexdigest()[:10]
