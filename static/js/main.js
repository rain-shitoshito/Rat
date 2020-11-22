// cookie取得
const get_cookie = name => {
	let cookie_value = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			let cookie = jQuery.trim(cookies[i]);
			if (cookie.substring(0, name.length+1) === (name+'=')) {
				cookie_value = decodeURIComponent(cookie.substring(name.length+1));
				break;
			}
		}
	}
	return cookie_value;
}

// arraybufferをbase64エンコード
const buffer_to_base64 = buffer => {
	let binary = '';
	const bytes = new Uint8Array(buffer);
	const len = bytes.byteLength;
	for (let i = 0; i < len; i++) {
		binary += String.fromCharCode( bytes[i] );
	}
	return window.btoa(binary);
}

class Transmission {
	constructor(method, content) {
		this.method = method;
		this.content = content;
		this.__proto__.csrftoken = get_cookie('csrftoken');
	}

	send(url, func) {
		fetch(url, {
			method: this.method,
			credentials: "same-origin",
			headers: {
				"Accept": "application/json",
				"Content-Type": "application/json",
				"X-CSRFToken": this.csrftoken,
			},
			body: JSON.stringify(this.content)
		})
		.then(response => {
			if(response.ok) {
				return response.json();
			} else {
				throw new Error("not found...");
			}
		})
		.then(data => {
			func(data);
		})
		.catch(e => {
			console.log(e.message);
		});
	}

	get(url, func) {
		fetch(url)
		.then(response => {
			if(response.ok) {
				return response.json();
			} else {
				throw new Error("not found...");
			}
		})
		.then(data => {
			func(data);
		})
		.catch(e => {
			console.log(e.message);
		});
	}
}
Transmission.uid = get_cookie('uid');


{
	let file_name = file_content = null;
	// ファイル中身を展開しbase64エンコード
	document.querySelector('.custom-file-input').addEventListener('change',function(e){
		const file = document.getElementById("input_file").files[0];
		const next_sibling = e.target.nextElementSibling;
		file_name = file.name;
		next_sibling.innerText = file_name;
		if (1 <= document.getElementById("input_file").files.length) {
			let reader = new FileReader();
			reader.onload = the_file => {
				file_content = buffer_to_base64(the_file.target.result);
			}
			reader.readAsArrayBuffer(file);
		}
	});

	window.addEventListener("load", (e) => {
		const base_url = `${location.protocol}//${location.host}`;
		const rgp = /^https?:\/\/([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(:8000|:8080)|[^\.\s\n~]+\.[^\.\s\d\n~])\/[^\.\s\n~]+/g;
		const tran = new Transmission();
		let url = `${base_url}/api/recipient/?format=json`;
		const get_table = data => {
			const tb = document.querySelector("#history tbody");
			const keys = ["id", "recipient", "cmd", "upfile", "cmd_finished", "response", "downfile", "resp_finished"];
			tb.innerHTML = "";
			if(data["results"] != null) {
				data["results"].forEach((obj) => {
					let tr = document.createElement("tr");
					let data;
					for(let i=0; i<keys.length; i++) {
						if(i == 3)
							data = obj[keys[i]] != null ? obj[keys[i]]["name"] : "null";
						else if(i == 6)
							data = obj[keys[i]] != null ? `<a href="${obj[keys[i]]["link"]}">${obj[keys[i]]["name"]}</a>` : "null";
						else if(i == 5 || i == 6 || i == 7)
							data = obj[keys[i]] != null ? obj[keys[i]] : "null";
						else
							data = obj[keys[i]];
						let td = document.createElement("td");
						td.innerHTML = data;
						tr.appendChild(td);
					}
					tb.appendChild(tr);
				});
			}
		};
		const get_nation = data => {
			const history_nation = document.getElementById("history_nation");
			history_nation.innerHTML = "";
			const urls = {
				"before": data["before"],
				"next": data["next"]
			};
			for(let key in urls) {
				console.log(urls[key]);
				if(urls[key] != null) {
					let btn = document.createElement("button");
					btn.setAttribute("type", "button");
					btn.setAttribute("class", "btn btn-outline-dark ml-1");
					btn.innerText = key == "before" ? "戻る" : "進む";
					btn.addEventListener("click", e => {
						tran.get(urls[key], data => {
							get_history(data);
						});
					});
					history_nation.appendChild(btn);
				}
			}
		};
		const get_history = data => {
			get_table(data);
			get_nation(data);
		};

		if(url.match(rgp)) {
			tran.get(
				url,
				(data) => {
					if(data.length != 0) {
						const target = document.getElementById("target");
						data.forEach(obj => {
							let option = document.createElement("option");
							option.value = obj["recipient"];
							option.text = obj["recipient"];
							target.appendChild(option);
						});
					}
				}
			)
		}
		url = `${base_url}/api/command/sender_cmd/?sender=${Transmission.uid}&format=json`;
		if(url.match(rgp)) {
			tran.get(url, get_history);
		}
	});


	// document.getElementById("send").addEventListener("click", e => {
	// 	const cmd = document.getElementById("cmd");
	// 	if(cmd.value != "") {
	// 		let content = {
	// 			sender: Transmission.uid,
	// 			cmd: cmd.value,
	// 			recipient: document.getElementById("target").value,
	// 		}
	// 		if(file_name != null && file_content != null) {
	// 			content["name"] = file_name;
	// 			content["content"] = file_content;
	// 		}
			
	// 		tran = new Transmission(
	// 			"POST",
	// 			content
	// 		);
	// 		tran.send("http://127.0.0.1:8000/api/command/?format=json", (data) => {
	// 			console.log(data);
	// 		});
	// 	}
	// });
	document.getElementById("send").addEventListener("click", e => {
		const cmd = document.getElementById("cmd");
		if(cmd.value != "") {
			let content = {
				response: cmd.value,
			}
			if(file_name != null && file_content != null) {
				content["name"] = file_name;
				content["content"] = file_content;
			}
			
			tran = new Transmission(
				"PATCH",
				content
			);
			tran.send("http://127.0.0.1:8000/api/command/1/?format=json", (data) => {
				console.log(data);
			});
		}
	});
}
