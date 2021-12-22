$.ajax({
    url: "/ajax/menu_permissions", 
    dataType: 'json',
    success: function(data){
        data.no_permissions.forEach(e => {
            let id = '#menu' + e
            $(id).hide()
        });
    }
});