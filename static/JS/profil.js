$(function () {
    // affiche photo téléchargée
    $("#photo").change(function () {
        const reader = new FileReader();
        reader.onload = function () {
            $("#photo-preview").attr("src", reader.result);
        };
        reader.readAsDataURL(this.files[0]);
    });

    $("#profil-form").submit(function (e) {
        e.preventDefault();
        const form = $(this)[0];
        const formData = new FormData(form);
        $.ajax({
            url: "/profil",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function () {
                alert("Modifications enregistrées avec succès");
            },
            error: function () {
                alert("Une erreur est survenue lors de l'enregistrement " +
                    "des modifications");
            }
        });
    });
});
