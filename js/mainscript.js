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
		var threadnum;
		var array = JSON.parse(xhr.responseText)[thread];
		for (threadnum in array) {
			var post = document.createElement("p");
			post.innerHTML = array[threadnum];
			mainframe.appendChild(post); 
		};
        // done
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
			var post = document.createElement("p");
			var a = document.createElement("a");
			a.innerHTML = array[threadnum];
			a.href = "res/"+array[threadnum]+"/"
			var br = document.createElement("br");
			var text = document.createElement("font");
			text.innerHTML = array[threadnum];
			//adding children
			post.appendChild(a);
			post.appendChild(br);
			post.appendChild(text);
			//added post
			mainframe.appendChild(post); 
		};
        // done
        };
};