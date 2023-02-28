# Continuted fraction expansion attack on 2048-bit RSA--CRT
 
# Directory construction
.  
├── README.md  
├── RSA2048key  
│   └── key8.csv  
├── cf_attack.py  
├── cf_attack.sh  
├── cf_attack_data  
│   └── cf_attack_data_key8_blind16bits_5used.csv  
├── enzan_rule.py  
├── expblindkey  
│   ├── Dp_16bitsmask_key8.csv  
│   └── Dq_16bitsmask_key8.csv  
├── expblindkeygen.py  
├── expblindkeygen.sh  
├── keytoseq.py  
└── slidingwindow.py  
  
# Requirement
  
* gcc
* libgcrypt1.7.8
* python3
 
# Usage

Compile RSA2048keygen.c using a PC with libgcrypt1.7.8.
```bash
gcc -o RSA2048keygen RSA2048keygen.c ‘libgcrypt-config --cflags --libs‘
```
1. Generate secret key of 2048-bit RSA--CRT.
Execute the following command at keygen directory.
```bash
bash make99keys.sh
```
2. Gnerate blinded secret key with a 16-bit randm mask.
Generated blinded key (Dp and Dq) are stored in expblindkey according to the key pairs generated at Step 1.
```bash
bash expblindkeygen.sh
```
3. Execute the following command to perform the continued fraction expansion attack.
```bash
bash cf_attack.sh
```
