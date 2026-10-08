# Tugas Week #3 - ISP Service Analysis (*858#) + Soal Segitiga

Struktur:

```
src/ussd_858_transfer_pulsa.py   simulasi *858# -> 1 Transfer Pulsa
segitiga/segitiga_int.c          Exercise #1, input bulat
segitiga/segitiga_pecahan.c      Exercise #1, input pecahan (toleransi 1%)
docs/LAPORAN.md                  laporan (DFD, PSPEC, pemetaan ke kode)
docs/PSPEC.md                    PSPEC Structured English
docs/DATA_DICTIONARY.md          data dictionary
docs/dfd/                        DFD level 0, 1, 2 (PNG + sumber .dot)
```

## Menjalankan

*858# (Python 3):

```bash
python src/ussd_858_transfer_pulsa.py          # interaktif, ketik *858#
python src/ussd_858_transfer_pulsa.py --test   # tes otomatis
```

Data uji bawaan: pengirim 081111111111 (Rp50.000), penerima 082222222222 (Rp10.000), 083333333333 (nonaktif).

Segitiga (gcc):

```bash
gcc segitiga/segitiga_int.c -o segitiga_int && ./segitiga_int
gcc segitiga/segitiga_pecahan.c -o segitiga_pecahan -lm && ./segitiga_pecahan
```

## Anggota kelompok

_(isi nama dan NIM)_
