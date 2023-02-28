# Step 3: Continuted fraction expansion attack on 1,024-bit RSA--CRT.
 
# Directory construction
.  
├── README.md  
├── blind_key  
│   └── key0_Dp32.csv etc  
├── blind_secret_key.py  
├── cal_ranktable.py  
├── cal_ranktable.sh  
├── enzan_rule.py  
├── keytoseq.py  
├── original_key  
│   └── key0.csv etc  
├── rank_table  
│   └── rank_table_32_choice5.csv  
└── valuation.py  

# Requirement
  
* python3

# Usage
 
1. Execute the following command, which stores the results of the attack in blind_secret_key directory.
```bash
python3 blind_secret_key.py [keyname] [Random mask bit length]
```
the result is given, for each secret key, as correct random mask, correct values of Dp and Dq, lengths of S--M sequence length, ratio of correct construction, how many correct bits of MSBs are estimated for each secret key. The result is sorted in the descending order in terms of S--M sequence length.

2. Execute the folowing command to compute the correct key rank.
```bash
bash cal_ranktable.sh
```
The result is stored in rank_table directory.
