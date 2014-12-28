function getposts(board, array){
	var data = {"action":"get posts code by num", "board":board, "ids":array};
	var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

        xhr.onloadend = function () {
		var postdict = JSON.parse(xhr.responseText);
		threadaddcode(postdict, array, board);
        // done
        };
};

function formatdate(date){
	var daylist = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
	var secs = date.getSeconds();
	if (secs < 10) {
		secs = "0" + secs;
	} else {
		secs = "" + secs;
	}
	var mins = date.getMinutes();
	if (mins < 10) {
		mins = "0" + mins;
	} else {
		mins = "" + mins;
	}
	var str = daylist[date.getDay()] + " " + date.getDate() + "/" + (date.getMonth()+1) + "/" + date.getFullYear() + " " + date.getHours() + ":" + mins + ":" + secs;
	return str;
};

function threadaddcode(postdict, array, board){//will be redone for normal adding from dict returned
	for (var i = 0; i < array.length; i++) {
		postdiv = document.getElementById(array[i]);
		
//should put it into a separate function
//also should add checking for null objects
		var post_details = document.createElement("div");
		post_details.className = "post_details";
	
		if (postdict[array[i]]["theme"] !== null) {
			var p_theme = document.createElement("span");
			p_theme.className = "theme";
			p_theme.innerHTML = postdict[array[i]]["theme"];
			post_details.appendChild(p_theme);
		}

		var p_name = document.createElement("span");
		p_name.className = "name";
		p_name.innerHTML = postdict[array[i]]["name"];
		post_details.appendChild(p_name);

		var p_date = document.createElement("span");
		p_date.className = "post_time";
		var post_time = new Date(postdict[array[i]]["post_time"]*1000);
		p_date.innerHTML = formatdate(post_time);
		post_details.appendChild(p_date);
	
		var p_id = document.createElement("span");
		p_id.className = "post_link";
		var a = document.createElement("a");
		if (postdict[array[i]]["op_post"] === null) {
			a.href = "/" + board + "/res/" + postdict[array[i]]["id"] + "#" + postdict[array[i]]["id"];
		} else {
			a.href = "/" + board + "/res/" + postdict[array[i]]["op_post"] + "#" + postdict[array[i]]["id"];
		};
		a.innerHTML = "№" + postdict[array[i]]["id"];
		p_id.appendChild(a);
		post_details.appendChild(p_id);

		if (postdict[array[i]]["op_post"] === null) {
			var p_answer = document.createElement("span");
			p_answer.className = "answer_link";
			var a = document.createElement("a");
			a.href = "/" + board + "/res/" + postdict[array[i]]["id"] + "#end";
			a.innerHTML = "[Ответ]";
			p_answer.appendChild(a);
			post_details.appendChild(p_answer);
		};
	
		postdiv.appendChild(post_details);
	
		var post_body = document.createElement("div");
		var p_text = document.createElement("blockquote");
		p_text.className = "post_text";
		p_text.innerHTML = postdict[array[i]]["text"];
		post_body.appendChild(p_text);
 	
		postdiv.appendChild(post_body);

//added post
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
		post.className = "oppost";
		mainframe.appendChild(post);

		var threadnum;
		var array = JSON.parse(xhr.responseText)[thread];
		for (i in array) {
			var post = document.createElement("div");
			post.id = array[i];
			post.className = "post";
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
	