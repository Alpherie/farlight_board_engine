function get_posts_num_from_time(elem) {
	elem.disabled=true;
	elem.parentNode.getElementsByTagName("span")[0].innerHTML = "Wait";
	var secs = parseInt(elem.parentNode.getElementsByTagName("input")[0].value)*parseInt(elem.parentNode.getElementsByTagName("select")[0].value);
	var board = elem.parentNode.parentNode.parentNode.getElementsByTagName("td")[0].getElementsByTagName("a")[0].innerHTML;
	console.log(secs);
	console.log(board);
	var data = {"action":"get num of posts during last", "board":board, "from_time":secs};
	var xhr = new XMLHttpRequest();
        xhr.open('POST', '', true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

        xhr.onload = function () {
		var num = JSON.parse(xhr.responseText);
		elem.parentNode.getElementsByTagName("span")[0].innerHTML = num;
		elem.disabled = false;
        // done
        };
	xhr.onerror = function () {
		elem.parentNode.getElementsByTagName("span")[0].innerHTML = "Fail";
		elem.disabled = false;
	}
}