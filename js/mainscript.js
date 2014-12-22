function getposts(board, array){
	var data = {"action":"get posts code by num", "board":board, "ids":array};
	var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

        xhr.onloadend = function () {
		var postdict = JSON.parse(xhr.responseText);
		threadaddcode(postdict, array);
        // done
        };
};

function threadaddcode(postdict, array){
	//need to operate with op-post separately
	postdiv = document.getElementById(array[0]);
	postdiv.innerHTML = postdict[array[0]];
	//added op-post

	for (var i = 1; i < array.length; i++) {
		postdiv = document.getElementById(array[i]);
		postdiv.innerHTML = postdict[array[i]];
       	};
};

function threadfunc() {
	var board = document.getElementById("board").innerHTML;
	var thread = parseInt(document.getElementById("thread").innerHTML);
	var data = {"action":"get post ids for threads", "board":board, "threads":[{"threadnum":thread, "begin":1, "end":"all"}]};

	// construct an HTTP request
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

        xhr.onloadend = function () {
        	var mainframe = document.getElementById("mainframe");
		//adding op-post
		var post = document.createElement("div");
		post.id = thread;
		mainframe.appendChild(post);

		var threadnum;
		var array = JSON.parse(xhr.responseText)[thread];
		for (i in array) {
			var post = document.createElement("div");
			post.id = array[i];
			//post.innerHTML = array[i];
			mainframe.appendChild(post);
			array[i] = parseInt(array[i]);
		};
        // done
		array.unshift(thread);
		getposts(board, array);
	};
};



function boardfunc() {
	var board = document.getElementById("board").innerHTML;
	var page = parseInt(document.getElementById("page").innerHTML);
	var step = 15;
	var data = {"action":"get threads ids for page", "board":board, "range":{"begin":step*page+1, "end":step*(page+1)+1}};

	// construct an HTTP request
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

        xhr.onloadend = function () {
        	var mainframe = document.getElementById("mainframe");
		var threadnum;
		var array = JSON.parse(xhr.responseText);
		for (threadnum in array) {
			var div = document.createElement("div");
			div.id = "op" + array[threadnum];
			div.className = "oppostcontainer";
			var div2 = document.createElement("div");
			div2.id = array[threadnum];
			div2.className = "oppost";
			var post = document.createElement("p");
			var a = document.createElement("a");
			a.innerHTML = array[threadnum];
			a.href = "res/"+array[threadnum]+"/";
			//adding children
			post.appendChild(a);
			//added post
			div.appendChild(post);
			div.appendChild(div2);
			mainframe.appendChild(div); 
		};
		var threaddata = [];
		for (i in array) {
			threaddata.push({"threadnum":array[i], "begin":-3, "end":-1}); //then change of amount of loaded posts should be added
		}		
		var data = {"action":"get post ids for threads", "board":board, "threads":threaddata};

		
		// construct an HTTP request
	        var xhr2 = new XMLHttpRequest();
        	xhr2.open('POST', '', true);
        	xhr2.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

	        // send the collected data as JSON
        	xhr2.send(JSON.stringify(data));

	        xhr2.onloadend = function () {
			var postdict = JSON.parse(xhr2.responseText);
			var postlist = array;
			for (i in array){//here we add posts to threads
				var oppostdiv = document.getElementById("op" + array[i]);
				for (j in postdict[array[i]]){
					var div = document.createElement("div");
					div.id = postdict[array[i]][j];
					div.className = "post";
					oppostdiv.appendChild(div);
					postlist.push(postdict[array[i]][j]);
				};
			};
			//done
			//now getting the posts
			getposts(board, postlist);
		};
        // done
        };
};
	