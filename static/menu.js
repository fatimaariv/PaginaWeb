// Cargar materias desde el servidor al cargar la página
window.onload = async () => {
    const res = await fetch('/materias');
    const materias = await res.json();
    const selectMateria = document.getElementById('materia');
    materias.forEach(m => {
    let opt = document.createElement('option');
    opt.value = m.id;
    opt.textContent = m.nombre;
    selectMateria.appendChild(opt);
    });
};

// Cargar maestros cuando se selecciona una materia
document.getElementById('materia').addEventListener('change', async function () {
    const materiaId = this.value;
    const res = await fetch(`/maestros?materia_id=${materiaId}`);
    const maestros = await res.json();
    const selectMaestro = document.getElementById('maestro');
    selectMaestro.innerHTML = '<option value="">Selecciona un maestro</option>';
    maestros.forEach(maestro => {
    let opt = document.createElement('option');
    opt.value = maestro.id;
    opt.textContent = maestro.nombre;
    selectMaestro.appendChild(opt);
    });
});

document.getElementById('materia').addEventListener('change', function () {
        const idMateria = this.value;
        const maestroSelect = document.getElementById('maestro');

        maestroSelect.innerHTML = '<option>-- Cargando... --</option>';

        fetch('/obtener-maestros/' + idMateria)
            .then(response => response.json())
            .then(data => {
                maestroSelect.innerHTML = '<option value="">-- Elige un maestro --</option>';
                data.maestros.forEach(maestro => {
                    const option = document.createElement('option');
                    option.value = maestro.idMaestro;
                    option.textContent = maestro.nombreMaestro;
                    maestroSelect.appendChild(option);
                });
            });
    });



function votar(elemento, tipo) {
    const interaccion = elemento.parentElement;
    const likeBtn = interaccion.querySelector('.likes');
    const dislikeBtn = interaccion.querySelector('.dislikes');
    const likeCount = likeBtn.querySelector('.like-count');
    const dislikeCount = dislikeBtn.querySelector('.dislike-count');

    // Si ya tiene like y vuelve a dar like, no hace nada
    if (tipo === 'like' && likeBtn.classList.contains('votado')) return;
    // Si ya tiene dislike y vuelve a dar dislike, no hace nada
    if (tipo === 'dislike' && dislikeBtn.classList.contains('votado')) return;

    if (tipo === 'like') {
        // Si tenía dislike, lo quita
        if (dislikeBtn.classList.contains('votado')) {
            dislikeBtn.classList.remove('votado');
            dislikeBtn.style.pointerEvents = '';
            dislikeBtn.style.opacity = '';
            dislikeCount.textContent = parseInt(dislikeCount.textContent) - 1;
        }
        likeCount.textContent = parseInt(likeCount.textContent) + 1;
        likeBtn.classList.add('votado');
        likeBtn.style.pointerEvents = 'none';
        likeBtn.style.opacity = '0.6';
    } else {
        // Si tenía like, lo quita
        if (likeBtn.classList.contains('votado')) {
            likeBtn.classList.remove('votado');
            likeBtn.style.pointerEvents = '';
            likeBtn.style.opacity = '';
            likeCount.textContent = parseInt(likeCount.textContent) - 1;
        }
        dislikeCount.textContent = parseInt(dislikeCount.textContent) + 1;
        dislikeBtn.classList.add('votado');
        dislikeBtn.style.pointerEvents = 'none';
        dislikeBtn.style.opacity = '0.6';
    }
}


