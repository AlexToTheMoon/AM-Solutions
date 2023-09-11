<pre><code>
MONIKER="your_moniker" <br/>
VALIDATOR_WALLET="validator" <br/>
<br/>
celestia-appd tx staking create-validator \<br/>
&nbsp; --amount=1000000utia \<br/>
&nbsp; --pubkey=$(celestia-appd tendermint show-validator) \<br/>
&nbsp; --moniker=$MONIKER \<br/>
&nbsp; --chain-id={constants.mochaChainId} \<br/>
&nbsp; --commission-rate=0.1 \<br/>
&nbsp; --commission-max-rate=0.2 \<br/>
&nbsp; --commission-max-change-rate=0.01 \<br/>
&nbsp; --min-self-delegation=1000000 \<br/>
&nbsp; --from=$VALIDATOR_WALLET \<br/>
&nbsp; --keyring-backend=test
</code></pre>
