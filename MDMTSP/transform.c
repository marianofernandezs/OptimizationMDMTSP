#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <assert.h>

#define in_t(i) ((i) >= depots && (i) < k)
#define in_V(i) ((i) < depots)
#define in_Vm(i) ((i) >= k)

int main(int argc, char *argv[])
{
    int n, depots, f, dim, i, j, k;
    double *x, *y, dx, dy;
    char *class, *name, in_name[256], out_name[256], outdir[256], cmd[256];
    FILE *in, *out;
    
    if (argc < 3) {
        printf("%s class name [f]", argv[0]);
        exit(999);
    }
    class = argv[1];
    name = argv[2];
    printf("convert %s\n", name);
    f = argc == 4 && !strcmp(argv[3], "f");

    strcpy(in_name, "DAT/");
    strcat(in_name, class);
    strcat(in_name, "/");
    strcat(in_name, name);
    strcat(in_name, ".dat");
    in = fopen(in_name, "r");
    if (!in) {
        printf("Cannot open %s for reading\n", in_name);
        exit(9999);
    }

    system("mkdir -p INSTANCES");
    strcpy(outdir, "INSTANCES/");
    strcat(outdir, class);
    strcpy(cmd, "mkdir -p ");
    strcat(cmd, outdir);
    system(cmd);
    strcpy(out_name, outdir);
    strcat(out_name, "/");
    strcat(out_name, name);
    strcat(out_name, ".atsp");
    out = fopen(out_name, "w");
    if (!out) {
        printf("Cannot open %s for writing\n", out_name);
        exit(9999);
    }

    fscanf(in, "%d %d", &n, &depots);
    dim = n + 2 * depots;
    x = (double *) malloc(dim * sizeof(double));
    y = (double *) malloc(dim * sizeof(double));
    k = depots + n;
    for (i = 0; i < k; i++)
        fscanf(in, "%lf %lf\n", &x[i], &y[i]);
    for (i = 0; i < depots; i++) {
        x[k + i] = x[i];
        y[k + i] = y[i];
    }
    fprintf(out, "NAME : %s\n", name);
    fprintf(out, "TYPE : ATSP\n");
    fprintf(out, "DIMENSION : %d\n", dim);
    fprintf(out, "EDGE_WEIGHT_TYPE : EXPLICIT\n");
    fprintf(out, "EDGE_WEIGHT_FORMAT : FULL_MATRIX\n");
    fprintf(out, "EDGE_WEIGHT_SECTION\n");
    for (i = 0; i < dim; i++) {
        for (j = 0; j < dim; j++) {
            if ((in_t(i) && (in_Vm(j) || in_t(j))) || 
                (in_V(i) && in_t(j))) {
                dx = x[i] - x[j];
                dy = y[i] - y[j];
                fprintf(out, "%d ", 
                        !f ?
                        (int) ceil(100 * sqrt(dx * dx + dy * dy)) : 
                        (int) round(100 * sqrt(dx * dx + dy * dy)));
            } else if ((in_V(i) && j == i + k) ||
                       (in_Vm(i) && i < dim - 1 && j == i - k + 1) ||
                       (i == dim - 1 && j == 0))
                fprintf(out, "0 ");
            else
                fprintf(out, "1000000 ");
        }
        fprintf(out, "\n");
    }
    fprintf(out, "EOF\n");
}

