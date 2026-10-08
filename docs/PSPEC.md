# PSPEC (Structured English) - Jalur: *858# -> 1 Transfer Pulsa

```
PSPEC 2.1 Validasi_Nomor_Tujuan
  GET nomor_tujuan
  IF format nomor_tujuan TIDAK sesuai definisi nomor_tujuan
      DISPLAY "Format nomor tujuan salah" ; ULANGI GET nomor_tujuan
  ELSE IF nomor_tujuan = msisdn_pengirim
      DISPLAY "Tidak bisa transfer ke nomor sendiri" ; ULANGI GET nomor_tujuan
  ELSE IF nomor_tujuan TIDAK ADA di D1 ATAU status_pelanggan <> aktif
      DISPLAY "Nomor tujuan tidak terdaftar" ; ULANGI GET nomor_tujuan
  ELSE
      MOVE nomor_tujuan ke nomor_valid ; LANJUT ke 2.2
  ENDIF

PSPEC 2.2 Validasi_Nominal
  GET nominal
  IF nominal bukan angka
      DISPLAY "Nominal harus berupa angka" ; ULANGI GET nominal
  ELSE IF nominal < 5000 ATAU nominal > 500000
      DISPLAY "Nominal di luar batas" ; ULANGI GET nominal
  ELSE IF pulsa pengirim di D1 < (nominal + biaya_admin)
      DISPLAY "Pulsa tidak cukup" ; ULANGI GET nominal
  ELSE
      MOVE nominal ke nominal_valid ; LANJUT ke 2.3
  ENDIF

PSPEC 2.3 Konfirmasi_Transfer
  DISPLAY ringkasan (nomor_valid, nominal_valid, biaya_admin) + "1.Ya 2.Batal"
  GET konfirmasi
  DO CASE
    CASE konfirmasi = 1  : LANJUT ke 2.4
    CASE konfirmasi = 2  : DISPLAY "Transaksi dibatalkan" ; AKHIRI sesi
    OTHERWISE            : DISPLAY "Pilihan tidak valid" ; ULANGI GET konfirmasi
  ENDCASE

PSPEC 2.4 Eksekusi_Transfer
  SUBTRACT (nominal + biaya_admin) FROM pulsa pengirim di D1
  ADD nominal TO pulsa penerima di D1
  SET id_transaksi = "TP" + nomor urut 6 digit
  WRITE data_transaksi ke D2
  SEND data_transaksi ke 6.0
  DISPLAY "Transfer pulsa berhasil" + id_transaksi ; AKHIRI sesi

PSPEC 6.0 Kirim_Notifikasi
  SEND SMS ke msisdn_pengirim : berhasil + nominal + sisa pulsa + id_transaksi
  SEND SMS ke msisdn_penerima : pulsa masuk + nominal + msisdn_pengirim + id_transaksi
```

## Pre / post condition (ringkas)

| Proses | Precondition | Postcondition |
|---|---|---|
| 2.4 Eksekusi_Transfer | nomor_valid, nominal_valid, konfirmasi = 1, pulsa pengirim >= nominal + biaya_admin | pulsa pengirim berkurang nominal + biaya, pulsa penerima bertambah nominal, 1 baris baru di D2 |
| 2.3 Konfirmasi_Transfer (Batal) | konfirmasi = 2 | D1 dan D2 tidak berubah |
