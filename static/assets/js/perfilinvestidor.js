document.getElementById('investorProfileForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const form = new FormData(event.target);
    const data = {};

    form.forEach((value, key) => {
        data[key] = value;
    });

    // Envia os dados do formulário para o servidor
    fetch('/save_profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('result').innerText = result.message;
    })
    .catch(error => {
        console.error('Erro ao enviar os dados:', error);
    });
});