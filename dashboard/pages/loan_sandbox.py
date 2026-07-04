# dashboard/pages/loan_sandbox.py
# Loan ECL Sandbox — interactive calculator embedded as a component

import streamlit as st
import streamlit.components.v1 as components

def show():
    st.markdown("""
    <div class='page-header'>Loan ECL Sandbox</div>
    <div class='page-subheader'>
        Input loan parameters and see Expected Credit Loss recalculate instantly
    </div>
    """, unsafe_allow_html=True)

    components.html(SANDBOX_HTML, height=820, scrolling=False)


SANDBOX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0f;--surf:#111118;--surf2:#1a1a24;--surf3:#22222f;
  --bd:rgba(255,255,255,0.06);--bd2:rgba(255,255,255,0.12);
  --ink:#f0f0f5;--muted:#9090a8;--hint:#5a5a72;
  --blue:#4f9cf9;--blue-dim:rgba(79,156,249,0.12);--blue-glow:rgba(79,156,249,0.25);
  --green:#3ecf8e;--green-dim:rgba(62,207,142,0.12);
  --amber:#f5a623;--amber-dim:rgba(245,166,35,0.12);
  --red:#f05252;--red-dim:rgba(240,82,82,0.12);
  --r:8px;--rl:14px;
}
html,body{background:var(--bg);color:var(--ink);font-family:'Outfit',sans-serif;
  padding:0 0 1rem;overflow-x:hidden}

.eyebrow{font-size:11px;font-weight:500;color:var(--hint);letter-spacing:.1em;
  text-transform:uppercase;margin-bottom:.75rem;font-family:'DM Mono',monospace}

.layout{display:grid;grid-template-columns:1fr 260px;gap:14px;padding:0 2px}

.card{background:var(--surf);border:0.5px solid var(--bd);border-radius:var(--rl);padding:1.25rem}

.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.full{grid-column:1/-1}

.field{display:flex;flex-direction:column;gap:5px}
.field label{font-size:10px;font-weight:500;color:var(--hint);letter-spacing:.1em;
  text-transform:uppercase;font-family:'DM Mono',monospace}

input[type=number],select{
  background:var(--surf2);border:0.5px solid var(--bd);border-radius:var(--r);
  padding:8px 10px;font-size:13px;color:var(--ink);font-family:'Outfit',sans-serif;
  outline:none;width:100%;transition:border-color .15s,box-shadow .15s;
  -webkit-appearance:none;appearance:none}
input[type=number]:focus,select:focus{
  border-color:var(--blue);box-shadow:0 0 0 3px var(--blue-glow)}
input[type=number]::placeholder{color:var(--hint)}
select option{background:#1a1a24}

.slider-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}
.slider-label{font-size:10px;font-weight:500;color:var(--hint);letter-spacing:.1em;
  text-transform:uppercase;font-family:'DM Mono',monospace}
.slider-val{font-size:12px;font-family:'DM Mono',monospace;color:var(--blue);font-weight:500}

input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:3px;
  background:var(--surf3);border-radius:2px;outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;
  border-radius:50%;background:var(--blue);cursor:pointer;
  box-shadow:0 0 0 3px var(--blue-glow);transition:transform .1s}
input[type=range]::-webkit-slider-thumb:active{transform:scale(1.2)}

.model-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
  margin-top:1rem;padding-top:1rem;border-top:0.5px solid var(--bd)}
.ms-item{background:var(--surf2);border-radius:var(--r);padding:9px;text-align:center}
.ms-val{font-size:14px;font-weight:500;font-family:'DM Mono',monospace;color:var(--blue)}
.ms-lbl{font-size:10px;color:var(--hint);margin-top:2px;letter-spacing:.05em;text-transform:uppercase}

.result-card{background:var(--surf);border:0.5px solid var(--bd);border-radius:var(--rl);
  padding:1.25rem;position:sticky;top:0}
.ecl-block{text-align:center;padding:1.1rem 0 .9rem;
  border-bottom:0.5px solid var(--bd);margin-bottom:1rem}
.ecl-lbl{font-size:10px;color:var(--hint);letter-spacing:.1em;text-transform:uppercase;
  margin-bottom:.3rem;font-family:'DM Mono',monospace}
.ecl-num{font-size:34px;font-weight:300;line-height:1;
  transition:color .3s;font-family:'DM Serif Display',serif}
.ecl-pct{font-size:11px;color:var(--hint);margin-top:.3rem}

.metrics{display:flex;flex-direction:column;gap:9px;margin-bottom:1rem}
.met-row{display:flex;justify-content:space-between;align-items:center}
.met-lbl{font-size:12px;color:var(--muted)}
.met-val{font-size:12px;font-family:'DM Mono',monospace;font-weight:500}

.tl{border-radius:var(--r);padding:10px 12px;
  transition:background .35s,border-color .35s;border:0.5px solid}
.tl.green{background:rgba(62,207,142,.1);border-color:rgba(62,207,142,.25)}
.tl.amber{background:rgba(245,166,35,.1);border-color:rgba(245,166,35,.25)}
.tl.red{background:rgba(240,82,82,.1);border-color:rgba(240,82,82,.25)}
.tl-top{display:flex;align-items:center;gap:6px;margin-bottom:2px}
.tl-dot{width:7px;height:7px;border-radius:50%;transition:background .35s}
.tl-lbl{font-size:12px;font-weight:500;transition:color .35s}
.tl-desc{font-size:10px;color:var(--hint)}

@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.card,.result-card{animation:fadeUp .35s ease both}
.result-card{animation-delay:.1s}
</style>
</head>
<body>

<div class="layout">
  <div class="card">
    <div class="eyebrow" style="margin-bottom:1rem">Loan parameters</div>
    <div class="form-grid">

      <div class="field">
        <label>Loan amount ($)</label>
        <input type="number" id="loanAmt" value="15000" min="1000" max="40000" step="500">
      </div>

      <div class="field">
        <label>Annual income ($)</label>
        <input type="number" id="annualInc" value="65000" min="10000" max="500000" step="1000">
      </div>

      <div class="field full">
        <div class="slider-row">
          <span class="slider-label">Interest rate</span>
          <span class="slider-val" id="rateOut">12.50%</span>
        </div>
        <input type="range" id="intRate" min="5" max="30" step="0.25" value="12.5">
      </div>

      <div class="field">
        <label>Loan grade</label>
        <select id="grade">
          <option value="A">A — Prime</option>
          <option value="B" selected>B — Near Prime</option>
          <option value="C">C — Subprime</option>
          <option value="D">D — Deep Subprime</option>
          <option value="E">E — High Risk</option>
          <option value="F">F — Very High Risk</option>
          <option value="G">G — Speculative</option>
        </select>
      </div>

      <div class="field">
        <label>Loan term</label>
        <select id="term">
          <option value="36" selected>36 months</option>
          <option value="60">60 months</option>
        </select>
      </div>

      <div class="field full">
        <div class="slider-row">
          <span class="slider-label">DTI (debt-to-income)</span>
          <span class="slider-val" id="dtiOut">18.0%</span>
        </div>
        <input type="range" id="dti" min="0" max="50" step="0.5" value="18">
      </div>

      <div class="field">
        <label>FICO score</label>
        <input type="number" id="fico" value="710" min="580" max="850" step="5">
      </div>

      <div class="field">
        <label>Employment (yrs)</label>
        <input type="number" id="empLen" value="5" min="0" max="10" step="1">
      </div>

      <div class="field full">
        <div class="slider-row">
          <span class="slider-label">Revolving utilisation</span>
          <span class="slider-val" id="revolOut">42%</span>
        </div>
        <input type="range" id="revol" min="0" max="100" step="1" value="42">
      </div>

    </div>

    <div class="model-strip">
      <div class="ms-item"><div class="ms-val">0.7115</div><div class="ms-lbl">AUC-ROC</div></div>
      <div class="ms-item"><div class="ms-val">0.4230</div><div class="ms-lbl">Gini</div></div>
      <div class="ms-item"><div class="ms-val">0.3046</div><div class="ms-lbl">KS stat</div></div>
    </div>
  </div>

  <div class="result-card">
    <div class="ecl-block">
      <div class="ecl-lbl">Expected credit loss</div>
      <div class="ecl-num" id="eclNum" style="color:var(--amber)">$0</div>
      <div class="ecl-pct" id="eclPct">— % of loan amount</div>
    </div>

    <div class="metrics">
      <div class="met-row">
        <span class="met-lbl">Probability of default</span>
        <span class="met-val" id="pdVal">—</span>
      </div>
      <div class="met-row">
        <span class="met-lbl">Loss given default</span>
        <span class="met-val" id="lgdVal">—</span>
      </div>
      <div class="met-row">
        <span class="met-lbl">Exposure at default</span>
        <span class="met-val" id="eadVal">—</span>
      </div>
      <div class="met-row">
        <span class="met-lbl">IFRS 9 stage</span>
        <span class="met-val" id="stageVal">—</span>
      </div>
    </div>

    <div class="tl green" id="tlBox">
      <div class="tl-top">
        <div class="tl-dot" id="tlDot" style="background:var(--green)"></div>
        <div class="tl-lbl" id="tlLbl" style="color:var(--green)">Green zone</div>
      </div>
      <div class="tl-desc" id="tlDesc">Basel II — model performing well</div>
    </div>
  </div>
</div>

<script>
const gPD  = {A:.04,B:.09,C:.16,D:.24,E:.34,F:.45,G:.58};
const gLGD = {A:.45,B:.50,C:.56,D:.62,E:.68,F:.73,G:.78};

function fmt(n){return '$'+Math.round(n).toLocaleString('en-US')}
function pct(n,d=1){return(n*100).toFixed(d)+'%'}

document.getElementById('intRate').addEventListener('input',function(){
  document.getElementById('rateOut').textContent=parseFloat(this.value).toFixed(2)+'%';compute();
});
document.getElementById('dti').addEventListener('input',function(){
  document.getElementById('dtiOut').textContent=parseFloat(this.value).toFixed(1)+'%';compute();
});
document.getElementById('revol').addEventListener('input',function(){
  document.getElementById('revolOut').textContent=parseInt(this.value)+'%';compute();
});
['loanAmt','annualInc','grade','term','fico','empLen'].forEach(function(id){
  var el=document.getElementById(id);
  if(el){el.addEventListener('input',compute);el.addEventListener('change',compute);}
});

function compute(){
  var loan  = parseFloat(document.getElementById('loanAmt').value)||15000;
  var inc   = parseFloat(document.getElementById('annualInc').value)||65000;
  var rate  = parseFloat(document.getElementById('intRate').value)||12.5;
  var grade = document.getElementById('grade').value;
  var term  = parseInt(document.getElementById('term').value)||36;
  var dti   = parseFloat(document.getElementById('dti').value)||18;
  var fico  = parseFloat(document.getElementById('fico').value)||710;
  var emp   = parseFloat(document.getElementById('empLen').value)||5;
  var revol = parseFloat(document.getElementById('revol').value)||42;

  var pd = gPD[grade]||.09;
  if(rate>20) pd+=.08; else if(rate>15) pd+=.04; else if(rate<8) pd-=.03;
  if(dti>35)  pd+=.06; else if(dti>25)  pd+=.03; else if(dti<10) pd-=.02;
  if(fico>780) pd-=.06; else if(fico>720) pd-=.03; else if(fico<620) pd+=.08;
  if(emp<1)   pd+=.03; else if(emp>=7)  pd-=.02;
  if(revol>75) pd+=.04; else if(revol<20) pd-=.01;
  if((loan/12)/(inc/12)>.3) pd+=.05;
  if(term===60) pd+=.03;
  pd = Math.min(Math.max(pd,.02),.85);

  var lgd = gLGD[grade]||.50;
  if(rate>20)  lgd+=.04;
  if(fico>760) lgd-=.05; else if(fico<640) lgd+=.04;
  lgd = Math.min(Math.max(lgd,.2),.95);

  var r = rate/100/12;
  var elapsed = Math.round(term*.4);
  var ead;
  if(r>0){
    var num = Math.pow(1+r,term)-Math.pow(1+r,elapsed);
    var den = Math.pow(1+r,term)-1;
    ead = den>0 ? loan*Math.max(num/den,0) : loan*.6;
  } else { ead=loan*.6; }
  ead = Math.max(ead,loan*.05);

  var ecl     = pd*lgd*ead;
  var eclPct  = ecl/loan;

  var stage,stageColor;
  if(pd<.1)      { stage='Stage 1'; stageColor='var(--green)'; }
  else if(pd<.3) { stage='Stage 2'; stageColor='var(--amber)'; }
  else           { stage='Stage 3'; stageColor='var(--red)';   }

  var eclColor = 'var(--green)';
  if(eclPct>.15)     eclColor='var(--red)';
  else if(eclPct>.08) eclColor='var(--amber)';

  document.getElementById('eclNum').textContent   = fmt(ecl);
  document.getElementById('eclNum').style.color   = eclColor;
  document.getElementById('eclPct').textContent   = pct(eclPct)+' of loan amount';
  var pdEl = document.getElementById('pdVal');
  pdEl.textContent = pct(pd);
  pdEl.style.color = pd>.3?'var(--red)':pd>.1?'var(--amber)':'var(--green)';
  document.getElementById('lgdVal').textContent   = pct(lgd);
  document.getElementById('eadVal').textContent   = fmt(ead);
  var stEl = document.getElementById('stageVal');
  stEl.textContent = stage; stEl.style.color = stageColor;

  var dev = Math.abs(pd-.2185)/.2185*100;
  var tlBox  = document.getElementById('tlBox');
  var tlDot  = document.getElementById('tlDot');
  var tlLbl  = document.getElementById('tlLbl');
  var tlDesc = document.getElementById('tlDesc');
  if(dev<20){
    tlBox.className='tl green';
    tlDot.style.background='var(--green)';tlLbl.style.color='var(--green)';
    tlLbl.textContent='Green zone';tlDesc.textContent='Basel II — model performing well';
  } else if(dev<40){
    tlBox.className='tl amber';
    tlDot.style.background='var(--amber)';tlLbl.style.color='var(--amber)';
    tlLbl.textContent='Amber zone';tlDesc.textContent='Basel II — monitor closely';
  } else {
    tlBox.className='tl red';
    tlDot.style.background='var(--red)';tlLbl.style.color='var(--red)';
    tlLbl.textContent='Red zone';tlDesc.textContent='Basel II — recalibration required';
  }
}
compute();
</script>
</body>
</html>
"""