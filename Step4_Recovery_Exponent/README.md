# Step 4: Extended branch-and-prune attack on 1,024-bit RSA--CRT.
 
# Directory construction
.  
├── ExtendHS4.py  
├── README.md  
├── blind_secret_key  
│   ├── key777_Dp_16bits.csv  
│   └── key777_Dq_16bits.csv  
├── blind_secret_key.py  
├── enzan_rule.py  
├── key_recover4.py  
├── keytoseq.py  
└── original_secret_key  
    └── key777.txt  

# Requirement

* python3

# Usage
 
1. Execute the following command.
```bash
python3 blind_secret_key.py [keyname] [Random mask bit length]
```
The result is given by the mask, correct values of Dp and Dq, S--M sequence, its length, ratio of correct estimation, how many continuous bits in MSBs are exposed, and is stored in blind_secret_key directory. The result is sorted in the descending order in terms of S--M sequence length and then the ratio of correct estimation.

2. Execute the following comand to try key recovery. Modify Lines 44--45 in key_recovery4.py to specify the random value which masks the key.
```bash
python3 key_recover4.py [keyname] [Random mask bit length]
```
