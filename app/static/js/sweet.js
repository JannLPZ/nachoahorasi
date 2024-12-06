(function () {
    const addbtn = document.querySelectorAll('.Agregar');
    const csrf_token = document.querySelector("[name='csrf-token']").value;


    addbtn.forEach((btn) => {
        btn.addEventListener('click', function () {

            isbn = document.getElementById('isbn').value;
            titulo = document.getElementById('titulo').value;
            autor_id = document.getElementById('autor_id').value;
            anoedicion = document.getElementById('anoedicion').value;
            descripcion = document.getElementById('descripcion').value;
            precio = document.getElementById('precio').value;
            const inputImagen = document.getElementById('imagen');
            const imagen = inputImagen.files[0];


            confirmarComprar();
        })
    });

    const confirmarComprar = () => {

        Swal.fire({
            title: '¿Desea continuar con el registro?',
            inputAttributes: {
                autocapitalize: 'off'
            },
            showCancelButton: true,
            confirmButtonText: 'Registrar',
            showLoaderOnConfirm: true,
            preConfirm: async () => {
                console.log(window.origin);

                const formData = new FormData();
                formData.append('isbn', isbn);
                formData.append('autor_id', autor_id);
                formData.append('titulo', titulo);
                formData.append('anoedicion', anoedicion);
                formData.append('descripcion', descripcion);
                formData.append('precio', precio);
                formData.append('imagen', imagen);
               
                return await fetch(`${window.origin}/add_book`, {
                    method: 'POST',
                    mode: 'same-origin',
                    credentials: 'same-origin',
                    headers: {
                        'X-CSRF-TOKEN': csrf_token
                    },
                    body: formData,
                }).then(response => {
                    if (!response.ok) {
                        notificacionSwal('Error', response.statusText, 'error', 'Cerrar');
                    }
                    return response.json();
                }).then(data => {
                    if (data.exito) {
                        Swal.fire({
                           position: "Center",
                            titleText: '¡Éxito!',
                            icon: "success",
                            title: "Libro registrado exitosamente",
                            showConfirmButton: '¡Ok!',
                            timer: 1500
                        }).then((result) => {
                            if (result.dismiss === Swal.DismissReason.timer) {
                                window.location.href = '/login';
                            } else if (result.isConfirmed) {
                                window.location.href = '/login';
                            }
                        });
                    } else {
                        Swal.fire({
                            title: "Error",
                            text: data.mensaje,
                            icon: "warning",
                        });
                    }
                }).catch(error => {
                    Swal.fire({
                        title: "Error",
                        text: error.message,
                        icon: "error",
                    });
                });
            },
            allowOutsideClick: () => false,
            allowEscapeKey: () => false
        });
    };
})();