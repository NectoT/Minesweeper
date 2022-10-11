var open_tile = async function(value) {
    data = await fetch("/open-tile", {
        method: "POST",
        mode: "cors",
        credentials: "same-origin",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({index: Number(value)})
    }).then((response) => response.json())
    console.log(data)
    return data["successful"]
}

var update_field = async function() {
    data = await fetch("/get-field", {
        method: "GET",
        credentials: "same-origin",
    }).then((response) => response.json())
    buttons = field.children
    for (var i = 0; i < 400; i++) {
        if (data["field"][i] != -1) {
            buttons[i].innerHTML = data["field"][i];
            // button.style.backgroundColor = "rgb(200, 200, 200)"
        }
    }
}

var field
window.onload = function() {
    field = document.getElementById("field")
    for (var i = 0; i < 400; i++) {
        var button = document.createElement("button")
        field.appendChild(button)
        button.value = i.toString()
        //button.style.backgroundColor = "rgb(100, 100, 100)"
        button.onclick = event => {
            open_tile(event.target.value).then((successful) => {
                if (successful) {
                    update_field()
                }
                else {
                    field.children[event.target.value].style.backgroundColor = "red"
                }
            })
        }
    }
        
}