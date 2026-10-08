/*
 * Exercise #1 - Determine Triangle (versi 2: bilangan pecahan, akurasi 1%)
 *
 * Aturan "sama": dua sisi x dan y dianggap SAMA jika
 *      |x - y| <= 0.01 * max(x, y)
 * Siku-siku: |c^2 - (a^2 + b^2)| <= 0.01 * c^2   (c = sisi terbesar)
 * Sama sisi: a ~ b DAN b ~ c (sesuai soal: "a=b and b=c").
 *
 * PSPEC sama dengan versi integer, hanya operator "=" diganti sama(x, y).
 * Kompilasi: gcc segitiga_pecahan.c -o segitiga_pecahan
 */
#include <stdio.h>
#include <math.h>

#define TOLERANSI 0.01

typedef enum { BUKAN_SEGITIGA, SEGITIGA_ADA } Status;

typedef struct {
    Status ada;
    const char *alasan;
    int sama_sisi, sama_kaki, siku, bebas;
} Hasil;

/* Proses: apakah x dan y dianggap sama (selisih <= 1% dari yang lebih besar) */
static int sama(double x, double y) {
    double besar = fmax(x, y);
    return fabs(x - y) <= TOLERANSI * besar;
}

static void urutkan(double *a, double *b, double *c) {
    double t;
    if (*a > *c) { t = *a; *a = *c; *c = t; }
    if (*b > *c) { t = *b; *b = *c; *c = t; }
    if (*a > *b) { t = *a; *a = *b; *b = t; }
}

Hasil tentukanSegitiga(double a, double b, double c) {
    Hasil h = {BUKAN_SEGITIGA, "", 0, 0, 0, 0};
    if (a <= 0 || b <= 0 || c <= 0) { h.alasan = "ada sisi <= 0"; return h; }
    urutkan(&a, &b, &c);
    if (c >= a + b) { h.alasan = "sisi terbesar >= jumlah dua sisi lain"; return h; }

    h.ada = SEGITIGA_ADA;
    if (sama(a, b) && sama(b, c))                         h.sama_sisi = 1;
    else if (sama(a, b) || sama(b, c) || sama(a, c))      h.sama_kaki = 1;
    if (fabs(c * c - (a * a + b * b)) <= TOLERANSI * c * c) h.siku = 1;
    if (!h.sama_sisi && !h.sama_kaki && !h.siku)          h.bebas = 1;
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
    double a, b, c;
    printf("Masukkan 3 sisi (bilangan real): ");
    if (scanf("%lf %lf %lf", &a, &b, &c) != 3) { printf("Input harus 3 bilangan.\n"); return 1; }
    tampilkan(tentukanSegitiga(a, b, c));
    return 0;
}