```
,--.   ,--.       ,--.    ,--.      ,--.   ,--.       ,--.    ,--. 
 \  `.'  /,--.,--.|  |,-. `--',-----.\  `.'  /,--.,--.|  |,-. `--' 
  '.    / |  ||  ||     / ,--.'-----' '.    / |  ||  ||     / ,--. 
    |  |  '  ''  '|  \  \ |  |          |  |  '  ''  '|  \  \ |  | 
    `--'   `----' `--'`--'`--'          `--'   `----' `--'`--'`--'

 __ __     _   _     __ __     _   _ 
|  |  |_ _| |_|_|___|  |  |_ _| |_|_|
|_   _| | | '_| |___|_   _| | | '_| |
  |_| |___|_,_|_|     |_| |___|_,_|_|

 __  __     __    _   __  __     __    _ 
 \ \/ /_ __/ /__ (_)__\ \/ /_ __/ /__ (_)
  \  / // /  '_// /___/\  / // /  '_// / 
  /_/\_,_/_/\_\/_/     /_/\_,_/_/\_\/_/  

```

## Build images
Build mysql image
```
docker build -f MYSQL_Dockerfile -t mysql6 .
```

Build docker image for application
```
docker build -t yuki .
```

## Run containers
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
 `category` int(9) NOT NULL,
 `link` VARCHAR(500) DEFAULT NULL,
 `date` date DEFAULT NULL,
 PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

INSERT INTO yuki.yuki(price, name, link, category) VALUES (350, "Роллы Инь-Янь", "https://clck.ru/CiAW7", 5);

INSERT INTO yuki.yuki(price, name, link, category) VALUES (250, "Венгерский суп-гуляш", "https://gotovim-doma.ru/images/recipe/6/40/64098f9e72a9cc65260d1e920f68d194_l.jpg", 1);

INSERT INTO yuki.yuki(price, name, link, category) VALUES (200, "Суп из рыбных консервов в томатном соусе", "http://natural-balkan.com/wp-content/uploads/2013/02/DSCN1738.jpg", 1);

SELECT * FROM yuki.yuki;
```

Run application
```
docker run -it --rm --link yuki_mysql6:mysql6 -v /home/etsu/Projects/yuki/:/app yuki6
```
