window.onload = function() {
    var input = document.getElementById('input');
    input.focus();
};

document.getElementById("input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        let userInput = event.target.value;
        
        // Desactivar el input para evitar más entradas mientras se procesa
        event.target.disabled = true;
        
        fetch('https://thermes-ai.onrender.com/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                displayResponse("Error: " + data.error);
            } else {
                displayPrompt(userInput);
                displayResponse(data.response); 
            }
        })
        .catch(error => {
            displayResponse("Network error: " + error.message);
        })
        .finally(() => {
            // Reactivar el input para permitir nuevas entradas
            document.getElementById("input").disabled = false;
            document.getElementById("input").value = "";  // Limpiar el campo de entrada
        });
    }
});

function displayResponse(response) {
    let terminalInside = document.querySelector('.terminal-inside');
    let responseElement = document.createElement('p');
    responseElement.textContent = `> ${response}`; // Agrega el sufijo "> " antes del texto
    responseElement.style.color = 'white';
    responseElement.style.padding = '2px';
    responseElement.style.textAlign = 'left'; // Alinea el texto a la izquierda
    responseElement.style.fontFamily = 'Arial, sans-serif'; // Especifica la fuente sans-serif
    terminalInside.appendChild(responseElement);

}

function displayPrompt(input) {
    let terminalInside = document.querySelector('.terminal-inside');
    let responseElement = document.createElement('div')
    responseElement.textContent = `>>> ${input}`; // Agrega el sufijo ">>> " ant
    responseElement.style.color = 'white';
    responseElement.style.padding = '3px';
    responseElement.style.textAlign = 'left'; // Alinea el texto a la izquierda
    responseElement.style.fontFamily = 'Arial, sans-serif'; // Especifica la fuente sans-serif
    responseElement.style.fontWeight = 'bold'; // Especifica la fuente sans-serif
    terminalInside.appendChild(responseElement);
}

document.addEventListener('DOMContentLoaded', () => {
    const headerLogo = document.getElementById('header-logo');
    const menuDrop = document.querySelector('.menu-drop');

    headerLogo.addEventListener('click', () => {
        if (menuDrop.classList.contains('show')) {
            menuDrop.classList.remove('show');
            menuDrop.classList.add('hide');
            headerLogo.style.borderRadius = '0px 20px 20px 20px';
        } else {
            menuDrop.classList.remove('hide');
            menuDrop.classList.add('show');
            headerLogo.style.borderRadius = '0px 0px 0px 20px';
        }
    });
});

