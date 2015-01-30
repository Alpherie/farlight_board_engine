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
	
		var p_checkbox = document.createElement("span");
		p_checkbox.className = "checkbox";
		var checkbox = document.createElement("input");
		checkbox.type = "checkbox";
		checkbox.name = "delete";
		checkbox.value = array[i];
		p_checkbox.appendChild(checkbox);
		post_details.appendChild(p_checkbox);

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
		
		if ("ip" in postdict[array[i]]){
			var p_ip = document.createElement("span");
			p_ip.className = "post_ip";
			var a = document.createElement("a");
			a.onclick = function() {click_on_ip(this)};
			a.href = "javascript:void(0);"
			a.innerHTML = postdict[array[i]]["ip"];
			p_ip.appendChild(a);
			post_details.appendChild(p_ip);
		};
		
		postdiv.appendChild(post_details);
	
		var post_body = document.createElement("div");

		//adding pictures
		if (postdict[array[i]]["pics"].length !== 0) {
			var pic_block = document.createElement("div");
			if (postdict[array[i]]["pics"].length === 1){
				pic_block.className = "imageblock";
			} else {
				pic_block.className = "manyimageblock";
			}
			//classname may depend on number of pics

			for (j in postdict[array[i]]["pics"]){
				var figure = document.createElement("figure");
				figure.className = "image imagenum"+j;
				var figcaption = document.createElement("figcaption");
				figcaption.className = "fileattrs";
				var filelink = document.createElement("a");
				filelink.innerHTML = postdict[array[i]]["pics"][j];
				filelink.href = "/" + board + "/img/" + postdict[array[i]]["pics"][j];
				filelink.target = "_blank";
				//also there will be preview
				var img = document.createElement("img");
				img.src = "/" + board + "/thumbs/s" + postdict[array[i]]["pics"][j];
				img.alt = postdict[array[i]]["pics"][j];
				img.className = "previewimg";
				//adding all the shit
				figcaption.appendChild(filelink);
				figure.appendChild(figcaption);
				figure.appendChild(img);
				pic_block.appendChild(figure);
			}

			post_body.appendChild(pic_block);
		};

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
        	var oppostcontainer = document.createElement("div");
		oppostcontainer.className = "oppostcontainer";
		oppostcontainer.id = "op" + thread;
		document.getElementById("mainframe").appendChild(oppostcontainer);
		//adding op-post
		var post = document.createElement("div");
		post.id = thread;
		post.className = "oppost";
		oppostcontainer.appendChild(post);

		var threadnum;
		var array = JSON.parse(xhr.responseText)[thread];
		postsarray = array.slice();
		for (i in array) {
			var post = document.createElement("div");
			post.id = array[i];
			post.className = "post";
			//post.innerHTML = array[i];
			oppostcontainer.appendChild(post);
			array[i] = parseInt(array[i]);
		};
        // done
		array.unshift(thread);
		getposts(board, array);

		var updlink = document.createElement("a");
		updlink.innerHTML = "Обновить";
		updlink.href = "javascript:updatethread()";
		updlink.id = "updlink";
		var updbtnspan = document.createElement("span");
		updbtnspan.id = "updbtnspan";
		updbtnspan.insertAdjacentHTML("beforeend", "[");
		updbtnspan.appendChild(updlink);
		updbtnspan.insertAdjacentHTML("beforeend", "]");
		
		var passwdfield = document.createElement("input");
		passwdfield.type = "password";
		passwdfield.name = "delpasswd";
		passwdfield.id = "delpasswd";
		passwdfield.size = 10;
		var delbtn = document.createElement("input");
		delbtn.type = "submit";
		delbtn.name = "delbtn";
		delbtn.value = "Удалить";
		var delbtnspan = document.createElement("span");
		delbtnspan.id = "delbtnspan";
		delbtnspan.appendChild(passwdfield);
		delbtnspan.appendChild(delbtn);

		var optionsdiv = document.getElementById("optionsdiv");
		optionsdiv.appendChild(updbtnspan);
		optionsdiv.appendChild(delbtnspan);
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

function arraydiff (a, b) {
	var diff = [];

	a.forEach(function(key) {
		if (-1 === b.indexOf(key)) {
			diff.push(key);
		}
	}, this);
	return diff;
};

function updatethread() {
	document.getElementById("updlink").href = "";
	document.getElementById("updlink").innerHTML = "Обновляется...";
	var board = document.getElementById("board").innerHTML;
	var thread = parseInt(document.getElementById("thread").innerHTML);
	var data = {"action":"get post ids for threads", "board":board, "threads":[{"threadnum":thread, "begin":1, "end":"all"}]};

	// construct an HTTP request
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

	//need to add exceptioning if failed
        xhr.onloadend = function () {
		var newarray = JSON.parse(xhr.responseText)[thread];
		var arrdiff = arraydiff(postsarray, newarray);
		
		var deletedposts = arraydiff(postsarray, newarray);
		var array = arraydiff(newarray, postsarray); //new posts
		postsarray = newarray.slice();
		
		var oppostcontainer = document.getElementById("op"+thread);
		for (i in array) {
			var post = document.createElement("div");
			post.id = array[i];
			post.className = "post";
			//post.innerHTML = array[i];
			oppostcontainer.appendChild(post);
			array[i] = parseInt(array[i]);
		};
		
		if (array != []) {
			getposts(board, array);
		}

		document.getElementById("updlink").innerHTML = "Обновить";
		document.getElementById("updlink").href = "javascript:updatethread()";
	}
	xhr.onerror = function () {
		alert("Failed to update thread!");
		document.getElementById("updlink").innerHTML = "Обновить";
		document.getElementById("updlink").href = "javascript:updatethread()";
	}
};

//utilfunctions ------------------------------------------------------------------------

function findParentPostNode(elem) {
	var elem_again = elem.parentNode;
	var count = 1;
	while((typeof(elem_again.className) !== 'undefined') && (elem_again.className != "post") && (elem_again.className != "oppost")) {
		elem_again = elem_again.parentNode;
		count++;
	}
	// now you have the object you are looking for - do something with it
	return elem_again;
}

//modfunctions ---------------------------------------------------------------------------

function modbanip(elem){
	alert("Bans are not implemented yet!");
}

function moddelpost(elem){
	elem.innerHTML = "Удаляется...";
	var listelems = elem.parentNode.parentNode.getElementsByTagName("li");
	var i = 0;
	while (i < listelems.length) {
		listelems[i].getElementsByTagName("a")[0].onclick = function(){void(0)}; 
		//console.log(listelems[i]);
		i = i + 1;
	}

	var board = document.getElementById("board").innerHTML;
	var this_post = findParentPostNode(elem).id;
	console.log(this_post);
	var data = {"action":"delete posts by ids", "board":board, "posts_to_del":[this_post]};
	
	// construct an HTTP request
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

	xhr.onload = function () {
	//	for (i in listelems) {
	//		listelems[i].getElementsByTagName("a")[0].href = "javascript:" + options[i][1] + "(this)";
	//	}
		var posts_deleted = JSON.parse(xhr.responseText);
		alert(posts_deleted + " было удалено!");
	}

	xhr.onerror = function () {
		alert("Failed to delete post!");
	//	for (i in listelems) {
	//		listelems[i].getElementsByTagName("a")[0].href = "javascript:" + options[i][1] + "(this)";
	//	}
	}
}
	
options = [["Забанить IP", function(){modbanip(this)}], ["Удалить пост", function(){moddelpost(this)}]] //, ["Удалить пост и забанить", moddelpostbanip], ["Удалить все посты", moddelall], ["Удалить все посты и забанить", moddelallbanip]];

function click_on_ip_again (elem) {
	rem = elem.parentNode.getElementsByClassName("banmenu")[0];
	elem.parentNode.removeChild(rem);
	elem.onclick = function() {click_on_ip(this)};
}

function click_on_ip (elem){
	elem.onclick = function () {click_on_ip_again(this)};
	var ul = document.createElement("ul");
	ul.className = "banmenu";
	for (i in options) {
		var li = document.createElement("li");
		var a = document.createElement("a");
		a.innerHTML = options[i][0];
		a.href="javascript:void(0);"
		a.onclick = options[i][1];
		li.appendChild(a);
		ul.appendChild(li);
	};
	elem.parentNode.appendChild(ul);
};

//this is not a mod function

function add_file_input (btn) {
	btn.disabled="disabled";

	var br = document.createElement("br");
	document.getElementById("filecell").appendChild(br);

	var cur_num = parseInt(btn.id);
	var maxfiles = parseInt(document.getElementById("maxfiles").innerHTML);
	if (maxfiles > (cur_num + 1)) {
		var finput = document.createElement("input");
		finput.type = "file";
		finput.name = "file" + (cur_num + 1);
		finput.accept = "image/*";
		document.getElementById("filecell").appendChild(finput);

		var new_btn = document.createElement("button");
		new_btn.type = "button";
		new_btn.id = (cur_num+1) + "filebutton";
		new_btn.innerHTML = "+";
		new_btn.onclick = function(){add_file_input(this)};	
		document.getElementById("filecell").appendChild(new_btn);
	} else {
		var fspan = document.createElement("span");
		fspan.innerHTML = "Only "+maxfiles+" file(s) can be added";
		document.getElementById("filecell").appendChild(fspan);
	}
};