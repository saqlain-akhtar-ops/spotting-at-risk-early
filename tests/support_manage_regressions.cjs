const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const source=fs.readFileSync('frontend/app.js','utf8');
function harness(){
  const elements={};
  const heading={};
  for(const key of ['#support-manage','#attendance-form','#enroll-form','#state-form','#attendance-list','#enroll-form [name=extra_class_id]','#enroll-form [name=student_ids]','#state-form [name=extra_class_id]','#state-form [name=state]'])elements[key]={hidden:true,value:'',querySelector:()=>heading,scrollIntoView(){this.scrolled=true}};
  const context=vm.createContext({window:{supportRows:[{id:1,class_id:1,topic:'Math',state:'CANCELLED',students:[]},{id:2,class_id:2,topic:'Science',state:'SCHEDULED',students:[]}]},elements,heading,api:async()=>[],option:()=>'',escapeHtml:x=>x,table:()=>''});
  vm.runInContext('const $=key=>elements[key];',context);
  vm.runInContext(source.slice(source.indexOf('let supportManageVersion='),source.indexOf('async function loadAssignments(')),context);
  return context;
}
test('Manage reveals and scrolls to the selected class before its students load',async()=>{
  const ctx=harness();let finish;ctx.api=()=>new Promise(resolve=>finish=resolve);
  const pending=ctx.manageSupport(1);
  assert.equal(ctx.elements['#support-manage'].hidden,false);
  assert.equal(ctx.elements['#support-manage'].scrolled,true);
  assert.equal(ctx.heading.textContent,'Manage class — Math');
  assert.equal(ctx.elements['#attendance-list'].textContent,'Loading students…');
  assert.equal(ctx.elements['#enroll-form'].hidden,true);
  finish([]);await pending;
  assert.equal(ctx.elements['#state-form [name=state]'].value,'CANCELLED');
});
test('an older class request cannot overwrite a newer selection',async()=>{
  const ctx=harness();let finish;ctx.api=()=>new Promise(resolve=>finish=resolve);
  const first=ctx.manageSupport(1);ctx.api=async()=>[];await ctx.manageSupport(2);finish([]);await first;
  assert.equal(ctx.elements['#enroll-form [name=extra_class_id]'].value,2);
  assert.equal(ctx.elements['#state-form [name=state]'].value,'SCHEDULED');
});
test('failed loading is visible in the management panel and stale controls remain hidden',async()=>{
  const ctx=harness();ctx.api=async()=>{throw Error('Connection unavailable')};
  await assert.rejects(ctx.manageSupport(1),/Connection unavailable/);
  assert.equal(ctx.elements['#attendance-list'].textContent,'Connection unavailable');
  assert.equal(ctx.elements['#enroll-form'].hidden,true);
});
test('a missing class returns a clear error',async()=>{
  const ctx=harness();await assert.rejects(ctx.manageSupport(99),/no longer available/);
});
