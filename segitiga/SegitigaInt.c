/*
 * Exercise #1 - Determine Triangle (versi 1: input bilangan bulat)
 *
 * PSPEC (Structured English):
 *   GET a, b, c
 *   SORT sisi sehingga c = sisi terbesar
 *   IF a <= 0 OR b <= 0 OR c <= 0
 *       DISPLAY "Bukan segitiga (ada sisi <= 0)"
 *   ELSE IF c >= a + b
 *       DISPLAY "Bukan segitiga (sisi terbesar >= jumlah dua sisi lain)"
 *   ELSE
 *       IF a = b AND b = c        -> SAMA SISI
 *       ELSE IF a = b OR b = c    -> SAMA KAKI
 *       IF c*c = a*a + b*b        -> SIKU-SIKU
 *       IF bukan sama sisi/sama kaki/siku-siku -> BEBAS
 *   ENDIF
 *
 * Kompilasi: gcc segitiga_int.c -o segitiga_int
 */
#include <stdio.h>

#define MAKS_SISI 1000000000LL   /* agar kuadrat tidak overflow long long */

typedef enum { BUKAN_SEGITIGA, SEGITIGA_ADA } Status;

typedef struct {
    Status ada;
    const char *alasan;      /* diisi jika bukan segitiga */
    int sama_sisi, sama_kaki, siku, bebas;
} Hasil;

/* Proses: urutkan sehingga *c adalah yang terbesar */
static void urutkan(long long *a, long long *b, long long *c) {
    long long t;
    if (*a > *c) { t = *a; *a = *c; *c = t; }
    if (*b > *c) { t = *b; *b = *c; *c = t; }
    if (*a > *b) { t = *a; *a = *b; *b = t; }
}

/* Proses: tentukan jenis segitiga dari tiga sisi (input -> output) */
Hasil tentukanSegitiga(long long a, long long b, long long c) {
    Hasil h = {BUKAN_SEGITIGA, "", 0, 0, 0, 0};
    if (a <= 0 || b <= 0 || c <= 0) { h.alasan = "ada sisi <= 0"; return h; }
    urutkan(&a, &b, &c);
    if (c >= a + b) { h.alasan = "sisi terbesar >= jumlah dua sisi lain"; return h; }

    h.ada = SEGITIGA_ADA;
    if (a == b && b == c)            h.sama_sisi = 1;
    else if (a == b || b == c)       h.sama_kaki = 1;   /* a==c mustahil setelah urut kecuali sama sisi */
    if (c * c == a * a + b * b)      h.siku = 1;
    if (!h.sama_sisi && !h.sama_kaki && !h.siku) h.bebas = 1;
    return h;
}

static void tampilkan(Hasil h) {
    if (h.ada == BUKAN_SEGITIGA) { printf("Bukan segitiga (%s)\n", h.alasan); return; }
    printf("Segitiga:");
    if (h.sama_sisi) printf(" SAMA SISI");
    if (h.sama_kaki) printf(" SAMA KAKI");
    if (h.siku)      printf(" SIKU-SIKU");
    if (h.bebas)     printf(" BEBAS");
    printf("\n");
}

int main(void) {
    long long a, b, c;
    printf("Masukkan 3 sisi (bilangan bulat, maks %lld): ", MAKS_SISI);
    if (scanf("%lld %lld %lld", &a, &b, &c) != 3) { printf("Input harus 3 bilangan bulat.\n"); return 1; }
    if (a > MAKS_SISI || b > MAKS_SISI || c > MAKS_SISI) { printf("Sisi terlalu besar.\n"); return 1; }
    tampilkan(tentukanSegitiga(a, b, c));
    return 0;
}