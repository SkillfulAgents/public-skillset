import { useCallback, useLayoutEffect, useRef, useState } from 'react';

/** Measure a container's width so SVG charts can be responsive without distortion. */
export function useWidth(initial = 640) {
  const ref = useRef(null);
  const [width, setWidth] = useState(initial);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const set = () => setWidth(Math.max(220, Math.round(el.getBoundingClientRect().width)));
    set();
    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', set);
      return () => window.removeEventListener('resize', set);
    }
    const ro = new ResizeObserver(set);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  return [ref, width];
}

/** Sortable table state. */
export function useSort(defaultKey, defaultDir = 'desc') {
  const [key, setKey] = useState(defaultKey);
  const [dir, setDir] = useState(defaultDir);

  const toggle = useCallback(
    (k, preferred = 'desc') => {
      setKey((prev) => {
        if (prev === k) {
          setDir((d) => (d === 'asc' ? 'desc' : 'asc'));
          return prev;
        }
        setDir(preferred);
        return k;
      });
    },
    [],
  );

  const sorter = useCallback(
    (rows, accessors = {}) => {
      const get = accessors[key] || ((r) => r[key]);
      const out = [...rows];
      out.sort((a, b) => {
        const av = get(a);
        const bv = get(b);
        const an = av === null || av === undefined || av === '';
        const bn = bv === null || bv === undefined || bv === '';
        if (an && bn) return 0;
        if (an) return 1; // nulls always last
        if (bn) return -1;
        let cmp;
        if (typeof av === 'number' && typeof bv === 'number') cmp = av - bv;
        else cmp = String(av).localeCompare(String(bv), 'en', { numeric: true });
        return dir === 'asc' ? cmp : -cmp;
      });
      return out;
    },
    [key, dir],
  );

  return { key, dir, toggle, sorter };
}

/** Rolling mean, null-safe, window w. */
export function rollingMean(values, w = 7) {
  const out = [];
  let sum = 0;
  const q = [];
  for (let i = 0; i < values.length; i++) {
    const v = Number(values[i]) || 0;
    q.push(v);
    sum += v;
    if (q.length > w) sum -= q.shift();
    out.push(i >= w - 1 ? sum / q.length : null);
  }
  return out;
}
