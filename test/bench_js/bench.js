
import fs from 'fs';
import {PNG} from 'pngjs';
import Delatin from './index.js';


const {width, height, data} = PNG.sync.read(fs.readFileSync('../data/fuji.png'));

const heights = new Float64Array(width * height);

for (let i = 0; i < heights.length; i++) {
    const r = data[4 * i];
    const g = data[4 * i + 1];
    const b = data[4 * i + 2];
    heights[i] = Math.round(((r * 256 * 256 + g * 256.0 + b) / 10.0 - 10000.0) * 10) / 10;
}

// Re-instantiating the class every time, so that I'm testing the total time to
// get **one** mesh resolution level. On my computer, instantiation only takes
// 18ms.
console.time('mesh (max_error=30m)');
let tin = new Delatin(heights, width, height);
tin.run(30);
console.timeEnd('mesh (max_error=30m)');

console.log(`vertices: ${tin.coords.length >> 1}`);
console.log(`triangles: ${tin.triangles.length / 3}\n`);

for (var i = 0; i < 21; i++) {
  console.time(`mesh (max_error=${i}m)`);
  tin = new Delatin(heights, width, height);
  tin.run(i);
  console.timeEnd(`mesh (max_error=${i}m)`);
}
