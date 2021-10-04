updateValue = function(id, value) {
    document.getElementById(id).innerText = value;
}

htmlToElement = function(html) {
    let template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}

pageSetup = function() {
    const minus = document.querySelector('.minus');
    const plus = document.querySelector('.plus');
    const value = document.querySelector('.value');
    // const users = document.querySelector('.users');
    const userInput = document.querySelector('.user-input');
    const userInputButton = document.querySelector('.user-input-button');
    const serverMessageValue = document.querySelector('.server-message-value');
    const messages = document.querySelector('.messages');
    const updatePersonality = document.getElementById("updatePersonality")
    const websocket = new WebSocket("wss://gpt2-chat.ai-research.id/");
    //const websocket = new WebSocket("ws://localhost:8502/");

    minus.onclick = function () {
        websocket.send(JSON.stringify({action: 'minus'}));
    }

    plus.onclick = function () {
        websocket.send(JSON.stringify({action: 'plus'}));
    }

    updatePersonality.onclick = function () {
        const elements = document.querySelectorAll(".bot-personality input")
        let data = {
            "action": "personality",
            "message": []
        }
        for (let i = 0; i < Math.min(elements.length, 5); i++) {
            if(elements[i].value.length >0)
                data.message.push(elements[i].value);
        }
        websocket.send(JSON.stringify(data));
    }

    let getParameters = function() {
        return {
            "do_sample": document.getElementById("doSample").checked,
            "min_length": parseInt(document.getElementById("minLength").value),
            "max_length": parseInt(document.getElementById("maxLength").value),
            "temperature": parseFloat(document.getElementById("temperature").value),
            "top_k": parseInt(document.getElementById("topK").value),
            "top_p": parseFloat(document.getElementById("topP").value),
        };
    }

    let processUserInput = function (userInput) {
        let parameters = getParameters();
        parameters["action"] = "talk";
        parameters["utterance"] = userInput.value;
        websocket.send(JSON.stringify(parameters));
        const element = htmlToElement("<div class=\"message outgoing\"><div class=\"message-inner badge bg-primary text-wrap\">"
            + userInput.value + "</div></div>");
        userInput.value = "";
        messages.appendChild(element);
        messages.scrollIntoView(false)
    }

    userInputButton.onclick = function () {
        processUserInput(userInput);
    }

    userInput.addEventListener("keyup", function(event) {
        if (event.keyCode === 13) {
            // Cancel the default action, if needed
            event.preventDefault();
            processUserInput(userInput);
        }
    });

    websocket.onmessage = function (event) {
        let data = JSON.parse(event.data);
        switch (data.type) {
            case 'connection':
                console.log(data.value)
                websocket.send(JSON.stringify({action: 'dialog', personality: []}));
                break;
            case 'state':
                value.textContent = data.value;
                break;
            case 'users':
                serverMessageValue.textContent = (
                    data.count.toString() + " user" +
                    (data.count === 1 ? "" : "s") + " online");
                break;
            case 'dialog':
                console.log(data.message)
                break;
            case 'talk':
                const element = htmlToElement("<div class=\"message incoming\"><div class=\"message-inner badge bg-success text-wrap\">"
                    + data.message+ "</div></div>");
                messages.appendChild(element);
                messages.scrollIntoView(false)
                break;
            case 'personality':
                const elements = document.querySelectorAll(".bot-personality input")
                for (let i = 0; i < Math.min(elements.length, data.message.length); i++) {
                    elements[i].value = data.message[i];
                }
                break;
            case 'personality_reply':
                serverMessageValue.textContent = data.message
                setTimeout(function() {
                    websocket.send(JSON.stringify({action: 'get_users'}));
                }, 3000);
                break;
            default:
                console.error(
                    "unsupported event", data);
        }
    };
}
