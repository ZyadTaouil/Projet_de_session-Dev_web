$(document).ready(function () {

    $('#inscription-form').submit(function (event) {
        event.preventDefault();

        const nom = $('#nom').val();
        const email = $('#email').val();
        const password = $('#password').val();
        const passwordConfirm = $('#password-confirm').val();
        const etablissements =
            $('#etablissements').val().split(',').map(e => e.trim());


        if (password !== passwordConfirm) {
            alert("Les mots de passe ne sont pas identiques.");
            return;
        }

        const formData = {
            'nom': nom,
            'email': email,
            'password': password,
            'etablissements': etablissements
        };

        $.ajax({
            type: 'POST',
            url: '/api/utilisateurs',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            dataType: 'json',
            success: function () {
                alert("Utilisateur créé avec succès !");
                window.location.href = '/';
            },
            error: function (jqXHR, textStatus, errorThrown) {
                // Si la requête échoue, affiche un message d'erreur
                // à l'utilisateur
                alert(textStatus + ' - ' + errorThrown);
            }
        });
    });
});
