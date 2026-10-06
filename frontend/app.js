let currentUser=null, csrf='', meta={}, students=[], selected=null, refreshVersion=0, liveTimer=null, liveBusy=false;
const $=s=>document.querySelector(s);
const escapeHtml=v=>String(v??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path,method='GET',body){
  const options={method,credentials:'same-origin',headers:{'X-CSRF-Token':csrf}};
  if(body instanceof FormData)options.body=body;
  else if(body!==undefined){options.headers['Content-Type']='application/json';options.body=JSON.stringify(body)}
  const r=await fetch('/api'+path,options),j=await r.json();
  if(!r.ok){if(r.status===401)$('#login').hidden=false;throw Error(j.message+(j.errors?.[0]?.message?' — '+j.errors[0].message:''))}
  return j.data;
}
const staff=()=>['admin','teacher'].includes(currentUser?.role);
const pct=v=>v==null?'—':Number(v).toFixed(1)+'%';
function table(headers,rows){return '<div class="table-wrap"><table><thead><tr>'+headers.map(h=>'<th>'+escapeHtml(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map(c=>'<td>'+c+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'}
function option(list,key,label){return list.map(x=>`<option value="${x[key]}">${escapeHtml(x[label])}</option>`).join('')}
function filters(){return new URLSearchParams([...document.querySelectorAll('#filters select')].filter(s=>s.value).map(s=>[s.name,s.value])).toString()}
function showPage(name){window.scrollTo({top:0,behavior:'instant'});document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id===name));document.querySelectorAll('[data-page]').forEach(b=>b.classList.toggle('active',b.dataset.page===name));$('#crumb').textContent=({overview:'Overview',risk:'At-Risk Triage',top:'Top Performers',slow:'Slow Learner Support',support:'Extra Classes',assignments:'Assignments & Submissions',reports:'Progress Reports',student:'Student 360',project:'Project'})[name];if(currentUser)loadPage(name).catch(error);}
function error(e){toast(e.message);$('#error').textContent=e.message;$('#error').hidden=false}
function toast(msg){const t=$('#toast');t.textContent=msg;t.classList.add('show');clearTimeout(window.__toast);window.__toast=setTimeout(()=>t.classList.remove('show'),3500)}
function card(label,value){return `<div class="card"><div class="kpi-label">${escapeHtml(label)}</div><div class="kpi-value">${escapeHtml(value)}</div><div class="kpi-accent"></div></div>`}
function studentTable(rows){return table(['Student','Class','Score','Attendance','Trend','Status','Review'],rows.map(r=>[escapeHtml(r.name),escapeHtml(r.class_name),pct(r.current_average),pct(r.attendance),escapeHtml(r.trend_delta),`<span class="badge ${r.status==='At Risk'?'danger':r.status==='Slow Learner'||r.status==='Watch'?'watch':'good'}">${escapeHtml(r.status)}</span>`,`<button class="btn secondary" data-student="${r.id}">Open</button>`]))}
async function refresh(){
  const version=++refreshVersion;
  $('#error').hidden=true;
  const live=await api('/power-bi/live?'+filters());const summary=live.summary,rows=live.students;if(version!==refreshVersion)return;students=rows;
  window.renderDashboard({live,onStudent:id=>loadStudent(id).catch(error),onPage:showPage});
  $('#refreshed').textContent='Live demo · Auto-refresh every 10s · '+new Date(live.fetched_at).toLocaleTimeString();
  $('#risk-table').innerHTML=studentTable(rows.filter(r=>['At Risk','Watch'].includes(r.status)));
  $('#slow-table').innerHTML=studentTable(rows.filter(r=>r.status==='Slow Learner'));
  $('#top-table').innerHTML=studentTable(rows.filter(r=>r.status==='Top Performer').sort((a,b)=>b.current_average-a.current_average));
  $('#student-select').innerHTML='<option value="">Choose student</option>'+option(rows,'id','name');
  if(selected&&rows.some(r=>r.id===selected))$('#student-select').value=selected;
}
async function loadPage(name){
  if(['overview','risk','slow','top'].includes(name))return refresh();
  if(name==='support')return loadSupport();
  if(name==='assignments')return loadAssignments();
  if(name==='reports')return loadReports();
}
async function init(){
  const auth=await api('/auth/me');currentUser=auth.user;csrf=auth.csrf_token;$('#login').hidden=true;
  $('#identity').textContent=currentUser.name+' · '+currentUser.role;
  meta=await api('/metadata');
  $('#filters').innerHTML=`<div class="filter"><label>Academic year</label><select name="academic_year"><option value="">All years</option><option>2026-27</option></select></div><div class="filter"><label>Term</label><select name="term_id"><option value="">Latest term</option>${option(meta.terms,'id','name')}</select></div><div class="filter"><label>Class</label><select name="class_id"><option value="">All permitted classes</option>${option(meta.classes,'id','name')}</select></div><div class="filter"><label>Subject</label><select name="subject_id"><option value="">All subjects</option>${option(meta.subjects,'id','name')}</select></div>`;
  document.querySelectorAll('.staff-only').forEach(e=>e.hidden=!staff());document.querySelectorAll('.admin-only').forEach(e=>e.hidden=currentUser.role!=='admin');
  document.querySelectorAll('.subject-options').forEach(e=>e.innerHTML=option(meta.subjects,'id','name'));document.querySelectorAll('.class-options').forEach(e=>e.innerHTML=option(meta.classes,'id','name'));document.querySelectorAll('.teacher-options').forEach(e=>e.innerHTML=option(meta.teachers,'id','name'));document.querySelectorAll('.term-options').forEach(e=>e.innerHTML=option(meta.terms,'id','name'));
  await refresh();
  startLivePolling();
}
function startLivePolling(){
  clearTimeout(liveTimer);
  liveTimer=setTimeout(async()=>{
    if(!currentUser)return;
    if(!document.hidden&&!liveBusy&&['overview','risk','slow','top'].includes($('.view.active')?.id)){
      liveBusy=true;
      try{await refresh()}catch(e){$('#refreshed').textContent='Live refresh failed · Showing last fetched values';if(e.message==='Please sign in'){currentUser=null;clearTimeout(liveTimer);return}}
      finally{liveBusy=false}
    }
    startLivePolling();
  },10000);
}
async function loadStudent(id){
  selected=Number(id);if(!selected)return;
  const s=await api('/students/'+selected);showPage('student');$('#student-select').value=selected;
  $('#student-detail').innerHTML=`<h2>${escapeHtml(s.name)} · ${escapeHtml(s.class_name)}</h2><p>Latest term · <strong>${escapeHtml(s.status)}</strong> · ${escapeHtml(s.reason_codes.join(', '))}</p><div class="grid kpis">${card('Score',pct(s.current_average))}${card('Attendance',pct(s.attendance))}${card('Prior score',pct(s.prior_average))}${card('Change',s.trend_delta)}</div><p>Rule ${escapeHtml(s.rule_version)} · Advisor review required</p>`+table(['Term','Subject','Score','Attendance'],s.performance.map(p=>[p.term_id,escapeHtml(meta.subjects.find(x=>x.id===p.subject_id)?.name),pct(p.score),pct(p.attendance)]));
  $('#student-detail').innerHTML+='<h2 style="margin-top:24px">Support history</h2>'+table(['Topic','When','State','Attendance','Outcome'],s.support.map(r=>[escapeHtml(r.session.topic),escapeHtml(r.session.date+' '+r.session.start_time),r.session.state,r.attendance,escapeHtml(r.outcome)]))+'<h2 style="margin-top:24px">Submission history</h2>'+table(['File','Version','Status','Feedback'],s.submissions.map(r=>[escapeHtml(r.original_filename),r.version_no,r.status,escapeHtml(r.feedback)]));
  $('#performance-form').hidden=!staff();$('#parent-form').hidden=!staff();$('#report-form').hidden=!staff();$('#profile-form').hidden=!staff();$('#profile-form [name=name]').value=s.name;
  $('#parents').innerHTML='';
  if(currentUser.role!=='student'){
    const ps=await api(`/students/${selected}/parents`);
    $('#parents').innerHTML=table(['Guardian','Email','Primary','Consent','Active','Action'],ps.map(p=>[escapeHtml(p.name),escapeHtml(p.email),p.primary?'Yes':'No',p.consent?'Yes':'No',p.active?'Yes':'No',staff()?`<button class="btn secondary" data-parent="${p.id}">Edit</button> <button class="btn secondary" data-notify="${p.id}">Preview notice</button>`:'Read only']));window.parentRows=ps;
  }
  $('#parent-form [name=parent_id]').value='';
  await loadStudentReports();
}
async function loadSupport(){
  const rows=await api('/extra-classes');window.supportRows=rows;
  $('#support-table').innerHTML=table(['Session','Subject','When (India)','Room','State','Students','Action'],rows.map(r=>[escapeHtml(r.topic),escapeHtml(r.subject),escapeHtml(r.date+' '+r.start_time+'–'+r.end_time),escapeHtml(r.room),r.state,r.students.length,staff()?`<button class="btn secondary" data-support="${r.id}">Manage</button>`:'Read only']));
}
async function manageSupport(id){
  const r=window.supportRows.find(x=>x.id===Number(id));$('#support-manage').hidden=false;$('#enroll-form [name=extra_class_id]').value=r.id;
  const options=await api('/students?class_id='+r.class_id);$('#enroll-form [name=student_ids]').innerHTML=option(options,'id','name');
  $('#attendance-list').innerHTML=table(['Student','Attendance','Outcome','Action'],r.students.map(e=>[escapeHtml(options.find(s=>s.id===e.student_id)?.name),e.attendance,escapeHtml(e.outcome),`<button class="btn secondary" data-attendance="${r.id},${e.student_id}">Record</button>`]));
  $('#state-form [name=extra_class_id]').value=r.id;
}
async function loadAssignments(){
  const [as,subs]=await Promise.all([api('/assignments'),api('/submissions')]);
  $('#assignment-table').innerHTML=table(['Assignment','Class','Due','Instructions'],as.map(a=>[escapeHtml(a.title),escapeHtml(meta.classes.find(c=>c.id===a.class_id)?.name),escapeHtml(new Date(a.due_date).toLocaleString()),escapeHtml(a.instructions)]));
  $('#upload-form').hidden=currentUser.role!=='student';$('#upload-form [name=assignment_id]').innerHTML=option(as,'id','title');$('#upload-form [name=student_id]').innerHTML=option(students,'id','name');
  $('#submission-table').innerHTML=table(['Student','File','Version','Status','Feedback','Action'],subs.map(s=>[s.student_id,escapeHtml(s.original_filename),s.version_no,s.status,escapeHtml(s.feedback),(currentUser.role!=='parent'?`<a class="btn secondary" href="/api/submissions/${s.id}/download">Download</a> `:'')+(staff()?`<button class="btn secondary" data-review="${s.id}">Review</button>`:'')]));
}
async function loadReports(){
  const [rs,ns]=await Promise.all([api('/reports'),staff()?api('/notifications'):Promise.resolve([])]);
  $('#report-table').innerHTML=reportTable(rs);
  $('#notification-table').innerHTML=table(['ID','Student','Template','Message','Delivery','Action'],ns.map(n=>[n.id,n.student_id,escapeHtml(n.template),escapeHtml(n.message),n.status,staff()&&n.status==='PREVIEW'?`<button class="btn secondary" data-send="${n.id}">Send configured email</button>`:'']));
}
function reportTable(rs){return table(['Student','Term','Version','Generated','State','Action'],rs.map(r=>[r.student_id,r.term_id,r.version,escapeHtml(new Date(r.generated_at).toLocaleString()),r.released?'Released':'Draft',`<a class="btn secondary" target="_blank" rel="noopener" href="/api/reports/${r.id}/download">View / Print PDF</a> `+(staff()&&!r.released?`<button class="btn secondary" data-release="${r.id}">Release</button>`:'')]))}
async function loadStudentReports(){const rs=await api('/reports');$('#student-reports').innerHTML=reportTable(rs.filter(r=>r.student_id===selected))}
function formData(form,numbers=[]){const d=Object.fromEntries(new FormData(form));numbers.forEach(k=>d[k]=Number(d[k]));return d}
function bindForm(id,handler){$(id).addEventListener('submit',async e=>{e.preventDefault();const b=e.target.querySelector('button[type=submit]');if(b)b.disabled=true;try{await handler(e.target);toast('Saved successfully')}catch(err){error(err)}finally{if(b)b.disabled=false}})}
bindForm('#login-form',async f=>{const d=await api('/auth/login','POST',formData(f));csrf=d.csrf_token;f.reset();await init()});
bindForm('#profile-form',async f=>{await api(`/students/${selected}`,'PUT',formData(f));await loadStudent(selected)});
bindForm('#parent-form',async f=>{const d=formData(f);const pid=d.parent_id;delete d.parent_id;['primary','consent','active'].forEach(k=>d[k]=f.elements[k].checked);await api(`/students/${selected}/parents`+(pid?'/'+pid:''),pid?'PUT':'POST',d);f.reset();await loadStudent(selected)});
bindForm('#performance-form',async f=>{const d=formData(f,['subject_id','term_id','attendance']);d.score=d.score===''?null:Number(d.score);await api(`/students/${selected}/performance`,'PUT',d);await loadStudent(selected)});
bindForm('#report-form',async f=>{await api(`/students/${selected}/progress-report`,'POST',formData(f,['term_id']));await loadStudentReports()});
bindForm('#extra-form',async f=>{await api('/extra-classes','POST',formData(f,['subject_id','teacher_id','class_id']));await loadSupport()});
bindForm('#enroll-form',async f=>{await api(`/extra-classes/${f.elements.extra_class_id.value}/students`,'POST',{student_ids:[...f.elements.student_ids.selectedOptions].map(x=>Number(x.value))});await loadSupport();await manageSupport(f.elements.extra_class_id.value)});
bindForm('#attendance-form',async f=>{const d=formData(f);const eid=d.extra_class_id,sid=d.student_id;delete d.extra_class_id;delete d.student_id;await api(`/extra-classes/${eid}/students/${sid}`,'PUT',d);await loadSupport();await manageSupport(eid)});
bindForm('#state-form',async f=>{await api(`/extra-classes/${f.elements.extra_class_id.value}`,'PUT',{state:f.elements.state.value});await loadSupport()});
bindForm('#assignment-form',async f=>{const d=formData(f,['subject_id','class_id']);d.due_date=new Date(d.due_date).toISOString();await api('/assignments','POST',d);await loadAssignments()});
bindForm('#upload-form',async f=>{await api('/submissions','POST',new FormData(f));f.reset();await loadAssignments()});
bindForm('#review-form',async f=>{const d=formData(f);const id=d.submission_id;delete d.submission_id;await api(`/submissions/${id}/review`,'POST',d);await loadAssignments()});
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;try{
  if(b.dataset.page)showPage(b.dataset.page);
  if(b.dataset.student)await loadStudent(b.dataset.student);
  if(b.dataset.support)await manageSupport(b.dataset.support);
  if(b.dataset.attendance){const [eid,sid]=b.dataset.attendance.split(',');$('#attendance-form').hidden=false;$('#attendance-form [name=extra_class_id]').value=eid;$('#attendance-form [name=student_id]').value=sid;$('#attendance-form').scrollIntoView({behavior:'smooth'})}
  if(b.dataset.review){$('#review-form').hidden=false;$('#review-form [name=submission_id]').value=b.dataset.review;$('#review-form').scrollIntoView({behavior:'smooth'})}
  if(b.dataset.parent){const p=window.parentRows.find(x=>x.id===Number(b.dataset.parent));const f=$('#parent-form');f.elements.parent_id.value=p.id;for(const k of ['name','email','phone','relationship'])f.elements[k].value=p[k];for(const k of ['primary','consent','active'])f.elements[k].checked=!!p[k]}
  if(b.dataset.notify){const n=await api(`/students/${selected}/notifications`,'POST',{parent_id:Number(b.dataset.notify),template:$('#notice-template').value});toast('Preview created. Open Progress Reports to inspect it.');showPage('reports')}
  if(b.dataset.send){await api(`/notifications/${b.dataset.send}/send`,'POST');await loadReports()}
  if(b.dataset.release){await api(`/reports/${b.dataset.release}/release`,'POST');await loadReports();if(selected)await loadStudentReports()}
}catch(err){error(err)}});
$('#logout').onclick=async()=>{try{await api('/auth/logout','POST');location.reload()}catch(e){error(e)}};
$('#refresh').onclick=()=>refresh().catch(error);
$('#filters').onchange=()=>refresh().catch(error);
$('#search').oninput=()=>$('#all-students').innerHTML=studentTable(students.filter(s=>s.name.toLowerCase().includes($('#search').value.toLowerCase())||String(s.id)===$('#search').value));
$('#student-select').onchange=e=>loadStudent(e.target.value).catch(error);
$('#export').onclick=async()=>{try{const m=await api('/admin/export','POST');$('#export-result').textContent=JSON.stringify(m,null,2);toast('Power BI snapshot exported')}catch(e){error(e)}};
$('#dq').onclick=async()=>{try{$('#export-result').textContent=JSON.stringify(await api('/admin/data-quality'),null,2)}catch(e){error(e)}};
$('#audit').onclick=async()=>{try{$('#export-result').textContent=JSON.stringify(await api('/audit'),null,2)}catch(e){error(e)}};
$('#theme').onclick=()=>document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark';
init().catch(e=>{if(e.message!=='Please sign in')error(e)});

window.addEventListener('chart-term',e=>{$('#filters [name=term_id]').value=e.detail;refresh().catch(error)});
