#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <malloc.h>
#include <unistd.h>
#include <gcrypt.h>



/* const rsa parms */
const char* parms_str =
  "(genkey"
  "  (rsa"
  "    (nbits 4:2048)))";


// ./RSA2048keygen 2> key_ex.csvで生成
int main(int argc, char** argv){
  /* Load the key pair components into sexps. */
  gcry_error_t err;
  gcry_sexp_t parms;
  gcry_sexp_t privk;
  gcry_sexp_t d_sexp;
  gcry_sexp_t p_sexp;
  gcry_sexp_t q_sexp;
  gcry_mpi_t d_mpi;
  gcry_mpi_t p_mpi;
  gcry_mpi_t q_mpi;
  gcry_mpi_t dp_mpi=gcry_mpi_new(0);
//   hp = p - 1
  gcry_mpi_t hp_mpi=gcry_mpi_new(0);
//   hq = q - 1
  gcry_mpi_t dq_mpi=gcry_mpi_new(0);
  gcry_mpi_t hq_mpi=gcry_mpi_new(0);
  
  
  
  /* Create parms */
  err = gcry_sexp_new(&parms, parms_str, strlen(parms_str), 0);
  if (err){
    fprintf(stderr, "failed to create parms.\n");
    return 1;
  }
  
  
  
  /* Create priv key */
  err = gcry_pk_genkey(&privk, parms);
  if (err){
    fprintf(stderr, "failed to create privk.\n");
    return 1;
  }
  // extruct key info
  d_sexp = gcry_sexp_find_token(privk, "d", 0);
  d_mpi = gcry_sexp_nth_mpi(d_sexp, 1, GCRYMPI_FMT_USG);  
  p_sexp = gcry_sexp_find_token(privk, "p", 0);
  p_mpi = gcry_sexp_nth_mpi(p_sexp, 1, GCRYMPI_FMT_USG);
  q_sexp = gcry_sexp_find_token(privk, "q", 0);
  q_mpi = gcry_sexp_nth_mpi(q_sexp, 1, GCRYMPI_FMT_USG);
  
  
  /* Create dp_blind */
  // dp = d mod (p - 1)
  gcry_mpi_sub_ui(hp_mpi, p_mpi, 1);
  gcry_mpi_mod(dp_mpi, d_mpi, hp_mpi);
  
  // dq = d mod (q - 1)
  gcry_mpi_sub_ui(hq_mpi, q_mpi, 1);
  gcry_mpi_mod(dq_mpi, d_mpi, hq_mpi);
  
  /* print key */
  fprintf(stderr, "d\n");
  fprintf(stderr, "0x");
  gcry_mpi_dump(d_mpi);
  fprintf(stderr, "\n");

  fprintf(stderr, "p\n");
  fprintf(stderr, "0x");
  gcry_mpi_dump(p_mpi);
  fprintf(stderr, "\n");

  fprintf(stderr, "q\n");
  fprintf(stderr, "0x");
  gcry_mpi_dump(q_mpi);
  fprintf(stderr, "\n");

  fprintf(stderr, "dp\n");
  fprintf(stderr, "0x");
  gcry_mpi_dump(dp_mpi);
  fprintf(stderr, "\n");

  fprintf(stderr, "dq\n");
  fprintf(stderr, "0x");
  gcry_mpi_dump(dq_mpi);
  fprintf(stderr, "\n");

  return 0;
}
