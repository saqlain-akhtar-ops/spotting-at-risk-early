const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const source=fs.readFileSync('frontend/app.js','utf8');
function harness(){
  const elements={};
  for(const name of ['login','login-error','error','identity','filters','upload-limit'])elements['#'+name]={id:name,hidden:name!=='login',textContent:'',focus(){this.focused=true}};
  const ctx=vm.createContext({elements,currentUser:{role:'admin'},csrf:'prior',liveTimer:1,liveBusy:false,AbortController,URLSearchParams,FormData,
    setTimeout:()=>1,clearTimeout(){ctx.cleared=true},document:{querySelectorAll:()=>[]},toast(){},option:()=>'',staff:()=>true,startLivePolling(){ctx.polling=true},meta:{},
    refresh:async()=>{},fetch:async()=>({ok:true,json:async()=>({data:{}})})});
  vm.runInContext('const $=selector=>elements[selector];',ctx);
  vm.runInContext(source.slice(source.indexOf('async function api('),source.indexOf('const staff=')),ctx);
  vm.runInContext(source.slice(source.indexOf('function error('),source.indexOf('function toast(')),ctx);
  vm.runInContext(source.slice(source.indexOf('async function init('),source.indexOf('function startLivePolling(')),ctx);
  return ctx;
}
test('failed login feedback is visible and focused inside the sign-in screen',()=>{
  const ctx=harness();ctx.error(new Error('Invalid email or password'));
  assert.equal(ctx.elements['#login-error'].hidden,false);
  assert.equal(ctx.elements['#login-error'].focused,true);
  assert.match(ctx.elements['#login-error'].textContent,/Invalid email/);
});
test('rejected authentication clears stale session state and permits retry',async()=>{
  const ctx=harness();ctx.elements['#login'].hidden=true;
  ctx.fetch=async()=>({ok:false,status:401,json:async()=>({message:'Invalid email or password'})});
  await assert.rejects(ctx.api('/auth/login','POST',{email:'demo@example.test',password:'wrong'}),/Invalid email/);
  assert.equal(ctx.currentUser,null);assert.equal(ctx.csrf,'');assert.equal(ctx.elements['#login'].hidden,false);assert.equal(ctx.cleared,true);
});
test('proxy HTML failures produce useful error feedback and release the timer',async()=>{
  const ctx=harness();ctx.fetch=async()=>({ok:false,status:502,json:async()=>{throw new SyntaxError('HTML')}});
  await assert.rejects(ctx.api('/auth/login','POST',{}),/unreadable response/);assert.equal(ctx.cleared,true);
});
test('timeouts permit retry',async()=>{
  const ctx=harness();ctx.fetch=async()=>{const err=new Error('abort');err.name='AbortError';throw err};
  await assert.rejects(ctx.api('/auth/login','POST',{}),/timed out/);assert.equal(ctx.cleared,true);
});
test('login stays visible when dashboard initialization fails',async()=>{
  const ctx=harness();ctx.api=async path=>path==='/auth/me'?{user:{role:'admin',name:'Demo'},csrf_token:'new'}:{subjects:[],classes:[],terms:[],teachers:[],upload_max_bytes:3145728};
  ctx.refresh=async()=>{throw new Error('Database unavailable')};
  await assert.rejects(ctx.init(),/Database unavailable/);assert.equal(ctx.elements['#login'].hidden,false);assert.notEqual(ctx.polling,true);
});
test('successful initialization loads dashboard before dismissing login',async()=>{
  const ctx=harness();ctx.api=async path=>path==='/auth/me'?{user:{role:'admin',name:'Demo'},csrf_token:'new'}:{subjects:[],classes:[],terms:[],teachers:[],upload_max_bytes:3145728};
  ctx.refresh=async()=>{assert.equal(ctx.elements['#login'].hidden,false);ctx.loaded=true};
  await ctx.init();assert.equal(ctx.loaded,true);assert.equal(ctx.elements['#login'].hidden,true);assert.equal(ctx.polling,true);
});
