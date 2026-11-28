// Run with one browser_eval on the Gamut app home page. avatars.py js fills IDS (in-scope agent ids) and KIND.
// Clones each agent's avatar (KIND "avatars") or member stack (KIND "members") into a fixed full-screen grid on white,
// so two screenshots (white, then black) let avatars.py recover the images with their transparency.
// Returns the agent ids in grid order, the order avatars.py crops them in.
const IDS = __IDS__, KIND = __KIND__;
const A = KIND === 'avatars', COLS = A ? 7 : 4, W = A ? 120 : 280, H = A ? 120 : 80, SCALE = A ? 3 : 2.5;
document.getElementById('wr-capture')?.remove();
const grid = document.createElement('div');
grid.id = 'wr-capture';
Object.assign(grid.style, {position: 'fixed', inset: '0', zIndex: '2147483647', background: '#fff', padding: '20px',
  margin: '0', display: 'grid', gridTemplateColumns: `repeat(${COLS}, ${W}px)`, gridAutoRows: `${H}px`, gap: '0',
  alignContent: 'start', boxSizing: 'border-box'});
const order = [];
for (const slug of IDS) {
  const item = document.querySelector(`[data-testid="agent-item-${slug.split('-').pop()}"]`);
  const li = item && item.closest('li');
  if (!li) continue;
  let el = null;
  if (A) el = li.querySelector('button[class*="group/avatar"] span.relative.block');
  else {
    const imgs = [...li.querySelectorAll('img')];
    el = imgs.length ? imgs[0].parentElement : null;
    while (el && !imgs.every(i => el.contains(i))) el = el.parentElement;
  }
  if (!el) continue;
  const cell = document.createElement('div');
  Object.assign(cell.style, {width: W + 'px', height: H + 'px', display: 'flex', alignItems: 'center',
    justifyContent: A ? 'center' : 'flex-start', overflow: 'visible'});
  const copy = el.cloneNode(true);
  Object.assign(copy.style, {transform: `scale(${SCALE})`, transformOrigin: A ? 'center' : 'left center', flex: 'none', margin: '0'});
  cell.appendChild(copy);
  grid.appendChild(cell);
  order.push(slug);
}
document.body.appendChild(grid);
return JSON.stringify(order);
