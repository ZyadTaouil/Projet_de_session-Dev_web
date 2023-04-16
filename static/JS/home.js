$(document).ready(function () {
    $('#search-form').submit(function (event) {
        event.preventDefault();
        var du = $('#du').val();
        var au = $('#au').val();
        $.ajax({
            url: '/contrevenants',
            method: 'GET',
            data: {du: du, au: au},
            success: function (data) {
                $('#results').html('<table id="results-table" class="table">' +
                    '<thead><tr><th>Nom de l\'établissement</th>' +
                    '<th>Nombre de contraventions</th></tr></thead>' +
                    '<tbody></tbody></table>');
                $.each(data.results, function (i, result) {
                    var row = '<tr><td>' + result.etablissement + '</td><td>' +
                        result.nb_violations + '</td></tr>';
                    $('#results-table tbody').append(row);
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert('Veuillez choisir des dates valides');
            }
        });
    });
});