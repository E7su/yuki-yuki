Build docker image for application
```
docker build -t yuki .
```

Run mysql image for centos6
```
docker run -it --rm --name yuki_mysql6 -v /home/etsu/Projects/yuki/db/:/db mysql6
```

Default credentials for mysql
```
mysql -uroot -pmysqlPassword
```

DDL queries
```
CREATE DATABASE yuki;

CREATE TABLE `yuki`.`yuki` (
 `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
 `price` float unsigned NOT NULL,
 `name` VARCHAR(500) NOT NULL,
 `category` VARCHAR(500) NOT NULL,
 `link` VARCHAR(500) DEFAULT NULL,
 `date` date DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

INSERT INTO yuki.yuki(price, name, link, category) VALUES (350, "Роллы Инь-Янь", "https://clck.ru/CiAW7", "Суши");
```
