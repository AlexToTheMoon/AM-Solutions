## Remote Signing setup via TMKMS for Namada Shielded testnet 

#### Please notice:

This guide about "Soft-Sign" option, which is software signing structure. There is also HSM option available, for hardware signing methods like Ledger etc.. What requires physical access to the server. More information available at official docs [HERE](https://github.com/iqlusioninc/tmkms)

At remote signing host (where we setup tmkms) should be managed high level of security. Like non root access, firewalls etc.. 

Best option to use VPN tunel for connection between remote signer host and validator node.

How to setup VPN at Ubuntu U can find [HERE](https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-an-openvpn-server-on-ubuntu-20-04)
or any another source like Google or YouTube.  

For any feedback or comments, please contact Discord - AlexeyM#5409

##
<p align="center">
Instructions
</p>

##### Create new user (from root)
```
adduser tmkms
usermod -aG sudo tmkms
su tmkms
cd $HOME
```

##### Install RUST
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

##### Install GCC 
```
sudo apt update & sudo apt install build-essential curl jq  --yes
```

##### Compile and sort TMKMS binaries
```
cd $HOME
cargo install tmkms --features=softsign
sudo mv $HOME/.cargo/bin/tmkms /usr/local/bin/
```

##### Create and Init TKMS working directory
```
mkdir -p $HOME/tmkms/namada
tmkms init $HOME/tmkms/namada
```
#### Import Private key
Upload your validator (or create and move data) priv_validator_key.json 
to directory **$HOME/priv_validator_key.json**  
Then check availablity ```cat $HOME/priv_validator_key.json```  
If right output is appeared, follow next step below 
```
tmkms softsign import $HOME/priv_validator_key.json $HOME/tmkms/namada/secrets/namada-consensus.key
```
Now we can erase copy of original file  
```
sudo shred -uvz $HOME/priv_validator_key.json
```

#### Swap tmkms.toml to the one below. The only "addr =" field edit need to be done, replace it with your validator node IP + port(26658 default)
```
rm -rf ~/tmkms/namada/tmkms.toml
```
```
tee ~/tmkms/namada/tmkms.toml << EOF
#CometBFT KMS configuration file
[[chain]]
id = "shielded-expedition.b40d8e9055"
key_format = { type = "bech32", account_key_prefix = "namadapub", consensus_key_prefix = "namadavalconspub" }
state_file = "/home/tmkms/tmkms/namada/state/namada-priv_validator_state.json"
#Software-based Signer Configuration
[[providers.softsign]]
chain_ids = ["shielded-expedition.b40d8e9055"]
key_type = "consensus"
path = "/home/tmkms/tmkms/namada/secrets/namada-consensus.key"
#Validator Configuration
[[validator]]
chain_id = "shielded-expedition.b40d8e9055"
addr = "tcp://0.0.0.0:26658" #Set here IP and port of the Namada node U will be using for signing blocks (port can be custom)   
secret_key = "/home/tmkms/tmkms/namada/secrets/kms-identity.key"
protocol_version = "v0.34"
reconnect = true
EOF
```

#### Create service file and run TMKMS
```
sudo tee /etc/systemd/system/namada-tmkmsd.service << EOF
[Unit]
Description=TMKMS-Namada
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=10
User=$USER
ExecStart=$(which tmkms) start -c $HOME/tmkms/namada/tmkms.toml
LimitNOFILE=1024
[Install]
WantedBy=multi-user.target
EOF
```
```
sudo systemctl daemon-reload
sudo systemctl enable tmkmsd.service
sudo systemctl restart tmkmsd.service
sudo systemctl status tmkmsd.service
```
to check logs
```
sudo journalctl -u tmkmsd.service -f -o cat
```
Sample of normal logs at present stage

`INFO tmkms::commands::start: tmkms 0.12.2 starting up...`    
`INFO tmkms::keyring: [keyring:softsign] added consensus Ed25519 key: namadavalconspub1`    
`INFO tmkms::connection::tcp: KMS node ID: a1dbc4edb1dbb2bcd9316081bd810f57e0d`  
`ERROR tmkms::client: [shielded-expedition.b40d8e9055@tcp://<NODE IP>:26658] I/O error: Connection`  

#### LAST STEPS. Activate signing from Namada node side

Find field `priv_validator_laddr = ""` at dir `$HOME/.local/share/namada/shielded-expedition.b40d8e9055/config.toml` and edit to your Validator IP + port  
**Make sure your firewall open only for KMS server IP to allow connect to port 26658 (or any custom port u set)**

Example : `priv_validator_laddr = "tcp://0.0.0.0:26658"`

If u have more than one IP u have to set right IP (the same as in tmkms config file)

##### Restart Namada node and check TMKMS logs   

Good logs example :  
`INFO tmkms::session: [shielded-expedition.b40d8e9055@tcp://<IP>:26658] connected to validator successfully`

`WARN tmkms::session: [shielded-expedition.b40d8e9055@tcp://<IP>:26658]: unverified validator peer ID! (ad1fc4b45ee2340bb8148d7247bf82ea780y213q)`  
`INFO tmkms::session: [shielded-expedition.b40d8e9055@tcp://<IP>:26658] signed PreCommit:<nil> at h/r/s 8825119/0/2 (0 ms)`  
`INFO tmkms::session: [shielded-expedition.b40d8e9055@tcp://<IP>:26658] signed PreVote:144665D1CE at h/r/s 8825120/0/1 (0 ms)`  
`INFO tmkms::session: [shielded-expedition.b40d8e9055@tcp://<IP>:26658] signed PreCommit:144665D1CE at h/r/s 8825120/0/2 (0 ms)`  
`INFO tmkms::session: [shielded-expedition.b40d8e9055@tcp://<IP>:26658] signed PreVote:13BF759486 at h/r/s 8825121/0/1 (0 ms)`  


### Backup in safe place priv_validator_key.json and delete it from Validator node. Now U signing from KMS server!

##
<p align="center">
That pretty much all. Good luck!
</p>
