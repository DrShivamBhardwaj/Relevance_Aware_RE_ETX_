"""Apply an explicit, reversible energy-cost hook to the pinned RPL-Lite MRHOF."""
from pathlib import Path
import hashlib
import subprocess

PIN = 'c20b12cd2db707d6c07918f8b26cfeb52cf298ca'

def patch(contiki):
    contiki = Path(contiki).resolve()
    actual = subprocess.check_output(['git','rev-parse','HEAD'],cwd=contiki,text=True).strip()
    if actual != PIN:
        raise RuntimeError(f'Expected Contiki {PIN}, found {actual}')
    path = contiki/'os/net/routing/rpl-lite/rpl-mrhof.c'
    text = path.read_text()
    needle = '  return MIN((uint32_t)base + link_metric_to_rank(nbr_link_metric(nbr)), 0xffff);'
    replacement = '''#if STUDY_ENERGY_AWARE
  extern uint16_t study_parent_penalty(const linkaddr_t *, uint16_t);
  uint16_t metric = link_metric_to_rank(nbr_link_metric(nbr));
  return MIN((uint32_t)base + metric +
             study_parent_penalty(rpl_neighbor_get_lladdr(nbr), metric), 0xffff);
#else
'''+needle+'\n#endif'
    if 'study_parent_penalty' not in text:
        if text.count(needle) != 1:
            raise RuntimeError('Pinned MRHOF source no longer matches the audited hook')
        path.write_text(text.replace(needle,replacement))
    return {'contiki_commit':actual,'mrhof_modified_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

if __name__ == '__main__':
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('contiki');a=p.parse_args()
    print(json.dumps(patch(a.contiki),indent=2))
