"""
Simulasi layanan USSD *858#  ->  menu 1 (Transfer Pulsa) sampai eksekusi.

Jalur: *858# -> 1 -> input nomor tujuan -> input nominal -> konfirmasi -> eksekusi

Struktur mengikuti DFD level 2 proses 2.0 (Transfer Pulsa) dan PSPEC-nya:
  2.1 Validasi_Nomor_Tujuan
  2.2 Validasi_Nominal
  2.3 Konfirmasi_Transfer
  2.4 Eksekusi_Transfer
  6.0 Kirim_Notifikasi (proses level 1, dipanggil oleh 2.4)

Jalankan:  python ussd_858_transfer_pulsa.py
Tes     :  python ussd_858_transfer_pulsa.py --test
"""
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime

# ---- Aturan bisnis (ASUMSI, silakan sesuaikan dengan aturan operator) ----
MIN_TRANSFER = 5_000
MAX_TRANSFER = 500_000
ADMIN_FEE = 1_000
MIN_SISA_PULSA = 0
NOMOR_REGEX = re.compile(r"^(08\d{8,11}|628\d{8,11})$")

MAIN_MENU = (
    "1.Transfer Pulsa\n2.Minta Pulsa\n3.Auto TP\n"
    "4.Delete Auto TP\n5.List Auto TP\n6.Cek Kupon Undian TP"
)


# ---- Data store (simulasi) ----
@dataclass
class Subscriber:
    msisdn: str
    pulsa: int
    aktif: bool = True


@dataclass
class DataStore:
    subscribers: dict = field(default_factory=dict)  # D1 Data_Pelanggan
    transactions: list = field(default_factory=list)  # D2 Log_Transaksi
    notifications: list = field(default_factory=list)  # keluaran ke SMS gateway

    def add(self, msisdn, pulsa, aktif=True):
        self.subscribers[msisdn] = Subscriber(msisdn, pulsa, aktif)


def normalisasi(nomor: str) -> str:
    """628xxx -> 08xxx supaya format seragam."""
    return "0" + nomor[2:] if nomor.startswith("62") else nomor


# ---- Proses-proses (PSPEC) ----
def validasi_nomor(store: DataStore, pengirim: str, tujuan: str):
    """2.1 Return (ok, pesan, nomor_ternormalisasi)."""
    if not NOMOR_REGEX.match(tujuan):
        return False, "Format nomor tujuan salah.", None
    tujuan = normalisasi(tujuan)
    if tujuan == pengirim:
        return False, "Tidak bisa transfer ke nomor sendiri.", None
    sub = store.subscribers.get(tujuan)
    if sub is None or not sub.aktif:
        return False, "Nomor tujuan tidak terdaftar/tidak aktif.", None
    return True, "", tujuan


def validasi_nominal(store: DataStore, pengirim: str, teks: str):
    """2.2 Return (ok, pesan, nominal)."""
    if not teks.isdigit():
        return False, "Nominal harus berupa angka.", None
    nominal = int(teks)
    if nominal < MIN_TRANSFER or nominal > MAX_TRANSFER:
        return False, f"Nominal harus Rp{MIN_TRANSFER:,}-Rp{MAX_TRANSFER:,}.", None
    saldo = store.subscribers[pengirim].pulsa
    if saldo - (nominal + ADMIN_FEE) < MIN_SISA_PULSA:
        return False, "Pulsa tidak cukup.", None
    return True, "", nominal


def eksekusi_transfer(store: DataStore, pengirim: str, tujuan: str, nominal: int):
    """2.4 Debit pengirim, kredit penerima, catat log. Return id transaksi."""
    store.subscribers[pengirim].pulsa -= nominal + ADMIN_FEE
    store.subscribers[tujuan].pulsa += nominal
    trx_id = f"TP{len(store.transactions) + 1:06d}"
    store.transactions.append(
        {"id": trx_id, "dari": pengirim, "ke": tujuan, "nominal": nominal,
         "fee": ADMIN_FEE, "waktu": datetime.now().isoformat(timespec="seconds")}
    )
    return trx_id


def kirim_notifikasi(store: DataStore, pengirim, tujuan, nominal, trx_id):
    """Proses 6.0: simulasi SMS ke pengirim dan penerima."""
    sisa = store.subscribers[pengirim].pulsa
    store.notifications.append((pengirim,
        f"Transfer pulsa Rp{nominal:,} ke {tujuan} berhasil. Sisa pulsa Rp{sisa:,}. Ref {trx_id}"))
    store.notifications.append((tujuan,
        f"Anda menerima pulsa Rp{nominal:,} dari {pengirim}. Ref {trx_id}"))


# ---- Sesi USSD (state machine) ----
class USSDSession:
    """Tiap input pengguna -> (teks_layar, sesi_selesai)."""

    def __init__(self, store: DataStore, msisdn: str):
        self.store, self.msisdn = store, msisdn
        self.state = "MAIN"
        self.tujuan = None
        self.nominal = None

    def start(self):
        return MAIN_MENU, False

    def input(self, teks: str):
        teks = teks.strip()
        s = self.state

        if s == "MAIN":
            if teks == "1":
                self.state = "INPUT_NOMOR"
                return "Masukkan nomor tujuan:", False
            if teks in {"2", "3", "4", "5", "6"}:
                return "Menu belum tersedia pada simulasi ini.", True
            return "Pilihan tidak valid.\n" + MAIN_MENU, False

        if s == "INPUT_NOMOR":
            ok, msg, nomor = validasi_nomor(self.store, self.msisdn, teks)
            if not ok:
                return msg + "\nMasukkan nomor tujuan:", False
            self.tujuan, self.state = nomor, "INPUT_NOMINAL"
            return "Masukkan nominal transfer:", False

        if s == "INPUT_NOMINAL":
            ok, msg, nominal = validasi_nominal(self.store, self.msisdn, teks)
            if not ok:
                return msg + "\nMasukkan nominal transfer:", False
            self.nominal, self.state = nominal, "KONFIRMASI"
            return (f"Transfer Rp{nominal:,} ke {self.tujuan}\n"
                    f"Biaya admin Rp{ADMIN_FEE:,}\n1.Ya\n2.Batal"), False

        if s == "KONFIRMASI":
            if teks == "1":
                trx = eksekusi_transfer(self.store, self.msisdn, self.tujuan, self.nominal)
                kirim_notifikasi(self.store, self.msisdn, self.tujuan, self.nominal, trx)
                self.state = "SELESAI"
                return f"Transfer pulsa berhasil. Ref {trx}", True
            if teks == "2":
                self.state = "SELESAI"
                return "Transaksi dibatalkan.", True
            return "Pilihan tidak valid.\n1.Ya\n2.Batal", False

        return "Sesi berakhir.", True


# ---- CLI ----
def run_cli():
    store = DataStore()
    store.add("081111111111", 50_000)
    store.add("082222222222", 10_000)
    store.add("083333333333", 0, aktif=False)
    me = "081111111111"
    print(f"Simulasi HP {me} (pulsa Rp{store.subscribers[me].pulsa:,}). Ketik *858# lalu Enter.")
    while input("> ").strip() != "*858#":
        print("Kode USSD tidak dikenal.")
    sesi = USSDSession(store, me)
    layar, selesai = sesi.start()
    while True:
        print("\n" + layar)
        if selesai:
            break
        layar, selesai = sesi.input(input("[input] "))
    for tujuan, sms in store.notifications:
        print(f"[SMS ke {tujuan}] {sms}")


# ---- Tes sederhana ----
def run_tests():
    def baru():
        st = DataStore()
        st.add("081111111111", 50_000)
        st.add("082222222222", 10_000)
        st.add("083333333333", 0, aktif=False)
        return st, USSDSession(st, "081111111111")

    # jalur sukses
    st, s = baru()
    s.start()
    for x in ["1", "082222222222", "10000", "1"]:
        out, done = s.input(x)
    assert done and "berhasil" in out
    assert st.subscribers["081111111111"].pulsa == 50_000 - 10_000 - ADMIN_FEE
    assert st.subscribers["082222222222"].pulsa == 20_000
    assert len(st.transactions) == 1 and len(st.notifications) == 2

    # nomor salah / sendiri / tidak aktif
    st, s = baru(); s.start(); s.input("1")
    assert "Format" in s.input("abc")[0]
    assert "sendiri" in s.input("081111111111")[0]
    assert "tidak terdaftar" in s.input("083333333333")[0]

    # nominal tidak valid / pulsa kurang
    st, s = baru(); s.start(); s.input("1"); s.input("082222222222")
    assert "angka" in s.input("10rb")[0]
    assert "Rp5,000" in s.input("1000")[0]
    assert "tidak cukup" in s.input("50000")[0]

    # batal
    st, s = baru(); s.start()
    for x in ["1", "082222222222", "10000", "2"]:
        out, done = s.input(x)
    assert done and st.subscribers["081111111111"].pulsa == 50_000 and not st.transactions

    print("Semua tes lulus.")


if __name__ == "__main__":
    run_tests() if "--test" in sys.argv else run_cli()
