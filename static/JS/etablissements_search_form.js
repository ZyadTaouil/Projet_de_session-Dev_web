// Lors de la soumission du formulaire de recherche rapide
$(document).ready(function () {
    $('#search-form').submit(function (event) {
        event.preventDefault();

        var etablissementId = $('#etablissement-select').val();

        // requête Ajax pour récupérer les informations
        // d'infraction pour l'établissement choisi
        $.ajax({
            type: 'GET',
            url: '/api/violations/etablissement/' + etablissementId,
            dataType: 'json',
            success: function (response) {
                var results = response.results;
                var html = '<h2>Infractions pour ' + results[0].etablissement +
                    '</h2><table class="table"><thead><tr><th>Date</th>' +
                    '<th>Description</th><th>Montant</th></tr></thead><tbody>';
                for (var i = 0; i < results.length; i++) {
                    var date = results[i].date;
                    var year = date.substring(0,4);
                    var month = date.substring(4,6);
                    var day = date.substring(6,8);
                    var formattedDate = `${day}/${month}/${year}`;
                    html += '<tr><td>' + formattedDate + '</td><td>' +
                        results[i].description + '</td><td>' +
                        results[i].montant + ' $</td></tr>';
                }
                html += '</tbody></table>';
                $('#results').html(html);
            },
            error: function (xhr, status, error) {
                var errorMessage = 'Une erreur est survenue : ' + error;
                $('#results').html('<div class="alert alert-danger">' +
                    errorMessage + '</div>');
            }
        });
    });
});
