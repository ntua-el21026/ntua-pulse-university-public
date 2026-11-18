import test from 'node:test';
import assert from 'node:assert/strict';
import { logoutSession } from '../src/api/logout.mjs';

function storage() {
 const values=new Map([['token','old-session'],['username','demo']]);
 return {getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,value),clear:()=>values.clear()};
}

test('logout clears the browser immediately while revocation is pending', async () => {
 const local=storage();let finish;
 const pending=new Promise(resolve=>{finish=resolve;});
 const done=logoutSession({storage:local,request:()=>pending,endpoint:'/logout'});
 try {assert.equal(local.getItem('token'),null);} finally {finish({ok:true});await done;}
});

test('completion of an older logout preserves a newer login', async () => {
 const local=storage();let finish;let headers;
 const pending=new Promise(resolve=>{finish=resolve;});
 const done=logoutSession({storage:local,request:(_url,options)=>{headers=options.headers;return pending;},endpoint:'/logout'});
 await Promise.resolve();
 local.setItem('token','new-session');
 finish({ok:true});await done;
 assert.equal(headers.Authorization,'Bearer old-session');
 assert.equal(local.getItem('token'),'new-session');
});

test('failed revocation still clears the browser without an unhandled rejection', async () => {
 const local=storage();
 await logoutSession({storage:local,request:()=>Promise.reject(new Error('offline')),endpoint:'/logout'});
 assert.equal(local.getItem('token'),null);
});
