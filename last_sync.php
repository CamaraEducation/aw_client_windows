<?php
define('SERVER_FILE', 'http://camaraethserver.local/awdata/file.php');
define('SERVER_CONFIG', 'http://camaraethserver.local/awdata/config.php');
define('SERVER_SYNC', 'http://camaraethserver.local/awdata/last_sync.php');
define('AWDB', 'C:\xampp\htdocs\camaranms\nms.db');
define('USERNAME', getenv('username'));
define('AFK_DATE_FILE_PATH', 'C:\Users\camara\.camaranms\logs\afkdate');
define('APP_DATE_FILE_PATH', 'C:\Users\camara\.camaranms\logs\appdate');
define('CHROME_DATE_FILE_PATH', 'C:\Users\camara\.camaranms\logs\chrome');
define('FIREFOX_DATE_FILE_PATH', 'C:\Users\camara\.camaranms\logs\firefox');
define('AFK_DATA', 'C:\Users\camara\.camaranms\logs\computer.json');
define('APP_DATA', 'C:\Users\camara\.camaranms\logs\application.json');
define('CHROME_DATA', 'C:\Users\camara\.camaranms\logs\chrome.json');
define('FIREFOX_DATA', 'C:\Users\camara\.camaranms\logs\firefox.json');
ob_start();
include 'C:\xampp\htdocs\camaranms\config';
$myvar = ob_get_clean();
define('CONFIG_FILE_PATH', $myvar);

// Get the last AFK row date value from server
function get_afk_app_chrome_firefox_last_synced($status) {
    $devicename = CONFIG_FILE_PATH;
    $arr = array('devicename' => $devicename, 'status' => $status);
    $json = json_encode($arr);
    $timeout = 30;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_URL, SERVER_SYNC);
    curl_setopt($ch, CURLOPT_HTTPGET, 1);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $json);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
    curl_setopt($ch, CURLOPT_LOW_SPEED_TIME, 15);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);

    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json',
        'Content-Length: ' . strlen($json)
    ));
    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error: ' . curl_error($ch);
    } else {
		switch ($status) {
			case 'afk':
				echo 'LAST SYNCED AFK DATE: '.$response;
				break;
			case 'app':
				echo 'LAST SYNCED APP DATE: '.$response;
				break;
			case 'chrome':
				echo 'LAST SYNCED CHROME DATE: '.$response;
				break;
			default:
				echo 'LAST SYNCED FIREFOX DATE: '.$response . PHP_EOL;
		}
        // echo $response;
    }
    curl_close($ch);
    // $dateFilePath = ($status == 'afk') ? AFK_DATE_FILE_PATH : APP_DATE_FILE_PATH;
	switch ($status) {
        case 'afk':
            $dateFilePath = AFK_DATE_FILE_PATH;
            break;
        case 'app':
            $dateFilePath = APP_DATE_FILE_PATH;
            break;
        case 'chrome':
            $dateFilePath = CHROME_DATE_FILE_PATH;
            break;
        default:
            $dateFilePath = FIREFOX_DATE_FILE_PATH;
    }
    if (!file_exists($dateFilePath)) {
        if ($response != '') {
            file_put_contents($dateFilePath, $response);
        }
    } else {
        if ($response != '') {
            file_put_contents($dateFilePath, $response);
        }
    }
}

function get_chrome_firefox_last_synced($browser) {
    $devicename = CONFIG_FILE_PATH;
    $arr = array('devicename' => $devicename, 'browser' => $browser);
    $json = json_encode($arr);
    $timeout = 30;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_URL, SERVER_SYNC);
    curl_setopt($ch, CURLOPT_HTTPGET, 1);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $json);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $timeout);
    curl_setopt($ch, CURLOPT_LOW_SPEED_TIME, 15);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);

    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json',
        'Content-Length: ' . strlen($json)
    ));
    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error: ' . curl_error($ch);
    } else {
        echo $response;
    }
    curl_close($ch);
    $dateFilePath = ($browser == 'chrome') ? CHROME_DATE_FILE_PATH : FIREFOX_DATE_FILE_PATH;
    if (!file_exists($dateFilePath)) {
        if ($response != '') {
            file_put_contents($dateFilePath, $response);
        }
    } else {
        if ($response != '') {
            file_put_contents($dateFilePath, $response);
        }
    }
}

// function to export AW Files
function awData($file, $query){
	// prepare the database
	$awdb = new SQLite3(AWDB);
	// echo $query;
	$result = $awdb->query($query);
	while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
		$data[] = $row;
	} 
	$awdb->close();
	isset($data) ? $jsonData = json_encode($data) : $jsonData ='';
	file_put_contents($file, $jsonData, JSON_PRETTY_PRINT);
}

function init(){
	echo "***********Statred Sync FOR Student!***********". PHP_EOL;
	config();
	get_afk_app_chrome_firefox_last_synced('afk');
	get_afk_app_chrome_firefox_last_synced('app');
	get_afk_app_chrome_firefox_last_synced('chrome');
	get_afk_app_chrome_firefox_last_synced('firefox');
	$username = USERNAME;
	$afkresult = file_get_contents(AFK_DATE_FILE_PATH);
	$appresult = file_get_contents(APP_DATE_FILE_PATH);
	$chromeresult = file_get_contents(CHROME_DATE_FILE_PATH);
	$firefoxresult = file_get_contents(FIREFOX_DATE_FILE_PATH);
	$yesterday = new DateTime('today');
	$yesterday = $yesterday->format('Y-m-d 00:00:00.000000+00:00');
	$afkfile = AFK_DATA;
	$afkquery = "select * from aw_afk where date_time > '$afkresult' and date_time < '$yesterday' and username='$username';";
	$appfile = APP_DATA;
	$appquery = "select * from aw_app where date_time > '$appresult' and date_time < '$yesterday' and username='$username';";
	$chromefile = CHROME_DATA;
	$chromequery = "select * from aw_chrome where date_time > '$chromeresult' and date_time < '$yesterday' and username='$username';";
	$firefoxfile = FIREFOX_DATA;
	$firefoxquery = "select * from aw_firefox where date_time > '$firefoxresult' and date_time < '$yesterday' and username='$username';";

	awData($afkfile, $afkquery);
	awData($appfile, $appquery);
	awData($chromefile, $chromequery);
	awData($firefoxfile, $firefoxquery);
	streamData();
}
// data streaming function
function streamData(){
	$client_name = CONFIG_FILE_PATH;
	if (filesize(AFK_DATA) == 0 && filesize(APP_DATA) == 0 && filesize(CHROME_DATA) == 0 && filesize(FIREFOX_DATA) == 0){
		sleep(2);
		echo "There is no new data to sync to the server." . PHP_EOL;
		sleep(2);
		echo "***********STOPED SYNC FOR Student!***********". PHP_EOL;
	}else{
		echo "Found new data to sync to the server." . PHP_EOL;
		$file1 = new CURLFile(AFK_DATA);
		$file2 = new CURLFile(APP_DATA);
		$file3 = new CURLFile(CHROME_DATA);
		$file4 = new CURLFile(FIREFOX_DATA);
		// $file3 = new CURLFile('document.json');
		$data = array(
			'file1' => $file1,
			'file2' => $file2,
			'file3' => $file3,
			'file4' => $file4,
			"client" => CONFIG_FILE_PATH,);
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, SERVER_FILE);
		curl_setopt($ch, CURLOPT_POST, 1);
		curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		$output = curl_exec($ch);
		curl_close($ch);
		$output = trim($output);
		// 2023-01-05 09:32:51
		if ($output == 'ok') {
			echo "Syncing exported data to server compeleted successfully!". PHP_EOL;
			sleep(2);
			echo "***********SYNC ALL DONE FOR Student!***********". PHP_EOL;
		}
	}
}

// Check if config file exists and if not get one from servere.
// Helps to give unique device name.
function config(){
	// file config.json does not exist send get request to url
	if (!file_exists('C:\xampp\htdocs\camaranms\config')) {
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, SERVER_CONFIG);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		$output = curl_exec($ch);
		curl_close($ch);
		// if output is not empty write to file
		if ($output != '') {
			file_put_contents(CONFIG_FILE_PATH, $output);
		}
	} 
}
init();
?>