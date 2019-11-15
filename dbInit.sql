CREATE DATABASE mydb;


产品列表
CREATE TABLE `BandInfo` (
  `PTFrom` varchar(128) NOT NULL COMMENT '平台类型',
  `EnName` varchar(128) NOT NULL COMMENT '英文名称',
  `CHName` varchar(128) NOT NULL COMMENT '中文名称',
  `Url` varchar(128) NOT NULL COMMENT '获取url',
  PRIMARY KEY (`PTFrom`,`EnName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



车信息
CREATE TABLE `CarsInfo` (
  `id` int(20) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `bordingdate` varchar(64),
  `title` varchar(512),
  `price` varchar(64),
  `displacement` varchar(64),
  `km` varchar(64),
  `address` varchar(64),
  `gearbox` varchar(64),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8


python库-安装方法

pip install pyquery -ihttps://pypi.mirrors.ustc.edu.cn/simple/
pip install mysqlclient -ihttps://pypi.mirrors.ustc.edu.cn/simple/
