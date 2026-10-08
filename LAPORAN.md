# Laporan Tugas Week #3 - ISP Service Analysis (*858#)

**Mata Kuliah:** CAK3BAB3  
**Fakultas:** Informatika, Telkom University  

### Kelompok

| Nama | NIM |
|---|---|
| Husnul Khotimah | 103012430019 |
| Raissa Putri Athaya | 103012400255 |
| Baliana Daniswara | 103012400363 |
| Surya Mirfattul Jannah | 103012400372 |

---
## 1. Soal Segitiga (Exercise #1)

Kode: `segitiga/segitiga_int.c` (input bilangan bulat) dan `segitiga/segitiga_pecahan.c` (pecahan, toleransi 1%).
PSPEC ada di komentar awal tiap file.

Asumsi versi pecahan:
- Dua sisi dianggap sama jika `|x - y| <= 1% x sisi yang lebih besar`.
- Siku-siku jika `|c^2 - (a^2 + b^2)| <= 1% x c^2`.
- Segitiga siku-siku sama kaki dapat terjadi (mis. 1, 1, 1.4142), sehingga kedua jenis ditampilkan.

Hasil uji:

| Input | Versi | Hasil |
|---|---|---|
| 3 4 5 | bulat | SIKU-SIKU |
| 5 5 5 | bulat | SAMA SISI |
| 5 5 8 | bulat | SAMA KAKI |
| 4 6 7 | bulat | BEBAS |
| 1 2 3 | bulat | bukan segitiga |
| 0 4 5 | bulat | bukan segitiga |
| 1 1 1.4142 | pecahan | SAMA KAKI + SIKU-SIKU |
| 5 5.04 5.02 | pecahan | SAMA SISI |
| 5 5.2 8 | pecahan | BEBAS |

## 2. Analisis layanan *858# (Telkomsel)

Menu utama: 1.Transfer Pulsa, 2.Minta Pulsa, 3.Auto TP, 4.Delete Auto TP, 5.List Auto TP, 6.Cek Kupon Undian TP.
Jalur yang dipilih untuk PSPEC dan kode: **\*858# -> 1 Transfer Pulsa -> nomor tujuan -> nominal -> konfirmasi -> eksekusi**.

### 2a. DFD

![DFD Level 0](dfd/level0.png)

![DFD Level 1](dfd/level1.png)

![DFD Level 2 - Proses 2.0](dfd/level2_proses2.png)

Catatan: proses 3.0, 4.0, 5.0 tidak didekomposisi karena di luar jalur yang dipilih.
Proses 6.0 (Kirim Notifikasi) dipanggil oleh 2.0 dan 3.0.

### 2b. PSPEC

Lihat [PSPEC.md](PSPEC.md). Data dictionary: [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

### 2c. Kode

`src/ussd_858_transfer_pulsa.py` (Python 3, tanpa library tambahan).

Pemetaan DFD ke kode (sesuai materi "From Design to Implementation"):

| Elemen DFD | Di kode |
|---|---|
| 2.1 Validasi_Nomor_Tujuan | `validasi_nomor()` |
| 2.2 Validasi_Nominal | `validasi_nominal()` |
| 2.3 Konfirmasi_Transfer | state `KONFIRMASI` di `USSDSession.input()` |
| 2.4 Eksekusi_Transfer | `eksekusi_transfer()` |
| 6.0 Kirim_Notifikasi | `kirim_notifikasi()` |
| 1.0 Tampilkan Menu Utama | `USSDSession.start()` dan state `MAIN` |
| D1 Data_Pelanggan | `DataStore.subscribers` |
| D2 Log_Transaksi | `DataStore.transactions` |
| Aliran data (panah) | parameter dan nilai kembali fungsi |
| PSPEC | alur if/else di dalam fungsi |

Asumsi aturan bisnis (bukan aturan resmi operator): nominal Rp5.000 - Rp500.000, biaya admin Rp1.000.
Menu 2 sampai 6 hanya menampilkan "belum tersedia".
