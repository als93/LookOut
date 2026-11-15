#!/usr/bin/env node
// Parses and samples a representative 40,600-record NIMS shard with the real source functions.
// No network requests; accepts a locally supplied shard path.
'use strict';
const fs=require('fs'),assert=require('assert'),{performance}=require('perf_hooks');
if(process.argv.length!==4)throw Error('Usage: node history_large_shard.cjs <index.html> <shard.json>');
const html=fs.readFileSync(process.argv[2],'utf8'),shard=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const a=html.indexOf('function lookoutV41SafeMediaURL('),b=html.indexOf('function lookoutV41Elapsed(',a);
assert(a>=0&&b>a);const code=html.slice(a,b);
const funcs=new Function('const LOOKOUT_V41_HOSTS=new Set(["usgs-nims-images.s3.amazonaws.com","phenocam.nau.edu"]); const location={href:"http://127.0.0.1:8878/"};'+code+'\nreturn {make:lookoutV41MakeFrames,sample:lookoutV41SampleByTime};')();
const started=performance.now(),frames=funcs.make(shard),afterLoad=performance.now(),sample=funcs.sample(frames,500),afterSample=performance.now();
assert(frames.length===shard.rows.length,'All rows retained');assert(sample.length>0&&sample.length<=500,'Sample count bounded');assert(sample[0].ms===frames[0].ms && sample.at(-1).ms===frames.at(-1).ms,'Keep both ends');
assert(frames.every(f=>f.url.startsWith(shard.baseUrl)),'All URLs are provider-approved');
console.log(`PASS ${frames.length} rows -> ${sample.length} time-spaced references (${(afterLoad-started).toFixed(0)} ms parse, ${(afterSample-afterLoad).toFixed(0)} ms sample); endpoints retained; no downloads`);
