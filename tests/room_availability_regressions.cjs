const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const source=fs.readFileSync('frontend/app.js','utf8');
function harness(){
  const elements={'#check-room':{disabled:false},'#room-availability':{textContent:''},
    '#extra-form':{elements:Object.fromEntries(Object.entries({date:'2031-10-12',start_time:'16:00',end_time:'17:00',room:'Lab 2'}).map(([key,value])=>[key,{value}]))}};
  const ctx=vm.createContext({elements,URLSearchParams,api:async()=>({room:'Lab 2',available:true,start_time:'16:00',end_time:'17:00'})});
  vm.runInContext('const $=key=>elements[key];',ctx);
  vm.runInContext(source.slice(source.indexOf('let roomCheckVersion='),source.indexOf('let supportManageVersion=')),ctx);
  return ctx;
}
test('room check validates required fields before requesting availability',async()=>{
  const ctx=harness();ctx.elements['#extra-form'].elements.date.value='';
  ctx.api=()=>{throw Error('Must not request')};await ctx.checkRoomAvailability();
  assert.match(ctx.elements['#room-availability'].textContent,/Enter a date/);
});
test('availability and occupied time slots are displayed and controls recover from failure',async()=>{
  const ctx=harness();await ctx.checkRoomAvailability();
  assert.match(ctx.elements['#room-availability'].textContent,/is available/);
  ctx.api=async()=>({room:'Lab 2',available:false,busy_slots:[{start_time:'16:00',end_time:'17:00'}]});
  await ctx.checkRoomAvailability();assert.match(ctx.elements['#room-availability'].textContent,/booked during 16:00–17:00/);
  ctx.api=async()=>{throw Error('Network unavailable')};await ctx.checkRoomAvailability();
  assert.equal(ctx.elements['#room-availability'].textContent,'Network unavailable');
  assert.equal(ctx.elements['#check-room'].disabled,false);
});
test('changing scheduling fields invalidates a pending room-check response',async()=>{
  const ctx=harness();let finish;ctx.api=()=>new Promise(resolve=>finish=resolve);
  const pending=ctx.checkRoomAvailability();
  vm.runInContext("roomCheckVersion++;elements['#room-availability'].textContent='Check again'",ctx);
  finish({room:'Lab 2',available:true,start_time:'16:00',end_time:'17:00'});await pending;
  assert.equal(ctx.elements['#room-availability'].textContent,'Check again');
});
