"""QC talking-head clips: frame contact sheet, whisper transcript, voice metrics (rms/f0/centroid).
usage: uv run --with faster-whisper --with librosa --with soundfile qc_heads.py clip1.mp4 clip2.mp4 ... [--sheet-dir DIR]
"""
import sys, subprocess, json, os, tempfile
import numpy as np

def audio(path):
    import soundfile as sf
    wav = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg','-y','-v','error','-i',path,'-ac','1','-ar','16000',wav],check=True)
    y, sr = sf.read(wav); os.unlink(wav)
    return y.astype(np.float32), sr

def metrics(y, sr):
    import librosa
    rms = librosa.feature.rms(y=y)[0]; voiced = rms > rms.max()*0.15
    rms_db = 20*np.log10(np.mean(rms[voiced])+1e-9)
    f0 = librosa.yin(y, fmin=70, fmax=350, sr=sr)
    f0v = f0[(f0>70)&(f0<350)]
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    return rms_db, float(np.median(f0v)) if len(f0v) else 0.0, float(np.mean(cent[voiced]))

def transcribe(path, model):
    segs, _ = model.transcribe(path, word_timestamps=True, language='en')
    words = [w for s in segs for w in s.words]
    return ' '.join(w.word.strip() for w in words), (words[-1].end if words else 0)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sheet_dir = '/tmp/qc-sheets'
    if '--sheet-dir' in sys.argv: sheet_dir = sys.argv[sys.argv.index('--sheet-dir')+1]
    os.makedirs(sheet_dir, exist_ok=True)
    from faster_whisper import WhisperModel
    model = WhisperModel('base.en', compute_type='int8')
    for p in args:
        base = os.path.splitext(os.path.basename(p))[0]
        sheet = f'{sheet_dir}/{base}.jpg'
        subprocess.run(['ffmpeg','-y','-v','error','-i',p,'-vf','fps=1,scale=200:-1,tile=8x2','-frames:v','1',sheet],check=True)
        y, sr = audio(p); r, f0, c = metrics(y, sr)
        txt, last = transcribe(p, model)
        print(json.dumps({'clip':base,'rms_db':round(float(r),1),'f0_hz':round(float(f0)),'centroid_hz':round(float(c)),'last_word_end':round(float(last),2),'text':txt,'sheet':sheet}))

main()
