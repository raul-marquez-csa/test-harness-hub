$(document).ready(function() {
    var socket = io();

    $('#runCommandBtn').click(function() {
        var command = $('#commandInput').val();
        $('#output').text('');
        socket.emit('run_command', command);
    });

    socket.on('command_output', function(msg) {
        $('#output').append(msg.data);
    });

    // Enable tab switching
    $('#myTab a').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });

    // Handle folder verification
    $('#verifyFolderBtn').click(function() {
        var folderPath = $('#folderPathInput').val();
        var $icon = $('#verifyFolderIcon');
        $icon.removeClass('pi-check pi-times text-success text-danger').addClass('pi-refresh pi-spin');

        $.ajax({
            url: '/verify-folder',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ folder_path: folderPath }),
            success: function(response) {
                if (response.valid) {
                    $icon.removeClass('pi-refresh pi-spin').addClass('pi-check text-success');
                    displayGitDetails(response.git_details);
                } else {
                    $icon.removeClass('pi-refresh pi-spin').addClass('pi-times text-danger');
                    $('#gitStatusOutput').html('<div class="text-danger">Directory does not exist or is not a valid git repository</div>');
                }
            },
            error: function() {
                $icon.removeClass('pi-refresh pi-spin').addClass('pi-times text-danger');
                $('#gitStatusOutput').html('<div class="text-danger">Error verifying folder</div>');
            }
        });
    });

    function displayGitDetails(details) {
        var output = '<div class="row">';
        var cardNames = ['Test Harness', 'Frontend', 'Backend', 'CLI'];
        cardNames.forEach(function(name, index) {
            if (index % 2 === 0 && index > 0) {
                output += '</div><div class="row">';
            }
            var detail = details[name];
            output += '<div class="col-md-6">';
            output += '<div class="card mb-3">';
            output += '<div class="card-header">' + name + '</div>';
            output += '<div class="card-body">';
            if (detail.error) {
                output += '<p class="text-danger">' + detail.error + '</p>';
            } else {
                output += '<p><strong>Branch:</strong> ' + detail.branch + '</p>';
                output += '<p><strong>Commit SHA:</strong> ' + detail.commit_sha + '</p>';
                output += '<p><strong>Commit Message:</strong> ' + detail.commit_message + '</p>';
                output += '<p><strong>Commit Author:</strong> ' + detail.commit_author + '</p>';
                output += '<p><strong>Commit Date:</strong> ' + detail.commit_date + '</p>';
            }
            output += '</div>';
            output += '</div>';
            output += '</div>';
        });
        output += '</div>';
        $('#gitStatusOutput').html(output);
    }
});
