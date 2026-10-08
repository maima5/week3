# Data Dictionary - Layanan *858# (jalur Transfer Pulsa)

Notasi: `=` terdiri dari, `+` dan, `[ a | b ]` pilih salah satu, `{ x }` pengulangan,
`n{ x }m` pengulangan minimal n maksimal m, `( x )` opsional, `* ... *` komentar.

## Aliran data (flow)

| Nama | Definisi | Keterangan |
|---|---|---|
| kode_ussd | `"*858#"` | Dikirim pelanggan dari dialer |
| menu_utama | `"1.Transfer Pulsa" + "2.Minta Pulsa" + "3.Auto TP" + "4.Delete Auto TP" + "5.List Auto TP" + "6.Cek Kupon Undian TP"` | Tampilan layar USSD |
| pilihan_menu | `[ 1 \| 2 \| 3 \| 4 \| 5 \| 6 ]` | Angka satu digit |
| nomor_tujuan | `[ "08" + 8{digit}11 \| "628" + 8{digit}11 ]` | Dinormalisasi ke format 08xx. Tidak boleh sama dengan nomor pengirim |
| nominal | `integer` | *5000 <= nominal <= 500000* (asumsi) |
| konfirmasi | `[ 1 \| 2 ]` | 1 = Ya, 2 = Batal |
| pesan_error | `{ karakter }` | Mis. "Format nomor tujuan salah." |
| hasil_transfer | `status + id_transaksi` | status = [ berhasil \| dibatalkan ] |
| data_transaksi | `id_transaksi + msisdn_pengirim + msisdn_penerima + nominal + biaya_admin + waktu` | Dari 2.4 ke D2 dan ke proses 6.0 |
| notifikasi_sms | `msisdn_tujuan + isi_pesan` | Satu untuk pengirim, satu untuk penerima |

## Elemen data

| Nama | Definisi |
|---|---|
| digit | `[ 0-9 ]` |
| msisdn | `[ "08" + 8{digit}11 ]` *(bentuk normal)* |
| id_transaksi | `"TP" + 6{digit}6` |
| biaya_admin | `integer` *(1000, asumsi)* |
| waktu | `tanggal + jam` *(ISO 8601, detik)* |
| pulsa | `integer >= 0` |
| status_pelanggan | `[ aktif \| nonaktif ]` |

## Data store

| Store | Definisi | Implementasi di kode |
|---|---|---|
| D1 Data_Pelanggan | `{ msisdn + pulsa + status_pelanggan }` | `DataStore.subscribers` (dict) |
| D2 Log_Transaksi | `{ id_transaksi + msisdn_pengirim + msisdn_penerima + nominal + biaya_admin + waktu }` | `DataStore.transactions` (list) |
| D3 Data_AutoTP | `{ msisdn_pengirim + msisdn_tujuan + nominal + jadwal }` | Belum diimplementasi (menu 3/4/5) |

## Bentuk database (jika D1 dan D2 disimpan di DBMS)

```sql
CREATE TABLE pelanggan (
    msisdn  VARCHAR(13) PRIMARY KEY,
    pulsa   INT NOT NULL CHECK (pulsa >= 0),
    status  ENUM('aktif','nonaktif') NOT NULL
);

CREATE TABLE log_transaksi (
    id_transaksi VARCHAR(8) PRIMARY KEY,
    pengirim     VARCHAR(13) NOT NULL REFERENCES pelanggan(msisdn),
    penerima     VARCHAR(13) NOT NULL REFERENCES pelanggan(msisdn),
    nominal      INT NOT NULL,
    biaya_admin  INT NOT NULL,
    waktu        DATETIME NOT NULL
);
```
