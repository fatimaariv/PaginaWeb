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

