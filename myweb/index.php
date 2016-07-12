
<html>
<head lang="en">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
	
	<title>CAR ACCIDENT SURVEILLANCE SYSTEM</title> 
	<meta name="description" content="BlackTie.co - Free Handsome Bootstrap Themes" />	    
	<meta name="keywords" content="themes, bootstrap, free, templates, bootstrap 3, freebie,">
	<meta property="og:title" content="">

	<link rel="stylesheet" type="text/css" href="css/bootstrap.min.css">
	<link rel="stylesheet" href="fancybox/jquery.fancybox-v=2.1.5.css" type="text/css" media="screen">
    <link rel="stylesheet" href="css/font-awesome.min.css" rel="stylesheet">
	
	<link rel="stylesheet" type="text/css" href="css/style.css">	
	
	<link href='http://fonts.googleapis.com/css?family=Titillium+Web:400,600,300,200&subset=latin,latin-ext' rel='stylesheet' type='text/css'>
	
	
	<link rel="prefetch" href="images/zoom.png">

	<style>
		table {
   			border-collapse: collapse;
 		  	width: 100%;
 		 	font-weight: bold;
 		 	font-size:20px;
		}

		th, td {
    		text-align: left;
    		padding: 8px;
		}

		tr:nth-child(even){background-color: #f2f2f2}

		th {
    		background-color: #4CAF50;
    		color: white;
		}
	</style>
		
</head>

<body>
	<div class="navbar navbar-fixed-top" data-activeslide="1">
		<div class="container">
		
			<!-- .navbar-toggle is used as the toggle for collapsed navbar content -->
			<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-responsive-collapse">
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
			</button>
			
			
			<div class="nav-collapse collapse navbar-responsive-collapse">
				<ul class="nav row">
					<li data-slide="1" class="col-12 col-sm-2"><a id="menu-link-1" href="#slide-1" title="Next Section"><span class="icon icon-home"></span> <span class="text">HOME</span></a></li>
					<li data-slide="2" class="col-12 col-sm-2"><a id="menu-link-2" href="#slide-2" title="Next Section"><span class="icon icon-user"></span> <span class="text">CAR_EVENT</span></a></li>
					<li data-slide="4" class="col-12 col-sm-2"><a id="menu-link-4" href="#slide-4" title="Next Section"><span class="icon icon-briefcase"></span> <span class="text">HEART_EVENT</span></a></li>
					
				</ul>
				<div class="row">
					<div class="col-sm-2 active-menu"></div>
				</div>
			</div><!-- /.nav-collapse -->
		</div><!-- /.container -->
	</div><!-- /.navbar -->
	
	
	<!-- === Arrows === -->
	<div id="arrows">
		<div id="arrow-up" class="disabled"></div>
		<div id="arrow-down"></div>
		<div id="arrow-left" class="disabled visible-lg"></div>
		<div id="arrow-right" class="disabled visible-lg"></div>
	</div><!-- /.arrows -->
	
	
	<!-- === MAIN Background === -->
	<div class="slide story" id="slide-1" data-slide="1">
		<div class="container">
			<div id="home-row-1" class="row clearfix">
				<div class="col-12">
					<h1 class="font-semibold">CAR ACCIDENT SURVEILLANCE SYSTEM</h1>
					
					<br>
					<br>
				</div><!-- /col-12 -->
			</div><!-- /row -->
			
		</div><!-- /container -->
	</div><!-- /slide1 -->
	
	<!-- === Slide 2 === -->
	<div class="slide story" id="slide-2" data-slide="2">
		<div class="container">
			<div class="row title-row">
				<div class="col-12 font-thin">CAR ACCIDENT EVENT </div>
			</div><!-- /row -->
			<div class="row line-row">
				<div class="hr">&nbsp;</div>
			</div><!-- /row -->
			<div class="row subtitle-row">
				<?php
					$servername="localhost";
					$username="root";
					$password="";
					$dbname="mydb";

					//create connect
					$conn=mysqli_connect($servername,$username,$password,$dbname);


					/* check connection */
					if (mysqli_connect_errno()) {
   						printf("Connect failed: %s\n", mysqli_connect_error());
    					exit();
					}

					mysqli_query($conn,"set names utf8");

					#$data=mysqli_query($conn,"select * from guestbook");
					$data=mysqli_query($conn,"SELECT * FROM CAR_EVENT order by eprikey desc");
					//echo mysql_num_rows($data);
					if($data === FALSE) { 
   						die(mysqli_error()); // TODO: better error handling
   					 //echo mysql_errno($conn) . ": " . mysql_error($conn). "\n";
					}

				?>

				<table width="900" border="1">
  			<tr>
    			<td>金鑰</td>
    			<td>時間</td>
    			<td>名字</td>
    			
  			</tr>
  	<?php
		for($i=1;$i<=mysqli_num_rows($data);$i++){
			$rs=mysqli_fetch_row($data);
	?>
  			<tr>
  				<td><?php echo $rs[0] ?></td>
  				<td><?php echo $rs[1] ?></td>
   				<td><?php echo $rs[2] ?></td>
   				
  			</tr>
	<?php
		}
	?>
		</table>
			
			</div><!-- /row -->
		</div><!-- /container -->
	</div><!-- /slide2 -->
	

	
	
	
	<!-- === Slide 4 - Process === -->
	<div class="slide story" id="slide-4" data-slide="4">
		<div class="container">
			<div class="row title-row">
				<div class="col-12 font-thin">HEART EVENT</div>
			</div><!-- /row -->
			<div class="row line-row">
				<div class="hr">&nbsp;</div>
			</div><!-- /row -->
			<div class="row subtitle-row">
				<?php
					$servername="localhost";
					$username="root";
					$password="";
					$dbname="mydb";

					//create connect
					$conn=mysqli_connect($servername,$username,$password,$dbname);


					/* check connection */
					if (mysqli_connect_errno()) {
   						printf("Connect failed: %s\n", mysqli_connect_error());
    					exit();
					}

					mysqli_query($conn,"set names utf8");

					$hdata=mysqli_query($conn,"SELECT * FROM HEART_EVENT  order by hprikey desc");

				?>

				<table width="900" border="1">
  			<tr>
    			<td>金鑰</td>
    			<td>時間</td>
    			<td>名字</td>
    			<td>心跳次數</td>
    			<td>異常</td>
    			
  			</tr>
  	<?php
		for($i=1;$i<=mysqli_num_rows($hdata);$i++){
			$hrs=mysqli_fetch_row($hdata);
			if($i==1){


	?>
  			<tr>
  				<td><span style="color:ff7676;"> <?php echo $hrs[0] ?></span></td>
  				<td><span style="color:red;"><?php echo $hrs[1] ?></span></td>
   				<td><span style="color:red;"><?php echo $hrs[2] ?></span></td>
   				<td><span style="color:red;"><?php echo $hrs[3] ?></span></td>
    			<td><span style="color:red;"><?php echo $hrs[4] ?></span></td>
    			
  			</tr>
	<?php
		}
		else{
	?>



	
  			<tr>
  				<td><?php echo $hrs[0] ?></td>
  				<td><?php echo $hrs[1] ?></td>
   				<td><?php echo $hrs[2] ?></td>
   				<td><?php echo $hrs[3] ?></td>
    			<td><?php echo $hrs[4] ?></td>
    			
  			</tr>
	<?php
		} //for else
	}//for forloop
	?>
		</table>
				
				
			</div><!-- /row -->
		</div><!-- /container -->
	</div><!-- /slide4 -->
	
	
	
</body>

	<!-- SCRIPTS -->
	<script src="js/html5shiv.js"></script>
	<script src="js/jquery-1.10.2.min.js"></script>
	<script src="js/jquery-migrate-1.2.1.min.js"></script>
	<script src="js/bootstrap.min.js"></script>
	<script src="js/jquery.easing.1.3.js"></script>
	<script type="text/javascript" src="fancybox/jquery.fancybox.pack-v=2.1.5.js"></script>
	<script src="js/script.js"></script>
	
	<!-- fancybox init -->
	<script>
	$(document).ready(function(e) {
		var lis = $('.nav > li');
		menu_focus( lis[0], 1 );
		
		$(".fancybox").fancybox({
			padding: 10,
			helpers: {
				overlay: {
					locked: false
				}
			}
		});
	
	});
	</script>

</html>