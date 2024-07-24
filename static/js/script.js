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
});
