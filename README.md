# myblockchain
python实现最简单的区块链

环境：python3.6

需要安装requests，flask


使用如下：

通过下面命令将区块链服务开启，并绑定到5000端口

```
python myblockchain.py -p 5000
```

![](http://obfs4iize.bkt.clouddn.com/%E5%90%AF%E5%8A%A8myblockchain.png)

先使用postman请求chain接口，看看此时节点上有无区块链，发现是空的，因为还没有开始创建区块

![](http://obfs4iize.bkt.clouddn.com/emtpyblock.png)


那么就请求mine接口来创建区块吧，第一次请求mine接口，创建出了创世区块，创世区块中记录了唯一一个交易就是系统奖励，奖励了50个数字货币给创世区块的创造者，比特币的创世区块也是奖励50个币，这里向本聪哥致敬

![](http://obfs4iize.bkt.clouddn.com/1block.png)

继续请求mine接口，创造第二个区块

![](http://obfs4iize.bkt.clouddn.com/2block.png)

第二个区块依旧没有交易，只有系统奖励，6个数字货币

其实这里已经有一个节点地址了，就是f675e46d829a44fc85783a87f1b52284，它创建了2个区块，已经有了56个数字货币，那我让他发5个数字货币给ayuliao，接济一下我这个穷人

![](http://obfs4iize.bkt.clouddn.com/1transactions.png)

这个交易是要写入第三个区块中的，但是此时第三个区块还没被创建出来，那么在第三个区块创建出来前，这些交易都会写到这个区块中，比如我再让他发50个币给我

![](http://obfs4iize.bkt.clouddn.com/2transactions.png)

交易完后，调用mine接口，创建第三块区块，它就包含了刚刚的两个交易记录和系统对区块建立者的奖励

![](http://obfs4iize.bkt.clouddn.com/3block.png)

此时调用chain接口，就可以发现该节点已经有3个区块了

![](http://obfs4iize.bkt.clouddn.com/4block.png)

此时你已经转了55个币给我了，你就剩下一个数字货币了，此时你又想转10币给我是会失败的

![](http://obfs4iize.bkt.clouddn.com/nomoneyblock.png)

为了验证前面编写的共识算法，也就是多节点区块链的一致性，这里再开启一个服务，你可以开在其他电脑，或者同一台电脑的不同端口

```
python myblockchain.py -p 5001
```

开始了5001后，请求5001的mine接口，让5001创建区块，让他创建2个区块，也就是请求两次mine接口，此时5001的区块链长为2，而且跟5000节点的完全不同

![](http://obfs4iize.bkt.clouddn.com/5001block1.png)

此时将5000节点注册到5001节点中，调用5001的/nodes/register接口(你可以通过注册多个节点)

![](http://obfs4iize.bkt.clouddn.com/add_nodes.png)

然后我们来访问5001的node/resolve接口，使用其共识算法，让5001这个节点的区块链与区块链网络上的一直，其实就是判断5001自己手上的区块链跟网络上其他节点的区块链相比是不是最长的，其实我们知道目前为止应该是5000节点拥有的区块链最长，所以5001节点上的区块链会被替换成5000节点上的区块链，以求网络上所有节点的区块链保持一致

![](http://obfs4iize.bkt.clouddn.com/replaceblockchain.png)


到这里这个项目也就表演完了
