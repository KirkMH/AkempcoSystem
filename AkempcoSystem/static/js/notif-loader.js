function load_permissions() {
    $.ajax({
        url: "/notif/list", 
        dataType: 'json',
        success: function(data){
            console.log(data.last_ten_notifs)
            $('#notif_num_unread').text(data.num_unread)
            console.log(data.new_notif)

        },
        complete: function() {
            setTimeout(function(){load_permissions();}, 10000)
        }
    });
}
load_permissions()