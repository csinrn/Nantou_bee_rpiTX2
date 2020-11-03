<?php
 
 echo "///////////////////////////////////////////////////////////////////////////".PHP_EOL;
 echo "//    UDP Receiving program for common platform WSN (NTU-BIME-LAB405)    //".PHP_EOL;
 echo "//                 IP ADDRESS: 140.112.94.128 PORT: 20021                //".PHP_EOL;
 echo "///////////////////////////////////////////////////////////////////////////".PHP_EOL;

 
 // Connection parameters:
 // Opens udp socket
ini_set('mysql.connect_timeout',3000);
ini_set('default_socket_timeout',3000);
ini_set('display_errors', 1);
error_reporting(E_ALL);
error_reporting(E_ALL | E_STRICT);
$socket = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
socket_bind($socket, '0.0.0.0', 20021);

 
// Database parameters:
define('DBHOST','localhost');//IP
define('DBUSER','root');
define('DBPASSWORD','root');

while(1)
{

	// Link to database
	$db = new mysqli(DBHOST,DBUSER,DBPASSWORD);
    $link = mysqli_connect(DBHOST,DBUSER,DBPASSWORD);

   
	// Set date/time
	date_default_timezone_set("Asia/Taipei");

	// Receive data:
    $r = socket_recvfrom($socket, $buf, 512, 0,  $remote_ip , $remote_port);
	$dataset = substr($buf,0,1);

	$date = date('m/d/Y h:i:s a', time());
	$date =  date ("Y-m-d H:i:s" , mktime(date('H'), date('i'), date('s'), date('m'), date('d'), date('Y'))) ;
	

	
	// Bee hive monitoring database set
	if($dataset=="B")
	{	
		$DBNAME = 'bee_hive405';
		list($dataset,$type) =  explode(":",$buf);
		
		if($type=="ACT")
		{
		mysqli_select_db($link, $DBNAME);
		list($dataset,$type,$act,$datex,$min,$sec,$hive,$bee_type,$dbx,$location) =  explode(":",$buf);
		
		//echo $dataset.PHP_EOL;
		//echo $type.PHP_EOL;
		//echo $act.PHP_EOL;
		//echo $date.PHP_EOL;
		//echo $hive.PHP_EOL;
		//echo $dbx.PHP_EOL;
		
		// default: 6.8.2017
		$location = "hsinchu";
		
		$sql1 = "SHOW TABLES  from `bee_hive405`";
		$result1 = $link->query($sql1);

		$new_table_name = "count_activity_".$location."_".$dbx;
		//echo $new_table_name;
		
		$new_table = 1;
		$x=0;
		while ($row = mysqli_fetch_row($result1)) {
		if (strpos($row[0], 'count_activity') !== false) {
			$table[$x] = $row[0];
					
			if($new_table_name == $table[$x])
			{
				$new_table = 0;
			}
			//echo $table[$x];
			$x++;
		}
		}
		

		// If table does not exist:
		if($new_table==1)
		{
		$tableSQL = "CREATE TABLE `bee_hive405`.`$new_table_name` 
			( `ID` BIGINT NOT NULL AUTO_INCREMENT , 
			`DATE` DATETIME NULL DEFAULT NULL , 
			`ACTION` CHAR(15) NULL DEFAULT NULL , 
			`HIVE` CHAR(15) NULL DEFAULT NULL ,
			`BEE_TYPE` CHAR(15) NULL DEFAULT NULL ,
			PRIMARY KEY (`ID`)) 
			ENGINE = InnoDB 
			CHARACTER SET utf8 
			COLLATE utf8_general_ci;";

		
		$result = $db->query($tableSQL);
		if($result)  
		{
			echo "[SUCCESS]";
			echo "New table created:";
			echo $new_table_name.PHP_EOL;
		}
		else         
		{
		echo "[ERROR]";
		}
		$new_table=0;
		}
			
		
		// If table exists:
		if($new_table==0)
		{
		$sqlx = "INSERT INTO `bee_hive405`.`$new_table_name` (`ID` ,`DATE`,`ACTION`,`HIVE`,`BEE_TYPE`)
								   VALUES (NULL , '$date', '$act', '$hive','$bee_type')";

		$result = $db->query($sqlx);
		if($result)  echo "[SUCCESS]";
		else         echo "[ERROR]";
		}
		}
	
	
	
	
	
	
	
	
		// For environmental sensors 6.29.2017
		if($type=="ENVI")
		{
		mysqli_select_db($link, $DBNAME);
		list($dataset,$type,$datex,$hive,$envi_type,$value,$location,$dbx) =  explode(":",$buf);
		
		
		/*
		echo $dataset.PHP_EOL;
		echo $type.PHP_EOL;
		echo $datex.PHP_EOL;
		echo $hive.PHP_EOL;
		echo $envi_type.PHP_EOL;
		echo $value.PHP_EOL;
		echo $location.PHP_EOL;
		echo $dbx.PHP_EOL;*/
		
		
		$location = strtolower($location);
	
		// Check for tables
		$sql1 = "SHOW TABLES  from `bee_hive405`";
		$result1 = $link->query($sql1);

		$new_table_name = "envi_".$location."_".$dbx;
		//echo $new_table_name;
		
		$new_table = 1;
		$x=0;
		while ($row = mysqli_fetch_row($result1)) {
		if (strpos($row[0], 'envi') !== false) {
			$table[$x] = $row[0];
					
			if($new_table_name == $table[$x])
			{
				$new_table = 0;
			}
			//echo $table[$x];
			$x++;
		}
		}
		
		
		
		
		// If table does not exist:
		if($new_table==1)
		{
		$tableSQL = "CREATE TABLE `bee_hive405`.`$new_table_name` 
			( `ID` BIGINT NOT NULL AUTO_INCREMENT , 
			`DATE` DATETIME NULL DEFAULT NULL , 
			`HIVE` CHAR(15) NULL DEFAULT NULL , 
			`TYPE` CHAR(20) NULL DEFAULT NULL ,
			`VALUE` CHAR(20) NULL DEFAULT NULL ,
			PRIMARY KEY (`ID`)) 
			ENGINE = InnoDB 
			CHARACTER SET utf8 
			COLLATE utf8_general_ci;";
			
			//echo $tableSQL;


		
		$result = $db->query($tableSQL);
		if($result)  
		{
			echo "[SUCCESS]";
			echo "New table created:";
			echo $new_table_name.PHP_EOL;
		}
		else         
		{
		echo "[ERROR]";
		}
		$new_table=0;
		}
			
		
		// If table exists:
		if($new_table==0)
		{

		$sqlx = "INSERT INTO `bee_hive405`.`$new_table_name` (`ID` ,`DATE`,`TYPE`,`VALUE`,`HIVE`)
								   VALUES (NULL , '$date', '$envi_type', '$value', '$hive')";

		$result = $db->query($sqlx);
		//echo $sqlx.PHP_EOL;
		if($result)  echo "[SUCCESS]";
		else         echo "[ERROR]";
		}


		
			
		}
	
	
	
	
		
	}
	
	
	
	
	echo $buf."\n";
	
	


}

 
socket_close($sock);
?>
