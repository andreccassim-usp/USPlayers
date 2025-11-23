document.addEventListener("DOMContentLoaded", function () {
    const campoBusca = document.getElementById("campo-busca");
    const resultadoLista = document.getElementById("resultado");

    campoBusca.addEventListener("input", async function () {
        const query = campoBusca.value.trim();

        if (query.length < 1) {
            resultadoLista.innerHTML = "";
            return;
        }

        const resposta = await fetch(`/buscar_api/?q=${query}`);
        const dados = await resposta.json();

        resultadoLista.innerHTML = "";

        // --- ATLETAS ---
        dados.atletas.forEach(atleta => {
            let li = document.createElement("li");
            li.innerHTML = `
                <strong>${atleta.nome}</strong> — ${atleta.modalidade}
                <br><a href="/atleta/${atleta.pk}/">Ver perfil</a>
            `;
            resultadoLista.appendChild(li);
        });

        // --- ATLÉTICAS ---
        dados.atleticas.forEach(atletica => {
            let li = document.createElement("li");
            li.innerHTML = `
                <strong>${atletica.nome}</strong> — ${atletica.universidade}
                <br><a href="/atletica/${atletica.pk}/">Ver perfil</a>
            `;
            resultadoLista.appendChild(li);
        });
    });
});
