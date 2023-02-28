# This represitory includes the source code used in the experiments in a paper published in TCHES 2023, issue 2, entitled ``How Secure is Exponent-blinded RSA-CRT with Sliding Window Exponentiation?'' by Rei Ueno and Naofumi Homma.
 
# Directory construction
.  
├── Aditional_Experiment  
├── README.md  
├── Step3_Continued_Fraction_Attack  
└── Step4_Recovery_Exponent  

# Requirement
* gcc
* Libgcrypt1.7.8
* python3

# Note
* Step1_FlushAndReload: A code for Flush+Reload and S--M sequence recovery (Under construction)
* Step3_Continued_Fraction_Attack: Simulation code for our continuted fraction expansion attack on 1024-bit RSA--CRT.
* Step4_Recovery_Exponent: A code for extended branch-and-prune attack using partial key information from Step 3.
* Additional_Experiment: Simulation code for our continuted fraction expansion attack on 2048-bit RSA--CRT.
