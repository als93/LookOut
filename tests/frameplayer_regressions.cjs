#!/usr/bin/env node
'use strict';
// Exercises the FramePlayer class extracted from the actual HTML rather than a reimplementation.
const fs = require('fs');
const assert = require('assert');
const file = process.argv[2];
if (!file) { console.error('Usage: node frameplayer_regressions.cjs <viewer.html>'); process.exit(2); }
const html=fs.readFileSync(file,'utf8');
const begin=html.indexOf('const TYPES=new Set('), end=html.indexOf('/* hls.js;',begin);
assert(begin!==-1&&end>begin,'Expected actual FramePlayer module');
const limitDecl=html.match(/const LIMITS = Object\.freeze\(\{[^\n]+\}\);/);
assert(limitDecl,'Expected actual LIMITS');
const FramePlayer=new Function(limitDecl[0]+'\n'+html.slice(begin,end)+'\nreturn FramePlayer;')();
let painted=[];
const context={fillRect(){},drawImage(){painted.push('draw')},set fillStyle(v) {}};
const canvas={width:300,height:200,getContext:()=>context,captureStream:()=>({getVideoTracks:()=>[{requestFrame(){}}],getTracks:()=>[{stop(){}}]})};
const delay=(ms)=>new Promise(resolve=>setTimeout(resolve,ms));
async function pauseDuringDecode(){
 painted=[];
 const states=[];const p=new FramePlayer(canvas,(i)=>states.push(i),()=>{});
 p.files=[{name:'first.jpg'},{name:'second.jpg'}];p.index=0;p.fps=8;
 const oldFrame=globalThis.requestAnimationFrame,oldCancel=globalThis.cancelAnimationFrame,oldBitmap=globalThis.createImageBitmap;
 globalThis.requestAnimationFrame=(cb)=>setTimeout(()=>cb(performance.now()+1000),0);
 globalThis.cancelAnimationFrame=(id)=>clearTimeout(id);
 globalThis.createImageBitmap=async()=>{await delay(90);return {width:300,height:200,close(){}}};
 try {p.play();await delay(25);p.pause();await delay(150);
 const ok=p.index===0&&states.length===0;console.log((ok?'PASS':'FAIL')+' pause invalidates an in-flight decode',JSON.stringify({index:p.index,states}));return ok;
 }finally{globalThis.requestAnimationFrame=oldFrame;globalThis.cancelAnimationFrame=oldCancel;globalThis.createImageBitmap=oldBitmap;}
}
async function rejectedBeforeRecorderStart(){
 const p=new FramePlayer(canvas,()=>{},()=>{});p.files=[{name:'first.jpg'}];p.draw=async()=>{throw Error('intentional decode failure')};
 const Prev=globalThis.MediaRecorder;
 class StubMediaRecorder{constructor(){this.state='inactive';}static isTypeSupported(){return true;}start(){this.state='recording';}stop(){this.state='inactive';this.onstop?.();}}
 globalThis.MediaRecorder=StubMediaRecorder;
 try{
 const result=await Promise.race([p.record().then(()=>({state:'resolved'}),e=>({state:'rejected',message:e.message})),delay(250).then(()=>({state:'timeout'}))]);
 const ok=result.state==='rejected'&&result.message==='intentional decode failure';console.log((ok?'PASS':'FAIL')+' export rejects instead of hanging when first draw fails',JSON.stringify(result));return ok;
 }finally{globalThis.MediaRecorder=Prev;}
}

async function recorderStartThrows(){
 const p=new FramePlayer(canvas,()=>{},()=>{});p.files=[{name:'first.jpg'}];p.draw=async()=>true;
 const Prev=globalThis.MediaRecorder;
 class FailingMediaRecorder{constructor(){this.state='inactive';}static isTypeSupported(){return true;}start(){throw Error('intentional recorder start failure');}}
 globalThis.MediaRecorder=FailingMediaRecorder;
 try{
 const result=await Promise.race([p.record().then(()=>({state:'resolved'}),e=>({state:'rejected',message:e.message})),delay(250).then(()=>({state:'timeout'}))]);
 const ok=result.state==='rejected'&&result.message==='intentional recorder start failure';
 console.log((ok?'PASS':'FAIL')+' export rejects if MediaRecorder.start() throws',JSON.stringify(result));return ok;
 }finally{globalThis.MediaRecorder=Prev;}
}

// An old asynchronous RAF callback must not resurrect after Pause -> Play.
async function restartDuringPendingDraw(shouldReject=false){
  const oldRAF=globalThis.requestAnimationFrame,oldCancel=globalThis.cancelAnimationFrame;
  const callbacks=new Map();let nextId=0,finishDraw=null;
  globalThis.requestAnimationFrame=fn=>{const id=++nextId;callbacks.set(id,fn);return id;};
  globalThis.cancelAnimationFrame=id=>callbacks.delete(id);
  const p=new FramePlayer(canvas,()=>{},()=>{});
  p.files=[{name:'first.jpg'},{name:'second.jpg'}];p.fps=8;
  const errors=[];p.onStatus=s=>errors.push(s);
  p.draw=()=>new Promise((resolve,reject)=>{finishDraw=shouldReject?()=>reject(Error('late old decode')):()=>resolve(true);});
  const step=()=>{const first=callbacks.entries().next().value;assert(first,'Expected scheduled animation callback');callbacks.delete(first[0]);return first[1](performance.now()+1000);};
  try{
    p.play();const oldTick=step();await Promise.resolve();
    assert(finishDraw,'Expected old playback draw to be pending');
    p.pause();p.play();await step(); // new session advances while old draw is still pending
    finishDraw();await oldTick;
    const count=callbacks.size;
    const ok=count===1&&p.playing&&!errors.length;
    console.log((ok?'PASS':'FAIL')+(shouldReject?' failed old playback request cannot stop the new session':' rapid Pause -> Play leaves only one animation loop'),JSON.stringify({scheduled:count,playing:p.playing,errors}));
    return ok;
  }finally{p.pause();globalThis.requestAnimationFrame=oldRAF;globalThis.cancelAnimationFrame=oldCancel;}
}

async function captureStreamSetupThrows(){
  const failingCanvas={...canvas,captureStream(){throw Error('intentional capture failure')}};
  let tracksStopped=0;
  const p=new FramePlayer(failingCanvas,()=>{},()=>{});
  p.files=[{name:'first.jpg'}];p.draw=async()=>true;
  const Old=globalThis.MediaRecorder;
  globalThis.MediaRecorder=class {static isTypeSupported(){return true;}};
  try{
    const first=await p.record().then(()=>({state:'resolved'}),e=>({state:'rejected',message:e.message}));
    const unlocked=!p.exporting;
    failingCanvas.captureStream=()=>({getVideoTracks:()=>[],getTracks:()=>[{stop(){tracksStopped++}}]});
    const second=await p.record().then(()=>({state:'resolved'}),e=>({state:'rejected',message:e.message}));
    const ok=first.state==='rejected'&&first.message==='intentional capture failure'&&unlocked&&second.message==='Canvas capture produced no video track'&&!p.exporting&&tracksStopped===1;
    console.log((ok?'PASS':'FAIL')+' captureStream/setup failure unlocks export and cleans up tracks',JSON.stringify({first,unlocked,second,tracksStopped,exporting:p.exporting}));
    return ok;
  }finally{globalThis.MediaRecorder=Old;}
}

(async()=>{const results=[await pauseDuringDecode(),await rejectedBeforeRecorderStart(),await recorderStartThrows(),await restartDuringPendingDraw(false),await restartDuringPendingDraw(true),await captureStreamSetupThrows()]; console.log(`${results.filter(Boolean).length}/${results.length} checks passed`);process.exit(results.every(Boolean)?0:1)})().catch(e=>{console.error(e);process.exit(2)});
