# How to move node from basic run to cosmovisor and prepare for upgrade.
## Testnet "INNUENDO-1" v. v0.6.4-rc.0 >> v0.6.6

*If any commnets or issues U can contact me at* **Discord** - AlexeyM#5409

## Step by step instructions 

Install Cosmovisor 
```bash
git clone https://github.com/cosmos/cosmos-sdk
cd cosmos-sdk
git checkout v0.45.8
make cosmovisor
cp cosmovisor/cosmovisor $HOME/go/bin/cosmovisor
cd $HOME
```
