# BackTest
基于事件驱动的可扩展的外汇量化策略回测引擎<br>
## 开发目的
传统外汇量化程序回测软件（MT4/MT5）提供功能完善的回测以及详尽的数据统计功能<br>
但是MT4/5的回测结果是以订单结算为驱动的，这就意味着只有订单平仓之后才会统计<br>
订单信息以及账户信息<br>
这种方式比较高效，但是对于某些持仓时间较长，或者用户希望能通过测试报告看到<br>
账户的实时浮亏的情况，MT4/5的回测机制就显得有些不友好。<br>
基于事件驱动的可扩展的外汇量化策略回测引擎支持后台记录每个时刻的账户净值，<br>
最大净值以及最小净值，通过画图工具可以展示策略回测中每个时刻的浮亏，这对于<br>
马丁格尔策略爱好者来说是比较重要的。<br>


