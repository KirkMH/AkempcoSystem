$.ajax({
    url: "/ajax/component_permissions", 
    dataType: 'json',
    success: function(data){
        data.user_types.forEach(e => {
            if (e[0] != data.type) {
                let class_name = '.type' + e[0]
                $(class_name).hide()
            }
        });
    }
});