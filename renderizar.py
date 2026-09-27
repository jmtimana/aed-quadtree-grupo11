"""Renderiza cada escena por separado y concatena. No necesita auxiliares."""
from pathlib import Path
import subprocess as sp
import argparse, sys
BASE=Path(__file__).resolve().parent
SCENES=['S01Concepto','S02Insercion','S03Eliminacion','S04Recorrido','S05Bordes','S06PeorCaso','S07Complejidad']
def run(cmd): sp.run(cmd,check=True,cwd=BASE)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--preview',action='store_true'); ap.add_argument('--scene',choices=SCENES); ap.add_argument('--solo-unir',action='store_true'); args=ap.parse_args()
    out=BASE.parent/'escenas'; out.mkdir(exist_ok=True)
    selected=[] if args.solo_unir else [args.scene] if args.scene else SCENES
    resolution='854,480' if args.preview else '1920,1080'
    for scene in selected:
        run([sys.executable,'-m','manim','--disable_caching','--fps','30','-r',resolution,'--media_dir',str(BASE/'media'),'-o',scene,'main.py',scene])
        source=BASE/'media'/'videos'/'main'/('480p30' if args.preview else '1080p30')/f'{scene}.mp4'
        import shutil
        shutil.copy2(source,out/f'{scene}.mp4')
    if not args.scene:
        manifest=out/'concat.txt'; manifest.write_text('\n'.join(f"file '{(out/(s+'.mp4')).as_posix()}'" for s in SCENES))
        video=BASE.parent/'video'; video.mkdir(exist_ok=True)
        run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(manifest),'-an','-sn','-c:v','copy','-movflags','+faststart',str(video/'quadtree.mp4')])
        print(video/'quadtree.mp4')
if __name__=='__main__': main()
