/* DATASUS .dbc -> .dbf: DBF header stored plain, 4-byte CRC, then PKWARE DCL "implode" stream.
   Decoder follows the structure of Mark Adler's blast.c (zlib contrib). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXBITS 13
#define MAXWIN 4096

static FILE *fin, *fout;
static int bitbuf = 0, bitcnt = 0;
static unsigned char win[MAXWIN];
static unsigned next = 0;
static int first = 1;
static unsigned char obuf[1 << 16];
static size_t onext = 0;
static long long total = 0;

static void die(const char *m) { fprintf(stderr, "error: %s at out=%lld\n", m, total); exit(2); }

static int bits(int need) {
    int val = bitbuf;
    while (bitcnt < need) {
        int c = fgetc(fin);
        if (c == EOF) die("unexpected end of input");
        val |= c << bitcnt;
        bitcnt += 8;
    }
    bitbuf = val >> need;
    bitcnt -= need;
    return val & ((1 << need) - 1);
}

struct huffman { short count[MAXBITS + 1]; short symbol[256]; };

static int decode(struct huffman *h) {
    int len, code = 0, first_ = 0, index = 0, count;
    for (len = 1; len <= MAXBITS; len++) {
        code |= bits(1) ^ 1;
        count = h->count[len];
        if (code < first_ + count) return h->symbol[index + (code - first_)];
        index += count;
        first_ += count;
        first_ <<= 1;
        code <<= 1;
    }
    die("ran out of codes");
    return -1;
}

static void construct(struct huffman *h, const unsigned char *rep, int n) {
    short length[256], offs[MAXBITS + 1];
    int symbol = 0, len, left;
    do {
        len = *rep++;
        left = (len >> 4) + 1;
        len &= 15;
        do { length[symbol++] = len; } while (--left);
    } while (--n);
    n = symbol;
    for (len = 0; len <= MAXBITS; len++) h->count[len] = 0;
    for (symbol = 0; symbol < n; symbol++) h->count[length[symbol]]++;
    offs[1] = 0;
    for (len = 1; len < MAXBITS; len++) offs[len + 1] = offs[len] + h->count[len];
    for (symbol = 0; symbol < n; symbol++)
        if (length[symbol] != 0) h->symbol[offs[length[symbol]]++] = symbol;
}

static void put(unsigned char c) {
    win[next++] = c;
    if (next == MAXWIN) { next = 0; first = 0; }
    obuf[onext++] = c;
    total++;
    if (onext == sizeof obuf) { fwrite(obuf, 1, onext, fout); onext = 0; }
}

int main(int argc, char **argv) {
    static const unsigned char litlen[] = {
        11, 124, 8, 7, 28, 7, 188, 13, 76, 4, 10, 8, 12, 10, 12, 10, 8, 23, 8,
        9, 7, 6, 7, 8, 7, 6, 55, 8, 23, 24, 12, 11, 7, 9, 11, 12, 6, 7, 22, 5,
        7, 24, 6, 11, 9, 6, 7, 22, 7, 11, 38, 7, 9, 8, 25, 11, 8, 11, 9, 12,
        8, 12, 5, 38, 5, 38, 5, 11, 7, 5, 6, 21, 6, 10, 53, 8, 7, 24, 10, 27,
        44, 253, 253, 253, 252, 252, 252, 13, 12, 45, 12, 45, 12, 61, 12, 45,
        44, 173};
    static const unsigned char lenlen[] = {2, 35, 36, 53, 38, 23};
    static const unsigned char distlen[] = {2, 20, 53, 230, 247, 151, 248};
    static const short base[16] = {3, 2, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264};
    static const char extra[16] = {0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8};
    static struct huffman litcode, lencode, distcode;
    unsigned char hdr[10];
    int hsize, lit, dict, symbol, len;
    unsigned dist;
    char *buf;

    if (argc != 3) { fprintf(stderr, "usage: dbc2dbf in.dbc out.dbf\n"); return 1; }
    fin = fopen(argv[1], "rb");
    fout = fopen(argv[2], "wb");
    if (!fin || !fout) die("open");
    if (fread(hdr, 1, 10, fin) != 10) die("header");
    hsize = hdr[8] | (hdr[9] << 8);
    buf = malloc(hsize);
    memcpy(buf, hdr, 10);
    if (fread(buf + 10, 1, hsize - 10, fin) != (size_t)(hsize - 10)) die("header body");
    fwrite(buf, 1, hsize, fout);
    fseek(fin, 4, SEEK_CUR); /* CRC */

    construct(&litcode, litlen, sizeof litlen);
    construct(&lencode, lenlen, sizeof lenlen);
    construct(&distcode, distlen, sizeof distlen);

    lit = bits(8);
    if (lit > 1) die("bad literal flag");
    dict = bits(8);
    if (dict < 4 || dict > 6) die("bad dictionary size");
    for (;;) {
        if (bits(1)) {
            symbol = decode(&lencode);
            len = base[symbol] + bits(extra[symbol]);
            if (len == 519) break;
            symbol = len == 2 ? 2 : dict;
            dist = decode(&distcode) << symbol;
            dist += bits(symbol);
            dist++;
            if (first && dist > next) die("distance too far back");
            while (len--) {
                unsigned from = (next + MAXWIN - dist) % MAXWIN;
                put(win[from]);
            }
        } else {
            put((unsigned char)(lit ? decode(&litcode) : bits(8)));
        }
    }
    fwrite(obuf, 1, onext, fout);
    fclose(fout);
    fprintf(stderr, "ok: header %d, body %lld bytes\n", hsize, total);
    return 0;
}
