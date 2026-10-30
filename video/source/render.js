const {chromium}=require('playwright');const fs=require('fs'),{spawn}=require('child_process');
const s=JSON.parse(fs.readFileSync('script.json'));
const fix={7:[19.3,21.0],13:[36.0,39.05],17:[46.0,49.0],26:[67.5,71.7],20:[54.4,55.3],21:[55.3,57.0]};
const subs=s.map(([a,b,t],i)=>fix[i]?[fix[i][0],fix[i][1],t]:[a,b,t]);
(async()=>{const mode=process.argv[2];const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
 await p.goto('file://'+__dirname+'/anim.html');await p.evaluate(s=>window.setSubs(s),subs);
 const grab=async t=>Buffer.from((await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.93)},t)).split(',')[1],'base64');
 if(mode==='preview'){fs.mkdirSync('prev',{recursive:true});for(const t of process.argv.slice(3).map(Number))fs.writeFileSync(`prev/${t.toFixed(1)}.jpg`,await grab(t))}
 else{const [f0,f1,out]=[+process.argv[3],+process.argv[4],process.argv[5]];
  const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
  for(let f=f0;f<f1;f++){const buf=await grab(f/30);if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r))}
  ff.stdin.end();await new Promise(r=>ff.on('close',r))}
 await b.close()})();
